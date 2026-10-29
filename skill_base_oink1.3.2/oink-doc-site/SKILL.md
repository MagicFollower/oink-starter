---
name: oink-doc-site
description: 从零搭建 Hugo + OINK v1.3.2 中文文档站的全流程（骨架 → 计划 → 内容 → 构建 → 验收）；当用户要求「新建/搭建文档站」「用 Hugo / OINK 做一个技术文档站」「从空目录起一个文档站」，或给出产品名与读者对象要求起站时使用。
when_to_use: 用户说要搭 OINK/Hugo 文档站、从 0 建站，或要把一批主题资料组织成可构建的中文文档站时。
argument-hint: <站点目录> [站点主题或一句话说明]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# 从 0 搭 Hugo + OINK 文档站

## Overview

在空目录里搭出一个**可离线构建、可挂任意子路径、导航与首页完整**的中文文档站，并在同一套判据上完成骨架验收与成品验收。完整浏览走 HTTP；`file://` 只适合看纯文字，原因见 Step 3。

主题 OINK v1.3.2 已内置（1,273 个文件 / 22,234,796 字节），Hugo、Go、字体、图标、搜索、Mermaid 运行时全部本地化，整个流程不联网。站点身份、首页、导航树与文章桩由一份 `site.plan.json` 驱动。骨架根目录带 `run.cmd`：顶部一个 PROJECT CONFIG 块（标题、默认端口、工具回退路径）随项目改，其余逻辑固定；Windows 双击即设离线环境、解析 Hugo/Go、从 8768 起选空闲端口启动并打开浏览器。

**贯穿全程的两条纪律：**

1. **判据先证明会红，再拿绿色当结论。** 先跑 `verify_site.py --selftest`，末行必须是 `SELFTEST_PASS`。真实站点的 `problems=0` 之前，必须看过一次注入缺陷被报出来。
2. **只读技能目录里的材料。** 写作规范、体裁样章、主题能力清单一律给本技能内的路径；站点副本是交付物，骨架阶段可能还不存在。

---

## 适用范围与锁定项

| 锁定项 | 现状 | 换了会怎样 |
|--------|------|------------|
| 主题 | OINK **v1.3.2**（Hugo Extended ≥ 0.166.0，本地 module replace） | 换主题则 `references/oink-theme-capabilities.md` 与 `assets/templates/` 全部作废 |
| 正文语言 | 中文单语 | `audit_content.py` 的 `NO_PAIN_OPEN` / `FEW_NEWBIE` / `ENGLISH_HEADING` 口径要改；`plan_site.py` 会拒绝非 `zh` |
| 内容模式 | `skeleton`（只搭骨架）与 `full`（正文写完）两挡 | 两挡判据不同，不能混绿 |
| 上游取源 | 无。事实来自用户材料、官方文档或真实命令输出 | 要整站复刻既有文档站，用 `replicate-doc-site` 技能，不要用本技能 |
| 构建 | Hugo Extended ≥ 0.166.0 + Go 与 `go.mod` 对齐（1.27.0） | 标准版 Hugo 编不了 SCSS；Go 版本不匹配会触发联网下载 |

不适用：多语言站、需要登录/内网取源、只写一两篇文档（直接照 `assets/example-docs/` 的体裁写即可）。

## Step 0 先把三个口径问清楚

用 AskUserQuestion 一次问完；**第一项没拍板不要建目录**。

| 口径 | 选项 | 影响 |
|------|------|------|
| **站点主题与读者** | 产品名、一句话定位、读者画像、有没有已有材料/官方文档 | 决定计划里的分类与文章清单；没有事实来源时只能写概念与结构，不能编默认值 |
| **内容模式** | ① 只搭骨架（`skeleton`）② 骨架 + 交付正文（`full`） | 决定 Step 4 是否写正文，以及最终用哪一挡验收 |
| **视觉预设** | ① 4 套全开（`paper/slate/ink/terminal`，**默认**）② 单套（`preset_menu: false`）③ Paper+Slate ④ 用户点名 | 只改计划里的 `preset` / `presetMenu`，不影响正文与判据 |

