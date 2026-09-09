# OINK Starter 零基础搭建教程

> 基于本项目模板，10 分钟搭建你自己的文档站

## 前言

### 本教程适合谁

- 从未接触过 Hugo 或静态站点生成器的开发者
- 想快速搭建技术文档、产品手册、知识库的团队或个人
- 有一定 Markdown 基础，但不熟悉前端工程化的用户

### 为什么选择 OINK Starter 作为模板

本项目已经帮你配置好了所有"基础设施"：

| 已内置能力 | 说明 |
|:----------:|------|
| Hugo Extended | 基于 Go 的极速静态站点生成器，构建通常几秒内完成 |
| OINK 主题 | 导航栏 + 自动侧边栏 + 暗色模式 + 代码高亮 + 离线搜索 |
| 三大内容板块 | Blog（博客）、Docs（文档）、Book（连续指南） |
| 多语言支持 | 默认启用中文，可选开启英文和法文 |
| 首页模板 | Hero 区域 + 特性卡片 + 行动按钮 |
| 部署就绪 | GitHub Pages 和 Cloudflare Pages 工作流开箱即用 |

你只需要关注**内容本身**（写 Markdown），其余的交给模板。

---

## 第 1 章：环境准备

### 1.1 安装 Hugo Extended

本项目需要 **Hugo Extended** 版本（支持 SCSS 样式编译）。

**Windows 用户**：

```bash
# 使用 winget 安装（推荐）
winget install Hugo.Hugo.Extended

# 或使用 Scoop
scoop install hugo-extended
```

**macOS 用户**：

```bash
brew install hugo
```

安装完成后，验证版本：

```bash
hugo version
# 应显示 v0.160.1 或更高版本，且输出中必须包含 "extended"
```

> **重要**：如果 `hugo version` 输出中没有 `extended`，SCSS 编译会失败。请确认安装的是 Extended 版本。

### 1.2 安装 Go

Hugo 通过 Go 模块系统加载 OINK 主题。

**Windows 用户**：前往 https://go.dev/dl/ 下载 Go 1.27 或更高版本的安装包。

**macOS 用户**：

```bash
brew install go
```

验证安装：

```bash
go version
# 应显示 go1.27.0 或更高版本
```

### 1.3 安装 Git

用于从 GitHub 获取项目代码和 Hugo 模块。

- Windows：https://git-scm.com/download/win
- macOS：`brew install git` 或 Xcode Command Line Tools

验证安装：

```bash
git --version
# 应显示 git version 2.x.x
```

### 1.4 安装编辑器

