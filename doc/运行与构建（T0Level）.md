# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。下面每条命令都在本机（Windows 11 10.0.26300，Git Bash + PowerShell 双通道）实跑过，「实测输出」代码块是原样回贴；跑过但结果依赖环境的，标了口径；没跑的写在最后的「未验证项汇总」里，不当作已成立。

本工程的八节按 Hugo 文档站做了映射（映射理由见每节标题括注）：桌面工程的「打包与启动」→ 静态产物与打开方式；「修改标题/图标」→ 站点标题、首页文案与配图；「发布·分发」→ 部署 `public/`。三个不变量不变：最短可跑路径不断链、判据可机器检、交付面收窄。

---

## 一、前置要求

| 工具 | 版本 | 本机路径 | 为什么必须是它 |
|------|------|---------|----------------|
| Hugo | v0.168.0 **Extended** | `C:\Users\webtu\tools\hugo\hugo.exe` | 主题用 SCSS，标准版编译不了（`oink-starter/doc/问题004`）；`hugo.yaml` 里 `hugoVersion.min: 0.160.1` |
| Go | 1.25.4 | `C:\Users\webtu\tools\go\bin\go.exe` | Hugo 模块系统需要 go；`go.mod` 声明 `go 1.25.4`，版本低了会触发联网下载工具链 |

```powershell
hugo version
go version
```

实测输出：

```
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio
go version go1.25.4 windows/amd64
```

两个环境变量是硬要求，不是优化：

| 变量 | 取值 | 不设会怎样 |
|------|------|-----------|
| `GOTOOLCHAIN` | `local` | go 发现工具链版本不匹配时尝试联网下载 `go1.x`，离线环境直接卡死 |
| `GOPROXY` | `off` | Hugo 尝试从 `proxy.golang.org` / GitHub 拉远程模块；本工程主题走 `go.mod` 的 `replace` 本地化，联网纯属多余 |

---

## 二、项目启动（首次构建）

```powershell
$env:PATH = "C:\Users\webtu\tools\go\bin;C:\Users\webtu\tools\hugo;" + $env:PATH
$env:GOTOOLCHAIN = "local"; $env:GOPROXY = "off"
cd "C:\Users\webtu\Desktop\RocketMQ文档站复刻\rocket-mq-docs"
hugo --cleanDestinationDir
```

实测输出（PowerShell，非 minify 档，本轮第 11 分类重建后复跑）：

```
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio
WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead.
 Pages            | 237
 Static files     | 172
Total in 3344 ms
```

判据：**0 个 ERROR**；WARN 只允许上面那一条，它是主题侧对 Hugo 弃用告警的固有提示（`oink-starter` 基线构建同样出这一条），不是本工程引入。SCSS 确实被编译（产物里有 `public/scss/main.min.<hash>.css`），这一点同时反证必须用 Extended 版。

把 stdout 落盘后按行首计数复测（同一目录、同一档）：

```
exit=0
ERROR_count=0
WARN_count=1
```

`Pages 237` 的拆法（本轮实测，别再按「一篇文档一页」读）：第 11 分类 7 篇文章 + 2 个板块页 + 1 个分类页 = 10 个页面，每页产 `index.html` 与 `index.md` 两份，加 3 个板块/分类 `index.xml`，再加 3 个 `_print/*/index.html`（打印档只为分类页与板块页生成，7 篇文章没有独立打印页），共 **26 个文件**落在 `public/docs/11-springboot-integration/`（10 html + 10 md + 3 xml）与 `public/_print/docs/11-springboot-integration/`（3 html）。页面数只用来核对「新内容确实进了产物」，真判据是 8.2 的四个脚本。

首次构建不需要联网：主题在 `oink-main/oink-main/`，`GOPROXY=off` 下构建成功即为证。

---

## 三、本地调试

```bash
hugo server --port 8770 --bind 127.0.0.1
```

实测输出（节选，本轮复跑）：

```
Watching for changes in .../rocket-mq-docs/assets/icons, .../content/docs, .../data/home, .../layouts/_partials, ...
Start building sites …
hugo v0.168.0-...+extended windows/amd64
Pages            │ 237
Built in 2710 ms
Web Server is available at http://localhost:8774/ (bind address 127.0.0.1)
```

（端口每次自己选一个没被占用的即可，上面是本轮用的 8774。）

