"""把 site.plan.json 落成 Hugo + OINK 站点：配置、首页、导航索引与文章桩。

用法：
  python plan_site.py --plan site.plan.json --check-only
  python plan_site.py --site <站点目录> --plan site.plan.json [--force]

--check-only 只校验计划，不写盘；退出码 0=无问题，1=有计划错误，2=用法/读文件错。
写盘时：
  - hugo.yaml / content/_index.md / content/docs/_index.md / data/home/zh.yaml / README.md
    是计划派生文件，总是重写；
  - 分类与板块的 _index.md 总是重写；
  - 文章桩只在文件不存在时写；已存在的文章默认保留（--force 才覆盖）。
这样在正文写完后重跑计划，不会把已写内容冲掉。

计划 schema 与写法见 references/site-plan.md。所有目录、文件名、权重、描述在写盘前校验。
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TEMPLATE_HUGO = os.path.join(SKILL, "assets", "templates", "hugo.yaml")

PRESETS = ("paper", "slate", "ink", "terminal")
CAT_DIR_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
BAD_NAME_RE = re.compile(r"[\\/\s]|(^|/)\.\.($|/)")
THIN_DESC = 20
CODES_ORDER = ("SCHEMA", "NO_CATEGORIES", "NO_ARTICLES", "BAD_PATH", "DUP_NAME",
               "DUP_WEIGHT", "WEIGHT_GAP", "THIN_DESC", "BAD_PRESET", "BAD_BASE_URL",
               "BAD_LANG", "BAD_HOME", "BAD_HOME_URL", "MISSING_TOKEN")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def q(value):
    """JSON 字符串就是合法的 YAML 双引号标量。"""
    return json.dumps(str(value), ensure_ascii=False)


def check_weights(items, where, problems):
    ws = [x.get("weight") for x in items if isinstance(x, dict)]
    if not ws:
        return
    if any(not isinstance(w, int) or isinstance(w, bool) or w < 1 for w in ws):
        problems.append(("SCHEMA", where, "weight 必须是 >=1 的整数"))
        return
    dup = sorted({w for w in ws if ws.count(w) > 1})
    if dup:
        problems.append(("DUP_WEIGHT", where, "重复 weight %s" % dup))
    if sorted(ws) != list(range(1, len(ws) + 1)):
        problems.append(("WEIGHT_GAP", where, "应为 1..%d，实际 %s" % (len(ws), sorted(ws))))


def check_unique(items, key, where, problems):
    vals = [x.get(key) for x in items if isinstance(x, dict)]
    dup = sorted({v for v in vals if v is not None and vals.count(v) > 1})
    if dup:
        problems.append(("DUP_NAME", where, "%s 重复：%s" % (key, dup)))


def check_name(name, where, problems, kind="dir", category=False):
    if not isinstance(name, str) or not name.strip():
        problems.append(("SCHEMA", where, "%s 缺失或不是字符串" % kind))
        return False
    if BAD_NAME_RE.search(name) or name.startswith("."):
        problems.append(("BAD_PATH", where, "%s 含空白、斜杠或 ..：%r" % (kind, name)))
        return False
    if category:
        if not CAT_DIR_RE.match(name):
            problems.append(("BAD_PATH", where,
                             "一级分类目录必须是小写字母/数字/连字符：%r（中文与空格会进 URL）" % name))
            return False
    if kind == "file":
        if not name.endswith(".md") or name == "_index.md":
            problems.append(("BAD_PATH", where, "文章文件必须是普通 .md：%r" % name))
            return False
    return True


def check_home(home, problems):
    if home is None:
        return
    if not isinstance(home, dict):
        problems.append(("BAD_HOME", "home", "home 必须是对象"))
        return
    for key in ("eyebrow", "lead", "cardsEyebrow", "cardsTitle"):
        if key in home and not isinstance(home[key], str):
            problems.append(("BAD_HOME", "home." + key, "必须是字符串"))
    title = home.get("title")
    if title is not None and not (isinstance(title, str) or
                                  (isinstance(title, list) and all(isinstance(x, str) for x in title))):
        problems.append(("BAD_HOME", "home.title", "必须是字符串或字符串数组"))
    for key in ("actions", "cards"):
        value = home.get(key)
        if value is None:
            continue
        if not isinstance(value, list):
            problems.append(("BAD_HOME", "home." + key, "必须是数组"))
            continue
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                problems.append(("BAD_HOME", "home.%s[%d]" % (key, i), "必须是对象"))
                continue
            for field in ("label", "title", "url"):
                if field in item and not isinstance(item[field], str):
                    problems.append(("BAD_HOME", "home.%s[%d].%s" % (key, i, field), "必须是字符串"))
            if key == "actions" and ("label" not in item or "url" not in item):
                problems.append(("BAD_HOME", "home.actions[%d]" % i, "缺少 label 或 url"))
            if key == "cards" and ("title" not in item or "url" not in item):
                problems.append(("BAD_HOME", "home.cards[%d]" % i, "缺少 title 或 url"))
    cta = home.get("cta")
    if cta is not None and cta is not False:
        if not isinstance(cta, dict):
            problems.append(("BAD_HOME", "home.cta", "必须是对象或 false"))
        else:
            for key in ("title", "url"):
                if not isinstance(cta.get(key), str):
                    problems.append(("BAD_HOME", "home.cta." + key, "必须是非空字符串"))
            for key in ("text", "label", "style"):
                if key in cta and not isinstance(cta[key], str):
                    problems.append(("BAD_HOME", "home.cta." + key, "必须是字符串"))
    columns = home.get("cardsColumns")
    if columns is not None and (not isinstance(columns, int) or isinstance(columns, bool)
                                or not 1 <= columns <= 4):
        problems.append(("BAD_HOME", "home.cardsColumns", "必须是 1..4 的整数"))


def normalize_url(url):
    u = url.strip().split("#")[0].split("?")[0]
    if u.startswith("/"):
        u = u[1:]
    if u and not u.endswith("/"):
        u += "/"
    return u


def planned_urls(cats):
    urls = {"docs/"}
    for cat in cats:
        if not isinstance(cat, dict) or not isinstance(cat.get("dir"), str):
            continue
        urls.add("docs/%s/" % cat["dir"])
        for sec in cat.get("sections") or []:
            if not isinstance(sec, dict) or not isinstance(sec.get("dir"), str):
                continue
            urls.add("docs/%s/%s/" % (cat["dir"], sec["dir"]))
            for art in sec.get("articles") or []:
                if not isinstance(art, dict) or not isinstance(art.get("file"), str):
                    continue
                urls.add("docs/%s/%s/%s/" % (cat["dir"], sec["dir"], art["file"][:-3]))
    return urls


def check_home_urls(home, cats, problems):
    if not isinstance(home, dict):
        return
    valid = planned_urls(cats)
    items = []
    for i, a in enumerate(home.get("actions") or []):
        if isinstance(a, dict):
            items.append(("home.actions[%d].url" % i, a.get("url")))
    for i, c in enumerate(home.get("cards") or []):
        if isinstance(c, dict):
            items.append(("home.cards[%d].url" % i, c.get("url")))
    cta = home.get("cta")
    if isinstance(cta, dict):
        items.append(("home.cta.url", cta.get("url")))
    for where, url in items:
        if not isinstance(url, str):
            continue
        if url.startswith(("http://", "https://", "#", "mailto:", "tel:")):
            continue
        if normalize_url(url) not in valid:
            problems.append(("BAD_HOME_URL", where,
                             "URL 不在计划树内：%s（文章页要写到板块层：docs/<分类>/<板块>/<文章>/）" % url))


def check_plan(data):
    problems = []
    if not isinstance(data, dict):
        return [("SCHEMA", "root", "计划顶层必须是对象")], {}
    site = data.get("site")
    if not isinstance(site, dict):
        problems.append(("SCHEMA", "site", "缺少 site 对象"))
        site = {}
    for key in ("title", "description"):
        if not isinstance(site.get(key), str) or not site[key].strip():
            problems.append(("SCHEMA", "site." + key, "必须是非空字符串"))
    base = site.get("baseURL", "")
    if not isinstance(base, str) or not re.match(r"^https?://", base):
        problems.append(("BAD_BASE_URL", "site.baseURL", "必须以 http:// 或 https:// 开头"))
    if site.get("lang", "zh") != "zh":
        problems.append(("BAD_LANG", "site.lang", "当前版本只支持中文站（zh）"))
    preset = site.get("preset", "paper")
    if preset not in PRESETS:
        problems.append(("BAD_PRESET", "site.preset", "只允许 %s" % "、".join(PRESETS)))
    menu = site.get("presetMenu", list(PRESETS))
    if menu not in (True, False):
        if not isinstance(menu, list) or not menu or any(x not in PRESETS for x in menu):
            problems.append(("BAD_PRESET", "site.presetMenu", "必须是 true/false 或预设名数组"))
        elif preset not in menu:
            problems.append(("BAD_PRESET", "site.presetMenu", "必须包含站点默认 preset=%s" % preset))

    check_home(data.get("home"), problems)

    cats = data.get("categories")
    if not isinstance(cats, list) or not cats:
        problems.append(("NO_CATEGORIES", "categories", "至少需要一个一级分类"))
        return problems, {"categories": 0, "sections": 0, "articles": 0}
    check_unique(cats, "dir", "categories", problems)
    check_weights(cats, "categories", problems)
    n_sec = n_art = 0
    for ci, cat in enumerate(cats):
        where = "categories[%d]" % ci
        if not isinstance(cat, dict):
            problems.append(("SCHEMA", where, "分类必须是对象"))
            continue
        check_name(cat.get("dir"), where + ".dir", problems, "dir", category=True)
        if not isinstance(cat.get("title"), str) or not cat["title"].strip():
            problems.append(("SCHEMA", where + ".title", "必须是非空字符串"))
        if not isinstance(cat.get("desc"), str) or not cat["desc"].strip():
            problems.append(("SCHEMA", where + ".desc", "必须是非空字符串"))
        secs = cat.get("sections")
        if not isinstance(secs, list) or not secs:
            problems.append(("NO_ARTICLES", where + ".sections", "分类至少需要一个板块"))
            continue
        check_unique(secs, "dir", where, problems)
        check_weights(secs, where + ".sections", problems)
        n_sec += len(secs)
        for si, sec in enumerate(secs):
            swhere = where + ".sections[%d]" % si
            if not isinstance(sec, dict):
                problems.append(("SCHEMA", swhere, "板块必须是对象"))
                continue
            check_name(sec.get("dir"), swhere + ".dir", problems, "dir")
            if not isinstance(sec.get("title"), str) or not sec["title"].strip():
                problems.append(("SCHEMA", swhere + ".title", "必须是非空字符串"))
            if not isinstance(sec.get("desc"), str) or not sec["desc"].strip():
                problems.append(("SCHEMA", swhere + ".desc", "必须是非空字符串"))
            arts = sec.get("articles")
            if not isinstance(arts, list) or not arts:
                problems.append(("NO_ARTICLES", swhere + ".articles", "板块至少需要一篇文章"))
                continue
            check_unique(arts, "file", swhere, problems)
            check_weights(arts, swhere + ".articles", problems)
            n_art += len(arts)
            for ai, art in enumerate(arts):
                awhere = swhere + ".articles[%d]" % ai
                if not isinstance(art, dict):
                    problems.append(("SCHEMA", awhere, "文章必须是对象"))
                    continue
                check_name(art.get("file"), awhere + ".file", problems, "file")
                if not isinstance(art.get("title"), str) or not art["title"].strip():
                    problems.append(("SCHEMA", awhere + ".title", "必须是非空字符串"))
                desc = art.get("desc")
                if not isinstance(desc, str) or not desc.strip():
                    problems.append(("SCHEMA", awhere + ".desc", "必须是非空字符串"))
                elif len(desc.strip()) < THIN_DESC:
                    problems.append(("THIN_DESC", awhere + ".desc",
                                     "description 仅 %d 字，至少 %d 字（会进侧边栏卡片与 SEO）"
                                     % (len(desc.strip()), THIN_DESC)))
                sources = art.get("sources")
                if sources is not None and (not isinstance(sources, list) or
                                            any(not isinstance(x, str) for x in sources)):
                    problems.append(("SCHEMA", awhere + ".sources", "sources 必须是字符串数组"))
    check_home_urls(data.get("home"), cats, problems)
    return problems, {"categories": len(cats), "sections": n_sec, "articles": n_art}


def category_url(cat):
    return "/docs/%s/" % cat["dir"]


def article_url(cat, sec, art):
    return "docs/%s/%s/%s/" % (cat["dir"], sec["dir"], art["file"][:-3])


def first_article(cats):
    cat = cats[0]
    sec = cat["sections"][0]
    art = sec["articles"][0]
    return article_url(cat, sec, art)


def render_hugo(site):
    text = read(TEMPLATE_HUGO)
    copies = site.get("copyright") if isinstance(site.get("copyright"), dict) else {}
    menu = site.get("presetMenu", list(PRESETS))
    if menu is True:
        menu_text = "true"
    elif menu is False:
        menu_text = "false"
    else:
        menu_text = "[" + ", ".join(menu) + "]"
    repl = {
        "【站点标题】": site["title"],
        "【BASE_URL】": site["baseURL"],
        "【站点摘要】": site["description"],
        "【版权主体】": str(copies.get("authors", "站点贡献者")),
        "【起始年】": str(copies.get("fromYear", 2026)),
        "【页脚说明】": str(site.get("footer", "内容以站点实际发布为准。")),
        "【PRESET】": site.get("preset", "paper"),
        "【PRESET_MENU】": menu_text,
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text


def render_index(title, description):
    return "---\ntitle: %s\ndescription: %s\n---\n" % (q(title), q(description))


def render_docs_index(cats):
    total = sum(len(s["articles"]) for c in cats for s in c["sections"])
    lines = [
        "---",
        "title: %s" % q("文档"),
        "linkTitle: %s" % q("文档"),
        "description: %s" % q("按主题组织的全部文档，共 %d 个分类、%d 篇文章。" % (len(cats), total)),
        "type: docs",
        "icon: fa-solid fa-book",
        "sidebar_root_for: self",
        "sidebar_root_link_self: true",
        "cascade:",
        "  type: docs",
        "  footer_style: slim",
        "---",
        "",
        "按下面的分类进入。每一类都可以独立成树，左侧边栏会跟随当前分类切换。",
        "",
    ]
    lines += ["- [%s](%s)" % (c["title"], category_url(c)) for c in cats]
    lines += ["{.cards}", ""]
    return "\n".join(lines)


def render_category(cat):
    boards = "\n".join("- **%s** — %s" % (s["title"], s["desc"]) for s in cat["sections"])
    return (
        "---\n"
        "title: %s\n"
        "linkTitle: %s\n"
        "description: %s\n"
        "type: docs\n"
        "icon: %s\n"
        "weight: %d\n"
        "sidebar_root_for: self\n"
        "sidebar_root_link_self: true\n"
        "cascade:\n"
        "  type: docs\n"
        "  footer_style: slim\n"
        "---\n\n%s\n\n## 知识板块\n\n%s\n"
        % (q(cat["title"]), q(cat["title"]), q(cat["desc"]), cat.get("icon", "fa-solid fa-folder"),
           cat["weight"], cat["desc"], boards)
    )


def render_section(sec):
    arts = "；".join(a["title"] for a in sec["articles"])
    return (
        "---\n"
        "title: %s\n"
        "linkTitle: %s\n"
        "description: %s\n"
        "weight: %d\n"
        "---\n\n%s\n\n本板块包含：%s。\n"
        % (q(sec["title"]), q(sec["title"]), q(sec["desc"]), sec["weight"], sec["desc"], arts)
    )


def render_article(art):
    return (
        "---\n"
        "title: %s\n"
        "description: %s\n"
        "weight: %d\n"
        "---\n\n"
        "<!-- OINK-STUB: 本页尚未撰写。写完正文后删除本行。 -->\n\n"
        "本页内容尚未撰写。\n"
        % (q(art["title"]), q(art["desc"]), art["weight"])
    )


def default_actions(cats):
    return [
        {"label": "开始阅读", "url": first_article(cats), "icon": "fa-solid fa-book", "style": "primary"},
        {"label": "浏览全部文档", "url": "docs/", "icon": "fa-solid fa-layer-group", "style": "ghost"},
    ]


def render_home(site, home, cats):
    home = home or {}
    title = home.get("title") or [site["title"]]
    if isinstance(title, str):
        title = [title]
    lead = home.get("lead") or site["description"]
    actions = home.get("actions") or default_actions(cats)
    cards = home.get("cards")
    if not cards:
        cards = [{"title": c["title"], "desc": c["desc"], "icon": c.get("icon", "fa-solid fa-folder"),
                  "url": category_url(c).lstrip("/")} for c in cats]
    cta = home.get("cta")
    if cta is None:
        cta = {
            "title": "从第一篇开始",
            "text": "按顺序阅读，或者直接从左侧目录跳到需要的章节。",
            "label": "开始阅读",
            "url": first_article(cats),
        }
    lines = [
        "sections: [hero, cards, cta]",
        "",
        "hero:",
        "  align: center",
        "  eyebrow: %s" % q(home.get("eyebrow") or site["title"]),
        "  title_lines:",
    ]
    lines += ["    - words: [{ text: %s }]" % q(x) for x in title]
    lines += [
        "  lead: %s" % q(lead),
        "  actions:",
    ]
    for a in actions:
        lines.append("    - { label: %s, url: %s, icon: %s, style: %s }" % (
            q(a["label"]), q(a["url"]), q(a.get("icon", "fa-solid fa-book")),
            q(a.get("style", "primary"))))
    lines += [
        "",
        "cards:",
        "  eyebrow: %s" % q(home.get("cardsEyebrow") or "按主题浏览"),
        "  title: %s" % q(home.get("cardsTitle") or "文档地图"),
        "  columns: %d" % int(home.get("cardsColumns") or 3),
        "  items:",
    ]
    for c in cards:
        lines.append("    - { title: %s, desc: %s, icon: %s, url: %s }" % (
            q(c["title"]), q(c.get("desc", "")), q(c.get("icon", "fa-solid fa-folder")), q(c["url"])))
    if cta is False:
        cta = {
            "title": "开始阅读",
            "text": "从左侧目录进入任意主题。",
            "label": "浏览文档",
            "url": "docs/",
        }
    lines += [
        "",
        "cta:",
        "  title: %s" % q(cta["title"]),
        "  text: %s" % q(cta.get("text", "")),
        "  label: %s" % q(cta.get("label", "开始阅读")),
        "  url: %s" % q(cta["url"]),
        "  style: %s" % q(cta.get("style", "primary")),
        "",
    ]
    return "\n".join(lines)


def render_readme(site, cats):
    rows = []
    for c in cats:
        secs = "、".join(s["title"] for s in c["sections"])
        rows.append("| `%s/` | %s | %s |" % (c["dir"], c["title"], secs))
    total = sum(len(s["articles"]) for c in cats for s in c["sections"])
    return """# %(title)s — 文档站操作规范