**视觉预设无回答 = 4 套全开**，不是「维持主题默认」；主题的默认是单预设。`preset` 必须在 `presetMenu` 列表里（漏了主题只 warn 不报错）。

同时确认输出目录与工具链：

```bash
hugo version   # 必须 extended，且 >= 0.166.0
go version     # 与 <站点>/go.mod 的 go 指令对齐（1.27.0）
```

Hugo 不在 PATH 时让用户给绝对路径，验收时用 `--hugo <exe>`，站点根 `run.cmd` 则用 `HUGO_EXE` 指向同一个 exe；Hugo 调不到 Go 时用 `--go-bin <go的bin目录>`。两者都找不到就报告缺什么并停在这里，不要现场换工具链。

如果 `go version` 打印 `go: downloading go1.27.0`，说明 PATH 选到了旧 Go（例如 `tools/go` 的 1.25.x）；把 `--go-bin` 指向 1.27.x 的 bin，或调整 PATH 顺序。验收时优先显式给 `--go-bin`。

## Step 1 落骨架

```bash
python <技能目录>/scripts/scaffold.py --out <站点目录>
```

期望输出：

```
theme -> <站点目录>/oink-main  copied=1273 skipped=0 files=1273
scaffold -> <站点目录>  copied=9 skipped=0
plan -> <站点目录>/site.plan.json  copied=1
```

主题副本必须含 `theme.toml`、`oink-main/…/scss/td/_presets.scss`、`oink-main/…/preset-config.html`、`oink-main/…/third_party/mermaid/mermaid.min.js`；`theme.toml` 的 `min_version` 必须是 `0.166.0`。缺任何一个都是主题副本不对，重拷，不要改配置救。

**接管/升级既有站点**（目录里已有 `content/`、`hugo.yaml`，不是本技能建的）：不要重跑 scaffold 去覆盖；按 `assets/scaffold/` 逐件补缺——`run.cmd`（只改 PROJECT CONFIG 块）、`doc/运行与构建（T0Level）.md`、`.gitignore`——再进 Step 2/3。`verify_site.py` 的 scaffold 行会检查 run.cmd 的存在与契约标记，缺件会直接红，别跳过。

## Step 2 写站点计划并生成

读 `references/site-plan.md`，把 `site.plan.json` 改成真实导航。骨架已复制一份示例计划，可直接改。

最小结构：

```json
{
  "site": {
    "title": "产品文档",
    "description": "面向研发与运维的中文文档站，覆盖概念、上手与生产实践。",
    "baseURL": "https://docs.example.com/",
    "preset": "paper",
    "presetMenu": ["paper", "slate", "ink", "terminal"]
  },
  "categories": [
    {
      "dir": "01-overview",
      "title": "概览",
      "weight": 1,
      "desc": "先回答它是什么、为什么需要它、由哪些部分组成。",
      "sections": [
        {
          "dir": "认识系统",
          "title": "认识系统",
          "weight": 1,
          "desc": "从痛点与设计目标出发，建立整体心智模型。",
          "articles": [
            {
              "file": "what-is-it.md",
              "title": "它是什么，为什么需要它",
              "weight": 1,
              "desc": "从真实痛点出发，说明系统解决的问题、核心抽象与适用边界。",
              "sources": ["用户提供的项目简介"]
            }
          ]
        }
      ]
    }
  ]
}
```

设计口径：3–6 个一级分类，按读者认知顺序排（概览 → 快速开始 → 核心机制 → 操作/参考 → 运维排障）；每分类 2–5 个板块，每板块 2–6 篇；一篇只归一个板块；文章 description ≥ 20 字，写「解决什么问题」。

```bash
python <技能目录>/scripts/plan_site.py --plan <站点目录>/site.plan.json --check-only
python <技能目录>/scripts/plan_site.py --site <站点目录> --plan <站点目录>/site.plan.json
```

