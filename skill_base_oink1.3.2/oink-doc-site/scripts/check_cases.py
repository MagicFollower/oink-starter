"""实验验证案例包判据：源目录、zip、static 副本、文档引用四方一致，且包内是「最小完整」。

用法：
  python check_cases.py --site <站点目录> [--max-file-kb 10240]
  python check_cases.py --selftest

退出码：0 = 无问题；1 = 有问题；2 = 没有 cases/（本轮没有实验验证案例，不是失败）。

判据口径（四方 + 最小完整）：

  cases/<主题>/<案例>/.gitignore        排除清单的唯一来源，--init 会写基线
  cases/<主题>/<案例>/README.md         介绍与使用手册，8 个小节都要有正文
  cases/<主题>/<案例>.zip               打包产物，条目 `<案例>/` 前缀 + 正斜杠
  static/cases/<主题>/<案例>.zip        发布副本，与源 zip 字节一致；构建后进 public/
  content/**/*.md                       至少一篇用真实 Markdown 链接引用该 zip

「最小完整」= 读者只看包内就能复现：手册、脚本、必要数据都在；依赖（node_modules、
__pycache__、.venv）、构建产物（dist、build）、密钥（.env、*.pem）与超大文件都不在。
"""

import argparse
import fnmatch
import hashlib
import io
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import check_links  # noqa: E402

REQUIRED_SECTIONS = (
    "## 案例简介",
    "## 适用文档",
    "## 前置条件",
    "## 运行步骤",
    "## 预期结果与判据",
    "## 包内容清单",
    "## 复现记录",
    "## 清理与回滚",
)
CASE_ZIP = re.compile(r"cases/[^)\s]+?\.zip$")

# 硬排除：这些路径永远不该进案例包，出现即判红（DEP_IN_ZIP）
HARD_DENY_DIRS = {"node_modules", "__pycache__", ".venv", "venv", ".git", ".idea", ".vscode",
                  ".pytest_cache", ".mypy_cache", ".ruff_cache", ".pnpm-store",
                  "dist", "build", "out", "target", "coverage", ".tmp", ".temp"}
HARD_DENY_SUFFIX = (".pyc", ".pyo")
HARD_DENY_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
# 密钥类：出现即拒绝打包并判红，别指望「顺手带上」
SECRET_NAMES = {".env", ".netrc", "credentials.json", "secrets.json", "id_rsa"}
SECRET_SUFFIX = (".pem", ".key", ".p12", ".pfx", ".jks")

BASELINE_IGNORE = """# 案例包排除清单：package_case.py 按这份规则打 zip，git 按同一份规则忽略。
# 需要带上某个默认排除项时，删掉对应行即可；不要往包里塞依赖目录。
node_modules/
__pycache__/
*.pyc
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.pnpm-store/
dist/
build/
out/
target/
coverage/
.idea/
.vscode/
.tmp/
.DS_Store
Thumbs.db
desktop.ini
"""


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def rel(site, path):
    return os.path.relpath(path, site).replace(os.sep, "/")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ignore(cdir):
    """读案例目录的 .gitignore，只支持三种形态：`dir/`、`*.ext`、`path/` 前缀。"""
    path = os.path.join(cdir, ".gitignore")
    dirs, patterns, prefixes = set(), [], set()
    if not os.path.isfile(path):
        return dirs, patterns, prefixes
    for line in read(path).splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        neg = raw.startswith("!")
        if neg:
            continue  # 不支持反向规则；出现即被忽略，作者要排除就别写 !
        entry = raw.rstrip("/")
        if not entry:
            continue
        if "*" in entry or "?" in entry:
            patterns.append(entry.lstrip("/"))
        elif raw.endswith("/") or "/" in raw:
            prefixes.add(entry.lstrip("/") + "/")
            if "/" not in entry:
                dirs.add(entry)
        else:
            dirs.add(entry)
    return dirs, patterns, prefixes


def ignored(relpath, rules):
    dirs, patterns, prefixes = rules
    parts = relpath.split("/")
    for seg in parts[:-1]:
        if seg in HARD_DENY_DIRS or seg in dirs:
            return True
    name = parts[-1]
    if name in HARD_DENY_NAMES or name in dirs:
        return True
    if name.endswith(HARD_DENY_SUFFIX):
        return True
    for pre in prefixes:
        if relpath.startswith(pre):
            return True
    for pat in patterns:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(relpath, pat):
            return True
    return False


