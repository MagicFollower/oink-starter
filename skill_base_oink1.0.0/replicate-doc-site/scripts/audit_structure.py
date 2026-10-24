"""结构静态审计：目录/索引配对、front matter、内容门槛、判据自污染防护。

用法：
  python audit_structure.py --site <站点目录> --matrix matrix.json
         [--min-lines 260] [--mode rewrite|copy] [--scratch _work] [--report out.md]

退出码：0 = problems 为 0；1 = 有问题（明细见 stdout 与 --report 文件）。

--mode 对应 Step 0 让用户拍板的内容形态：rewrite（默认）= 按规范重写，全部判据生效；
copy = 完整复制原文，跳过 10 类文体判据（GENRE_CODES），因为上游原文本来就不满足
「痛点开场 / ≥260 行 / ≥3 个新人小结 / ≥1 个 mermaid」。矩阵一致性、front matter、
图片落地、暂存路径泄漏、判据词泄漏、非中文文件这些与形态无关，两种模式都生效。
汇总行会带上 `mode=`，别让 copy 模式的绿被当成 rewrite 模式的绿。

判据先要能红：空骨架（只有 front matter）必须在这里报出 TOO_SHORT / NO_MERMAID /
FEW_NEWBIE 等成片问题，否则说明判据没咬住，别拿 problems=0 当结论。
一条命令跑完全套红/绿对照：`python verify_all.py --selftest`。

口径声明：本脚本的判据默认面向「中文长文科普体」（痛点开头、💡 新人小结、
中文省略语黑名单、只允许中文语言文件）。换语言或换文体时要改的就是下面这几个常量：
BOX_CHARS / SKIP_WORDS / SELF_CHECK_LITERALS / GENRE_CODES，以及 main() 里的 FEW_NEWBIE、
NO_PAIN_OPEN、ENGLISH_HEADING、NON_ZH_FILE 四条判据；--min-lines 按文体调。
只是「同一批判据不适用于完整复制形态」的话不用改代码，跑 --mode copy 即可。
本脚本自己没有 --selftest，改完跑 `python verify_all.py --selftest`，夹具里有每条判据对应的红样本。
"""

import argparse
import json
import os
import re
import sys
import urllib.parse

FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.S)
BOX_CHARS = "┌┐└┘├┤┬┴┼"
SKIP_WORDS = ("限于篇幅", "此处从略", "自行查阅", "待补充", "TODO", "感兴趣请", "众所周知", "不言而喻")
# 本脚本报告里自己会出现的字面量：正文出现即说明判据词被抄进了交付物
SELF_CHECK_LITERALS = ("方框字符", "省略式表达", "SCRATCH_PATH", "MISSING_INDEX", "TOO_SHORT")
FENCE = re.compile(r"^```")
# 只属于「按规范重写」这一内容形态的判据：完整复制原文时上游本来就不会满足，
# 报了也只是噪音，所以 --mode copy 下整组过滤掉。剩下的（矩阵一致性、front matter、
# 图片落地、暂存路径泄漏、判据词泄漏、非中文文件）与内容形态无关，两种模式都生效。
GENRE_CODES = frozenset(("BOX_CHARS", "SKIP_LANGUAGE", "TOO_SHORT", "FEW_NEWBIE", "NO_MERMAID",
                         "FEW_TABLES", "NO_CODE", "NO_SUMMARY", "NO_PAIN_OPEN", "ENGLISH_HEADING"))


