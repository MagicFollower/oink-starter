# OINK 主题能力清单（本地 vendor 副本实测调研，OINK **v1.4.0**）

## 这份文档解决什么

调研对象是本技能自带的 OINK 主题副本 `assets/theme/oink-main/oink-main/`（即 `github.com/pgsty/oink` v1.4.0 的本地化；`scaffold.py` 把它整目录拷成 `<site>/oink-main/`，匹配 `assets/scaffold/go.mod` 里的 `replace github.com/pgsty/oink => ./oink-main/oink-main`），以及多次真实构建。新站可以直接照抄这里的配置片段、front matter 片段与「文件在哪、被谁消费」的对应关系。所有结论只来自亲眼读到的文件与实测输出。

**路径书写约定**：本文中 `oink-main/oink-main/…` 指技能内的 `assets/theme/oink-main/oink-main/…`（落地后是 `<site>/oink-main/oink-main/…`）；不带这个前缀的相对路径指**生成后的站点根**，其模板在 `assets/templates/`，站点身份/首页/导航由 `scripts/plan_site.py` 生成。凡是要「读」的文件都在技能目录内，不依赖任何站外路径。

文中数字用 python `os.path.getsize` / `len()` 实测并标注「实测」；数目录一律用 `os.walk` 而不是 `glob`——`glob` 的 `*`/`**` 不匹配以点开头的路径段，会静默少数（实测本副本 `os.walk` 得 1,292 个文件 / 27,213,292 字节；`glob` 会更少，见 `references/pitfalls.md` 第 19 条——glob 少数差额随版本结构变化，一切计数以 `os.walk` 为准）。

主题定位（`oink-main/oink-main/README.md` 第 9 行起）：local-first 的工程文档 Hugo 主题，字体、图标、搜索、图表运行时全部 vendored，普通构建零远程拉取，消费站点不需要 Node.js/npm/CDN。

**与 1.3.2 的主要差异**（2026-10-29 对齐基线时逐文件核实；副本与上游 tag `v1.4.0` 的 1,292 个 blob 全等，`VENDOR.json` 29 包 / 74 工件 sha256 全中）：

- **Hugo 下限 0.166.0 → 0.168.0**（`theme.toml min_version`、`hugo.yaml module.hugoVersion` 第 306-309 行、AGENTS.md 契约三处一致）；**Go 下限 1.27.0 → 1.27.3**（主题自身 `go.mod` 第 3 行）。两条都是下界，且被 `replace` 的主题 go.mod 也参与取最大值。
- **契约翻转：禁止 `--panicOnWarning`**。1.3.2 的 AGENTS.md 写「default checkers 用 `--panicOnWarning`、0.166.0 是严格闸门版本」；1.4.0 明确「不要在任何 build、checker、preview、CI 里开 `--panicOnWarning` 或 `HUGO_PANICONWARNING`」，LibSass WARN 要保持可见并被接受，同时删掉了 warning-fatal 构建旗标与旧 Hugo 编译器矩阵。
- **新增 PlantUML 本地渲染**：vendored `@plantuml/core` 1.2026.9（`assets/third_party/plantuml/plantuml.js` 3,359,666 B）+ Viz.js 3.24.0（`viz-global.js` 1,445,436 B），零 Java/Graphviz/npm/服务端。默认 `params.plantuml.enable: false`（在 `params` 顶层，与 `markmap`/`drawio` 同级，**不在 `params.ui` 下**；主题 hugo.yaml 第 33-34 行），未启用时页面不引用这两个资产（实测首页 grep = 0）。技能体积 +4.98 MB 主要来自这里。
- **图表运行时改版**：新增 `assets/js/diagram.js`（20,035 B）统一 Mermaid/PlantUML 的平移缩放、适应窗口、看/复制源码、下载 SVG；`layouts/_partials/scripts/mermaid.html` 不再直接吐 `<script src … integrity>`，改成 `<script type="application/json" data-td-mermaid-config>` 让适配器按需加载；`render-codeblock-mermaid.html` 现在额外输出 `<pre class="td-mermaid-source">` 源文（JS 关闭、打印、渲染前都可读）。**渲染改为接近视口才执行**（`IntersectionObserver`，`rootMargin: '320px'`）。
- **表格阅读**：新增 `.expand`（`layouts/_partials/content/table-reader.html` + `assets/js/table-reader.js`，原生 `<dialog>`，保原文/字号/链接/选区，关闭还原阅读位置）与作者侧 `.wide` 标记（与既有 `td-table--wide` 兼容）。`_table.scss` 2,458 → 6,341 B。
- **离线搜索重写**：`assets/js/search-engine.js` 5,516 → 11,687 B；新增 `layouts/_partials/search/sections.html`（当前小节筛选）；索引模板 `assets/json/offline-search-index.json` 2,539 → 3,204 B，每条 doc 新增 `section`/`headings`/`breadcrumb` 等字段（实测 1.4.0 构建产物 409 条）；`i18n/zh.yaml` 新增 11 键（`ui_search_scope*`、`ui_table_*`、`ui_diagram_*`）。
- **新组件变体**：`cards variant="list"`、`steps variant="compact"`、代码围栏 `.td-code-command`；`blog_index` 增加第四种 `gallery`（配 `params.ui.blog_gallery.mode: wall|cards|seamless`、`size: 160..360`）。
- **不变项**（实测核对，所以这些判据不用重测）：`mermaid.min.js` **字节全等**（3,572,661 B，sha256 `581ed7d7…`，VENDOR 仍 pin 11.17.2）；4 个预设名 `paper/slate/ink/terminal` 全在且 `preset-config.html` 未变；`_markup/render-codeblock-*` 仍 11 个文件（10 种数据围栏无增删）；`head-css.html`、`shell/root-menu*.html` 三个文件字节未变（本文后面引用它们的行号仍有效）；callout 类型白名单、29 个 shortcode、32 个 i18n 文件数量不变；产物文件名口径不变（`offline-search-index.zh.<hash>.json`、`llms.txt`、`_print/`、`data-td-preset` 全部照旧）。