def deny_hit(relpath):
    """zip 里出现这些路径就是打包漏了过滤，判红而不是静默剔除。"""
    parts = relpath.split("/")
    return (any(seg in HARD_DENY_DIRS for seg in parts[:-1])
            or parts[-1] in HARD_DENY_NAMES or parts[-1].endswith(HARD_DENY_SUFFIX))


def secret_hit(relpath):
    name = relpath.split("/")[-1]
    return name in SECRET_NAMES or name.endswith(SECRET_SUFFIX)


def iter_files(cdir, rules=None):
    """返回 (要进包的相对路径, 被排除的相对路径)；按 .gitignore + 硬排除过滤。"""
    rules = rules or load_ignore(cdir)
    keep, dropped = [], []
    for dp, dirs, fns in os.walk(cdir):
        dirs[:] = sorted(dirs)
        for f in sorted(fns):
            full = os.path.join(dp, f)
            r = os.path.relpath(full, cdir).replace(os.sep, "/")
            (dropped if ignored(r, rules) else keep).append(r)
    return keep, dropped


def list_cases(site):
    root = os.path.join(site, "cases")
    out = []
    if not os.path.isdir(root):
        return out
    for theme in sorted(os.listdir(root)):
        tdir = os.path.join(root, theme)
        if not os.path.isdir(tdir):
            continue
        for case in sorted(os.listdir(tdir)):
            if os.path.isdir(os.path.join(tdir, case)):
                out.append((theme, case))
    return out


def case_paths(site, theme, case):
    tdir = os.path.join(site, "cases", theme)
    return {
        "dir": os.path.join(tdir, case),
        "ignore": os.path.join(tdir, case, ".gitignore"),
        "manual": os.path.join(tdir, case, "README.md"),
        "zip": os.path.join(tdir, case + ".zip"),
        "static": os.path.join(site, "static", "cases", theme, case + ".zip"),
        "public": os.path.join(site, "public", "cases", theme, case + ".zip"),
        "url": "cases/%s/%s.zip" % (theme, case),
    }


def zip_items(path):
    with zipfile.ZipFile(path) as z:
        return [(i.filename, i.file_size) for i in z.infolist()]


def zip_entries(path):
    return [n for n, _ in zip_items(path)]


def section_bodies(text):
    """返回 {小节标题: 正文行数}，正文指非空且不是标题/引用的行。"""
    out = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            out.setdefault(current, 0)
            continue
        if current and line.strip() and not line.startswith(("#", ">")):
            out[current] += 1
    return out


def manual_problems(site, theme, case):
    p = case_paths(site, theme, case)
    problems = []
    if not os.path.isfile(p["ignore"]):
        problems.append(("NO_CASE_IGNORE", rel(site, p["ignore"]),
                         "缺排除清单；跑 package_case.py --init 生成基线"))
    if not os.path.isfile(p["manual"]):
        problems.append(("NO_MANUAL", rel(site, p["manual"]), "缺介绍与使用手册"))
        return problems
    text = read(p["manual"])
    missing = [s for s in REQUIRED_SECTIONS
               if not re.search(r"^%s\s*$" % re.escape(s), text, re.M)]
    if missing:
        problems.append(("MANUAL_SECTION", rel(site, p["manual"]), "缺小节：" + "、".join(missing)))
    if "【" in text:
        problems.append(("MANUAL_PLACEHOLDER", rel(site, p["manual"]), "手册仍有全角中括号占位未填"))
    bodies = section_bodies(text)
    thin = [s for s in REQUIRED_SECTIONS if s in bodies and bodies[s] == 0]
    if thin:
        problems.append(("MANUAL_THIN", rel(site, p["manual"]), "空小节：" + "、".join(thin)))
    return problems


