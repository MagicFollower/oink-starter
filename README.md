# OINK Starter

基于 [OINK](https://oink.pgsty.com/) 和 Hugo 构建的项目文档站点模板。内置多语言支持（英文、简体中文、法语），包含博客、文档、手册等内容模块，并提供 GitHub Pages 和 Cloudflare Pages 的部署工作流。

## 快速开始

### 环境要求

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Git | 任意版本 | 版本管理 |
| Go | ≥ 1.25.4 | Hugo 模块依赖管理 |
| Hugo | ≥ 0.160.1 **Extended 版** | 必须使用 Extended 版以支持 SCSS 编译 |

> **注意：** 标准版 Hugo 无法编译本主题的 SCSS 样式，必须使用 Extended 版。详见 [问题004](./doc/问题004-Hugo标准版无法编译SCSS.md)。

### 启动项目

```powershell
# 克隆项目
git clone https://github.com/pgsty/oink-starter.git
cd oink-starter

# 启动开发服务器（包含草稿）
hugo serve -D
```

打开浏览器访问 <http://localhost:1313/>。

### 内网/离线环境启动

内网环境无法从 GitHub 下载主题模块，需要额外配置。详见 [问题001](./doc/问题001-内网环境hugo serve启动失败.md) 和 [问题003](./doc/问题003-Hugo本地主题替换仍下载模块.md)。

**简要步骤：**

1. 在有外网的机器上下载主题：
   ```bash
   git clone --depth 1 https://github.com/pgsty/oink.git
   ```

2. 将主题放入项目目录（如 `oink-main/oink-main/`）

3. 修改 `go.mod`，添加本地替换：
   ```go
   replace github.com/pgsty/oink => ./oink-main/oink-main
   ```

4. 修改 `hugo.yaml`，设置本地主题路径：
   ```yaml
   module:
     imports:
       - path: github.com/pgsty/oink
         replacement: ./oink-main/oink-main
   ```

5. 确保所有 `go.mod` 中的 Go 版本 ≤ 本地安装版本

## 项目结构

```text
oink-starter/
├── content/              # 内容目录（多语言）
│   ├── blog/             # 博客
│   │   ├── post/         # 文章
│   │   ├── design/       # 设计笔记
│   │   └── release/      # 发布公告
│   ├── docs/             # 文档
│   │   ├── introduction/ # 项目介绍
│   │   ├── get-started/  # 快速开始
│   │   ├── tutorial/     # 使用教程
│   │   └── reference/    # 参考手册
│   └── book/             # 手册（短教程）
├── data/home/            # 首页数据（多语言）
├── assets/icons/         # 图标资源
├── static/               # 静态资源
├── i18n/                 # 国际化翻译文件
├── examples/             # 配置示例
│   ├── hugo.single.yaml      # 单语言配置
│   └── hugo.bilingual.yaml   # 双语配置
├── doc/                  # 问题文档（见下方清单）
├── hugo.yaml             # 站点配置（唯一配置文件）
├── go.mod                # Go 模块依赖
└── go.sum                # 依赖校验文件
```

### 多语言文件命名规则

| 语言 | 文件后缀 | 示例 |
|------|---------|------|
| 英文 | `.md` | `overview.md` |
| 简体中文 | `.zh.md` | `overview.zh.md` |
| 法语 | `.fr.md` | `overview.fr.md` |

翻译文件与原文放在同一目录，保持相邻排列。

## 自定义配置

### 必改项

打开 `hugo.yaml`，修改顶部两项：

```yaml
title: &siteTitle 你的项目名称    # 站点标题
baseURL: https://your-domain.org/ # 站点地址
```

### 可选项

`hugo.yaml` 中已预置并注释了以下可选配置，按需取消注释：

| 配置项 | 说明 |
|--------|------|
| `github_repo` | 仓库链接 |
| `comments` | Giscus 评论系统 |
| `services.googleAnalytics` | Google Analytics |
| `logo` / `wordmark` | 品牌标识 |
| `ui.theme_color` | 主题色 |
| `ui.typography` | 字体方案 |

## 构建与部署

### 本地预览

```powershell
# 开发预览（包含草稿）
hugo serve -D

# 仅预览已发布内容
hugo serve

# 局域网访问
hugo serve --bind 0.0.0.0 -p 8080
```

### 生产构建

```powershell
hugo --cleanDestinationDir --gc --minify --environment production
```

生成的静态文件位于 `public/` 目录。

### GitHub Pages 部署

1. 进入 **Settings → Pages**，选择 **GitHub Actions** 作为部署源
2. 推送 `main` 分支，或在 Actions 中手动运行 **Deploy to GitHub Pages**

### Cloudflare Pages 部署

1. 创建 Cloudflare Pages **Direct Upload** 项目
2. 添加仓库密钥 `CLOUDFLARE_ACCOUNT_ID` 和 `CLOUDFLARE_API_TOKEN`
3. 在 Actions 中运行 **Deploy to Cloudflare Pages**

## 常用命令速查

| 命令 | 功能 |
|------|------|
| `hugo serve` | 启动开发服务器 |
| `hugo serve -D` | 启动服务器（包含草稿） |
| `hugo serve --bind 0.0.0.0` | 允许局域网访问 |
| `hugo` | 构建站点 |
| `hugo --minify` | 压缩构建 |
| `hugo new content/blog/post.md` | 创建新内容 |
| `hugo list drafts` | 列出所有草稿 |
| `hugo env` | 查看环境信息 |

更多命令详解见 [问题005](./doc/问题005-Hugo常用命令详解.md)。

## 问题文档清单

开发过程中遇到的问题及解决方案归档于 `doc/` 目录：

| 编号 | 文档 | 问题描述 |
|------|------|---------|
| 001 | [内网环境 hugo serve 启动失败](./doc/问题001-内网环境hugo%20serve启动失败.md) | Go 工具链下载 + Hugo 模块下载失败 |
| 002 | [查看本地 Go 和 Hugo 安装路径](./doc/问题002-查看本地Go和Hugo安装路径.md) | 确认工具安装位置 |
| 003 | [Hugo 本地主题替换仍下载模块](./doc/问题003-Hugo本地主题替换仍下载模块.md) | 需同时配置 hugo.yaml 和 go.mod |
| 004 | [Hugo 标准版无法编译 SCSS](./doc/问题004-Hugo标准版无法编译SCSS.md) | 需使用 Hugo Extended 版本 |
| 005 | [Hugo 常用命令详解](./doc/问题005-Hugo常用命令详解.md) | 命令参考手册 |

## 许可证

MIT。使用本模板时请替换版权信息。