**与 1.0.0 的主要差异**（历史口径，改判据/写正文前值得知道）：

- **Hugo 下限从 0.160.1 升到 0.166.0**（1.3.x 时代）；1.4.0 再升到 **0.168.0**。Go 下限 1.27.0 → **1.27.3**。
- **视觉预设**（1.2.0 新增）：`params.ui.preset: paper|slate`，实验项 `ink|terminal`；`preset_menu` 让读者在外观菜单自选。实现：`layouts/_partials/preset-config.html`、`assets/scss/td/_presets.scss`、`_experimental-presets.scss`、`assets/js/appearance.js`、`layouts/_partials/shell/appearance-menu.html`。
- **Expo 图片相册**（1.3.0 新增）：第 5 种阅读外壳 `type: expo`（`shell_types` 已含 expo），页面 bundle 内 `images/*` 资源出墙/卡片/无缝三种布局 + 原图查看器。实现：`layouts/expo/`（baseof/list/single + print 变体）、`layouts/_partials/expo/`、`assets/js/expo.js`、`assets/scss/td/_expo.scss`。
  **`type: expo` 必须写在相册页自己身上**：Hugo 的页面 `.Type` 默认取 section 名，section `_index.md` 上写 `type: expo` 只让该 section 走 expo 外壳，子页仍走 `_default/single.html`，结果是**页面正常构建、零告警、但一张相册图都不出**。实测补上页级 `type: expo` 后：`data-td-expo-item` 6 与 5、`<img>` 9 与 8、`data-td-expo-mode` 分别为 cards/seamless、`data-td-expo-size` 260/220。配置项 `expo` 是 map（`images` 资源通配、`mode`、`size`），由 `expo/config.html` 校验，非法值 warn 后退回默认。
- **`blog_index_toggle` 的产物形态**：开关生效时索引页出现 1 个 `data-td-blog-forms` 容器与 4 个 `data-td-blog-form`（list/cards/table/gallery）；取值走 `ui-param.html`，页面 front matter 优先于 `params.ui.blog_index_toggle`，写在 section 上即可，不必改 `hugo.yaml`。
- **正文排版增强**（1.3.1）：filetree 围栏新增 `wrap=true` 参数（默认 false，长注释换行）；表格新增 `.td-table--wide` 修饰类（横向滚动宽表，`_content.scss` 第 199 行消费）；Markmap 明暗模式文字可读性修复。
- **1.3.2 本身**：撤销 1.3.1 误加的 Dart Sass 强依赖，恢复 Hugo Extended 内置 LibSass——普通消费者**不需要**装任何外部 Sass 编译器（README 兼容表明说）。
- **不变项**（实测核对）：29 个 shortcode、18 个 `_markup` render hook、10 种数据围栏、callout 11 种、22 个 landing 节、32 个 i18n 文件全部与 1.0.0 同名同数；`sidebar_root_for`/`sidebar_root_link_self`/`backlinks` 等站点模板在用的键全部保留。

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
| note | 说明 | fa-circle-info | 版本适用说明、口径澄清（长文的主力 callout） |
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

渲染链三步，全在主题内（1.4.0 口径；1.3.2 的两处差异见本节末）：

1. 围栏钩子 `oink-main/oink-main/layouts/_markup/render-codeblock-mermaid.html`：HTML 输出时置页面 flag `.Page.Store.Set "hasmermaid" true`（第 24 行）并产出容器 `<figure class="td-diagram td-diagram--mermaid" data-td-diagram>`，内含空舞台 `div.td-diagram__stage`（第 26 行）、**新增的可读源码 `<pre class="td-mermaid-source" tabindex="0">`（第 27 行）**、放大按钮、`<script type="application/json" data-td-diagram-source>` 存 JSON 化的图源（第 32 行）。markdown/rss/print 三种输出格式走静态分支，只输出 `<pre class="td-mermaid-source">` 源码（第 21-22 行）。
2. 装载 `oink-main/oink-main/layouts/_partials/scripts.html`：`$hasMermaid := and $interactiveOutput (.Page.Store.Get "hasmermaid")`（第 37 行），为真才 `partial "scripts/mermaid.html"`（第 267-268 行）；并且只要 `$hasMermaid` 或「启用 PlantUML 且没配服务端」（第 184 行）就追加共享运行时 chunk `js/chunks/diagram.js`（第 186 行）。所以仍是**按页引入**，不是全局。
3. 运行时：`oink-main/oink-main/layouts/_partials/scripts/mermaid.html` 在 1.4.0 **不再直接发 `<script src=… integrity>`**，改为输出一段 `<script type="application/json" data-td-mermaid-config>`，内容是 `{"src": …, "integrity": …}`；适配器 `assets/js/mermaid.js` 第 3-4 行读这段配置、且要求 `window.OinkDiagrams` 已存在才工作，第 59 行用 `OinkDiagrams.register({kind:'mermaid', …})` 登记渲染器。**引擎真正加载推迟到图接近视口**：`assets/js/diagram.js` 第 111-112 行 `new IntersectionObserver(wake, { rootMargin: '320px' })`，滚动是「无 IntersectionObserver」的兜底路径（第 171 行注释）。`startOnLoad` 仍被强制为 `false`（`assets/js/mermaid.js` 第 36 行）。

