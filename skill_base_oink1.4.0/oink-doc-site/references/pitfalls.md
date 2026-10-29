# 踩坑清单（从 0 建 OINK 文档站）

只列真实付过代价的项。每条给出「现象 → 先查 → 处理」。

## 1. 中文与 emoji 的计数不可信

Git Bash 控制台默认 GBK 码页，`grep -c '💡'` 可能恒为 0；`grep -c` 数的还是**行数**不是出现次数。

处理：计数一律用 Python，`PYTHONIOENCODING=utf-8` + `io.open(..., encoding="utf-8")` + `str.count()` / `re.findall()`。技能里的 `audit_content.py` 就是这么数的；不要自己另写一套 shell 计数。

## 2. Bash 的 cwd 会漂，`/tmp` 也不是 Windows Python 的 `/tmp`

每次 Bash 调用后 cwd 可能回到工作区根。不要依赖上一条 `cd`；脚本与临时产物一律用绝对路径，临时目录用工作区 `.tmp/`（脚本已支持 `OINK_DOC_TMP`），不要用系统 `%TEMP%` 兜底——Windows 沙箱常拒绝在托管 Temp 根下建子目录。

## 3. 判据自己会污染被检对象

`audit_content.py` 的报告和写作规范里会出现 `NO_MERMAID`、`方框字符` 等词。正文抄进这些词会触发 `SELF_CHECK_LEAK`。写文档时用中文描述问题，不要复制审计输出；规范里的方框反例也不要搬进正文（代码块内也扫）。

## 4. 骨架模式与成品模式不能混绿

`--mode skeleton` 的 `problems=0` 只代表导航/front matter/图片/权重没坏，不代表文章达标（`genre_checks=0`）。成品验收必须 `--mode full`，并且 `STUB_PAGE` 不能出现。`verify_site.py` 的汇总行会带 `mode=`，先看这个再读数字。

## 5. 判据先证明会红

`verify_site.py --selftest` 会跑四个子脚本自证，并在假站点上注入「占位符 / 缺 `data-td-preset` / 缺 T0 文档 / 坏计划」四类缺陷，逐条要求 FAIL。自证不是 `SELFTEST_PASS` 时，真实站点的绿色不可信。改判据脚本或夹具后必须重跑。

## 6. Mermaid 必须过真解析器

只数 ```mermaid 围栏数量不等于图能渲染。技能里的 `validate_mermaid.py` 用主题自带 `mermaid.min.js` 生成解析台：

```bash
# 1) 生成解析台（会额外注入一好一坏两块 SELFTEST）
python <技能目录>/scripts/validate_mermaid.py --site <站点> --selftest

# 2) 起本地 http 服务（file:// 下 fetch 会被拦）
python -m http.server 8767 --directory <站点>/_mermaid-harness

# 3) 用任意 Chromium 读回结果（离线，无需联网）
msedge --headless=new --virtual-time-budget=8000 \
  --dump-dom http://127.0.0.1:8767/index.html
```

期望在 `#out` 里读到 `TOTAL=<真实块数> REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`。`TOTAL` 不含 2 个注入样本。读不到说明解析台没跑起来，此时 `REAL_FAIL=0` 不可信；增大 `--virtual-time-budget` 或检查 http 服务。2026-10-25 实测：540 行样章的 2 张图 `TOTAL=2 REAL_FAIL=0 SELFTEST_PASS`。

## 7. Hugo / 主题的构建约束

- 必须 Hugo **Extended ≥ 0.168.0**（OINK 1.4.0 的 `min_version`）；标准版编不了 SCSS。
- Go 必须 **≥ 1.27.3**：取「站点 go.mod」与「被 replace 的主题 go.mod」两处 `go` 指令的最大值，本机验证用 go1.27.3。
- 本地主题站必须 `GOTOOLCHAIN=local GOPROXY=off`，否则 Hugo 可能联网重试，报出来的却是 `failed to load modules`，看着像内容错。
- PATH 里可能同时有多个 Go（本机实测：`Program Files/Go` = go1.27.2、`tools/go` = go1.25.4、`tools/go1.27.3` = go1.27.3）。`go version` 打印 `go: downloading go1.27.3` 就是命中的 Go 低于下界、正试图自己下载工具链；用 `--go-bin` 指向 1.27.3 的 bin，不要只依赖 PATH 顺序。
- `WARN deprecated: css.Sass: libsass was deprecated` 是主题固有提示，判据是 0 个 ERROR。**不要再加 `--panicOnWarning`**：1.4.0 的 AGENTS.md 明令任何 build/checker/preview/CI 都不要开它，警告要保持可见；旧口径「严格闸门用 Hugo 0.166.0」已作废，0.166.0 现在连主题下限都不满足。
- Hugo 报 `binary with name "go" not found in PATH` 时用 `--go-bin <go的bin目录>`，不是内容错误。

