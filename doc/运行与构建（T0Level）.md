# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。三条硬规矩：**每条命令都在本机跑过，并把真实输出原样贴进「实测输出」**；跑不了或没跑的显式写「未验证」+ 原因；不写想象中的命令与想象中的输出。环境数字标清口径：是否 minify、是否冷缓存、测的是本机还是静态服务器。

## 一、前置要求

| 工具 | 版本 | 本机路径 | 为什么必须是它 |
|------|------|---------|----------------|
| Hugo | `v0.168.0 ... +extended windows/amd64` | `C:\Users\webtu\tools\hugo\hugo.exe` | 主题用 SCSS，标准版编不了；`theme.toml` 要求 `min_version = "0.166.0"` |
| Go | `go1.27.2 windows/amd64` | `C:\Program Files\Go\bin\go.exe` | `go.mod` 的 `go` 指令是 `1.27.0`，Go 必须不小于它，否则会尝试联网下载工具链 |

本机还有一份旧 Go 在 `C:\Users\webtu\tools\go\bin\go.exe`。它是 `go1.25.4`，不要用；把它排在 PATH 前面时，`GOTOOLCHAIN=local` 也压不住 `go.mod` 的版本要求，实测会去下载 `go1.27.0`：

```text
$ go version
go: downloading go1.27.0 (windows/amd64)
go: download go1.27.0: golang.org/toolchain@v0.0.1-go1.27.0.windows-amd64: Get "https://proxy.golang.org/golang.org/toolchain/@v/v0.0.1-go1.27.0.windows-amd64.zip": dial tcp 142.250.69.177:443: connectex: A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond.
```

本机正确版本：

```text
$ hugo version
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

$ "C:\Program Files\Go\bin\go.exe" version
go version go1.27.2 windows/amd64
```

Git Bash 里这样把工具链排好（`C:\Program Files\Go\bin` 要带引号，路径含空格）：

```bash
cd "/c/Users/webtu/Desktop/Zookeeper文档站"
export PATH="/c/Users/webtu/tools/hugo:/c/Program Files/Go/bin:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
```

`GOTOOLCHAIN=local` 禁止下载其他 Go 版本；`GOPROXY=off` 禁止模块走网络。这个站的主题是本地 `replace`，离线构建必须同时满足：`oink-main/oink-main/` 存在、`go.mod` 的 replace 指向它、Go 版本不低于 `go.mod` 要求。

## 二、首次构建

```bash
export PATH="/c/Users/webtu/tools/hugo:/c/Program Files/Go/bin:$PATH"
export GOTOOLCHAIN=local GOPROXY=off
hugo --cleanDestinationDir
```

实测输出（非 minify；`resources/` 资源缓存已存在，不是冷缓存）：

```text
Start building sites … 
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio

WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass

                  │ ZH 
──────────────────┼────
 Pages            │ 155 
 Paginator pages  │  0 
 Non-page files   │  0 
 Static files     │ 41 
 Processed images │  0 
 Aliases          │  0 
 Cleaned          │  0 

Total in 2301 ms
```

判据：**0 个 ERROR**；WARN 只允许主题侧 `css.Sass: libsass was deprecated` 这一条。产物在 `public/`，非 minify 档为 212 个文件、15,557,180 字节（`find public -type f | wc -l` 与 `du -sb public`）。搜索索引名为 `offline-search-index.zh.9da284adbe9aa9d52dc86e3914a2c448.json`，547,044 字节；`public/index.html` 为 45,794 字节，`llms.txt` 为 11,634 字节。

## 三、本地调试

### 3.1 启动与热重建

```bash
hugo server --bind 127.0.0.1 --port 8770 --disableFastRender
```

实测启动段：

```text
Built in 826 ms
Environment: "development"
Serving pages from disk
Web Server is available at http://localhost:8770/ (bind address 127.0.0.1) 
Press Ctrl+C to stop
```

改一篇文章的 mtime 后，实测触发重建：

```text
Change detected, rebuilding site (#1).
2026-10-25 21:15:02.809 +0800
Source changed /docs/01-overview/认识zookeeper/why-zookeeper.md
...
Total in 391 ms
```

停止：在启动它的终端按 `Ctrl+C`。`hugo server` 是开发服务器，不要在发布环境用它代替静态服务器。

### 3.2 路由探针

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
| `/offline-search-index.zh.9da284adbe9aa9d52dc86e3914a2c448.json` | 200 | `application/json` |
| `/llms.txt` | 200 | `text/plain; charset=utf-8` |
| `/no-such-page-xyz/` | 404 | `text/html; charset=utf-8` |

