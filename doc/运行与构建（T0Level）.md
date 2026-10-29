# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。三条硬规矩：**每条命令都在本机跑过，并把真实输出原样贴进「实测输出」**；跑不了或没跑的显式写「未验证」+ 原因；不写想象中的命令与想象中的输出。环境数字标清口径：是否 minify、是否冷缓存、测的是本机还是静态服务器。

## 一、前置要求

| 工具 | 版本 | 本机路径 | 为什么必须是它 |
|------|------|---------|----------------|
| Hugo | `v0.168.0 ... +extended windows/amd64` | `C:\Users\webtu\tools\hugo\hugo.exe` | 主题用 SCSS，标准版编不了；OINK 1.4.0 的 `theme.toml` 要求 `min_version = "0.168.0"` |
| Go | `go1.27.3 windows/amd64` | `C:\Users\webtu\tools\go1.27.3\go\bin\go.exe` | 站点与主题两处 `go.mod` 都写 `go 1.27.3`；Go 低于它时模块命令直接失败，或触发联网下载工具链 |

本机 PATH 默认还放着两份更旧的 Go：`C:\Program Files\Go\bin\go.exe` 是 1.27.2，`C:\Users\webtu\tools\go\bin\go.exe` 是 1.25.4。1.27.2 的 `go version` 仍会打印版本号，但一碰模块就报：

```text
$ GOTOOLCHAIN=local GOPROXY=off "C:\Program Files\Go\bin\go.exe" list -m
go: go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)
```

1.25.4 在自动工具链模式下会尝试联网下载 1.27.3，离线机直接失败：

```text
go: downloading go1.27.3 (windows/amd64)
go: download go1.27.3: golang.org/toolchain@v0.0.1-go1.27.3.windows-amd64: Get "https://proxy.golang.org/golang.org/toolchain/@v/v0.0.1-go1.27.3.windows-amd64.zip": dial tcp 192.179.26.141:443: connectex: A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond.
```

本机正确版本：

```text
$ hugo version
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

$ "C:\Users\webtu\tools\go1.27.3\go\bin\go.exe" version
go version go1.27.3 windows/amd64
```

Git Bash 里这样把工具链排好：

```bash
cd "/c/Users/webtu/Desktop/Zookeeper文档站"
export PATH="/c/Users/webtu/tools/go1.27.3/go/bin:/c/Users/webtu/tools/hugo:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
```

`GOTOOLCHAIN=local` 禁止下载其他 Go 版本；`GOPROXY=off` 禁止模块走网络。这个站的主题是本地 `replace`，离线构建必须同时满足：`oink-main/oink-main/` 存在、`go.mod` 的 replace 指向它、实际执行的 Go ≥ 1.27.3。

主题副本已升到 OINK 1.4.0：1292 个文件 / 27,213,292 字节（`os.walk` 计数），含 `assets/third_party/plantuml/plantuml.js`、`assets/js/diagram.js`、`assets/js/table-reader.js`。`VENDOR.json` 的 29 个包 / 74 个工件 sha256 全部命中（`missing=0 hash_bad=0`）。技能自带的 `check-vendor.py` 还会比对 `trees[].sha256`，这条汇总哈希在技能源副本上就与文件树不一致；本轮以 74 条工件哈希 + 1292 文件逐字节一致为准，不修改 vendored 主题去迁就 manifest。

## 二、首次构建

```bash
export PATH="/c/Users/webtu/tools/go1.27.3/go/bin:/c/Users/webtu/tools/hugo:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir
```

实测输出（非 minify；本轮把 1.3.2 的 `resources/` 整体移到 `.tmp/resources-1.3.2`，按冷缓存重建）：

```text
Start building sites … 
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass

                  │ ZH  
──────────────────┼─────
 Pages            │ 155 
 Paginator pages  │   0 
 Non-page files   │   0 
 Static files     │  41 
 Processed images │   0 
 Aliases          │   0 
 Cleaned          │   0 

Total in 2647 ms
```

