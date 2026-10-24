---
name: replicate-doc-site
description: 把一个既有文档站（Docusaurus/VitePress/GitBook/自站）整站复刻成本地 Hugo + OINK 知识站点的全流程，含多版本文档合并、逐篇覆盖矩阵、按体裁的重写规范、构建验证与判据自证夹具。当用户要求「复刻这个文档站」「把某站搬进 OINK 主题」「重整一批技术文档成站」，或给出 docs 网址/仓库要求照样式重做时使用。产出为可独立构建、可离线打开、可验证覆盖率的文档站目录。
argument-hint: <上游站点或仓库地址/路径> [输出目录]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# 文档站复刻（Hugo + OINK）

## Overview

复刻不是爬下来贴上去。上游文档站常见三件事同时不满足：**版本分叉**（同一内容在 4.x/5.0 各写一遍且有差异）、
**粒度过碎**（一篇只讲一个参数）、**结构按产品菜单排**（而不是按读者的认知顺序）。
本技能把它们重组成「按知识板块合并的长文」，并留下**可机检的覆盖证据**——
一篇都不漏、漏了能指出来、指出来的是人判断过的。

主题本体（OINK **v1.3.2**，1,273 个文件 / 22,234,796 字节）已打进 `assets/theme/oink-main/`，全流程离线，不联网。

**贯穿五步的唯一纪律：任何判据，先证明它会红，再拿它的绿色当结论。**
本技能自带一套 mini 站点夹具（`assets/fixtures/`：31 个 content 页 + 26 个源文件 + 5 份矩阵），
一条 `python scripts/verify_all.py --selftest` 就把「20 个红样本逐条报出、5 个合规样本一条不误报」钉成断言。
不要拿真实站点的 `problems=0` 当结论——先跑自证。
自证的临时目录落在**当前工作目录的 `.tmp/`**（可用环境变量 `REPLICATE_TMP` 改指他处；`.gitignore` 已忽略该目录）——
不用系统 `%TEMP%`，因为 Windows 沙箱常把 Python 在托管 Temp 根里建子目录直接拒掉（WinError 5），selftest 第一步就会炸。

**第二条纪律：技能只读自己目录里的文件。** 所有要「先读一遍」的材料——写作规范、体裁样章、
主题能力清单、骨架模板——一律给技能内的路径（`assets/scaffold/…`、`assets/example-docs/…`、
`references/…`）。`scaffold.py` 会把其中一部分拷进新站当**交付物**，但那是产物不是输入：
骨架还没落地时站点副本根本不存在，指向它的阅读指令必然落空。
派子代理时同理，材料路径只写技能目录内的绝对路径。

---

## 适用范围与判据口径

这套判据不是中立的，换场景前必须知道它锁死了什么：

| 锁定项 | 现状 | 换了会怎样 |
|--------|------|------------|
| 主题 | OINK **v1.3.2**（Hugo Extended ≥0.166.0，本地 module replace） | 换主题则 `references/oink-theme-capabilities.md` 与 `assets/scaffold/` 全部作废，只有矩阵与判据脚本可留 |
| 正文语言 | 中文技术长文 | `audit_structure.py` 的 `SKIP_WORDS`、`ENGLISH_HEADING`（内联的 `[\u4e00-\u9fff]` 汉字范围判定）、`NON_ZH_FILE` 三条要改；`check_coverage.py` 的 `CJK` 术语口径要改 |
| 文体 | 「痛点开场 → 机制 → 表格 → 图 → 要点总结 → 新人小结」的长文（≥260 行） | `--min-lines`、`NO_PAIN_OPEN`、`NO_SUMMARY`、`FEW_NEWBIE` 四条要改或关掉 |
| 上游取源 | GitHub 仓库（`git/trees` + raw + gh-proxy 回退） | 换 GitLab/内网要重写 `fetch_source.py` 的取数层，字节校验逻辑可留 |