改动 `content/` 下任意 md 会即时重建，无需重启进程。停止：终端 `Ctrl + C`。

路由探针（两条通道本轮都跑过：`hugo server` 与把 `public/` 起在 `python -m http.server 8773` 的静态档；下表两条通道读数一致，`/docs/nope/` 两边都是 404。**中文路径必须按 URL 编码请求**——同一 URL 直接塞裸 UTF-8 中文进 `curl` 时返回 404，编码后 200，这是 curl 侧没做百分号编码，不是站点缺页）：

```
/                                                   HTTP 200
/docs/                                              HTTP 200
/docs/11-springboot-integration/                    HTTP 200
/docs/11-springboot-integration/六种消息实战/定时消息与任意时刻投递/  HTTP 200（URL 编码后请求）
/picture/Message.png                                HTTP 200
/offline-search-index.zh.json                       HTTP 200（带 hash 的真身 2,066,238 字节）
/docs/nope/                                         HTTP 404
```

浏览器实测（Chromium 内核，`hugo --gc --minify` 产物由 `python -m http.server 8773` 起服务后读取；第 11 分类重建后本轮复跑）：

| 判据 | 实测值 |
|------|--------|
| Mermaid 真出图 | 顺序消息篇（HTTP 档，活页 DOM）2 个 `figure.td-diagram--mermaid` → 2 个 `<svg>`，viewBox `0 0 1102.734375 382`、`36 0 717.2099609375 510.1499938964844`；集成基线篇（`file://` 档）2 个 `figure` → 2 个 `<svg>`，viewBox `0 0 896 1093.921875`、`0 0 723.44921875 990` |
| 没有退化成源码块 | 新分类 10 个页面（7 文章 + 2 板块 + 1 分类）里 `code.language-mermaid` 命中数全为 0 |
| 表格 / 代码块 / 💡 小结 | 逐篇读数见下表（活页 DOM 与 `fetch`+`DOMParser` 两取一致，`<article>` 范围内计数） |
| 分类可达 | `/docs/` 页面上 13 个链接指向 `/docs/11-springboot-integration/` 及其子页；新分类文章页的侧栏里同前缀链接 23 个 |
| 离线搜索 | 索引文件 `offline-search-index.zh.dc658a9500c57c9a75bb96687d159930.json` 2,066,238 字节 |
| 图片落盘 | 新分类 7 篇**一张官方配图都没引用**：`grep -rn '!\[' content/docs/11-springboot-integration` 命中 0 处，页面上 `<img>` 数为 0。这一分类的图片判据是空集，`BROKEN_IMAGE` 检查仍由 01~10 的 38 篇承担，本轮 `problems=0` 里含该项 |
| 控制台 | 顺序消息篇（HTTP 档）0 条消息 |
| 主题样式生效 | 该页 5 张样式表且 `cssRules` 全部可读（两张内联 7 条、`fontawesome.min…css` 2,699 条、`main.min…css` 3,226 条、内联 59 条），`body` 背景 `rgb(11, 17, 25)`、`h1` 计算字体 `Inter` |

7 篇的逐篇结构读数。💡 只数正文含「新人小结」的 `blockquote > h3`；「首个 H2」取 `<article>` 内第一个 `h2` 的文本：

| 文章 | figure | 表格 | `pre` | 💡 小结 | 有「要点总结」 | 首个 H2 含「为什么」 |
|------|--------|------|-------|---------|----------------|--------------------|
| SpringBoot 集成方案与版本基线 | 2 | 15 | 4 | 4 | 是 | 是 |
| 普通消息与三种发送语义 | 2 | 7 | 15 | 4 | 是 | 是 |
| 批量消息与整批上限 | 1 | 7 | 9 | 4 | 是 | 是 |
| 延时消息与订单超时关单 | 2 | 9 | 17 | 5 | 是 | 是 |
| 定时消息与任意时刻投递 | 1 | 11 | 19 | 5 | 是 | 是 |
| 顺序消息与分区有序落地 | 2 | 11 | 14 | 5 | 是 | 是 |
| 事务消息与半消息回查 | 1 | 9 | 11 | 5 | 是 | 是 |

`figure` 与 `code.language-mermaid` 的比是 11:0（7 篇的 mermaid 块总数经 `validate_mermaid.py` 独立数为 11），说明主题的 mermaid 短码已经把源码块包成 figure、没有把裸 `<pre>` 留给运行时。

