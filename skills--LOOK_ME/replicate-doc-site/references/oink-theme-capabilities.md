# OINK 主题能力清单（本地 vendor 副本实测调研）

## 这份文档解决什么

调研对象是本技能自带的 OINK 主题副本 `assets/theme/oink-main/oink-main/`（即 `github.com/pgsty/oink` 的本地化；`scaffold.py` 会把它整目录拷成 `<site>/oink-main/`，正好匹配 `assets/scaffold/go.mod` 里的 `replace github.com/pgsty/oink => ./oink-main/oink-main`），以及一份已验收的真实产出（本站 `hugo.yaml` + `content/docs/**` + `public/`）。下一条复刻任务可以直接照抄这里的配置片段、front matter 片段与「文件在哪、被谁消费」的对应关系。所有结论只来自亲眼读到的文件。

**路径书写约定**：本文中 `oink-main/oink-main/…` 指技能内的 `assets/theme/oink-main/oink-main/…`（落地后是 `<site>/oink-main/oink-main/…`）；不带这个前缀的相对路径指**生成后的站点根**，其模板对应物在 `assets/scaffold/` 下同名位置。凡是要「读」的文件都在技能目录内，不依赖任何站外路径。

文中数字用 python `os.path.getsize` / `len()` 实测并标注「实测」；数目录一律用 `os.walk` 而不是 `glob`——`glob` 的 `*`/`**` 不匹配以点开头的路径段，会静默少数（实测同一份主题 `os.walk` 得 1,196 个文件 / 21,257,008 字节，`glob` 只得 1,189 / 21,239,566，见 `references/pitfalls.md` 第 19 条）。

主题定位（`oink-main/oink-main/README.md` 第 32-35 行）：local-first 的工程文档 Hugo 主题，字体、图标、搜索、图表运行时全部 vendored，普通构建零远程拉取，消费站点不需要 Node.js/npm/CDN。

## 1. callout/admonition

渲染钩子：`oink-main/oink-main/layouts/_markup/render-blockquote-alert.html`（Hugo 的 GFM blockquote-alert render hook）。语法是 GitHub 风格：

```markdown
> [!NOTE] 可选的自定义标题（AlertTitle）
> 正文若干行。

> [!WARNING]- 折叠且默认收起
> [!TIP]+ 折叠且默认展开
> [!CAUTION]{icon="fa-solid fa-rocket"} 自定义图标
```

类型白名单（render-blockquote-alert.html 第 5 行 `$canonical`）共 11 种，渲染为 `<div class="td-callout td-callout--<type>" role="note">`（含 `__title`/`__icon`/`__label`/`__body` 子结构；可折叠时外层变 `<details class="td-callout td-callout--<type> td-callout--collapsible">`）。未知类型不报错，降级为普通 `<blockquote>` 且标记 `[!TYPE]` 保留可见（第 29-36 行）。中文标题在 `oink-main/oink-main/i18n/zh.yaml`（实测 i18n 目录 32 个语言文件）：

| 类型 | zh 标题 | 图标（第 6-18 行） | 什么场合用 |
|------|---------|--------------------|------------|
| note | 说明 | fa-circle-info | 版本适用说明、口径澄清（本站主力：实测 31 篇里 `> [!NOTE]` 101 处） |
| tip | 提示 | fa-lightbulb | 技巧性建议（本站 4 处） |
| important | 重要 | fa-circle-exclamation | 多口径并存、必须遵守的纪律（本站 2 处） |
| warning | 警告 | fa-triangle-exclamation | 破坏性操作、上游缺陷记录（本站 12 处） |
| caution | 注意 | fa-circle-xmark | 危险动作前置提醒 |
| success | 成功 | fa-circle-check | 正向结果 |
| danger | 危险 | fa-fire | 严重风险 |
| question | 问题 | fa-circle-question | 存疑待确认 |
| example | 示例 | fa-flask | 示例说明 |
| quote | 引用 | fa-quote-left | 引用出处 |
| details | 详情 | 无图标 | 默认折叠的补充材料（第 40 行：`details` 类型天然折叠） |

