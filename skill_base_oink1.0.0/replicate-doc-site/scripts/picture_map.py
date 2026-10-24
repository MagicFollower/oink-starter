"""配图清单生成：按矩阵逐篇解析源文档图片引用，映射到站点 static/picture/，产出可直接粘贴的清单与缺失项。

用法：
  python picture_map.py --matrix matrix.json --src <源文档根> --site <站点目录>
      [--prefix 4x=docs --prefix 50=versioned_docs/version-5.0] [--out image_map.md]

Step 4 派写作子代理时必须随任务单给出「这篇能用哪些配图」，否则子代理会猜图片路径造成断链。
引用解析规则：markdown ![alt](url) 与 html <img src="url">；相对 url 按源文件所在目录解析，
以 / 开头的按 --src 根解析，url 先做 percent 解码；外部 http(s)/data 引用跳过。
落地匹配规则：在 <site>/static/picture/ 下按 basename 匹配（上游多棵图树会被拍平到同一目录），
同名多份的 basename 报为 ambiguous，不产出可用项，留给人裁决。
矩阵里混有「不在上游文档树内」的源（local: 指向同级示例工程/本地附件）时，用 --skip-prefix local
声明跳过，单独计入 out_of_scope；未声明的未知前缀仍退出 2。
退出码：0 = 正常（missing 不算失败，是给人看的清单）；2 = 用法错（缺参、JSON 解析失败、目录不存在、未知前缀）。
最后一行汇总：articles=N refs=M mapped=K missing_in_static=J ambiguous_basename=K out_of_scope=S
"""

import argparse
import io
import json
import os
import sys
import urllib.parse

LIMIT = 40


def load_matrix(path):
    """读矩阵 JSON，兼容顶层 dict（含 categories/prefixes）与顶层直接是 categories 数组两种形态。"""
    with io.open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("categories") or [], data.get("prefixes") or {}
    if isinstance(data, list):
        return data, {}
    raise ValueError("矩阵顶层既不是 dict 也不是 list")


def resolve_source(s, prefixes, src):
    """把 tag:rel 形式的 source 解析为 (tag, 逻辑相对路径, 磁盘绝对路径, bad_prefix)。"""
    if ":" in s:
        tag, rel = s.split(":", 1)
        base = prefixes.get(tag)
        if base is None:
            return tag, s, None, True
        parts = rel.split("/")
        return tag, "/".join([base] + parts), os.path.join(src, base, *parts), False
    parts = s.split("/")
    return "", s, os.path.join(src, *parts), False


def extract_images(text):
    """字符串扫描 markdown ![alt](url) 与 html <img src="url">，返回 (url, alt) 列表。"""
    refs = []
    i = 0
    while True:
        j = text.find("![", i)
        if j < 0:
            break
        k = text.find("](", j + 2)
        if k < 0:
            break
        m = text.find(")", k + 2)
        if m < 0:
            break
        refs.append((text[k + 2:m].strip(), text[j + 2:k].strip()))
        i = m + 1
    i = 0
    while True:
        j = text.find("<img", i)
        if j < 0:
            break
        e = text.find(">", j)
        tag = text[j:e] if e >= 0 else text[j:]
        q = tag.find('src="')
        if q >= 0:
            refs.append((tag[q + 5:].split('"')[0].strip(), ""))
        i = j + 4
    return refs


def build_picture_index(pic_root):
    """basename -> [相对 pic_root 的落地路径]，同名多份会被完整列出。"""
    idx = {}
    for dp, dns, fns in os.walk(pic_root):
        dns.sort()
        for fn in sorted(fns):
            rel = os.path.relpath(os.path.join(dp, fn), pic_root).replace(os.sep, "/")
            idx.setdefault(fn, []).append(rel)
    return idx


def print_details(rows):
    for r in rows[:LIMIT]:
        print("  " + " :: ".join(str(x) for x in r))
    if len(rows) > LIMIT:
        print("  另有 %d 条" % (len(rows) - LIMIT))


