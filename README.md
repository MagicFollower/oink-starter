# Docker 团队知识库 — AI Agent 操作规范

本项目是基于 Hugo + OINK 主题的 **中文文档站**，主题本地副本为 OINK **v1.4.0**（`oink-main/oink-main/`，1,292 个文件 / 27,213,292 字节）。仅简体中文，可完全离线构建：`GOTOOLCHAIN=local` + `GOPROXY=off` 下不触网。

结构源是《Docker知识库内容结构与组织清单》v2.1。**该清单不在仓库内**，`.staging/` 目录（含取源、建矩阵、矩阵校验脚本与 `matrix.json`）也已从磁盘移除，且从未进过 git 历史。因此本文件描述的一律是**磁盘现状**：结构一致性靠人工比对目录树，没有自动闸门兜着。第八节列了当前跑不了的校验与仓库里的遗留物。

读取本文件后，AI 应能自主完成文档的归类、格式化、放置、关联更新与构建验证。

## 一、项目结构

下面是 `ls -A` 与 `find` 实测出来的树，不含 `public/`、`resources/` 的内容明细（两者是构建产物，已被 `.gitignore` 忽略）：

```text
Docker知识库/
├── content/
│   ├── _index.md                  # 首页
│   └── docs/
│       ├── _index.md              # 文档总览页：11 行 `- [显示名](/docs/NN-目录名/)` + `{.cards}`
│       └── NN-中文分类名/          # 一级分类 → 中文板块子目录 → 中文文章文件
│           ├── _index.md          # 分类页（带 cascade）
│           └── 中文板块名/
│               ├── _index.md      # 板块页
│               └── 中文文章名.md
├── assets/
│   ├── icons/logo.svg             # 站点 logo；hugo.yaml 不写 logo 键，主题默认就取这个路径
│   └── scss/_styles_project.scss  # 站点级 SCSS 覆盖（主题 _main.scss 末尾 @import 它），表格列宽规则在这里
├── static/
│   ├── favicon.svg
│   └── picture/.gitkeep           # 配图目录，当前是空的（只有占位文件）
├── data/home/zh.yaml              # 首页 hero / cards / cta 三段数据
├── layouts/_partials/shell/root-menu-roots.html   # 唯一的站点级 partial 覆盖
├── hugo.yaml                      # 站点唯一配置
├── go.mod / go.sum                # 主题走 replace 本地化
├── oink-main/oink-main/           # 本地化主题副本（v1.4.0，1,292 文件 / 27,213,292 字节，勿改）
├── doc/
│   ├── 技术文档编写规范.md          # 19,067 字节
│   ├── 复刻覆盖矩阵.md             # 15,743 字节，数字已滞后（见第八节）
│   └── 运行与构建（T0Level）.md     # 252,824 字节，逐轮实测台账
├── 示例/                          # 可跑的配套示例，不参与 Hugo 构建
│   ├── 入门-hello与nginx/
│   ├── 贯穿示例/
│   ├── 存储双案例/
│   └── Harbor私有仓库/
├── run.cmd                        # Windows 启动入口（141 行 CRLF / 4,214 字节 / 纯 ASCII）
├── .gitignore / LICENSE(MIT) / README.md
└── 构建产物与遗留物：public/ resources/ .hugo_build.lock .tmp/ noopen2.out Docker知识库/
```

`示例/` 四个子目录各自带 `README.md`，其中三个还带校验脚本（`入门跑一遍.py`、`verify_storage.py`、`verify_chain.py`），`Harbor私有仓库/` 另带 `Harbor.cmd`、`harborctl.py`、`docker-compose.yml` 与官方安装包留档。它们在 `content/` 之外，Hugo 不构建，正文用站内链接指过去而不是把它们当页面。

## 二、内容分类体系

磁盘实测：**11 个一级分类 / 26 个知识板块 / 38 篇文章**。`content/` 下共 77 个 `.md`，其中 39 个是 `_index.md`（1 个首页 + 1 个文档总览 + 11 个分类 + 26 个板块），77 − 39 = 38 与文章数吻合。