`{icon=...}` 属性经 `oink-main/oink-main/layouts/_partials/content/attributes.html` 白名单消费，值必须是 `fa-solid|regular|brands fa-xxx` 否则 warnf 回退类型默认图标（第 19-28 行）。样式在 `oink-main/oink-main/assets/scss/td/_alerts.scss`。

## 2. mermaid

渲染链三步，全在主题内：

1. 围栏钩子 `oink-main/oink-main/layouts/_markup/render-codeblock-mermaid.html`：HTML 输出时置页面 flag `.Page.Store.Set "hasmermaid" true`（第 24 行）并产出容器 `<figure class="td-diagram td-diagram--mermaid" data-td-diagram>`，内含空舞台 `div.td-diagram__stage`、放大按钮、`<script type="application/json" data-td-diagram-source>` 存 JSON 化的图源（第 25-32 行）。markdown/rss/print 三种输出格式走静态分支，只输出 `<pre class="td-mermaid-source">` 源码（第 21-22 行）。
2. 装载 `oink-main/oink-main/layouts/_partials/scripts.html`：`$hasMermaid := and $interactiveOutput (.Page.Store.Get "hasmermaid")`（第 37 行），为真才 `partial "scripts/mermaid.html"`（第 244-246 行）并追加运行时 chunk `js/chunks/mermaid-<lang>.js`（第 308-313 行）。所以是**按页引入**，不是全局。实测 `public/docs` 下 62 个 HTML 页面中 31 个含 `chunks/mermaid`。
3. 运行时 `oink-main/oink-main/layouts/_partials/scripts/mermaid.html` 发 vendored 库（production 时 `fingerprint`），`oink-main/oink-main/assets/js/mermaid.js`（经 `ExecuteAsTemplate` 注入 i18n 标签）负责渲染调度：读 `[data-td-diagram]` 舞台、`window.mermaid.render()` 出 SVG、配色切换时重渲。

实测文件与大小：`oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 3,572,661 字节（production 构建后在 `public/third_party/mermaid/` 下同时有 `mermaid.min.js` 与指纹版 `mermaid.min.581ed7d7…390eb8.js`，均 3,572,661 字节）。版本 11.17.2（`oink-main/oink-main/VENDOR.json`）。

配置：`startOnLoad` 被运行时强制为 `false`（`oink-main/oink-main/assets/js/mermaid.js` 第 25、56 行，注释明说这是对 Docsy 时代 `startOnLoad:true` 的替换）。`securityLevel` 未在主题配置里出现；vendored 库内置默认 `securityLevel:"strict"`（在 `oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 中实测可搜到）。站点若要改任何 Mermaid 参数，走 `params.mermaid`：运行时把 `.Site.Params.mermaid` 注入 `PARAMS`（第 30 行），`norm()` 按 Mermaid defaultConfig 的大小写键名匹配小写化的 params 键（第 31-51 行）。本站未配置该项。

## 3. outputs 与额外产物

主题在 `oink-main/oink-main/hugo.yaml` 第 233-272 行注册输出格式：`BookManifest`（book.json）、`LLMS`（llms.txt）、`LLMSFULL`（llms-full.txt，按顶级 section 全文打包，主题不默认开）、`NAVJSON`（navigation.json，机器可读导航树，schema 在 `oink-main/oink-main/schema/nav.v1.schema.json`）、`print`（`path: _print`、`baseName: index`）。每页 `.md` 由 Hugo 内置 markdown 输出 + 主题模板 `oink-main/oink-main/layouts/all.md` 产出，正文渲染共用 `oink-main/oink-main/layouts/_partials/content/markdown-document.md`（all.md 头注：LLMSFULL 也复用这一份渲染器）。RSS 在 `oink-main/oink-main/layouts/_default/rss.xml`，LLMS 首页模板 `oink-main/oink-main/layouts/index.llms.txt`。

本站 `hugo.yaml` 第 35-38 行的启用组合与 `public/` 实测对应物：