期望先 `PLAN_OK`，再 `problems=0` / `placeholders_remaining=0`。`plan_site.py` 会重写 `hugo.yaml`、`README.md`、总览与分类/板块 `_index.md`、`data/home/zh.yaml`；**已存在的文章默认保留**（`articles_kept`），不会冲掉正文。生成器会在 `hugo.yaml` 写入 `menus.main` 的「文档」顶栏入口；OINK 1.3.2 的顶栏只渲染这个配置，不会自动挂 docs 入口，不要手删。

首页 `home.actions[].url` / `home.cta.url` 必须落在计划树内；文章页 URL 是 `docs/<分类>/<板块>/<文章>/`，漏写板块层会被 `BAD_HOME_URL` 拦住。

## Step 3 骨架验收

```bash
cd <站点目录>
GOTOOLCHAIN=local GOPROXY=off hugo --cleanDestinationDir
python <技能目录>/scripts/verify_site.py --site <站点目录> --plan <站点目录>/site.plan.json \
    --mode skeleton --hugo hugo [--go-bin <go的bin目录>]
```

构建期望：`0 ERROR`；只允许主题侧 `css.Sass: libsass was deprecated` 一条 WARN。骨架站实测 `Pages 51 / Static files 34 / Total in 1271 ms`。

验收表期望 `FAIL=0`，`plan/scaffold/build/preset/nav/audit/links` 全 PASS；`mermaid` 是 `MANUAL`，`delivery_doc` 在 skeleton 模式 SKIP，`source_ledger` 是 MANUAL。**MANUAL 不是通过**。

产物抽查：

- `public/index.html` 的 `<html>` 带 `data-td-preset="paper"`（或计划里的 preset）；
- `public/llms.txt`、`public/offline-search-index.zh.<hash>.json`、`public/_print/` 存在；
- 顶栏有「文档」入口，点击能进 `/docs/`（`verify_site` 的 `nav` 判据）；
- `run.cmd` 实跑一次：`NO_OPEN=1 NO_PAUSE=1 cmd /c run.cmd`，贴横幅（含端口顺延 Note）与 `Built in …` 行，再 `curl` 打印的 URL 确认 200；
- 浏览器打开首页/文档/文章页，侧边栏、面包屑、Appearance 面板、离线搜索都能用；390px 窄屏无横向溢出（方法见 `references/pitfalls.md` 第 11 条）。

浏览器请用 HTTP 打开（`hugo server` 或 `python -m http.server`）。`file://` 下 OINK 产物的 CSS/JS 带 `integrity` + `crossorigin`，会被浏览器按 CORS 拦截，只剩无样式文字，Mermaid、搜索、Appearance 都不可用；不要用双击结果做功能验收。

骨架模式可以给用户预览，但**不要说「内容已完成」**——文章桩还在。

Windows 上可直接双击站点根目录的 `run.cmd`：设置 `GOTOOLCHAIN=local`/`GOPROXY=off`；Hugo 依次取 `HUGO_EXE` → `where hugo` → 配置块 `HUGO_FALLBACK`，并校验 Extended；Go 依次取 `GO_BIN` → `GO_FALLBACK` → `where go`；未显式 `PORT` 时从 `DEFAULT_PORT`（默认 8768）探测到 `PORT_MAX`，被占用自动顺延并打印 Note；就绪后打开浏览器。脚本验证设 `NO_OPEN=1`、`NO_PAUSE=1`。**只改顶部 PROJECT CONFIG 块，不要动下面的逻辑**；逻辑层的坑见 `references/pitfalls.md` 第 22–25 条。

## Step 4 写正文（仅 full 模式）

先读 `references/writing-spec.md`，再按分类分批，一批 4–8 篇。每批给写作子代理五样：目标文件绝对路径、计划条目、写作规范绝对路径、对应体裁样章、事实来源。

必读材料（都在技能目录内）：