| 目录 | `weight` | 分类名 | 知识板块（各板块篇数） | 篇数 |
|------|-----|--------|----------|-----|
| `00-导读/` | 1 | 导读 | 怎么用这个库(2)、把环境搭好(1) | 3 |
| `01-基础认知/` | 2 | 基础认知 | 为什么是容器(2)、第一次动手(1) | 3 |
| `02-核心操作/` | 3 | 核心操作 | 跑起来(2)、接上去(1) | 3 |
| `03-镜像构建/` | 4 | 镜像构建 | 写出来(1)、养小养快(1)、交出去(1) | 3 |
| `04-单机编排/` | 5 | 单机编排 | 定义(1)、启停(1)、日常(1) | 3 |
| `05-原理深入/` | 6 | 原理深入 | 隔离与资源(2)、网络与运行时(1) | 3 |
| `06-工程化与生产/` | 7 | 工程化与生产 | 交付链路(1)、运行基线(2) | 3 |
| `07-运维手册/` | 8 | 运维手册 | 检索与规矩(1)、按故障域排错(3) | 4 |
| `08-生态与附录/` | 9 | 生态与附录 | 生态坐标(1)、查阅件(1) | 2 |
| `09-常见问题/` | 10 | 常见问题 | FAQ(1) | 1 |
| `10-存储专题/` | 11 | 存储专题 | 基础(2)、落点与生命周期(2)、配置与内容(1)、数据保护(2)、故障手册(3) | 10 |

`weight` 从 1 到 11 连续无跳号，与 `content/docs/_index.md` 的 11 行卡片顺序一致（落地清单写在该文件末尾的 HTML 注释里：链接条目数必须等于一级分类目录数）。

> **新增一级分类**：优先归入现有分类；确需新增时按编号递增建目录，`weight` 取同级最大值 +1，并同步更新本表、`content/docs/_index.md` 的卡片行、以及父级分类 `_index.md` 里的「知识板块」列表。矩阵校验脚本已不在仓库，这三处只能靠人工对齐——改完务必 `grep -c '^- \[' content/docs/_index.md` 数一遍卡片行是否等于分类目录数。

**归类原则**：一篇文档只归属一个板块，判据是「读者在什么场景下需要它」，不是「清单把它编在第几章」。讲机制原理、讲怎么搭、讲参数默认值、讲踩坑约束，各归各处。清单的章节与本站的 38 篇是多对一关系，合并边界以「同一个意图能概括」为准。

## 三、命名与 Front Matter

| 层级 | 命名 | 示例 |
|------|------|------|
| 一级分类目录 | 两位编号 + 短横线 + 中文分类名 | `03-镜像构建/` |
| 二级子目录（板块） | 中文命名 | `养小养快/` |
| 文章文件 | 中文命名，不含空格、不含路径分隔符、必须 `.md` 结尾 | `分层缓存、多阶段构建与镜像瘦身.md` |

不使用 `.zh.md` / `.en.md` 后缀；`defaultContentLanguage: zh` 下 `.md` 即中文。

「必须 `.md` 结尾」这条要当硬规矩守，起因是一次实测事故：清单曾出现 `7.1-命令速查表.md（置顶）` 与 `复盘库/（一事故一文件）` 这类写法，它们照样建得出文件、照样被认领、`isfile` 照样过，但按 `.md` 后缀收集文章的校验器看不见它们，于是这些源**永远不会被判为漏覆盖**——`UNCOVERED=0` 是假的。当时兜住这条的校验脚本在 `.staging/` 里，现已移除，所以只能靠人守：新建文件后用 `find content -name '*.md' ! -name '_index.md' | wc -l` 数一遍，看是否等于本表「篇数」列的合计。

文章三字段缺一不可，`weight` 取同目录最大值 +1：

