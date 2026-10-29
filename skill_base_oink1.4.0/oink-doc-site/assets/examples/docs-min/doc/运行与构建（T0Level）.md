# 运行与构建（T0Level）

读者设定：从没碰过这个工程的人。下面每条命令都跑过，输出贴的是**本机示例读数**——换机器请按同样命令重跑一遍，把数字换成你自己的，不要把本文的数字当验收依据。

环境口径：Hugo Extended ≥ 0.168.0 + Go ≥ 1.27.3（取站点与主题两处 `go.mod` 的最大下界），离线可构建。

## 一、前置要求

| 工具 | 要求 | 说明 |
|------|------|------|
| Hugo | Extended ≥ 0.168.0 | 标准版编不了主题的 SCSS；`hugo version` 输出里必须带 `extended` |
| Go | ≥ 1.27.3 | 是**实际被执行**的那个 `go.exe`；低于下界时 Go 会自己去 proxy 拉工具链，离线机必然超时 |

```text
hugo version   # 需含 extended，且 >= 0.168.0
go version     # 需 >= 1.27.3
```

环境变量：`GOTOOLCHAIN=local`、`GOPROXY=off`。两种失败形状：`binary with name "go" not found in PATH` 是没装；`go: downloading go1.27.3 …` 是装了但低于下界。设 `GOTOOLCHAIN=local` 只改报错形态，不会让旧 Go 够用。

## 二、从示例包生成站点

```bash
python <技能目录>/scripts/scaffold.py --out <站点目录>
python <技能目录>/scripts/use_example.py --example docs-min --site <站点目录>
```

`use_example.py` 会复制 `site.plan.json` 与正文、执行 `plan_site.py`，并打印下一条命令。它拒绝覆盖已有正文，除非加 `--force`。

本机示例读数：`scaffold -> theme copied=1292 files=1292`；`plan_write: generated=9 articles_stubbed=0 articles_kept=2 placeholders_remaining=0`。

## 三、构建

```bash
hugo --cleanDestinationDir
```

本机示例读数：

```text
 Pages            │ 35
 Static files     │ 34
Total in 1428 ms
```

判据：0 个 ERROR；只允许主题侧 `css.Sass: libsass was deprecated` 一条 WARN（主题契约禁止 `--panicOnWarning`，别加）。

## 四、本地预览

```bash
run.cmd            # Windows：双击或命令行；NO_OPEN=1 NO_PAUSE=1 便于脚本验证
```

`run.cmd` 会设好 `GOTOOLCHAIN=local`/`GOPROXY=off`，按 `GO_BIN → GO_FALLBACK → where go` 取 Go、按 `HUGO_EXE → where hugo → HUGO_FALLBACK` 取 Hugo，未显式指定 `PORT` 时从 8768 起找空闲端口并打印 Note。

完整功能必须走 HTTP：`file://` 打开 `public/index.html` 时，production 产物的 `integrity`+`crossorigin` 会被按 CORS 拦截，只剩无样式文字。

## 五、内容审计

```bash
python <技能目录>/scripts/audit_content.py --site . --plan site.plan.json --mode full --min-lines 260
```

本机示例读数：`articles=2 expected=2 dirs=5 stubs=0 problems=0 mode=full genre_checks=11`。

两篇正文都过结构门槛：≥260 行、3 个「💡 新人小结」、≥1 张 Mermaid、≥2 组表格、≥1 个带语言代码块、有「要点总结」，首个真实 H2 用「为什么…」开头。

## 六、统一验收

```bash
python <技能目录>/scripts/verify_site.py --site . --plan site.plan.json --mode full \
    --hugo hugo --go-bin "<go1.27.3 的 bin 目录>"
```

本机示例读数：`FAIL=0 MANUAL=2 PASS=8 SKIP=0`。`MANUAL` 两项是 Mermaid 真解析与内容来源核对，**不是通过**。

## 七、Mermaid 真解析与产物核对

```bash
python <技能目录>/scripts/validate_mermaid.py --site . --selftest
python -m http.server 8899 --directory _mermaid-harness
msedge --headless=new --disable-gpu --virtual-time-budget=9000 --dump-dom http://127.0.0.1:8899/index.html
```

读页内元素那一行（不是脚本里的同名字符串常量）。本机示例读数：`TOTAL=3 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`——`TOTAL` 按源文统计，含写在代码围栏里的示例块。

产物层核对三例：`<table id="param-migration-live" class="wide td-table--wide">`、`<table id="error-codes-live" class="expand">`、`<table id="wide-plus-expand" class="wide expand td-table--wide">`；`.expand` 另带 `td-table-frame`，页内共享一个 `data-td-table-reader` 抽屉。

## 八、常见故障

| 现象 | 结论 |
|---|---|
| `hugo server` 打出 `go: downloading go1.27.3` 后失败 | 命中的 Go 低于下界；换实际执行的那个 go.exe，改站点 `go.mod` 没用（主题那条也参与取下界） |
| 页面 200 但样式全丢、logo 碎图标 | `baseURL` 带了子路径，与 `relativeURLs` 冲突；改回根重跑计划与构建，`check_links` 的 broken 会归零 |
| 表格标记写了没生效 | 属性行必须**写在表格之后紧贴**；id 必须是 ASCII（`[A-Za-z][A-Za-z0-9_.:-]*`），中文 id 会被丢并打 WARN |
| `{{< step >}}` 报 `template for shortcode "step" not found` | steps 没有子 shortcode，条目是一个三级标题算一步 |
| 构建通过但相册页不出图 | `type: expo` 要写在相册页自己的 front matter 上 |
