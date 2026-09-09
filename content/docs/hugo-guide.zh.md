---
title: "Hugo 技术文档"

weight: 999
type: docs
icon: fa-solid fa-book-open
---

[//]: # (# Hugo 技术文档)

> 本文档面向 OINK Starter 站点的维护者，涵盖 Hugo 核心概念、项目配置、内容编写与日常构建。

---

## Hugo 简介

**Hugo** 是一个用 Go 编写的静态站点生成器。本项目通过 Hugo Module 加载 **OINK** 主题，将 `content/` 下的 Markdown 文件转化为完整的静态 HTML 站点。

```
content/*.md  →  Hugo + OINK 主题  →  public/*.html
     ↑                ↑
  Markdown 内容     主题模板 + SCSS 样式
```

### 常用命令

| 命令 | 作用 |
|------|------|
| `hugo server -D` | 启动本地开发服务器（支持热重载，包含草稿） |
| `hugo` | 构建生产站点到 `public/` |
| `hugo --minify` | 构建并压缩输出文件 |
| `hugo --gc` | 构建并清理无用缓存 |
| `hugo mod get -u` | 更新主题模块依赖 |

---

## 项目结构

```
oink-starter/
├── hugo.yaml               # 唯一的站点配置文件（语言、参数、模块全部在此）
├── go.mod / go.sum          # Go 模块依赖（锁定 OINK 主题版本）
├── package.json             # npm 脚本（dev / build / hugo）
│
├── content/                 # 内容目录（所有 Markdown 文件）
│   ├── _index.zh.md         # 首页
│   ├── docs/                # 文档章节（type: docs）
│   │   ├── _index.zh.md     # 文档概览（section 首页）
│   │   ├── administration/  # 管理
│   │   ├── compatibility/   # 兼容性
│   │   ├── developers/      # 开发
│   │   ├── integrations/    # 集成
│   │   ├── operations/      # 运维
│   │   ├── reference/       # 参考
│   │   ├── glossary.zh.md   # 术语表
│   │   └── hugo-guide.zh.md # 本文
│   ├── blog/                # 博客（type: blog）
│   │   ├── post/            # 文章
│   │   ├── design/          # 设计记录
│   │   └── release/         # 版本公告
│   └── book/                # 书籍（type: book）
│       ├── 01-preview.zh.md # 章节文件
│       └── ...
│
├── data/home/               # 首页数据文件
│   ├── zh.yaml              # 中文首页区块内容
│   ├── en.yaml              # 英文首页区块内容
│   └── fr.yaml              # 法文首页区块内容
│
├── assets/icons/            # 品牌资源
│   └── logo.svg             # 站点 Logo
├── static/                  # 静态资源（原样发布到 public/）
│   └── favicon.svg          # 站点图标
├── i18n/                    # 国际化翻译文件
├── examples/                # 配置示例
│   ├── hugo.bilingual.yaml  # 中英双语配置示例
│   └── hugo.single.yaml     # 单语言配置示例
│
├── scripts/                 # 维护脚本
│   ├── remove-en-docs.ps1   # 移除英文文档
│   └── remove-fr-docs.ps1   # 移除法文文档
│
└── public/                  # 构建输出（勿手动编辑）
```

> **重要**：项目中不存在 `config/` 目录、`languages.toml`、`menus.toml` 或 `params.toml`。所有配置集中在根目录的 `hugo.yaml` 一个文件中。

---

## 站点配置

### hugo.yaml 总览

本项目只有一个配置文件 `hugo.yaml`，包含全部站点设置：

```yaml
title: &siteTitle Project Name       # 站点标题（YAML 锚点，各语言共享）
baseURL: https://example.org/         # 生产环境 URL
defaultContentLanguage: zh            # 默认语言为中文
enableGitInfo: true                   # 使用 Git 提交信息作为最后修改时间
enableRobotsTXT: true
enableEmoji: true
timeZone: UTC

languages:
  zh:
    label: 简体中文
    locale: zh-CN
    weight: 2
    title: *siteTitle
    hasCJKLanguage: true
    params:
      description: 你的项目文档、动态与指南。

params:
  offline_search: true                # 启用 Lunr 离线搜索
  ui:
    dark_mode: true                   # 导航栏显示明暗切换按钮
    section_index: cards              # 章节首页使用卡片布局
    blog_index: cards                 # 博客首页使用卡片布局
    sidebar_menu_foldable: true       # 侧边栏可折叠
    sidebar_icon_policy: groups       # 图标按分组显示
    backlinks: true                   # 启用反向链接

module:
  imports:
    - path: github.com/pgsty/oink     # OINK 主题（Hugo Module）
  hugoVersion:
    extended: true                    # 需要 Extended 版（支持 SCSS）
    min: 0.160.1
```

### 关键配置项说明

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `defaultContentLanguage` | `zh` | 默认语言为中文 |
| `hasCJKLanguage` | `true` | 启用中日韩语言支持（影响字数统计和段落分割） |
| `enableGitInfo` | `true` | 从 Git 历史读取最后修改时间 |
| `markup.goldmark.renderer.unsafe` | `true` | 允许 Markdown 中嵌入原始 HTML |
| `markup.goldmark.parser.attribute.block` | `true` | 支持块级属性语法（如 `{#custom-id}`） |
| `markup.highlight.noClasses` | `false` | 代码高亮使用内联样式而非 CSS 类 |

### 语言配置

当前仅启用中文。英文和法文已注释但保留在配置中：

```yaml
languages:
#  en:
#    label: English
#    ...
  zh:
    label: 简体中文
    ...
#  fr:
#    label: Français
#    ...
```

如需启用英文，取消 `en:` 块的注释即可。启用的语言会出现在导航栏的语言切换器中。

### UI 参数

`params.ui` 控制界面的交互行为：

| 参数 | 类型 | 说明 |
|------|------|------|
| `dark_mode` | bool | `true` 时导航栏显示明暗模式切换按钮 |
| `section_index` | string | 章节首页布局：`cards`（卡片）或默认列表 |
| `blog_index` | string | 博客首页布局：`cards`（卡片）或默认列表 |
| `sidebar_menu_foldable` | bool | 侧边栏菜单是否可折叠展开 |
| `sidebar_icon_policy` | string | 侧边栏图标策略：`groups` / `all` / `none` |
| `backlinks` | bool | 是否显示反向链接 |
| `theme_color` | string | 章节强调色（十六进制），影响侧边栏选中态、hover 效果等 |
| `typography` | string | 字体预设：`technical`（默认）或 `system`（平台字体） |
| `page_width` | string | 页面宽度：`normal` / `wide` / `full` |

---

## 内容类型

项目包含三种内容类型，各自有独立的 front matter 约定和展示方式：

### Docs — 技术文档

用于组织结构化的技术文档，按章节（section）分层。

```
content/docs/
├── _index.zh.md           # section 首页，设置 cascade 级联
├── administration/        # 管理章节
├── operations/            # 运维章节
├── reference/             # 参考手册
└── glossary.zh.md         # 独立页面（术语表）
```

**Section 首页 front matter**（`_index.zh.md`）：

```yaml
---
title: "文档"
linkTitle: "文档"              # 侧边栏中显示的短标题
description: "项目技术文档"
type: docs                     # 标记为文档类型
icon: fa-solid fa-book         # 侧边栏图标
cascade:                       # 级联到所有子页面
    type: docs                 # 子页面自动继承文档类型
    footer_style: slim         # 子页面使用精简页脚
---
```

**普通页面 front matter**：

```yaml
---
title: "页面标题"
weight: 10                     # 排序权重（越小越靠前）
type: docs                     # 继承自 cascade，通常无需重复
---
```

### Blog — 博客

用于发布文章、设计记录与版本公告。

```
content/blog/
├── _index.zh.md               # 博客首页
├── post/                      # 普通文章
│   └── welcome.zh.md
├── design/                    # 设计记录
│   └── content-model.zh.md
└── release/                   # 版本公告
    └── 0.1.0.zh.md
```

**博客文章 front matter**：

```yaml
---
title: 文章标题
date: 2026-01-15               # 发布日期
description: 文章摘要
tags: [社区, 快速上手]          # 标签
---
```

### Book — 书籍

提供连续的阅读体验，适合教程和指南。

```
content/book/
├── _index.zh.md               # 书籍首页
├── 01-preview.zh.md           # 第 1 章
├── 02-structure.zh.md         # 第 2 章
├── 03-customize.zh.md         # 第 3 章
└── 04-deploy.zh.md            # 第 4 章
```

**书籍章节 front matter**：

```yaml
---
title: 预览站点
description: 章节描述
book_kind: chapter             # 标记为章节
book_number: 1                 # 章节编号
weight: 10                     # 排序权重
---
```

---

## 多语言文件命名约定

本项目使用 OINK 主题的多语言文件命名规则。所有语言的文件放在同一目录下，通过后缀区分：

| 文件名 | 语言 | 访问路径 |
|--------|------|----------|
| `welcome.md` | 默认语言（zh） | `/zh/blog/post/welcome/` |
| `welcome.zh.md` | 中文（显式标记） | `/zh/blog/post/welcome/` |
| `welcome.fr.md` | 法文 | `/fr/blog/post/welcome/` |
| `_index.md` | 默认语言 section 首页 | `/zh/docs/` |
| `_index.zh.md` | 中文 section 首页 | `/zh/docs/` |

**规则**：
- 默认语言（`zh`）的文件可以不带后缀（`page.md`），也可以显式标记（`page.zh.md`）
- 非默认语言文件必须带语言后缀（`page.fr.md`）
- Section 首页统一使用 `_index` 或 `_index.LANG.md`
- 两种语言的文件放在同一目录下

---

## Front Matter 通用字段

所有类型的内容文件共享以下 front matter 字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题（必填） |
| `linkTitle` | string | 侧边栏和导航中显示的短标题 |
| `description` | string | 页面描述，用于 SEO 和卡片摘要 |
| `weight` | int | 排序权重，越小越靠前 |
| `type` | string | 内容类型（`docs` / `blog` / `book`），通常由 cascade 继承 |
| `icon` | string | Font Awesome 图标类名 |
| `date` | date | 发布日期（博客文章常用） |
| `tags` | []string | 标签列表（博客文章常用） |
| `draft` | bool | 标记为草稿，仅 `hugo server -D` 时渲染 |
| `cascade` | map | 级联配置，设置在 section 首页上，自动继承到所有子页面 |
| `upstream_link` | string | 上游文档链接（已废弃，保留为空字符串） |

### 级联（cascade）示例

在 section 首页的 `cascade` 中设置的字段，会自动应用到该 section 下的所有子页面：

```yaml
---
title: "文档"
type: docs
cascade:
    type: docs              # 所有子页面自动标记为文档类型
    footer_style: slim      # 所有子页面使用精简页脚
    reading_time: true      # 所有子页面显示阅读时间
---
```

---

## Markdown 编写指南

### Goldmark 配置

项目在 `hugo.yaml` 中启用了以下 Markdown 扩展：

```yaml
markup:
  goldmark:
    renderer:
      unsafe: true                  # 允许原始 HTML
    parser:
      attribute:
        block: true                 # 支持块级属性
      wrapStandAloneImageWithinParagraph: false
  highlight:
    noClasses: false                # 代码高亮使用内联样式
```

### 自定义标题锚点

使用块级属性语法为标题指定锚点 ID：

```markdown
## 快速开始 {#quick-start}

## 前置条件 {#prerequisites}
```

### Callout 提示框

使用 GitHub 风格块引用语法：

```markdown
> [!NOTE]
> 普通提示信息。

> [!WARNING]
> 警告信息。

> [!TIP]
> 技巧提示。

> [!IMPORTANT]
> 重要信息。
```

### 内部链接

使用绝对路径链接站内页面，路径不含语言前缀：

```markdown
[迁移指南](/docs/compatibility/migration/)
[术语表](/docs/glossary/)
```

Hugo 会根据当前语言自动解析到对应语言的页面。

---

## 首页配置

首页内容由 `data/home/<language>.yaml` 数据文件驱动，支持以下区块：

```yaml
# data/home/zh.yaml
sections: [hero, cards, cta]      # 区块顺序

hero:                              # 主视觉区域
  align: center
  eyebrow: 开源项目起步模板        # 小标签文字
  title_lines:                     # 主标题（可多行）
    - words: [{ text: 你的项目， }]
    - words: [{ text: 清楚讲明白。 }]
  lead: 一个可以直接修改的项目首页  # 副标题
  actions:                         # 按钮组
    - { label: 阅读文档, url: docs/, icon: fa-solid fa-book, style: primary }
    - { label: 跟随教程, url: book/, icon: fa-solid fa-arrow-right, style: ghost }

cards:                             # 卡片区块
  title: 每类内容都有自己的位置
  columns: 3
  items:
    - title: 博客
      desc: 发布文章与设计记录。
      icon: fa-solid fa-pen-nib
      url: blog/

cta:                               # 行动号召
  title: 把这个模板变成你的站点。
  label: 开始使用
  url: docs/get-started/
```

---

## 构建与部署

### npm 脚本

`package.json` 定义了四个脚本：

| 脚本 | 命令 | 等价于 |
|------|------|--------|
| `npm run dev` | 开发服务器 | `hugo server -D` |
| `npm run hugo` | 标准构建 | `hugo` |
| `npm run build` | 生产构建 | `hugo --minify` |
| `npm run stop` | 停止开发服务器 | 终止占用 1313 端口的进程 |

### 构建流程

```
读取 hugo.yaml 配置
    ↓
加载 OINK 主题模块（go.mod → github.com/pgsty/oink）
    ↓
解析 content/ 下的 Markdown 文件（front matter + 正文）
    ↓
渲染模板（主题 layouts/ + 项目覆盖）
    ↓
编译 SCSS 样式（Dart Sass）
    ↓
复制 static/ 静态资源
    ↓
输出到 public/
```

### 开发服务器 vs 生产构建

| 特性 | `hugo server -D` | `hugo --minify` |
|------|-------------------|-----------------|
| 用途 | 本地开发调试 | 生产环境部署 |
| 输出 | 内存（默认） | `public/` 目录（压缩） |
| 文件监听 | 自动监听变更并热重载 | 无 |
| 草稿渲染 | 是（`-D` 参数） | 否 |
| 构建速度 | 首次完整，后续增量（< 100ms） | 完整构建 + 压缩 |

### 环境要求

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| Hugo Extended | >= 0.160.1 | 站点生成（必须 Extended 版以支持 SCSS） |
| Go | >= 1.27.0 | Hugo 模块系统 |
| Node.js | >= 18 | PostCSS / Autoprefixer |

---

## 主题定制

### SCSS 覆盖

在 `assets/scss/` 下创建以下文件覆盖主题样式（当前项目尚未创建这些文件）：

| 文件 | 用途 | 加载时机 |
|------|------|----------|
| `_variables_project.scss` | 覆盖 Sass 变量（如 `$primary`） | Bootstrap 之前 |
| `_variables_project_after_bs.scss` | 依赖 Bootstrap 已定义变量 | Bootstrap 之后 |
| `_styles_project.scss` | 自定义 CSS 和 CSS 变量 | 主题样式之后 |

```scss
// assets/scss/_variables_project.scss — 修改主题色
$primary: #315f8f;
$secondary: #b4762e;
```

```scss
// assets/scss/_styles_project.scss — 自定义品牌色
:root {
  --td-brand-copper: #a66722;
  --td-brand-mark-from: #1d588c;
  --td-brand-mark-to: #a66722;
}
```

### 字体配置

通过 `hugo.yaml` 直接配置字体（无需 SCSS）：

```yaml
params:
  ui:
    fonts:
      ui: "'Source Han Sans SC', 'PingFang SC', sans-serif"
      code: "'Sarasa Mono SC', 'Noto Sans Mono CJK SC', monospace"
```

### 局部钩子

`layouts/_partials/hooks/head-end.html` 可在 `<head>` 末尾注入自定义内容（如分析脚本、Meta 标签）。

> **注意**：不要直接编辑主题模块内的任何文件。`hugo mod` 升级会覆盖整个主题目录。所有自定义应通过项目级的 SCSS 文件、layout 覆盖或 `hugo.yaml` 参数完成。

---

## 故障排查

### Sass 编译失败

```
TOCSS-DART: failed to transform "/scss/main.scss"
```

**原因**：Dart Sass 运行时缺失。

**解决**：确认 Hugo Extended 已正确安装。`hugo version` 输出中必须包含 `extended`。

### Go 版本不匹配

```
module requires go >= 1.27.0 (running go 1.24.0)
```

**原因**：OINK 主题要求 Go 1.27.0+。

**解决**：升级 Go 版本到 1.27.0 或更高。

### 页面不渲染

**检查清单**：
1. 文件是否在 `content/` 目录下
2. Front matter 是否完整（至少包含 `title`）
3. Section 首页是否设置了 `cascade: type: docs`（或 `blog` / `book`）
4. 文件名是否符合多语言命名约定（`.md` / `.zh.md` / `.fr.md`）
5. 语言是否在 `hugo.yaml` 的 `languages` 中声明（注释掉的语言不会渲染对应文件）

### 直接打开 index.html 显示异常

Hugo 生成的 `public/` 目录不能通过 `file://` 协议直接打开，因为资源路径基于 HTTP 协议解析。

**解决**：始终使用 `hugo server` 或任意 HTTP 服务器访问构建产物：

```powershell
# 开发模式
hugo server -D

# 预览构建产物
python -m http.server 8080 --directory public
```
