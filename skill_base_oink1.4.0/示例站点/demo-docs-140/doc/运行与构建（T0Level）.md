# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。下面每条命令都在本机跑过，输出原样贴在「实测输出」里；没跑的显式写「未验证」并给原因。

环境口径：Hugo v0.168.0 Extended + Go 1.27.3，Windows 11 本机，非首次构建（模块已本地化，无联网）。技能版本基线：OINK v1.4.0。

## 一、前置要求

| 工具 | 本机路径 | 为什么必须是它 |
|------|---------|----------------|
| Hugo | `C:\Users\webtu\tools\hugo\hugo.exe`（与 `D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe` 同版本） | 主题用 SCSS，标准版编不了；OINK 1.4.0 要求 Extended ≥ 0.168.0 |
| Go | `C:\Users\webtu\tools\go1.27.3\go\bin\go.exe` | 必须 ≥ 1.27.3：取本站 `go.mod` 与被 `replace` 的主题 `go.mod` 两处 `go` 指令的最大值 |

```text
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64 BuildDate=2026-10-13T16:42:50Z VendorInfo=gohugoio
go version go1.27.3 windows/amd64
```

环境变量：`GOTOOLCHAIN=local`、`GOPROXY=off`。两种失败形状要分清——没装 Go 报 `binary with name "go" not found in PATH`；装了但低于下界报 `go: downloading go1.27.3 …` 然后连接超时（Go 正试图自己拉工具链）。设 `GOTOOLCHAIN=local` 只会把后者换成 `go.mod requires go >= 1.27.3`，不会让旧 Go 够用。

本机 PATH 里排第一的是 `C:\Program Files\Go\bin\go.exe`（go1.27.2，**不够**），所以裸敲 `hugo server` 会失败；`run.cmd` 按 `GO_BIN → GO_FALLBACK → where go` 取到 1.27.3 才跑得起来。

## 二、构建

```bash
hugo --cleanDestinationDir
```

实测输出（截取统计段）：

```text
Start building sites …
hugo v0.168.0-e27a6760c5547237f87d353aebe0580feadb20f4+extended windows/amd64

WARN  deprecated: css.Sass: libsass was deprecated in Hugo v0.153.0 and will be removed in a future release. Use dartsass instead. See https://gohugo.io/functions/css/sass/#dart-sass

                  │ ZH
──────────────────┼────
 Pages            │ 35
 Static files     │ 34
Total in 1396 ms
```

判据：0 个 ERROR。唯一 WARN 是主题侧的 libsass 提示，属固有输出——**不要加 `--panicOnWarning`**，1.4.0 的主题契约明确禁止在任何构建、检查、预览与 CI 里开它。同一份内容在本轮的三次构建耗时分别是 1339 / 1386 / 1398 ms，量级稳定；这里贴最后一次。

## 三、本地预览

```bash
run.cmd                    # 双击或命令行
```

实测输出（`NO_OPEN=1 NO_PAUSE=1` 跑法，横幅与统计段）：

```text
 Project : C:\Users\webtu\Desktop\silo文档站\示例站点\demo-docs-140
 Note    : port 8768 was busy, using 8769.
 Hugo    : D:\Apps\hugo_extended_0.168.0_windows-amd64\hugo.exe
 Go      : C:\Users\webtu\tools\go1.27.3\go\bin\go.exe
 Note    : Go 1.27.3 or newer is required by go.mod.
Starting Hugo server without opening a browser...
 Pages            │ 35
Built in 677 ms
```

实测 `http://127.0.0.1:8768/` 返回 200、标题「OINK 1.4.0 文档站示例」，页面里的 `./scss/main.css` 与 `./icons/logo.svg` 也都返回 200。

**`baseURL` 必须是根。** 本站一度写成 `https://docs.example.com/demo-docs-140/`，结果 `relativeURLs` 把子路径烤进每个资源 URL：首页写的是 `./demo-docs-140/scss/main.css`，浏览器从 `/demo-docs-140/` 解析成 `/demo-docs-140/demo-docs-140/scss/main.css` → 404，页面 200 却完全无样式、logo 变碎图标。当时的 `check_links` 报 `broken=191`（16 个页面、191 条资源），改回根之后 `broken=0`。要挂子路径请交给部署目录，不要写进 `baseURL`。

不要用 `file://` 打开 `public/index.html`：主题给 CSS/JS 写了 `integrity` + `crossorigin`，`file://` 的 origin 是 `null`，会被按 CORS 拦截，只剩无样式文字。

## 四、结构审计

```bash
python <技能目录>/scripts/audit_content.py --site . --plan site.plan.json --mode full --min-lines 260
```

实测输出：

```text
articles=2 expected=2 dirs=5 stubs=0 problems=0 mode=full genre_checks=11
```

