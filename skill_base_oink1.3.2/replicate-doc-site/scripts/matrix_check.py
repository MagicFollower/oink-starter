"""矩阵自检：schema 与权重不变量、源文件集合运算、跨版本同名 MD5 查重，可选导出覆盖矩阵报告。

用法：
  python matrix_check.py --matrix matrix.json --src <源文档根>
      [--prefix 4x=docs --prefix 50=versioned_docs/version-5.0] [--skip-prefix local] [--report out.md]

失败判据代码：SCHEMA / DUP_WEIGHT / WEIGHT_GAP / NO_SOURCES / BAD_PREFIX / NONEXISTENT /
UNCOVERED / DUPLICATED。另打印两组查重统计（不是失败项）：
  same_name_pairs   —— 各 prefix 根之间按 basename 的同名对，逐字节 MD5 判相同/差异；
  per_article_pairs —— 同一篇文章 sources 内部的同名对，differing 的必须显式对比版本差异。
矩阵可以混有上游文档树之外的源（同级示例工程、二进制发行包、本地附件），用 --skip-prefix <tag>
声明后它们只计入 out_of_scope，不参与存在性核对、认领去重与查重；未声明的未知前缀仍报 BAD_PREFIX，
那是防前缀写错的闸门，不要拿 --skip-prefix 当消音器。
退出码：0 = 无失败判据；1 = 有；2 = 用法错（缺参、矩阵 JSON 解析失败、prefix 根目录不存在）。
输出最后一行是机器可读汇总：categories=… sections=… articles=… source_refs=… on_disk=… UNCOVERED=… DUPLICATED=… NONEXISTENT=… out_of_scope=… problems=…
"""

import argparse
import hashlib
import io
import itertools
import json
import os
import sys

LIMIT = 40
KINDS = ("SCHEMA", "DUP_WEIGHT", "WEIGHT_GAP", "NO_SOURCES", "BAD_PREFIX", "NONEXISTENT", "UNCOVERED", "DUPLICATED")
MD5_CACHE = {}


def load_matrix(path):
    """读矩阵 JSON，兼容顶层 dict（含 categories/prefixes）与顶层直接是 categories 数组两种形态。"""
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("categories") or [], data.get("prefixes") or {}
    if isinstance(data, list):
        return data, {}
    raise ValueError("矩阵顶层既不是 dict 也不是 list")


def slash(p):
    return p.replace(os.sep, "/")


def md5_of(path):
    """逐字节 MD5（带缓存），用于同名文件查重。"""
    if path not in MD5_CACHE:
        with io.open(path, "rb") as f:
            MD5_CACHE[path] = hashlib.md5(f.read()).hexdigest()
    return MD5_CACHE[path]