判据：**0 个 ERROR**；WARN 只允许主题侧 `css.Sass: libsass was deprecated` 这一条（1.4.0 明确禁止 `--panicOnWarning`）。产物在 `public/`，非 minify 档为 213 个文件、15,836,294 字节（`find public -type f | wc -l` 与 `du -sb public`）。搜索索引名为 `offline-search-index.zh.1b4874b4449c3566ad1862d9476d7a99.json`，643,891 字节；`public/index.html` 为 46,798 字节，`llms.txt` 为 11,634 字节。索引 51 条，每条新增 `section`/`sections`/`headings`/`breadcrumb` 字段；PlantUML 默认未启用，`public/` 的 HTML 里 `plantuml` 引用为 0。

## 三、本地调试

### 3.1 一键启动（run.cmd）

1.4.0 的 `run.cmd` 顶部是一段 PROJECT CONFIG：`SITE_TITLE`、`DEFAULT_PORT`、`PORT_MAX`、`HUGO_FALLBACK`、`GO_FALLBACK`、`GO_MIN_NOTE`。脚本先 `chcp 65001`、`cd /d "%~dp0"`，设置 `GOTOOLCHAIN=local` 与 `GOPROXY=off`；Hugo 按 `HUGO_EXE` → PATH → `%USERPROFILE%\tools\hugo\hugo.exe` 查找，Go 按 `GO_BIN` → `%USERPROFILE%\tools\go1.27.3\go\bin` → PATH 查找。默认从 `127.0.0.1:8768` 起服务，端口被占用时自动探测到 8787；显式 `set PORT=...` 则直接使用。

本次用 `NO_PAUSE=1`、`NO_OPEN=1`、`PORT=8803` 验证启动：

```text
============================================================
 ZooKeeper 文档
============================================================
 Project : C:\Users\webtu\Desktop\Zookeeper文档站
 URL     : http://127.0.0.1:8803/
 Stop    : Ctrl+C in this window

 Hugo    : D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe
           hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio
 Go      : C:\Users\webtu\tools\go1.27.3\go\bin\go.exe
go version go1.27.3 windows/amd64
 Note    : Go 1.27.3 or newer is required by go.mod.

Starting Hugo server without opening a browser...

 Pages            │ 155
 Static files     │  41

Built in 2428 ms
Environment: "development"
Web Server is available at http://localhost:8803/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

以上为实测输出摘录，省略 `Watching for changes` 两行与构建表中间行。另测自动换端口：保持 8768 被占用、不设 `PORT` 启动，脚本输出：

```text
 URL     : http://127.0.0.1:8769/
 Note    : port 8768 was busy, using 8769.
```

两种启动的根路径都返回 HTTP 200。`NO_PAUSE=1` 供脚本验证时跳过末尾 `pause`；`NO_OPEN=1` 跳过 `--openBrowser`。自动打开浏览器仍未单独验证（见未验证项）。

本机 PATH 里的 Hugo 是 `D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe`（与前置表里的 `C:\Users\webtu\tools\hugo\hugo.exe` 同为 0.168.0 extended），所以 `HUGO_FALLBACK` 不生效；Go 则相反，脚本优先用 1.27.3 的 fallback，PATH 里的 1.27.2 不会被选中。

### 3.2 启动与热重建

```bash
export PATH="/c/Users/webtu/tools/go1.27.3/go/bin:/c/Users/webtu/tools/hugo:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
hugo server --bind 127.0.0.1 --port 8770 --disableFastRender
```

实测启动段：

```text
Built in 1766 ms
Environment: "development"
Serving pages from disk
Web Server is available at http://localhost:8770/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

改一篇文章的 mtime 后，实测触发重建：

```text
Change detected, rebuilding site (#1).
2026-10-30 01:02:29.380 +0800
Source changed /docs/01-overview/认识zookeeper/why-zookeeper.md
WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass
Web Server is available at http://localhost:8770/ (bind address 127.0.0.1)
Total in 1074 ms
```