01 的两篇历史文章、06 的 7 个 Dubbo 页面与 07 的 7 个实战页面在 `python -m http.server 8766 --directory public` 上逐个用 URL 编码请求，全部返回 200；中文字段由浏览器或 `urllib.parse.quote` 自动编码，不能把未编码的中文路径直接交给 `curl`。

### 3.3 浏览器实测

内核：Microsoft Edge `156.0.4314.42`（headless，CDP `Emulation.setDeviceMetricsOverride` 设真实视口；不是 `--window-size` 的近似值）。

| 页面 | 实测 |
|------|------|
| 顶栏（首页/文档页） | `.td-nav-menu-zone` 有 1 个「文档」tab，1280px 下尺寸 73×36；点击进入 `/docs/`；文档页该 tab 带 `active` |
| 首页 1280×900 | `title="ZooKeeper 文档"`，`h1="把分布式协调讲清楚"`，`innerWidth=1280`，`documentElement.scrollWidth=1265`，`data-td-preset="paper"` |
| 文档总览 1280×900 | `title="文档 | ZooKeeper 文档"`，`h1="文档"`，站内 `a[href*="/docs/"]` 75 个，文档卡片 7 个，`scrollWidth=1265` |
| 架构文章 1280×900 | 5 个 Mermaid SVG，0 个 Mermaid 错误；11 个表格；`scrollWidth=1265` |
| 架构文章 390×844 | `innerWidth=390`，`docScrollWidth=390`，`horizontalOverflow=false`；5 个 Mermaid、11 个表格、12 个代码块、10 个「💡 新人小结」 |
| 新增 6 页 1280×900 | FAQ、AdminServer、4lw、四条监控通道、端口地图、管理面收口：全部 `scrollWidth=1265`、无横向溢出；Mermaid 分别为 1/1/1/2/1/1 个，错误 0；表格 13/6/9/10/9/6 个；导航 tab 全部 `active`；FAQ 的 16 个站内链接覆盖全部 5 篇专题文档 |
| 新增 7 页 1280×900 | Dubbo 架构、为什么推荐 ZooKeeper、运行时架构、注册发现全流程、生效原理、节点数据、Spring Boot 集成：全部 `scrollWidth=1265`、`horizontalOverflow=false`；Mermaid 分别为 3/3/3/2/2/1/1 个，缺失 0；表格 6/6/8/5/3/8/8 个；导航 tab 全部 `active` |
| Dubbo 架构 390×844 | `innerWidth=390`，`docScrollWidth=390`，`horizontalOverflow=false`；3 个 Mermaid、6 个表格、6 个代码块、4 个「💡 新人小结」 |
| 07 实战 7 页 1280×900 | 工程蓝图、Maven 骨架、契约、ZooKeeper 配置、提供者、消费者、构建排障：全部 `horizontalOverflow=false`、Mermaid 缺失 0；Mermaid 分别为 6/2/2/2/2/3/5 个（合计 22）；表格 9/5/7/8/8/7/10 个；代码块 3/9/11/10/9/6/13 个；导航 tab 全部 `active` |
| 07 工程蓝图 390×844 | `innerWidth=390`，`docScrollWidth=390`，`horizontalOverflow=false`；6 个 Mermaid、9 个表格、3 个代码块、4 个「💡 新人小结」 |
| 01 历史 2 页 1280×900 | 前生、今世与未来：均 `scrollWidth=1265`、`horizontalOverflow=false`、Mermaid 4 个且错误 0；表格 8/10 个、代码块 1/1 个、「💡 新人小结」4/5 个；导航 tab 全部 `active` |
| 01 历史 2 页 390×844 | 两页均 `innerWidth=390`、`docScrollWidth=390`、`horizontalOverflow=false`；各 4 个 Mermaid、0 个错误；表格 8/10 个、代码块 1/1 个、「💡 新人小结」4/5 个 |
| FAQ 390×844 | `innerWidth=390`，`scrollWidth=390`，`horizontalOverflow=false`；1 个 Mermaid、13 个表格、14 个「💡 新人小结」 |
| 搜索「Dubbo 实战」/「动态引用」/「端口」 | 状态栏分别显示「找到 2 条结果」「找到 10 条结果」「找到 10 条结果」；索引文件 547,044 字节、51 条记录，首次打开搜索面板要等加载态结束再输入 |
| Appearance | 导航栏与抽屉里的外观菜单各有一组选项，预设值共 4 个（paper/slate/ink/terminal）；切到 Slate 后 `<html data-td-preset="slate">` 且 `localStorage['td-preset']="slate"`；切回 Paper 后 `preset="paper"` 且存储键被删除（`stored=null`） |