def main():
    ap = argparse.ArgumentParser(
        description="按覆盖矩阵为每篇目标文档生成可用配图清单（映射到站点 static/picture/）",
        epilog="示例：python picture_map.py --matrix <暂存目录>/matrix.json --src <暂存目录>/src "
               "--site <站点目录> --prefix 4x=docs --prefix 50=versioned_docs/version-5.0 "
               "--out <暂存目录>/image_map.md")
    ap.add_argument("--matrix", required=True, help="矩阵 JSON（顶层 dict 或 categories 数组）")
    ap.add_argument("--src", required=True, help="源文档根目录")
    ap.add_argument("--site", required=True, help="站点目录（其下需有 static/picture/）")
    ap.add_argument("--prefix", action="append", default=[], help="tag=相对src的根路径，可重复")
    ap.add_argument("--skip-prefix", action="append", default=[],
                    help="声明这些 tag 的源不在上游文档树内，跳过解析只计数；可重复")
    ap.add_argument("--out", help="把清单写成 markdown 到该路径")
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    site = os.path.abspath(a.site)
    pic_root = os.path.join(site, "static", "picture")
    try:
        cats, file_prefixes = load_matrix(a.matrix)
    except Exception as e:
        print("FAIL 矩阵解析失败: %s" % e)
        sys.exit(2)
    if not os.path.isdir(src):
        print("FAIL --src 目录不存在: %s" % src)
        sys.exit(2)
    if not os.path.isdir(pic_root):
        print("FAIL 站点配图目录不存在: %s" % pic_root)
        sys.exit(2)
    prefixes = dict(file_prefixes)
    for p in a.prefix:
        if "=" not in p:
            print("FAIL --prefix 需要 tag=path 形式: %s" % p)
            sys.exit(2)
        k, v = p.split("=", 1)
        prefixes[k] = v
    for tag in sorted(prefixes):
        root = os.path.join(src, prefixes[tag]) if prefixes[tag] else src
        if not os.path.isdir(root):
            print("FAIL prefix 根目录不存在: %s -> %s" % (tag, root))
            sys.exit(2)

    index = build_picture_index(pic_root)
    skip_tags = set(a.skip_prefix)
    articles = []
    for cat in cats:
        for sec in cat.get("sections") or []:
            for art in sec.get("articles") or []:
                key = "%s/%s/%s" % (cat.get("dir"), sec.get("dir"), art.get("file"))
                articles.append((key, art.get("sources") or []))

    refs_total = mapped_total = missing_total = 0
    out_of_scope = 0
    ambiguous = {}
    missing_all = set()
    skipped_sources = []
    report = []
    for key, srcs in articles:
        usable = {}
        missing_here = set()
        for s in srcs:
            tag = s.split(":", 1)[0] if ":" in s else ""
            if tag in skip_tags:
                out_of_scope += 1
                continue
            tag, logical, fs, bad = resolve_source(s, prefixes, src)
            if bad:
                print("FAIL 未知前缀 %s:，用 --prefix %s=<路径> 声明；"
                      "若该源本就不在上游文档树内，用 --skip-prefix %s" % (tag, tag, tag))
                sys.exit(2)
            if not os.path.isfile(fs):
                skipped_sources.append((key, s))
                continue
            with io.open(fs, encoding="utf-8") as f:
                text = f.read()
            sdir = os.path.dirname(fs)
            for url, alt in extract_images(text):
                if url.startswith("http://") or url.startswith("https://") or url.startswith("data:") or url.startswith("//"):
                    continue
                u = urllib.parse.unquote(url)
                parts = u.split("/")
                if u.startswith("/"):
                    fsref = os.path.join(src, *parts[1:])
                else:
                    fsref = os.path.normpath(os.path.join(sdir, *parts))
                base = os.path.basename(fsref)
                if not base:
                    continue
                refs_total += 1
                hits = index.get(base) or []
                if len(hits) == 1:
                    mapped_total += 1
                    site_url = "/picture/" + urllib.parse.quote(hits[0])
                    old = usable.get(site_url)
                    if old is None or (not old and alt):
                        usable[site_url] = alt
                elif len(hits) > 1:
                    ambiguous.setdefault(base, hits)
                else:
                    missing_total += 1
                    missing_here.add((s, u))
        missing_all |= missing_here
        report.append((key, usable, sorted(missing_here)))

    out_lines = ["# 各目标文章可用配图（可直接粘贴的 /picture/ 绝对站内路径）", ""]
    for key, usable, miss in report:
        print("%s usable=%d missing=%d" % (key, len(usable), len(miss)))
        out_lines.append("### %s  （%d 张）" % (key, len(usable)))
        if usable:
            for site_url in sorted(usable):
                out_lines.append("![%s](%s)" % (usable[site_url], site_url))
        else:
            out_lines.append("（本篇源文档未引用可落地配图）")
        if miss:
            out_lines.append("")
            out_lines.append("缺失（源文引用但 static/picture 未找到）：")
            for s, u in miss:
                out_lines.append("- `%s` 引用 `%s`" % (s, u))
        out_lines.append("")

    if skipped_sources:
        print("skipped_sources（矩阵引用但磁盘不存在，交给 matrix_check.py 判 NONEXISTENT）:")
        print_details(skipped_sources)
    if missing_all:
        print("missing_in_static 明细（basename 未在 static/picture 落地）:")
        print_details(sorted((os.path.basename(u), s, u) for s, u in missing_all))
    if ambiguous:
        print("ambiguous_basename 明细（同名多份，人工裁决后才可入正文）:")
        print_details([(b, "、".join(hits)) for b, hits in sorted(ambiguous.items())])
    if a.out:
        op = os.path.abspath(a.out)
        parent = os.path.dirname(op)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)
        with io.open(op, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out_lines) + "\n")
        print("out=" + op)
    print("articles=%d refs=%d mapped=%d missing_in_static=%d ambiguous_basename=%d out_of_scope=%d"
          % (len(report), refs_total, mapped_total, missing_total, len(ambiguous), out_of_scope))
    sys.exit(0)


if __name__ == "__main__":
    main()
