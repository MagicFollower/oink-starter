"""从 GitHub 仓库拉取源文档与配图，逐文件按 tree 元数据的字节数校验落地。

用法：
  python fetch_source.py --repo OWNER/REPO --ref BRANCH \
      --include "docs/**/*.md" --include "versioned_docs/**/*.md" \
      --out <暂存目录>/src
  python fetch_source.py --repo OWNER/REPO --ref BRANCH \
      --include "**/picture/**" --tail-after picture --out <site>/static/picture
  python fetch_source.py --selftest        # 只测 --include 的匹配语义，不联网

要点（都是实测结论）：
  * `--include` 用**严格 glob 语义**，不是 fnmatch：`*` 不跨 `/`，`**` 跨任意层，`?` 单字符。
    这条是踩过坑改的——fnmatch 里 `docs/**/*.md` **匹配不到** `docs/FAQ.md`（`**` 不表示
    「零或多层」），照抄文档示例会静默少取文件。现在每个 pattern 的命中数都会打印，
    命中 0 直接 WARN，不会再无声漏掉。
  * 直连 GitHub 的 release/资产下载会超时甚至截断，本脚本先直连、失败或字节数不符时
    自动改走 https://gh-proxy.com/<原 URL>，两条通道都失败才计为失败。
  * 每个文件都拿 tree 里的 size 比对，不符即判失败——截断比报错更阴。
  * --tail-after 用于把多棵 picture 树合并到同一个 static 根（上游按版本各存一份）。
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API = "https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"
MIRROR = "https://gh-proxy.com/"


def glob_to_re(pattern):
    """严格 glob → 正则：`**/` 吃零或多层目录，`**` 吃任意字符，`*` 不跨 `/`。"""
    out, i, n = [], 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if pattern.startswith("**", i):
                i += 2
                if i < n and pattern[i] == "/":
                    # `**/` 吃零或多层目录，所以 docs/**/*.md 也要命中 docs/FAQ.md
                    i += 1
                    out.append("(?:.*/)?")
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
            i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def match_any(path, patterns):
    return [p for p, rx in patterns if rx.match(path)]


def selftest():
    cases = [
        ("docs/**/*.md", "docs/FAQ.md", True),
        ("docs/**/*.md", "docs/00-introduction/01whychoose.md", True),
        ("docs/**/*.md", "docs/a/b/c.md", True),
        ("docs/*.md", "docs/FAQ.md", True),
        ("docs/*.md", "docs/00-introduction/01whychoose.md", False),
        ("**/picture/**", "static/picture/v5/mainarchi.png", True),
        ("versioned_docs/version-5.0/**/*.md", "docs/FAQ.md", False),
        ("docs/??.md", "docs/ab.md", True),
        ("docs/??.md", "docs/abc.md", False),
    ]
    bad = 0
    for pat, path, want in cases:
        got = bool(glob_to_re(pat).match(path))
        flag = "ok " if got == want else "BAD"
        if got != want:
            bad += 1
        print(f"  {flag} {pat:<34} {path:<44} want={want} got={got}")
    print(f"SELFTEST_CASES={len(cases)} BAD={bad}")
    print("SELFTEST_PASS" if bad == 0 else "SELFTEST_INVALID")
    return 0 if bad == 0 else 1


def get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "replicate-doc-site"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--ref")
    ap.add_argument("--include", action="append", default=[], help="可重复，严格 glob（** 跨层，* 不跨 /）")
    ap.add_argument("--out")
    ap.add_argument("--tail-after", help="按该标记切路径，只保留标记之后的部分（如 picture）")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--tree-cache", help="复用已下载的 tree JSON，避免重复打 API")
    ap.add_argument("--selftest", action="store_true", help="只测 include 匹配语义，不联网")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if not a.repo or not a.ref or not a.out:
        print("FAIL 需要 --repo / --ref / --out（或改用 --selftest）")
        sys.exit(2)
    if not a.include:
        print("FAIL 至少给一个 --include")
        sys.exit(2)

    if a.tree_cache and os.path.isfile(a.tree_cache):
        blob = json.loads(open(a.tree_cache, encoding="utf-8").read())
    else:
        blob = json.loads(get(API.format(repo=a.repo, ref=a.ref)).decode("utf-8"))
        if a.tree_cache:
            with open(a.tree_cache, "w", encoding="utf-8") as f:
                json.dump(blob, f)
    trees = blob.get("tree", [])
    if blob.get("truncated"):
        print("WARN tree 被截断，改用逐目录列举或缩小 --include")

    compiled = [(p, glob_to_re(p)) for p in a.include]
    hits = {p: 0 for p in a.include}
    wanted = []
    for x in trees:
        if x.get("type") != "blob":
            continue
        p = x["path"]
        matched = match_any(p, compiled)
        if not matched:
            continue
        for pat in matched:
            hits[pat] += 1
        wanted.append((p, x["size"]))
    for pat in a.include:
        print(f"  include {pat:<40} matched={hits[pat]}")
        if hits[pat] == 0:
            print(f"  WARN 这个 include 一个文件都没命中，检查 glob（* 不跨 /，跨层要写 **）")

    os.makedirs(a.out, exist_ok=True)
    done = [0]
    fail = []

    def one(item):
        path, size = item
        rel = path
        if a.tail_after:
            marker = a.tail_after + "/"
            if marker in path:
                rel = path.split(marker, 1)[1]
        dst = os.path.join(a.out, rel.replace("/", os.sep))
        url = RAW.format(repo=a.repo, ref=a.ref, path=urllib.parse.quote(path))
        for attempt, u in enumerate((url, MIRROR + url)):
            try:
                data = get(u)
            except Exception:  # noqa: BLE001
                if attempt:
                    fail.append((path, "两通道均失败"))
                continue
            if len(data) != size:
                if attempt == 0:
                    continue
                fail.append((path, f"字节不符 got={len(data)} want={size}"))
                break
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(data)
            done[0] += 1
            return

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        list(ex.map(one, wanted))

    total_bytes = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(a.out) for f in fs)
    print(f"wanted={len(wanted)} ok={done[0]} failed={len(fail)} out={a.out} bytes_on_disk={total_bytes:,}")
    for p, why in fail[:20]:
        print("  FAIL", p, why)
    if len(fail) > 20:
        print(f"  ...另有 {len(fail) - 20} 条")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