## 8. 视觉预设：配置层绿不等于产物层绿

`params.ui.preset` / `preset_menu` 写成实值，且主题副本必须是 OINK 1.4.0（含 `_presets.scss`、`preset-config.html`；`scaffold.py`/`verify_site.py` 另查 1.4.0 独有的 `assets/js/diagram.js`、`table-reader.js`、`third_party/plantuml/plantuml.js`）。旧主题副本 + 正确配置 = **构建零报错但产物没有 `data-td-preset`**。判据看 `public/index.html` 的 `<html data-td-preset="<preset>">`，再看 4 个预设名是否在产物里（Appearance 菜单在 HTML 中，是 `<dialog>`；不要只看首屏截图就断言没有）。

实测：骨架站与成品站的 `public/index.html` 都带 `data-td-preset="paper"`；点击 Appearance 触发器后面板可切到 `slate`，`localStorage['td-preset']` 写入 `slate`；切回 paper 后该键被删除。

## 9. `relativeURLs` 与首页 URL：两处最容易断

`relativeURLs: true` 下产物可挂子路径，但不要把它当「双击完整可用」：主题给 CSS/JS 写了 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，浏览器会按 CORS 拦截，页面只剩无样式文字，Mermaid 与搜索都不可用。完整浏览走 `hugo server` 或 `python -m http.server`。此外，`data/home/zh.yaml` 的 `url` 和 `content/docs/_index.md` 的卡片链接是手写数据，不会自动帮你补层级：

```
正确：docs/01-overview/认识系统/what-is-it/
错误：docs/01-overview/what-is-it/          # 漏了板块层，构建后 404
```

`plan_site.py` 现在用 `BAD_HOME_URL` 在写盘前校验首页 URL；站内链接最终仍以 `check_links.py` 对 `public/` 的判定为准。`unmapped` 非零时 `broken` 数字不可信，先对齐 URL 规则。

## 10. 搜索面板首次打开会加载索引

MB 级索引首次打开要一两秒建库，期间输入会落空。判据：等面板不再显示「正在加载搜索索引……」再输入；或先打开面板等状态消失。2026-10-25 实测：查询「安装」返回 3 条命中（文章、板块、分类各一条）。

## 11. 浏览器截图的宽度不等于布局视口

Edge `--headless=new --window-size=390,844` 实测 `window.innerWidth=492`，而截图文件仍是 390 宽——拿截图看会误判「右侧被裁」。判据：

- 先读 `window.innerWidth` / `document.documentElement.scrollWidth`，再判断溢出；
- 要真 390px，用 CDP `Emulation.setDeviceMetricsOverride({width:390,height:844,deviceScaleFactor:1,mobile:true})` 后截图；
- Qoder 内置浏览器在窗口不可见时 viewport 为 0×0，截图会失败；此时只用 DOM 断言，布局测量改用 headless Edge。

实测：390×844 下 `scrollWidth=390`，h1 右边界 323、两个按钮右边界 359，无横向溢出；1440×1200 下首页/文档/文章均正常。

## 12. 主题 partial 覆盖必须同名

Hugo 按模板名精确查找；`root-menu-roots（说明）.html` 这类带说明性后缀的文件是死文件，永远不会被调用。本技能骨架**不附带** `root-menu-roots.html` 覆盖——主题自 OINK 1.3.2 起就原生处理 `sidebar_root_menu` 与分隔节（1.4.0 该文件字节未变，实测），旧覆盖反而少过滤。

## 13. 主题注释与代码可能不一致