两篇正文都达到篇幅与结构门槛。审计按源文统计，因此写在代码围栏里的示例也算一次；页面实际出现的图数要看产物里的舞台数（下一节）。

## 五、统一验收

```bash
python <技能目录>/scripts/verify_site.py --site . --plan site.plan.json --mode full \
    --hugo hugo --go-bin "C:\Users\webtu\tools\go1.27.3\go\bin"
```

实测汇总行：

```text
FAIL=0 MANUAL=2 PASS=8 SKIP=0
```

`MANUAL` 两项是 Mermaid 真解析与内容来源清单，**不是通过**：前者要把解析台跑起来读回一行结果，后者要人工核对来源是否覆盖全部事实。

## 六、Mermaid 真解析

```bash
python <技能目录>/scripts/validate_mermaid.py --site . --selftest
python -m http.server 8901 --directory _mermaid-harness
msedge --headless=new --disable-gpu --virtual-time-budget=12000 --dump-dom http://127.0.0.1:8901/index.html
```

实测读回（取页内元素内容，不取脚本里那份同名字符串常量）：

```text
id="out">TOTAL=3 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS
```

`TOTAL` 是按源文正则统计的块数，包含正文里当作示例写在代码围栏中的那张图；真正会在页面上出现的图有 2 张（产物中舞台数为 1 每页）。判据本身只回答「语法能不能解析」。

## 七、产物层核对（1.4.0 新特性是否真的生效）

先说一条**实测纠正的语法**：goldmark 的块属性行要写在**表格之后并紧贴**。写在表格上方不会绑定（产物里那张 `<table>` 既无 id 也无类，主题也不告警）。这条是用三变体探针页量出来的，探针页已删除。

| 检查 | 命令 | 实测 |
|---|---|---|
| `.wide` 是否落到表上 | `grep -o '<table[^>]*>' …feature-tour/index.html` | `<table class="wide td-table--wide">` 1 处 |
| `.expand` 是否出框与抽屉 | `grep -c 'td-table-frame'` / `'data-td-table-reader'` | 1 / 1，展开按钮 2 个 |
| 未用标记的页是否零开销 | `grep -c 'data-td-table-reader' public/index.html` | 0 |
| 卡片列表变体 | `grep -o 'class="td-content-cards[^"]*"'` | 2 个容器带 `td-cards-list` |
| 步骤紧凑变体 | `grep -o 'class="td-steps[^"]*"'` | 2 个容器带 `td-steps-compact` |
| 命令条 | `grep -o 'class="td-code[^"]*"' \| sort \| uniq -c` | `td-code td-code--untitled td-code-command` 1 处（另有 5 个普通块） |
| 没图的页面不挂 PlantUML | `grep -c plantuml public/index.html` | 0 |
| 有 PlantUML 的页按需挂载 | 在 diagrams 页搜 `plantuml` | 引用 `plantuml-browser-zh` 运行时块 |
| Mermaid 舞台与源码并存 | 数两个类名 | 舞台 1、源码块 1 |
| 共享控件运行时已产出 | `find public/js -name 'diagram*'` | 1 个块 |

未验证项（写清楚，别当成通过）：PlantUML 在浏览器里真的画出图、图表控件（缩放/适应/看源/下载 SVG/键盘）、颜色模式切换后的重渲、390 像素窄屏的横向溢出、打印档里的图呈现、`.expand` 抽屉打开后关闭是否准确还原阅读位置。本轮只做了构建与产物层核对，没有逐页走查。

补充一条踩坑记录：`{{< steps >}}` **没有** `step` 子 shortcode，条目是「一个三级标题算一步」。误写 `{{< step title="…" >}}` 会让构建直接失败：`template for shortcode "step" not found`。

## 八、重新生成与常见故障

正文改了直接重跑第二节的构建命令；导航结构改了要改 `site.plan.json` 后重跑 `plan_site.py`，不要手补 `_index.md`。

| 现象 | 结论 |
|---|---|
| `hugo server` 打出 `go: downloading go1.27.3` 后失败 | 命中的 Go 低于下界，见第一节；换执行的那个 go.exe，不是改本站 `go.mod` |
| 构建报 `template for shortcode "step" not found` | 步骤的条目不是子 shortcode，本站用「一个三级标题算一步」的写法 |
| 页面 200 但样式全丢、logo 碎图标 | `baseURL` 带了子路径，与 `relativeURLs` 冲突；改回根后重跑 `plan_site.py` 与构建，`check_links` 的 `broken` 会列出双前缀那批资源 |
| 表/卡片/命令条看不出效果 | 确认写的是真实块而不是代码围栏里的示例；再按第七节去产物里找痕迹 |
