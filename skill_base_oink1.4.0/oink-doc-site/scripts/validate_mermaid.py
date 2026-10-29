"""用主题自带的 mermaid.min.js 真解析全站 ```mermaid 代码块（离线，不联网）。

用法：
  python validate_mermaid.py --site <站点目录>              # 生成解析台
  python validate_mermaid.py --site <站点目录> --selftest   # 额外注入一好一坏块并核对注入

生成后按 stdout 给的三行命令：起本地 http 服务 → 浏览器打开 → 读回 TOTAL/FAIL。
判据是「页内 MERMAID.parse() 逐块不抛异常」，不是「正则配平了括号」。

--selftest 只证明解析台和注入样本生成正确（SELFTEST_PASS）；真正的
REAL_FAIL=0 仍要在浏览器里读回，属于 MANUAL，不能拿本命令的退出码当绿色。
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys

BLOCK_RE = re.compile(r"^```mermaid\n(.*?)^```", re.S | re.M)

GOOD_SELFTEST = 'graph LR\n  A["起点"] -->|"动作"| B["终点"]\n'
BAD_SELFTEST = 'graph LR\n  A[起点 -- 缺右括号\n'

HARNESS = """<!doctype html>
<html lang="zh"><head><meta charset="utf-8"><title>mermaid parse harness</title></head>
<body>
<pre id="out">RUNNING</pre>
<script src="mermaid.min.js"></script>
<script>
const NS = window.__esbuild_esm_mermaid_nm || {};
const MERMAID = NS.mermaid && (NS.mermaid.default || NS.mermaid);
window.__RESULT = null;
async function run() {
  const blocks = await (await fetch('blocks.json')).json();
  if (!MERMAID || !MERMAID.parse) {
    document.getElementById('out').textContent = 'HARNESS_ERROR mermaid 未挂载，全局名不对';
    return;
  }
  MERMAID.initialize({ startOnLoad: false, securityLevel: 'loose' });
  const results = [];
  for (const b of blocks) {
    try {
      const r = await MERMAID.parse(b.source);
      results.push({ ...b, ok: true, diagramType: (r && r.diagramType) || 'unknown' });
    } catch (e) {
      results.push({ ...b, ok: false, error: String((e && e.message) || e).slice(0, 400) });
    }
  }
  window.__RESULT = results;
  const real = results.filter(r => r.file !== 'SELFTEST');
  const bad = real.filter(r => !r.ok);
  const st = results.filter(r => r.file === 'SELFTEST');
  const stOk = st.filter(r => r.ok).length;
  const stBad = st.length - stOk;
  const valid = stOk === 1 && stBad === 1;
  const head = 'TOTAL=' + real.length + ' REAL_FAIL=' + bad.length;
  document.getElementById('out').textContent =
    (st.length ? head + ' SELFTEST=' + stOk + '/' + st.length + (valid ? ' SELFTEST_PASS' : ' SELFTEST_INVALID')
              : head) + '\\n' +
    (st.length && !valid ? '判据没咬住：REAL_FAIL=0 不可信\\n' : '') +
    bad.map(r => 'FAIL ' + r.file + '#' + r.index + ' :: ' + r.error).join('\\n');
  window.__HEADLINE = (st.length && !valid) || bad.length > 0 ? 'RED' : 'GREEN';
}
run().catch(e => {
  document.getElementById('out').textContent = 'HARNESS_ERROR ' + e;
  window.__RESULT = 'ERR';
});
</script>
</body></html>
"""


def find_mermaid_js(site, explicit):
    if explicit:
        return os.path.abspath(explicit)
    cands = [os.path.join(site, "oink-main", "oink-main", "assets", "third_party", "mermaid", "mermaid.min.js")]
    cands += glob.glob(os.path.join(site, "themes", "**", "mermaid.min.js"), recursive=True)
    cands += glob.glob(os.path.join(site, "**", "third_party", "mermaid", "mermaid.min.js"), recursive=True)
    for c in cands:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None


def collect(docs):
    items = []
    for dirpath, _, filenames in os.walk(docs):
        for f in sorted(filenames):
            if not f.endswith(".md"):
                continue
            p = os.path.join(dirpath, f)
            text = open(p, encoding="utf-8").read()
            for i, src in enumerate(BLOCK_RE.findall(text), start=1):
                items.append({
                    "file": os.path.relpath(p, docs).replace(os.sep, "/"),
                    "index": i,
                    "source": src.rstrip("\n"),
                })
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--mermaid-js")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    site = os.path.abspath(a.site)
    docs = os.path.join(site, "content", "docs")
    out_dir = os.path.abspath(a.out or os.path.join(site, "_mermaid-harness"))
    if not os.path.isdir(docs):
        print(f"FAIL 没有 {docs}")
        sys.exit(2)

    js = find_mermaid_js(site, a.mermaid_js)
    if not js:
        print("FAIL 找不到主题自带的 mermaid.min.js；用 --mermaid-js 指定绝对路径")
        sys.exit(2)

    items = collect(docs)
    if a.selftest:
        items = [
            {"file": "SELFTEST", "index": 1, "source": GOOD_SELFTEST.rstrip("\n")},
            {"file": "SELFTEST", "index": 2, "source": BAD_SELFTEST.rstrip("\n")},
        ] + items

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(js, os.path.join(out_dir, "mermaid.min.js"))
    with open(os.path.join(out_dir, "blocks.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(HARNESS)

    print(f"mode={'selftest+real' if a.selftest else 'real'} blocks={len(items)} js={js}")
    print(f"out={out_dir}")
    print("下一步（三条命令按序执行，服务必须走 http，file:// 下 fetch 会被拦）：")
    print(f"  1) python -m http.server 8765 --directory \"{out_dir}\"   # 后台运行")
    print(f"  2) 浏览器打开 http://127.0.0.1:8765/index.html")
    print("  3) 读回页面文本（#out 与 window.__HEADLINE）：期望 SELFTEST=1/2 后 SELFTEST_PASS 且 REAL_FAIL=0 / HEADLINE=GREEN")
    if a.selftest:
        injected = [x for x in items if x["file"] == "SELFTEST"]
        st_ok = len(injected) == 2
        print("harness_selftest: injected=%d %s（真解析仍需浏览器，属 MANUAL）"
              % (len(injected), "PASS" if st_ok else "FAIL"))
        print("SELFTEST_PASS" if st_ok else "SELFTEST_INVALID")
        sys.exit(0 if st_ok else 1)


if __name__ == "__main__":
    main()