本项目是基于 Hugo + OINK v1.3.2 的中文文档站，主题与运行时全部本地化，构建过程不联网。本文件说明目录约定、写作门槛与验收命令，读完即可接手维护。

## 一、项目结构

```text
%(title)s/
├── content/_index.md              # 首页
├── content/docs/                  # 文档主区域
│   ├── _index.md                  # 文档总览（卡片导航）
│   └── NN-分类/板块/文章.md
├── static/images/                 # 配图（正文用 /images/xxx.png）
├── data/home/zh.yaml              # 首页 hero / 卡片 / CTA
├── hugo.yaml                      # 站点唯一配置
├── go.mod                         # 主题走 replace 本地化
├── run.cmd                        # Windows 双击启动本地预览
├── oink-main/oink-main/           # OINK 主题（勿修改）
├── doc/                           # 编写规范、运行与构建
└── site.plan.json                 # 导航计划（生成导航的源数据）
```

## 二、内容分类（共 %(ncat)d 类 / %(nart)d 篇）

| 目录 | 分类 | 板块 |
|------|------|------|
%(rows)s

新增分类或文章：改 `site.plan.json`，再跑 `plan_site.py --site . --plan site.plan.json`。不要只手建目录，目录与 `_index.md` 必须成对。

顶栏「文档」tab 由生成器写入 `hugo.yaml` 的 `menus.main`（`identifier: docs`、`pageRef: /docs`）。OINK 1.3.2 的顶栏只渲染这个配置，主题不会自动挂入口；重跑计划会保留该键。