停止：在启动它的终端按 `Ctrl+C`。`hugo server` 是开发服务器，不要在发布环境用它代替静态服务器。

### 3.3 路由探针

对站点逐个请求（`hugo server` 的 `127.0.0.1:8770` 与 `python -m http.server` 的 `127.0.0.1:8766`），实测状态码与 Content-Type：

| 路径 | 状态码 | Content-Type |
|------|--------|--------------|
| `/` | 200 | `text/html; charset=utf-8` |
| `/docs/` | 200 | `text/html; charset=utf-8` |
| `/docs/01-overview/%E8%AE%A4%E8%AF%86ZooKeeper/architecture-and-data-model/` | 200 | `text/html; charset=utf-8` |
| `/docs/01-overview/%E8%AE%A4%E8%AF%86ZooKeeper/history-and-origins/` | 200 | `text/html; charset=utf-8` |
| `/docs/01-overview/%E8%AE%A4%E8%AF%86ZooKeeper/evolution-and-future/` | 200 | `text/html; charset=utf-8` |
| `/docs/06-dubbo-integration/架构与选型/dubbo-architecture/` | 200 | `text/html; charset=utf-8` |
| `/docs/07-dubbo-springboot-lab/工程蓝图/project-blueprint/` | 200 | `text/html; charset=utf-8` |
| `/images/zookeeper/zknamespace.jpg` | 200 | `image/jpeg` |
| `/offline-search-index.zh.1b4874b4449c3566ad1862d9476d7a99.json` | 200 | `application/json` |
| `/llms.txt` | 200 | `text/plain; charset=utf-8` |
| `/no-such-page-xyz/` | 404 | `text/html; charset=utf-8` |

01 的两篇历史文章、06 的 7 个 Dubbo 页面与 07 的 7 个实战页面在 `python -m http.server 8766 --directory public` 上逐个用 URL 编码请求，全部返回 200；中文字段由浏览器或 `urllib.parse.quote` 自动编码，不能把未编码的中文路径直接交给 `curl`。

### 3.4 浏览器实测

内核：Microsoft Edge `156.0.4314.42`（headless，CDP `Emulation.setDeviceMetricsOverride` 设真实视口；不是 `--window-size` 的近似值）。

1.4.0 起 Mermaid 改懒渲染：未接近视口时页面里是 `<pre class="td-mermaid-source">` 源码态，不是渲染失败；验收必须先把图滚进视口，等 `svg` 出现再判。

| 项目 | 1.4.0 实测 |
|------|------------|
| 顶栏 | 首页与文档页均有「文档」入口（`href="./docs/"`）；文档页带 `active` |
| 首页 1280×900 | `title="ZooKeeper 文档"`，`h1="把分布式协调讲清楚"`，`data-td-preset="paper"`，`scrollWidth=1265` |
| 含 Mermaid 的 30 页，1280×900 | 共 70 个图块；逐页逐图 `scrollIntoView` 后 70/70 出 SVG，错误 0；未滚动前历史页 4 个图块 SVG=0、源码块=4 |
| 含 Mermaid 的 30 页，390×844 | 同样 70/70 出 SVG，错误 0；`horizontalOverflow=0` |
| 01 历史页 1280/390 | 4 个图块、8 个表格、5 个代码块、4 个「💡 新人小结」；两档均 4/4 SVG，`scrollWidth` 1265/390 |
| 搜索 | 索引 51 条，字段含 `section`/`sections`/`headings`/`breadcrumb`；「Chubby」找到 2 条；范围控件显示「搜索范围 / 全部栏目 / ZooKeeper 文档」 |
| Appearance | 4 个预设（paper/slate/ink/terminal）；切 Slate 后 `data-td-preset="slate"`、`localStorage['td-preset']="slate"`；切回 Paper 后 `preset="paper"`、存储键删除 |
| 控制台/网络 | 0 个 console error、0 个 loadingFailed、0 个 PlantUML 请求 |
| PlantUML | 默认 `params.plantuml.enable=false`；`public/` HTML 中 plantuml 引用 0，未加载 3.36 MB 运行时 |