一个坑：搜索面板首次打开显示加载状态，索引没读完就输入会得到空结果或旧结果；等状态消失再输查询。

## 四、静态产物与打开方式

### 4.1 两档产物的体积

非 minify（上面「首次构建」那一档）：

```text
files=212  bytes=15557180
```

发布档：

```bash
hugo --cleanDestinationDir --gc --minify
```

实测输出末尾与产物：

```text
 Pages            │ 155 
 Static files     │ 41 
 Total in 2268 ms
```

```text
files=212  bytes=14699229  index_html=40146
search=OK llms=OK
```

minify 只减少 857,951 字节（约 5.52%），因为体积大头是 `third_party/mermaid/mermaid.min.581ed7d7….js`（3,572,661 字节），它已经被主题预压缩。`public/index.html` 仍是 40,146 字节；搜索索引（547,044 字节）与 `llms.txt`（11,634 字节）在 minify 档实测存在。

minify 产物上的判据也单独跑过（`--skip-build`，所以 build 为 SKIP）：

```text
preset         BUILD   PASS       data-td-preset=paper menu=list:4
nav            BUILD   PASS       顶栏「文档」入口存在
FAIL=0 MANUAL=2 PASS=7 SKIP=1
```

Hugo `--minify` 会把 `data-td-preset="paper"`、`href="./docs/"` 这类简单属性值去掉引号；`verify_site.py` 的 preset/nav 判据已同时接受带引号与去引号两种形态。

### 4.2 relativeURLs 的实证

`hugo.yaml` 的 `relativeURLs: true` 让页面内资源走相对路径。实测产物：

```text
# public/index.html
data-td-index-src="./offline-search-index.zh.9da284adbe9aa9d52dc86e3914a2c448.json"
href="./favicon.svg"

# public/docs/01-overview/认识ZooKeeper/architecture-and-data-model/index.html
data-td-index-src="../../../../offline-search-index.zh.9da284adbe9aa9d52dc86e3914a2c448.json"
src="../../../../images/zookeeper/zknamespace.jpg"
```

深页面的搜索索引和图片都自动补了 `../../../../`，所以整目录挂到任意子路径都能找到资源。

### 4.3 双击打开的真实边界

本机用 Edge `file:///C:/Users/webtu/Desktop/Zookeeper%E6%96%87%E6%A1%A3%E7%AB%99/public/index.html` 实测：

- 页面能打开，`title`、`h1` 和 `data-td-preset` 都在，文字内容可读；
- 但主题给 CSS/JS 链接同时写了 `integrity` 与 `crossorigin="anonymous"`，`file://` 的 origin 是 `null`，浏览器按 CORS 拦截：

```text
Access to CSS stylesheet at 'file:///.../scss/main.min.dc8890df....css' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: ...
Access to script at 'file:///.../js/chunks/mermaid-zh.min.c45255dd....js' from origin 'null' has been blocked by CORS policy: ...
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

必须整目录分发 `public/`，不要只拷 HTML。离线搜索依赖根目录的 `offline-search-index.zh.<hash>.json`（本机 547,044 字节），Mermaid 依赖 `third_party/mermaid/`，样式与字体在 `scss/`、`webfonts/`，图标在 `assets` 产物与 `favicon.svg`，整节打印档在 `_print/`，另有 `llms.txt`、`sitemap.xml`、`robots.txt`。

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
  --go-bin "C:/Program Files/Go/bin" \
  --report doc/验收汇总.md
```

实测输出：

```text
判据             类别      状态         摘要
plan           AUTO    PASS       categories=7 sections=13 articles=30 problems=0
scaffold       AUTO    PASS       theme_files=1273 placeholders=0 preset=paper
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
| 冷缓存首次构建耗时 | 未验证 | 本轮构建复用了 `resources/` 缓存；`--cleanDestinationDir` 只清 `public/`，没有清 Hugo 资源缓存 |
| 真实域名、HTTPS、CDN、反向代理 | 未验证 | 只在 `127.0.0.1:8766` 的 HTTP 静态服务与 `file://` 下测试，没有可用的发布目标 |
| ink / terminal 两套实验预设的逐页可读性 | 未验证 | 验证了菜单存在与切换机制，没有逐页人眼核对正文、代码块、表格的对比度 |
| minify 档的完整交互回归 | 未验证 | 只验证了构建、文件存在与体积；交互回归在非 minify 档跑 |
| `--panicOnWarning` 严格闸门 | 未验证 | 主题侧 libsass WARN 会触发失败，本轮按主题契约没有启用该闸门 |
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