## 三、命名与 Front Matter

| 层级 | 命名 | 示例 |
|------|------|------|
| 一级分类目录 | 小写字母/数字/短横线 | `01-overview/` |
| 二级板块目录 | 中文或英文，不含空白与斜杠 | `核心概念/` |
| 文章文件 | 中文或英文，不含空白与斜杠 | `一致性协议.md` |

文章三字段缺一不可；`weight` 在同目录内 1..N 连续不重复：

```yaml
---
title: 文章标题
description: 一句话说明本文解决什么问题（至少 20 字，会进侧边栏卡片与 SEO）。
weight: 1
---
```

一级分类 `_index.md` 带 `type: docs`、`icon`、`weight`、`sidebar_root_for: self`、`sidebar_root_link_self: true` 与 `cascade`；板块 `_index.md` 只需 `title`/`linkTitle`/`description`/`weight`。这些文件由 `plan_site.py` 生成，手改后重跑计划会被覆盖。

## 四、写作与事实来源

正文按 `doc/技术文档编写规范.md` 写。机器门槛（`audit_content.py --mode full`）：

- 首个真实 H2 以「为什么」开头；
- 全文 ≥ 260 行、≥ 3 个「💡 新人小结」、≥ 1 个 mermaid、≥ 2 组表格、≥ 1 个带语言标注的代码块；
- 必须有「要点总结」；description ≥ 20 字；
- 禁止「限于篇幅 / 此处从略 / 自行查阅 / 待补充 / TODO / 感兴趣请 / 众所周知 / 不言而喻」；
- 禁止用 `┌┐└┘├┤┬┴┼` 画图，结构化图用 mermaid。