`audit_structure.py` 的 docstring 里有一份「口径声明」，逐条列出换语言/换文体时必须改的常量
（`BOX_CHARS`、`SKIP_WORDS`、`SELF_CHECK_LITERALS`、`FEW_NEWBIE`/`NO_PAIN_OPEN`/`NON_ZH_FILE` 阈值、`--min-lines`）。
改判据前先读它，别在交付物里留一套咬不住自己文体的判据。

| 用 | 不用 |
|----|------|
| 整站搬运或重整成静态站 | 只写一两篇文档（直接照 `assets/example-docs/` 的体裁写即可） |
| 上游有多版本、需要合并与差异标注 | 上游闭源/需登录且拿不到源文件（先解决取源） |
| 要求「覆盖率可证明」「离线能打开」 | 只要一个能搜的 wiki（现成 SSG 默认结构更快） |
| 交付要能被下一个人机检验收 | 一次性交付、无人复核（判据的成本收不回来） |

## Step 0 先把四个口径问死（用户没拍板前不动手）

这四项决定后面所有工作量，**必须用选项形式（AskUserQuestion）让用户拍板**。
在他选定之前不要建骨架、不要取源、更不要开始写正文——第一项选错，后面全部返工。
**例外是「视觉预设」：问到就停，没答也不等**，按它的默认值（4 套全开）继续，见下表最后一行。

| 口径 | 选项 | 影响 |
|------|------|------|
| **内容形态** | ① **完整复制**：逐字搬运原文，只补 front matter、改站内链接与图片路径<br>② **按规范重写**：按知识板块合并（N 篇碎文 → 20~35 篇长文），套 `assets/scaffold/doc/技术文档编写规范.md` 的体裁 | 决定矩阵形状、总工作量，以及**哪些判据适用** |
| 版本盘子 | ① 最新版 ② 最新版 + 历史版全量 | 决定取源范围与查重工作量 |
| 交付形态 | ① 只要内容 ② 独立可构建站 + 构建验证 | 决定是否装工具链 |
| **视觉预设**（读者可切换的主题） | ① **4 套全开**（`preset_menu: [paper, slate, ink, terminal]`，**默认**）② 1 套（`preset_menu: false`）③ Paper+Slate 两套 ④ 用户点名的其它列表 | 只改 `hugo.yaml` 的 `ui.preset` / `ui.preset_menu` 两行，不影响正文与判据 |

**视觉预设这一项的三条硬规矩**（历史上它是静默失效的，别再看错一遍）：

- **无回答 = 全部 4 套**，不是「维持主题默认」。主题的默认是 `preset_menu: false`（只有一个预设），
  而 `assets/scaffold/hugo.yaml` 已把 4 套写成实值默认——**不要把它改回注释**，也不要把「用户没提」当成「只要 1 套」。
- `preset`（站点默认观感，`paper` 或 `slate`）必须出现在 `preset_menu` 列表里；漏了主题只 warn 不报错。
  想要 1.0/1.1 的技术风就写 `preset: slate`，但列表照旧 4 套。
- 预设体系是 **OINK 1.2+ 才有的**。`preset_menu` 配在 1.0/1.1 的主题副本上完全不生效，
  而且**构建照样通过、一个错都不报**（那份副本连 `_presets.scss` 与 `preset-config.html` 都没有，
  产物的 `<html>` 上也就没有 `data-td-preset`）。所以 Step 3 之后必须按这条核：
  副本内要有 `assets/scss/td/_presets.scss`、`_experimental-presets.scss`、`layouts/_partials/preset-config.html`，
  构建产物里 `data-td-preset` 要能在 `public/index.html` 上读到值。1.3.2 副本实测 1,273 个文件、
  `theme.toml` 的 `min_version = 0.166.0`；1,196 文件 / `0.160.1` 那份是 1.0.0，没有这套能力。

