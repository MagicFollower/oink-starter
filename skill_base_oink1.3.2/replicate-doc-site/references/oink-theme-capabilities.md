# OINK 主题能力清单（本地 vendor 副本实测调研，OINK **v1.3.2**）

## 这份文档解决什么

调研对象是本技能自带的 OINK 主题副本 `assets/theme/oink-main/oink-main/`（即 `github.com/pgsty/oink` v1.3.2 的本地化；`scaffold.py` 会把它整目录拷成 `<site>/oink-main/`，正好匹配 `assets/scaffold/go.mod` 里的 `replace github.com/pgsty/oink => ./oink-main/oink-main`），以及该副本在本地的一次实测构建（scaffold 骨架 + Hugo v0.168.0 Extended + Go 1.27.2，`Pages 15 / Static files 34 / 0 ERROR`）。下一条复刻任务可以直接照抄这里的配置片段、front matter 片段与「文件在哪、被谁消费」的对应关系。所有结论只来自亲眼读到的文件。

**路径书写约定**：本文中 `oink-main/oink-main/…` 指技能内的 `assets/theme/oink-main/oink-main/…`（落地后是 `<site>/oink-main/oink-main/…`）；不带这个前缀的相对路径指**生成后的站点根**，其模板对应物在 `assets/scaffold/` 下同名位置。凡是要「读」的文件都在技能目录内，不依赖任何站外路径。

文中数字用 python `os.path.getsize` / `len()` 实测并标注「实测」；数目录一律用 `os.walk` 而不是 `glob`——`glob` 的 `*`/`**` 不匹配以点开头的路径段，会静默少数（实测本副本 `os.walk` 得 1,273 个文件 / 22,234,796 字节；`glob` 会更少，见 `references/pitfalls.md` 第 19 条——glob 少数差额随版本结构变化，一切计数以 `os.walk` 为准）。

主题定位（`oink-main/oink-main/README.md` 第 9 行起）：local-first 的工程文档 Hugo 主题，字体、图标、搜索、图表运行时全部 vendored，普通构建零远程拉取，消费站点不需要 Node.js/npm/CDN。

**与 1.0.0 的主要差异**（改判据/写正文前值得知道，均已在副本内核实）：

- **Hugo 下限从 0.160.1 升到 0.166.0**（`hugo.yaml` `module.hugoVersion` 第 299-302 行、`theme.toml` `min_version`、README 兼容表三处一致）；Go 下限 1.27.0。
- **视觉预设**（1.2.0 新增）：`params.ui.preset: paper|slate`，实验项 `ink|terminal`；`preset_menu` 让读者在外观菜单自选。实现：`layouts/_partials/preset-config.html`、`assets/scss/td/_presets.scss`、`_experimental-presets.scss`、`assets/js/appearance.js`、`layouts/_partials/shell/appearance-menu.html`。
- **Expo 图片相册**（1.3.0 新增）：第 5 种阅读外壳 `type: expo`（`shell_types` 已含 expo），页面 bundle 内 `images/*` 资源出墙/卡片/无缝三种布局 + 原图查看器。实现：`layouts/expo/`（baseof/list/single + print 变体）、`layouts/_partials/expo/`、`assets/js/expo.js`、`assets/scss/td/_expo.scss`。
- **正文排版增强**（1.3.1）：filetree 围栏新增 `wrap=true` 参数（默认 false，长注释换行）；表格新增 `.td-table--wide` 修饰类（横向滚动宽表，`_content.scss` 第 199 行消费）；Markmap 明暗模式文字可读性修复。
- **1.3.2 本身**：撤销 1.3.1 误加的 Dart Sass 强依赖，恢复 Hugo Extended 内置 LibSass——普通消费者**不需要**装任何外部 Sass 编译器（README 兼容表明说）。
- **不变项**（实测核对）：29 个 shortcode、18 个 `_markup` render hook、10 种数据围栏、callout 11 种、22 个 landing 节、32 个 i18n 文件全部与 1.0.0 同名同数；`sidebar_root_for`/`sidebar_root_link_self`/`backlinks` 等骨架在用的键全部保留。

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
| note | 说明 | fa-circle-info | 版本适用说明、口径澄清（长文复刻的主力 callout） |
| tip | 提示 | fa-lightbulb | 技巧性建议 |
| important | 重要 | fa-circle-exclamation | 多口径并存、必须遵守的纪律 |
| warning | 警告 | fa-triangle-exclamation | 破坏性操作、上游缺陷记录 |
| caution | 注意 | fa-circle-xmark | 危险动作前置提醒 |
| success | 成功 | fa-circle-check | 正向结果 |
| danger | 危险 | fa-fire | 严重风险 |
| question | 问题 | fa-circle-question | 存疑待确认 |
| example | 示例 | fa-flask | 示例说明 |
| quote | 引用 | fa-quote-left | 引用出处 |
| details | 详情 | 无图标 | 默认折叠的补充材料（第 40 行：`details` 类型天然折叠） |

