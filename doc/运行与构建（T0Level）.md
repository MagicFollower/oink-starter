# 运行与构建（T0Level）

读者设定：第一次接手这个仓库的人。本文件记录 OINK v1.3.2 → v1.4.0 升级后的真实命令与实测输出（2026-10-29，Windows 10.0.26300，Git Bash）。未执行的项目在第 8 节与「未验证项汇总」中逐条列出，不写想象中的输出。

## 一、前置要求

| 工具 | 版本 | 本机路径 | 为什么必须是它 |
|------|------|---------|----------------|
| Hugo | Extended 0.168.0 | 本机 `where hugo` 命中 `D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe`；`run.cmd` 也可用 `HUGO_EXE` 指定，最后回退配置块 `HUGO_FALLBACK`（默认 `%USERPROFILE%\tools\hugo\hugo.exe`） | 主题用 SCSS，标准版编不了；OINK v1.4.0 的最低要求是 Extended 0.168.0 |
| Go | 1.27.3 | `C:\Users\webtu\tools\go1.27.3\go\bin\go.exe`（`run.cmd` 依次尝试 `GO_BIN`、配置块 `GO_FALLBACK`、PATH） | `go.mod` 与主题模块都要求 `go 1.27.3`；低于此版本会拒绝构建 |
| Git | 任意 | 系统自带 | `enableGitInfo` 读取提交时间，且主题副本由 Git 跟踪 |

本机实测版本：

```text
$ hugo version
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

$ go version
go version go1.27.3 windows/amd64
```

注意：`C:\Program Files\Go\bin` 里是 Go 1.27.2，`C:\Users\webtu\tools\go` 里是 Go 1.25.4；两者都不满足 `go 1.27.3`。构建前把 1.27.3 的 `bin` 放到 PATH 最前面。

反例（2026-10-29 实测，Go 1.27.2 + `GOTOOLCHAIN=local`）：

```text
$ go version
go version go1.27.2 windows/amd64

$ hugo --cleanDestinationDir
go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)
ERROR failed to load modules: failed to download modules: failed to execute 'go [mod download]': failed to execute binary "go" with args [mod download]: go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)
```

不设置 `GOTOOLCHAIN=local` 时，Go 会尝试下载 go1.27.3；本机实测该下载因网络超时失败。

环境变量硬要求：`GOTOOLCHAIN=local`、`GOPROXY=off`。本站主题用本地 `replace`，全程不需要联网。本轮实测：Go 1.27.2 且未设 `GOTOOLCHAIN=local` 时，Go 会尝试下载 go1.27.3，网络超时失败；`run.cmd` 始终设置这两个变量，正常路径不触发下载。

## 二、项目启动（首次构建）

### 双击启动（Windows）

双击根目录的 `run.cmd`，或在当前目录执行 `cmd /c run.cmd`。脚本顶部 PROJECT CONFIG 块是唯一按项目改的部分（`SITE_TITLE`、`DEFAULT_PORT`、`PORT_MAX`、`HUGO_FALLBACK`、`GO_FALLBACK`、`GO_MIN_NOTE`），下面的逻辑固定：

- 切换项目目录，设置 `GOTOOLCHAIN=local` / `GOPROXY=off`；`chcp 65001` 让中文路径在重定向日志里保持 UTF-8；
- Hugo：`HUGO_EXE` → `where hugo` → `HUGO_FALLBACK`，并校验 Extended；
- Go：`GO_BIN` → `GO_FALLBACK` → `where go`，打印 `go version`；
- 端口：未显式 `PORT` 时从 `DEFAULT_PORT` 探测到 `PORT_MAX`（本机 8768 被另一个 Hugo 实例占用，实测顺延到 8769）；显式设置 `PORT` 时按指定端口启动且不打 busy 提示；
- `NO_OPEN=1` 不打开浏览器，`NO_PAUSE=1` 结束后不等待按键，便于脚本化验收。

实测（2026-10-29，`NO_OPEN=1 NO_PAUSE=1`，默认端口探测）：

