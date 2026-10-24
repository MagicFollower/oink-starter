# SILO 中文文档站

基于 [Hugo](https://gohugo.io/) + [OINK](https://oink.pgsty.com/) v1.3.2 构建的 **PGSTY SILO 中文文档站**。内容为 `pgsty/silo` 20260903 快照的中文文档手册，覆盖安装、迁移、管理、开发、运维与兼容边界。

> **SILO 是由 Pigsty 社区维护的 MinIO 分支。本项目并非 MinIO, Inc. 的关联项目，也未获得其认可、赞助或背书。**"MinIO" 是 MinIO, Inc. 的商标，此处仅用于标识上游项目。

## 站点特征

- **仅简体中文**：`defaultContentLanguage: zh`，英文与法文语言块保持注释状态；
- **完全离线可构建**：主题本地化在 `oink-main/oink-main/`（OINK v1.3.2，1,273 个文件），配合 `go.mod` 的 `replace` 指向，无需联网下载任何模块；
- **4 套视觉预设**：Paper / Slate / Ink / Terminal，读者在页面 Appearance 面板一键切换，选择写入 localStorage 跨页记住。

本仓库从 [pgsty/oink-starter](https://github.com/pgsty/oink-starter) 模板骨架起步，内容已整体替换为 SILO 文档克隆：2026-09-09 首次导入内容（首提交 `0a69173`），2026-10-24 主题从 v1.0.0 升级到 v1.3.2（详见「主题与视觉预设」一节）。模板自带的首页文案、博客示例与四章节小书仍保留，尚未替换为 SILO 品牌内容。

> 第一次接触 Hugo？阅读 [零基础搭建教程](getting-started.zh.md)，从零开始 10 分钟理解一套文档站的搭建流程。

## 快速开始

```bash
git clone https://github.com/MagicFollower/oink-starter.git
cd oink-starter
hugo server
```

打开 <http://localhost:1313/>。主题已本地化，无需联网；离线或内网环境建议显式设置两个环境变量，避免 Hugo 尝试联网拉取工具链与远程模块：

```powershell
$env:GOTOOLCHAIN = "local"; $env:GOPROXY = "off"   # PowerShell
hugo server -D
```

### 环境要求

| 依赖 | 版本要求 | 用途 |
|------|----------|------|
| Hugo Extended | >= 0.166.0 | 站点生成（必须 Extended 版以支持 SCSS；OINK v1.3.2 的最低要求） |
| Go | >= 1.27.0 | Hugo 模块系统（`go.mod` 声明 `go 1.27.0`） |
| Git | 任意 | 版本控制 + `enableGitInfo` 时间戳 |

不需要 Node.js 或 npm（`package.json` 只是可选的命令别名，见「构建与部署」）。

## 项目结构

```text
oink-starter/
├── hugo.yaml                  # 唯一的站点配置文件
├── go.mod / go.sum            # Go 模块（replace 指向本地 oink-main，锁定 OINK v1.3.2）
├── oink-main/oink-main/       # 本地化主题副本（OINK v1.3.2，勿修改）
├── package.json               # 可选 npm 命令别名（dev / build / hugo / stop）
│
├── content/                   # 内容目录（所有 Markdown）
│   ├── _index.zh.md           # 首页（仍为模板占位文案）
│   ├── docs/                  # SILO 文档主区域（404 个中文页面，见「内容地图」）
│   │   ├── _index.zh.md       # 文档总览页（含 SILO 归属声明与快速开始）
│   │   ├── glossary.zh.md     # 术语表
│   │   └── hugo-guide.zh.md   # Hugo 技术文档
│   ├── blog/                  # 博客（模板示例文章，post/design/release 各 2 篇）
│   └── book/                  # 书籍（模板自带 4 章小书，讲骨架自身工作流）
│
├── data/home/                 # 首页数据（zh/en/fr 三份；zh 仍为模板占位）
├── assets/icons/logo.svg      # 站点 Logo
├── static/favicon.svg         # 站点图标
├── i18n/fr.yaml               # 法文翻译残留（fr 语言未启用，文件不生效）
├── examples/                  # 语言配置档（single / bilingual，见「多语言」）
├── scripts/                   # 语言清理脚本（remove-en-docs / remove-fr-docs）
├── .github/workflows/         # GitHub Pages 与 Cloudflare Pages 部署工作流
├── getting-started.zh.md      # 零基础搭建教程（独立文档，不纳入站点）
└── public/                    # 构建输出（勿手动编辑，已加入 .gitignore）
```

> 所有配置集中在根目录 `hugo.yaml` 一个文件，不存在 `config/` 目录或多个 TOML 配置文件。

## 内容地图

`content/docs/` 下共 404 个中文 Markdown 页面（含各级 `_index.zh.md`），按读者场景分六个一级分类：

| 分类 | 篇数 | 覆盖内容 |
|------|------|----------|
| `administration/` | 53 | 日常管理：批量框架、桶复制、控制台、IAM、监控、对象管理、服务端加密 |
| `operations/` | 63 | 部署运维：cert-manager、部署形态、监控告警、数据恢复、网络加密、排障 |
| `reference/` | 254 | 命令与参数参考：`silo` 服务端与 `mc` 全量子命令（baremetal / kubernetes / deprecated 各档） |
| `developers/` | 16 | 开发集成：Go / Java / Python / JS / .NET / Haskell / Rust SDK、STS、对象 Lambda |
| `compatibility/` | 8 | 兼容与迁移：二进制与软件包、控制台、mcli、迁移指南、健康检查 |
| `integrations/` | 7 | 第三方集成：AWS CLI、Spark/Hive、cert-manager 签发、nginx 反代、Veeam |

另有 `blog/`（post / design / release 各 2 篇）与 `book/`（模板自带 4 章）为骨架示例内容，与 SILO 无关，可整体替换或删除。

## 主题与视觉预设

- **主题版本**：OINK **v1.3.2**（2026-10-18 发布），本地副本 1,273 个文件 / 22,234,796 字节，位于 `oink-main/oink-main/`。技能基线副本与判据脚本见工作区 `oink-starter/skill_base_oink1.3.2/`。
- **升级记录**（2026-10-24，自 v1.0.0）：整目录替换主题副本；`go.mod` / `go.sum` 升 v1.3.2；`hugo.yaml` 的 `hugoVersion.min` 从 0.160.1 升到 0.166.0；新增 `preset` / `preset_menu` 两行实值配置；本站无站点级 partial 覆盖，不涉及覆盖清理。
- **生效判据**（只查配置不算数，要看产物）：`hugo.yaml` 中 `preset: paper` 与 `preset_menu: [paper, slate, ink, terminal]` 必须是不带 `#` 的实值；构建产物 `public/index.html` 的 `<html>` 标签上要能读到 `data-td-preset="paper"`。升级后实测：`Pages 1022 / Static files 34 / 0 ERROR`，产物含 `llms.txt`、带哈希的离线搜索索引与 `_print/` 打印档。
- **升级前不可离线构建**：v1.0.0 时代主题靠远程模块解析（本地 `oink-main/` 为空目录），离线环境直接失败；升级后主题落地本地，`GOTOOLCHAIN=local GOPROXY=off` 下即可完整构建。

## 配置说明

`hugo.yaml` 是唯一的配置文件。当前生效的关键配置（摘录）：

```yaml
title: &siteTitle Project Name      # 站点标题（YAML 锚点）—— 仍为模板占位，待改成 SILO
baseURL: https://example.org/       # 生产环境 URL —— 待改
relativeURLs: true                  # 相对链接：产物可直接从磁盘路径打开，可挂任意子路径
defaultContentLanguage: zh
enableGitInfo: true                 # 从 Git 提交记录读每页最后修改时间

languages:
  zh:
    label: 简体中文
    locale: zh-CN
    hasCJKLanguage: true            # en / fr 语言块整块注释，需要时取消注释

params:
  offline_search: true              # 离线搜索（构建产物带搜索索引 JSON）
  ui:
    dark_mode: true                 # 明暗模式切换（与视觉预设相互独立）
    sidebar_menu_foldable: true
    sidebar_expand_levels: 4
    backlinks: true
    preset: paper                              # 站点默认观感，必须出现在 preset_menu 里
    preset_menu: [paper, slate, ink, terminal] # 4 套预设全开

module:
  imports:
    - path: github.com/pgsty/oink
      replacement: ./oink-main/oink-main   # 指向本地主题副本，离线构建的关键
  hugoVersion:
    extended: true
    min: 0.166.0                           # OINK v1.3.2 的最低 Hugo 要求
```

`hugo.yaml` 中还预置了整块注释的可选配置：仓库链接、Giscus 评论、Google Analytics、主题色、字体、图片缩放、分享按钮、反馈组件、logo 与 wordmark。启用某个集成时取消对应注释即可。

## 多语言

所有语言的文件放在同一目录，通过后缀区分：

| 文件名 | 语言 | 访问路径 |
|--------|------|----------|
| `page.zh.md` | 中文 | `/page/` |
| `page.md` | 默认语言（当前即中文） | `/page/` |
| `page.fr.md` | 法文 | `/fr/page/`（fr 未启用时被安全忽略） |

当前仅启用中文。`docs/` 已全量中文化（404 个页面全部为 `.zh.md`）；`blog/`、`book/` 还残留模板的英文源文件（`.md` 无后缀形式），因默认语言即中文，它们与 `.zh.md` 同名并排时以中文版为准，不影响构建。需要彻底清理时用维护脚本：

```powershell
powershell -File scripts/remove-en-docs.ps1    # 递归删除英文 .md（保留 .zh.md）
powershell -File scripts/remove-fr-docs.ps1    # 递归删除法文 .fr.md
```

切换语言配置档（先备份当前 `hugo.yaml`）：

```bash
cp examples/hugo.single.yaml hugo.yaml     # 仅英文
cp examples/hugo.bilingual.yaml hugo.yaml  # 英文 + 中文
```

## 添加与维护文档

以在 `operations/` 下新增一篇文档为例。

**第一步**：选择归属分类（一篇只归一类：讲机制原理进 `administration/`，讲部署运维进 `operations/`，讲参数默认值进 `reference/`，讲 SDK 用法进 `developers/`）。已有对应板块则直接进，确认要新开板块时先建板块 `_index.zh.md`。

**第二步**：创建 `content/operations/<板块>/<文件名>.zh.md`，front matter 至少三字段：

```yaml
---
title: 使用 cert-manager 管理 Operator 证书
description: 一句话说明本文解决什么问题。
weight: 10                       # 同目录现有最大值 + 1
---
```

板块 `_index.zh.md` 需要 `title` / `linkTitle` / `description` / `weight`，子页面的 `type: docs` 由一级分类的 `cascade` 级联继承，无需逐页声明。

**第三步**：预览验证：

```bash
hugo server -D
```

侧边栏应出现新条目；构建 0 ERROR、新增页面的内部链接可点开。

**内部链接规则**：用**绝对路径**引用站内页面，不带语言前缀，Hugo 按当前语言自动解析：

```markdown
[迁移指南](/docs/compatibility/migration/)
[术语表](/docs/glossary/)
```

## 构建与部署

### 常用命令

```bash
hugo server -D                        # 开发服务器（热重载 + 草稿）
hugo --cleanDestinationDir            # 标准构建（验证用）
hugo --cleanDestinationDir --gc --minify --environment production \
  --printPathWarnings --panicOnWarning    # 发布闸门（有告警即失败）
```

可选的 npm 别名（等价关系，非必需）：

| 命令 | 等价于 |
|------|--------|
| `npm run dev` | `hugo server -D` |
| `npm run hugo` | `hugo` |
| `npm run build` | `hugo --minify` |
| `npm run stop` | 终止占用 1313 端口的进程 |

### 部署

仓库带两条现成工作流：`.github/workflows/github-pages.yaml`（GitHub Actions 部署 GitHub Pages，需在 **Settings → Pages** 把来源设为 **GitHub Actions**）与 `cloudflare-pages.yaml`（Direct Upload，需 `CLOUDFLARE_ACCOUNT_ID` 与 `CLOUDFLARE_API_TOKEN` 两个 secret）。

> **注意**：两条工作流的 `HUGO_VERSION` 仍钉在 **0.165.0**，低于 OINK v1.3.2 要求的 **0.166.0** 下限。启用任一工作流前，先把该值改为 `0.166.0` 或更高，否则 CI 构建会因主题用了新版本特性而失败。

也可以手动部署：本地跑上面的发布闸门命令，把 `public/` 交给你选择的静态托管。

## 已知内容缺口（克隆自带，非升级引入）

全站产物有约 743 条站内断链，**全部自首次克隆就存在**（已用 git 首提交核对：当时 `static/` 就只有 `favicon.svg`，断链目标页面在 `content/` 里从未存在；主题升级未动过 `content/`）。三类：

| 类型 | 数量 | 原因 |
|------|------|------|
| 图片 | 293 | 正文引用上游 `images/*.svg` 等配图，克隆时未随带（`static/` 仅 `favicon.svg`） |
| 页面 | 119 | 指向 `docs/get-started/`、`/about/`、`blog/design/*` 等模板或上游页面，本站从未建过 |
| 锚点 | 331 | 指向上述缺失页或术语表内不存在的锚 ID |

处理原则：这些是上游文档克隆的既有缺口，补齐需要回上游取图取页，属于内容工作项，与主题版本无关。新增文档时不要再引用 `images/` 下的路径，配图请放入 `static/` 后引用。

## 什么叫做完了

本地构建成功、改动已提交、工作流转绿、公网渲染正确，是四道各自独立的闸门。部署后逐个打开首页、`/docs/` 与六个分类页，桌面和移动端各看一遍；换预设（Paper/Slate/Ink/Terminal）后再抽两页确认观感切换与记住生效。

## 许可

MIT（见 `LICENSE`）。采用模板部分时替换通用版权声明；SILO 文档内容的著作权与许可遵循其上游 `pgsty/silo` 项目的口径。