| outputs 声明 | 产物（实测计数） |
|--------------|------------------|
| home: HTML, RSS, markdown, LLMS | `public/index.html`、`public/index.xml`、`public/index.md`、`public/llms.txt`（站点+各页 `index.md` 链接清单） |
| page: HTML, markdown | 每篇一个 `index.md`；`public/**/*.md` 实测 63 个，与 `content/**/*.md` 63 个一一对应 |
| section: HTML, RSS, print, markdown | 每个 section 目录带 `index.xml` 与 `index.md`；`public/**/index.xml` 实测 34 个；整节合并的打印版在 `public/_print/<section 路径>/index.html`，实测 31 个（31 个 section） |

本站未启用 `LLMSFULL`、`NAVJSON`、`BookManifest`（`public/` 根实测无 `llms-full.txt`、无 `navigation.json`）。

## 4. 离线搜索（Lunr）

- 开关：`params.offline_search`（主题 `oink-main/oink-main/hugo.yaml` 第 15 行默认 `false`，站点 opt-in；本站设 `true`）。判定收敛在 `oink-main/oink-main/layouts/_partials/shell/search-enabled.html`：`offline_search` 为真、非 print 格式、且（非 server 或 `offline_search_on_serve` 为真）才挂搜索 UI（第 28-33 行）。
- 索引生成：模板是 `oink-main/oink-main/assets/json/offline-search-index.json`（一个 Hugo 模板），由 `oink-main/oink-main/layouts/_partials/offline-search-index.html` 以 `ExecuteAsTemplate` 物化为 `offline-search-index.<lang>.json`，production 下 `fingerprint "md5"`（第 2-7 行）。`public/` 实测两个文件并存：`offline-search-index.zh.85c6ac53ed4acc0df8132b8e6530f20f.json` 与未哈希的 `offline-search-index.zh.json`，各 1,571,752 字节；当前快照的页面 HTML 里 `data-td-index-src` 指向未哈希名。
- 索引字段：范围是 kind 为 page/section 且有 RawContent 的页（排除 `search_exclude: true`），实测 62 条（content 63 个 md，首页 kind=home 被过滤）。每条字段（`oink-main/oink-main/assets/json/offline-search-index.json` 第 33-49 行 + 实测 JSON 键）：`ref,title,excerpt,categories,tags,headings,description,body,root,section,type,keywords,boost,breadcrumb,icon`。索引深度由 `params.offline_search_index` 控制，取值 `title|heading|summary|content`（本站用默认 content，所以带 `body` 全文）。
- 前端：`oink-main/oink-main/layouts/_partials/shell/search-dialog.html` 把索引 URL 写进 `data-td-index-src`（第 2、4 行），`oink-main/oink-main/assets/js/command-palette.js` 第 168 行 `fetch(root.dataset.tdIndexSrc)`；建库在 `oink-main/oink-main/assets/js/search-engine.js`，运行时三个文件打包为 `js/chunks/local-search.js`（scripts.html 第 234-242 行）。lunr 实测 `oink-main/oink-main/assets/js/third_party/lunr.min.js` 29,510 字节，版本 2.3.9（VENDOR.json）。
- 体验注记（本站实测结论）：1.5 MB 级索引首次打开面板要一两秒建库，期间输入会落空，别误判为坏了。

## 5. 侧边栏根选择器与相关 UI 开关

`sidebar_root_for`（front matter，仅对 section 有意义）：`oink-main/oink-main/layouts/_partials/shell/sidebar-root.html` 消费。语义：站点默认根是 `Site.Home`（或 `params.ui.docs_sidebar_root: section` 时的 docs section）；某 section 声明 `sidebar_root_for: self` 后，从当前页向上走 Ancestors，第一个命中者成为侧边栏根（第 8-24 行），即「这个分类自己就是一棵独立侧边栏树的根」。取值只接受 `self|children`，非法值 warnf 跳过。本站 10 个一级分类的 `_index.md` 都带：

```yaml
type: docs
icon: fa-solid fa-compass
weight: 1
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
```