`{icon=...}` 属性经 `oink-main/oink-main/layouts/_partials/content/attributes.html` 白名单消费，值必须是 `fa-solid|regular|brands fa-xxx` 否则 warnf 回退类型默认图标（第 18-34 行）。样式在 `oink-main/oink-main/assets/scss/td/_alerts.scss`。

## 2. mermaid

渲染链三步，全在主题内：

1. 围栏钩子 `oink-main/oink-main/layouts/_markup/render-codeblock-mermaid.html`：HTML 输出时置页面 flag `.Page.Store.Set "hasmermaid" true`（第 24 行）并产出容器 `<figure class="td-diagram td-diagram--mermaid" data-td-diagram>`，内含空舞台 `div.td-diagram__stage`、放大按钮、`<script type="application/json" data-td-diagram-source>` 存 JSON 化的图源（第 25-32 行）。markdown/rss/print 三种输出格式走静态分支，只输出 `<pre class="td-mermaid-source">` 源码（第 21-22 行）。
2. 装载 `oink-main/oink-main/layouts/_partials/scripts.html`：`$hasMermaid := and $interactiveOutput (.Page.Store.Get "hasmermaid")`（第 36 行），为真才 `partial "scripts/mermaid.html"`（第 255-257 行）并追加运行时 chunk `js/chunks/mermaid-<lang>.js`（第 327-328 行）。所以是**按页引入**，不是全局。
3. 运行时 `oink-main/oink-main/layouts/_partials/scripts/mermaid.html` 发 vendored 库（production 时 `fingerprint`），`oink-main/oink-main/assets/js/mermaid.js`（经 `ExecuteAsTemplate` 注入 i18n 标签）负责渲染调度：读 `[data-td-diagram]` 舞台、`window.mermaid.render()` 出 SVG、配色切换时重渲。

实测文件与大小：`oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 3,572,661 字节，版本 11.17.2（`oink-main/oink-main/VENDOR.json`，与 1.0.0 相同）。production 构建后 `public/third_party/mermaid/` 下会有原文件与指纹版两个副本。

配置：`startOnLoad` 被运行时强制为 `false`（`oink-main/oink-main/assets/js/mermaid.js` 第 25、56 行，注释明说这是对 Docsy 时代 `startOnLoad:true` 的替换）。`securityLevel` 未在主题配置里出现；vendored 库内置默认 `securityLevel:"strict"`（在 `oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 中实测可搜到）。站点若要改任何 Mermaid 参数，走 `params.mermaid`：运行时把 `.Site.Params.mermaid` 注入 `PARAMS`，`norm()` 按 Mermaid defaultConfig 的大小写键名匹配小写化的 params 键。骨架未配置该项。

## 3. outputs 与额外产物