**提问时必须把判据差别一起讲清楚**，否则用户会以为「完整复制」也能拿到同一套质量结论：

| | ① 完整复制 | ② 按规范重写 |
|---|---|---|
| 验收命令 | `verify_all.py --mode copy` | `verify_all.py`（默认 `--mode rewrite`） |
| 生效判据 | 12 类：矩阵一致性（`NOT_WRITTEN`/`UNLISTED`/`MISSING_INDEX`）、`DUP_WEIGHT`/`WEIGHT_GAP`、front matter 三类、`BROKEN_IMAGE`、`SCRATCH_PATH`、`SELF_CHECK_LEAK`、`NON_ZH_FILE` | 上面 12 类 + 10 类文体判据（`TOO_SHORT`/`NO_PAIN_OPEN`/`NO_SUMMARY`/`FEW_NEWBIE`/`NO_MERMAID`/`NO_CODE`/`FEW_TABLES`/`BOX_CHARS`/`SKIP_LANGUAGE`/`ENGLISH_HEADING`） |
| 为什么 | 上游原文本来就不满足「痛点开场 / ≥260 行 / ≥3 个新人小结 / ≥1 个 mermaid」，报了只是噪音 | 重写就要对得起这套体裁，判据必须全部咬住 |
| 额外要证明的 | 与源文件逐字一致（自己加 MD5 或 diff 判据，本技能不内置） | 覆盖率分诊表逐条人工判定 |

`audit_structure.py` 的汇总行会带 `mode=`，别让 copy 模式的绿被当成 rewrite 模式的绿。
两种模式的判据互为补集，自证实测 `文体判据沉默=10/10 结构判据仍生效=12/12`，10+12 正好等于
rewrite 模式的可达判据代码总数 22——划错边界会当场报出来。

参考答案（本项目 119 篇 → 31 篇，10 分类 20 板块，选 ②重写 + 历史版全量 + 独立可构建站 + 预设 4 套全开——
最后这项用户没点名，就走默认，不追问第二轮）。
若上游之外还有素材（同级示例工程、二进制发行包、本地附件），此时就要问清是否纳入矩阵——
纳入的话它们的 source 前缀走 `--skip-prefix`（见 Step 2）。

---

## Step 1 取源

```
python scripts/fetch_source.py --repo <owner>/<repo> --ref <branch-or-tag> \
    --include 'docs/**/*.md' --include 'versioned_docs/version-5.0/**/*.md' \
    --out <暂存源目录> --jobs 8
```

- 直连 raw.githubusercontent 失败或字节数不符时自动改走 `https://gh-proxy.com/<原 URL>` 重试；
  逐文件按 tree 的 size 校验，输出 `wanted=N ok=N failed=0 bytes_on_disk=…`。
- `--include` 用的是**严格 glob 而不是 fnmatch**：`**/` 才跨目录，`*` 不跨 `/`。
  `docs/**/*.md` 命中 `docs/a/b.md` 也命中 `docs/a.md`。每个 pattern 会打印 `matched=N`，
  0 命中直接 WARN——写错 pattern 的代价是「静默少取一半源」，比报错阴。
  先跑 `python scripts/fetch_source.py --selftest`（9 个 glob 用例）确认口径。
- 仓库名与默认分支要先用 `gh api` 确认。实例：`apache/rocketmq-website` 不存在，
  实为 `apache/rocketmq-site`，默认分支 `new-official-website`。
- 本地已有源（用户给了目录或 zip）就跳过取源，但必须记录文件数与总字节，后续判据要用。

**配图另走一趟**：先用 `--include '**/picture/**' --tail-after picture --out <site>/static/picture`
把图树拍平到站点（上游按版本各存一份，`--tail-after` 把多棵树合并到同一个 static 根）。
Step 2 之后再用 `picture_map.py` 生成「哪篇能用哪些图」的清单，写作时只准引用清单内的路径。

## Step 2 定覆盖矩阵（本技能的核心资产）