- `assets/scaffold/doc/技术文档编写规范.md`（445 行；站点里的 `doc/` 是交付物，可能还没落地或被手改）
- `assets/example-docs/00-骨架.md` + `01`~`04` 中对应体裁那一份
- `references/pitfalls.md` 第 19 条（事实来源）与第 3 条（判据词泄漏）

硬门槛（`--mode full` 会逐条咬）：

| 项 | 门槛 |
|----|------|
| 首个真实 H2 | 含「为什么」（`NO_PAIN_OPEN`） |
| 篇幅 | ≥ 260 行（`TOO_SHORT`） |
| 新人小结 | `💡 新人小结` ≥ 3（`FEW_NEWBIE`） |
| 图/表/代码 | mermaid ≥ 1、表格行对 ≥ 2、带语言标注代码块 ≥ 1 |
| 总结 | 必须有 `## 要点总结` |
| 禁用 | 方框字符、省略式表达、审计代码名入正文 |

每批写完：

```bash
python <技能目录>/scripts/audit_content.py --site <站点目录> --plan <站点目录>/site.plan.json \
    --mode full --min-lines 260
```

`problems=0` 才派下一批。**源文件/官方文档是唯一事实来源**：默认值、版本号、限制数值、命令输出查不到就不写，或写「上游未给出」；不要按同类系统惯例推定。每批在 `doc/内容来源.md` 追加来源记录。

新文章写完要删掉 `<!-- OINK-STUB: ... -->` 标记；留着会在 full 模式报 `STUB_PAGE`。

## Step 5 交付验收

1. 填 `doc/运行与构建（T0Level）.md`：每条命令贴真实输出；没跑的写「未验证」+ 原因；文件里不能留 `【` 占位。
2. 跑 Mermaid 真解析（MANUAL）：

   ```bash
   python <技能目录>/scripts/validate_mermaid.py --site <站点目录> --selftest
   python -m http.server 8767 --directory <站点目录>/_mermaid-harness
   msedge --headless=new --virtual-time-budget=8000 \
     --dump-dom http://127.0.0.1:8767/index.html
   ```

   期望 `TOTAL=<真实块数> REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS`。

3. 统一验收：

   ```bash
   python <技能目录>/scripts/verify_site.py --site <站点目录> --plan <站点目录>/site.plan.json \
       --mode full --hugo hugo [--go-bin <go的bin目录>] --report <站点目录>/doc/验收汇总.md
   ```

   期望 `FAIL=0`；`mermaid` / `source_ledger` 仍是 MANUAL。`delivery_doc` 必须 PASS。

4. 浏览器最后走一遍（HTTP）：首页 → 顶栏「文档」→ 文档总览 → 任一文章 → Appearance 切预设 → 搜索命中 → 390px 无溢出。截图/测量口径见 `references/pitfalls.md`。

5. 检查/补写站点根 `.gitignore`（见文末「收尾：.gitignore」）：`public/`、`resources/`、`_mermaid-harness/` 等生成物必须忽略；`oink-main/`、`content/`、`hugo.yaml`、`go.mod`、`site.plan.json` 不能被忽略。

6. 确认站点根有 `run.cmd` 且 `verify_site` 的 scaffold 行带 `run_cmd=ok`；以 `NO_OPEN=1 NO_PAUSE=1` 实跑一次，贴横幅与 `Built in …` 行（8768 被占时记录顺延端口）。

7. 报告给用户：站点绝对路径与 `tree`、分类/板块/篇数、`verify_site.py` 的真实汇总行、`verify_site.py --selftest` 的 `SELFTEST_PASS`、`run.cmd` 的启动实测输出、MANUAL 项与未验证项。不要只写「搭好了」。

---

## 失败处理