一个坑：搜索面板首次打开显示加载状态，索引没读完就输入会得到空结果或旧结果；等状态消失再输查询。

## 四、静态产物与打开方式

### 4.1 两档产物的体积

非 minify（上面「首次构建」那一档）：

```text
files=213  bytes=15836294
```

发布档：

```bash
export PATH="/c/Users/webtu/tools/go1.27.3/go/bin:/c/Users/webtu/tools/hugo:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir --gc --minify
```

实测输出末尾与产物：

```text
 Pages            │ 155
 Static files     │ 41
 Total in 3413 ms
```

```text
files=213  bytes=14960528  index_html=40938
search=OK llms=OK
```

minify 只减少 875,766 字节（约 5.53%），因为体积大头是 `third_party/mermaid/mermaid.min.581ed7d7….js`（3,572,661 字节），它已经被主题预压缩。`index.html` 为 40,938 字节；搜索索引（643,891 字节）与 `llms.txt`（11,634 字节）在 minify 档实测存在。`data-td-preset=paper` 在 minified HTML 中存在；1.4.0 的 `js/chunks/diagram.min.<hash>.js` 也在产物里；PlantUML 未启用，`public/` 没有 `third_party/plantuml/`。

minify 目录本轮只做了体积与关键标记检查，没有单独对它重跑 `verify_site.py --skip-build`；完整交互回归仍在非 minify 档跑。

### 4.2 relativeURLs 的实证

`hugo.yaml` 的 `relativeURLs: true` 让页面内资源走相对路径。实测产物：

```text
# public/index.html
data-td-index-src="./offline-search-index.zh.1b4874b4449c3566ad1862d9476d7a99.json"
href="./favicon.svg"

# public/docs/01-overview/认识ZooKeeper/architecture-and-data-model/index.html
data-td-index-src="../../../../offline-search-index.zh.1b4874b4449c3566ad1862d9476d7a99.json"
src="../../../../images/zookeeper/zknamespace.jpg"
```

深页面的搜索索引和图片都自动补了 `../../../../`，所以整目录挂到任意子路径都能找到资源。

### 4.3 双击打开的真实边界

本机用 Edge `file:///C:/Users/webtu/Desktop/Zookeeper%E6%96%87%E6%A1%A3%E7%AB%99/public/index.html` 实测：

- 页面能打开，`title`、`h1` 和 `data-td-preset` 都在，文字内容可读；
- 但主题给 CSS/JS 链接同时写了 `integrity` 与 `crossorigin="anonymous"`，`file://` 的 origin 是 `null`，浏览器按 CORS 拦截：

```text
Access to CSS stylesheet at 'file:///.../scss/main.min.<hash>.css' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: ...
Access to script at 'file:///.../js/chunks/mermaid-zh.min.<hash>.js' from origin 'null' has been blocked by CORS policy: ...
```

结果是双击打开时页面**没有样式、Mermaid 不渲染（实测 `mermaidSvgs=0`）、离线搜索 fetch 直接 `Failed to fetch`**。所以：

- 只做纯文本粗略预览：双击 `public/index.html` 可以；
- 要完整使用导航、搜索、Mermaid、外观切换：必须通过 HTTP 打开，例如

```bash
python -m http.server 8766 --directory public
# 浏览器打开 http://127.0.0.1:8766/
```

这不是站点内容错误，是浏览器对 `file://` + CORS 的安全限制；发布到 HTTP 服务器后全部功能正常。

## 五、改站点标题与首页文案

站点身份的唯一源数据是 `site.plan.json` 的 `site` 段；改完重跑生成器，不要只手改 `hugo.yaml`。