主题 `hugo.yaml` 的注释描述的是主题侧默认；站点侧不写 `markup` 就不生效（Hugo 不合并主题的 Goldmark 设置）。改配置前读主题的 render hook / 消费方代码，不要只信注释。`preset_menu` 的默认是 `false`，本技能计划默认 4 套全开，是站点侧显式覆盖。

## 14. 计数用 `os.walk`，不要用 `glob`

`glob` 的 `*`/`**` 不匹配点开头的路径段，会静默少数。主题 1,292 个文件用 `os.walk` 数；脚手架输出 `theme_files=1292` 就是实测口径（1.3.2 时代是 1,273）。

## 15. 注释、代码块里的链接不是链接

`check_links.py` 会先剥 HTML 注释、围栏代码、行内代码。不要把模板注释里的示例路径当断链修；反过来，正文里的真链接不要藏在代码块里。

## 16. 文章桩与重跑计划

`plan_site.py` 重写配置、README、总览与分类/板块 `_index.md`，但**已存在的文章默认保留**（`articles_kept`）。重跑计划不会冲掉正文；加 `--force` 才会覆盖文章。改文章标题/描述/weight 优先改 front matter，或确认要覆盖时再加 `--force`。

## 17. T0Level 文档的占位是交付判据

`doc/运行与构建（T0Level）.md` 模板含 `【待填】`。skeleton 模式不要求它；full 模式 `verify_site.py` 的 `delivery_doc` 会检查：文件存在、无 `【`、含 `hugo` 与 `verify_site.py`、≥6 个 H2。没有真实跑过的命令写「未验证」+ 原因，不要编输出。

## 18. 计划里的数字与磁盘要双向对账

`NOT_WRITTEN`（计划有、磁盘没有）与 `UNLISTED`（磁盘有、计划没有）都是问题。新增文章先改计划再生成；删除文章也要同步删计划。`DUP_WEIGHT` / `WEIGHT_GAP` 由磁盘 front matter 判定，手改 weight 会让侧边栏顺序漂移。

## 19. 事实来源要在写之前定

从 0 建站不等于可以编事实。默认值、版本号、命令输出、异常类型必须来自用户材料、官方文档或真实运行；没有来源就写「上游未给出」，不要按同类系统惯例推定。每批在 `doc/内容来源.md` 登记；`verify_site.py` 会把它列为 MANUAL，需人工核对。

## 20. 顶栏空白与长站点名折行

OINK 1.4.0 的顶栏只渲染 `.Site.Menus.main`，不会自动挂 docs 入口。`plan_site.py` 现在会在 `hugo.yaml` 写入 `menus.main` 的「文档」入口（`identifier: docs`、`pageRef: /docs`）；重跑计划会保留。旧站或手删过 `menus.main` 时，顶栏 `.td-nav-menu-zone` 为空，`verify_site.py` 的 `nav` 判据会报。

2026-10-25 实测：未加菜单时 `td-nav-menu-zone` 为空；加后首页出现 73×36 的「文档」tab，点击进 `/docs/`，文档页 tab 带 `active`。另外，站点名过长时 1280px 侧边栏品牌会折行（`ZooKeeper 中文文档` 会把最后一个「档」挤到第二行）；改标题后先在 1280px 宽度看侧边栏，不要只看 1920px。

## 21. 交付前的最小自证清单

1. `python scripts/verify_site.py --selftest` → `SELFTEST_PASS`；
2. `python scripts/verify_site.py --site <站点> --plan <计划> --mode full --hugo hugo` → `FAIL=0`；
3. `public/index.html` 有 `data-td-preset` 与顶栏「文档」入口，`public/offline-search-index.zh.*.json`、`public/llms.txt`、`public/_print/` 存在；
4. Mermaid 解析台读回 `REAL_FAIL=0`；
5. T0Level 文档无 `【`，未验证项写清原因；
6. 内容来源清单覆盖所有具体事实（MANUAL，人工过一遍）。

## 22. 批处理括号块里的 `echo %VAR%` 会提前展开

在 `if … ( … )` 块里先 `for /f … set "GOVER=%%V"` 再 `echo %GOVER%`，打印的是**解析期**的空值（中文系统显示「ECHO 处于关闭状态」），不是命令没跑。要打印命令输出就直接执行该命令（`"%GO%" version`），或把 echo 移到块外/启用延迟展开。run.cmd 模板已按前者固化。