| 现象 | 先查 | 处理 |
|------|------|------|
| `PLAN_INVALID` + `BAD_HOME_URL` | 首页按钮/CTA 的 URL 是否漏了板块层 | 改成 `docs/<分类>/<板块>/<文章>/`，或直接删掉自定义 `home` 让生成器用默认值 |
| `plan_site.py` 报 `【` 残留 | 文章正文里是否用了全角中括号当标点 | 换成普通标点；配置/README 的占位由生成器替换，不要手改模板 |
| `hugo` 报 `failed to load modules` / 找不到 go | Go 是否在 PATH，版本是否与 `go.mod` 一致 | 用 `--go-bin <go的bin目录>`；设 `GOTOOLCHAIN=local GOPROXY=off` |
| `go version` 打印 `go: downloading go1.27.0` 或下载超时 | PATH 里选到了低于 `go.mod` 的旧 Go | 把 `--go-bin` 指向 1.27.x 的 bin，或调整 PATH 顺序；不要只设 `GOTOOLCHAIN=local` |
| 顶栏菜单区为空 / 没有「文档」tab | `hugo.yaml` 是否有 `menus.main` | 生成器会写 `identifier: docs`、`pageRef: /docs`；手删或旧站删了要补，`verify_site` 的 `nav` 判据会报 |
| 双击 `public/index.html` 只有无样式文字 | 是否用 `file://` 打开 | 改用 `hugo server` 或 `python -m http.server`；`integrity`/`crossorigin` 在 file:// 被 CORS 拦截，不是站点内容坏了 |
| 双击 `run.cmd` 窗口一闪而过 | Hugo 是否在 PATH，或 `HUGO_EXE` 是否指对 | 在终端执行 `run.cmd` 看完整报错；设置 `HUGO_EXE` 后重试 |
| `run.cmd` 报端口被占用 | 8768 是否已被其他服务使用 | `set PORT=9000` 后重新运行，或关闭占用端口的进程 |
| `run.cmd` 没有自动打开浏览器 | 系统默认浏览器/权限是否阻止 | 手动打开脚本打印的 `http://127.0.0.1:8768/`；服务本身通常已启动 |
| `verify` 的 scaffold 行报缺 run.cmd / 缺契约标记 | 站点是接管自建、或 run.cmd 还是旧模板 | 拷 `assets/scaffold/run.cmd` 覆盖，只填 PROJECT CONFIG 块；不要手拼批处理 |
| `run.cmd` 横幅里中文路径乱码 | 重定向日志的码页，不是脚本坏了 | 模板已带 `chcp 65001`；控制台直看正常，GBK 日志别当缺陷报 |
| 8768 被别的长驻 Hugo 占用 | 本机另有实例（先按 PID 的 CommandLine 确认归属） | 模板自动顺延并打印 Note；要固定端口先 `set PORT=`；停服务只杀自己起的 PID，别按名字批量杀 |
| 构建通过但外观菜单没有 4 套 | 先看 `public/index.html` 有没有 `data-td-preset` | 没有 = 主题副本是 1.0/1.1；有 = 检查 `preset_menu` 是否被注释 |
| `links` 报 broken | 首页 `data/home/zh.yaml` 的 `url`、`content/docs/_index.md` 的卡片链接 | 以 `public/` 产物为准；`unmapped` 非零时先对齐 URL 规则 |
| `audit` 报 `TOO_SHORT` / `FEW_NEWBIE` / `NO_MERMAID` | 文章是否还是桩或只有梗概 | 按 `references/writing-spec.md` 补正文；骨架阶段用 `--mode skeleton`，不要用 full 的绿骗自己 |
| `audit` 报 `STUB_PAGE` | 正文里是否还有 `OINK-STUB` 标记 | 写完正文后删掉整行；不要只在末尾补一句 |
| `audit` 报 `MISSING_INDEX` / `UNLISTED` | 是否只手建了目录/文章没改计划 | 改 `site.plan.json` 后重跑 `plan_site.py`，不要手补 `_index.md` 了事 |
| Mermaid 解析台 `HARNESS_ERROR` / 无读数 | 是否走了 http、`--virtual-time-budget` 是否够 | 用 `python -m http.server`，不要 `file://`；增大预算重跑 |
| 截图右侧被裁 | 截图宽是否小于 `window.innerWidth` | 先读 `innerWidth/scrollWidth`；用 CDP `Emulation.setDeviceMetricsOverride` 设真 390px 再截图 |
| `verify_site` 全绿但你怀疑没跑 | `verify_site.py --selftest` 是否 `SELFTEST_PASS` | 先修判据/夹具，不要信绿色 |