```yaml
---
title: 文章标题
description: 一句话说明本文解决什么问题（会进侧边栏卡片与 SEO）。
weight: 1
---
```

一级分类 `_index.md` 必须带 `type: docs`、`icon`、`weight`、`sidebar_root_for: self`、`sidebar_root_link_self: true` 与 `cascade`；板块 `_index.md` 只需 `title`/`linkTitle`/`description`/`weight`，`type: docs` 由一级分类 `cascade` 继承。

## 四、AI 操作流程

1. **判断归属** → 2. **定路径** `content/docs/{一级}/{板块}/{文件}.md` → 3. **写 front matter 与正文** → 4. **新建板块时成对操作**（先建板块 `_index.md`，再在父级分类 `_index.md` 的「知识板块」列表补一行；新建一级分类还要补 `content/docs/_index.md` 的卡片行与第二节那张表）→ 5. **构建验证**。

正文按 `doc/技术文档编写规范.md` 写（对应清单的写作要求 W1~W5），硬性门槛：

- 每篇第一屏是清单 W5 的**七项**元数据引用块：实战落点、示例版本、前置依赖、本篇产出物、拓展接口、难度·耗时、自测三题；
- 首个二级标题必须是「为什么需要 X？（痛点引入）」，全篇走 痛点 → 设计 → 流程；
- 全文 ≥ 3 个「💡 新人小结」（开头 / 复杂概念处 / 结尾），每个小结在类比之后必须补一句**机制对应**，类比会在某处误导的要写明在哪里失效；
- 架构、流程、状态机用 **Mermaid**；轻量线性流程可用文本箭头；**严禁** `┌┐└┘├┤┬┴┼` 等制表字符；
- 专有名词与缩写给术语表，含「在本文中的角色」列；
- 代码/配置块可运行、带注释、带真实输出、带 ✅ 推荐与 ❌ 不推荐；
- 禁止「限于篇幅」「此处从略」「自行查阅」「待补充」「TODO」；
- 正文 ≥ 260 行（参考量级，不是灌水指标）。

**技术事实的出处口径**：本站无上游仓库可抄，事实只有两个合法来源——**Docker 官方文档**（写清版本与 as-of 日期）与**本机实测输出**（贴真实终端文本）。不得按「同类 API 惯例」推定默认值、版本号、超时值或异常行为；查不到就写「官方文档未给出」或「未实测」。凡引用清单的结论，出处写**章节号**（如 `清单 3.6`），不写本地暂存目录路径。

**版本查重**：本站只有一份清单源、不存在多版本分叉。将来若引入 Docker 4.x/5.x 之类的版本分叉，必须回到逐字节 MD5 比对的口径，不得只取一版。

**配图引用**：`![说明](/picture/xxx.png)` 绝对路径即可，构建时自动改写为相对路径；中文与空格文件名要 URL 编码。`static/picture/` 目前只有一个 `.gitkeep`，`content/` 里对 `picture/` 的引用数实测为 **0**——要配图先把文件放进 `static/picture/` 再引用，不要写指向空目录的链接。

## 五、构建与环境

**日常入口是站点根的 `run.cmd`**（双击即可）：设 `GOTOOLCHAIN=local`/`GOPROXY=off`、解析 Hugo 与 Go、从 8768 起探测空闲端口（被占自动顺延并打印 `Note`）、校验 Hugo 必须是 Extended、然后 `hugo server --disableFastRender --openBrowser`。可用变量 `PORT`、`HUGO_EXE`、`GO_BIN`、`NO_OPEN=1`、`NO_PAUSE=1`。**只改顶部 PROJECT CONFIG 块**（第 5–12 行），下面的逻辑是技能物料。逐轮实测读数见 `doc/运行与构建（T0Level）.md` 第三节。

手动方式：

```powershell
$env:GOTOOLCHAIN = "local"; $env:GOPROXY = "off"
hugo --cleanDestinationDir                 # 验证构建
hugo server -D                             # 本地预览，默认端口 1313
hugo --cleanDestinationDir --gc --minify   # 发布档
```