本轮全站已没有「照录篇」这一类文章（`VERBATIM` 集合为空，见 8.2.1 第 2 条），所以上表七行都按完整重写体裁判据度量，没有豁免行。

一个坑要提前知道：搜索面板首次打开会显示「正在加载搜索索引……」，2 MB 级索引 + 建库需要一两秒，此时输入的查询会落空。**等状态文字消失再输**，别以为搜索坏了。

本轮的浏览器读数同样是**隐藏页**取的（`document.hidden = true`，`window.innerWidth` 与 `clientWidth` 均为 0）。后果要说清：`<body>` 宽度算成 0，凡依赖布局视口的量本轮一律没采——包括「`scrollWidth > innerWidth` = false」那条横向溢出判据，本轮未复测，已移到文末「未验证项汇总」；viewBox 是 mermaid 自己离屏排版算出的几何，不受视口为 0 影响，所以照采（`svg` 计数需要等主题脚本跑完，本轮用「每 500ms 轮询、最多 8s」的步进取到非零值，不是同步读一次）。

---

## 四、静态产物与打开方式（对应桌面工程的「打包与启动」）

```powershell
hugo --cleanDestinationDir --gc --minify
```

实测输出：`Pages 237`、`Static files 172`、`Total in 3381 ms`，产物 `public/` 共 **424 个文件 / 47,088,984 字节**（minify 档口径）。同一目录树在**非 minify** 档下为 424 个文件 / 48,974,187 字节——两档文件数不变，体积差 1,885,203 字节全部来自 HTML/CSS/JS 空白压缩。两档本轮各跑一次，文件数一致。

第 11 分类重建带来的文件数变化：该分类在产物里落 26 个文件（`public/docs/11-springboot-integration/` 下 10 个 `index.html` + 10 个 `index.md` + 3 个 `index.xml`，加 `public/_print/docs/11-springboot-integration/` 下 3 个打印页）。上一轮记的是 28 个文件（当时该分类有 8 篇、含一个 8 图的照录篇），本轮是 7 篇，`Pages` 也从 225 变成 237——两个数不同档不同内容，不要跨轮相减当增量用。

`hugo.yaml` 里开了 `relativeURLs: true`，所以产物是**路径无关**的：既可以直接双击 `public/index.html` 用 `file://` 打开，也可以整目录丢进任意子路径的静态服务器。两条通道本轮都实测过：

- **HTTP 档**：minify 产物由 `python -m http.server 8773` 起在 `/`，第 11 分类 10 个页面逐个 `fetch` 全 200（中文路径走 URL 编码）；顺序消息篇 2 张 mermaid 出真 `<svg>`（viewBox 见第三章表格）；深页上的搜索索引属性解析后 200。
- **`file://` 档**：直接打开 `public/docs/11-springboot-integration/集成基线/springboot集成方案与版本基线/index.html`，读到 `location.protocol = file:`、标题「Spring Boot 集成方案选型与版本基线 | RocketMQ 文档」、`h1` 与标题一致、5 张样式表且 `cssRules` 全部可读（两张内联 7 + 59 条、`fontawesome…css` 2,699 条、`main…css` 3,227 条）、`body` 背景 `rgb(11, 17, 25)`、2 个 `figure` → 2 个 `<svg>`（viewBox `0 0 896 1093.921875`、`0 0 723.44921875 990`）、`code.language-mermaid` 0 处、15 张表格 4 个 `pre`。

`file://` 下**没有**验搜索：浏览器策略拦 `file://` 页面里的 `fetch`/XHR，索引加载走的那条路在 `file://` 档不可达，所以这条只在 HTTP 档成立——别把它当成「双击也能搜」。本轮在 `file://` 深页上取索引属性时读到的是 `null`（页面没暴露可直接断言的属性名），因此这条判据仍按「`file://` 档不成立」处理。

产物里每页还额外产出可下载的 Markdown：`public/docs/**/index.md` 命中 79 个，正好等于 45 篇文章 + 34 个 `_index.md`（另有站点根 `public/index.md`，全站合计 80 个）。

---

## 五、改站点标题与首页文案（对应「修改标题」）

