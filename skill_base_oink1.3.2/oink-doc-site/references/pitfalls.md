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

- 必须 Hugo **Extended ≥ 0.166.0**；标准版编不了 SCSS。
- Go 与 `go.mod` 的 `go 1.27.0` 对齐（本机验证用 go1.27.2）。
- 本地主题站必须 `GOTOOLCHAIN=local GOPROXY=off`，否则 Hugo 可能联网重试，报出来的却是 `failed to load modules`，看着像内容错。
- PATH 里可能同时有旧 Go（如 `tools/go` 1.25.4）和新 Go（如 `Program Files/Go` 1.27.2）。`go version` 若打印 `go: downloading go1.27.0`，是选错 Go 并试图联网；验收时用 `--go-bin` 指向 1.27.x 的 bin，不要只依赖 PATH 顺序。
- `WARN deprecated: css.Sass: libsass was deprecated` 是主题固有提示，普通构建 0 ERROR 即通过；但带 `--panicOnWarning` 的严格闸门会因此致败，严格闸门用 Hugo 0.166.0。
- Hugo 报 `binary with name "go" not found in PATH` 时用 `--go-bin <go的bin目录>`，不是内容错误。

## 8. 视觉预设：配置层绿不等于产物层绿

`params.ui.preset` / `preset_menu` 写成实值，且主题副本必须是 OINK 1.3.2（含 `_presets.scss`、`preset-config.html`）。旧主题副本 + 正确配置 = **构建零报错但产物没有 `data-td-preset`**。判据看 `public/index.html` 的 `<html data-td-preset="<preset>">`，再看 4 个预设名是否在产物里（Appearance 菜单在 HTML 中，是 `<dialog>`；不要只看首屏截图就断言没有）。

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

Hugo 按模板名精确查找；`root-menu-roots（说明）.html` 这类带说明性后缀的文件是死文件，永远不会被调用。本技能骨架**不附带** `root-menu-roots.html` 覆盖——OINK 1.3.2 已原生处理 `sidebar_root_menu` 与分隔节，旧覆盖反而少过滤。

## 13. 主题注释与代码可能不一致

主题 `hugo.yaml` 的注释描述的是主题侧默认；站点侧不写 `markup` 就不生效（Hugo 不合并主题的 Goldmark 设置）。改配置前读主题的 render hook / 消费方代码，不要只信注释。`preset_menu` 的默认是 `false`，本技能计划默认 4 套全开，是站点侧显式覆盖。

## 14. 计数用 `os.walk`，不要用 `glob`

`glob` 的 `*`/`**` 不匹配点开头的路径段，会静默少数。主题 1,273 个文件用 `os.walk` 数；脚手架输出 `theme_files=1273` 就是实测口径。

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

OINK 1.3.2 的顶栏只渲染 `.Site.Menus.main`，不会自动挂 docs 入口。`plan_site.py` 现在会在 `hugo.yaml` 写入 `menus.main` 的「文档」入口（`identifier: docs`、`pageRef: /docs`）；重跑计划会保留。旧站或手删过 `menus.main` 时，顶栏 `.td-nav-menu-zone` 为空，`verify_site.py` 的 `nav` 判据会报。

2026-10-25 实测：未加菜单时 `td-nav-menu-zone` 为空；加后首页出现 73×36 的「文档」tab，点击进 `/docs/`，文档页 tab 带 `active`。另外，站点名过长时 1280px 侧边栏品牌会折行（`ZooKeeper 中文文档` 会把最后一个「档」挤到第二行）；改标题后先在 1280px 宽度看侧边栏，不要只看 1920px。

## 21. 交付前的最小自证清单

1. `python scripts/verify_site.py --selftest` → `SELFTEST_PASS`；
2. `python scripts/verify_site.py --site <站点> --plan <计划> --mode full --hugo hugo` → `FAIL=0`；
3. `public/index.html` 有 `data-td-preset` 与顶栏「文档」入口，`public/offline-search-index.zh.*.json`、`public/llms.txt`、`public/_print/` 存在；
4. Mermaid 解析台读回 `REAL_FAIL=0`；
5. T0Level 文档无 `【`，未验证项写清原因；
6. 内容来源清单覆盖所有具体事实（MANUAL，人工过一遍）。
