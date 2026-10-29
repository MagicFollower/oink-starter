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
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
THEME = os.path.join(SKILL, "assets", "theme", "oink-main")
SCAFFOLD = os.path.join(SKILL, "assets", "scaffold")
PLAN_EXAMPLE = os.path.join(SKILL, "assets", "site.plan.example.json")

# 单基线：只认这一条主题版本。min_version 给下限，MARKERS 证明它确实是这一版。
THEME_BASELINE = "1.4.0"
HUGO_MIN = (0, 168, 0)

REQUIRED_THEME = (
    "oink-main/theme.toml",
    "oink-main/hugo.yaml",
    "oink-main/assets/scss/td/_presets.scss",
    "oink-main/layouts/_partials/preset-config.html",
    "oink-main/assets/third_party/mermaid/mermaid.min.js",
)

# 1.4.0 才有的运行时；1.3.2 副本一个都没有，所以旧底片过不了这道门。
THEME_MARKERS = (
    "oink-main/assets/third_party/plantuml/plantuml.js",
    "oink-main/assets/js/diagram.js",
    "oink-main/assets/js/table-reader.js",
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


def parse_min_version(text):
    m = re.search(r'min_version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text)
    return tuple(int(x) for x in m.groups()) if m else None


def check_theme():
    missing = [p for p in REQUIRED_THEME if not os.path.isfile(os.path.join(THEME, p))]
    if missing:
        return "主题副本不完整，缺：%s" % "、".join(missing)
    markers = [p for p in THEME_MARKERS if not os.path.isfile(os.path.join(THEME, p))]
    if markers:
        return "主题不是 OINK %s 基线：缺 1.4.0 独有文件 %s（旧副本要整目录换，不要改配置救）" % (
            THEME_BASELINE, "、".join(markers))
    got = parse_min_version(open(os.path.join(THEME, "oink-main", "theme.toml"),
                                encoding="utf-8").read())
    if got is None:
        return "theme.toml 里没有可解析的 min_version"
    if got < HUGO_MIN:
        return "主题 min_version %s 低于 OINK %s 要求的 %s" % (
            ".".join(str(x) for x in got), THEME_BASELINE, ".".join(str(x) for x in HUGO_MIN))
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


def gate_bites(probe_dir):
    """证明版本闸会红：造两份假主题副本（缺 1.4.0 标记 / min_version 低于闸门）。

    判据先证明会红，绿色才当结论——所以 selftest 不只跑绿。
    """
    global THEME
    saved = THEME
    results = []
    try:
        # 1) 1.3.2 形态：有 REQUIRED 五件、无 1.4.0 标记
        old = os.path.join(probe_dir, "old")
        for rel in REQUIRED_THEME:
            p = os.path.join(old, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write('name = "OINK"\nmin_version = "0.166.0"\n')
        THEME = old
        results.append(("缺 1.4.0 标记 -> FAIL", check_theme() is not None))

        # 2) 有标记但 min_version 低于闸门
        low = os.path.join(probe_dir, "low")
        for rel in tuple(REQUIRED_THEME) + tuple(THEME_MARKERS):
            p = os.path.join(low, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write('name = "OINK"\nmin_version = "0.167.0"\n')
        THEME = low
        results.append(("min_version 低于闸门 -> FAIL", check_theme() is not None))

        # 3) 合基线形态：标记齐 + min_version 达标
        good = os.path.join(probe_dir, "good")
        for rel in tuple(REQUIRED_THEME) + tuple(THEME_MARKERS):
            p = os.path.join(good, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8").write('name = "OINK"\nmin_version = "0.168.0"\n')
        THEME = good
        results.append(("基线形态 -> PASS", check_theme() is None))
    finally:
        THEME = saved
    return results


def selftest():
    root = os.environ.get("OINK_DOC_TMP") or os.path.join(os.getcwd(), ".tmp")
    os.makedirs(root, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="oink-scaffold-", dir=os.path.abspath(root))
    try:
        out = os.path.join(tmp, "site")
        rc1 = scaffold(out, force=False)
        theme_files = count_files(os.path.join(out, "oink-main"))
        src_files = count_files(THEME)
        scaffold_ok = all(os.path.isfile(os.path.join(out, p)) for p in (
            "go.mod", "LICENSE", "run.cmd", "doc/技术文档编写规范.md", "doc/运行与构建（T0Level）.md"))
        plan_ok = os.path.isfile(os.path.join(out, "site.plan.json"))
        rc2 = scaffold(out, force=False)
        kept = os.path.isfile(os.path.join(out, "site.plan.json"))
        bites = gate_bites(os.path.join(tmp, "gate-probe"))
        bites_ok = all(hit for _, hit in bites)
        ok = (rc1 == 0 and rc2 == 0 and theme_files == src_files and src_files > 1200
              and scaffold_ok and plan_ok and kept and bites_ok)
        print("selftest: rc1=%d rc2=%d theme_files=%d src_files=%d scaffold_ok=%s plan_ok=%s "
              "rerun_kept=%s" % (rc1, rc2, theme_files, src_files, scaffold_ok, plan_ok, kept))
        for label, hit in bites:
            print("gate_probe: %-28s %s" % (label, "OK" if hit else "MISS"))
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