| 要改什么 | 改哪里 | 生效位置 |
|----------|--------|----------|
| 站点名 | `hugo.yaml` 的 `title: &siteTitle`（YAML 锚点，`languages.zh.title` 复用它） | 浏览器标签、顶栏、页脚 |
| 首页大标题/副标题/按钮 | `data/home/zh.yaml` 的 `hero.title_lines`、`lead`、`actions` | 首页 hero |
| 首页三张卡片 | 同文件 `cards.items`（`title`/`desc`/`icon`/`url`） | 首页「按板块逐步深入」 |
| 首页底部 CTA | 同文件 `cta` | 首页尾部 |
| 文档总览卡片 | `content/docs/_index.md` 正文的链接列表 + 末行 `{.cards}` | `/docs/` |
| 一级分类卡片文字 | 各 `content/docs/NN-xxx/_index.md` 的 `linkTitle`、`description`、`icon` | 侧边栏顶部下拉 |

只改 `hugo.yaml` 的 `title` 而忘改 `data/home/zh.yaml` 是最常见的「标题改了一半」——首页 hero 与站点名是两处数据源。

---

## 六、改图标与配图（对应「修改图标」）

| 资源 | 位置 | 说明 |
|------|------|------|
| 站点 logo | `assets/icons/logo.svg` | 当前是主题自带的中性图标；换掉即可，`params.logo` 未启用 |
| 浏览器图标 | `static/favicon.svg` | 直接覆盖同名文件 |
| 分类图标 | 各一级分类 `_index.md` 的 `icon: fa-solid fa-xxx` | FontAwesome 6 类名，见主题 `assets` 内图标集 |
| 官方配图 | `static/picture/`（150 个文件 / 16,458,543 字节） | 正文用绝对路径引用，如 `![消费位点](/picture/消费位点.png)`，构建时自动改写为相对路径 |

配图引用规则：文件名含中文或空格时必须 URL 编码（例：`/picture/RocketMQ%20Prometheus%20Exporter-1.jpeg`）。审计脚本对每张被引用的图做落盘存在性检查，引用不存在的图会以 `BROKEN_IMAGE` 报出来。

---

## 七、发布与分发

`public/` 是纯静态目录，任何静态托管都能吃：内网 Nginx、GitHub Pages、对象存储、直接发压缩包都行。要点：

1. 用 `hugo --cleanDestinationDir --gc --minify` 出发布档（`--gc` 清掉孤儿产物，`--minify` 压 HTML/CSS/JS）。
2. 因为 `relativeURLs: true`，**不需要**为子路径改 `baseURL`；`baseURL` 只在需要生成 canonical/RSS 绝对链接时才有意义，当前是占位值 `https://example.org/`，正式部署请改成真实域名。
3. 分发前确认 `public/offline-search-index.zh.<hash>.json` 在里面——离线搜索靠它，丢了搜索就只剩空框。

**本节命令未做真实部署验证**（本机无部署目标），只验证了 `public/` 在本地 HTTP 服务与相对路径下自洽。

---

## 八、注意事项与判据

### 8.1 内容新增的硬规矩

见 `README.md` 第四、六章。最容易踩的两条：新建二级板块必须同时建该板块的 `_index.md` 并在父级分类的「知识板块」列表补一行；文章必须带 `title`/`description`/`weight` 三字段。

第三条只对本轮重建的第 11 分类生效：它是**官方取证专题**，不是上游复刻，也不是「跑一个工程把数字采回来」。矩阵里 sources 以 `ref:` 开头的文章，技术事实只有三处来源——`rocketmq-spring` 仓库 tag `rocketmq-spring-all-2.2.3` 的源码与 `rocketmq-spring-boot-samples` 官方示例（正文写文件相对路径 + tag + 行号）、上游 `apache/rocketmq-site` 的 4.x/5.0 中文文档、`rocketmq-all-4.9.8-bin-release` 发行包内 jar 的类结构与常量池静态取证；正文不写本地暂存目录路径，也不进 119 篇覆盖率统计。本轮**不搭建、不运行任何工程**：没有依赖安装、没有建库、没有起 Broker、没有打接口，因此正文里不允许出现运行读数（毫秒、吞吐、msgId 字面量、队列分布、回查秒数），代码块的输出行统一写 `// 预期输出:` 并注明推定依据；凡正文用到「实测」二字的篇章，开头都有一条 `[!NOTE] 证据口径` 声明「实测＝静态取证」（本轮命中的是集成基线、普通消息、定时消息、顺序消息 4 篇，另外 3 篇通篇不用「实测」二字）。上一轮那套「同级工程 `../springboot-rocketmq-demo/` + `_build/evidence/` 实测档」的口径随该工程被删除一起作废，`local:` 前缀在当前矩阵里已无使用者（脚本仍支持该前缀，`check_coverage.py` 会把它单独出一行「本地实战专题」）。