把归属关系写成**可执行数据结构**，不要写成说明文档。最小形态：

```json
{"categories": [{"dir": "01-overview", "title": "…", "icon": "fa-solid fa-compass",
                 "weight": 1, "desc": "…",
                 "sections": [{"dir": "认识X", "title": "…", "weight": 1, "desc": "…",
                                "articles": [{"file": "a.md", "title": "…", "desc": "…",
                                              "weight": 1,
                                              "sources": ["4x:00-introduction/01whychoose.md"]}]}]}],
 "prefixes": {"4x": "docs", "50": "versioned_docs/version-5.0"}}
```

一份矩阵驱动五个消费者：`gen_skeleton.py` 建目录树、`matrix_check.py` 自检、
`audit_structure.py` 双向比对磁盘、`check_coverage.py` 核对术语与数值、`picture_map.py` 出配图清单。

写完立刻自检，必须 `problems=0`：

```
python scripts/matrix_check.py --matrix matrix.json --src <暂存源目录> \
    --prefix 4x=docs --prefix 50=versioned_docs/version-5.0 --report <站点>/doc/复刻覆盖矩阵.md
```

失败判据代码：`SCHEMA` / `DUP_WEIGHT` / `WEIGHT_GAP` / `NO_SOURCES` / `BAD_PREFIX` /
`NONEXISTENT` / `UNCOVERED` / `DUPLICATED`。`--report` 顺手生成收尾要交的覆盖矩阵文档。

多版本必做逐字节查重，`matrix_check.py` 打印两组（都不是失败项，是给写作的指令）：

- `same_name_pairs` —— 各 prefix 根之间按 basename 的同名对，MD5 分「相同 / 有差异」。
  相同 → 合并成一份正文，只在版本适用处加 callout；有差异 → 正文里必须显式对比。
- `per_article_pairs` —— 同一篇 `sources` 内部的同名对；`differing` 的那些不写对比就是漏。

另有一类边界要单独确认：同名且逐字节相同、却被拆进两篇不同文档（本站是两版 `02admintool.md`）。

**树外源**：矩阵可以混有不在上游文档树内的源（同级示例工程、本地附件）。给它们一个自己的前缀
（如 `local:`），并在所有脚本上一律带 `--skip-prefix local`——它们只计入 `out_of_scope`，
不参与存在性核对、认领去重、查重与术语覆盖。**未声明的未知前缀必须报错**，那是防前缀写错的闸门，
不要拿 `--skip-prefix` 当消音器。

详细 schema、不变量、分派词模板都在 `references/matrix-and-prompts.md`。

## Step 3 搭骨架

```
python scripts/scaffold.py --out <新站目录>            # 拷主题 + 模板，报告剩余占位数
python scripts/gen_skeleton.py --site <新站目录> --matrix matrix.json
```

`scaffold.py` 实测：`copied=1273`（主题）+ `copied=14`（模板）+ `placeholders_remaining=71`（分布在 6 个文件）。
然后手工做五件事：

1. 把全角中括号占位换成真实内容，直到 `scaffold.py` 报 `placeholders_remaining=0`。
   `assets/scaffold/hugo.yaml` 的 goldmark 三项与 `relativeURLs: true` 不许删（作用见 `references/oink-theme-capabilities.md`）。
   批量替换的正则**必须排掉换行**，否则会从第一个占位一路吞到下一个右括号，把中间整行配置带走。
2. `assets/scaffold/content/docs/_index.md` 的卡片导航与 `assets/scaffold/data/home/zh.yaml` 的
   `url:` 必须换成真实分类目录。刚搭好的骨架跑 `check_links.py` 实测报
   `links_checked=9 home_urls=6 broken=8`——那是待办清单，不是误报。
   首页数据文件是历史上的系统性盲区：分类改名最先断的就是首页卡片，而旧版判据根本不看 `data/`。