实测文件与大小：`oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 3,572,661 字节，版本 11.17.2（`VENDOR.json`，与 1.0.0/1.3.2 **字节全等**，sha256 `581ed7d7…`）。production 构建后 `public/third_party/mermaid/` 下会有原文件与指纹版两个副本。

**判据口径的两条影响**：

- 页面级验收**必须先把图滚进视口附近**再判渲染，否则看到的是 `<pre>` 源码而不是图；源码态既不是失败也不是成功。
- 本技能的 `validate_mermaid.py` 直连 vendored 引擎（页内 `MERMAID.parse()`），**不走** diagram.js 的懒渲染路径，所以解析台读数与「页面上是否已渲染」是两套口径，不要互相顶替。引擎字节未变 ⇒ 1.3.2 时代跑通的解析台判据仍然有效，无需重建。

配置：`securityLevel` 未在主题配置里出现；vendored 库内置默认 `securityLevel:"strict"`（在 `oink-main/oink-main/assets/third_party/mermaid/mermaid.min.js` 中实测可搜到）。站点若要改任何 Mermaid 参数，走 `params.mermaid`：运行时把 `.Site.Params.mermaid` 注入 `PARAMS`，`norm()` 按 Mermaid defaultConfig 的大小写键名匹配小写化的 params 键。站点模板未配置该项。

## 3. outputs 与额外产物

主题在 `oink-main/oink-main/hugo.yaml` 第 250-289 行注册输出格式：`BookManifest`（book.json）、`LLMS`（llms.txt）、`LLMSFULL`（llms-full.txt，按顶级 section 全文打包，主题不默认开）、`NAVJSON`（navigation.json，机器可读导航树，schema 在 `oink-main/oink-main/schema/nav.v1.schema.json`）、`print`（`path: _print`、`baseName: index`）。每页 `.md` 由 Hugo 内置 markdown 输出 + 主题模板 `oink-main/oink-main/layouts/all.md` 产出，正文渲染共用 `oink-main/oink-main/layouts/_partials/content/markdown-document.md`（all.md 头注：LLMSFULL 也复用这一份渲染器）。RSS 在 `oink-main/oink-main/layouts/_default/rss.xml`，LLMS 首页模板 `oink-main/oink-main/layouts/index.llms.txt`。

站点模板 `assets/templates/hugo.yaml` 的启用组合与产物对应关系（产物计数以真实构建为准）：

| outputs 声明 | 产物（形态；计数以真实构建为准） |
|--------------|------------------|
| home: HTML, RSS, markdown, LLMS | `public/index.html`、`public/index.xml`、`public/index.md`、`public/llms.txt`（站点+各页 `index.md` 链接清单） |
| page: HTML, markdown | 每篇一个 `index.md`，与 `content/**/*.md` 一一对应 |
| section: HTML, RSS, print, markdown | 每个 section 目录带 `index.xml` 与 `index.md`；整节合并的打印版在 `public/_print/<section 路径>/index.html`，每个 section 一个 |

模板未启用 `LLMSFULL`、`NAVJSON`、`BookManifest`（启用与否看站点 `outputs` 声明；模板与 schema 见第 3 节首段）。

## 4. 离线搜索（Lunr）

- 开关：`params.offline_search`（主题 `oink-main/oink-main/hugo.yaml` 第 15 行默认 `false`，站点 opt-in；站点模板设 `true`）。判定收敛在 `oink-main/oink-main/layouts/_partials/shell/search-enabled.html`：`offline_search` 为真、非 print 格式、且（非 server 或 `offline_search_on_serve` 为真）才挂搜索 UI（第 28-33 行）。
- 索引生成：模板是 `oink-main/oink-main/assets/json/offline-search-index.json`（一个 Hugo 模板），由 `oink-main/oink-main/layouts/_partials/offline-search-index.html` 以 `ExecuteAsTemplate` 物化为 `offline-search-index.<lang>.json`，production 下 `fingerprint "md5"`（第 2-7 行）。production 下两个文件并存：带 md5 指纹的 `offline-search-index.<lang>.<hash>.json` 与未哈希的 `offline-search-index.<lang>.json`；页面 HTML 的 `data-td-index-src` 指向未哈希名（历史项目实测）。
- 索引字段：范围是 kind 为 page/section 且有 RawContent 的页（排除 `search_exclude: true`；首页 kind=home 被过滤，所以索引条数 = content md 数 - 1）。每条字段（`oink-main/oink-main/assets/json/offline-search-index.json` 第 35 行起）：`ref,title,excerpt,categories,tags,headings,description,body,root,section,type,keywords,boost,breadcrumb,icon`。索引深度由 `params.offline_search_index` 控制，取值 `title|heading|summary|content`（模板用默认 content，所以带 `body` 全文）。**1.4.0 实测**：索引模板 2,539 → 3,204 字节，构建产物顶层是数组、每条 doc 带上述字段（在 Silo 站产物里实测 409 条，含 `section`/`headings`/`breadcrumb`）；文件名口径不变（`offline-search-index.zh.<hash>.json` + 未哈希名并存）。
- 前端：`oink-main/oink-main/layouts/_partials/shell/search-dialog.html` 把索引 URL 写进 `data-td-index-src`（第 2、4 行），`oink-main/oink-main/assets/js/command-palette.js` 第 209 行 `fetch(root.dataset.tdIndexSrc)`；建库在 `oink-main/oink-main/assets/js/search-engine.js`（1.4.0 从 5,516 → 11,687 字节：中英混排分词、字面技术标识、整词/短语排序、每页一条结果），运行时三个文件打包为 `js/chunks/local-search.js`。**1.4.0 新增「当前小节筛选」**：`layouts/_partials/search/sections.html`（2,032 B，新文件）收集候选小节，面板标签走 zh 新键 `ui_search_scope`（搜索范围）/`ui_search_scope_all`（全部栏目）/`ui_search_partial`（部分匹配：{matched}/{total} 个关键词）/`ui_search_partial_results`。产物层实测：Silo 站 424 个 html 带「搜索范围」串。lunr 未变：`oink-main/oink-main/assets/js/third_party/lunr.min.js` 29,510 字节，版本 2.3.9（VENDOR.json，1.3.2→1.4.0 字节全等）。
- 体验注记（历史项目实测结论）：MB 级索引首次打开面板要一两秒建库，期间输入会落空，别误判为坏了。

## 5. 侧边栏根选择器与相关 UI 开关

`sidebar_root_for`（front matter，仅对 section 有意义）：`oink-main/oink-main/layouts/_partials/shell/sidebar-root.html` 消费。语义：站点默认根是 `Site.Home`（或 `params.ui.docs_sidebar_root: section` 时的 docs section）；某 section 声明 `sidebar_root_for: self` 后，从当前页向上走 Ancestors，第一个命中者成为侧边栏根（第 8-24 行），即「这个分类自己就是一棵独立侧边栏树的根」。取值只接受 `self|children`，非法值 warnf 跳过。`plan_site.py` 生成的分类 `_index.md` 带：

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

`oink-main/oink-main/layouts/_partials/shell/root-menu-roots.html`：全站侧边栏顶部「根切换下拉」的候选收集器（partialCached）：先收 `Site.Home.Sections`，再收所有 `sidebar_root_for: self` 的 section。**1.3.2 起两个循环都过滤（1.4.0 该文件字节未变，已实测）：两个循环都过滤 `sidebar_root_menu: false`、无 permalink的分隔节（`sidebar_divider`）**（第 8、19 行），1.0.0 时代第二个循环不查 `sidebar_root_menu` 的缺口已由主题原生补上。`oink-main/oink-main/layouts/_partials/shell/root-menu.html` 第 5 行以 `params.ui.sidebar_root_menu` 为总开关；只有 1 个候选时降级为静态链接，多个才渲染下拉。当前根的判定与「当前根不在候选集时补入」由 `root-menu-entries.html` 完成（v1.3.2 新拆出的 partial，含 `current` 返回值）。

**本技能骨架不附带 `layouts/_partials/shell/root-menu-roots.html` 覆盖**：主题自 1.3.2 起已原生补齐 `sidebar_root_menu` 过滤与分隔节处理，旧覆盖反而比主题新版少了 `sidebar_divider`/`RelPermalink` 过滤。新站以主题原生行为为准。

另一条历史记录：旧站曾试图用带中文括号后缀的 `root-menu-entries（侧边栏下拉卡片列表选中置顶效果）.html` 做「当前根置顶」。主题按名字调用的是 `partial "shell/root-menu-entries.html"`，带后缀的文件名注册成另一个模板名，**永远不会被调用**（详见 `references/pitfalls.md` 第 13 条）。1.3.2 起的下拉触发器直接显示当前根（`root-menu.html` 第 24 行起 `$current` 逻辑），置顶需求已由主题原生满足。**技能骨架不附带任何带说明性后缀的 partial。**

`params.ui.*` 各自控制什么（都能被同名 front matter 覆盖，覆盖解析器是 `oink-main/oink-main/layouts/_partials/ui-param.html`：站点 `params.ui.<key>` 对应 front matter `<key>`，可经 cascade 下发到整节）：

| 配置 | 消费处 | 控制什么 |
|------|--------|----------|
| `section_index: cards`（默认 list） | `oink-main/oink-main/layouts/_partials/section-index.html` 第 31-37 行 | section 落地页子页列表形态；cards 模式输出 `.td-content-card` 卡片网格，列数由 `section_index_columns`（默认 2）控制 |
| `sidebar_menu_foldable`（默认 true） | `oink-main/oink-main/layouts/_partials/shell/sidebar.html` 第 9-12 行 → `sidebar-tree-node.html` | 侧边栏节点是否可点击折叠/展开子树 |
| `sidebar_expand_levels`（默认 2，站点模板设 4） | `sidebar.html` 第 13-16 行 → `oink-main/oink-main/layouts/_partials/shell/sidebar-tree.html` 第 30 行 `$ulShow := add $expandLevels 1` | 初始化时默认展开到第几层 |
| `sidebar_icon_policy`（`all|groups|none`，非法值 warn 回退 all） | `oink-main/oink-main/layouts/_partials/shell/sidebar-icon-policy.html` | 侧边栏图标密度；模板用 `groups` = 只显示结构性根与有子节点的行（该文件第 3-4 行注释） |
| `backlinks`（默认 false，站点模板 true） | `oink-main/oink-main/layouts/_partials/backlinks-sources.html` 第 6-10 行 + `oink-main/oink-main/layouts/_partials/shell/toc-aside.html` 第 9、53 行 | 右栏 TOC 下方「链向本页的页面」分组；构建期由 `oink-main/oink-main/layouts/_partials/backlinks-index.html` 从站内 Markdown 链接与 ref/relref 推导，无运行时请求 |

## 6. `relativeURLs: true` 的实际效果

站点模板 `assets/templates/hugo.yaml` 开启（注释：产物可挂任意子路径；file:// 只有文字预览，完整功能走 HTTP）。机制与验证方法（历史项目实测过的证据形态，任何站点都可复验）：

- 深层文章页里 `<img ... src="../../../../picture/Message.png">`（正文源写的是绝对路径 `![...](/picture/Message.png)`，构建时被改写成 N 级回退的相对路径，N=页面深度）；
- 浅层页同理：`data-td-index-src="../../offline-search-index.zh.json"`、`<link href="../../scss/main.css">`。

两个收益：其一，产物可整目录挂到任意子路径的静态服务器而**不必**为子路径改 `baseURL`（`baseURL` 只影响 canonical/RSS/llms.txt 里的绝对链接；`assets/templates/hugo.yaml` 给的是占位值 `https://example.org/`，上线前必须换掉）；其二，深层页面的图片与搜索索引会自动补 `../../`。