```text
============================================================
 SILO 中文文档站 - Local Preview
============================================================
 Project : C:\Users\webtu\Desktop\silo文档站\oink-starter（官方文档--禁止修改，只可参考）
 URL     : http://127.0.0.1:8769/
 Stop    : Ctrl+C in this window
 Note    : port 8768 was busy, using 8769.

 Hugo    : D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe
           hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio
 Go      : C:\Users\webtu\tools\go1.27.3\go\bin\go.exe
go version go1.27.3 windows/amd64
 Note    : Go 1.27.3 or newer is required by go.mod.

Starting Hugo server without opening a browser...
```

Hugo 的构建输出随后出现，末尾为：

```text
Built in 19848 ms
Environment: "development"
Serving pages from disk
Web Server is available at http://localhost:8769/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

访问 `http://127.0.0.1:8769/` 实测 HTTP 200。显式 `PORT=8799` 也实测启动于 8799，且不再打印「8768 busy」提示。

### 手动构建

不经过 `run.cmd` 时：

```bash
cd "/c/Users/webtu/Desktop/silo文档站/oink-starter（官方文档--禁止修改，只可参考）"
export PATH="/c/Users/webtu/tools/hugo:/c/Users/webtu/tools/go1.27.3/go/bin:$PATH"
GOTOOLCHAIN=local GOPROXY=off hugo --cleanDestinationDir
```

实测输出（2026-10-29，非 minify，`--cleanDestinationDir`）：

```text
Start building sites …
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass

                  │  ZH
──────────────────┼──────
 Pages            │ 1022
 Paginator pages  │    0
 Non-page files   │    0
 Static files     │   34
 Processed images │    0
 Aliases          │    7
 Cleaned          │    0

Total in 21719 ms
```

判据：0 个 ERROR；WARN 只允许主题侧 `css.Sass: libsass was deprecated` 一条。

## 三、本地调试

优先双击 `run.cmd`：它会从 8768 起自动挑空闲端口（本机实测选 8769）。手动启动可用下面的等价命令（本测试用 8799）：

```bash
export PATH="/c/Users/webtu/tools/hugo:/c/Users/webtu/tools/go1.27.3/go/bin:$PATH"
GOTOOLCHAIN=local GOPROXY=off hugo server --bind 127.0.0.1 --port 8799 --renderToMemory --disableFastRender
```

实测输出（首轮）：

```text
Built in 19193 ms
Environment: "development"
Serving pages from memory
Web Server is available at http://localhost:8799/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

浏览器实测（Edge headless，同源 390px iframe，2026-10-29）：

| 项 | 实测 |
|----|------|
| 视口 | `innerWidth=390`、`clientWidth=375`、`scrollWidth=375`（375 = 390 减竖向滚动条，无横向溢出） |
| 样式表 | `document.styleSheets.length=3` |
| 默认预设 | `<html data-td-preset="paper">` |
| 预设选项 | paper / slate / ink / terminal 各 2 份（桌面与移动菜单），共 8 个 `data-td-preset-value` |
| 顶栏「文档」 | 4 条指向 `/docs/` 的链接（桌面、移动、首页按钮与卡片） |
| 预设切换 | slate → ink → terminal → paper；`localStorage['td-preset']` 依次为 slate / ink / terminal / null（null 表示回到站点默认） |
| 搜索索引 | `offline-search-index.zh.97657c....json` HEAD 200，`application/json` |
| 搜索查询 | 「安装」→「找到 10 条结果」；「silo」→ 10 条；范围切到「文档」→ 10 条，结果行 10 |
| 搜索面板 | 打开后 `#td-shell-search` 不再带 `hidden` |

一个截图坑：`msedge --headless=new --window-size=390,844 --screenshot` 得到的图可能按更宽的布局渲染后裁切，右侧文字像是溢出。判断横向溢出要用同源 390px iframe 读 `scrollWidth/clientWidth`，不要用这种截图下结论。

## 四、静态产物与打开方式

生产构建：

```bash
export PATH="/c/Users/webtu/tools/hugo:/c/Users/webtu/tools/go1.27.3/go/bin:$PATH"
GOTOOLCHAIN=local GOPROXY=off hugo --cleanDestinationDir --gc --minify \
  --environment production --printPathWarnings
```

实测输出（连续两次）：