def load_categories(path):
    data = json.load(open(path, encoding="utf-8"))
    return data.get("categories") if isinstance(data, dict) else data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--min-lines", type=int, default=260)
    ap.add_argument("--mode", choices=("rewrite", "copy"), default="rewrite",
                    help="rewrite = 按规范重写（默认，全部判据生效）；"
                         "copy = 完整复制原文，跳过 10 类文体判据（见 GENRE_CODES）")
    ap.add_argument("--scratch", default="_work",
                    help="取源暂存目录名；正文出现该串即判 SCRATCH_PATH（应写上游仓库相对路径）")
    ap.add_argument("--report")
    a = ap.parse_args()

    SITE = os.path.abspath(a.site)
    DOCS = os.path.join(SITE, "content", "docs")
    PIC = os.path.join(SITE, "static", "picture")
    cats = load_categories(a.matrix)
    problems, rows = [], []

    def fail(p, kind, detail):
        problems.append((p, kind, detail))

    if not os.path.isdir(DOCS):
        print(f"FAIL 没有 {DOCS}")
        sys.exit(2)

    # 1 目录与 _index.md 配对
    dirs = 0
    for dirpath, dirnames, filenames in os.walk(DOCS):
        dirnames.sort()
        dirs += 1
        if "_index.md" not in filenames:
            fail(os.path.relpath(dirpath, SITE).replace(os.sep, "/"), "MISSING_INDEX", "目录缺 _index.md")

    # 2 矩阵与磁盘一致
    expected = {os.path.normpath(os.path.join(DOCS, c["dir"], s["dir"], x["file"]))
                for c in cats for s in c["sections"] for x in s["articles"]}
    on_disk = {os.path.normpath(os.path.join(dp, f))
               for dp, _, fs in os.walk(DOCS) for f in fs
               if f.endswith(".md") and f != "_index.md"}
    for p in sorted(expected - on_disk):
        fail(os.path.relpath(p, SITE).replace(os.sep, "/"), "NOT_WRITTEN", "矩阵要求但文件不存在")
    for p in sorted(on_disk - expected):
        fail(os.path.relpath(p, SITE).replace(os.sep, "/"), "UNLISTED", "文件存在但不在矩阵内")

    # 3 逐篇检查
    for path in sorted(expected & on_disk):
        # 判据的 key 一律用站点相对路径：早先文章级用 content/docs 相对、目录级用站点相对，
        # 两种口径混在一份报告里，机器比对要额外猜前缀。
        short = os.path.relpath(path, SITE).replace(os.sep, "/")
        text = open(path, encoding="utf-8").read()
        fm = FM_RE.match(text)
        if not fm:
            fail(short, "NO_FRONT_MATTER", "开头不是 YAML front matter")
            continue
        meta = fm.group(1)
        for field in ("title", "description", "weight"):
            if not re.search(rf"^{field}:[ \t]*\S", meta, re.M):
                fail(short, "FM_FIELD", f"缺少 {field}")
        weight = re.search(r"^weight:[ \t]*(\d+)", meta, re.M)
        desc = re.search(r"^description:[ \t]*(.+)$", meta, re.M)
        body = text[fm.end():]
        lines = text.count("\n") + 1

        if [c for c in BOX_CHARS if c in body]:
            fail(short, "BOX_CHARS", "".join(c for c in BOX_CHARS if c in body))
        skips = [w for w in SKIP_WORDS if w in body]
        if skips:
            fail(short, "SKIP_LANGUAGE", "、".join(skips))
        polluted = [w for w in SELF_CHECK_LITERALS if w in body]
        if polluted:
            fail(short, "SELF_CHECK_LEAK", "、".join(polluted))
        if a.scratch and a.scratch in body:
            fail(short, "SCRATCH_PATH", f"正文引用本地暂存目录 {a.scratch}/，应改为上游仓库相对路径")

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
            "weight": int(weight.group(1)) if weight else None,
            "desc_len": len(desc.group(1).strip()) if desc else 0,
        }
        rows.append(summary)

        if lines < a.min_lines:
            fail(short, "TOO_SHORT", f"{lines} 行 < {a.min_lines}")
        if summary["newbie"] < 3:
            fail(short, "FEW_NEWBIE", f"💡 新人小结 {summary['newbie']} < 3")
        if summary["mermaid"] < 1:
            fail(short, "NO_MERMAID", "缺 Mermaid 图")
        if summary["tables"] < 2:
            fail(short, "FEW_TABLES", f"表格行对约 {summary['tables']} < 2")
        if summary["codeblocks"] < 1:
            fail(short, "NO_CODE", "缺代码块")
        if not summary["points"]:
            fail(short, "NO_SUMMARY", "缺『要点总结』")
        if not (real_h2 and "为什么" in real_h2[0]):
            fail(short, "NO_PAIN_OPEN", f"首个真实 H2 未用『为什么…』：{real_h2[0][:40] if real_h2 else '无 H2'}")
        if summary["desc_len"] < 20:
            fail(short, "THIN_DESC", f"description 仅 {summary['desc_len']} 字")
        for h in real_h2:
            # 汉字范围写 \u 转义而不是字面量：区末码位 U+9FFF 多数字体没有字形，
            # 源码里看起来是豆腐块。非 raw 字符串的转义由 Python 编译期解析，pattern 与字面量逐字节相同。
            if re.search(r"[A-Za-z]{4,}", h) and not re.search("[\u4e00-\u9fff]", h):
                fail(short, "ENGLISH_HEADING", h[:60])
        for m in re.finditer(r"!\[[^\]]*\]\((/picture/[^)\s]+)\)", body):
            name = urllib.parse.unquote(m.group(1)[len("/picture/"):])
            if not os.path.isfile(os.path.join(PIC, name.replace("/", os.sep))):
                fail(short, "BROKEN_IMAGE", m.group(1))

    # 4 同目录 weight 唯一且 1..N
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
            fail(d, "WEIGHT_GAP", f"应为 1..{len(ws)}，实际 {sorted(ws)}")

    # 5 非中文语言文件
    for dp, dns, fns in os.walk(SITE):
        dns[:] = [x for x in dns if x != "oink-main"]
        for f in fns:
            if re.search(r"\.(en|fr|ja|ko)\.md$", f):
                fail(os.path.relpath(os.path.join(dp, f), SITE).replace(os.sep, "/"), "NON_ZH_FILE", f)

    if a.mode == "copy":
        before = len(problems)
        problems = [p for p in problems if p[1] not in GENRE_CODES]
        print("mode=copy 完整复制原文：%d 类文体判据不生效（%s），本次因此少报 %d 条问题"
              % (len(GENRE_CODES), "、".join(sorted(GENRE_CODES)), before - len(problems)))

    if a.report:
        with open(a.report, "w", encoding="utf-8", newline="\n") as f:
            f.write("# 结构审计\n\n")
            f.write(f"- 文章 {len(rows)} / 矩阵要求 {len(expected)} / 目录 {dirs}\n")
            f.write(f"- 问题 {len(problems)}\n\n")
            f.write("| 文件 | 行 | H2 | 小结 | mermaid | 代码块 | 表格行对 | callout | 要点 | weight | desc |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
            for r in sorted(rows, key=lambda x: x["file"]):
                f.write(f"| `{r['file']}` | {r['lines']} | {r['h2']} | {r['newbie']} | {r['mermaid']} | "
                        f"{r['codeblocks']} | {r['tables']} | {r['callouts']} | {r['points']} | {r['weight']} | {r['desc_len']} |\n")
            f.write("\n## 明细\n\n")
            for p, k, d in sorted(problems):
                f.write(f"- **{k}** `{p}` — {d}\n")

    kinds = {}
    for _, k, _ in problems:
        kinds[k] = kinds.get(k, 0) + 1
    print(f"articles={len(rows)} expected={len(expected)} dirs={dirs} problems={len(problems)} mode={a.mode}")
    print("by_kind=" + json.dumps(kinds, sort_keys=True))
    for p, k, d in sorted(problems)[:45]:
        print("  " + k + " :: " + p + " :: " + str(d))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
