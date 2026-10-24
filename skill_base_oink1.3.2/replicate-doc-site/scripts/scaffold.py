"""从技能自带模板立起一个可构建的 OINK 文档站骨架。

用法：
  python scaffold.py --out D:/path/new-site [--theme-only] [--scaffold-only] [--force]

行为：
  1) 复制 assets/theme/oink-main -> <out>/oink-main（Hugo 模块 replace 目标，勿裁剪）
  2) 复制 assets/scaffold/*      -> <out>/（跳过已存在文件，除非 --force）
  3) 报告剩余全角中括号占位数量——必须清零才算落地完成
"""

import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
THEME = os.path.join(SKILL, "assets", "theme", "oink-main")
SCAFFOLD = os.path.join(SKILL, "assets", "scaffold")


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


def count_placeholders(root):
    hits = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith((".md", ".yaml", ".yml", ".html")):
                continue
            p = os.path.join(dirpath, f)
            try:
                t = open(p, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            n = t.count("【")
            if n:
                hits[os.path.relpath(p, root).replace(os.sep, "/")] = n
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="新站目录（不存在则创建）")
    ap.add_argument("--theme-only", action="store_true")
    ap.add_argument("--scaffold-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的同名文件")
    a = ap.parse_args()

    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    if not a.scaffold_only:
        if not os.path.isdir(THEME):
            print(f"FAIL 主题缺失：{THEME}")
            sys.exit(1)
        dst = os.path.join(out, "oink-main")
        made, skipped = copy_tree(THEME, dst, a.force)
        print(f"theme -> {dst}  copied={made} skipped={skipped}")
    if not a.theme_only:
        made, skipped = copy_tree(SCAFFOLD, out, a.force)
        print(f"scaffold -> {out}  copied={made} skipped={skipped}")

    ph = count_placeholders(out)
    total = sum(ph.values())
    print(f"placeholders_remaining={total}")
    for k, v in sorted(ph.items(), key=lambda kv: -kv[1]):
        print(f"  {v:3d}  {k}")
    if total:
        print("下一步：把上述文件里的全角中括号占位换成真实内容，再跑 gen_skeleton.py 建内容树。")


if __name__ == "__main__":
    main()