`sidebar_root_link_self`（布尔）：`oink-main/oink-main/layouts/_partials/shell/sidebar-node.html` 第 36-47 行消费。当某节点是根且 `sidebar_root_for: self` 而 `sidebar_root_link_self: false` 时，侧边栏根那一行的链接改为指向其父级；默认 `true`（指向自己）。非布尔值 warnf 回退 true。

`oink-main/oink-main/layouts/_partials/shell/root-menu-roots.html`：全站侧边栏顶部「根切换下拉」的候选收集器（partialCached）：先收 `Site.Home.Sections`（按 weight，`sidebar_root_menu: false` 者剔除），再收所有 `sidebar_root_for: self` 的 section（主题原版这第二个循环**不查** `sidebar_root_menu`）。`oink-main/oink-main/layouts/_partials/shell/root-menu.html` 第 5 行以 `params.ui.sidebar_root_menu` 为总开关；只有 1 个候选时降级为静态链接，多个才渲染下拉（第 9-17 行）。

本站的两个覆盖（放在站点 `layouts/_partials/shell/` 下，与主题同名 partial 时站点优先）：

- `layouts/_partials/shell/root-menu-roots.html`：在第二个循环补了 `(ne .Params.sidebar_root_menu false)`，让 `sidebar_root_menu: false` 对两类来源都生效（文件头注自述；代码第 38 行）。同名覆盖，确定生效；本站 content 实测没有任何页面用 `sidebar_root_menu: false`，所以当前是「备而未用」。
- `layouts/_partials/shell/root-menu-entries（侧边栏下拉卡片列表选中置顶效果）.html`：意图是把当前页所属根节点移到下拉列表首位（头注自述 + 代码里的置顶排序段）。但注意：主题按名字调用的是 `partial "shell/root-menu-entries.html"`，这个带中文括号后缀的文件会注册成另一个模板名；在 `public/docs/10-community/index.html`（晚于该 partial 的构建快照）里实测 `td-is-active` 项排在第 11 位而非首位，即**置顶行为在当前产物中未生效**。要让它生效需改名为精确的 `root-menu-entries.html`——此点属推断，需重建验证。**技能骨架已不再附带这个文件**：带说明性后缀的 partial 名永远不会被 Hugo 调用，留在骨架里等于把死文件复制进每一个新站（详见 `references/pitfalls.md` 第 13 条）。

`params.ui.*` 各自控制什么（都能被同名 front matter 覆盖，覆盖解析器是 `oink-main/oink-main/layouts/_partials/ui-param.html`：站点 `params.ui.<key>` 对应 front matter `<key>`，可经 cascade 下发到整节）：

| 配置 | 消费处 | 控制什么 |
|------|--------|----------|
| `section_index: cards`（默认 list） | `oink-main/oink-main/layouts/_partials/section-index.html` 第 31-37 行 | section 落地页子页列表形态；cards 模式输出 `.td-content-card` 卡片网格，列数由 `section_index_columns`（默认 2）控制 |
| `sidebar_menu_foldable`（默认 true） | `oink-main/oink-main/layouts/_partials/shell/sidebar.html` 第 9-12 行 → `sidebar-tree-node.html` | 侧边栏节点是否可点击折叠/展开子树 |
| `sidebar_expand_levels`（默认 2，本站设 4） | `sidebar.html` 第 13-16 行 → `oink-main/oink-main/layouts/_partials/shell/sidebar-tree.html` 第 30 行 `$ulShow := add $expandLevels 1` | 初始化时默认展开到第几层 |
| `sidebar_icon_policy`（`all|groups|none`，非法值 warn 回退 all） | `oink-main/oink-main/layouts/_partials/shell/sidebar-icon-policy.html` | 侧边栏图标密度；本站 `groups` = 只显示结构性根与有子节点的行（该文件第 3-4 行注释） |
| `backlinks`（默认 false，本站 true） | `oink-main/oink-main/layouts/_partials/backlinks-sources.html` 第 6-10 行 + `oink-main/oink-main/layouts/_partials/shell/toc-aside.html` 第 9、53 行 | 右栏 TOC 下方「链向本页的页面」分组；构建期由 `oink-main/oink-main/layouts/_partials/backlinks-index.html` 从站内 Markdown 链接与 ref/relref 推导，无运行时请求 |