**双击 `public/index.html` 的真实边界**（2026-10-25 Edge 156.0.4314.42 实测）：页面能打开、文字可读，但主题给 CSS/JS 写了 `integrity` + `crossorigin="anonymous"`，`file://` 的 origin 是 `null`，浏览器按 CORS 拦截全部样式与脚本；结果是页面无样式、Mermaid 0 个、离线搜索 fetch 直接 `Failed to fetch`。`file://` 只适合看纯文字，完整功能必须走 HTTP（`hugo server` 或 `python -m http.server`）。

## 6.1 顶栏 docs 入口

OINK 1.4.0 的顶栏只渲染 `.Site.Menus.main`，不会自动挂 docs。站点模板 `assets/templates/hugo.yaml` 已写入：

```yaml
menus:
  main:
    - identifier: docs
      name: 文档
      pageRef: /docs
      weight: 1
```

`plan_site.py` 每次生成都会保留该键；重跑计划不会丢。2026-10-25 实测：未加时 `.td-nav-menu-zone` 为空；加上后首页出现「文档」tab（1280px 下 73×36），点击进 `/docs/`，文档页 tab 带 `active`；390px 下缩成图标，无横向溢出。`verify_site.py` 的 `nav` 判据会检查产物里的入口。

## 7. goldmark 三项设置