主题在 `oink-main/oink-main/hugo.yaml` 第 250-289 行注册输出格式：`BookManifest`（book.json）、`LLMS`（llms.txt）、`LLMSFULL`（llms-full.txt，按顶级 section 全文打包，主题不默认开）、`NAVJSON`（navigation.json，机器可读导航树，schema 在 `oink-main/oink-main/schema/nav.v1.schema.json`）、`print`（`path: _print`、`baseName: index`）。每页 `.md` 由 Hugo 内置 markdown 输出 + 主题模板 `oink-main/oink-main/layouts/all.md` 产出，正文渲染共用 `oink-main/oink-main/layouts/_partials/content/markdown-document.md`（all.md 头注：LLMSFULL 也复用这一份渲染器）。RSS 在 `oink-main/oink-main/layouts/_default/rss.xml`，LLMS 首页模板 `oink-main/oink-main/layouts/index.llms.txt`。

骨架 `assets/scaffold/hugo.yaml` 的启用组合与产物对应关系（产物计数以真实构建为准）：

| outputs 声明 | 产物（形态；计数以真实构建为准） |
|--------------|------------------|
| home: HTML, RSS, markdown, LLMS | `public/index.html`、`public/index.xml`、`public/index.md`、`public/llms.txt`（站点+各页 `index.md` 链接清单） |
| page: HTML, markdown | 每篇一个 `index.md`，与 `content/**/*.md` 一一对应 |
| section: HTML, RSS, print, markdown | 每个 section 目录带 `index.xml` 与 `index.md`；整节合并的打印版在 `public/_print/<section 路径>/index.html`，每个 section 一个 |

骨架未启用 `LLMSFULL`、`NAVJSON`、`BookManifest`（启用与否看站点 `outputs` 声明；模板与 schema 见第 3 节首段）。

## 4. 离线搜索（Lunr）

- 开关：`params.offline_search`（主题 `oink-main/oink-main/hugo.yaml` 第 15 行默认 `false`，站点 opt-in；骨架模板设 `true`）。判定收敛在 `oink-main/oink-main/layouts/_partials/shell/search-enabled.html`：`offline_search` 为真、非 print 格式、且（非 server 或 `offline_search_on_serve` 为真）才挂搜索 UI（第 28-33 行）。
- 索引生成：模板是 `oink-main/oink-main/assets/json/offline-search-index.json`（一个 Hugo 模板），由 `oink-main/oink-main/layouts/_partials/offline-search-index.html` 以 `ExecuteAsTemplate` 物化为 `offline-search-index.<lang>.json`，production 下 `fingerprint "md5"`（第 2-7 行）。production 下两个文件并存：带 md5 指纹的 `offline-search-index.<lang>.<hash>.json` 与未哈希的 `offline-search-index.<lang>.json`；页面 HTML 的 `data-td-index-src` 指向未哈希名（历史项目实测）。
- 索引字段：范围是 kind 为 page/section 且有 RawContent 的页（排除 `search_exclude: true`；首页 kind=home 被过滤，所以索引条数 = content md 数 - 1）。每条字段（`oink-main/oink-main/assets/json/offline-search-index.json` 第 35 行起）：`ref,title,excerpt,categories,tags,headings,description,body,root,section,type,keywords,boost,breadcrumb,icon`。索引深度由 `params.offline_search_index` 控制，取值 `title|heading|summary|content`（骨架用默认 content，所以带 `body` 全文）。
- 前端：`oink-main/oink-main/layouts/_partials/shell/search-dialog.html` 把索引 URL 写进 `data-td-index-src`（第 2、4 行），`oink-main/oink-main/assets/js/command-palette.js` 第 209 行 `fetch(root.dataset.tdIndexSrc)`；建库在 `oink-main/oink-main/assets/js/search-engine.js`，运行时三个文件打包为 `js/chunks/local-search.js`（scripts.html 的 local-search chunk 段）。lunr 实测 `oink-main/oink-main/assets/js/third_party/lunr.min.js` 29,510 字节，版本 2.3.9（VENDOR.json）。
- 体验注记（历史项目实测结论）：MB 级索引首次打开面板要一两秒建库，期间输入会落空，别误判为坏了。

## 5. 侧边栏根选择器与相关 UI 开关