本机工具链实测（**「本机版本是 X」必须绑定解析顺序说**，这台机器上同名工具有多份）：

| 工具 | 解析位置 | 实测版本 | 说明 |
|------|------|------|------|
| Hugo | `where hugo` → `D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe` | v0.168.0 **+extended** | `run.cmd` 走的就是这一份 |
| Hugo | `C:\Users\webtu\tools\hugo\hugo.exe`（`run.cmd` 的 `HUGO_FALLBACK`） | v0.168.0 **+extended** | 与上面同版本，PATH 失效时的兜底 |
| Go | `where go` → `C:\Program Files\Go\bin\go.exe` | **go1.27.2** | 系统 PATH 选中它；**升级到 1.4.0 后它已低于下界，直接拿它构建会失败**（实测 `go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)`，rc=1） |
| Go | `C:\Users\webtu\tools\go1.27.3\go\bin\go.exe`（`run.cmd` 的 `GO_FALLBACK`） | **go1.27.3** | **`GO_FALLBACK` 排在 PATH 之前**，所以 `run.cmd` 里生效的是这一份；升级后它是本机唯一能满足下界的那一份 |
| Go | `C:\Users\webtu\tools\go\bin\go.exe` | **go1.25.4** | 低于 `go.mod` 下界，把它顶到 PATH 前面构建就会失败，见第七节 |

两处 `go.mod`（站点与 `oink-main/oink-main/`）的 `go` 指令都是 **1.27.3**——这是 OINK 1.4.0 抬上去的，1.3.2 时代两处都是 1.27.0。取下界时要看两处、不是只看站点那一条。标准版 Hugo 编不了 SCSS，`hugo.yaml` 的 `module.hugoVersion` 写的是 `extended: true` / `min: 0.168.0`（1.4.0 要求 ≥ 0.168.0，1.3.2 时代是 0.166.0）。

`GOTOOLCHAIN=local` 与 `GOPROXY=off` 这两条**实测过的**后果是：在 `local` 口径下，若被选中的 Go 低于 `go.mod` 的 `go` 指令，Hugo 会报 `failed to load modules: failed to download modules: ... go.mod requires go >= 1.27.0 (running go 1.25.4; GOTOOLCHAIN=local)` 并以返回码 1 退出——文本长得像内容错误，其实是工具链闸门（见第七节 A/B 的 B 臂）。不设 `GOTOOLCHAIN=local` 时 Go 会自己去 proxy 拉工具链：本轮在 `C:\Users\webtu\tools\go\bin` 上直接复现到 `go: downloading go1.27.0 (windows/amd64)` 后接 `dial tcp 142.250.204.49:443: connectex: ... failed to respond`，离线机必败。

**升级到 OINK 1.4.0 之后这条闸门的样子变了**（2026-10-30 同日 A/B，两臂都回读确认，不是空跑）：同一个站点、同一条 `hugo --cleanDestinationDir`，只换被选中的 Go：

| 臂 | 生效 Go | 结果 |
|---|---|---|
| A | `C:\Program Files\Go` = go1.27.2（PATH 默认） | **rc=1**，`go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)` |
| B | `C:\Users\webtu\tools\go1.27.3` = go1.27.3 | **rc=0**，`Pages 239 / Static files 35 / Total in 2972 ms` |

所以直接在 PATH 默认环境里敲 `hugo` 现在会失败；`run.cmd` 因为把 `GO_FALLBACK` 排在 PATH 之前，照常成功（横幅实跑读到 `Go 1.27.3 or newer is required by go.mod.` 与 `go version go1.27.3`）。手动构建时把 `C:\Users\webtu\tools\go1.27.3\go\bin` 前置即可。

