"""按 matrix.json 生成 content/docs 目录树、全部 _index.md 与文章 stub。

用法：
  python gen_skeleton.py --site <站点目录> --matrix matrix.json [--force]

matrix.json 结构（与 references/matrix-and-prompts.md 一致）：
  {
    "categories": [
      {"dir":"01-overview","title":"产品认知","icon":"fa-solid fa-compass","weight":1,"desc":"…",
       "sections":[{"dir":"认识X","title":"认识 X","weight":1,"desc":"…",
         "articles":[{"file":"a.md","title":"…","desc":"…","weight":1,
                      "sources":["4x:docs/00-intro/a.md"]}]}]}
    ],
    "prefixes": {"4x":"docs","50":"versioned_docs/version-5.0"}   # 可选，供 check_coverage 用
  }
也兼容顶层直接是 categories 数组。
"""

import argparse
import json
import os
import sys

TEMPLATE_CAT = """---
title: {title}
linkTitle: {title}
description: {desc}
type: docs
icon: {icon}
weight: {weight}
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

{desc}

## 知识板块

{boards}
"""

TEMPLATE_SEC = """---
title: {title}
linkTitle: {title}
description: {desc}
weight: {weight}
---

{desc}

本板块包含：{arts}。
"""

TEMPLATE_ART = """---
title: {title}
description: {desc}
weight: {weight}
---
"""


def load_matrix(path):
    data = json.load(open(path, encoding="utf-8"))
    cats = data.get("categories") if isinstance(data, dict) else data
    if not cats:
        print("FAIL matrix 里没有 categories")
        sys.exit(1)
    return cats


def write(path, text, force):
    if os.path.exists(path) and not force:
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True)
    ap.add_argument("--matrix", required=True)
    ap.add_argument("--force", action="store_true", help="覆盖已存在的 _index.md 与文章")
    a = ap.parse_args()

    cats = load_matrix(a.matrix)
    docs = os.path.join(os.path.abspath(a.site), "content", "docs")
    n_idx = n_art = n_skip = 0
    for cat in cats:
        cdir = os.path.join(docs, cat["dir"])
        boards = "\n".join(f"- **{s['title']}** — {s['desc']}" for s in cat["sections"])
        body = TEMPLATE_CAT.format(
            title=cat["title"], desc=cat["desc"], icon=cat["icon"],
            weight=cat["weight"], boards=boards,
        )
        if write(os.path.join(cdir, "_index.md"), body, a.force):
            n_idx += 1
        else:
            n_skip += 1
        for sec in cat["sections"]:
            sdir = os.path.join(cdir, sec["dir"])
            arts = "；".join(x["title"] for x in sec["articles"])
            if write(os.path.join(sdir, "_index.md"),
                     TEMPLATE_SEC.format(title=sec["title"], desc=sec["desc"],
                                         weight=sec["weight"], arts=arts), a.force):
                n_idx += 1
            else:
                n_skip += 1
            for art in sec["articles"]:
                if write(os.path.join(sdir, art["file"]),
                         TEMPLATE_ART.format(title=art["title"], desc=art["desc"],
                                             weight=art["weight"]), a.force):
                    n_art += 1
                else:
                    n_skip += 1
    print(f"categories={len(cats)} index_written={n_idx} articles_stubbed={n_art} skipped_existing={n_skip}")
    print(f"docs_root={docs}")


if __name__ == "__main__":
    main()