`sidebar_root_for`（front matter，仅对 section 有意义）：`oink-main/oink-main/layouts/_partials/shell/sidebar-root.html` 消费。语义：站点默认根是 `Site.Home`（或 `params.ui.docs_sidebar_root: section` 时的 docs section）；某 section 声明 `sidebar_root_for: self` 后，从当前页向上走 Ancestors，第一个命中者成为侧边栏根（第 8-24 行），即「这个分类自己就是一棵独立侧边栏树的根」。取值只接受 `self|children`，非法值 warnf 跳过。骨架的分类 `_index.md` 模板带：

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

`oink-main/oink-main/layouts/_partials/shell/root-menu-roots.html`：全站侧边栏顶部「根切换下拉」的候选收集器（partialCached）：先收 `Site.Home.Sections`，再收所有 `sidebar_root_for: self` 的 section。**v1.3.2 里两个循环都过滤 `sidebar_root_menu: false`、无 permalink的分隔节（`sidebar_divider`）**（第 8、19 行），1.0.0 时代第二个循环不查 `sidebar_root_menu` 的缺口已由主题原生补上。`oink-main/oink-main/layouts/_partials/shell/root-menu.html` 第 5 行以 `params.ui.sidebar_root_menu` 为总开关；只有 1 个候选时降级为静态链接，多个才渲染下拉。当前根的判定与「当前根不在候选集时补入」由 `root-menu-entries.html` 完成（v1.3.2 新拆出的 partial，含 `current` 返回值）。

骨架自带的站点覆盖 `layouts/_partials/shell/root-menu-roots.html`（放在站点 `layouts/_partials/shell/` 下，与主题同名时站点优先）：**v1.3.2 起它是多余的**——它当年补的 `sidebar_root_menu` 过滤缺口主题已自带，且它比主题新版少了 `sidebar_divider`/`RelPermalink` 过滤。保留它无害（行为上只会少过滤分隔节，文档站没有分隔节），但新站点可以直接删掉这个覆盖，以主题原生行为为准。

另一条历史记录：旧站曾试图用带中文括号后缀的 `root-menu-entries（侧边栏下拉卡片列表选中置顶效果）.html` 做「当前根置顶」。主题按名字调用的是 `partial "shell/root-menu-entries.html"`，带后缀的文件名注册成另一个模板名，**永远不会被调用**（详见 `references/pitfalls.md` 第 13 条）。v1.3.2 的下拉触发器直接显示当前根（`root-menu.html` 第 24 行起 `$current` 逻辑），置顶需求已由主题原生满足。**技能骨架不附带任何带说明性后缀的 partial。**

`params.ui.*` 各自控制什么（都能被同名 front matter 覆盖，覆盖解析器是 `oink-main/oink-main/layouts/_partials/ui-param.html`：站点 `params.ui.<key>` 对应 front matter `<key>`，可经 cascade 下发到整节）：

| 配置 | 消费处 | 控制什么 |
|------|--------|----------|
| `section_index: cards`（默认 list） | `oink-main/oink-main/layouts/_partials/section-index.html` 第 31-37 行 | section 落地页子页列表形态；cards 模式输出 `.td-content-card` 卡片网格，列数由 `section_index_columns`（默认 2）控制 |
| `sidebar_menu_foldable`（默认 true） | `oink-main/oink-main/layouts/_partials/shell/sidebar.html` 第 9-12 行 → `sidebar-tree-node.html` | 侧边栏节点是否可点击折叠/展开子树 |
| `sidebar_expand_levels`（默认 2，骨架模板设 4） | `sidebar.html` 第 13-16 行 → `oink-main/oink-main/layouts/_partials/shell/sidebar-tree.html` 第 30 行 `$ulShow := add $expandLevels 1` | 初始化时默认展开到第几层 |
| `sidebar_icon_policy`（`all|groups|none`，非法值 warn 回退 all） | `oink-main/oink-main/layouts/_partials/shell/sidebar-icon-policy.html` | 侧边栏图标密度；骨架用 `groups` = 只显示结构性根与有子节点的行（该文件第 3-4 行注释） |
| `backlinks`（默认 false，骨架模板 true） | `oink-main/oink-main/layouts/_partials/backlinks-sources.html` 第 6-10 行 + `oink-main/oink-main/layouts/_partials/shell/toc-aside.html` 第 9、53 行 | 右栏 TOC 下方「链向本页的页面」分组；构建期由 `oink-main/oink-main/layouts/_partials/backlinks-index.html` 从站内 Markdown 链接与 ref/relref 推导，无运行时请求 |