| 要改什么 | 改哪里 | 生效位置 |
|----------|--------|----------|
| 站点名 | `site.plan.json` 的 `site.title`，重跑 `plan_site.py` | `hugo.yaml` 的 `title`/`languages.zh.title`、浏览器标签页、顶栏/侧边栏品牌 |
| 顶栏「文档」入口 | `hugo.yaml` 的 `menus.main`（`identifier: docs`、`pageRef: /docs`） | 首页、文档总览和文章页的顶栏；由 `plan_site.py` 生成，重跑计划会保留 |
| 首页大标题、导语、按钮 | `data/home/zh.yaml` 的 `hero` | 首页 |
| 首页卡片与 CTA | 同文件 `cards.items`、`cta` | 首页 |
| 文档总览卡片 | `content/docs/_index.md` 的链接列表与 `{.cards}` | `/docs/` |
| 侧边栏分类文字 | 各一级分类 `_index.md` 的 `linkTitle`/`description`/`icon` | 侧边栏与分类页 |
| 文章标题与摘要 | 文章 front matter 的 `title`/`description` | 文章页、侧边栏、卡片、SEO |

本轮把站点名定为 `ZooKeeper 文档`。更长的 `ZooKeeper 中文文档` 在 1280px 宽的侧边栏里会把最后一个字挤到第二行；如果必须用长名字，先测 1280px 侧边栏，不要只看 1920px。

顶栏的 `menus.main` 由 `plan_site.py` 写入模板并随每次生成保留，不在 `site.plan.json` 的 schema 里；不要手删。本轮实测：生成后首页出现 73×36 的「文档」tab，点击进入 `/docs/`，文章页该 tab 带 `active`；`verify_site.py` 的 `nav` 判据会检查产物里的入口。

常见半改：只改 `hugo.yaml` 不改 `data/home/zh.yaml`，首页 hero 仍是旧的；或者手改 `_index.md` 后重跑 `plan_site.py`，手改被覆盖。以计划文件为准。

## 六、图标与配图

| 资产 | 位置 | 现状与改法 |
|------|------|------------|
| 导航栏 logo | 站点 `assets/icons/logo.svg`（415 字节，与 favicon 同图案） | 当前已生效：主题按默认路径 `icons/logo.svg` 查找，站点 `assets/` 的同名文件覆盖主题资产；替换这个文件即可换 logo，或设置 `params.logo` 指向别的路径 |
| favicon | `static/favicon.svg`（378 字节，本站自制） | 构建后复制到 `public/favicon.svg`；主题的 favicons partial 会自动引用 |
| 分类图标 | `content/docs/01-overview/_index.md` 等七个分类页的 `icon:` | 当前分别是 `fa-solid fa-compass`、`fa-solid fa-rocket`、`fa-solid fa-server`、`fa-solid fa-book-open`、`fa-solid fa-circle-question`、`fa-solid fa-plug`、`fa-solid fa-flask`；改 class 即可，字体由主题本地提供 |
| 正文配图 | `static/images/zookeeper/*.jpg` | 正文用 `/images/zookeeper/<文件名>` 引用；Hugo 会改写成相对路径。当前只引用了 `zknamespace.jpg`，其余四张是发行包原图，保留备用 |
| 许可文件 | `static/licenses/apache-zookeeper-LICENSE.txt`、`NOTICE.txt` | 与发行包逐字节一致，随站分发；图片均来自 Apache ZooKeeper 3.8.7 发行包 `docs/images/`，Apache-2.0 |

复核图片与许可来源：

```bash
md5sum "D:/ZK/apache-zookeeper-3.8.7-bin/apache-zookeeper-3.8.7-bin/docs/images/zknamespace.jpg" \
       static/images/zookeeper/zknamespace.jpg
cmp -s "D:/ZK/apache-zookeeper-3.8.7-bin/apache-zookeeper-3.8.7-bin/LICENSE.txt" \
       static/licenses/apache-zookeeper-LICENSE.txt && echo LICENSE_SAME
cmp -s "D:/ZK/apache-zookeeper-3.8.7-bin/apache-zookeeper-3.8.7-bin/NOTICE.txt" \
       static/licenses/apache-zookeeper-NOTICE.txt && echo NOTICE_SAME
```