站点模板 `assets/templates/hugo.yaml` 的 goldmark 段：

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

- `ul.cards`（`oink-main/oink-main/assets/scss/td/_markers.scss` 第 105 行起）：链接列表挂 `{.cards}` 变自适应卡片网格（`grid … minmax(min(100%,15rem),1fr)`）。生成器写出的 `content/docs/_index.md` 用法：`- [标题](/docs/xx/)` 链接列表，末行单独写 `{.cards}`。列表项里「链接是标题，其后文字是描述」（该 scss 第 142-144 行注释）。
- `ol.steps`（同文件第 7 行起）：有序列表挂 `{.steps}` 得带圆形计数标记与竖线的步骤条；`start="N"` 偏移在 2..40 范围内被预编译（第 93 行起）。
- `{{< cards >}}/{{< card >}}` 短代码（`oink-main/oink-main/layouts/_shortcodes/cards.html` 第 7 行输出 `<div class="td-content-cards td-content-cards--auto">`）与 `section_index: cards` 共用同一套卡片样式（`oink-main/oink-main/assets/scss/td/_content-components.scss` 第 322-336 行，注释「Shared by `{{< cards >}}` and the section index」）。
- 数据围栏类（`oink-main/oink-main/layouts/_markup/` 下 `render-codeblock-*.html` 实测存在，10 种与 1.0.0 相同）：`mermaid`、`markmap`、`plantuml`、`echarts`、`infographic`、`math`、`chem`、`filetree`、`gallery`、`checksums`；其中 markmap/plantuml/drawio 需 `params.markmap`/`params.plantuml.enable`/`params.drawio.enable` 显式开启（主题 `oink-main/oink-main/hugo.yaml` 第 29-35 行，plantuml/drawio 还强制要求自备服务 URL）。
- 表格有专用钩子 `oink-main/oink-main/layouts/_markup/render-table.html`（及 print/rss 变体）；标题钩子 `oink-main/oink-main/layouts/_markup/render-heading.html`；图片钩子 `oink-main/oink-main/layouts/_markup/render-image.html`。

**1.3.x 排版增强**（写技术文档时按需用，均为正文级语法）：

- **filetree `wrap` 参数**（1.3.1）：```filetree``` 围栏的允许属性新增 `wrap`（`render-codeblock-filetree.html` 第 4 行 allowed 列表），`wrap=true` 让长注释完整换行（含不换行的长标识符），默认 `wrap=false` 保持紧凑行；非法值 warn 回退 false。文件名、折叠、分隔线、移动端堆叠、Print 行为不变。
- **`.td-table--wide` 宽表**（1.3.1）：表格结尾的属性行写 `{.td-table--wide}`，得到「标识符不折断 + 描述限宽 + 横向滚动」的技术宽表（消费在 `assets/scss/td/_content.scss` 第 199 行）；普通表格、字段列表、静态输出布局不变。上游表格逐行保留时，长参数表用这个最稳。
- **Expo 图片相册**（1.3.0）：front matter `type: expo` 的页面（通常做成 leaf bundle），bundle 内 `images/*`（可用 front matter `expo.images` 改 glob）渲染成 wall/cards/seamless 三种布局（`expo.mode`，tile 尺寸 `expo.size` 160-360），带原图查看器（拖拽/WASD 平移、QE/HL 前后张、JK 缩放、R 重置、F 扩展）。站点级默认在 `params.ui.expo`。相册与元数据保留在 Print/Markdown/LLMSFULL/RSS 输出里。
- **视觉预设**（1.2.0，非正文语法但影响观感）：`params.ui.preset: paper`（默认暖纸面）/`slate`（1.1 及以前的技术风）；实验项 `ink`（黑白红）/`terminal`（等宽琥珀）需显式点名。字体本地 IBM Plex Sans，无额外字体文件下载。

**外观一键切换（Appearance 菜单，1.2.0+）**：读者可在最终页面上切换视觉预设与明暗模式，即时生效、不刷新、跨页记住。实现链：`layouts/_partials/shell/appearance-menu.html`（面板，导航栏/页脚/移动端抽屉三处入口）+ `assets/js/appearance.js`（改 `<html data-td-preset>` 换肤、写 `localStorage['td-preset']`、storage 事件跨标签页同步；明暗由 `dark-mode.js` 独立管理）+ `layouts/_partials/head.html` 第 42-66 行内联脚本（首帧渲染前应用存储的预设，无闪烁；非法存储值按白名单清除）。选回站点默认预设会删存储键，站点日后改默认能到达读者；存储被禁用时面板提示「仅本页生效」；无 JS 则面板不渲染、站点默认观感照常。**门控**：面板的渲染条件是 `dark_mode.showMenu` 或 `preset.menu` 二者其一（`preset.menu` = `preset_menu` 提供的选项多于 1 个，`preset-config.html` 第 70 行）。主题默认 `preset_menu: false`——单观感站没有 Style 组；`preset_menu: true` 给 Paper+Slate+站点默认；`preset_menu: [paper, slate, ink, terminal]` 全开放（列表必须含站点默认 `preset`，缺了 WARN 自动补）。站点模板 `dark_mode: true` 已默认开明暗切换，`preset_menu: [paper, slate, ink, terminal]` 也已写成实值（4 套默认全开）。2026-10-25 浏览器实测：点击导航栏 Appearance 触发器后面板打开，4 个预设都在；切到 Slate 后 `<html data-td-preset="slate">` 且 `localStorage['td-preset']='slate'`，切回 Paper 后存储键被删除。