3. `scaffold.py` 已把 `assets/scaffold/doc/技术文档编写规范.md` 与 `assets/scaffold/README.md`
   拷进新站——那是给站点读者的**交付物**。写作子代理要读的是**技能目录里的那两份**，
   分派词里写技能内绝对路径，不要指向站点副本。
4. 建 `doc/运行与构建（T0Level）.md`，逐条命令带**真实输出**（模板 `assets/scaffold/doc/运行与构建（T0Level）.md` 已给结构）。
5. 核一遍 `hugo.yaml` 的两行预设配置还活着——`preset: paper` 与 `preset_menu: [paper, slate, ink, terminal]` 是
   **实值不是注释**，占位批量替换正则会顺手吃掉整行的历史毛病就落在这一带。判据两条，缺一都不算数：
   `grep` 站点 `hugo.yaml` 要能读到这两行且行首不带 `#`；构建产物 `public/index.html` 的 `<html>` 标签上
   要带 `data-td-preset=`（1.3.2 副本实测值 `paper`）。只查配置不查产物，等于没查——配置写对而主题副本是旧的
   那一站，产物上根本没有这个属性，而 `hugo build` 一句错都不报。

构建验证需要 Hugo Extended ≥0.166.0 与对齐 `go.mod`（`go 1.27.0`）的 Go，且**两者都要能被找到**：

```
GOTOOLCHAIN=local GOPROXY=off hugo --cleanDestinationDir
```

刚搭好、占位未清的骨架实测可构建（Hugo v0.168.0 Extended + Go 1.27.2）：`Pages 15 / Static files 34 / Total in 1231 ms / 0 ERROR`，产物含 `llms.txt`、`offline-search-index.zh.<md5>.json` 与 `_print/`。
`WARN deprecated: css.Sass: libsass was deprecated` 是主题固有的，**不是失败**（注意：若跑带 `--panicOnWarning` 的
严格发布闸门，这条 WARN 会致败——主题契约是严格闸门用 Hugo 0.166.0，普通构建用更新版本无妨）。
Go 不在 PATH 时 Hugo 报的是 `failed to load modules: … binary with name "go" not found in PATH`，
看着像内容错误——`verify_all.py` 认得这句，会直接提示用 `--go-bin`。

## Step 4 分批产出正文

**Step 0 选 ① 完整复制**：逐篇把源文件正文原样落位，只补 front matter（`title`/`description`/`weight`）、
把站内链接改成新站路径、把图片改成 `/picture/…`。不要改写句子、不要重排章节、不要补体裁块。
验收跑 `verify_all.py --mode copy`，另加一条自己的逐字一致判据（对每篇 `diff` 或比 MD5，
本技能不内置——复制形态的核心承诺是「没动原文」，这条必须自己证）。

**Step 0 选 ② 按规范重写**（本项目走的是这条）：

一批 4–8 篇，**按分类切而不是按字数平均**。每批派子代理时给全五样，路径**一律写技能目录内的绝对路径**：
目标文件绝对路径 + 该篇 `sources` 清单 + 已验收样板文档路径（`assets/example-docs/` 里对应体裁那一份）+
`picture_map.py` 产出的该篇可用配图清单 + `assets/scaffold/doc/技术文档编写规范.md`；
要求交付时贴实测计数。分派词模板直接拷 `references/matrix-and-prompts.md` 第五节。

三条不可退让的纪律：

- **源文件是唯一事实来源**。默认值、限制数值、命令输出、异常语义查不到就不写，或写「上游未给出」。禁止按同类 API 惯例推定。
- **上游表格必须逐行保留**，不得抽样、不得「略」。
- **统计一律用 python**（Git Bash 是 GBK 控制台，`grep -c` 数中文/emoji 会恒为 0，且它数的是行数不是次数）。

每批交付后立刻跑 `audit_structure.py`，绿的才派下一批。写进分派词的事实也要有出处——
本站分派词有三处前提被子代理按源文件纠正回来（见 `references/pitfalls.md`）。