## 6. `relativeURLs: true` 的实际效果

本站 `hugo.yaml` 第 4 行开启（注释原话：「相对链接：构建产物可直接从磁盘路径打开」）。实测证据：取深层文章页 `public/docs/01-overview/版本演进与限制/4x与5x差异及迁移选型/index.html`（该文件内）：

- `<img ... src="../../../../picture/Message.png">`（正文源里写的是绝对路径 `![...](/picture/Message.png)`，构建时被改写成 4 级回退的相对路径）；
- 浅两层处同理：`public/docs/10-community/index.html` 里 `data-td-index-src="../../offline-search-index.zh.json"`、`<link href="../../scss/main.css">`。

两个收益：其一，`public/` 双击 `index.html` 用 `file://` 直开即完整可用（无需任何服务器）；其二，产物可整目录挂到任意子路径的静态服务器而**不必**为子路径改 `baseURL`（`baseURL` 只影响 canonical/RSS/llms.txt 里的绝对链接；骨架模板 `assets/scaffold/hugo.yaml` 第 4 行给的是占位值 `https://example.org/`，上线前必须换掉）。

## 7. goldmark 三项设置

本站 `hugo.yaml` 第 23-31 行：

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true
    parser:
      attribute:
        block: true
      wrapStandAloneImageWithinParagraph: false
  highlight:
    noClasses: false