---

## Resources

- `references/site-plan.md` —— 计划 schema、URL 规则、校验代码、导航设计口径。Step 2 必读。
- `references/writing-spec.md` —— 规范条目与 21 类判据的映射、分批写作与分派词模板。Step 4 必读。
- `references/oink-theme-capabilities.md` —— 主题能力清单（按 OINK v1.3.2 实测）：callout 11 种、10 种数据围栏、mermaid 渲染链、离线搜索、侧边栏根、goldmark 三项、视觉预设、expo、构建约束与本技能实测记录。改 `hugo.yaml` 或写非正文页前必读。
- `references/pitfalls.md` —— 21 条真实踩坑：编码、cwd、判据自污染、Mermaid 真解析、预设产物、URL 层级、截图视口、事实来源等。
- `scripts/scaffold.py` —— 落主题与模板。退出码 0/1/2。
- `scripts/plan_site.py` —— 计划校验与站点生成；`--check-only` 只校验，`--selftest` 自证。
- `scripts/audit_content.py` —— 结构/文体审计；`--mode skeleton|full` 必须显式给；`--selftest` 自证。
- `scripts/check_links.py` —— 以 `public/` 为判据的站内链接检查；`--selftest` 自证。
- `scripts/validate_mermaid.py` —— 生成离线 Mermaid 解析台；`--selftest` 只证明注入样本生成正确，真解析是 MANUAL。
- `scripts/verify_site.py` —— 统一入口：plan/scaffold/build/preset/nav/audit/links/mermaid/delivery；`--selftest` 用四个子脚本 + 假站点注入缺陷自证。
- `assets/site.plan.example.json` —— 三分类示例计划，可复制成 `<站点>/site.plan.json` 后改。
- `assets/templates/hugo.yaml` —— 站点配置模板；由 `plan_site.py` 填值，不要直接拷进站点手改。
- `assets/scaffold/` —— 9 个骨架文件：`.gitignore`、`LICENSE`、`run.cmd`（PROJECT CONFIG 块 + 固定逻辑，只改配置块）、`go.mod`/`go.sum`、品牌 SVG、写作规范、T0Level 模板。
- `assets/example-docs/` —— 6 份体裁样章（216–540 行）；结构照它，事实不照抄。
- `assets/theme/oink-main/oink-main/` —— OINK v1.3.2 主题本体（1,273 文件）；`scaffold.py` 整目录拷入。
- `assets/fixtures/` —— 自证夹具（site / plan.json / expected.json）；只被 `--selftest` 消费。

## 自证基线（改脚本或夹具后重跑并更新本节）

```text
scaffold --selftest: theme_files=1273 scaffold_ok=True（含 run.cmd）; SELFTEST_PASS
plan_site --selftest: good problems=0; bad problems=12 codes=BAD_HOME_URL,BAD_PATH,BAD_PRESET,
  DUP_WEIGHT,NO_ARTICLES,THIN_DESC,WEIGHT_GAP; run.cmd title patch ok; SELFTEST_PASS
audit_content --selftest: full problems=26 codes=21; skeleton problems=11 codes=10;
  genre_checks=11/0; SELFTEST_PASS
check_links --selftest: stub_public_pages=31 observed_codes=4; SELFTEST_PASS
validate_mermaid --selftest: blocks=23 injected=2; SELFTEST_PASS（真解析 MANUAL）
verify_site --selftest: 4 子脚本 PASS；scaffold/preset/nav/delivery/plan/audit/run.cmd 缺文件/
  run.cmd 缺标记 注入均 FAIL，preset/nav 的 minify 去引号形态 PASS、run.cmd 恢复 PASS；SELFTEST_PASS
```

