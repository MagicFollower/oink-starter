"""站内链接检查：以 public/ 真实产物为判据，不猜 Hugo 的 URL 规则。

用法：先 hugo --cleanDestinationDir，再
  python check_links.py --site <站点目录> [--content content]
  python check_links.py --selftest

退出码：0 = 无 broken 且无 unmapped；1 = 有问题；2 = 没有 public/（构建没跑）。

覆盖三类链接来源：
  1) content/**/*.md 正文里的 [文本](目标)
  2) content/**/_index.md 与 leaf bundle 的 index.md（含 `{.cards}` 列表）
  3) data/home/*.yaml 里 hero/cards/cta 的 `url:` 字段

每条源文件先确认自己在 public/ 里的落地目录真的存在，不存在报 UNMAPPED：
那说明 URL 推断与产物不一致（leaf bundle、uglyURLs、disablePathToLower 之类），
此时 broken 数字已经不可信，必须先对齐再看链接。

第四类判据是**产物资源 URL**：解析 `public/**/*.html` 里的 `<link rel=stylesheet>`、
`<script src>`、`<img src>`，按页面所在目录还原浏览器会请求的路径，落不到文件就报
`ASSET_404`。目标按浏览器口径解析：百分号编码先还原，目录也算命中（看目录下的
`index.html`，以及 uglyURLs 的 `.html` 形态）。

这一条专治「页面 200 但样式全丢」：`relativeURLs` 遇上带路径的 `baseURL`
会把子路径烤进资源 URL，从子路径页面再解析就成了双前缀。

只认真实链接：HTML 注释、围栏代码块、行内代码里的 `[文本](目标)` 一律先剥掉，
YAML 里整行注释掉的 `# url:` 也不计入 home_urls。
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.parse

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ASSET_TAG = re.compile(r"<(?:link|script|img)\b[^>]*?>", re.I)
ASSET_ATTR = re.compile(r"\b(?:href|src)\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
ASSET_SKIP = ("http://", "https://", "mailto:", "tel:", "#", "data:", "//", "blob:")
YAML_URL = re.compile(r"(?:^|[\s{,])(?:url|link)\s*:\s*[\"']?([^\s\"'#,}]+)", re.M)
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "#", "//")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE_LINE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"`[^`\n]*`")


def strip_noncontent(text):
    """去掉 HTML 注释、围栏代码块、行内代码：这三处的链接不是链接，是说明文本。"""
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
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def asset_exists(pub, target):
    """资源目标是否落地：文件本体、目录下的 index.html、以及 uglyURLs 的 .html 形态。"""
    target = urllib.parse.unquote(target)
    base = os.path.join(pub, target.replace("/", os.sep))
    for cand in (base, os.path.join(base, "index.html"), base + ".html"):
        if os.path.isfile(cand):
            return True
    return False


def asset_targets(page_rel, html):
    """产出一页里所有需要落地的资源目标（posix 相对 public 的路径）。"""
    import posixpath
    out = []
    for tag in ASSET_TAG.findall(html):
        m = ASSET_ATTR.search(tag)
        if not m:
            continue
        href = m.group(1).strip("\"'")
        if not href or href.startswith(ASSET_SKIP):
            continue
        href = href.split("#")[0].split("?")[0]
        if not href:
            continue
        if href.startswith("/"):
            target = href[1:]
        else:
            target = posixpath.normpath(posixpath.join(posixpath.dirname(page_rel), href)).lstrip("/")
        if target:
            out.append((href, target))
    return out


def check_assets(site):
    """扫 public/**/*.html 的资源指向；返回 broken 列表（origin 用产物路径）。"""
    pub = os.path.join(site, "public")
    broken, checked = [], 0
    pages = 0
    for dp, _, fns in os.walk(pub):
        for f in sorted(fns):
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            page_rel = os.path.relpath(p, pub).replace(os.sep, "/")
            pages += 1
            html = read(p)
            for href, target in asset_targets(page_rel, html):
                checked += 1
                if not asset_exists(pub, target):
                    broken.append(("public/" + page_rel, "%s -> 缺 public/%s" % (href, target)))
    return broken, {"asset_pages": pages, "assets_checked": checked}


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


def check(site, content_name="content"):
    site = os.path.abspath(site)
    content = os.path.join(site, content_name)
    pub = os.path.join(site, "public")
    data_home = os.path.join(site, "data", "home")
    if not os.path.isdir(pub):
        raise OSError("FAIL 无 public/，先跑 hugo --cleanDestinationDir（判据是产物，不是源文件）")
    if not os.path.isdir(content):
        raise OSError("FAIL 无 %s" % content)

    ugly, lower = site_flags(site)

    def public_paths(parts):
        if not parts:
            return ["index.html"]
        if ugly:
            return ["/".join(parts) + ".html", "/".join(parts) + "/index.html"]
        return ["/".join(parts) + "/index.html", "/".join(parts) + ".html"]

    def exists_site(path):
        rel = path.lstrip("/")
        if not rel:
            rel = "index.html"
        f = os.path.join(pub, rel.replace("/", os.sep))
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
    for dp, _, fns in os.walk(content):
        for f in sorted(fns):
            if f.endswith(".md"):
                mds.append(os.path.join(dp, f))

    for md in sorted(mds):
        rel_md = os.path.relpath(md, site).replace(os.sep, "/")
        rel = os.path.relpath(md, content).replace(os.sep, "/")
        parts = rel.split("/")
        base = parts[-1]
        if base in ("_index.md", "index.md"):
            parts = parts[:-1]
        else:
            parts[-1] = re.sub(r"\.md$", "", base)
        if lower:
            parts = [p.lower() for p in parts]
        cands = public_paths(parts)
        if not any(os.path.isfile(os.path.join(pub, c.replace("/", os.sep))) for c in cands):
            unmapped.append((rel_md, "、".join(cands)))
        page = "/" + "/".join(parts) + "/" if parts else "/"
        body = strip_noncontent(read(md).split("---\n", 2)[-1])
        for m in LINK.finditer(body):
            resolve(m.group(2), page, rel_md)

    if os.path.isdir(data_home):
        for f in sorted(os.listdir(data_home)):
            if not f.endswith((".yaml", ".yml")):
                continue
            p = os.path.join(data_home, f)
            origin = os.path.relpath(p, site).replace(os.sep, "/")
            live = "\n".join(l for l in read(p).splitlines() if not l.lstrip().startswith("#"))
            for m in YAML_URL.finditer(live):
                home_urls += 1
                resolve(m.group(1), "/", origin)

    asset_broken, asset_stats = check_assets(site)
    broken = broken + asset_broken
    stats = {"checked": checked, "skipped": skipped, "home_urls": home_urls,
             "ugly": ugly, "lower": lower}
    stats.update(asset_stats)
    return broken, unmapped, stats


def print_result(broken, unmapped, stats):
    print("links_checked=%d external_or_anchor=%d home_urls=%d broken=%d unmapped=%d uglyURLs=%s lowercase=%s "
          "assets(pages=%d checked=%d)"
          % (stats["checked"], stats["skipped"], stats["home_urls"], len(broken),
             len(unmapped), stats["ugly"], stats["lower"],
             stats.get("asset_pages", 0), stats.get("assets_checked", 0)))
    for p, t in broken[:40]:
        print("  BROKEN", p, "->", t)
    if len(broken) > 40:
        print("  ...另有 %d 条" % (len(broken) - 40))
    for p, t in unmapped[:20]:
        print("  UNMAPPED", p, "-> public/ 里找不到", t)
    if unmapped:
        print("  提示：UNMAPPED 非零时 broken 数字不可信，先对齐 URL 规则（leaf bundle / uglyURLs / disablePathToLower）")


def build_stub_public(root, skip_names):
    content = os.path.join(root, "content")
    pub = os.path.join(root, "public")
    made = 0
    for dp, _, fns in os.walk(content):
        for f in fns:
            if not f.endswith(".md") or f in skip_names:
                continue
            rel = os.path.relpath(os.path.join(dp, f), content).replace(os.sep, "/")
            parts = rel.split("/")
            if parts[-1] in ("_index.md", "index.md"):
                parts = parts[:-1]
            else:
                parts[-1] = re.sub(r"\.md$", "", parts[-1])
            parts = [p.lower() for p in parts]
            target = os.path.join(pub, *parts) if parts else pub
            os.makedirs(target, exist_ok=True)
            io.open(os.path.join(target, "index.html"), "w", encoding="utf-8", newline="\n").write(
                "<!doctype html><title>stub</title>\n")
            made += 1
    return made


def selftest():
    skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixtures = os.path.join(skill, "assets", "fixtures")
    exp = json.load(io.open(os.path.join(fixtures, "expected.json"), encoding="utf-8"))
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-links-", dir=os.path.abspath(root))
    ok = True
    try:
        site = os.path.join(tmp, "site")
        shutil.copytree(os.path.join(fixtures, "site"), site)
        made = build_stub_public(site, {"unmapped.md"})
        broken, unmapped, stats = check(site)
        obs = {}
        for p, t in broken:
            obs.setdefault(p, set()).add("BROKEN")
        for p, t in unmapped:
            obs.setdefault(p, set()).add("UNMAPPED")
        obs = {k: sorted(v) for k, v in obs.items()}
        want = {k: sorted(v) for k, v in exp["links"].items()}
        if obs != want:
            ok = False
            print("SELFTEST_INVALID 链接明细不符")
            for k in sorted(set(obs) | set(want)):
                if obs.get(k) != want.get(k):
                    print("  %s observed=%s expected=%s" % (k, obs.get(k), want.get(k)))
        if not (broken and unmapped):
            ok = False
            print("SELFTEST_INVALID 红样本没有同时触发 BROKEN 与 UNMAPPED")
        print("links: stub_public_pages=%d %s" % (made, "observed_codes=%d" % len(obs)))
        asset_ok = asset_selfprobe(site)
        ok = ok and asset_ok
        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def asset_selfprobe(site):
    """证明 ASSET_404 判据会红、且不会因编码/目录形态假红。

    三件事一起验：坏资源必须被报；好资源（同目录文件、子目录文件、目录型链接）
    必须不报；中文目录的百分号编码必须还原后再判，否则会把存在的页面报成缺。
    """
    import urllib.parse
    pub = os.path.join(site, "public")
    page_dir = os.path.join(pub, "asset-probe")
    sub_dir = os.path.join(page_dir, "sub")
    cn_dir = os.path.join(page_dir, "\u4e2d\u6587\u76ee\u5f55")
    for d in (page_dir, sub_dir, cn_dir):
        os.makedirs(d, exist_ok=True)
    io.open(os.path.join(page_dir, "good.css"), "w", encoding="utf-8").write("/* ok */\n")
    for d in (sub_dir, cn_dir):
        io.open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n").write(
            "<!doctype html><title>probe</title>\n")
    cn_href = "./%s/" % urllib.parse.quote("\u4e2d\u6587\u76ee\u5f55".encode("utf-8"), safe="")
    io.open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8", newline="\n").write(
        "<!doctype html><title>probe</title>"
        '<link rel="stylesheet" href="good.css">'
        '<link rel="stylesheet" href="./sub/../good.css">'
        '<link rel="next" href="sub/">'
        '<link rel="alternate" href="%s">'
        '<link rel="stylesheet" href="./missing/main.css">'
        "<script src=\"https://example.com/x.js\"></script>" % cn_href)
    broken, stats = check_assets(site)
    hits = [b for b in broken if b[0].endswith("asset-probe/index.html")]
    good_count = stats.get("assets_checked", 0)
    ok = (len(hits) == 1 and "missing/main.css" in hits[0][1] and good_count >= 5)
    print("asset_probe: 报红=%d（期望 1，只报缺的那个）checked=%d %s"
          % (len(hits), good_count, "OK" if ok else "MISS"))
    for origin, detail in hits:
        print("   ", detail)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--content", default="content", help="内容目录名，默认 content")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.site:
        print("FAIL 需要 --site（或 --selftest）")
        sys.exit(2)
    try:
        broken, unmapped, stats = check(a.site, a.content)
    except OSError as e:
        print("FAIL %s" % e)
        sys.exit(2)
    print_result(broken, unmapped, stats)
    sys.exit(1 if (broken or unmapped) else 0)


if __name__ == "__main__":
    main()