## 6. `relativeURLs: true` 的实际效果

骨架 `assets/scaffold/hugo.yaml` 开启（注释原话：「相对链接：构建产物可直接从磁盘路径打开」）。机制与验证方法（历史项目实测过的证据形态，任何站点都可复验）：

- 深层文章页里 `<img ... src="../../../../picture/Message.png">`（正文源写的是绝对路径 `![...](/picture/Message.png)`，构建时被改写成 N 级回退的相对路径，N=页面深度）；
- 浅层页同理：`data-td-index-src="../../offline-search-index.zh.json"`、`<link href="../../scss/main.css">`。

两个收益：其一，`public/` 双击 `index.html` 用 `file://` 直开即完整可用（无需任何服务器）；其二，产物可整目录挂到任意子路径的静态服务器而**不必**为子路径改 `baseURL`（`baseURL` 只影响 canonical/RSS/llms.txt 里的绝对链接；骨架模板 `assets/scaffold/hugo.yaml` 第 4 行给的是占位值 `https://example.org/`，上线前必须换掉）。

## 7. goldmark 三项设置

骨架 `assets/scaffold/hugo.yaml` 的 goldmark 段：

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

- `ul.cards`（`oink-main/oink-main/assets/scss/td/_markers.scss` 第 105 行起）：链接列表挂 `{.cards}` 变自适应卡片网格（`grid … minmax(min(100%,15rem),1fr)`）。骨架用法见 `assets/scaffold/content/docs/_index.md`：`- [标题](/docs/xx/)` 链接列表，末行单独写 `{.cards}`。列表项里「链接是标题，其后文字是描述」（该 scss 第 142-144 行注释）。
- `ol.steps`（同文件第 7 行起）：有序列表挂 `{.steps}` 得带圆形计数标记与竖线的步骤条；`start="N"` 偏移在 2..40 范围内被预编译（第 93 行起）。
- `{{< cards >}}/{{< card >}}` 短代码（`oink-main/oink-main/layouts/_shortcodes/cards.html` 第 7 行输出 `<div class="td-content-cards td-content-cards--auto">`）与 `section_index: cards` 共用同一套卡片样式（`oink-main/oink-main/assets/scss/td/_content-components.scss` 第 322-336 行，注释「Shared by `{{< cards >}}` and the section index」）。
- 数据围栏类（`oink-main/oink-main/layouts/_markup/` 下 `render-codeblock-*.html` 实测存在，10 种与 1.0.0 相同）：`mermaid`、`markmap`、`plantuml`、`echarts`、`infographic`、`math`、`chem`、`filetree`、`gallery`、`checksums`；其中 markmap/plantuml/drawio 需 `params.markmap`/`params.plantuml.enable`/`params.drawio.enable` 显式开启（主题 `oink-main/oink-main/hugo.yaml` 第 29-35 行，plantuml/drawio 还强制要求自备服务 URL）。
- 表格有专用钩子 `oink-main/oink-main/layouts/_markup/render-table.html`（及 print/rss 变体）；标题钩子 `oink-main/oink-main/layouts/_markup/render-heading.html`；图片钩子 `oink-main/oink-main/layouts/_markup/render-image.html`。

**1.3.x 排版增强**（写技术文档时按需用，均为正文级语法）：

