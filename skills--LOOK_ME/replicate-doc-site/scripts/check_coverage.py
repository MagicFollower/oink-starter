"""覆盖度核对：每篇目标文档是否真的承接了源文档的术语与数值。

用法：
  python check_coverage.py --site <站点目录> --matrix matrix.json --src <源文档根> \
      [--prefix 4x=docs --prefix 50=versioned_docs/version-5.0] [--filter 关键词] [--worst 12]

判据不用标题字面匹配（标题会被重写，术语不会凭空消失）：
  术语覆盖 = 源文件里的「≥4 字中文短语」∪「≥4 字符英文标识符」去重后，出现在目标文档的比例；
  数值覆盖 = 源文件里「数字+单位」token 的命中比例。
漏项会列出，供人工判定是「真漏」还是「上游客套句被改写」——覆盖率不是唯一结论。
默认只出分诊表（恒退出 0）；要当闸门用就加 --gate 0.6，违规行会让脚本退出 1。

矩阵里可以混有「不在上游文档树内」的源（典型是 local: 指向同级示例工程、二进制发行包、
本地附件）。这类源做术语覆盖核对没有意义——拿 Java 源码去比中文术语只会产出垃圾分诊行，
所以用 --skip-prefix local 显式声明跳过，它们单独计入 out_of_scope，不进 rows。
未声明的未知前缀仍然退出 2，那是防前缀写错的闸门，不要靠 --skip-prefix 绕过。
"""

import argparse
import json
import os
import re
import sys

# 汉字范围写 \u 转义而不是字面量：区末码位 U+9FFF 多数字体没有字形，源码里看着是豆腐块。
# 非 raw 字符串的转义由 Python 编译期解析，编译出的 pattern 与字面量写法逐字节相同。
CJK = re.compile("[\u4e00-\u9fff]{4,24}")
ASCII_ID = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{3,32}")
NUM_UNIT = re.compile(r"\b\d{1,6}(?:\.\d+)?\s?(?:MB|KB|GB|ms|毫秒|秒|分钟|小时|天|次|条|个|台|字符|字节|%)\b")
FENCE = re.compile(r"`{3}.*?`{3}", re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--src", required=True, help="源文档根（fetch_source.py 的 --out）")
    ap.add_argument("--prefix", action="append", default=[], help="tag=相对src的路径，可重复")
    ap.add_argument("--filter", default="", help="只核对目标文档路径含该串的行")
    ap.add_argument("--worst", type=int, default=12, help="按覆盖率升序详报前 N 个源文件")
    ap.add_argument("--gate", type=float, default=0.0,
                    help="给定阈值（如 0.6）才判成败；默认只出分诊表，恒退出 0")
    ap.add_argument("--min-lines", type=int, default=40,
                    help="目标文档低于该行数视为「未写」，不核对其源（默认 40）")
    ap.add_argument("--skip-prefix", action="append", default=[],
                    help="声明这些 tag 的源不在上游文档树内，跳过核对只计数；可重复")
    a = ap.parse_args()

    data = json.load(open(a.matrix, encoding="utf-8"))
    cats = data.get("categories") if isinstance(data, dict) else data
    prefixes = {}
    if isinstance(data, dict):
        prefixes.update(data.get("prefixes") or {})
    for p in a.prefix:
        if "=" in p:
            k, v = p.split("=", 1)
            prefixes[k] = v
    skip_tags = set(a.skip_prefix)

    rows = []
    out_of_scope = 0
    for cat in cats:
        for sec in cat["sections"]:
            for art in sec["articles"]:
                key = f"{cat['dir']}/{sec['dir']}/{art['file']}"
                if a.filter and a.filter not in key:
                    continue
                target = os.path.join(a.site, "content", "docs", cat["dir"], sec["dir"], art["file"])
                if not os.path.isfile(target):
                    rows.append((key, "-", 0, 0, 0, 0, ["缺目标文件"]))
                    continue
                tt = open(target, encoding="utf-8").read()
                if len(tt.splitlines()) < a.min_lines:
                    rows.append((key, "-", 0, 0, 0, 0, [f"未写({len(tt.splitlines())}行)"]))
                    continue
                for s in art.get("sources", []):
                    tag, rel = (s.split(":", 1) + [""])[:2] if ":" in s else ("", s)
                    if tag in skip_tags:
                        out_of_scope += 1
                        continue
                    base = prefixes.get(tag)
                    if base is None and ":" in s:
                        print(f"FAIL 未知前缀 {tag}:，用 --prefix {tag}=<路径> 声明；"
                              f"若该源本就不在上游文档树内，用 --skip-prefix {tag}")
                        sys.exit(2)
                    sp = os.path.join(a.src, base or "", (rel or s).replace("/", os.sep))
                    if not os.path.isfile(sp):
                        rows.append((key, s, 0, 0, 0, 0, ["源文件不存在"]))
                        continue
                    st = open(sp, encoding="utf-8").read()
                    body = FENCE.sub(" ", st)
                    terms = set(CJK.findall(body)) | {x for x in ASCII_ID.findall(body)}
                    hit = [t for t in terms if t in tt]
                    nums = sorted(set(NUM_UNIT.findall(st)))
                    nhit = [n for n in nums if n in tt]
                    rows.append((key, s, len(hit), len(terms), len(nhit), len(nums),
                                 sorted(terms - set(hit))[:10]))

    rows.sort(key=lambda r: (0 if r[6] and r[3] == 0 else 1, r[2] / r[3] if r[3] else 1.0))
    print(f"{'目标文档':46s} {'源':30s} {'术语':14s} {'数值':10s}")
    for key, src, h, ht, n, nt, miss in rows:
        cov = f"{h}/{ht}={h / ht:.0%}" if ht else "-"
        ncov = f"{n}/{nt}={n / nt:.0%}" if nt else "无数值"
        print(f"{key[:46]:46s} {src[:30]:30s} {cov:14s} {ncov:10s}")
    print("\n== 覆盖率最低的源文件（漏项需人工判定，不是自动结论） ==")
    for key, src, h, ht, n, nt, miss in rows[:a.worst]:
        if not ht:
            continue
        print(f"{src} @ {key}  {h}/{ht}={h / ht:.0%}  漏项: {'、'.join(miss[:8])}")
    low = [r for r in rows if r[3] and r[2] / r[3] < 0.8]
    broken = [r for r in rows if r[3] == 0]
    print(f"\ntriage_below_80pct={len(low)} error_rows={len(broken)} rows={len(rows)} "
          f"out_of_scope={out_of_scope}")
    if out_of_scope:
        print(f"（out_of_scope={out_of_scope} 条源按 --skip-prefix 声明跳过，未计入上面任何分母）")
    if a.gate:
        bad = [r for r in rows if r[3] == 0 or r[2] / r[3] < a.gate]
        print(f"gate={a.gate:.0%} violating={len(bad)}")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