**版本对照**（同一份站点配置，只换主题副本，Hugo v0.168.0 Extended；1.4.0 为本技能当前基线并当轮复验，1.3.2/1.0.0 为历史数据）：

| 主题副本 | `hugo build` | 产物 `<html>` | 预设菜单 |
|---|---|---|---|
| **1.4.0（1,292 文件 / 27,213,292 字节 / `min_version 0.168.0`）** | **通过**，骨架站 Pages 51 / Static files 34 / 1292 ms；`verify --mode skeleton` → FAIL=0 MANUAL=2 PASS=7 SKIP=2；**Static files 没涨**——PlantUML/表格抽屉资产只在使用它们的页面输出（实测未启用页面 grep = 0） | 带 `data-td-preset="paper"`（与 1.3.2 同形）；产物文件口径未变（`offline-search-index.zh.<hash>.json`、`llms.txt`、`_print/` 全在） | 四个名字仍全在（`preset-config.html` 字节未变）；`run.cmd` 实跑 Built in 634 ms + http=200 |
| 1.3.2（1,273 文件 / `min_version 0.166.0`） | 通过，骨架站 Pages 51 / Static 34 / 1271 ms；成品样章站 Pages 25 / Static 35 / 1313 ms；Zookeeper 站 Pages 63 / Static 41 / 1590 ms | 带 `data-td-preset="paper" data-td-site-preset="paper"` | 四个名字 paper/slate/ink/terminal 全在；浏览器实测可切换并写 localStorage |
| 1.0.0（1,196 文件 / `min_version 0.160.1`） | **照样通过**，Pages 15 / Static 22 / 1090 ms | 只有 `data-td-typography="technical"`，**无 `data-td-preset`** | **无** |

第二行就是这条约束存在的全部理由：**旧副本 + 正确的 `preset_menu` = 静默失效**，构建零报错，配置层 grep 全绿。所以判据必须落在产物层（读 `public/index.html` 的 `<html>` 属性），只读 `hugo.yaml` 的那一条会假绿。

## 9. 首页数据文件

`data/home/<lang>.yaml`（由 `plan_site.py` 生成）的结构（主题按 `<lang>` 取 `data/home/` 下的语言文件；按 home-data.html 头注，单语站可直接放一份不分语言的 home 数据文件）：

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

- `hugoVersion`：主题 `oink-main/oink-main/hugo.yaml` 第 306-309 行 `module.hugoVersion: { extended: true, min: 0.168.0 }`；`oink-main/oink-main/AGENTS.md` 契约一节写「Use OINK v1.4.0 and Hugo Extended 0.168.0 for maintained consumer sites, development, CI, and release checks」；`oink-main/oink-main/theme.toml` `min_version = "0.168.0"`；`oink-main/oink-main/README.md` 兼容性表与主题 `go.mod`：**Extended 0.168.0 起步**、Go 1.27.3（主题与站点两处 go.mod 同值；离线归档/replace 本地化时不需要 Go 联网，但执行的那个 go.exe 必须真的 ≥ 1.27.3）。站点模板 `assets/templates/hugo.yaml` 复制了同一约束；本技能当前基线实测跑通的组合是 **Hugo v0.168.0 Extended + Go 1.27.3**（1.4.0 骨架站 `Pages 51 / Static files 34 / 1292 ms / 0 ERROR`）。旧的 Go 1.27.2 组合（1.3.2 时代的 `Pages 25 / Static 35` 等读数）在 1.4.0 下会直接失败：Go 会试图下载 go1.27.3 工具链，见 `references/pitfalls.md` 第 26 条。
- 必须 Extended 的依据：主题全部样式经 SCSS 编译——`oink-main/oink-main/layouts/_partials/head-css.html` 第 2-3 行 `resources.Get "scss/main.scss" | toCSS …`（redoc.scss 同理），标准版 Hugo 无 SCSS 编译器，构建直接失败。**纯 LibSass 契约延续**：1.3.1 曾误加 Dart Sass 强依赖、1.3.2 撤销，1.4.0 的 AGENTS.md 继续写「Ordinary consumers must not install Dart Sass or another Sass executable」。
- libsass WARN：上述 `toCSS` 即 Hugo 的 css.Sass（libsass）通道，Hugo v0.153.0 起弃用该别名，构建时打出 `WARN deprecated: css.Sass: libsass was deprecated … Use dartsass instead.`（本技能实测：Hugo 0.168.0 下每次构建都打这一条）。这条 WARN 是主题侧固有提示、非消费站点引入，普通构建的验收判据是 0 个 ERROR。**`--panicOnWarning` 是禁用项**（1.4.0 契约翻转）：AGENTS.md 原文「Do not enable `--panicOnWarning` or `HUGO_PANICONWARNING` in any build, checker, preview, or CI job. … warnings do not change Hugo's exit status.」旧口径「严格闸门用 0.166.0」作废——0.166.0 现在连主题的 `min_version` 都不满足。
- Hugo 0.168.0 之外的新版本：主题 README 明说「Future Hugo releases that remove LibSass require a separate compatibility decision」——LibSass 被移除的 Hugo 版本不在支持范围，别随手升级工具链。