体裁拿不准时看 `assets/example-docs/`（6 份 / 132,837 字节）：`00-骨架.md`（215 行）是必需块的完整清单
（含判据代码注释），`01-概念机制型.md`（246 行）、`02-操作部署型.md`（239 行）、
`03-命令参数参考型.md`（249 行）、`04-FAQ排障型.md`（244 行）是四种体裁的节选样章，
`99-完整参考全文.md`（539 行）是一篇成品全貌。

主题可用的正文语法别猜，照 `references/oink-theme-capabilities.md`：callout **11 种**
（note/tip/important/warning/caution/success/danger/question/example/quote/details，未知类型降级为普通引用）、
数据围栏 **10 种**（mermaid/markmap/plantuml/echarts/infographic/math/chem/filetree/gallery/checksums，
其中 markmap/plantuml/drawio 要显式开且需自备服务）、`{.cards}` 与 `{.steps}` 靠 goldmark 块级属性。
1.3.x 的排版增强按需用：filetree 围栏可加 `wrap=true` 让长注释换行（默认 false 保持紧凑）、
技术表格可在表后写 `{.td-table--wide}` 换成横向滚动宽表、图片相册用 `type: expo` 页面（详见能力清单第 8 节）。

## Step 5 验收：一条命令 + 先红后绿

先跑自证，确认判据会红：

```
python scripts/verify_all.py --selftest
```

再跑真实站点：

```
python scripts/verify_all.py --site <站点目录> --matrix matrix.json --src <暂存源目录> \
    --prefix 4x=docs --prefix 50=versioned_docs/version-5.0 [--skip-prefix local] \
    [--mode rewrite|copy] --hugo <hugo可执行文件> --go-bin <go的bin目录> \
    --report <暂存目录>/验收汇总.md
```

`--mode` 用 Step 0 里用户选的那个，别自己改：选 ① 完整复制就带 `--mode copy`。

汇总把结论分三类，**别把 MANUAL 当 PASS**：

| 判据 | 类别 | 结论从哪来 |
|------|------|------------|
| `hugo build` | BUILD | `Pages=`/`Static files=`/`ERROR=0`；给了 `--hugo` 才跑 |
| `matrix_check` | AUTO | 八类判据代码 + 两组查重统计 |
| `audit_structure` | AUTO | rewrite 模式 22 类判据全生效，copy 模式只留 12 类结构判据；键是站点相对路径 |
| `check_links` | AUTO | 以 `public/` 真实产物为准，含首页 `data/home/*.yaml`；`unmapped` 非零时 `broken` 不可信 |
| `check_coverage` | AUTO | 术语/数值覆盖分诊表，默认恒退出 0；加 `--gate 0.6` 才当闸门 |
| `picture_map` | AUTO | 配图引用是否都在 `static/picture/` 落地 |
| `validate_mermaid` | MANUAL | 脚本只生成解析台并核对注入的好坏样本；真解析要在浏览器里读回 `REAL_FAIL=0` |

`check_coverage.py` 的覆盖率是**线索不是结论**：低覆盖大多是上游客套句被改写，必须逐条人工判定。

收尾两件交付物：`doc/复刻覆盖矩阵.md`（`matrix_check.py --report` 生成，逐条归属 + MD5 查重表）
与 `doc/运行与构建（T0Level）.md`（每条命令带真实输出 + 未验证项汇总）。

---

## 自证基线（`verify_all.py --selftest` 实测原样输出）

