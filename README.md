# OINK Starter

一个面向开源项目的生产就绪型站点骨架，基于 [OINK](https://oink.pgsty.com/) 主题和 Hugo 构建。预置博客（Blog）、技术文档（Docs）和连续指南（Book）三大内容板块，默认启用简体中文，可选开启英文和法文。

不包含 OINK 主题文档、分析账号、评论仓库、回归测试套件或项目专属品牌资产。Google Analytics 和 Giscus 默认保持注释状态，按需启用。

> 第一次使用？阅读 [零基础搭建教程](getting-started.zh.md)，从零开始 10 分钟完成站点搭建。

## 快速开始

### 使用此模板

在 GitHub 上点击 **Use this template** 创建你的仓库，然后执行：

```bash
git clone https://github.com/YOU/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
hugo server
```

打开 <http://localhost:1313/>。首次运行会自动下载 OINK Hugo 模块。

### 直接克隆

```bash
git clone https://github.com/pgsty/oink-starter.git
cd oink-starter
hugo server
```

### 环境要求

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| Hugo Extended | >= 0.160.1 | 站点生成（必须 Extended 版以支持 SCSS） |
| Go | >= 1.27.0 | Hugo 模块系统 |
| Git | 任意 | 版本控制 + `enableGitInfo` 时间戳 |

不需要 Node.js 或 npm。

## 项目结构

```text
oink-starter/
├── hugo.yaml                  # 唯一的站点配置文件
├── go.mod / go.sum            # Go 模块依赖（锁定 OINK 主题版本）
├── package.json               # npm 脚本（dev / build / hugo / stop）
│
├── content/                   # 内容目录（所有 Markdown 文件）
│   ├── _index.zh.md           # 首页
│   ├── docs/                  # 技术文档（type: docs）
│   │   ├── _index.zh.md       # 文档 section 首页（设置 cascade 级联）
│   │   ├── administration/    # 管理
│   │   ├── compatibility/     # 兼容性
│   │   ├── developers/        # 开发
│   │   ├── integrations/      # 集成
│   │   ├── operations/        # 运维
│   │   ├── reference/         # 参考手册
│   │   ├── glossary.zh.md     # 术语表
│   │   └── hugo-guide.zh.md   # Hugo 技术文档
│   ├── blog/                  # 博客（type: blog）
│   │   ├── post/              # 文章
│   │   ├── design/            # 设计记录
│   │   └── release/           # 版本公告
│   └── book/                  # 书籍（type: book，连续阅读体验）
│       ├── 01-preview.zh.md
│       ├── 02-structure.zh.md
│       ├── 03-customize.zh.md
│       └── 04-deploy.zh.md
│
├── data/home/                 # 首页数据文件（按语言分）
│   ├── zh.yaml
│   ├── en.yaml
│   └── fr.yaml
│
├── assets/icons/logo.svg      # 站点 Logo
├── static/favicon.svg         # 站点图标
├── i18n/                      # 国际化翻译文件
├── examples/                  # 配置示例
│   ├── hugo.bilingual.yaml    # 中英双语配置
│   └── hugo.single.yaml       # 单语言配置
├── scripts/                   # 维护脚本
│   ├── remove-en-docs.ps1     # 移除英文文档
│   └── remove-fr-docs.ps1     # 移除法文文档
│
├── getting-started.zh.md      # 零基础搭建教程（独立文档，不纳入站点）
└── public/                    # 构建输出（勿手动编辑，已加入 .gitignore）
```

> **注意**：所有配置集中在根目录的 `hugo.yaml` 一个文件中，不存在 `config/` 目录或多个 TOML 配置文件。

## 配置说明

`hugo.yaml` 是唯一的配置文件，包含站点标题、语言、UI 参数和模块声明：

```yaml
title: &siteTitle Project Name    # 站点标题（YAML 锚点，各语言共享）
baseURL: https://example.org/      # 生产环境 URL
defaultContentLanguage: zh         # 默认语言

languages:
  zh:
    label: 简体中文
    locale: zh-CN
    hasCJKLanguage: true

params:
  ui:
    dark_mode: true                # 明暗模式切换
    sidebar_menu_foldable: true    # 侧边栏可折叠
    section_index: cards           # 章节首页卡片布局
    blog_index: cards              # 博客首页卡片布局
  offline_search: true             # Lunr 离线搜索

module:
  imports:
    - path: github.com/pgsty/oink  # OINK 主题
```

`hugo.yaml` 中还预置了已注释的可选配置：仓库链接、Giscus 评论、Google Analytics、强调色、字体、图片缩放、分享按钮和反馈组件。准备好启用某个集成时，取消对应注释即可。

## 多语言文件命名约定

所有语言的文件放在同一目录下，通过后缀区分：

| 文件名 | 语言 | 访问路径 |
|--------|------|----------|
| `page.md` | 默认语言（zh） | `/page/` |
| `page.zh.md` | 中文（显式标记） | `/page/` |
| `page.fr.md` | 法文 | `/fr/page/` |
| `_index.md` | 默认语言 section 首页 | `/docs/` |
| `_index.zh.md` | 中文 section 首页 | `/docs/` |

当前项目仅启用中文（`en` 和 `fr` 已注释）。如需启用其他语言，取消 `hugo.yaml` 中对应语言块的注释即可。

### 语言配置切换

项目提供三份预置配置，按需复制：

```bash
cp examples/hugo.single.yaml hugo.yaml     # 仅英文
cp examples/hugo.bilingual.yaml hugo.yaml  # 英文 + 中文
```

## 构建与开发

### 常用命令

```bash
# 开发服务器（热重载 + 草稿渲染）
hugo server -D

# 标准构建
hugo

# 生产构建（压缩 + 清理缓存）
hugo --minify --gc --cleanDestinationDir
```

### npm 脚本

| 命令 | 等价于 |
|------|--------|
| `npm run dev` | `hugo server -D` |
| `npm run hugo` | `hugo` |
| `npm run build` | `hugo --minify` |
| `npm run stop` | 终止占用 1313 端口的进程 |

## 实战：添加你的第一篇文档

下面以创建一个「快速开始」文档页面为例，演示如何将内容放入项目并正确显示。

### 第一步：创建 section 目录和首页

在 `content/docs/` 下新建一个目录，并创建 section 首页 `_index.zh.md`：

```bash
mkdir content/docs/get-started
```

```yaml
# content/docs/get-started/_index.zh.md
---
title: 快速开始
linkTitle: 快速开始
description: 从零到运行，五分钟上手指南。
weight: 10
icon: fa-solid fa-rocket
cascade:
  type: docs
---

从这里开始，了解如何安装、配置和运行你的第一个项目。
```

**关键字段说明**：

| 字段 | 作用 |
|------|------|
| `title` | 页面标题，显示在浏览器标签和页面顶部 |
| `linkTitle` | 侧边栏中显示的短标题 |
| `description` | 页面描述，用于 SEO 和卡片摘要 |
| `weight` | 排序权重，数值越小排越前 |
| `icon` | 侧边栏图标（Font Awesome 类名） |
| `cascade.type: docs` | 级联到子页面，让子页面自动继承文档类型 |

### 第二步：创建文档内容页

在 section 目录下创建具体的文档页面：

```yaml
# content/docs/get-started/install.zh.md
---
title: 安装指南
description: 在不同操作系统上安装项目的完整步骤。
weight: 10
---

## 系统要求

- 操作系统：Windows 10+、macOS 12+、Ubuntu 20.04+
- 内存：最低 4 GB，推荐 8 GB

## 安装步骤

### Windows

1. 下载安装包：

   ```bash
   winget install my-project
   ```

2. 验证安装：

   ```bash
   my-project --version
   ```

### macOS

```bash
brew install my-project
```

### Linux

```bash
curl -fsSL https://example.com/install.sh | bash
```

## 下一步

安装完成后，请阅读[配置说明](/docs/get-started/configure/)了解基本设置。
```

### 第三步：预览效果

```bash
hugo server -D
```

打开浏览器访问 <http://localhost:1313/docs/get-started/>，你应该能看到：

- 左侧边栏新增了「快速开始」分组，带有火箭图标
- 点击展开后显示「安装指南」子页面
- 页面正文正常渲染，代码块高亮正确

### 第四步（可选）：添加更多子页面

继续在 `content/docs/get-started/` 下创建新文件即可自动出现在侧边栏：

```text
content/docs/get-started/
├── _index.zh.md        # section 首页
├── install.zh.md       # 安装指南（weight: 10）
├── configure.zh.md     # 配置说明（weight: 20）
└── first-run.zh.md     # 首次运行（weight: 30）
```

`weight` 值控制侧边栏中的排列顺序。

### 内部链接规则

在文档中使用**绝对路径**链接其他页面，不需要加语言前缀：

```markdown
[迁移指南](/docs/compatibility/migration/)
[术语表](/docs/glossary/)
```

Hugo 会根据当前语言自动解析到对应版本的页面。

## 部署

### GitHub Pages

1. 打开仓库 **Settings → Pages**，选择 **GitHub Actions** 作为来源
2. 推送 `main` 分支，或在 Actions 标签页手动运行 **Deploy to GitHub Pages**

### Cloudflare Pages

1. 创建 Cloudflare Pages **Direct Upload** 项目
2. 添加仓库密钥 `CLOUDFLARE_ACCOUNT_ID` 和 `CLOUDFLARE_API_TOKEN`
3. 运行 **Deploy to Cloudflare Pages** 工作流

### 本地验证生产构建

```bash
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning
```

构建产物输出到 `public/` 目录，可直接部署到任意静态文件服务器。

## 许可

MIT。采用此模板时请替换通用版权声明。