正文引用了不存在的图片时，`audit_content.py` 会报 `BROKEN_IMAGE`；图片文件名不要带空格、`#`、`?`，中文目录由 Hugo 自动做百分号编码（例如 `认识ZooKeeper` 变成 `%E8%AE%A4%E8%AF%86ZooKeeper`）。

## 七、发布与分发

发布档命令：

```bash
export PATH="/c/Users/webtu/tools/hugo:/c/Program Files/Go/bin:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir --gc --minify
```

必须整目录分发 `public/`，不要只拷 HTML。离线搜索依赖根目录的 `offline-search-index.zh.<hash>.json`（本机 643,891 字节），Mermaid 依赖 `third_party/mermaid/`，样式与字体在 `scss/`、`webfonts/`，图标在 `assets` 产物与 `favicon.svg`，整节打印档在 `_print/`，另有 `llms.txt`、`sitemap.xml`、`robots.txt`。

部署前把 `hugo.yaml` 的 `baseURL`（当前占位值 `https://example.org/`）改成真实地址，否则 canonical、RSS、`sitemap.xml` 和 `llms.txt` 里的绝对链接仍指向示例域名。`relativeURLs: true` 让浏览和资源在任意子路径下都能工作，但**不能**替你把上述绝对元数据改对。

搜索必须通过 HTTP/HTTPS 访问；`file://` 下浏览器会拦掉索引 fetch（见 4.3）。本机没有做真实域名、HTTPS、CDN 或反向代理部署，相关项在「未验证项汇总」中列出。

## 八、交付判据与未验证项

| 脚本 | 判据 | 本轮实测 |
|------|------|----------|
| `verify_site.py --selftest` | 判据本身先证明会红 | 末行 `SELFTEST_PASS` |
| `verify_site.py --mode full` | 统一验收：plan/scaffold/build/preset/nav/audit/links/delivery | 最终汇总见下方代码块 |
| `audit_content.py --mode full --min-lines 260` | 结构、front matter、文体门槛 | `articles=30 expected=30 dirs=21 stubs=0 problems=0 mode=full genre_checks=11` |
| `check_links.py --site .` | 以 `public/` 为判据的站内链接 | `links_checked=66 external_or_anchor=0 home_urls=10 broken=0 unmapped=0 uglyURLs=False lowercase=True` |
| `validate_mermaid.py` | 生成 Mermaid 解析台；浏览器逐块 `MERMAID.parse()` 才算法真解析 | 生成 72 个块（70 真实 + 2 自测）；Edge 读回 `TOTAL=70 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS` |

最终统一验收命令：

```bash
python "C:/Users/webtu/.qoder-cn/skills/oink-doc-site/scripts/verify_site.py" \
  --site . --plan site.plan.json --mode full \
  --hugo "C:/Users/webtu/tools/hugo/hugo.exe" \
  --go-bin "C:/Users/webtu/tools/go1.27.3/go/bin" \
  --report doc/验收汇总.md
```

实测输出：

```text
判据             类别      状态         摘要
plan           AUTO    PASS       categories=7 sections=13 articles=30 problems=0
scaffold       AUTO    PASS       theme_files=1292 placeholders=0 preset=paper run_cmd=ok
build          BUILD   PASS       Pages=155 Static files=41 ERROR=0 rc=0
preset         BUILD   PASS       data-td-preset=paper menu=list:4
nav            BUILD   PASS       顶栏「文档」入口存在
audit          AUTO    PASS       articles=30 expected=30 problems=0 mode=full genre_checks=11
links          AUTO    PASS       links_checked=66 broken=0 unmapped=0 home_urls=10
mermaid        MANUAL  GENERATED  blocks=72 out=C:\Users\webtu\Desktop\Zookeeper文档站\_mermaid-harness；需按脚本三步在浏览器读回 REAL_FAIL=0
delivery_doc   AUTO    PASS       doc/运行与构建（T0Level）.md 已落地
source_ledger  MANUAL  PRESENT    doc/内容来源.md 已存在，需人工核对来源是否覆盖全部事实
FAIL=0 MANUAL=2 PASS=8 SKIP=0
```

