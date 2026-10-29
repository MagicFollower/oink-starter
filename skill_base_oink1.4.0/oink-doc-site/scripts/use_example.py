"""把一个技能内的最小示例装进已脚手架的站点。

用法：
  python use_example.py --list
  python use_example.py --example <docs-min|gallery-min> --site <站点目录> [--force]
  python use_example.py --selftest

行为：复制 site.plan.json 与 content/**（合并，遇到已有正文会拒绝，除非 --force），
对 gallery-min 额外跑站点内的 make-placeholders.py 生成图片，最后执行 plan_site.py。
只读技能目录内的文件，不访问网络，也不引用技能目录之外的任何路径。
"""

import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
EXAMPLES = os.path.join(SKILL, "assets", "examples")

STUB_MARK = "OINK-STUB"


def examples():
    if not os.path.isdir(EXAMPLES):
        return []
    return sorted(d for d in os.listdir(EXAMPLES) if os.path.isdir(os.path.join(EXAMPLES, d)))


def has_real_content(site):
    """目标站点里是否已有非桩正文。"""
    docs = os.path.join(site, "content", "docs")
    for dp, _, fns in os.walk(docs):
        for f in fns:
            if not f.endswith(".md") or f == "_index.md":
                continue
            if STUB_MARK not in io.open(os.path.join(dp, f), encoding="utf-8").read():
                return os.path.join(dp, f)
    return None


def install(name, site, force=False, quiet=False):
    site = os.path.abspath(site)
    src = os.path.join(EXAMPLES, name)
    if not os.path.isdir(src):
        print("FAIL 没有示例 %s；可用：%s" % (name, "、".join(examples())))
        return 2
    if not os.path.isfile(os.path.join(site, "oink-main", "oink-main", "theme.toml")):
        print("FAIL %s 不是脚手架站点（缺 oink-main/oink-main/theme.toml）。先跑 scaffold.py --out <站点目录>" % site)
        return 2
    real = has_real_content(site)
    if real and not force:
        print("FAIL 站点已有正文：%s\n     要覆盖请加 --force（会保留不冲突的文件）" % real)
        return 1

    copied = 0
    plan_src = os.path.join(src, "site.plan.json")
    shutil.copy2(plan_src, os.path.join(site, "site.plan.json"))
    copied += 1
    content_src = os.path.join(src, "content")
    for dp, _, fns in os.walk(content_src):
        for f in fns:
            s = os.path.join(dp, f)
            rel = os.path.relpath(s, src)
            d = os.path.join(site, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            copied += 1
    for sub in ("scripts", "doc"):
        s_dir = os.path.join(src, sub)
        if not os.path.isdir(s_dir):
            continue
        for f in sorted(os.listdir(s_dir)):
            s = os.path.join(s_dir, f)
            d = os.path.join(site, sub, f)
            if os.path.exists(d):
                # 脚手架带来的 T0Level 模板还是占位态时，用示例里填好的那份覆盖
                stale = u"【" in io.open(d, encoding="utf-8").read()
                if not (stale and u"【" not in io.open(s, encoding="utf-8").read()):
                    continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            copied += 1
    if not quiet:
        print("example %s -> %s  copied=%d" % (name, site, copied))

    gen = os.path.join(site, "scripts", "make-placeholders.py")
    if os.path.isfile(gen):
        rc = subprocess.call([sys.executable, gen, site])
        if rc != 0:
            print("FAIL 图片生成器返回 %d" % rc)
            return rc
        if not quiet:
            print("generated images -> %s" % os.path.join(site, "content"))

    plan = os.path.join(site, "site.plan.json")
    rc = subprocess.call([sys.executable, os.path.join(HERE, "plan_site.py"),
                          "--site", site, "--plan", plan])
    if rc != 0:
        print("FAIL plan_site.py 返回 %d" % rc)
        return rc
    if not quiet:
        print("next: hugo --cleanDestinationDir && python %s --site %s --plan %s --mode skeleton"
              % (os.path.join(HERE, "verify_site.py"), site, plan))
    return 0


def selftest():
    ok = True
    root = os.path.join(os.environ.get("OINK_DOC_TMP") or tempfile.gettempdir(), "oink-example-probe")
    if os.path.isdir(root):
        shutil.rmtree(root)
    names = examples()
    print("examples=%s" % ",".join(names))
    if names != ["docs-min", "gallery-min"]:
        print("SELFTEST_INVALID 示例清单不符：%s" % names)
        return 1
    for name in names:
        site = os.path.join(root, name)
        # 最小脚手架标记：plan_site 只要求 oink-main/oink-main/theme.toml 存在
        os.makedirs(os.path.join(site, "oink-main", "oink-main"), exist_ok=True)
        theme_toml = os.path.join(site, "oink-main", "oink-main", "theme.toml")
        io.open(theme_toml, "w", encoding="utf-8").write('name = "OINK"\nmin_version = "0.168.0"\n')
        rc = install(name, site, force=True, quiet=True)
        plan_ok = rc == 0
        md = sum(1 for dp, _, fns in os.walk(os.path.join(site, "content"))
                 for f in fns if f.endswith(".md"))
        png = sum(1 for dp, _, fns in os.walk(os.path.join(site, "content"))
                  for f in fns if f.lower().endswith(".png"))
        print("%-12s rc=%d md=%-3d png=%d" % (name, rc, md, png))
        if not plan_ok:
            ok = False
        if name == "gallery-min" and png != 23:
            print("SELFTEST_INVALID gallery-min 图片数 %d（期望 23）" % png)
            ok = False
        if name == "docs-min" and png != 0:
            ok = False
    # 模板自身必须不含二进制图
    tpl_png = sum(1 for dp, _, fns in os.walk(EXAMPLES) for f in fns if f.lower().endswith(".png"))
    print("template_png=%d（必须为 0）" % tpl_png)
    ok = ok and tpl_png == 0
    # 已有正文必须被拒
    site = os.path.join(root, "docs-min")
    rc = install("docs-min", site, force=False, quiet=True)
    print("reinstall without --force: rc=%d（期望 1）" % rc)
    ok = ok and rc == 1
    shutil.rmtree(root, ignore_errors=True)
    print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--example")
    ap.add_argument("--site")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.list:
        for n in examples():
            print(n)
        return 0
    if a.selftest:
        return selftest()
    if not a.example or not a.site:
        print("FAIL 需要 --example 与 --site（或 --list / --selftest）")
        return 2
    return install(a.example, a.site, a.force)


if __name__ == "__main__":
    sys.exit(main())