端到端（2026-10-25，Hugo v0.168.0 Extended + Go 1.27.2）：

```text
骨架站（示例计划）: Pages 51 / Static 34 / 1271 ms；verify --mode skeleton -> FAIL=0 MANUAL=2 PASS=7 SKIP=1
成品站（Zookeeper）: Pages 63 / Static 41 / 1590 ms；verify --mode full     -> FAIL=0 MANUAL=2 PASS=8 SKIP=0
Mermaid: Zookeeper 站 TOTAL=18 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS；骨架解析台 blocks=2（未单独跑真解析）
搜索「安装」4 条命中；顶栏「文档」tab 73×36 可进 /docs/；390×844 scrollWidth=390 无横向溢出
Appearance 可切 Slate 并写 localStorage；file:// 直开只有无样式文字（完整功能走 HTTP）
```

## 未确证项

- **Expo 相册**的浏览器端交互（原图查看器手势、键盘流、记忆布局）未实测；本技能不生成 expo 页面。
- **LLMSFULL / NAVJSON / BookManifest** 三种输出未启用、未实测；模板与 schema 可读。
- **minify 发布档**在 Zookeeper 站实测通过（120 文件 / 8,622,116 字节），真实主机部署未验证。
- **`--panicOnWarning` 严格闸门**未实测；主题侧 libsass WARN 会致败，严格闸门按主题契约用 Hugo 0.166.0。
- **多语言**不支持；`lang` 非 `zh` 会被计划校验拒绝。
- **ink / terminal 两套实验预设**只验证了菜单可切换，未逐页人眼核对正文/代码块/表格的对比度。
- **`file://` 完整功能**已实测不可用：CSS/JS 的 `integrity` + `crossorigin` 在 origin `null` 下被 CORS 拦截，只剩无样式文字；完整浏览必须 HTTP。这不是未验证，是浏览器限制。

## 收尾：编写 `.gitignore`

站点根必须有 `.gitignore`，它是交付物的一部分，不是可选项。`scaffold.py` 已带一份基线；如果目标目录已有 `.gitignore`，**先读再补缺项，不要覆盖用户已有规则**。

**必须忽略**（构建产物、缓存、本地验证台、依赖与日志，不应入库）：

```gitignore
/public/
/resources/
/.hugo_build.lock
/.hugo_cache/
/.tmp/
/_mermaid-harness/
node_modules/
*.log
.DS_Store
Thumbs.db
desktop.ini
.idea/
.vscode/
*.swp
```

骨架基线（`assets/scaffold/.gitignore`）已含上面全部条目；`*.log` 是给构建/探针重定向留的口子，`Thumbs.db`、`desktop.ini` 在 Windows 桌面上会自己长出来。接管既有站点时**先读它的 `.gitignore`，只补缺项，不要覆盖已有规则**。

**必须不忽略**（少了就无法离线构建，或丢配置/正文）：

- `oink-main/`：本地主题副本，`go.mod` 的 replace 指向它；忽略后新环境无法构建。
- `content/`、`data/`、`static/`、`layouts/`（有站点级覆盖时）。
- `hugo.yaml`、`go.mod`、`go.sum`、`site.plan.json`。
- `run.cmd`：Windows 双击启动入口，丢了就只能手动敲 `hugo server`。
- `README.md`、`doc/`。

**检查命令**（在 Git 仓库内）：

```bash
git check-ignore -v public resources _mermaid-harness .tmp oink-main content hugo.yaml site.plan.json run.cmd doc
```

输出里应出现 `public`、`resources`、`_mermaid-harness`、`.tmp`，不应出现 `oink-main`、`content`、`hugo.yaml`、`site.plan.json`、`run.cmd`、`doc`。目录不是 Git 仓库时不要为了这条检查去执行 `git init`；直接读 `.gitignore` 核对条目即可。

如果发布流程确实要提交 `public/`，必须在 `doc/运行与构建（T0Level）.md` 与 `README.md` 写明理由，并同步调整 `.gitignore`；默认不提交构建产物。