## 23. 显式 `PORT` 时不要打印「8768 busy」

用 `PORT_EXPLICIT` 标记区分「用户指定端口」与「自动顺延」：只有顺延才打 Note。否则用户 `set PORT=8799` 却看到「8768 被占用，改用 8799」的假提示，会误以为探测逻辑抢了他的端口。

## 24. 重定向日志里的中文路径乱码是码页，不是脚本错

cmd 默认按 GBK 写重定向文件，`echo %CD%` 的中文路径在日志里是乱码；脚本开头 `chcp 65001 >nul` 后重定向才是 UTF-8（2026-10-29 实测字节为合法 UTF-8）。控制台直看正常。别把 GBK 日志当 run.cmd 缺陷修，也别为它删掉中文路径打印。

## 25. 端口被别的长驻 Hugo 占用：只探测，不杀

`netstat` 命中 8768 后先用 CIM `Win32_Process` 的 `CommandLine` 确认归属——那可能是用户另一个文档站的实例。run.cmd 从 `DEFAULT_PORT` 顺延到空闲端口并打印 Note；停止自己的服务时只杀按 CommandLine 校验过的 PID，绝不按进程名批量杀。

## 26. Go 版本闸门：改站点 go.mod 那一行不解决问题

`go` 指令是**下界**，实际执行取「主模块 + 被 `replace` 进来的主题」两处 `go.mod` 的最大值。2026-10-29 用临时探针模块实测：站点线写 `go 1.27.0`、被 replace 的主题写 `go 1.27.3`，用 go1.27.2 跑 `go mod download` 得

```text
go: github.com/pgsty/oink@v1.4.0: module .../oink-main/oink-main requires go >= 1.27.3 (running go 1.27.2)
go: switching to go >= 1.27.3: module lookup disabled by GOPROXY=off
```

所以「把站点 go.mod 降一行」躲不掉。三条分支的实测读数：装了够新的 Go → rc=0 且**零下载**（反向也成立：go1.27.3 跑 `go 1.27.0` 的老站点 rc=0，不会反过来下载旧版）；`GOTOOLCHAIN` 未设（默认 auto）+ 版本低 → 试图联网下载、离线机超时 rc=1；`GOTOOLCHAIN=local` + 版本低 → `go.mod requires go >= 1.27.3 (running go 1.27.2; GOTOOLCHAIN=local)` rc=1。最后这条最重要：**设 local 不是修法**，只是把报错形态换掉。

## 27. 图表改为懒渲染：源码态与失败态同形

1.4.0 起 Mermaid/PlantUML 由 `assets/js/diagram.js` 统一调度，第 111-112 行 `new IntersectionObserver(wake, { rootMargin: '320px' })`——**接近视口才加载引擎并渲染**；同时 `render-codeblock-mermaid.html` 第 27 行开始，HTML 分支也输出 `<pre class="td-mermaid-source">` 源文。后果：

- 页面截图/命中测试如果在首屏判下方的图，看到的是一个源码 `<pre>`，既不红也不绿。判渲染前先滚到图前（`scrollIntoView`），或读 `data-td-diagram-state`。
- `validate_mermaid.py` 解析台直连 vendored 引擎（页内 `MERMAID.parse()`），不受懒渲染影响，两者口径不同：解析台 GREEN 不代表页面已画出来，页面没画不代表语法错。
- `mermaid.min.js` 在 1.3.2→1.4.0 **字节全等**（3,572,661 B，sha256 `581ed7d7…`），所以旧解析台判据可以直接沿用，不必重建；但「图表控件」（缩放/适应/SVG 下载/看源码）是新增的，页面级验收口径要另立。

## 28. 再烘焙主题必须按字节拷贝