### 8.2 四个验收脚本（都在仓库外 `_work/`，改内容后重跑）

| 脚本 | 判据 | 本轮实测 |
|------|------|----------|
| `_work/audit_structure.py` | 目录与 `_index.md` 配对、矩阵与磁盘一致、front matter 三字段、weight 同目录 1..N 连续、正文 ≥260 行、💡 ≥3、Mermaid ≥1、表格 ≥2、代码块 ≥1、有「要点总结」、首个 H2 是「为什么…」、无制表符、无省略式表达、图片引用可落盘、无英文裸标题、正文不出现本地暂存目录 `_work`、不出现审计脚本自己的字面量 | `articles=45 expected=45 dirs=34 problems=0`（`by_kind={}`） |
| `_work/check_links.py` | 以 `public/` 真实产物为判据解析站内链接 | `links_checked=266 external_or_anchor=81 broken=0` |
| `_work/validate_mermaid.py` | 抽出全部 ```mermaid 块，用主题自带 `mermaid.min.js` 在浏览器里 `parse()` | 真实档 `TOTAL=100 REAL_FAIL=0`；`--selftest` 档页头 `TOTAL=100 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`、`window.__HEADLINE = GREEN`（其中第 11 分类 11 块全部解析通过，图型为 sequence / flowchart-v2 / stateDiagram） |
| `_work/check_coverage.py` | 每篇对其源文档的术语/数值覆盖率 | 119 个源→文映射逐条：术语覆盖 15%–100%（≥90% 的 35 条），数值覆盖 116/119 条为 100%（非 100% 的三条为 0%、0%、50%）；`ref:` 源单独出一行「综合参考取证 / 不认领单一上游页面，不参与上游覆盖率统计」，全站 10 行、其中第 11 分类 7 行 |

覆盖率低的那几条要看得懂是什么：`4x:02push.md → 05-consumption/消费模型/消费者类型与推拉模型.md` 术语 38/260=15%、`50:05sendretrypolicy.md → 04-message-features/发送可靠性与存储/发送重试流控与消息存储清理.md` 术语 82/150=55%、`4x:06log.md → 07-configuration/参数与日志配置/客户端与服务端参数配置.md` 数值 1/2=50%。三行的漏项样例里排着 `TabItem`、`import`、`label`、`theme`、`github`、`blob`、`master`、`Admin`、`Dashboard`、`RETRY`、`TAGS` 这类词——它们是上游 Docusaurus 页面的组件标签、JSX 关键字与外链 token，不是丢了的技术事实。所以这个指标只用于「没有整段漏搬」的量级核对，低分先去看样例词表属于哪一类，别直接当缺陷读。

配套的 `_work/matrix.py` 本轮读数：`categories=11 sections=22 articles=45 source_refs=119`、`on_disk=119 claimed=119 duplicated=[]`、`UNCOVERED=0`、`NONEXISTENT_CLAIMS=0`。`_work/gen_matrix_doc.py` 重写映射文档：`lines=614 identical=12 differing=17`。

### 8.2.1 判据自己会红的三条证明

绿值只有在判据会红时才有意义。本轮跑的三条：

1. **mermaid 判据会红**：`python _work/validate_mermaid.py --selftest` 在真实 100 块前面插 1 好 1 坏两块（`blocks.json` 共 102 条），把 `_work/mermaid-harness/index.html` 起在 http 服务上用主题自带的 `mermaid.min.js` 真解析，页头读数原样：

   ```
   TOTAL=100 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS
   ```

   `window.__HEADLINE` 为 `GREEN`；坏块那一条的报错是 `Parse error on line 3: ...h LR  A[起点 -- 缺右括号`。即：注入的坏图确实让它红，所以 `REAL_FAIL=0` 不是静默放行。老版模板（`mermaid-test/index.html`）在同一个 `blocks.json` 上报的是 `TOTAL=102 FAIL=1`，两种口径都是同一判据。

2. **矩阵与磁盘的交叉判据会红**：把 `content/docs/11-springboot-integration/六种消息实战/批量消息与整批上限.md` 临时改名成 `.bak`（不动矩阵、不动脚本），重跑 `audit_structure.py` 得

   ```
   articles=44 expected=45 dirs=34 problems=2
   by_kind={"NOT_WRITTEN": 1, "WEIGHT_GAP": 1}
     WEIGHT_GAP  :: 11-springboot-integration/六种消息实战 :: 应为 1..5，实际 [1, 3, 4, 5, 6]
     NOT_WRITTEN :: content/docs/11-springboot-integration/六种消息实战/批量消息与整批上限.md :: 矩阵要求但文件不存在
   ```

   改回原名再跑得 `articles=45 expected=45 dirs=34 problems=0`。这条同时替代上一轮的「清空 `VERBATIM` 看照录篇会不会红」——**本轮 `VERBATIM` 集合已为空**（矩阵里没有任何 `verbatim=True` 文章），照录豁免那条会红证明失去了对象，改成上面这条交叉判据的会红证明；将来再加照录篇时，按 `README.md` 第四章第 5 步的四条仍生效判据重新做一次豁免自证。

3. **审计脚本在骨架上也红**：只有 front matter 的骨架目录报 **217 条**问题。这条是第 11 分类并入前那轮的读数，本轮未复跑骨架夹具，引用时请按「上一轮实测」对待。

### 8.3 已知上游缺陷（正文里都做了显式标注，不是本站的错）

| 缺陷 | 本站处理 |
|------|----------|
| `04-deployment/02admintool.md` 的「Broker相关」表与「消息相关」表逐行相同（70 行窗口完全相等），Broker 侧命令上游根本没写 | mqadmin 上篇用 `> [!WARNING] 上游文档缺陷` 记录判据，不重复搬运，并给出 `mqadmin` 列命令 / `-h` / 读源码三条可核实替代路径 |
| 同文件 NameServer 段与「其他」段的折叠标题都误写成「连接相关参数」 | 上篇按真实内容归段，未沿用错误标题 |
| `02server.md` 里 `fileReservedTime` 说明栏「默认 72 小时」与默认值栏印「120」自相矛盾 | 参数篇与存储篇并列两口径，不裁决 |
| 定时时长上限：特性文档 24 小时 vs 领域模型 40 天 | 消息类型篇并列引用 + 出处，标注按部署版本验证 |
| 日志单文件大小三口径（64MB / 1GB / 索引回落 10 个） | 参数篇 `> [!IMPORTANT]` 集中说明 |
| Connect 实战 1 的 source topic 与 sink topic 不同名、`max.task` 与 `max.tasks` 混用、SFTP 连接器类名落在 `...http.sink` 包下 | 照抄并注「上游原文如此」 |

### 8.4 复刻口径与正文体量

上游 119 篇（5.0 69 + 4.x 50）→ 认领上游页面的重写文档 31 篇；另有 4 篇「本地实战专题」（`local:`，即 03/06/07 里的原文照录页）与 10 篇「综合参考取证」（`ref:`，其中 3 篇在 01~10、第 11 分类 7 篇），三类相加 45 篇 = 全站文章数。逐条归属与「同名文件是否逐字节相同」的判据见 `doc/复刻覆盖矩阵.md`（本轮重生成：`lines=614 identical=12 differing=17`，指标表实测为「一级分类 11 / 知识板块 22 / 重写文档 31 / 本地实战专题文档 4 / 综合参考取证文档 10 / 源文档 119 / 合并倍率 3.84 篇源文档 / 篇重写文档 / 官方配图 150 个文件 16,458,543 字节」——每格都由 `gen_matrix_doc.py` 从 `_work/matrix.json` 现算，只有配图那格的字节数是脚本里落的实测常量）。

正文体量按实测分开记，别把两类混成一个数：

| 口径 | 篇数 | 行数 | 字节 |
|------|------|------|------|
| 上游重写文档 + 照录 + 综合参考（分类 1–10） | 38 | 24,548 | 1,813,304 |
| 与 Spring Boot 的集成（分类 11） | 7 | 4,221 | 388,666 |
| 两类合计 | 45 | 28,769 | 2,201,970 |
| 另加各级 `_index.md` | 34 | 507 | 15,605 |
| `content/docs/` 下全部 md | 79 | 29,276 | 2,217,575 |

行数按 `\n` 计数、字节按 `os.path.getsize`，取法见 `_work` 里的统计片段。上游源正文约 1.16 MB，增量来自类比、对比表、Mermaid 与术语表；第 11 分类 4,221 行里 mermaid 块占 11 个，全部由 `validate_mermaid.py` 真解析过。

上一轮记录的「照录篇逐字节判据」（源文件 `RocketMQ技术参考文档.md` 78,317 字节 / MD5 `ac9b7f88…`，站内文件剥 front matter 后逐字节相等）**本轮不可复跑**：该照录文章与它指向的源文件、以及素材工程 `../springboot-rocketmq-demo/` 都不在本机磁盘上（本轮工作区里第 11 分类是从零重写的）。这条判据连同它证明过的文章一起作废，别再引用。

上游类正文的引用出处一律写上游仓库相对路径（`docs/...`、`versioned_docs/version-5.0/...`），官方取证类反过来写「仓库 + tag + 文件 + 行号」或发行包 jar 内的类路径——两条都由审计脚本把住：任何分类正文出现 `_work` 即报 `SCRATCH_PATH`，取证类的来源要求成文在 `README.md` 第四章第 6 步。

---

## 未验证项汇总

| 项 | 状态 | 原因 |
|----|------|------|
| **新分类正文的运行时验证** | 未做（本轮明确不搭工程） | 用户本轮要求「无需本地搭建真实工程，按官方与社区最优案例写示例」。因此第 11 分类的全部结论都停在「源码/文档/发行包实物」这一层：没有起过 Broker、没有起过 Spring Boot 应用、没有打过任何接口。文中所有 `// 预期输出:` 是推定，不是读数 |
| starter 2.2.3 在 Boot 2.7.18 + JDK 8 上的实际装配结果 | 未验证 | 只有 `rocketmq-spring-boot-parent:2.2.3` 的 pom（构建基线 Boot 2.5.9 / Spring 5.3.20）与自动装配条件源码作依据；没跑过 `@ConditionalOnProperty` 的实际评估，也没看过一次启动日志 |
| 「5.0.0 客户端连 4.9.8 Broker 时 `TIMER_*` 属性的服务端处理细节」 | 未验证 | 本机没有 5.0.0 客户端 jar 的正文可比对，只证到「4.9.8 侧 `Message`/`MessageConst` 无 `TIMER` 符号、官方 javadoc 声明该方法需 Broker 5.0+」；正文按「不成立/无入口」写，没写成「报错」或「静默丢弃」 |
| 部署到真实 Web 服务器 / CDN | 未验证 | 本机无部署目标；仅验证 `public/` 在本地 HTTP 与 `file://` 相对路径下自洽 |
| 深色/浅色主题切换、阅读进度、图片放大等主题交互 | 未验证 | 主题自带能力；本轮只在 `file://` 与 HTTP 两个深页上读到深色计算样式（`body` 背景 `rgb(11, 17, 25)`），没点过切换控件 |
| 打印档 `_print/` 的图表呈现 | 未验证 | 主题对非交互输出走静态分支（mermaid 出源码块），未逐项核对；本轮只核出它的页数（新分类 3 个 `_print/*/index.html`） |
| 非 Chromium 浏览器（Firefox / Safari） | 未验证 | 本机可用浏览器内核为 Chromium |
| `file://` 档的离线搜索 | 未验证（且预期不可用） | 浏览器策略拦 `file://` 页面的 `fetch`/XHR，索引加载不成立；搜索只在 HTTP 档验过 |
| 窄屏与横向溢出 | 本轮未复测 | 上一轮 1280×1024 视口实测 `scrollWidth > innerWidth` = false；本轮浏览器读数是隐藏页（`innerWidth`/`clientWidth` 均为 0），凡依赖布局视口的量一律没采，包括这条 |
| Go 版本升级后的构建 | 未验证 | 当前锁 1.25.4；升级需同步 `go.mod` 的 `go` 指令，否则触发工具链下载 |
| 审计骨架夹具的 217 条红值 | 上一轮读数，本轮未复跑 | 本轮改跑了「矩阵与磁盘交叉判据」的会红证明（8.2.1 第 2 条：改名一篇文章 → `problems` 从 0 变 2，改回 → 0）；`VERBATIM` 集合本轮为空，照录豁免的自证失去对象，骨架档复跑需要另建临时目录树 |