```
stub_public_pages=30（unmapped.md 故意不造，用来触发 UNMAPPED）
audit: rc=1 expected_keys=20 observed_keys=20 mismatch=0 沉默样本=5 其中被误报=0
audit: 可达判据代码=22
audit --mode copy: rc=1 文体判据沉默=10/10 结构判据仍生效=12/12
links: rc=1 links_checked=7 external_or_anchor=0 home_urls=2 broken=3 unmapped=1 uglyURLs=False lowercase=True
fetch_source --selftest: rc=0 PASS
validate_mermaid 生成解析台: rc=0 blocks=22 注入好坏各一=True（真解析仍需浏览器，属 MANUAL）
matrix_check 绿路: rc=0 codes=0 categories=1 sections=7 articles=22 source_refs=24 on_disk=24 UNCOVERED=0 DUPLICATED=0 NONEXISTENT=0 out_of_scope=0 problems=0
matrix_check 红路: rc=1 codes=8 categories=1 sections=7 articles=21 source_refs=23 on_disk=24 UNCOVERED=4 DUPLICATED=1 NONEXISTENT=1 out_of_scope=0 problems=11
picture_map: rc=0 articles=22 refs=2 mapped=1 missing_in_static=1 ambiguous_basename=0 out_of_scope=0
check_coverage 未声明树外前缀: rc=2 命中「未知前缀 local」=True
check_coverage 声明 --skip-prefix local: rc=0 triage_below_80pct=1 error_rows=0 rows=1 out_of_scope=1
matrix_check 未声明树外前缀: rc=1 BAD_PREFIX=1
matrix_check 声明 --skip-prefix local: BAD_PREFIX=0 out_of_scope=1
SELFTEST_PASS
```

读这份输出的三个要点：

1. `mismatch=0` 且 `其中被误报=0` 才叫通过——只报「红样本都红了」不够，合规样本被误报同样是判据坏。
2. 红路 `codes=8` 对上了 `matrix_check` 全部八类判据代码；`可达判据代码=22` 对上了 `audit_structure` 的全部判据。
   数字掉了说明有判据永远触发不了，那是死判据。
3. 每条闸门都要有「不声明就报错 / 声明了就放行」的成对读数（末四行），
   否则无法区分「闸门生效」与「闸门被拆了」。

改判据脚本、改夹具、改矩阵 schema 之后**必须重跑这份自证**，并把新输出替换到本节。

---

## 失败处理

| 现象 | 先查 | 处理 |
|------|------|------|
| 审计 `problems=0` 但你怀疑没跑起来 | `verify_all.py --selftest` 是否 `SELFTEST_PASS` | 先修判据本身，别信绿色 |
| 验收数字整体突变（分类数、篇数、前缀都变了） | 共享暂存目录里的矩阵是否被另一条工作流重生成 | 先确认输入归属再改；别急着「修」站点 |
| `hugo build` 报 `failed to load modules` | Go 是否在 PATH | 用 `--go-bin <go的bin目录>`；这不是内容错 |
| `check_links` 报 `unmapped=N`（N>0） | URL 推断与产物是否一致（leaf bundle / uglyURLs / disablePathToLower） | 此时 `broken` 数字不可信，先对齐再看链接 |
| mermaid 解析台无读数 | 是否走了 http（`file://` 下 `fetch` 被拦）；是否有 promise 不返回 | 用 `python -m http.server` + 页内轮询读 `#out` |
| 渲染页面里出现本地暂存路径 | 正文是否引用了暂存目录 | 全局改成上游仓库相对路径；`audit_structure.py --scratch <暂存目录名>` 兜住后续 |
| 下载大包超时或截断 | HEAD 通不代表 GET 通 | 换 `gh-proxy.com`；逐文件校验字节数 |
| Hugo 报 `could not find alias` | 替换占位符的正则是否吃掉了整行 | 字符类要排掉换行 |
| 搜索面板显示 0 results | 选择器取错 / 索引异步加载 / 索引文件名带哈希 | 读面板文本；从 `public/` 列真实文件名 |
| 子代理报告与自己数出来的不一致 | 谁的正则口径 | 以脚本实测为准，逐条复核它给的 `file:line` |
| 数出来的文件数比实际少 | 是否用 `glob` 数载荷 | `glob` 跳过点开头的文件，数目录一律用 `os.walk` |
| 侧边栏/下拉的自定义 partial 不生效 | 文件名是否与主题调用的模板名**逐字相同** | 带说明性后缀的文件名是死文件，Hugo 按精确名解析 |
| 外观面板只有亮/暗两挡、没有 Paper/Slate/Ink/Terminal | 站点 `hugo.yaml` 的 `preset_menu` 是否为实值；`public/index.html` 的 `<html>` 上有没有 `data-td-preset` | 配置是注释 → 改回实值即可。配置对而产物没 `data-td-preset` → **主题副本是 1.0/1.1**（1,196 文件 / `min_version 0.160.1`，无 `_presets.scss`），换 1,273 文件的 1.3.2 副本，改配置救不了 |