def zip_problems(site, theme, case, max_file_bytes):
    p = case_paths(site, theme, case)
    problems = []
    if not os.path.isfile(p["zip"]):
        problems.append(("NO_ZIP", rel(site, p["zip"]), "先跑 package_case.py 打包"))
        return problems
    items = zip_items(p["zip"])
    names = [n for n, _ in items]
    if not names:
        problems.append(("EMPTY_ZIP", rel(site, p["zip"]), "zip 里没有任何文件"))
        return problems
    bad = [e for e in names
           if "\\" in e or e.startswith("/") or ".." in e.split("/") or not e.startswith(case + "/")]
    if bad:
        problems.append(("BAD_ZIP_ENTRY", rel(site, p["zip"]),
                         "首条异常条目：%s（要求以 `%s/` 开头且用正斜杠）" % (bad[0], case)))
    if "%s/README.md" % case not in names:
        problems.append(("NO_MANUAL_IN_ZIP", rel(site, p["zip"]), "包里没有手册，读者拿到没法复现"))
    dep = [e for e in names if deny_hit(e)]
    if dep:
        problems.append(("DEP_IN_ZIP", rel(site, p["zip"]),
                         "把依赖/产物打进包了：%s（共 %d 条，改 .gitignore 后重打包）"
                         % (dep[0], len(dep))))
    sec = [e for e in names if secret_hit(e)]
    if sec:
        problems.append(("SECRET_IN_ZIP", rel(site, p["zip"]),
                         "包里有疑似密钥文件：%s（删掉或换成 .env.example 再打包）" % ", ".join(sec[:3])))
    big = [(e, s) for e, s in items if s > max_file_bytes]
    if big:
        problems.append(("OVERSIZE_FILE", rel(site, p["zip"]),
                         "%s = %d 字节，超过上限 %d；这类产物应写再生成命令而不是入库"
                         % (big[0][0], big[0][1], max_file_bytes)))
    return problems


def case_refs(site):
    refs = {}
    content = os.path.join(site, "content")
    if not os.path.isdir(content):
        return refs
    for dp, _, fns in os.walk(content):
        for f in sorted(fns):
            if not f.endswith(".md"):
                continue
            md = os.path.join(dp, f)
            origin = rel(site, md)
            body = check_links.strip_noncontent(read(md))
            for m in check_links.LINK.finditer(body):
                target = urllib.parse.unquote(m.group(2).split("#")[0])
                hit = CASE_ZIP.search(target)
                if hit:
                    refs.setdefault(hit.group(0), []).append(origin)
    return refs


def check(site, max_file_kb=10240):
    site = os.path.abspath(site)
    root = os.path.join(site, "cases")
    if not os.path.isdir(root):
        raise OSError("无 cases/ 目录：本轮没有实验验证案例（verify_site 按 SKIP 处理）")
    max_bytes = int(max_file_kb) * 1024
    problems = []
    cases = list_cases(site)
    refs = case_refs(site)
    has_public = os.path.isdir(os.path.join(site, "public"))

    for theme, case in cases:
        p = case_paths(site, theme, case)
        problems.extend(manual_problems(site, theme, case))
        problems.extend(zip_problems(site, theme, case, max_bytes))

        if os.path.isfile(p["zip"]) and not os.path.isfile(p["static"]):
            problems.append(("NO_STATIC_ZIP", rel(site, p["static"]), "发布副本缺失，站点上下载不到"))
        elif os.path.isfile(p["zip"]) and os.path.isfile(p["static"]) \
                and sha256(p["zip"]) != sha256(p["static"]):
            problems.append(("ZIP_MISMATCH", rel(site, p["static"]), "与 cases/ 下的 zip 字节不一致（改完没重打包）"))

        if p["url"] not in refs:
            problems.append(("UNREFERENCED", p["url"], "没有 content/**/*.md 引用它"))
        if has_public and not os.path.isfile(p["public"]):
            problems.append(("NOT_IN_PUBLIC", rel(site, p["public"]),
                             "static 副本没进 public/（构建没跑，或被 .gitignore/部署漏拷）"))

    for target, origins in sorted(refs.items()):
        if not (os.path.isfile(os.path.join(site, "static", target.replace("/", os.sep)))
                or os.path.isfile(os.path.join(site, target.replace("/", os.sep)))):
            problems.append(("BROKEN_CASE_LINK", origins[0], "引用了不存在的案例包：" + target))

    stats = {"cases": len(cases), "themes": len(set(t for t, _ in cases)),
             "doc_links": len(refs), "public": has_public, "max_file_kb": max_file_kb}
    return problems, stats