## 11. 1.4.0 作者侧新增语法（本节全部从主题源码核到，未跑浏览器的标在最末）

**PlantUML 本地渲染**——开关是 `params.plantuml.enable`（主题 `oink-main/oink-main/hugo.yaml` 第 33-34 行默认 `false`；注意在 `params` 顶层，与 `markmap`、`drawio` 同级，**不在 `params.ui` 下**）。主题注释：「PlantUML renders locally unless `svg_image_url` is set; only Draw.io requires a server URL.」所以开 `enable: true` 就够了，引擎是 vendored 的 `@plantuml/core` 1.2026.9 + Viz.js 3.24.0，零 Java/Graphviz/npm。装载条件：`scripts.html` 第 184 行 `if or $hasMermaid (and $hasPlantuml (not $plantumlServer))` → 才追加 `js/chunks/diagram.js`；`layouts/_partials/scripts/plantuml.html`（1,082 B，新文件）负责按需带引擎。**未实测**：启用后的真实渲染、SVG 下载、失败回退。`audit_content.py` 的 `NO_MERMAID` 仍只认 ```` ```mermaid ````，原因见 SKILL.md 未确证项——解析台覆盖不到 plantuml，放宽就是假绿。

**表格阅读两把标记**（goldmark 块属性行，**写在表格之后并紧贴**）：

```markdown
| 项 | 值 |
|---|---|
{#迁移对照表 .wide caption="技术表格排布"}
```

位置是 2026-10-29 用三变体探针实测的：属性行放**表格上方**时 goldmark 不把它绑到这张表（产物里那张 `<table>` 既无 id 也无类），放**表格下方紧贴**才生效——而且放错位置**不会告警**，属于典型的静默失效。核对要看产物：`.wide` 渲染成 `<table class="wide td-table--wide">`，`.expand` 渲染成 `<table class="expand">` 外加 `<div class="td-table-frame">` 与页内一个 `data-td-table-reader` 抽屉。

- `.wide`：技术表格排布标记，与既有 `td-table--wide` 兼容（`content/table-render.html` 第 159 行：有 `.wide` 且没写 `td-table--wide` 时自动补）。
- **id 字符集是硬约束**：主题 `layouts/_partials/content/attributes.html` 只接受匹配 `[A-Za-z][A-Za-z0-9_.:-]*` 的 id，中文 id 会被丢掉并打 WARN（`shortcode "table": id must match …; got "参数迁移对照表" …; dropping it`）。类与 `caption=` 不受影响，但**锚点直达会失效**——中文文档站要给表起锚点时必须用 ASCII id。
- 两把标记可叠加：`{#wide-plus-expand .wide .expand}` 实测渲染成 `<table id="wide-plus-expand" class="wide expand td-table--wide">`，每张表各得一个 `td-table-frame`，页内抽屉 `data-td-table-reader` 只有一个（共享）。
- `.expand`：桌面 hover/focus 出现角上「展开表格」按钮、触屏常显，点开是原生 `<dialog>`（`layouts/_partials/content/table-reader.html` + `assets/js/table-reader.js`），保原文/字号/链接/选区，关闭还原阅读位置与焦点。与 `.fields` **互斥**（第 26-29 行 `warnf "table: .fields cannot be combined with .expand"`，丢 `.expand` 留表）。no-JS、markdown/rss/print 输出仍保留完整内联表；打印会先把打开的表还原。
- 不标记时零开销：实测 Silo 站首页 grep `td-table-reader` = 0。

**命令条 `.td-code-command`**（写在围栏属性里，单行命令专用）：

````markdown
```bash {.td-code-command}
mc cp --recursive backup/ myalias/bucket/
```
````

要求「单行 + 无行号 + 不折叠」，否则 `code/normalize.html` 第 218-222 行 `warnf … using the regular block` 并剥掉该类；渲染后若仍带 `ln|lnt|lntable`，`code/render.html` 第 5-7 行再兜一次。主题只警告并退回常规块，**不改源文本**。

**shortcode 变体**：`{{< cards variant="list" >}}`（分隔线卡片列表）与 `{{< steps variant="compact" >}}`（紧凑步骤）。两者 `allowed` 参数只有 `variant`，值不对就 `warnf` 并退回默认形态（`layouts/_shortcodes/cards.html` 第 1-8 行、`steps.html` 同构）。

内层写法两条不一样，弄错其中一条会让**构建直接失败**：

- `cards` 有子 shortcode：`{{< card title="…" >}}`（`_shortcodes/card.html` 存在），产物容器类 `td-content-cards td-content-cards--auto td-cards-list`。
- `steps` **没有** `step` 子 shortcode：条目就是「一个三级标题算一步」，`{{< step title="…" >}}` 会报 `failed to extract shortcode: template for shortcode "step" not found`（本技能示例站实测踩过）。产物容器类 `td-steps td-max-width-on-larger-screens td-steps-compact`。

**博客画廊索引（第四种 index 形态）**：`params.ui.blog_index: gallery`（第 88-93 行注释已含 gallery），配 `params.ui.blog_gallery.mode: wall|cards|seamless` 与 `blog_gallery.size: 160..360`（第 106-108 行）；读者偏好独立于 Expo 相册，实现是 `assets/js/blog-gallery.js`（5,566 B）+ `assets/scss/td/shell/_blog-gallery.scss`（3,120 B）+ `layouts/_partials/shell/blog-gallery{,-config,-item}.html`。`blog_index_toggle: true` 时读者可在 list/cards/table/gallery 四态间切换。

## 建站必开的主题开关清单

| 配置项 | 建议值 | 不开会怎样 |
|--------|--------|------------|
| `markup.goldmark.renderer.unsafe` | true | 主题各 render hook 的 HTML 与正文内嵌 HTML 被转义为字面文本 |
| `markup.goldmark.parser.attribute.block` | true | `{.cards}`/`{.steps}`/`{icon=}` 等块级属性失效并露出字面字符串 |
| `markup.goldmark.parser.wrapStandAloneImageWithinParagraph` | false | 独占行图片被包进 `<p>`，figure/caption 渲染退化 |
| `markup.highlight.noClasses` | false | 代码高亮内联色，不跟明暗色板（配合主题 `params.highlight_classes`） |
| `relativeURLs` | true | 整目录挂子路径不必改 baseURL；file:// 只有无样式文字，完整功能要 HTTP |
| `params.offline_search` | true | 没有站内搜索；`offline_search_on_serve` 控制 `hugo server` 下是否也建索引 |
| `outputs.home` 含 `markdown` 与 `LLMS` | 按需 | 没有 `/index.md` 与 `/llms.txt` 的机器可读面 |
| `outputs.section` 含 `print` | 按需 | 没有 `_print/` 整节合并打印页 |
| 每篇文章 front matter `title/description/weight` | 必填 | description 缺失会让搜索摘要与卡片描述变空 |
| section `_index.md` 的 `sidebar_root_for: self`（+按需 `sidebar_root_link_self: true`、`icon`、`cascade`） | 按站的分类树定 | 侧边栏不以此为根，全站一棵大树 |
| `params.ui.section_index: cards` | 按需 | section 落地页退回纵向列表 |
| `params.ui.sidebar_expand_levels` / `sidebar_menu_foldable` / `sidebar_icon_policy: groups` | 按需 | 默认只展开 2 层、图标全显 |
| `params.ui.backlinks` | 按需 | 右栏无反向链接组 |
| `params.ui.dark_mode` | 按需 | 无明暗切换 |
| `params.ui.preset` | `paper`（计划生成器写成实值） | 站点默认观感；漏写回退主题默认 paper |
| `params.ui.preset_menu` | `[paper, slate, ink, terminal]`（**计划生成器默认，4 套全开**） | 写成 `false` 或注释 = 只有单一视觉预设，读者不能自选外观（`dark_mode: true` 只带明暗切换）。**注意：配在 OINK <1.2 的主题副本上完全不生效且构建不报错**——判据看产物 `public/index.html` 的 `<html data-td-preset=…>`，对照实测见第 8 节 |

## 未在主题副本中找到、需实测的项

- `params.mermaid.securityLevel` 等自定义注入：机制在（`oink-main/oink-main/assets/js/mermaid.js` 的 PARAMS/norm），但主题与站点模板均未写任何实例配置；实际传参大小写行为需自建一个 `params.mermaid` 验证。
- `LLMSFULL`、`NAVJSON`、`BookManifest` 三个输出的真实产物：本模板未启用，`public/` 里没有对应文件；只有模板（`oink-main/oink-main/layouts/list.llmsfull.txt`、`oink-main/oink-main/layouts/index.navjson.json`、`oink-main/oink-main/layouts/book/list.bookmanifest.json`）与 `oink-main/oink-main/schema/nav.v1.schema.json` 可读，渲染效果需实测。
- `print` 输出对 mermaid/echarts 围栏的静态分支呈现（`_print/` 里应看到源码块）：本次只验证了构建与 `_print/` 产物存在，未逐页核对渲染质量。
- expo 相册的浏览器端交互（原图查看器手势、键盘流、记忆布局）：实现文件俱在（`assets/js/expo.js`），本技能未生成 expo 页面，效果需实测。
- ink / terminal 两个实验预设的**实际观感与可读性**：机制层已实测（4 套全开，产物里四个预设名都在，浏览器可切换），但没有逐页人眼核对过正文/代码块/表格在这两套配色下的观感，也没跑上游 `bin/check-presets.py`。默认观感仍是 paper。

## 本技能实测记录（2026-10-25）

| 项 | 实测输出 |
|----|----------|
| 骨架站构建（示例计划，含顶栏菜单） | `Pages 51 / Static files 34 / Total in 1271 ms / 0 ERROR`，仅 libsass WARN |
| 成品样章站构建 | `Pages 25 / Static files 35 / Total in 1313 ms / 0 ERROR`，仅 libsass WARN |
| Zookeeper 成品站构建 | `Pages 63 / Static files 41 / Total in 1590 ms / 0 ERROR`，仅 libsass WARN |
| 产物面 | `public/llms.txt`、`public/offline-search-index.zh.<md5>.json`、`public/_print/**`、`public/index.md` 均存在 |
| 顶栏 docs 入口 | 首页 `td-nav-menu-zone` 出现「文档」tab（1280px 73×36），点击进 `/docs/`，文档页带 `active`；`verify_site` 的 `nav` PASS |
| 预设 | `public/index.html` 带 `data-td-preset="paper"`；面板 4 个预设可切换，Slate 写入 localStorage，切回 Paper 删键 |
| 离线搜索 | 打开面板输入「安装」，返回 3 条命中（文章/板块/分类）；Zookeeper 站为 4 条 |
| 响应式 | CDP `Emulation.setDeviceMetricsOverride` 390×844：`innerWidth=390`、`scrollWidth=390`、无横向溢出；1440×1200 首页/文章页截图正常 |
| Mermaid | 540 行样章 2 张图：解析台 `TOTAL=2 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`；Zookeeper 站为 `TOTAL=18 REAL_FAIL=0` |
| 统一验收 | 骨架站 `FAIL=0 MANUAL=2 PASS=7 SKIP=1`；Zookeeper 成品站 `FAIL=0 MANUAL=2 PASS=8 SKIP=0` |
| `file://` 直开 | 只有无样式文字：CSS/JS 被 CORS 拦截，Mermaid 0 个、搜索 `Failed to fetch`；完整功能走 HTTP |