---

## Resources

- `references/oink-theme-capabilities.md` —— 主题能力清单（按 OINK **v1.3.2** 副本实测）：callout 11 种与渲染结构、
  10 种数据围栏、mermaid 渲染链与本地运行时、`outputs`/离线搜索索引产物、侧边栏根选择器字段、`relativeURLs` 实际效果、
  goldmark 三项依赖、视觉预设与 expo 相册（1.2/1.3 新增）、构建时开关清单、以及「未实测项」清单。改 `hugo.yaml` 或写非正文类页面前必读。
- `references/matrix-and-prompts.md` —— 覆盖矩阵 schema 与不变量、多版本查重判据、
  子代理分派词完整模板、复核清单、批次节奏。Step 2 与 Step 4 照着它做。
- `references/pitfalls.md` —— 实际付过代价的坑（控制台编码、判据自污染、浏览器探针假红、下载通道、
  Hugo 与 Go 约束、占位替换正则、`broken` 非零是待办、分派词前提错误、表格正则、partial 精确名、
  配置注释与代码不一致、glob 语义、计数口径、共享暂存目录、字体没字形的码位、交付前自证清单）。
- `references/writing-spec.md` —— 写作规范与判据映射表。规范全文在技能内的
  `assets/scaffold/doc/技术文档编写规范.md`（445 行），子代理读这一份，不要指向站点副本。
- `assets/scaffold/` —— 站点骨架模板（14 个文件）：`hugo.yaml`、`go.mod`/`go.sum`、`.gitignore`、`LICENSE`、
  `README.md`、`data/home/zh.yaml`、`content/_index.md`、`content/docs/_index.md`、
  `doc/运行与构建（T0Level）.md`、`doc/技术文档编写规范.md`、
  `layouts/_partials/shell/root-menu-roots.html`、`assets/scaffold/assets/icons/logo.svg`、
  `assets/scaffold/static/favicon.svg`。
- `assets/example-docs/` —— `00-骨架.md` 与四种体裁样章、`99-完整参考全文.md` 一篇成品全貌。
- `assets/fixtures/` —— 自证夹具：一个含 20 类缺陷样本与 5 个合规样本的 mini 站点、配套源文件、
  四份矩阵（主矩阵、绿路、红路、树外前缀）与 `expected.json` 契约。只被 `verify_all.py --selftest` 消费。
- `assets/theme/oink-main/` —— OINK 主题本体 **v1.3.2**（1,273 文件 / 22,234,796 字节），`scaffold.py` 整目录拷入新站。
- `scripts/scaffold.py`、`scripts/gen_skeleton.py`、`scripts/fetch_source.py`、`scripts/matrix_check.py`、
  `scripts/audit_structure.py`、`scripts/check_links.py`、`scripts/check_coverage.py`、
  `scripts/picture_map.py`、`scripts/validate_mermaid.py`、`scripts/verify_all.py` —— 十个可执行工具。
  每个都必须实测使用；判据类脚本一律先跑其自证路径（`--selftest`，或经 `verify_all.py --selftest` 统一跑）。