- **filetree `wrap` 参数**（1.3.1）：```filetree``` 围栏的允许属性新增 `wrap`（`render-codeblock-filetree.html` 第 4 行 allowed 列表），`wrap=true` 让长注释完整换行（含不换行的长标识符），默认 `wrap=false` 保持紧凑行；非法值 warn 回退 false。文件名、折叠、分隔线、移动端堆叠、Print 行为不变。
- **`.td-table--wide` 宽表**（1.3.1）：表格结尾的属性行写 `{.td-table--wide}`，得到「标识符不折断 + 描述限宽 + 横向滚动」的技术宽表（消费在 `assets/scss/td/_content.scss` 第 199 行）；普通表格、字段列表、静态输出布局不变。上游表格逐行保留时，长参数表用这个最稳。
- **Expo 图片相册**（1.3.0）：front matter `type: expo` 的页面（通常做成 leaf bundle），bundle 内 `images/*`（可用 front matter `expo.images` 改 glob）渲染成 wall/cards/seamless 三种布局（`expo.mode`，tile 尺寸 `expo.size` 160-360），带原图查看器（拖拽/WASD 平移、QE/HL 前后张、JK 缩放、R 重置、F 扩展）。站点级默认在 `params.ui.expo`。相册与元数据保留在 Print/Markdown/LLMSFULL/RSS 输出里。
- **视觉预设**（1.2.0，非正文语法但影响观感）：`params.ui.preset: paper`（默认暖纸面）/`slate`（1.1 及以前的技术风）；实验项 `ink`（黑白红）/`terminal`（等宽琥珀）需显式点名。字体本地 IBM Plex Sans，无额外字体文件下载。

**外观一键切换（Appearance 菜单，1.2.0+）**：读者可在最终页面上切换视觉预设与明暗模式，即时生效、不刷新、跨页记住。实现链：`layouts/_partials/shell/appearance-menu.html`（面板，导航栏/页脚/移动端抽屉三处入口）+ `assets/js/appearance.js`（改 `<html data-td-preset>` 换肤、写 `localStorage['td-preset']`、storage 事件跨标签页同步；明暗由 `dark-mode.js` 独立管理）+ `layouts/_partials/head.html` 第 42-66 行内联脚本（首帧渲染前应用存储的预设，无闪烁；非法存储值按白名单清除）。选回站点默认预设会删存储键，站点日后改默认能到达读者；存储被禁用时面板提示「仅本页生效」；无 JS 则面板不渲染、站点默认观感照常。**门控**：面板的渲染条件是 `dark_mode.showMenu` 或 `preset.menu` 二者其一（`preset.menu` = `preset_menu` 提供的选项多于 1 个，`preset-config.html` 第 70 行）。主题默认 `preset_menu: false`——单观感站没有 Style 组；`preset_menu: true` 给 Paper+Slate+站点默认；`preset_menu: [paper, slate, ink, terminal]` 全开放（列表必须含站点默认 `preset`，缺了 WARN 自动补）。骨架 `dark_mode: true` 已默认开明暗切换，预设组开不开在 `preset_menu` 一行。

## 9. 首页数据文件

骨架 `assets/scaffold/data/home/zh.yaml` 的结构（主题按 `<lang>` 取 `data/home/` 下的语言文件；按 home-data.html 头注，单语站可直接放一份不分语言的 home 数据文件）：

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

读取链：主题 `oink-main/oink-main/layouts/index.html` 调 `partial "landing/home-data.html"`（实现在 `oink-main/oink-main/layouts/_partials/landing/home-data.html`，按 `hugo.Data.home` 的语言取，zh 缺失回退 en，再回退单文件形态），无 `sections` 键会 warnf 且不渲染任何节；随后 `oink-main/oink-main/layouts/_partials/landing/render.html` 把每个节名派发到手上有 22 个节实现的 `oink-main/oink-main/layouts/_partials/landing/sections/` 目录（实测 22 个文件），hero/cards/cta 的键名消费分别见 `hero.html` 第 4-6、36-38 行、`cards.html` 第 7-8、15 行、`cta.html` 第 4-24 行。首页文案与 `hugo.yaml` 的 `title` 是两个数据源，改一处必改两处。

## 10. 版本要求与 libsass WARN