def print_result(problems, stats):
    print("cases=%d themes=%d doc_links=%d public=%s max_file_kb=%d problems=%d"
          % (stats["cases"], stats["themes"], stats["doc_links"], stats["public"],
             stats["max_file_kb"], len(problems)))
    for code, target, detail in problems[:40]:
        print("  %s %s：%s" % (code, target, detail))
    if len(problems) > 40:
        print("  ...另有 %d 条" % (len(problems) - 40))


# --------------------------------------------------------------------------- selftest

GOOD_MANUAL = "\n".join(
    ["# 慢查询复现——介绍与使用手册", "> 主题：04-ops", ""]
    + [s + "\n\n本节已填写，用于验证判据绿灯。" for s in REQUIRED_SECTIONS] + [""])

ALL_CODES = ("NO_MANUAL", "MANUAL_SECTION", "MANUAL_PLACEHOLDER", "MANUAL_THIN", "NO_CASE_IGNORE",
             "NO_ZIP", "EMPTY_ZIP", "BAD_ZIP_ENTRY", "NO_MANUAL_IN_ZIP", "DEP_IN_ZIP",
             "SECRET_IN_ZIP", "OVERSIZE_FILE", "NO_STATIC_ZIP", "ZIP_MISMATCH",
             "UNREFERENCED", "BROKEN_CASE_LINK", "NOT_IN_PUBLIC")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def make_zip(zip_path, cdir, case, extra=None, drop_manual=False, names=None):
    """按源目录重打 zip；extra 用于注入坏条目，names 可完全接管条目清单。"""
    if names is not None:
        entries = names
    else:
        keep, _ = iter_files(cdir)
        entries = ["%s/%s" % (case, r) for r in keep]
    if drop_manual:
        entries = [e for e in entries if not e.endswith("/README.md")]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for e in entries:
            src = os.path.join(cdir, e.split("/", 1)[1].replace("/", os.sep))
            if os.path.isfile(src):
                z.write(src, e)
            else:
                z.writestr(e, "injected\n")
        for e in (extra or []):
            z.writestr(e, "x" * 40)


def build_case_site(root):
    site = os.path.join(root, "site")
    theme, case = "04-ops", "slow-query"
    cdir = os.path.join(site, "cases", theme, case)
    os.makedirs(os.path.join(cdir, "data"), exist_ok=True)
    write(os.path.join(cdir, ".gitignore"), BASELINE_IGNORE)
    write(os.path.join(cdir, "README.md"), GOOD_MANUAL)
    write(os.path.join(cdir, "run.cmd"), "netstat -ano | findstr 3080\n")
    write(os.path.join(cdir, "data", "rows.csv"), "id,ms\n" + "".join("%d,42\n" % i for i in range(400)))
    zp = os.path.join(site, "cases", theme, case + ".zip")
    make_zip(zp, cdir, case)
    os.makedirs(os.path.join(site, "static", "cases", theme), exist_ok=True)
    shutil.copyfile(zp, os.path.join(site, "static", "cases", theme, case + ".zip"))
    os.makedirs(os.path.join(site, "public", "cases", theme), exist_ok=True)
    shutil.copyfile(zp, os.path.join(site, "public", "cases", theme, case + ".zip"))
    write(os.path.join(site, "content", "docs", "04-ops", "slow.md"),
          "---\ntitle: \"慢查询复现\"\n---\n\n"
          "判据来自案例包：[slow-query.zip](/cases/04-ops/slow-query.zip)\n")
    return site, theme, case