def walk_md(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for fn in sorted(fns):
            if fn.endswith(".md"):
                out.append(slash(os.path.relpath(os.path.join(dp, fn), root)))
    return out


def resolve_source(s, prefixes, src):
    """把 tag:rel 形式的 source 解析为 (tag, 逻辑相对路径, 磁盘绝对路径, bad_prefix)。"""
    if ":" in s:
        tag, rel = s.split(":", 1)
        base = prefixes.get(tag)
        if base is None:
            return tag, s, None, True
        parts = rel.split("/")
        return tag, slash(os.path.join(base, *parts)), os.path.join(src, base, *parts), False
    parts = s.split("/")
    return "", slash(s), os.path.join(src, *parts), False


def is_int_weight(w):
    return isinstance(w, int) and not isinstance(w, bool)


def check_weights(items, where, problems):
    """同层级 weight 必须唯一且为 1..N 连续（分类之间、板块之间、文章之间都查）。"""
    ws = [it.get("weight") for it in items]
    if any(not is_int_weight(w) for w in ws):
        return
    dup = sorted({w for w in ws if ws.count(w) > 1})
    if dup:
        problems.append((where, "DUP_WEIGHT", "重复 weight: %s" % dup))
    if sorted(ws) != list(range(1, len(ws) + 1)):
        problems.append((where, "WEIGHT_GAP", "应为 1..%d，实际 %s" % (len(ws), sorted(ws))))


def need_fields(node, fields, where, problems):
    """schema 判据：缺任一必备字段、或 weight 不是整数即报 SCHEMA。"""
    for f in fields:
        if f not in node:
            problems.append((where, "SCHEMA", "缺字段 " + f))
    if "weight" in node and not is_int_weight(node.get("weight")):
        problems.append((where, "SCHEMA", "weight 不是整数: %r" % (node.get("weight"),)))


def lines_of(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read().count("\n") + 1


def print_details(rows):
    for r in rows[:LIMIT]:
        print("  " + " :: ".join(str(x) for x in r))
    if len(rows) > LIMIT:
        print("  另有 %d 条" % (len(rows) - LIMIT))


def write_report(path, cats, prefixes, src, problems, cross, per, skip_tags=frozenset()):
    """导出 markdown 覆盖矩阵文档：分类→板块→文章→逐源（版本标记/行数/字节数），末尾附两组查重结论表。"""
    out = []
    w = out.append
    n_sec = sum(len(c.get("sections") or []) for c in cats)
    n_art = sum(len(s.get("articles") or []) for c in cats for s in (c.get("sections") or []))
    n_src = sum(len(a.get("sources") or []) for c in cats for s in (c.get("sections") or [])
                for a in (s.get("articles") or []))
    w("# 复刻覆盖矩阵")
    w("")
    w("本文件由 matrix_check.py 从覆盖矩阵与源文档实测生成：逐条给出源文件与目标文档的归属，并附同名查重结论。")
    w("")
    w("| 指标 | 数值 |")
    w("|------|------|")
    w("| 一级分类 | %d |" % len(cats))
    w("| 知识板块（二级目录） | %d |" % n_sec)
    w("| 重写文档 | %d |" % n_art)
    w("| 源文档归属条目 | %d |" % n_src)
    if n_art:
        w("| 合并倍率 | %.2f 篇源文档 / 篇重写文档 |" % (n_src / n_art))
    w("| 失败判据 | %d |" % len(problems))
    w("")
    if prefixes:
        w("版本前缀：")
        w("")
        for tag in sorted(prefixes):
            w("- `%s:` = `%s/`" % (tag, prefixes[tag]))
        w("")
    if skip_tags:
        w("树外前缀（--skip-prefix 声明，不参与存在性与查重核对）：")
        w("")
        for tag in sorted(skip_tags):
            w("- `%s:`" % tag)
        w("")
    w("## 一、逐篇归属")
    w("")
    for cat in cats:
        w("### %s. %s — `%s/`" % (cat.get("weight"), cat.get("title"), cat.get("dir")))
        w("")
        for sec in cat.get("sections") or []:
            w("**板块：%s** (`%s/`)" % (sec.get("title"), sec.get("dir")))
            w("")
            for art in sec.get("articles") or []:
                key = "%s/%s/%s" % (cat.get("dir"), sec.get("dir"), art.get("file"))
                w("#### `%s` — %s" % (art.get("file"), art.get("title")))
                w("")
                w("- 目标路径：`content/docs/%s`" % key)
                srcs = art.get("sources") or []
                w("- 源文档（%d 篇）：" % len(srcs))
                for s in sorted(srcs):
                    stag = s.split(":", 1)[0] if ":" in s else ""
                    if stag in skip_tags:
                        w("  - [%s] `%s` — 树外源，未核对" % (stag, s))
                        continue
                    tag, logical, fs, bad = resolve_source(s, prefixes, src)
                    if bad or fs is None or not os.path.isfile(fs):
                        w("  - [%s] `%s` — 无法解析或文件不存在" % (tag or "-", s))
                        continue
                    w("  - [%s] `%s` — %d 行 / %s 字节"
                      % (tag or "-", logical, lines_of(fs), format(os.path.getsize(fs), ",")))
                w("")
    w("## 二、跨版本根同名查重（逐字节 MD5）")
    w("")
    csame = sum(1 for r in cross if r[3])
    w("同名对 %d：逐字节相同 %d 对（合并为一份正文，只在版本适用处标注），存在差异 %d 对（正文必须显式对比版本差异）。"
      % (len(cross), csame, len(cross) - csame))
    w("")
    w("| 同名源文件 | 甲（MD5 前 10 位） | 乙（MD5 前 10 位） | 判定 |")
    w("|-----------|--------------------|--------------------|------|")
    for base, a1, a2, ident in cross:
        w("| `%s` | `%s` `%s` | `%s` `%s` | %s |"
          % (base, a1[0], a1[1][:10], a2[0], a2[1][:10], "相同" if ident else "不同"))
    w("")
    w("## 三、同一篇文章内部同名源查重")
    w("")
    psame = sum(1 for r in per if r[6])
    w("同名对 %d：逐字节相同 %d 对（写一份即可），存在差异 %d 对（写作时必须显式对比，不许只取一版）。"
      % (len(per), psame, len(per) - psame))
    w("")
    w("| 目标文章 | 同名文件 | 源甲 MD5 | 源乙 MD5 | 判定 |")
    w("|----------|----------|----------|----------|------|")
    for key, base, s1, h1, s2, h2, ident in per:
        w("| `%s` | `%s` | `%s` | `%s` | %s |" % (key, base, h1[:10], h2[:10], "相同" if ident else "不同"))
    w("")
    if problems:
        w("## 四、失败判据明细")
        w("")
        for where, kind, detail in sorted(problems):
            w("- **%s** `%s` — %s" % (kind, where, detail))
        w("")
    rp = os.path.abspath(path)
    parent = os.path.dirname(rp)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with io.open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return rp


def main():
    ap = argparse.ArgumentParser(
        description="覆盖矩阵自检：schema/权重不变量 + 源文件集合运算 + 跨版本同名 MD5 查重",
        epilog="示例：python matrix_check.py --matrix <暂存目录>/matrix.json --src <暂存目录>/src "
               "--prefix 4x=docs --prefix 50=versioned_docs/version-5.0 --report <暂存目录>/matrix_report.md")
    ap.add_argument("--matrix", required=True, help="矩阵 JSON（顶层 dict 或 categories 数组）")
    ap.add_argument("--src", required=True, help="源文档根目录")
    ap.add_argument("--prefix", action="append", default=[], help="tag=相对src的根路径，可重复")
    ap.add_argument("--skip-prefix", action="append", default=[],
                    help="声明这些 tag 的源不在上游文档树内（同级示例工程/本地附件），"
                         "跳过存在性与查重核对，只计入 out_of_scope；可重复")
    ap.add_argument("--report", help="额外导出 markdown 覆盖矩阵文档到该路径")
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    try:
        cats, file_prefixes = load_matrix(a.matrix)
    except Exception as e:
        print("FAIL 矩阵解析失败: %s" % e)
        sys.exit(2)
    if not isinstance(cats, list):
        print("FAIL 矩阵 categories 不是数组")
        sys.exit(2)
    if not os.path.isdir(src):
        print("FAIL --src 目录不存在: %s" % src)
        sys.exit(2)
    prefixes = dict(file_prefixes)
    for p in a.prefix:
        if "=" not in p:
            print("FAIL --prefix 需要 tag=path 形式: %s" % p)
            sys.exit(2)
        k, v = p.split("=", 1)
        prefixes[k] = v
    skip_tags = set(a.skip_prefix)
    for tag in sorted(skip_tags & set(prefixes)):
        print("WARN %s: 同时被 --prefix 与 --skip-prefix 声明，按 skip 处理（不核对存在性）" % tag)
    for tag in sorted(prefixes):
        root = os.path.join(src, prefixes[tag]) if prefixes[tag] else src
        if not os.path.isdir(root):
            print("FAIL prefix 根目录不存在: %s -> %s" % (tag, root))
            sys.exit(2)

    problems = []
    check_weights(cats, "<categories>", problems)
    articles = []
    for cat in cats:
        cdir = str(cat.get("dir", "?"))
        need_fields(cat, ("dir", "title", "weight", "desc"), "category " + cdir, problems)
        secs = cat.get("sections")
        if not isinstance(secs, list):
            problems.append(("category " + cdir, "SCHEMA", "缺 sections 列表"))
            continue
        check_weights(secs, "category " + cdir, problems)
        for sec in secs:
            sdir = cdir + "/" + str(sec.get("dir", "?"))
            need_fields(sec, ("dir", "title", "weight", "desc"), "section " + sdir, problems)
            arts = sec.get("articles")
            if not isinstance(arts, list):
                problems.append(("section " + sdir, "SCHEMA", "缺 articles 列表"))
                continue
            check_weights(arts, "section " + sdir, problems)
            for art in arts:
                key = sdir + "/" + str(art.get("file", "?"))
                need_fields(art, ("file", "title", "weight", "desc", "sources"), "article " + key, problems)
                srcs = art.get("sources")
                if not srcs:
                    problems.append(("article " + key, "NO_SOURCES", "sources 为空，等于这篇是凭空写的"))
                articles.append((key, list(srcs) if isinstance(srcs, list) else []))

    claimed = {}
    source_refs = 0
    out_of_scope = 0
    art_resolved = []
    for key, srcs in articles:
        resolved = []
        for s in srcs:
            source_refs += 1
            if (s.split(":", 1)[0] if ":" in s else "") in skip_tags:
                out_of_scope += 1
                continue
            tag, logical, fs, bad = resolve_source(s, prefixes, src)
            if bad:
                problems.append((key, "BAD_PREFIX",
                                 "未知前缀 %s:（既不在矩阵 prefixes 也未给 --prefix；"
                                 "树外源要显式 --skip-prefix %s）" % (tag, tag)))
                continue
            if not os.path.isfile(fs):
                problems.append((key, "NONEXISTENT", s))
                continue
            claimed.setdefault(logical, set()).add(key)
            resolved.append((s, logical, fs))
        art_resolved.append((key, resolved))
    for logical in sorted(claimed):
        ks = claimed[logical]
        if len(ks) >= 2:
            problems.append((logical, "DUPLICATED", "被 %d 篇认领: %s" % (len(ks), "、".join(sorted(ks)))))

    roots = dict((t, p) for t, p in prefixes.items() if t not in skip_tags) or {"": ""}
    files_by_tag = {}
    on_disk = set()
    for tag in sorted(roots):
        base = roots[tag]
        rels = walk_md(os.path.join(src, base) if base else src)
        files_by_tag[tag] = rels
        for rel in rels:
            on_disk.add(base + "/" + rel if base else rel)
    uncovered = sorted(on_disk - set(claimed))
    for logical in uncovered:
        problems.append((logical, "UNCOVERED", "磁盘存在但未被任何文章认领"))

    by_base = {}
    for tag in sorted(files_by_tag):
        for rel in files_by_tag[tag]:
            by_base.setdefault(os.path.basename(rel), {})[tag] = rel
    cross = []
    for base in sorted(by_base):
        d = by_base[base]
        if len(d) < 2:
            continue
        for t1, t2 in itertools.combinations(sorted(d), 2):
            l1 = (t1 + ":" + d[t1]) if t1 else d[t1]
            l2 = (t2 + ":" + d[t2]) if t2 else d[t2]
            p1 = os.path.join(src, roots[t1], *d[t1].split("/")) if roots[t1] else os.path.join(src, *d[t1].split("/"))
            p2 = os.path.join(src, roots[t2], *d[t2].split("/")) if roots[t2] else os.path.join(src, *d[t2].split("/"))
            cross.append((base, (l1, md5_of(p1)), (l2, md5_of(p2)), md5_of(p1) == md5_of(p2)))

    per = []
    for key, resolved in art_resolved:
        groups = {}
        for s, logical, fs in resolved:
            groups.setdefault(os.path.basename(logical), []).append((s, fs))
        for base in sorted(groups):
            items = groups[base]
            if len(items) < 2:
                continue
            for (s1, f1), (s2, f2) in itertools.combinations(items, 2):
                per.append((key, base, s1, md5_of(f1), s2, md5_of(f2), md5_of(f1) == md5_of(f2)))

    counts = dict((k, 0) for k in KINDS)
    for _, k, _ in problems:
        counts[k] += 1
    print(" ".join("%s=%d" % (k, counts[k]) for k in KINDS))
    csame = sum(1 for r in cross if r[3])
    print("same_name_pairs=%d identical=%d differing=%d" % (len(cross), csame, len(cross) - csame))
    psame = sum(1 for r in per if r[6])
    print("per_article_pairs=%d identical=%d differing=%d" % (len(per), psame, len(per) - psame))
    diff_per = [r for r in per if not r[6]]
    if diff_per:
        print("per-article differing pairs（写作时必须显式对比版本差异）:")
        print_details([(r[0], r[1], r[2], r[4]) for r in diff_per])
    if problems:
        print("problems:")
        print_details(sorted(problems))
    if a.report:
        rp = write_report(a.report, cats, prefixes, src, problems, cross, per, skip_tags)
        print("report=" + rp)
    n_sec = sum(len(c.get("sections") or []) for c in cats)
    n_art = sum(len(s.get("articles") or []) for c in cats for s in (c.get("sections") or []))
    print("categories=%d sections=%d articles=%d source_refs=%d on_disk=%d UNCOVERED=%d DUPLICATED=%d "
          "NONEXISTENT=%d out_of_scope=%d problems=%d"
          % (len(cats), n_sec, n_art, source_refs, len(on_disk), len(uncovered),
             counts["DUPLICATED"], counts["NONEXISTENT"], out_of_scope, len(problems)))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