本轮构建实测（`run.cmd`，`NO_OPEN=1 NO_PAUSE=1`）：`Pages 239 / Static files 35`，`Built in 2157 ms` 与 `2239 ms` 两次，**0 个 ERROR**，唯一 WARN 是主题侧 `css.Sass: libsass was deprecated`（主题固有，不是失败，也不要为此加 `--panicOnWarning`）。

**1.4.0 带来的三样东西，产物层逐个核过**（`Static files` 仍是 35，不是 1,292 副本带来的增量——新资产只在使用它们的页面才输出）：

| 能力 | 产物证据 |
|---|---|
| 图表懒渲染（`assets/js/diagram.js`，`IntersectionObserver rootMargin: 320px`） | 产出 `public/js/chunks/diagram.min.fce3cf5c…js`；76 个页面出现 1.4.0 新增的 `<pre class="td-mermaid-source">`，`figure.td-diagram--mermaid` 共 47 个，`stage` 为空待脚本填充 |
| PlantUML 本地渲染 | **默认关闭**，全站 `grep -rl plantuml public --include=*.html` 命中 **0** —— 与技能「未启用时产物里没有 plantuml 引用」一致。要启用得在 `params.ui.plantuml.enable` 打开，本站没开 |
| 表格 `.wide` / `.expand` 阅读抽屉 | `td-table-frame` / `data-td-table-reader` / `class="wide` 全站计数均 **0**，因为内容里 `.wide` 与 `.expand` 标记实测也是 **0**；这是「没用就没输出」，不是回归 |

## 六、约束与禁止事项

1. 不可修改 `oink-main/` 主题目录下任何文件（当前 OINK **v1.4.0**，1,292 个文件与技能物料逐字节一致——74 件 vendored 产物 sha256 全对、三棵树文件数全对，见第七节）。
2. 不可添加非中文内容文件，不可改动 `hugo.yaml` 的语言配置。
3. 新建板块必须同时创建其 `_index.md` 并更新父级分类的「知识板块」列表；新建一级分类还要同步 `content/docs/_index.md` 的卡片行与第二节那张表。目录与索引成对出现。
4. 不可删除已有 `_index.md`；不可让文章缺失 front matter。
5. 不可把「官方未给出」「未实测」的句子写成肯定结论；重组结构、补类比与图示是本职。
6. 一篇文档只属一个板块；跨板块关联用站内链接，不复制正文。
7. 正文不得出现本地暂存目录路径（`.staging/` 一类）。该目录现已不存在，但规矩照旧：交付正文里不该出现只在本机成立的路径。
8. `hugo.yaml` 的 goldmark 三项（`renderer.unsafe`、`parser.attribute.block`、`parser.wrapStandAloneImageWithinParagraph`）、`relativeURLs: true`，以及 `ui.preset` / `ui.preset_menu` 两行不许删或注释掉——后者是 4 套观感可切换的唯一开关，配在 1.0/1.1 主题副本上不生效但**构建一个错都不报**。
9. `baseURL` 一律写根（当前是 `https://example.org/`，仍是待改的占位）。要挂子路径靠部署时把 `public/` 放进那个子目录，**不要**把子路径写进 `baseURL`：与 `relativeURLs: true` 冲突，会把子路径烤进每个资源 URL，页面 200 但 CSS 与 logo 全 404。
10. 站点级自定义开关写进配置文件的 `params` 段，不要指望手改能活过下一轮重新生成。
11. 要改观感（字体、表格、间距一类）**改 `assets/scss/_styles_project.scss`，不要去动 `oink-main/`**。主题 `assets/scss/td/_main.scss` 第 76 行 `@import '../styles_project'` 就是给站点的扩展点，站点 `assets/` 下同名文件会遮住主题里那份空壳——这是唯一既生效又不破坏「主题副本逐字节等于技能物料」的改法。

## 七、偏离登记：一处曾登记、现已撤销的误诊