**技术事实只能来自可核验来源**：用户提供的材料、官方文档/仓库、真实命令输出。具体默认值、版本号、限制数值、异常语义查不到就不写，或明确写「上游未给出」。每批写作在 `doc/内容来源.md` 登记来源，交付时作为 MANUAL 项核对。

## 五、构建与环境

| 工具 | 版本 | 要求 |
|------|------|------|
| Hugo | ≥ 0.166.0 **Extended** | 标准版无法编译 SCSS；严格 `--panicOnWarning` 闸门用 0.166.0 |
| Go | 与 `go.mod` 的 `go` 指令一致（1.27.0） | 版本不匹配会触发联网下载工具链；PATH 里有旧 Go 时用 `--go-bin` 指向 1.27.x 的 bin |

```bash
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir          # 构建
run.cmd                             # Windows：双击或命令行启动本地预览
hugo server -D                      # 非 Windows 或手动启动
python -m http.server 8766 --directory public   # 纯静态产物预览
hugo --cleanDestinationDir --gc --minify   # 发布档
```

Windows 的 `run.cmd` 会自动设置离线构建变量、查找 Hugo（找不到时可用 `HUGO_EXE` 指定完整路径）、在 `127.0.0.1:8768` 启动 Hugo server 并打开浏览器；端口冲突时先 `set PORT=9000` 再运行。`NO_OPEN=1` 可跳过自动打开浏览器，适合脚本验证。

