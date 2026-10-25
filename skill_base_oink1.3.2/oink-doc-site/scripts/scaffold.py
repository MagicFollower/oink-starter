"""把一个可离线构建的 Hugo + OINK 站点骨架落到目标目录。

用法：
  python scaffold.py --out <新站目录> [--theme-only] [--scaffold-only] [--force] [--selftest]

行为：
  1) 复制 assets/theme/oink-main -> <out>/oink-main（Hugo module replace 目标，勿裁剪）
  2) 复制 assets/scaffold/*      -> <out>/（文档规范、T0Level 模板、go.mod、品牌资产）
  3) 若 <out>/site.plan.json 不存在，复制 assets/site.plan.example.json 作为可编辑起点

主题与模板都是离线载荷，不联网。站点身份、首页、导航与文章桩由 plan_site.py 生成。
"""

import argparse
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
THEME = os.path.join(SKILL, "assets", "theme", "oink-main")
SCAFFOLD = os.path.join(SKILL, "assets", "scaffold")
PLAN_EXAMPLE = os.path.join(SKILL, "assets", "site.plan.example.json")

REQUIRED_THEME = (
    "oink-main/theme.toml",
    "oink-main/hugo.yaml",
    "oink-main/assets/scss/td/_presets.scss",
    "oink-main/layouts/_partials/preset-config.html",
    "oink-main/assets/third_party/mermaid/mermaid.min.js",
)


def copy_tree(src, dst, force=False):
    made, skipped = 0, 0
    for dirpath, _, files in os.walk(src):
        rel = os.path.relpath(dirpath, src)
        for f in files:
            s = os.path.join(dirpath, f)
            d = os.path.join(dst, rel, f) if rel != "." else os.path.join(dst, f)
            if os.path.exists(d) and not force:
                skipped += 1
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            made += 1
    return made, skipped


def count_files(root):
    return sum(len(fs) for _, _, fs in os.walk(root))


def check_theme():
    missing = [p for p in REQUIRED_THEME if not os.path.isfile(os.path.join(THEME, p))]
    if missing:
        return "主题副本不完整，缺：%s" % "、".join(missing)
    theme_toml = open(os.path.join(THEME, "oink-main", "theme.toml"), encoding="utf-8").read()
    if 'min_version = "0.166.0"' not in theme_toml:
        return "主题不是 OINK 1.3.2 基线：theme.toml 的 min_version 不是 0.166.0"
    return None


def scaffold(out, force=False, theme_only=False, scaffold_only=False):
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    err = check_theme()
    if err:
        print("FAIL " + err)
        return 1
    if not scaffold_only:
        dst = os.path.join(out, "oink-main")
        made, skipped = copy_tree(THEME, dst, force)
        print("theme -> %s  copied=%d skipped=%d files=%d"
              % (dst, made, skipped, count_files(dst)))
    if not theme_only:
        made, skipped = copy_tree(SCAFFOLD, out, force)
        print("scaffold -> %s  copied=%d skipped=%d" % (out, made, skipped))
        plan = os.path.join(out, "site.plan.json")
        if not os.path.exists(plan) or force:
            shutil.copyfile(PLAN_EXAMPLE, plan)
            print("plan -> %s  copied=1" % plan)
        else:
            print("plan -> %s  kept（已存在）" % plan)
    print("next: 编辑 %s，然后运行" % os.path.join(out, "site.plan.json"))
    print('  python "%s" --site "%s" --plan "%s"'
          % (os.path.join(HERE, "plan_site.py"), out, os.path.join(out, "site.plan.json")))
    return 0


def selftest():
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-scaffold-", dir=os.path.abspath(root))
    try:
        out = os.path.join(tmp, "site")
        rc1 = scaffold(out, force=False)
        theme_files = count_files(os.path.join(out, "oink-main"))
        scaffold_ok = all(os.path.isfile(os.path.join(out, p)) for p in (
            "go.mod", "LICENSE", "doc/技术文档编写规范.md", "doc/运行与构建（T0Level）.md"))
        plan_ok = os.path.isfile(os.path.join(out, "site.plan.json"))
        rc2 = scaffold(out, force=False)
        kept = os.path.isfile(os.path.join(out, "site.plan.json"))
        ok = (rc1 == 0 and rc2 == 0 and theme_files > 1200 and scaffold_ok and plan_ok and kept)
        print("selftest: rc1=%d rc2=%d theme_files=%d scaffold_ok=%s plan_ok=%s rerun_kept=%s"
              % (rc1, rc2, theme_files, scaffold_ok, plan_ok, kept))
        print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--theme-only", action="store_true")
    ap.add_argument("--scaffold-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的同名文件")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.out:
        print("FAIL 需要 --out（或 --selftest）")
        sys.exit(2)
    sys.exit(scaffold(a.out, a.force, a.theme_only, a.scaffold_only))


if __name__ == "__main__":
    main()