1.4.0 的 `.gitattributes` 新增一行 `assets/third_party/plantuml/* -text whitespace=cr-at-eol`（注释写明「Preserve upstream bytes and VENDOR.json hashes, including original CRLFs」）。实测新副本：`viz-global.js` 9/9 行 CRLF、`LICENSE` 72/72 行 CRLF、`plantuml.js` 0 CRLF。所以换主题副本要用 `shutil.copytree` 一类字节级拷贝；经 git 检出（`core.autocrlf` 生效）或某些编辑器保存都可能把 CRLF 改成 LF，构建照样过、页面照样跑，但 `VENDOR.json` 的 sha256 会对不上——供应链口径失真且没有症状。验收：`VENDOR.json` 逐条 sha256 比对，判据是 `missing=0 hash_bad=0`；要更强就与上游 tag 的 tree blob 逐个比（实测技能副本 1,292/1,292 全等）。

## 29. 版本判定不要写字符串全等

`scaffold.py` 旧版用 `'min_version = "0.166.0"' in theme_toml` 判基线，主题一升版就整条流水线第一步拒绝；而 `verify_site.py` 用的是 `>= (0,166,0)`，同一件事两种语义，结果是「一个死锁、一个放过」。现在两处统一成：解析 `min_version` 成三元组比下限（下限取自 `scaffold.HUGO_MIN`，单点定义）+ 检查 1.4.0 独有文件存在。判据要能红：`scaffold.py --selftest` 的 `gate_probe` 三条（缺标记→红、低于闸门→红、基线→绿），`verify_site.py --selftest` 注入「min_version 改回 0.166.0」和「删掉一个 1.4.0 独有文件」两类缺陷。

## 30. 表格块属性行写错位置不告警，steps 少一个子 shortcode 会直接红

2026-10-29 在示例站上做的三变体探针，结论两条：

| 探针 | 源文写法 | 产物读数 |
|---|---|---|
| 属性行放表格**上方** | `{#v1 .wide}` 紧接表头 | `<table>`（无 id、无类）——**标记失效且不告警** |
| 属性行放表格**下方紧贴** | 表尾下一行 `{#v2 .wide}` | `<table id="v2" class="wide td-table--wide">` |
| 同上放 `.expand` | 表尾下一行 `{#v3 .expand}` | `<table id="v3" class="expand">` + `<div class="td-table-frame">` + 页内 `data-td-table-reader` 抽屉 |

所以 goldmark 的表格块属性是**后置**的，把它当「门牌钉在门口」一定会写错，而且是静默错：构建 0 ERROR、0 WARN，审计也绿，只有去产物里数类名才发现。判据固定成三条 grep：`<table[^>]*>` 看有没有拿到类、`td-table-frame` 看 `.expand` 是否成框、`data-td-table-reader` 看抽屉是否产出（未用标记的页应为 0，这一条同时是「零开销」的证据）。

第二条相反，是硬失败：`{{< steps >}}` **没有** `step` 子 shortcode，条目是一个三级标题算一步。误写 `{{< step title="…" >}}` 构建直接报 `failed to extract shortcode: template for shortcode "step" not found`。`cards` 则有 `card` 子 shortcode——两者不对称，别照着 cards 类推 steps。

## 31. `baseURL` 写子路径 + `relativeURLs`：页面 200，样式全丢

2026-10-29 两个示例站同时踩到。`baseURL: https://docs.example.com/demo-docs-140/` 配 `relativeURLs: true` 时，Hugo 把子路径烤进资源 URL：首页里写的是 `href="./demo-docs-140/scss/main.css"`。浏览器从 `/demo-docs-140/` 解析这个相对路径 → 请求 `/demo-docs-140/demo-docs-140/scss/main.css` → **404**；而文件真实在 `/demo-docs-140/scss/main.css`（去掉双前缀请求就是 200）。同一页的 logo `<img>` 同理碎掉，Mermaid/搜索/Appearance 全不初始化。

实测对照（同一份产物，`hugo server --renderToMemory`）：

| 项 | 子路径 baseURL | baseURL 在根 |
|---|---|---|
| 首页 CSS href | `./demo-docs-140/scss/main.css` → 解析后 404 | `./scss/main.css` → 200 |
| logo | `./demo-docs-140/icons/logo.svg` → 404 | `./icons/logo.svg` → 200 |
| `check_links` 的 broken | 191（16 个页面、191 条资源） | 0 |
| 页面 HTTP | 200（所以只看状态码会以为没事） | 200 |