离线构建要同时满足：主题副本在 `oink-main/oink-main/`、`go.mod` 的 replace 指向它、Go 与 `go.mod` 指令对齐。Hugo 报 `failed to load modules` 时先查 Go 是否在 PATH，不是内容错误。验收时 Go 版本不对可用 `--go-bin` 指向正确 bin；如果 `go version` 打印 `go: downloading go1.27.0`，说明 PATH 选到了旧 Go。

**打开方式**：完整功能请走 HTTP（`hugo server` 或上面的 `python -m http.server`）。直接双击 `public/index.html` 只有无样式文字：OINK 产物的 CSS/JS 带 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，会被浏览器 CORS 拦截，Mermaid、离线搜索、Appearance 都不可用。

## 六、约束

1. 不修改 `oink-main/` 主题目录。
2. 正文语言为中文，不做多语言混排；`.md` 即中文正文。
3. 目录与 `_index.md` 成对出现；文章必须有 front matter。
4. 一篇文档只归一个板块；跨板块关联用站内链接，不复制正文。
5. 不把本地临时路径、审计报告措辞写进正文；配图放 `static/images/`，正文用 `/images/...`。
""" % {
        "title": site["title"],
        "rows": "\n".join(rows),
        "ncat": len(cats),
        "nart": total,
    }


RUN_TITLE_RE = re.compile(r'set "SITE_TITLE=[^\r\n]*')


def patch_run_cmd_title(site_dir, title):
    """只改 run.cmd 配置块里的 SITE_TITLE 一行；没有 run.cmd 时 no-op。"""
    path = os.path.join(site_dir, "run.cmd")
    if not os.path.isfile(path):
        return False
    with open(path, "rb") as f:
        raw = f.read()
    safe = title.replace('"', "").replace("\r", " ").replace("\n", " ").strip()
    text = raw.decode("utf-8")
    new = RUN_TITLE_RE.sub(lambda m: 'set "SITE_TITLE=%s"' % safe, text, count=1)
    if new == text:
        return False
    with open(path, "wb") as f:
        f.write(new.encode("utf-8"))
    return True


def write_plan(site_dir, data, force):
    site = data["site"]
    cats = data["categories"]
    generated = 0
    stubbed = 0
    kept = 0

    write(os.path.join(site_dir, "hugo.yaml"), render_hugo(site))
    write(os.path.join(site_dir, "content", "_index.md"),
          render_index(site["title"], site["description"]))
    write(os.path.join(site_dir, "content", "docs", "_index.md"), render_docs_index(cats))
    write(os.path.join(site_dir, "data", "home", "zh.yaml"), render_home(site, data.get("home"), cats))
    write(os.path.join(site_dir, "README.md"), render_readme(site, cats))
    generated += 5
    if patch_run_cmd_title(site_dir, site["title"]):
        print("run.cmd SITE_TITLE -> %s" % site["title"])

    docs = os.path.join(site_dir, "content", "docs")
    for cat in cats:
        cdir = os.path.join(docs, cat["dir"])
        write(os.path.join(cdir, "_index.md"), render_category(cat))
        generated += 1
        for sec in cat["sections"]:
            sdir = os.path.join(cdir, sec["dir"])
            write(os.path.join(sdir, "_index.md"), render_section(sec))
            generated += 1
            for art in sec["articles"]:
                path = os.path.join(sdir, art["file"])
                if os.path.exists(path) and not force:
                    kept += 1
                    continue
                write(path, render_article(art))
                stubbed += 1

    leftovers = []
    for dp, dns, fns in os.walk(site_dir):
        dns[:] = [d for d in dns if d not in ("oink-main", "public", "resources", ".git", ".tmp", "doc")]
        for f in fns:
            if not f.endswith((".md", ".yaml", ".yml", ".html")):
                continue
            p = os.path.join(dp, f)
            try:
                text = read(p)
            except (OSError, UnicodeDecodeError):
                continue
            if "【" in text:
                leftovers.append(os.path.relpath(p, site_dir).replace(os.sep, "/"))
    print("plan_write: generated=%d articles_stubbed=%d articles_kept=%d placeholders_remaining=%d"
          % (generated, stubbed, kept, len(leftovers)))
    for p in sorted(leftovers):
        print("  PLACEHOLDER", p)
    print("docs_root=%s" % docs)
    print("next: python <技能目录>/scripts/verify_site.py --site <站点目录> --plan <计划文件> --mode skeleton")
    return 0 if not leftovers else 1


def selftest():
    """证明校验器既能放行合规计划，也能逐条报出已知计划缺陷。"""
    good = {
        "site": {"title": "示例文档", "description": "一套用于验证计划生成器的示例文档站。",
                 "baseURL": "https://example.org/", "preset": "paper",
                 "presetMenu": ["paper", "slate", "ink", "terminal"]},
        "categories": [{
            "dir": "01-overview", "title": "概览", "weight": 1, "desc": "先建立整体认识。",
            "icon": "fa-solid fa-compass",
            "sections": [{
                "dir": "认识系统", "title": "认识系统", "weight": 1, "desc": "从问题出发认识系统。",
                "articles": [{"file": "why.md", "title": "为什么需要它",
                              "weight": 1, "desc": "从一个真实痛点出发，解释这个系统解决的问题与边界。",
                              "sources": ["官方文档"]}]
            }]
        }]
    }
    bad = json.loads(json.dumps(good))
    bad["site"]["preset"] = "neon"
    bad["site"]["presetMenu"] = ["paper", "slate"]
    bad["categories"][0]["dir"] = "01 overview/中文"
    bad["categories"][0]["sections"][0]["dir"] = "a/b"
    bad["categories"][0]["sections"][0]["articles"][0]["file"] = "_index.md"
    bad["categories"][0]["sections"][0]["articles"][0]["desc"] = "太短"
    bad["categories"][0]["sections"][0]["articles"].append({
        "file": "dup.md", "title": "重复权重", "weight": 1,
        "desc": "这一篇用来触发重复权重判据，描述长度必须超过二十个字。"})
    bad["categories"][0]["sections"].append({
        "dir": "空板块", "title": "空板块", "weight": 1, "desc": "没有文章。", "articles": []})
    bad["home"] = {"actions": [{"label": "坏链接", "url": "docs/does-not-exist/"}]}

    pgood, sgood = check_plan(good)
    pbad, _ = check_plan(bad)
    codes = {c for c, _, _ in pbad}
    want = {"BAD_PRESET", "BAD_PATH", "THIN_DESC", "DUP_WEIGHT", "NO_ARTICLES", "BAD_HOME_URL"}
    missing = sorted(want - codes)
    print("good: problems=%d categories=%d sections=%d articles=%d"
          % (len(pgood), sgood["categories"], sgood["sections"], sgood["articles"]))
    print("bad: problems=%d codes=%s" % (len(pbad), ",".join(sorted(codes))))
    ok = not pgood and not missing
    tmp = os.path.join(os.environ.get("OINK_DOC_TMP") or os.getcwd(), ".tmp", "plan-run-cmd")
    os.makedirs(tmp, exist_ok=True)
    run_dst = os.path.join(tmp, "run.cmd")
    with open(os.path.join(SKILL, "assets", "scaffold", "run.cmd"), "rb") as f:
        blob = f.read()
    with open(run_dst, "wb") as f:
        f.write(blob)
    patched = patch_run_cmd_title(tmp, good["site"]["title"])
    with io.open(run_dst, encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l.startswith('set "SITE_TITLE=')]
    title_ok = patched and lines == ['set "SITE_TITLE=%s"' % good["site"]["title"]]
    noop_ok = patch_run_cmd_title(os.path.join(tmp, "nope"), "x") is False
    for name in os.listdir(tmp):
        os.remove(os.path.join(tmp, name))
    os.rmdir(tmp)
    print("run.cmd title patch: patched=%s title_ok=%s missing_noop=%s" % (patched, title_ok, noop_ok))
    ok = ok and patched and title_ok and noop_ok
    if missing:
        print("SELFTEST_INVALID 未触发的缺陷：%s" % ",".join(missing))
    print("SELFTEST_PASS" if ok else "SELFTEST_INVALID")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site")
    ap.add_argument("--plan")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="覆盖已存在的文章文件")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if not a.plan:
        print("FAIL 需要 --plan（或 --selftest）")
        sys.exit(2)
    try:
        data = json.load(io.open(a.plan, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print("FAIL 读计划失败：%s" % e)
        sys.exit(2)
    problems, summary = check_plan(data)
    print("plan_check: categories=%d sections=%d articles=%d problems=%d"
          % (summary.get("categories", 0), summary.get("sections", 0),
             summary.get("articles", 0), len(problems)))
    for code, where, detail in problems[:60]:
        print("  %s :: %s :: %s" % (code, where, detail))
    if problems:
        print("PLAN_INVALID")
        sys.exit(1)
    if a.check_only:
        print("PLAN_OK")
        sys.exit(0)
    if not a.site:
        print("FAIL 写盘需要 --site（或用 --check-only）")
        sys.exit(2)
    site_dir = os.path.abspath(a.site)
    if not os.path.isfile(os.path.join(site_dir, "oink-main", "oink-main", "theme.toml")):
        print("FAIL %s 不是已落地的站点：先跑 scaffold.py 复制主题" % site_dir)
        sys.exit(2)
    if not os.path.isfile(TEMPLATE_HUGO):
        print("FAIL 缺模板 %s" % TEMPLATE_HUGO)
        sys.exit(2)
    sys.exit(write_plan(site_dir, data, a.force))


if __name__ == "__main__":
    main()