**当前状态：主题副本是技能物料 OINK v1.4.0 的逐字节拷贝，零手改。** 2026-10-30 从技能 `assets/theme/oink-main/oink-main/` 整棵换入（`cp -a`，不过任何 eol 转换）：1,292 个文件 / 27,213,292 字节，与技能副本 `diff -rq` 干净。校验不是只数文件——用主题自带 `VENDOR.json` 逐件核 sha256：**74 件 vendored 产物 `missing=0 hash_bad=0`**，三棵树（`assets/third_party` 246、`assets/js/third_party` 1、`static/webfonts` 33）声明文件数与实测全对；技能点名的 CRLF 文件也保住了（`viz-global.js` 9/9 行、`LICENSE` 72/72 行）。站点侧 `go.mod` / `go.sum` / `hugo.yaml` 的版本号同步到 `v1.4.0` / `go 1.27.3` / `min: 0.168.0`。

升级前那棵 1.3.2 树（1,273 文件）留了站点外备份 `%TEMP%\oink132-backup`，确认无误后可删；git 里也提交过，随时可 `git checkout` 复原。`go.mod` 的 CRLF/LF 说明照旧：仓库 `core.autocrlf=true`，磁盘 CRLF 与库内 LF 是同一份内容。

这一节保留误诊记录本身，因为它比「没偏离」更有用。

2026-10-25 建骨架时，我登记过一条偏离：把两处 `go.mod` 的 `go 1.27.0` 降成 `go 1.25`，理由是「本机 Go 是 1.25.4，离线口径下 1.27.0 会让 Hugo 加载模块失败」，还做了 A/B 并贴出过 `go: go.mod requires go >= 1.27.0 (running go 1.25.4; GOTOOLCHAIN=local)` 这条真实报错。

报错是真的，结论是错的。2026-10-27 复核时发现两件事：

| 事实 | 读数 |
|---|---|
| 本机其实装着两个 Go | `C:\Program Files\Go` = **go1.27.2**；`C:\Users\webtu\tools\go` = go1.25.4。系统 PATH 选中的是前者 |
| 我上一轮把后者顶到了前面 | 所有测量都在 `export PATH="/c/Users/webtu/tools/go/bin:$PATH"` 之后做，所以「本机 Go」这个说法从一开始就只对我自己造的 PATH 成立 |
| 上一次 A/B 其实是空跑 | 那条命令链里 `cp` 先失败，**`&&` 短路导致写入 go.mod 的 Python 根本没执行**，两臂都跑在 `go 1.25` 上。我把「两臂都成功」当成了对照成立 |

重做的 A/B（每步都回读 `go.mod` 确认写入生效，Hugo 前后都不改写它）：

| 臂 | `go.mod` | 生效 Go | 结果 |
|---|---|---|---|
| A | `go 1.27.0` | go1.27.2 | 返回码 0，构建通过 |
| B | `go 1.27.0` | go1.25.4 | 返回码 1，`go.mod requires go >= 1.27.0 (running go 1.25.4; GOTOOLCHAIN=local)` |

所以真正的约束不是「降级 go.mod 迁就本机」，而是**「保证被选中的 Go ≥ 1.27.0」**。撤销偏离后站点照常构建，已实测。

三条可复用的教训，留在文档里比删掉划算：

1. **别让 `&&` 链的前置失败悄悄吃掉你的写入。** 写入命令失败或被跳过时，后续「对照实验」测的是同一份配置，两臂读数会高度一致——那种一致恰恰是假的。凡是改配置再做 A/B，中间必须插一次**回读确认**。
2. **`$?` 不要接在管道后面。** 本文早期一次读数里，`hugo … | grep …` 的退出码属于 `grep`，构建失败也会显示「命令成功」。要判成败就重定向到文件，单独看退出码。
3. **「本机版本是 X」必须绑定 PATH 说。** 多个工具链共存的机器上，不指明解析顺序的版本结论没有意义。第五节那张表就是按这条重写的。

## 八、已知遗留与当前跑不了的校验

如实登记，别把它们当成可用能力：