**结论**：`baseURL` 写根，挂子路径交给部署目录。判据补在 `check_links.py`：解析 `public/**/*.html` 的 `<link>`/`<script>`/`<img>`，按浏览器口径还原相对路径后逐个查文件是否存在（百分号编码要 `unquote`，目录看 `index.html`，`..` 段要 `normpath`，uglyURLs 还要试 `.html`），缺一条报一条。这条判据自带反例证明：`check_links --selftest` 的 `asset_probe` 放 5 种形态（同目录、`./sub/../good.css`、目录型 `sub/`、百分号编码中文目录、外链）只许报出那 1 条 `missing/main.css`。

## 32. 手改站点 `hugo.yaml` 会被下一次 `plan_site.py` 冲掉

`plan_site.py` 每次都从 `assets/templates/hugo.yaml` 重写站点配置（它保留的是**文章**，不是配置）。实测：往站点 `hugo.yaml` 手工加 `params.plantuml.enable: true` 后重跑计划，该键计数从 1 变 0，构建照过、PlantUML 静默不出图。

现在两条路：站点级开关写进 `site.plan.json` 的 `site.params`（支持嵌套 dict，由 `render_param_lines` 落到 `params` 段内、`module:` 之前）；或写在页面 front matter（如 `blog_index: gallery` + `blog_gallery`，本来就是页级覆盖）。`plan_site --selftest` 多了一条断言：`site.params 落盘 ok=True`，覆盖嵌套、标量与带冒号字符串三种形态。

## 33. `integrity` 只出现在 production 构建

`file://` 下样式被 CORS 拦，前提是产物带 `integrity` + `crossorigin`。实测同一站点：普通 `hugo` 构建 `integrity=` 出现 **0** 次，`hugo --environment production` 出现 **7** 次（主题 `head-css.html` 与 `fingerprint` 走的是 production 分支）。所以「双击只剩无样式文字」对发布档是定论；开发构建下 `file://` 的完整功能未单独验证，别拿它当「file:// 也能看」的依据——验收一律走 HTTP。

## 34. 表格 id 只认 ASCII，中文 id 被丢掉但类和题注照常生效

主题 `layouts/_partials/content/attributes.html` 校验 id，规则是 `[A-Za-z][A-Za-z0-9_.:-]*`。中文文档站很自然想写 `{#参数迁移对照表 .wide}`，实测主题会**丢 id、保留类与题注**，并打一条 WARN：

```text
WARN  shortcode "table": id must match [A-Za-z][A-Za-z0-9_.:-]*; got "参数迁移对照表" at "…feature-tour.md:82:1"; dropping it
```

后果不是样式坏，而是**锚点没了**：任何指向该表的 `#参数迁移对照表` 链接都落空，而构建仍然 0 ERROR。中文站给表起锚点请一律用 ASCII 名（如 `{#param-migration .wide caption="参数迁移对照"}`，题注可以留中文）。同一条规则也适用于 `.expand`；两把标记可以叠加，实测 `{#wide-plus-expand .wide .expand}` 渲染成 `<table id="wide-plus-expand" class="wide expand td-table--wide">`。

判据口径：验收这类标记要看**开标签本身**，不是看页面有没有表格——`grep -o '<table[^>]*>' 产物` 才能同时确认 id 与类；WARN 计数也要单独看（`hugo` 输出里除 libsass 那条以外应当干净）。

## 35. Expo 相册：`type: expo` 写在 section 上不出图，也不报错

Hugo 的页面 `.Type` 默认取所在 section 名。只在 `content/albums/_index.md` 写 `type: expo` 时，section 列表页走 expo 外壳，**子页仍走 `_default/single.html`**：构建 0 ERROR、0 WARN，相册页 HTML 正常生成，但 `data-td-expo-item` 计数为 0、页面只剩 1 个 `<img>`（站点 logo）。2026-10-29 图库示例站实测就是这个形状。

补上**页级** `type: expo` 之后同一命令的读数变成：机柜相册 `data-td-expo-item`=6、`<img>`=9、`mode=cards`、`size=260`；换盘相册 5 / 8 / `seamless` / 220。判据因此落在产物上：`grep -c 'data-td-expo-item' 相册页` 必须等于 bundle 里的图片数，光看构建返回码会假绿。