```

主题 `oink-main/oink-main/README.md` 第 105-117 行说明这是硬性前提且「Hugo 不会把主题模块的 Goldmark 设置合并进站点」，必须由站点自己写。对应支撑的能力：

- `unsafe: true`：放行正文里的原始 HTML。删掉后主题各 render hook 产出的 HTML 组件（callout、figure、卡片等）与内容里手写的 HTML 会被转义成字面文本。
- `parser.attribute.block: true`：启用块级属性 `{.cards}` `{.steps}` `{#id}` `{icon=...}`。`oink-main/oink-main/assets/scss/td/_markers.scss` 第 1-2 行注释明说「Goldmark list classes are the authoring API for CSS-only steps and cards」。删掉后列表尾行的 `{.cards}` 变成正文里的字面字符串，卡片网格、步骤条、callout 的 `{icon=}` 全失效。
- `wrapStandAloneImageWithinParagraph: false`：独占一行的图片不再被包进 `<p>`，`oink-main/oink-main/layouts/_markup/render-image.html` 才能把它升级为 `<figure class="td-figure…">` 并挂 caption/编号（第 114-121 行）。删掉后块级图片属性与 figure 渲染退化。
- `highlight.noClasses: false` 配合主题 `params.highlight_classes: true`（主题 `oink-main/oink-main/hugo.yaml` 第 10 行注释：Hugo 会忽略主题自带的 `markup`，所以主题在 `oink-main/oink-main/layouts/_markup/render-codeblock.html` 里自己套 Chroma class），使代码高亮跟随明暗色板。

## 8. 卡片/网格等正文语法

主题 CSS 里实测查到的「原生 Markdown + 属性」语法：

- `ul.cards`（`oink-main/oink-main/assets/scss/td/_markers.scss` 第 105 行起）：链接列表挂 `{.cards}` 变自适应卡片网格（`grid … minmax(min(100%,15rem),1fr)`）。本站用法见 `content/docs/_index.md` 第 20-30 行：10 行 `- [标题](/docs/xx/)` 列表，末行单独写 `{.cards}`。列表项里「链接是标题，其后文字是描述」（该 scss 第 142-144 行注释）。
- `ol.steps`（同文件第 7 行起）：有序列表挂 `{.steps}` 得带圆形计数标记与竖线的步骤条；`start="N"` 偏移在 2..40 范围内被预编译（第 92-96 行）。
- `{{< cards >}}/{{< card >}}` 短代码（`oink-main/oink-main/layouts/_shortcodes/cards.html` 第 7 行输出 `<div class="td-content-cards td-content-cards--auto">`）与 `section_index: cards` 共用同一套卡片样式（`oink-main/oink-main/assets/scss/td/_content-components.scss` 第 322-336 行，注释「Shared by `{{< cards >}}` and the section index」）。
- 数据围栏类（`oink-main/oink-main/layouts/_markup/` 下 `render-codeblock-*.html` 实测存在）：`mermaid`、`markmap`、`plantuml`、`echarts`、`infographic`、`math`、`chem`、`filetree`、`gallery`、`checksums`；其中 markmap/plantuml/drawio 需 `params.markmap`/`params.plantuml.enable`/`params.drawio.enable` 显式开启（主题 `oink-main/oink-main/hugo.yaml` 第 29-35 行，plantuml/drawio 还强制要求自备服务 URL）。
- 表格有专用钩子 `oink-main/oink-main/layouts/_markup/render-table.html`（及 print/rss 变体）；标题钩子 `oink-main/oink-main/layouts/_markup/render-heading.html`；图片钩子 `oink-main/oink-main/layouts/_markup/render-image.html`。

## 9. 首页数据文件

本站 `data/home/zh.yaml` 实测结构（主题按 `<lang>` 取 `data/home/` 下的语言文件；按 home-data.html 头注，单语站可直接放一份不分语言的 home 数据文件）：

```yaml
sections: [hero, cards, cta]      # 必填：渲染顺序
hero:
  align: center                    # start|center
  eyebrow: …
  title_lines:
    - words: [{ text: … }]
  lead: …
  actions:
    - { label: …, url: …, icon: fa-solid fa-book, style: primary }   # style: primary|ghost
cards:
  eyebrow: …
  title: …
  columns: 3                       # 缺省 3
  items:
    - { title: …, desc: …, icon: …, url: … }
cta:
  title: …
  text: …                          # 也可写 desc；单按钮用 label/url/style，多按钮用 actions 列表
```

读取链：主题 `oink-main/oink-main/layouts/index.html` 调 `partial "landing/home-data.html"`（实现在 `oink-main/oink-main/layouts/_partials/landing/home-data.html`，按 `hugo.Data.home` 的语言取，zh 缺失回退 en，再回退单文件形态），无 `sections` 键会 warnf 且不渲染任何节；随后 `oink-main/oink-main/layouts/_partials/landing/render.html` 把每个节名派发到手上有 22 个节实现的 `oink-main/oink-main/layouts/_partials/landing/sections/` 目录（实测 22 个文件），hero/cards/cta 的键名消费分别见 `hero.html` 第 4-6、36-38 行、`cards.html` 第 7-8、15 行、`cta.html` 第 4-24 行。首页文案与 `hugo.yaml` 的 `title` 是两个数据源，改一处必改两处（本站文档第五章同告）。

## 10. 版本要求与 libsass WARN

- `hugoVersion`：主题 `oink-main/oink-main/hugo.yaml` 第 283-285 行 `module.hugoVersion: { extended: true, min: 0.160.1 }`；`oink-main/oink-main/AGENTS.md` 契约一节写「Hugo Extended 0.160.1 is the compatibility floor」；`oink-main/oink-main/theme.toml` `min_version = "0.160.1"`；`oink-main/oink-main/README.md` 第 205 行兼容性表：Extended 0.160.1 起步、CI 锁 0.165.0、Go 1.27+（离线归档/replace 本地化时不需要 Go 联网）。骨架模板 `assets/scaffold/hugo.yaml` 第 70-72 行复制了同一约束；本项目实测跑通的组合是 Hugo v0.168.0 Extended + Go 1.25.4。
- 必须 Extended 的依据：主题全部样式经 SCSS 编译——`oink-main/oink-main/layouts/_partials/head-css.html` 第 2-3 行 `resources.Get "scss/main.scss" | toCSS …`（`oink-main/oink-main/layouts/_partials/scripts.html` 第 253 行对 redoc.scss 同样），标准版 Hugo 无 SCSS 编译器，构建直接失败。
- libsass WARN：上述 `toCSS` 即 Hugo 的 css.Sass（libsass）通道，Hugo v0.153.0 起弃用该别名，构建时打出 `WARN deprecated: css.Sass: libsass was deprecated … Use dartsass instead.`（本项目实测：骨架与成品站每次构建都会打这一条）。`head-css.html` 第 4-5 行注释解释主题为何还在 libsass 上：Font Awesome 7 的 SCSS 源码需要 Dart Sass，主题改投官方编译好的 CSS。结论：这条 WARN 是主题侧固有提示、非消费站点引入，验收判据是 0 个 ERROR。

## 复刻时必开的主题开关清单

| 配置项 | 建议值 | 不开会怎样 |
|--------|--------|------------|
| `markup.goldmark.renderer.unsafe` | true | 主题各 render hook 的 HTML 与正文内嵌 HTML 被转义为字面文本 |
| `markup.goldmark.parser.attribute.block` | true | `{.cards}`/`{.steps}`/`{icon=}` 等块级属性失效并露出字面字符串 |
| `markup.goldmark.parser.wrapStandAloneImageWithinParagraph` | false | 独占行图片被包进 `<p>`，figure/caption 渲染退化 |
| `markup.highlight.noClasses` | false | 代码高亮内联色，不跟明暗色板（配合主题 `params.highlight_classes`） |
| `relativeURLs` | true | 产物不能双击直开、挂子路径要改 baseURL |
| `params.offline_search` | true | 没有站内搜索；`offline_search_on_serve` 控制 `hugo server` 下是否也建索引 |
| `outputs.home` 含 `markdown` 与 `LLMS` | 按需 | 没有 `/index.md` 与 `/llms.txt` 的机器可读面 |
| `outputs.section` 含 `print` | 按需 | 没有 `_print/` 整节合并打印页 |
| 每篇文章 front matter `title/description/weight` | 必填 | description 缺失会让搜索摘要与卡片描述变空 |
| section `_index.md` 的 `sidebar_root_for: self`（+按需 `sidebar_root_link_self: true`、`icon`、`cascade`） | 按站的分类树定 | 侧边栏不以此为根，全站一棵大树 |
| `params.ui.section_index: cards` | 按需 | section 落地页退回纵向列表 |
| `params.ui.sidebar_expand_levels` / `sidebar_menu_foldable` / `sidebar_icon_policy: groups` | 按需 | 默认只展开 2 层、图标全显 |
| `params.ui.backlinks` | 按需 | 右栏无反向链接组 |
| `params.ui.dark_mode` | 按需 | 无主题切换 |

## 未在主题副本中找到、需实测的项

- `params.mermaid.securityLevel` 等自定义注入：机制在（`oink-main/oink-main/assets/js/mermaid.js` 的 PARAMS/norm），但主题与本站均未写任何实例配置；实际传参大小写行为需自建一个 `params.mermaid` 验证。
- 带中文括号文件名的 partial 覆盖是否参与 Hugo 模板解析：主题副本无规则文档；产物证据显示置顶未生效（见第 5 节），需要重命名后重建对比。
- `LLMSFULL`、`NAVJSON`、`BookManifest` 三个输出的真实产物：本站未启用，`public/` 里没有对应文件；只有模板（`oink-main/oink-main/layouts/list.llmsfull.txt`、`oink-main/oink-main/layouts/index.navjson.json`、`oink-main/oink-main/layouts/book/list.bookmanifest.json`）与 `oink-main/oink-main/schema/nav.v1.schema.json` 可读，渲染效果需实测。
- `print` 输出对 mermaid/echarts 围栏的静态分支呈现（`_print/` 里应看到源码块）：本次只统计了文件数，未逐页核对渲染质量。
- 官方文档站（`oink.pgsty.com`）上的组件参数手册不在本仓库副本内（`oink-main/oink-main/AGENTS.md` 明说公共文档在 sibling 仓库），本清单只覆盖实现文件本身。
- 浏览器端交互类能力（命令面板全键盘流、图片放大 `image_zoom`、阅读进度等）：主题文件俱在（如 `oink-main/oink-main/assets/js/image-zoom.js`、`oink-main/oink-main/layouts/_partials/content/image-zoom-config.html`），但本站未开启 `params.ui.image_zoom`，效果需实测。