```text
第一次：Pages 1022 / Static files 34 / Cleaned 2 / Total in 21220 ms
第二次：Pages 1022 / Static files 34 / Cleaned 0 / Total in 21332 ms
WARN 只有 css.Sass: libsass was deprecated 一条；--printPathWarnings 没有额外输出
```

产物口径（2026-10-29，minify + gc + production）：

```text
public/：1,078 个文件 / 115,533,517 字节
搜索索引：public/offline-search-index.zh.97657c1cdc67cd644db8538be9bd9af8.json（2,649,112 字节）
llms.txt：36,146 字节
_print/ 打印档：85 个 HTML
```

用 HTTP 打开（生产产物路由探针，`python -m http.server 8801 --directory public`）：

```text
/                                                        200  40811  text/html
/docs/                                                   200 200394  text/html
/docs/administration/batch-framework/                    200 203315  text/html
/offline-search-index.zh.97657c....json                  200 2649112 application/json
/llms.txt                                                200  36146  text/plain
/_print/docs/administration/batch-framework/             200  20112  text/html
/favicon.svg                                             200    378  image/svg+xml
/images/architecture/architecture-4-node-deploy.svg      404    335  text/html
/no-such-page/                                           404    335  text/html
```

图片 404 是克隆自带的已知内容缺口（见 README「已知内容缺口」），不是本次升级引入。

`file://` 双击 `public/index.html` 只能看到无样式文字：OINK 产物的 CSS/JS 带 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，会被浏览器按 CORS 拦截。完整功能必须走 HTTP。本轮未重测这一条，结论来自技能基线。

## 五、改站点标题与首页文案

| 要改什么 | 改哪里 | 生效位置 |
|----------|--------|----------|
| 站点名 | `hugo.yaml` 的 `title: &siteTitle`（当前仍是模板占位 `Project Name`） | 标签页、顶栏品牌、页脚 |
| 生产地址 | `hugo.yaml` 的 `baseURL`（当前仍是 `https://example.org/`） | canonical、RSS、sitemap、llms.txt |
| 顶栏入口 | 各根栏目 `_index.zh.md` 的 `menus.main`（`docs` / `blog` / `book`） | 全站顶栏 |
| 顶栏入口文字 | 同文件的 `linkTitle` / `title` | 全站顶栏与侧边栏 |
| 首页大标题、导语、按钮 | `data/home/zh.yaml` 的 `hero` | 首页 |
| 首页卡片 / CTA | 同文件的 `cards.items` / `cta` | 首页 |

当前 `data/home/zh.yaml` 仍是模板示例文案（「你的项目，清楚讲明白。」），`hugo.yaml` 的标题和地址也仍是 `Project Name` / `example.org`。这三处属于站点身份，不是主题升级能替你改的内容。

## 六、改图标与配图

| 要改什么 | 路径 | 生效位置 |
|----------|------|----------|
| 顶栏/页脚 logo | `assets/icons/logo.svg` | 全站品牌位 |
| 浏览器图标 | `static/favicon.svg` | 标签页、收藏夹 |
| 正文配图 | `static/images/...`，正文用 `/images/...` 引用 | 文章内 |

正文引用的 `images/architecture/*.svg` 等配图在克隆时没有随带，`static/` 目前只有 `favicon.svg`，所以这些图片是 404。新增配图请放进 `static/images/` 后用绝对路径引用；不要再引用上游的 `images/` 路径。

## 七、发布与分发

发布产物是 `public/` 整目录，至少包含：

- `public/offline-search-index.zh.<hash>.json`（离线搜索）
- `public/llms.txt`、`public/sitemap.xml`、`public/index.xml`
- `public/_print/`（打印档）
- `public/webfonts/`、`public/favicon.svg`、主题指纹化的 CSS/JS

上线前把 `hugo.yaml` 的 `baseURL` 改成真实域名并重新构建，否则 canonical、RSS、sitemap 与 `llms.txt` 里的绝对链接仍指向 `https://example.org/`。

子路径部署：当前 `baseURL` 是根域名 + `relativeURLs: true`，页面内资源用相对路径。若挂到 `https://host/silo/`，按技能基线（2026-10-26 实测）应把 `baseURL` 设为子路径并关闭 `relativeURLs`，否则相对链接会重复一次子路径段，CSS/JS 全部 404。本轮未复测该组合。