| 项 | 现状 | 影响 |
|---|---|---|
| `.staging/`（取源、建矩阵、`matrix_check.py`、`picture_map.py`、`verify_all.py`、`matrix.json`） | 目录已从磁盘移除，且从未进过 git 历史（`git log --all` 里查不到任何 `.staging/` 路径） | 结构审计、链接检查、Mermaid 真解析、覆盖矩阵校验**四类判据全部跑不了**。「矩阵是目录树的唯一事实来源」这句话目前没有任何脚本兜着 |
| `replicate-doc-site` 技能 | 未安装（`~/.qoder-cn/skills/` 下只有 `oink-doc-site`）。`matrix_check.py` / `picture_map.py` 只在 git 历史的 `skill_base_oink1.3.2/replicate-doc-site/scripts/` 等路径下出现过 | 本站最初由它搭建，但要复跑得先把技能装回来 |
| 《Docker知识库内容结构与组织清单》v2.1 | 仓库内与上级目录都找不到（`hugo.yaml` 的 `footer_center_info` 与 `content/docs/_index.md` 正文仍引用它） | 章节归属只能查 `doc/复刻覆盖矩阵.md`，而那份也滞后 |
| `doc/复刻覆盖矩阵.md` | 表头仍是 `一级分类 10 / 知识板块 21 / 重写文档 28 / 源文档归属条目 76`，磁盘实测是 **11 / 26 / 38** | 整个 `10-存储专题/`（5 板块 10 篇）不在矩阵里。生成它的脚本已不在，逐篇归属明细无法从源清单重算，所以本轮**未动这个文件**，只在此登记 |
| `Docker知识库/public/` | 仓库**跟踪着**一个嵌套的 `Docker知识库/public/`，共 246 个构建产物文件 | 根 `public/` 已被 `.gitignore` 忽略，这份嵌套副本看着像误提交。未确认归属前不要删 |
| `noopen2.out` | 2,582 字节，内容是旧版 `run.cmd` 的横幅（`Docs Site - Local Preview`，即换模板前的 `SITE_TITLE`） | 一次 `NO_OPEN` 实跑留下的日志残留，被跟踪进了仓库 |
| `static/picture/` | 只有 `.gitkeep`，`content/` 里 `picture/` 引用数 0 | 第一节旧版说的「drawio 源 + 导出 png」当前不成立 |
| `content/docs/_index.md` 正文 | 第 4 行 `description` 写「十一个主题篇」，第 18 行正文写「十个主题篇」 | 卡片行实测是 11 条，正文那句少算了一个；属站点内容缺陷，不在本轮范围 |
| `.gitignore` | 仍是 7 行旧基线 | 缺 `/_mermaid-harness/`、`*.log`、`Thumbs.db`、`desktop.ini`、`.vscode/`、`*.swp`、`node_modules/` |
| `layouts/_partials/shell/root-menu-roots.html` | 站点级 override 已**冗余**：它与主题 1.3.2 / 1.4.0 两版的差异只在注释，而且比主题版**少** `sidebar_divider` 支持；主题 1.4.0 早已自带它当初要补的 `sidebar_root_menu` 判断 | 内容里 `sidebar_root_menu` 与 `sidebar_divider` 的使用数都是 **0**，所以产物无差别；但它会遮住主题的后续修复。**本轮未删，等你点头** |

**当前唯一能实测的闸门是 `hugo` 构建本身**：0 ERROR、WARN 只允许主题侧 `libsass deprecated` 一条。升级后另有两项可跑通的：`oink-doc-site` 的 `check_links.py --site .`（以 `public/` 为准，实测 `links_checked=360 broken=0 unmapped=0`，资源判据 `pages=118 checked=1548` 全落地）与 `validate_mermaid.py` 生成的离线解析台（真解析实测 `TOTAL=47 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`）。要跑 `verify_site.py` 的全套仍需一份 `site.plan.json`——本站没有，且主题已是 1.4.0，只剩 plan 这一道闸挡着。