推荐使用 [Visual Studio Code](https://code.visualstudio.com/)（简称 VS Code），免费且对 Markdown 和 YAML 支持优秀。

推荐安装的 VS Code 扩展：
- **Markdown All in One** — Markdown 编辑增强
- **YAML** (Red Hat) — YAML 语法高亮和校验
- **EditorConfig** — 统一代码格式

---

## 第 2 章：获取项目模板

### 2.1 克隆项目

```bash
# 方式一：克隆你自己的仓库（推荐先 Fork 再克隆）
git clone https://github.com/你的用户名/你的仓库.git
cd 你的仓库

# 方式二：直接克隆模板试用
git clone https://github.com/pgsty/oink-starter.git my-docs
cd my-docs
```

### 2.2 首次运行

```bash
hugo server
```

首次运行会自动下载 OINK Hugo 模块（通过 Go），大约需要 30 秒到 2 分钟。看到以下输出表示启动成功：

```
Web Server is available at http://localhost:1313/
```

打开浏览器访问 `http://localhost:1313/`，你就能看到文档站的完整效果。

> **注意**：不需要 `npm install`，不需要 Node.js。Hugo 模块系统会自动处理主题依赖。

### 2.3 构建验证

```bash
hugo
```

看到 `Total in xxx ms` 且无 ERROR 表示构建成功。构建产物在 `public/` 目录下。

---

## 第 3 章：理解项目结构

```text
oink-starter/
│
├── hugo.yaml                  # ★ 唯一的站点配置文件
│
├── content/                   # ★ 内容目录（你的所有文档都放这里）
│   ├── _index.zh.md           # 首页
│   ├── docs/                  # 技术文档
│   │   ├── _index.zh.md       # 文档 section 首页（控制侧边栏根节点）
│   │   ├── administration/    # 文档分组 A
│   │   ├── operations/        # 文档分组 B
│   │   └── reference/         # 文档分组 C
│   ├── blog/                  # 博客
│   │   ├── post/              # 文章
│   │   ├── design/            # 设计记录
│   │   └── release/           # 版本公告
│   └── book/                  # 书籍（连续阅读体验）
│
├── data/home/                 # 首页数据文件
│   └── zh.yaml                # ★ 中文首页区块内容
│
├── assets/icons/logo.svg      # 站点 Logo
├── static/favicon.svg         # 站点图标
├── go.mod                     # Go 模块依赖（锁定 OINK 主题版本）
├── package.json               # npm 脚本（可选）
└── public/                    # 构建输出（勿手动编辑）
```

### 核心文件说明

| 文件 | 作用 | 你需要改吗 |
|------|------|:----------:|
| `hugo.yaml` | 站点配置（标题、URL、语言、UI 参数） | 必须改 |
| `data/home/zh.yaml` | 首页内容（Hero + 卡片 + 行动按钮） | 必须改 |
| `content/docs/` 下的文件 | 文档页面内容 | 必须改 |
| `assets/icons/logo.svg` | 站点 Logo | 按需替换 |
| `static/favicon.svg` | 站点图标 | 按需替换 |
| `go.mod` | 主题依赖版本 | 一般不改 |

### 与其他模板的关键区别

如果你之前用过 VuePress 或其他框架，注意以下区别：

| 对比项 | VuePress | OINK Starter |
|--------|----------|--------------|
| 配置文件 | `docs/.vuepress/config.js` | `hugo.yaml`（一个文件搞定） |
| 侧边栏 | 手动在 config.js 中配置 | **自动生成**（根据文件结构） |
| 依赖安装 | `npm install` | 不需要（Hugo 模块自动处理） |
| 内容目录 | `docs/` | `content/` |
| 导航栏 | 手动配置 | 根据 section 首页的 `menus` 字段自动生成 |

---

## 第 4 章：五步改造法

### 第 1 步：修改站点基本信息

打开 `hugo.yaml`，找到开头的两行：

```yaml
title: &siteTitle Project Name    # ← 改成你的站点名称
baseURL: https://example.org/      # ← 改成你的实际网址
```

**改成你的内容**（以"我的产品文档"为例）：

```yaml
title: &siteTitle 我的产品         # ← 你的站点名称
baseURL: https://my-product.pages.dev/  # ← 你的实际网址
```

> `&siteTitle` 是 YAML 锚点，修改这一处即可同时更新所有语言的站点标题。

### 第 2 步：定制首页

打开 `data/home/zh.yaml`，你会看到三个区块：

```yaml
sections: [hero, cards, cta]

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

cards:                             # 特性卡片
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

**改成你的内容**：

```yaml
sections: [hero, cards, cta]

hero:
  align: center
  eyebrow: 我的产品
  title_lines:
    - words: [{ text: 简单高效的 }]
    - words: [{ text: 解决方案。 }]
  lead: 帮助你快速构建和管理项目。
  actions:
    - { label: 快速开始, url: docs/, icon: fa-solid fa-rocket, style: primary }

cards:
  title: 核心特性
  columns: 3
  items:
    - title: 高性能
      desc: 基于最新技术栈，响应速度极快。
      icon: fa-solid fa-bolt
      url: docs/performance/
    - title: 易集成
      desc: 提供丰富的 SDK，5 分钟完成接入。
      icon: fa-solid fa-puzzle-piece
      url: docs/integration/
    - title: 安全可靠
      desc: 企业级安全机制，数据加密传输。
      icon: fa-solid fa-shield-halved
      url: docs/security/

cta:
  title: 立即开始使用
  label: 查看文档
  url: docs/
```

**各字段说明**：

| 字段 | 说明 |
|------|------|
| `hero.eyebrow` | 主标题上方的小标签 |
| `hero.title_lines` | 主标题行，每行一个 `words` 数组 |
| `hero.lead` | 副标题描述 |
| `hero.actions` | 按钮数组，`style: primary` 为主按钮，`ghost` 为透明按钮 |
| `cards.items` | 特性卡片数组，每个包含 `title`、`desc`、`icon`、`url` |
| `cta` | 底部行动号召区块 |

### 第 3 步：替换文档内容

#### 3.1 清理旧内容

删除 `content/docs/` 下你不需要的目录：

```bash
# Windows PowerShell
Remove-Item -Recurse content\docs\administration
Remove-Item -Recurse content\docs\compatibility
Remove-Item -Recurse content\docs\developers
Remove-Item -Recurse content\docs\integrations
Remove-Item -Recurse content\docs\operations
Remove-Item -Recurse content\docs\reference

# macOS / Linux
rm -rf content/docs/administration content/docs/compatibility \
       content/docs/developers content/docs/integrations \
       content/docs/operations content/docs/reference
```

同时删除不再需要的独立文件：

```bash
# Windows PowerShell
Remove-Item content\docs\glossary.zh.md
Remove-Item content\docs\hugo-guide.zh.md
```

#### 3.2 创建你的文档目录

```bash
mkdir content\docs\guide
```

#### 3.3 编写 section 首页

创建 `content/docs/guide/_index.zh.md`：

```yaml
---
title: 使用指南
linkTitle: 指南
description: 从零开始了解我的产品。
weight: 10
type: docs
icon: fa-solid fa-book
cascade:
  type: docs
---

欢迎使用我的产品！本指南将帮助你快速上手。
```

**关键字段说明**：

| 字段 | 作用 |
|------|------|
| `title` | 页面标题和侧边栏根节点名称 |
| `linkTitle` | 导航栏中显示的短标题（可选） |
| `weight` | 侧边栏中的排序权重（越小越靠前） |
| `type: docs` | 标记为文档类型，启用文档布局 |
| `icon` | 侧边栏图标（Font Awesome 类名） |
| `cascade.type: docs` | **级联到所有子页面**，子页面自动继承文档类型 |

#### 3.4 编写第一个文档页面

创建 `content/docs/guide/introduction.zh.md`：

```yaml
---
title: 产品介绍
description: 了解我的产品的核心功能和特性。
weight: 10
---

## 什么是我的产品

我的产品是一个用于解决 XX 问题的工具。

## 核心特性

- **高性能**：毫秒级响应
- **易集成**：5 分钟完成接入
- **安全可靠**：企业级安全保障

## 下一步

前往 [快速上手](/docs/guide/getting-started/) 开始使用。
```

再创建 `content/docs/guide/getting-started.zh.md`：

```yaml
---
title: 快速上手
description: 安装和基本使用指南。
weight: 20
---

## 安装

```bash
npm install my-product
```

## 基本使用

```js
import { MyProduct } from 'my-product'

const app = new MyProduct()
app.start()
```

## 下一步

前往 [配置指南](/docs/guide/configuration/) 了解更多选项。
```

#### 3.5 文件命名约定

| 文件名 | 说明 |
|--------|------|
| `_index.zh.md` | Section 首页（侧边栏根节点） |
| `introduction.zh.md` | 普通文档页面 |
| `.zh.md` 后缀 | 标记为中文内容 |

> **与其他框架的区别**：在 VuePress 中，每新增一个页面都需要在 `config.js` 的 `sidebar` 中手动添加链接。而在 OINK Starter 中，**新文件会自动出现在侧边栏**，无需任何额外配置。

### 第 4 步：理解自动侧边栏

OINK 主题会根据 `content/` 的目录结构和 front matter 自动生成侧边栏。你不需要手动配置任何导航树。

**侧边栏的生成规则**：

1. Section 首页（`_index.zh.md`）的 `title` 成为侧边栏分组名称
2. `weight` 值控制分组和页面的排列顺序
3. `icon` 字段为分组添加图标
4. 子目录自动嵌套为二级、三级菜单
5. `cascade` 中设置的字段自动继承到所有子页面

**常用 front matter 字段**：

| 字段 | 作用 | 示例 |
|------|------|------|
| `title` | 页面标题 | `"安装指南"` |
| `linkTitle` | 侧边栏短标题 | `"安装"` |
| `weight` | 排序权重 | `10` |
| `icon` | 图标 | `fa-solid fa-rocket` |
| `description` | 页面描述 | `"安装步骤说明"` |
| `draft: true` | 标记为草稿（仅 `hugo server -D` 时显示） | `true` |

### 第 5 步：构建与部署

#### 5.1 本地构建

```bash
# 生产构建（压缩输出）
hugo --minify

# 完整生产构建（清理缓存 + 压缩）
hugo --gc --cleanDestinationDir --minify
```

构建成功后，`public/` 目录下就是完整的静态网站文件。

#### 5.2 部署到 GitHub Pages

1. 在 GitHub 创建仓库（如 `my-docs`）
2. 打开仓库 **Settings → Pages**，选择 **GitHub Actions** 作为来源
3. 推送代码到 `main` 分支

如果项目模板已包含 GitHub Pages 工作流，推送后会自动部署。否则创建工作流文件 `.github/workflows/github-pages.yaml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

permissions:
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.27'
      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: '0.165.0'
          extended: true
      - run: hugo --minify --gc --environment production
      - uses: actions/upload-pages-artifact@v3
        with:
          path: ./public
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

#### 5.3 部署到 Vercel / Cloudflare Pages

**Vercel**：
1. 前往 https://vercel.com ，从 GitHub 导入项目
2. Build Command: `hugo --minify --environment production`
3. Output Directory: `public`
4. 点击 Deploy

**Cloudflare Pages**：
1. 前往 Cloudflare Dashboard → Pages → 创建项目
2. 连接 GitHub 仓库
3. Build Command: `hugo --minify --environment production`
4. Output Directory: `public`
5. 点击 Deploy

---

## 第 5 章：进阶定制

### 自定义样式

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

> **注意**：不要直接编辑主题模块内的任何文件。`hugo mod` 升级会覆盖整个主题目录。

### 自定义字体

通过 `hugo.yaml` 直接配置字体（无需 SCSS）：

```yaml
params:
  ui:
    fonts:
      ui: "'Source Han Sans SC', 'PingFang SC', sans-serif"
      code: "'Sarasa Mono SC', 'Noto Sans Mono CJK SC', monospace"
```

### 暗色模式

```yaml
params:
  ui:
    dark_mode: true    # true = 显示切换按钮，false = 关闭
```

### 离线搜索

```yaml
params:
  offline_search: true  # 启用 Lunr 离线搜索（无需外部服务）
```

### 启用评论（Giscus）

在 `hugo.yaml` 中取消 Giscus 区块的注释并填入你的仓库信息：

```yaml
params:
  comments:
    enable: true
    type: giscus
    giscus:
      repo: 你的用户名/你的仓库
      repoId: R_xxxxxxxxxx
      category: Announcements
      categoryId: DIC_xxxxxxxxxx
      mapping: pathname
      inputPosition: bottom
      theme: auto
      loading: lazy
```

### 启用分析（Google Analytics）

```yaml
services:
  googleAnalytics:
    id: G-XXXXXXXXXX
```

---

## 第 6 章：常见问题

### Q: `hugo version` 输出中没有 extended

**原因**：安装的是 Hugo 标准版，不支持 SCSS 编译。

**解决**：卸载标准版，安装 Extended 版本：

```bash
# Windows
winget uninstall Hugo.Hugo
winget install Hugo.Hugo.Extended

# macOS
brew uninstall hugo
brew install hugo
```

### Q: 新增的页面在侧边栏不显示

**原因**：Section 首页（`_index.zh.md`）缺少 `cascade` 配置，或文件的 `type` 字段不正确。

**解决**：
1. 确认 section 首页包含 `cascade: type: docs`
2. 确认文件放在正确的 section 目录下
3. 确认文件名以 `.zh.md` 结尾（或 `.md`）

### Q: 页面能打开但内容为空

**原因**：Front matter 格式不正确，或文件编码不是 UTF-8。

**解决**：
1. 确认 `---` 分隔符独占一行且成对出现
2. 确认 YAML 缩进使用空格（不是 Tab）
3. 确认文件编码为 UTF-8（VS Code 右下角可查看和切换编码）

### Q: 构建报错 Sass 编译失败

```
TOCSS-DART: failed to transform "/scss/main.scss"
```

**原因**：Hugo 不是 Extended 版本，或 Go 模块缓存损坏。

**解决**：
1. 确认安装了 Hugo Extended（见上方 Q1）
2. 清理模块缓存后重试：

```bash
hugo mod clean
hugo server
```

### Q: Go 版本不匹配

```
module requires go >= 1.27.0 (running go 1.24.0)
```

**原因**：OINK 主题要求 Go 1.27.0+。

**解决**：升级 Go 到 1.27.0 或更高版本。

### Q: 直接打开 index.html 显示异常

**原因**：Hugo 生成的 `public/` 目录设计为通过 HTTP 协议访问，直接用 `file://` 协议打开会导致资源路径解析失败。

**解决**：始终使用 HTTP 服务器访问：

```bash
# 开发模式
hugo server

# 预览构建产物
python -m http.server 8080 --directory public
```

---

## 附录：完整示例 — 从零搭建 3 页文档站

以下是一个可以直接运行的最小示例，创建 3 个文档页面的完整站点。

### 文件清单

```text
my-docs/
├── hugo.yaml
├── data/
│   └── home/
│       └── zh.yaml
├── content/
│   ├── _index.zh.md
│   └── docs/
│       ├── _index.zh.md
│       └── guide/
│           ├── _index.zh.md
│           ├── introduction.zh.md
│           ├── getting-started.zh.md
│           └── configuration.zh.md
└── go.mod
```

### hugo.yaml

```yaml
title: &siteTitle 我的产品
baseURL: https://example.org/
defaultContentLanguage: zh

languages:
  zh:
    label: 简体中文
    locale: zh-CN
    weight: 2
    title: *siteTitle
    hasCJKLanguage: true

markup:
  goldmark:
    renderer:
      unsafe: true
    parser:
      attribute:
        block: true
  highlight:
    noClasses: false

params:
  ui:
    dark_mode: true
    sidebar_menu_foldable: true

module:
  imports:
    - path: github.com/pgsty/oink
  hugoVersion:
    extended: true
    min: 0.160.1
```

### data/home/zh.yaml

```yaml
sections: [hero, cta]

hero:
  align: center
  eyebrow: 我的产品
  title_lines:
    - words: [{ text: 简单高效的 }]
    - words: [{ text: 解决方案。 }]
  lead: 帮助你快速构建和管理项目。
  actions:
    - { label: 阅读文档, url: docs/, icon: fa-solid fa-book, style: primary }

cta:
  title: 立即开始
  label: 查看文档
  url: docs/
```

### content/_index.zh.md

```yaml
---
title: 我的产品
description: 我的产品官方文档。
---
```

### content/docs/_index.zh.md

```yaml
---
title: 文档
linkTitle: 文档
type: docs
icon: fa-solid fa-book
cascade:
  type: docs
  footer_style: slim
---

我的产品技术文档。
```

### content/docs/guide/_index.zh.md

```yaml
---
title: 使用指南
linkTitle: 指南
description: 从零开始了解我的产品。
weight: 10
icon: fa-solid fa-book-open
cascade:
  type: docs
---

本指南将帮助你快速上手我的产品。
```

### content/docs/guide/introduction.zh.md

```yaml
---
title: 产品介绍
description: 了解核心功能和特性。
weight: 10
---

## 什么是我的产品

我的产品是一个用于解决 XX 问题的工具。

## 核心特性

- **高性能**：毫秒级响应
- **易集成**：5 分钟完成接入
- **安全可靠**：企业级安全保障
```

### content/docs/guide/getting-started.zh.md

```yaml
---
title: 快速上手
description: 安装和基本使用。
weight: 20
---

## 安装

```bash
npm install my-product
```

## 基本使用

```js
import { MyProduct } from 'my-product'
const app = new MyProduct()
app.start()
```
```

### content/docs/guide/configuration.zh.md

```yaml
---
title: 配置指南
description: 了解所有配置选项。
weight: 30
---

## 基础配置

```js
const config = {
  apiKey: 'your-api-key',
  debug: false,
}
```

## 高级配置

详见 API 参考文档。
```

### go.mod

```text
module my-docs

go 1.27.0

require github.com/pgsty/oink v1.0.0
```

### 运行

```bash
hugo server
```

打开 `http://localhost:1313/`，你将看到一个完整的 3 页文档站：

- 首页显示 Hero 区域和行动按钮
- 导航栏包含「文档」入口
- 侧边栏自动显示「使用指南」分组，包含 3 个页面
- 点击页面可在侧边栏中切换

---

> 本教程基于 OINK Starter 项目实际结构和配置编写，所有示例均可直接运行。
> 如需了解更多，请参考 OINK 主题官方文档：https://oink.pgsty.com/