真实主机部署本轮未执行，见第 8 节。

## 八、交付判据与未验证项

| 判据 | 方法 | 本轮实测 |
|------|------|----------|
| 主题副本 | 与上游 v1.4.0 压缩包逐文件哈希比对 | 1,292/1,292，0 差异 |
| 启动脚本 | `run.cmd`（`NO_OPEN=1 NO_PAUSE=1`） | 默认从 8768 探测；8768 忙时选 8769 并打印 Note；中文横幅正常；`http://127.0.0.1:8769/` 返回 200；`Built in 19848 ms`；显式 `PORT=8799` 亦启动成功且无 busy 提示 |
| 标准构建 | `hugo --cleanDestinationDir` | Pages 1022 / Static 34 / Total 21719 ms，仅 1 条 WARN |
| 生产构建 | `hugo --cleanDestinationDir --gc --minify --environment production --printPathWarnings` | Cleaned 2 → 0；Total 21220 / 21332 ms；无 path warning |
| 产物路由 | 对 `public/` 起 HTTP，逐个 `curl` | 首页/文档/文章/搜索索引/llms/打印档/favicon 均 200；缺失配图与不存在路径 404 |
| 产物级链接 | 爬 `public/` 全部 HTML 的 href/src | 517 页 / 204,638 引用；CSS/JS 缺失 0；116 个唯一断链目标（页面 48、图片 68）；按引用次数 450 + 293 = 743，与 README 既有缺口一致 |
| 390px 布局 | 同源 iframe 探针 | `scrollWidth=clientWidth=375`，无横向溢出 |
| 预设与搜索 | headless Edge + 页面内点击 | 4 套预设可切换并写入 localStorage；搜索「安装」10 条、「silo」10 条、范围「文档」10 条 |
| `verify_site.py` | 技能统一验收 | 未运行：本仓库没有 `site.plan.json` 与技能骨架，脚本不适用 |
| `audit_content.py` | 结构/文体审计 | 未运行：没有计划文件；本站是上游 SILO 文档克隆，不是按技能计划生成的文章 |
| `check_links.py` | 以 `public/` 为判据 | 运行过但不适用：脚本把 `.zh.md` 源映射成 `page.zh/`，本站产物是 `page/`，全部报 UNMAPPED；改用上面的产物级爬取 |
| Mermaid 真解析 | `validate_mermaid.py` | 未运行：`content/` 中没有 mermaid 围栏 |
| 案例包判据 | `check_cases.py` | 未运行：本仓库没有 `cases/` |

## 未验证项汇总

| 项 | 状态 | 原因 |
|----|------|------|
| `run.cmd` 自动打开浏览器 | 未验证 | 测试使用 `NO_OPEN=1`，未走 `--openBrowser` 分支 |
| `run.cmd` 交互 `pause` | 未验证 | 测试使用 `NO_PAUSE=1`，未测结束后等待按键 |
| `HUGO_EXE` / `GO_BIN` 显式覆盖 | 未验证 | 本轮走 `where hugo` 与侧装 Go 自动回退；未单独测两个覆盖变量 |
| 真实主机/子路径部署 | 未验证 | 没有可用的部署目标；`baseURL` 仍为示例地址 |
| `file://` 完整功能 | 未验证（本轮未重测） | 技能基线已在 stock Edge 实测 CORS 拦截；本轮只走 HTTP |
| Firefox / Safari | 未验证 | 本轮只用 Edge headless |
| ink / terminal 逐页观感 | 未验证 | 只验证了预设切换与属性/存储，没有逐页人眼核对正文、表格、代码块对比度 |
| PlantUML 本地渲染 | 未验证 | 站点未启用 `params.plantuml`，`content/` 无 plantuml 围栏 |
| `.expand` 表格阅读器 | 未验证 | `content/` 没有使用 `.expand` / `.wide` 的表格 |
| blog gallery 视图 | 未验证 | `blog_index` 仍为 `cards`，未切换 gallery |
| 案例 zip 浏览器下载 | 未验证 | 本仓库没有案例包 |