def selftest():
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-cases-", dir=os.path.abspath(root))
    want = set(ALL_CODES)
    ok = True
    seen = set()
    try:
        site, theme, case = build_case_site(tmp)
        cdir = os.path.join(site, "cases", theme, case)
        zp = os.path.join(site, "cases", theme, case + ".zip")
        manual = os.path.join(cdir, "README.md")
        doc = os.path.join(site, "content", "docs", "04-ops", "slow.md")
        problems, stats = check(site)
        print("green: cases=%d doc_links=%d entries=%d problems=%d"
              % (stats["cases"], stats["doc_links"], len(zip_entries(zp)), len(problems)))
        if problems:
            ok = False
            for code, target, detail in problems:
                print("  意外红 %s %s：%s" % (code, target, detail))

        def snapshot():
            files = [manual, doc, zp, os.path.join(cdir, ".gitignore"),
                     os.path.join(site, "static", "cases", theme, case + ".zip"),
                     os.path.join(site, "public", "cases", theme, case + ".zip")]
            return {f: (open(f, "rb").read() if os.path.isfile(f) else None) for f in files}

        def restore(snap):
            for f, data in snap.items():
                if data is None:
                    if os.path.isfile(f):
                        os.remove(f)
                else:
                    os.makedirs(os.path.dirname(f), exist_ok=True)
                    with open(f, "wb") as h:
                        h.write(data)

        def inject(label, code, mutate, max_kb=10240):
            nonlocal ok
            snap = snapshot()
            mutate()
            obs = {c for c, _, _ in check(site, max_file_kb=max_kb)[0]}
            print("%-24s observed=%s（期望含 %s）" % (label, ",".join(sorted(obs)) or "-", code))
            if code not in obs:
                ok = False
            else:
                seen.add(code)
            restore(snap)

        inject("missing manual", "NO_MANUAL", lambda: os.remove(manual))
        inject("manual section cut", "MANUAL_SECTION",
               lambda: write(manual, GOOD_MANUAL.replace("## 复现记录", "## 别的名字")))
        inject("manual placeholder", "MANUAL_PLACEHOLDER",
               lambda: write(manual, GOOD_MANUAL + "\n【待填】\n"))
        inject("manual empty section", "MANUAL_THIN",
               lambda: write(manual, GOOD_MANUAL.replace(
                   "## 复现记录\n\n本节已填写，用于验证判据绿灯。", "## 复现记录\n")))
        inject("missing .gitignore", "NO_CASE_IGNORE", lambda: os.remove(os.path.join(cdir, ".gitignore")))
        inject("zip deleted", "NO_ZIP", lambda: os.remove(zp))
        inject("zip empty", "EMPTY_ZIP", lambda: zipfile.ZipFile(zp, "w").close())
        inject("zip bad entry", "BAD_ZIP_ENTRY",
               lambda: make_zip(zp, cdir, case, names=["other/README.md"]))
        inject("zip without manual", "NO_MANUAL_IN_ZIP",
               lambda: make_zip(zp, cdir, case, drop_manual=True))
        inject("zip has deps", "DEP_IN_ZIP",
               lambda: make_zip(zp, cdir, case, extra=[case + "/node_modules/x/index.js"]))
        inject("zip has secret", "SECRET_IN_ZIP",
               lambda: make_zip(zp, cdir, case, extra=[case + "/.env"]))
        inject("zip oversize", "OVERSIZE_FILE", lambda: None, max_kb=1)
        inject("static zip missing", "NO_STATIC_ZIP",
               lambda: os.remove(os.path.join(site, "static", "cases", theme, case + ".zip")))
        inject("static zip drift", "ZIP_MISMATCH",
               lambda: _append(os.path.join(site, "static", "cases", theme, case + ".zip"), b"x"))
        inject("doc reference removed", "UNREFERENCED",
               lambda: write(doc, "---\ntitle: \"慢查询复现\"\n---\n\n正文没有链接。\n"))
        inject("doc link broken", "BROKEN_CASE_LINK",
               lambda: write(doc, "[ghost.zip](/cases/04-ops/ghost.zip)\n"))
        inject("zip not in public", "NOT_IN_PUBLIC",
               lambda: os.remove(os.path.join(site, "public", "cases", theme, case + ".zip")))

        missing = sorted(want - seen)
        if missing:
            ok = False
            print("SELFTEST_INVALID 未命中的错误码：" + "、".join(missing))
        print("cases: codes_hit=%d/%d" % (len(seen), len(want)))
        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _append(path, data):
    with open(path, "ab") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--max-file-kb", type=int, default=10240,
                    help="单个文件字节上限，超过判 OVERSIZE_FILE；默认 10240 = 10 MiB")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.site:
        print("FAIL 需要 --site（或 --selftest）")
        sys.exit(2)
    try:
        problems, stats = check(a.site, a.max_file_kb)
    except OSError as e:
        print("FAIL %s" % e)
        sys.exit(2)
    print_result(problems, stats)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