- `hugoVersion`：主题 `oink-main/oink-main/hugo.yaml` 第 299-302 行 `module.hugoVersion: { extended: true, min: 0.166.0 }`；`oink-main/oink-main/AGENTS.md` 契约一节写「Hugo Extended 0.166.0 is the minimum and default development/strict CI version」；`oink-main/oink-main/theme.toml` `min_version = "0.166.0"`；`oink-main/oink-main/README.md` 兼容性表：**Extended 0.166.0 起步**、严格 CI 锁 0.166.0、Go 1.27.0 起（当前开发默认 1.27.2；离线归档/replace 本地化时不需要 Go 联网）。骨架模板 `assets/scaffold/hugo.yaml` 复制了同一约束；本项目实测跑通的组合是 Hugo v0.168.0 Extended + Go 1.27.2（`Pages 15 / Static files 34 / 0 ERROR`）。
- 必须 Extended 的依据：主题全部样式经 SCSS 编译——`oink-main/oink-main/layouts/_partials/head-css.html` 第 2-3 行 `resources.Get "scss/main.scss" | toCSS …`（redoc.scss 同理），标准版 Hugo 无 SCSS 编译器，构建直接失败。**1.3.2 恢复纯 LibSass**：1.3.1 曾要求 Dart Sass，1.3.2 撤销——消费者不需要装任何外部 Sass 可执行文件。
- libsass WARN：上述 `toCSS` 即 Hugo 的 css.Sass（libsass）通道，Hugo v0.153.0 起弃用该别名，构建时打出 `WARN deprecated: css.Sass: libsass was deprecated … Use dartsass instead.`（本项目实测：Hugo 0.168.0 下骨架每次构建都打这一条）。这条 WARN 是主题侧固有提示、非消费站点引入，普通构建的验收判据是 0 个 ERROR。**但带 `--panicOnWarning` 的严格发布闸门除外**：该 WARN 会致败——主题契约是严格闸门用 Hugo 0.166.0（其上游无此告警口径差异，见 AGENTS.md「Ordinary 0.168.0 builds may warn」），普通构建/预览用 0.168.0 无妨。
- Hugo 0.166.0 与 0.168.0 之外的新版本：主题 README 明说「Future Hugo releases that remove LibSass require a separate compatibility decision」——LibSass 被移除的 Hugo 版本不在支持范围，别随手升级工具链。

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
| `params.ui.dark_mode` | 按需 | 无明暗切换 |
| `params.ui.preset` / `preset_menu` | paper（默认）/ 按需开放菜单 | 只有单一视觉预设，读者不能自选外观 |
| `params.ui.preset_menu` | `[paper, slate, ink, terminal]`（按需） | 页面上没有外观一键切换面板的 Style 组（`dark_mode: true` 只开明暗切换） |

## 未在主题副本中找到、需实测的项

- `params.mermaid.securityLevel` 等自定义注入：机制在（`oink-main/oink-main/assets/js/mermaid.js` 的 PARAMS/norm），但主题与骨架均未写任何实例配置；实际传参大小写行为需自建一个 `params.mermaid` 验证。
- `LLMSFULL`、`NAVJSON`、`BookManifest` 三个输出的真实产物：本骨架未启用，`public/` 里没有对应文件；只有模板（`oink-main/oink-main/layouts/list.llmsfull.txt`、`oink-main/oink-main/layouts/index.navjson.json`、`oink-main/oink-main/layouts/book/list.bookmanifest.json`）与 `oink-main/oink-main/schema/nav.v1.schema.json` 可读，渲染效果需实测。
- `print` 输出对 mermaid/echarts 围栏的静态分支呈现（`_print/` 里应看到源码块）：本次只验证了构建，未逐页核对渲染质量。
- expo 相册的浏览器端交互（原图查看器手势、键盘流、记忆布局）与 ink/terminal 实验预设的实际观感：实现文件俱在（`assets/js/expo.js`、`assets/scss/td/_experimental-presets.scss`），骨架站没有 expo 页面也没开实验预设，效果需实测。
- 骨架 `content/docs/_index.md` 里 `menus.main.identifier: docs` 与主题自动挂的 docs 入口在构建时报 `duplicate menu entry` WARN（实测，Hugo 0.168.0 + 本主题副本）：普通构建无害，但说明主题 1.3.x 会自己把 `docs_section` 挂进顶栏——新站点若不需要显式菜单项可删掉 front matter 里的 `menus` 块再验证顶栏（此点为观察记录，顶栏最终形态需浏览器实测）。
