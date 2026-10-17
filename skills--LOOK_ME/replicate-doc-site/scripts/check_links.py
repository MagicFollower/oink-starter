"""站内链接检查：以 public/ 真实产物为判据，不猜 Hugo 的 URL 规则。

用法：先 hugo --cleanDestinationDir，再
  python check_links.py --site <站点目录> [--content content]

退出码：0 = 无 broken 且无 unmapped；1 = 有问题；2 = 没有 public/（构建没跑）。

覆盖三类链接来源（旧版只有第 1 类，首页卡片因此是盲区）：
  1) content/**/*.md 正文里的 [文本](目标)
  2) content/**/_index.md 与 leaf bundle 的 index.md（含 `{.cards}` 列表）
  3) data/home/*.yaml 里 hero/cards/cta 的 `url:` 字段

每条源文件先确认自己在 public/ 里的落地目录真的存在，不存在报 UNMAPPED：
那说明 URL 推断与产物不一致（leaf bundle、uglyURLs、disablePathToLower 之类），
此时 broken 数字已经不可信，必须先对齐再看链接。

只认真实链接：HTML 注释、围栏代码块、行内代码里的 `[文本](目标)` 一律先剥掉，
YAML 里整行注释掉的 `# url:` 也不计入 home_urls——模板注释里的示例路径不是断链。
"""

import argparse
import os
import re
import sys
import urllib.parse

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
# 同时吃块式（`url: x` 独占一行）与流式（`- { label: a, url: x }`）两种 YAML 写法
YAML_URL = re.compile(r"(?:^|[\s{,])(?:url|link)\s*:\s*[\"']?([^\s\"'#,}]+)", re.M)
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "#", "//")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE_LINE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_noncontent(text):
    """去掉 HTML 注释、围栏代码块、行内代码：这三处的 [文本](目标) 不是链接，是说明文本。

    不剥就会把模板注释里的示例路径判成断链（骨架 content/docs/_index.md 的落地清单注释里
    就写着一条 `/docs/NN-目录名/` 示例），交付物里留着注释时永远是假红。
    """
    text = COMMENT.sub(" ", text)
    out, fencing = [], False
    for line in text.splitlines():
        if FENCE_LINE.match(line):
            fencing = not fencing
            continue
        if not fencing:
            out.append(line)
    return INLINE_CODE.sub(" ", "\n".join(out))


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def site_flags(site):
    """从 hugo.yaml/hugo.toml 读两个会改变 URL 形态的开关；读不到就按 Hugo 默认。"""
    ugly = lower = False
    for name in ("hugo.yaml", "hugo.yml", "hugo.toml", "config.yaml"):
        p = os.path.join(site, name)
        if os.path.isfile(p):
            t = read(p)
            ugly = bool(re.search(r"^\s*uglyURLs\s*:\s*true", t, re.M))
            lower = not bool(re.search(r"^\s*disablePathToLower\s*:\s*true", t, re.M))
            break
    return ugly, lower


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--content", default="content", help="内容目录名，默认 content（旧版写死 content/docs）")
    a = ap.parse_args()

    SITE = os.path.abspath(a.site)
    CONTENT = os.path.join(SITE, a.content)
    PUB = os.path.join(SITE, "public")
    DATA_HOME = os.path.join(SITE, "data", "home")
    if not os.path.isdir(PUB):
        print(f"FAIL 无 public/，先跑 hugo --cleanDestinationDir（判据是产物，不是源文件）")
        sys.exit(2)
    if not os.path.isdir(CONTENT):
        print(f"FAIL 无 {CONTENT}")
        sys.exit(2)

    ugly, lower = site_flags(SITE)

    def public_paths(parts):
        """返回该页在 public/ 下可接受的落地文件相对路径候选。"""
        if not parts:
            return ["index.html"]
        if ugly:
            return ["/".join(parts) + ".html", "/".join(parts) + "/index.html"]
        return ["/".join(parts) + "/index.html", "/".join(parts) + ".html"]

    def exists_site(path):
        rel = path.lstrip("/")
        if not rel:
            rel = "index.html"
        f = os.path.join(PUB, rel.replace("/", os.sep))
        return (os.path.isfile(f)
                or os.path.isfile(os.path.join(f, "index.html"))
                or os.path.isfile(f + ".html"))

    broken, unmapped = [], []
    checked = skipped = home_urls = 0

    def resolve(target, base_url, origin):
        nonlocal checked, skipped
        if target.startswith(EXTERNAL):
            skipped += 1
            return
        checked += 1
        raw = urllib.parse.unquote(target.split("#")[0])
        if not raw:
            return
        if raw.startswith("/"):
            shown = raw
        else:
            base = base_url
            while raw.startswith("../"):
                base = base.rstrip("/").rsplit("/", 1)[0] + "/"
                raw = raw[3:]
            raw = raw.lstrip("./")
            shown = (base if base.endswith("/") else base + "/") + raw
        if not exists_site(shown):
            broken.append((origin, shown))

    mds = []
    for dp, _, fns in os.walk(CONTENT):
        for f in sorted(fns):
            if f.endswith(".md"):
                mds.append(os.path.join(dp, f))

    for md in sorted(mds):
        rel_md = os.path.relpath(md, SITE).replace(os.sep, "/")
        rel = os.path.relpath(md, CONTENT).replace(os.sep, "/")
        parts = rel.split("/")
        base = parts[-1]
        if base in ("_index.md", "index.md"):
            parts = parts[:-1]
        else:
            parts[-1] = re.sub(r"\.md$", "", base)
        if lower:
            parts = [p.lower() for p in parts]
        cands = public_paths(parts)
        if not any(os.path.isfile(os.path.join(PUB, c.replace("/", os.sep))) for c in cands):
            unmapped.append((rel_md, "、".join(cands)))
        page = "/" + "/".join(parts) + "/" if parts else "/"
        body = strip_noncontent(read(md).split("---\n", 2)[-1])
        for m in LINK.finditer(body):
            resolve(m.group(2), page, rel_md)

    if os.path.isdir(DATA_HOME):
        for f in sorted(os.listdir(DATA_HOME)):
            if not f.endswith((".yaml", ".yml")):
                continue
            p = os.path.join(DATA_HOME, f)
            origin = os.path.relpath(p, SITE).replace(os.sep, "/")
            live = "\n".join(l for l in read(p).splitlines() if not l.lstrip().startswith("#"))
            for m in YAML_URL.finditer(live):
                home_urls += 1
                resolve(m.group(1), "/", origin)

    print(f"links_checked={checked} external_or_anchor={skipped} home_urls={home_urls} "
          f"broken={len(broken)} unmapped={len(unmapped)} uglyURLs={ugly} lowercase={lower}")
    for p, t in broken[:40]:
        print("  BROKEN", p, "->", t)
    if len(broken) > 40:
        print(f"  ...另有 {len(broken) - 40} 条")
    for p, t in unmapped[:20]:
        print("  UNMAPPED", p, "-> public/ 里找不到", t)
    if unmapped:
        print("  提示：UNMAPPED 非零时 broken 数字不可信，先对齐 URL 规则（leaf bundle / uglyURLs / disablePathToLower）")
    sys.exit(1 if (broken or unmapped) else 0)


if __name__ == "__main__":
    main()
