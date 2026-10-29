"""结构静态审计：导航/索引配对、front matter、内容门槛与判据自污染防护。

用法：
  python audit_content.py --site <站点目录> --plan site.plan.json --mode full|skeleton
         [--min-lines 260] [--report out.md] [--selftest]

退出码：0 = problems 为 0；1 = 有问题；2 = 输入缺失/读文件失败。

--mode 是口径声明，不是可选项：
  full      正文已写完。11 类文体判据 + 10 类结构判据全部生效；文章桩（OINK-STUB）报 STUB_PAGE。
  skeleton  只搭了骨架、正文还是桩。只保留 10 类结构判据，文体判据与 STUB_PAGE 不报；
            汇总行会打印 mode=skeleton，别把这个绿色当成成品质量结论。

结构判据（两种模式都生效）：
  MISSING_INDEX / NOT_WRITTEN / UNLISTED / NO_FRONT_MATTER / FM_FIELD / THIN_DESC /
  BROKEN_IMAGE / SELF_CHECK_LEAK / DUP_WEIGHT / WEIGHT_GAP

文体判据（仅 full）：
  BOX_CHARS / SKIP_LANGUAGE / TOO_SHORT / FEW_NEWBIE / NO_MERMAID / FEW_TABLES /
  NO_CODE / NO_SUMMARY / NO_PAIN_OPEN / ENGLISH_HEADING / STUB_PAGE

判据先要能红：`--selftest` 用 fixtures 逐条比对注入缺陷，任何一条没命中或误报都打
SELFTEST_INVALID。不要把真实站点的 problems=0 当结论，先跑自证。
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.parse

FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
BOX_CHARS = "┌┐└┘├┤┬┴┼"
SKIP_WORDS = ("限于篇幅", "此处从略", "自行查阅", "待补充", "TODO", "感兴趣请", "众所周知", "不言而喻")
SELF_CHECK_LITERALS = ("方框字符", "省略式表达", "TOO_SHORT", "NO_PAIN_OPEN", "FEW_NEWBIE",
                       "NO_MERMAID", "FEW_TABLES", "NO_CODE", "NO_SUMMARY", "BROKEN_IMAGE",
                       "SKIP_LANGUAGE", "BOX_CHARS", "SELF_CHECK_LEAK")
FENCE = re.compile(r"^```")
IMAGE = re.compile(r"!\[[^\]]*\]\((/[^)\s]+)(?:\s+\"[^\"]*\")?\)")
GENRE_CODES = frozenset((
    "BOX_CHARS", "SKIP_LANGUAGE", "TOO_SHORT", "FEW_NEWBIE", "NO_MERMAID",
    "FEW_TABLES", "NO_CODE", "NO_SUMMARY", "NO_PAIN_OPEN", "ENGLISH_HEADING", "STUB_PAGE",
))
STRUCT_CODES = frozenset((
    "MISSING_INDEX", "NOT_WRITTEN", "UNLISTED", "NO_FRONT_MATTER", "FM_FIELD",
    "THIN_DESC", "BROKEN_IMAGE", "SELF_CHECK_LEAK", "DUP_WEIGHT", "WEIGHT_GAP",
))


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_categories(path):
    data = json.load(io.open(path, encoding="utf-8"))
    cats = data.get("categories") if isinstance(data, dict) else data
    if not isinstance(cats, list) or not cats:
        raise ValueError("计划里没有 categories")
    return cats


def audit(site, plan, mode, min_lines):
    site = os.path.abspath(site)
    docs = os.path.join(site, "content", "docs")
    static = os.path.join(site, "static")
    if not os.path.isdir(docs):
        raise OSError("没有 %s" % docs)
    cats = load_categories(plan)
    problems, rows = [], []

    def fail(path, kind, detail):
        problems.append((path, kind, detail))

    # 1 目录与 _index.md 配对（含 content/docs 根）
    dirs = 0
    for dirpath, dirnames, filenames in os.walk(docs):
        dirnames.sort()
        dirs += 1
        if "_index.md" not in filenames:
            fail(os.path.relpath(dirpath, site).replace(os.sep, "/"),
                 "MISSING_INDEX", "目录缺 _index.md")

    # 2 计划与磁盘一致
    expected = {os.path.normpath(os.path.join(docs, c["dir"], s["dir"], x["file"]))
                for c in cats for s in c["sections"] for x in s["articles"]}
    on_disk = {os.path.normpath(os.path.join(dp, f))
               for dp, _, fs in os.walk(docs) for f in fs
               if f.endswith(".md") and f != "_index.md"}
    for p in sorted(expected - on_disk):
        fail(os.path.relpath(p, site).replace(os.sep, "/"),
             "NOT_WRITTEN", "计划要求但文件不存在")
    for p in sorted(on_disk - expected):
        fail(os.path.relpath(p, site).replace(os.sep, "/"),
             "UNLISTED", "文件存在但不在计划内")

    # 3 逐篇检查
    for path in sorted(expected & on_disk):
        short = os.path.relpath(path, site).replace(os.sep, "/")
        try:
            text = read(path)
        except (OSError, UnicodeDecodeError) as e:
            fail(short, "NO_FRONT_MATTER", "读文件失败：%s" % e)
            continue
        if text.startswith("\ufeff"):
            text = text[1:]
        fm = FM_RE.match(text)
        if not fm:
            fail(short, "NO_FRONT_MATTER", "开头不是 YAML front matter")
            continue
        meta = fm.group(1)
        for field in ("title", "description", "weight"):
            if not re.search(rf"^{field}:[ \t]*\S", meta, re.M):
                fail(short, "FM_FIELD", "缺少 %s" % field)
        weight = re.search(r"^weight:[ \t]*(\d+)", meta, re.M)
        desc = re.search(r"^description:[ \t]*(.+)$", meta, re.M)
        desc_text = strip_quotes(desc.group(1)).strip() if desc else ""
        body = text[fm.end():]
        lines = text.count("\n") + 1
        stub = "OINK-STUB" in body

        if desc_text and len(desc_text) < 20:
            fail(short, "THIN_DESC", "description 仅 %d 字 < 20" % len(desc_text))
        if mode == "full" and any(c in body for c in BOX_CHARS):
            fail(short, "BOX_CHARS", "".join(c for c in BOX_CHARS if c in body))
        if mode == "full":
            skips = [w for w in SKIP_WORDS if w in body]
            if skips:
                fail(short, "SKIP_LANGUAGE", "、".join(skips))
        polluted = [w for w in SELF_CHECK_LITERALS if w in body]
        if polluted:
            fail(short, "SELF_CHECK_LEAK", "、".join(polluted))
        for m in IMAGE.finditer(body):
            rel = urllib.parse.unquote(m.group(1).split("#")[0].split("?")[0]).lstrip("/")
            if not os.path.isfile(os.path.join(static, rel.replace("/", os.sep))):
                fail(short, "BROKEN_IMAGE", m.group(1))

        fenced, real_h2 = False, []
        for line in body.splitlines():
            if FENCE.match(line):
                fenced = not fenced
                continue
            if not fenced and line.startswith("## "):
                real_h2.append(line[3:].strip())
        summary = {
            "file": short, "lines": lines, "h2": len(real_h2),
            "newbie": body.count("💡 新人小结"),
            "mermaid": len(re.findall(r"^```mermaid", body, re.M)),
            "codeblocks": len(re.findall(r"^```\s*(?!mermaid)[a-zA-Z]", body, re.M)),
            "tables": len(re.findall(r"^\|.*\|\s*$", body, re.M)) // 2,
            "callouts": len(re.findall(r"^> \[!", body, re.M)),
            "points": 1 if "要点总结" in body else 0,
            "stub": 1 if stub else 0,
            "weight": int(weight.group(1)) if weight else None,
            "desc_len": len(desc_text),
        }
        rows.append(summary)

        if mode == "full":
            if stub:
                fail(short, "STUB_PAGE", "正文仍是文章桩（OINK-STUB）")
            if lines < min_lines:
                fail(short, "TOO_SHORT", "%d 行 < %d" % (lines, min_lines))
            if summary["newbie"] < 3:
                fail(short, "FEW_NEWBIE", "💡 新人小结 %d < 3" % summary["newbie"])
            if summary["mermaid"] < 1:
                fail(short, "NO_MERMAID", "缺 Mermaid 图")
            if summary["tables"] < 2:
                fail(short, "FEW_TABLES", "表格行对约 %d < 2" % summary["tables"])
            if summary["codeblocks"] < 1:
                fail(short, "NO_CODE", "缺带语言标注的代码块")
            if not summary["points"]:
                fail(short, "NO_SUMMARY", "缺『要点总结』")
            if not (real_h2 and "为什么" in real_h2[0]):
                fail(short, "NO_PAIN_OPEN",
                     "首个真实 H2 未用『为什么…』：%s" % (real_h2[0][:40] if real_h2 else "无 H2"))
            for h in real_h2:
                if re.search(r"[A-Za-z]{4,}", h) and not re.search("[\u4e00-\u9fff]", h):
                    fail(short, "ENGLISH_HEADING", h[:60])

    # 4 同目录 weight 唯一且 1..N（以磁盘 front matter 为准）
    by_dir = {}
    for r in rows:
        by_dir.setdefault(os.path.dirname(r["file"]), []).append(r["weight"])
    for d, ws in sorted(by_dir.items()):
        if any(w is None for w in ws):
            continue
        dup = sorted({w for w in ws if ws.count(w) > 1})
        if dup:
            fail(d, "DUP_WEIGHT", str(dup))
        if sorted(ws) != list(range(1, len(ws) + 1)):
            fail(d, "WEIGHT_GAP", "应为 1..%d，实际 %s" % (len(ws), sorted(ws)))

    problems.sort()
    stats = {
        "articles": len(rows), "expected": len(expected), "dirs": dirs,
        "stubs": sum(r["stub"] for r in rows), "mode": mode,
        "genre_checks": len(GENRE_CODES) if mode == "full" else 0,
        "problems": len(problems),
    }
    return problems, rows, stats


def write_report(path, rows, problems, stats):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 内容结构审计\n\n")
        f.write("- mode=%s / 文章 %d / 计划要求 %d / 目录 %d / 文章桩 %d\n\n"
                % (stats["mode"], stats["articles"], stats["expected"], stats["dirs"], stats["stubs"]))
        f.write("| 文件 | 行 | H2 | 小结 | mermaid | 代码块 | 表格行对 | callout | 要点 | 桩 | weight | desc |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in sorted(rows, key=lambda x: x["file"]):
            f.write("| `%s` | %d | %d | %d | %d | %d | %d | %d | %d | %d | %s | %d |\n" % (
                r["file"], r["lines"], r["h2"], r["newbie"], r["mermaid"], r["codeblocks"],
                r["tables"], r["callouts"], r["points"], r["stub"], r["weight"], r["desc_len"]))
        f.write("\n## 问题明细\n\n")
        for p, code, detail in problems:
            f.write("- **%s** `%s` — %s\n" % (code, p, detail))


def selftest():
    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixtures = os.path.join(skill, "assets", "fixtures")
    site = os.path.join(fixtures, "site")
    plan = os.path.join(fixtures, "plan.json")
    exp_path = os.path.join(fixtures, "expected.json")
    if not all(os.path.exists(p) for p in (site, plan, exp_path)):
        print("SELFTEST_INVALID 缺 fixtures：%s" % fixtures)
        return 1
    exp = json.load(io.open(exp_path, encoding="utf-8"))
    min_lines = exp.get("min_lines", 20)
    full, _, stats_full = audit(site, plan, "full", min_lines)
    skel, _, stats_skel = audit(site, plan, "skeleton", min_lines)

    def as_map(problems):
        out = {}
        for path, code, _ in problems:
            out.setdefault(path, set()).add(code)
        return {k: sorted(v) for k, v in out.items()}

    obs_full = as_map(full)
    obs_skel = as_map(skel)
    want_full = {k: sorted(v) for k, v in exp["full"].items() if v}
    want_skel = {k: sorted(v) for k, v in exp["skeleton"].items() if v}
    ok = True
    if obs_full != want_full:
        ok = False
        print("SELFTEST_INVALID full 明细不符")
        for k in sorted(set(obs_full) | set(want_full)):
            if obs_full.get(k) != want_full.get(k):
                print("  %s observed=%s expected=%s" % (k, obs_full.get(k), want_full.get(k)))
    if obs_skel != want_skel:
        ok = False
        print("SELFTEST_INVALID skeleton 明细不符")
        for k in sorted(set(obs_skel) | set(want_skel)):
            if obs_skel.get(k) != want_skel.get(k):
                print("  %s observed=%s expected=%s" % (k, obs_skel.get(k), want_skel.get(k)))
    if set(GENRE_CODES) & set(STRUCT_CODES):
        ok = False
        print("SELFTEST_INVALID 判据分组有交集：%s" % sorted(set(GENRE_CODES) & set(STRUCT_CODES)))
    if len(GENRE_CODES) + len(STRUCT_CODES) != 21:
        ok = False
        print("SELFTEST_INVALID 判据总数不是 21：%d + %d"
              % (len(GENRE_CODES), len(STRUCT_CODES)))
    for p in exp.get("silent", []):
        if p in obs_full:
            ok = False
            print("SELFTEST_INVALID 合规样本被误报：%s -> %s" % (p, obs_full[p]))
    stub = exp.get("stub_file")
    if stub:
        if "STUB_PAGE" not in obs_full.get(stub, []):
            ok = False
            print("SELFTEST_INVALID 文章桩未报 STUB_PAGE：%s" % stub)
        if stub in obs_skel:
            ok = False
            print("SELFTEST_INVALID skeleton 模式误报文章桩：%s" % obs_skel[stub])
    print("full: problems=%d articles=%d genre_checks=%d codes=%d"
          % (stats_full["problems"], stats_full["articles"], stats_full["genre_checks"],
             len({c for _, c, _ in full})))
    print("skeleton: problems=%d genre_checks=%d codes=%d"
          % (stats_skel["problems"], stats_skel["genre_checks"],
             len({c for _, c, _ in skel})))
    print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--plan")
    ap.add_argument("--mode", choices=("full", "skeleton"), required=False)
    ap.add_argument("--min-lines", type=int, default=260)
    ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.site or not a.plan or not a.mode:
        print("FAIL 需要 --site、--plan、--mode（或 --selftest）")
        sys.exit(2)
    try:
        problems, rows, stats = audit(a.site, a.plan, a.mode, a.min_lines)
    except (OSError, ValueError) as e:
        print("FAIL %s" % e)
        sys.exit(2)
    if a.report:
        write_report(a.report, rows, problems, stats)
    kinds = {}
    for _, code, _ in problems:
        kinds[code] = kinds.get(code, 0) + 1
    print("articles=%d expected=%d dirs=%d stubs=%d problems=%d mode=%s genre_checks=%d"
          % (stats["articles"], stats["expected"], stats["dirs"], stats["stubs"],
             stats["problems"], stats["mode"], stats["genre_checks"]))
    print("by_kind=" + json.dumps(kinds, sort_keys=True))
    for p, code, detail in problems[:60]:
        print("  %s :: %s :: %s" % (code, p, detail))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