`mermaid` 与 `source_ledger` 在统一验收里是 MANUAL/GENERATED 或 PRESENT，不是 PASS：Mermaid 要按上面的真解析读数人工确认 `REAL_FAIL=0`；`doc/内容来源.md` 要人工核对是否覆盖全部事实。本轮来源清单已按 30 篇更新：新增 01 两篇历史文章的官方发布页、Release Notes、安全公告、董事会纪要与论文来源，并把命名趣闻、Observer 引入版本、早期版本日期、3.10 路线图与 Kafka 迁移等未验证项单独列出。

Mermaid 的复现方式：先跑 `python validate_mermaid.py --site . --out _mermaid-harness --selftest` 生成解析台，按 stdout 给的三步起本地 HTTP 服务、用浏览器打开 `index.html`、读回 `#out` 与 `window.__HEADLINE`。命令行退出码只证明夹具生成成功；`REAL_FAIL=0` 必须来自浏览器页内 `MERMAID.parse()` 的读数。本机用 Edge 156.0.4314.42 headless 读回 `TOTAL=70 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`，`HEADLINE=GREEN`。01 新增 8 个历史图、06 的 15 个 Dubbo 图与 07 的 22 个实战图都包含在这 70 个真实块里。

## 未验证项汇总

| 项 | 状态 | 原因 |
|----|------|------|
| OINK 1.4.0 的 VENDOR tree digest | 已知偏差 | 74 个工件 sha256 全部命中；`check-vendor.py` 的 `trees[].sha256` 在技能源副本上也与文件树不一致，本轮不修改 vendored 主题 |
| 真实域名、HTTPS、CDN、反向代理 | 未验证 | 只在 `127.0.0.1:8766` 的 HTTP 静态服务与 `file://` 下测试，没有可用的发布目标 |
| ink / terminal 两套实验预设的逐页可读性 | 未验证 | 验证了菜单存在与切换机制，没有逐页人眼核对正文、代码块、表格的对比度 |
| minify 档的完整交互回归 | 未验证 | 只验证了构建、文件存在与体积；交互回归在非 minify 档跑 |
| `--panicOnWarning` 严格闸门 | 禁用项 | 1.4.0 主题契约明确禁止在任何 build/checker/preview/CI 里开启；LibSass WARN 保持可见 |
| `run.cmd` 自动打开浏览器 | 未验证 | 自动换端口 8768→8769 已实测；`NO_OPEN=1` 只验证服务启动，没有验证 `--openBrowser` 是否拉起系统默认浏览器 |
| 1.4.0 PlantUML 本地渲染 | 未启用/未验证 | 默认 `params.plantuml.enable=false`；本轮只验证产物 0 引用，没有开启并渲染 PlantUML |
| 1.4.0 表格阅读器 `.expand`/`.wide` | 未验证 | 站点正文没有使用这两个作者侧标记；只确认主题资产与脚本存在 |
| 1.4.0 搜索范围筛选的键盘流 | 部分验证 | 控件与「Chubby」检索已验证；没有逐项走键盘/读屏 |
| AdminServer 所有 `/commands/*` 端点 | 未逐一验证 | 本机请求了 `/commands`、`/commands/stat`、`/commands/ruok`、`/commands/mntr`（均 200 JSON）；其余端点正文只引用官方 Admin 文档，没有逐个请求 |
| 远程 JMX / 1099 端口 | 未验证 | 本机未配置远程 JMX；正文只写官方文档支持的本地/远程差异，并明确 1099 是常见约定而非 ZooKeeper 固定默认值 |
| 第三方监控工具生态占比 | 未量化 | 问答实录里的“主流/少数派”是经验判断，没有官方统计；正文只保留按端口/URL 判断通道的方法 |
| `SnapshotComparer`、`zkCleanup`、`zkServer-initialize` | 未验证 | 内容侧未在本机执行，正文已明确标注；参数来自官方 Tools/脚本 |
| Dubbo + ZooKeeper 三节点 ensemble | 未验证 | 06 与 07 的 Dubbo 实验都使用 standalone 2182；没有复测 3 节点 ZK 的注册、选主与多数派丢失 |
| Dubbo Admin / Monitor / Prometheus | 未验证 | 本地工程未部署管理端与监控，正文只说明角色与端口 |
| Nacos / etcd / Consul / Redis 注册中心 | 未验证 | 对比表只比较机制，没有搭环境做功能或性能对比 |
| Dubbo 优雅停机与节点删除时序 | 未验证 | 实验使用强制终止；正文区分“正常注销”与“会话超时”，但没有实测优雅停机 |
| ZooKeeper ACL / TLS / SASL | 未验证 | 实验 ZK 未开启认证与加密 |
| Dubbo 压测、连接池与线程池调优 | 未验证 | 没有并发/容量测试；“最优参数”不在本站结论范围内 |
| 07 实战“从空目录逐条执行”的完整终端录像 | 未留存 | 07 以本地 `dubbo-flow-springboot` 为最终参考实现重写；正文只引用可回查的产物与日志，没有保存从空目录逐条敲命令的完整记录 |
| 完全离线 Maven 构建 | 已实测失败 | 本地 Maven 缓存缺少部分 Spring BOM，需联网补齐依赖；正文不把离线构建当默认路径 |
| Java 8 / Java 21 双 JDK 构建矩阵 | 未验证 | 构建 JVM 为 Dragonwell 21、`java.version=1.8`，运行 JVM 为 Dragonwell 8；没有用两套 JDK 各构建一次并比对产物 |
| 实战工程的 Linux/macOS 启动方式 | 未验证 | 命令与路径按本机 Windows + Git Bash 记录，没有在 Linux/macOS 上验证脚本、路径分隔符与进程管理 |
| ZooKeeper 命名趣闻的每一句对话 | 社区口径 | 在《从 Paxos 到 ZooKeeper》与多篇社区文章中出现；没有找到 Apache 一手记录，正文标为趣闻 |
| Observer 是否恰好在 3.3.0 引入 | 社区口径 | 官方 3.3.0 Release Notes 页面当前不可直接访问；官方 3.4 发行包已把 Observer 作为既有角色，正文按“3.3 线出现”并加注 |
| 3.4–3.9 每个版本的官方公告日 | 部分未验证 | 时间线用 Maven Central 制品时间排序，已注明不等于官方公告日；没有逐个翻邮件列表公告 |
| 3.10 的发布时间与功能范围 | 未验证 | 只能确认 master POM 为 `3.10.0-SNAPSHOT`、仓库存在 3.9.7/3.8.8 维护分支；官方发布页没有 3.10，正文不写日期或功能承诺 |
| Kafka 4.0 的迁移步骤与收益数字 | 未验证 | 只引用官方公告的定性描述；没有在本机搭 Kafka 4.0 集群或复现迁移、性能数据 |
| 历史文章中的未来方向判断 | 作者判断 | 基于公开版本线、仓库状态与 Kafka 4.0 公告的推断，不是 Apache 官方路线图；正文已标注 |
| Safari、Firefox、移动端真机 | 未验证 | 本机只有 Edge 156.0.4314.42 的 headless 环境；390px 是 CDP 模拟视口，不是真机 |
| `file://` 下的完整功能 | 已实测为不可用 | CSS/JS 被 CORS 拦截，页面无样式、Mermaid 0 个、搜索 fetch 失败；完整使用请走 HTTP |
