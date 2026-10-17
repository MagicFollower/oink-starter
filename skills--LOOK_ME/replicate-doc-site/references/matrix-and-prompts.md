# 覆盖矩阵与子代理分派

复刻一个文档站的核心难点不是「会不会写」，而是**「怎么证明 119 篇原文一篇都没漏」**。
本文给出可机检的答案：把「哪篇原文进了哪篇成文」写成一份数据结构（matrix），让它同时驱动
骨架生成、结构审计、覆盖度核对三件事；再给出把成文批量派给子代理的分派词模板。

---

## 一、matrix 是唯一事实来源

| 做法 | 后果 |
|------|------|
| 把归属关系写在 Markdown 说明文档里 | 人读方便，机器用不上；改一处忘改另一处，漏项看不出来 |
| 把归属关系写成**可执行数据结构**（Python 列表或 JSON） | 骨架、审计、覆盖率三件工具都从它读；不一致会当场报错 |

本项目采用的是「Python 模块 + 导出 JSON」两栖形态：模块里写树状 `dict`，`__main__` 自检并导出 `matrix.json`。
这样做的收益是**归属关系能与磁盘上的源文件做集合运算**，而不只是自我声明。

导出的 JSON 交给 `scripts/matrix_check.py` 做正式自检（本项目 119 篇 → 31 篇时实测）：

```
python scripts/matrix_check.py --matrix matrix.json --src <暂存源目录> \
    --prefix 4x=docs --prefix 50=versioned_docs/version-5.0 --report <站点>/doc/复刻覆盖矩阵.md

SCHEMA=0 DUP_WEIGHT=0 WEIGHT_GAP=0 NO_SOURCES=0 BAD_PREFIX=0 NONEXISTENT=0 UNCOVERED=0 DUPLICATED=0
same_name_pairs=30 identical=13 differing=17
per_article_pairs=29 identical=12 differing=17
categories=10 sections=20 articles=31 source_refs=119 on_disk=119 UNCOVERED=0 DUPLICATED=0 NONEXISTENT=0 out_of_scope=0 problems=0
```

关键数字的含义：

- `source_refs=119` 且 `on_disk=119`、`UNCOVERED=0`：磁盘上 119 个源文件全部被某篇文章认领，没有漏。
- `NONEXISTENT=0`：声明的每个源路径都真实存在（防止「凭印象写路径」）。
- `DUPLICATED=0`：没有一条源被两篇同时认领。
- `out_of_scope`：按 `--skip-prefix` 声明的树外源条数，不进上面任何分母（见第二节）。
- `problems=0` 才退出 0；`--report` 顺手生成收尾要交的 `doc/复刻覆盖矩阵.md`。

**这三条判据必须自己会红。** 早期版本漏了 21 篇 5.0 重复文档，`UNCOVERED=21` 直接把问题暴露出来；
补全 sources 后才归零。判据先能红，`UNCOVERED=0` 才有信息量。
现在这组「会红」的证明固化在夹具里，不依赖真实站点：`matrix_check` 红路实测
`codes=8 UNCOVERED=4 DUPLICATED=1 NONEXISTENT=1 problems=11`，八类判据代码全部被触发
（`python scripts/verify_all.py --selftest`）。

---

## 二、schema

```json
{
  "categories": [
    {
      "dir": "01-overview",
      "title": "产品认知",
      "icon": "fa-solid fa-compass",
      "weight": 1,
      "desc": "一句话说明这个分类解决什么疑问。",
      "sections": [
        {
          "dir": "认识X",
          "title": "认识 X",
          "weight": 1,
          "desc": "板块说明。",
          "articles": [
            {
              "file": "是什么与为什么选择X.md",
              "title": "X 是什么、为什么选它",
              "desc": "用于 front matter description，写清承接了哪些上游内容。",
              "weight": 1,
              "sources": ["4x:00-introduction/01whychoose.md", "50:01-introduction/01whychoose.md"]
            }
          ]
        }
      ]
    }
  ],
  "prefixes": { "4x": "docs", "50": "versioned_docs/version-5.0" }
}
```

`gen_skeleton.py` / `matrix_check.py` / `audit_structure.py` / `check_coverage.py` / `picture_map.py`
都兼容顶层直接是 `categories` 数组（此时 `prefixes` 只能走命令行 `--prefix`）。

| 字段 | 约束 | 违反后果 |
|------|------|----------|
| `dir` | 分类目录带 `NN-` 数字前缀；板块与文章目录用中文 | `audit_structure.py` 不管，但 Hugo 侧边栏排序会乱 |
| `weight` | 同目录内 1..N 连续且不重复 | `DUP_WEIGHT` / `WEIGHT_GAP` |
| `icon` | 只有分类 `_index.md` 需要；`params.ui.sidebar_icon_policy: groups` 下分组才显图标 | 图标缺失不报错，视觉退化 |
| `desc` | ≥20 字（会被写进 front matter description） | `THIN_DESC` |
| `sources` | `tag:相对路径`；tag 必须能在 `prefixes` 或 `--prefix` 里解析 | `matrix_check.py` 报 `BAD_PREFIX`；`check_coverage.py` / `picture_map.py` 直接退出 2 |

**树外源**：素材不止上游仓库时（同级示例工程、二进制发行包、本地附件），给它们一个独立前缀
（本项目用 `local:`），并在所有脚本上统一带 `--skip-prefix local`。这些源只计入 `out_of_scope`，
不参与存在性核对、认领去重、查重与术语覆盖——拿 Java 源码去比中文术语只会产出垃圾分诊行。
**未声明的未知前缀必须报错**，那是防前缀写错的闸门；`--skip-prefix` 是表达「这条源不在上游树内」，
不是消音器。自证：夹具里同一份矩阵跑两遍，不声明时 `matrix_check` 报 `BAD_PREFIX=1`、
`check_coverage` 退出 2 并点名前缀；声明后 `BAD_PREFIX=0 out_of_scope=1`。

不变量（写进矩阵前先自问）：

1. 每篇源文件**恰好**属于一篇文章（跨版本同名要显式成对声明，见下节）。
2. 每篇文章的 `sources` 非空——空即「这篇是凭空写的」，复刻任务不允许。
3. 分类数 = 上游导航一级条目数；板块数 = 你希望侧边栏第二级有几张卡片。

---

## 三、多版本源的同名查重

Docusaurus 类上游常见结构：`docs/` 放最新版，`versioned_docs/version-X/` 放历史版。
两版会有一批**同名文件**。必须逐字节判定，不能按文件名猜：

```python
import hashlib, io, os
def by_name(root):
    d = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                d.setdefault(f, []).append(hashlib.md5(io.open(p, "rb").read()).hexdigest()[:10])
    return d
```

本项目实测（源文件总数 `docs=50 / versioned_docs/version-5.0=69`，合计 119）。
`matrix_check.py` 打两组，**口径不同，别混用**：

| 统计 | 口径 | 本项目实测 | 怎么用 |
|------|------|------------|--------|
| `same_name_pairs` | 各 prefix 根之间按 basename 配成的同名对（不管有没有被同一篇认领） | `30 identical=13 differing=17` | 决定「这批同名文件要不要合并」，是矩阵设计的输入 |
| `per_article_pairs` | 同一篇文章 `sources` 内部的同名对 | `29 identical=12 differing=17` | 决定「这篇文章正文里要不要写版本对比」，是写作要求 |

写作要求：`identical` 的合并为一份正文，只在版本适用处加 `> [!NOTE]` 标注；
`differing` 的必须在正文内显式对比，不许只取一版。`matrix_check.py` 会把
per-article 的 `differing` 对逐条打出来（含两边的源路径），照着清单写就不会漏。

两个数字差 1 的原因正是下面这类边界情形，必须单独确认：
**同名但被拆到两篇不同文档**。本项目有一例——两版 `02admintool.md` 逐字节相同（MD5 前 10 位 `19d6e660d6`，各 111,737 字节），
但因为 mqadmin 命令太多被拆成「主题集群与 Broker」「消息消费与连接」两篇，各自认领一版。
遇到这种就按两篇分别处理，别为了「合并同类」把两篇撑到 1,900 行。

---

## 四、matrix → 骨架 → 审计 的配对

```
matrix.py（人写） --导出--> matrix.json
   |                              |
   +-> gen_skeleton.py --建--> content/docs/**（_index.md + 只有 front matter 的文章）
   |                              |
   +-> matrix_check.py <----------- 自检 + --src，顺带 --report 出覆盖矩阵文档
   +-> audit_structure.py <--验收--┘   同一份 matrix.json 当验收单
   +-> check_coverage.py <------------- 再加 --src 源文档根
   +-> picture_map.py <---------------- 再加 --site，出「哪篇能用哪些图」
   |
   +--> verify_all.py 把上面这些 + hugo build + check_links + validate_mermaid 串成一条命令
```

判据先能红的实证有两组，**都要跑**：

其一，对刚生成的空骨架跑 `audit_structure.py`（本项目 31 篇矩阵，实测）：

```
articles=31 expected=31 dirs=31 problems=218
by_kind={"FEW_NEWBIE": 31, "FEW_TABLES": 31, "MISSING_INDEX": 1, "NO_CODE": 31,
         "NO_MERMAID": 31, "NO_PAIN_OPEN": 31, "NO_SUMMARY": 31, "TOO_SHORT": 31}
```

31 篇 × 7 类 = 217，说明每篇都被逐条判据咬住；多出的那 1 条 `MISSING_INDEX` 是临时目录里
没有 `content/docs/_index.md`（那份由 `scaffold.py` 提供，`gen_skeleton.py` 只写分类与板块的索引）。
成品站同一命令输出 `problems=0`。**没有这组「先红后绿」的对照，`problems=0` 只是脚本没跑起来。**

其二，`python scripts/verify_all.py --selftest`：夹具里 20 个红样本逐条报出、5 个合规样本一条不误报、
22 类判据代码全部可达。它不依赖任何真实站点，所以改了判据就能立刻重跑——空骨架对照做不到这一点。

---

## 五、子代理分派词模板

批量重写时，每个子代理一份「共享简报 + 私有任务单」。共享简报固定七节，直接拷下面这份改：

模板里 `<site>` 是新站目录，`<skill>` 是本技能根目录。
**凡是「要读的材料」一律给 `<skill>/…` 路径**：`scaffold.py` 虽然会把规范与 README 拷进新站，
但那是交付物；骨架还没落地时站点副本不存在，指向它的阅读指令必然落空。
Step 0 若选了「完整复制」，这份简报的第 2/3/4/5 节（事实纪律之外的体裁要求）整段换成
「原文照录，不改句子、不重排章节、不补体裁块」，其余各节照用。

```markdown
# 作者简报（每个写作子代理必读）

## 0. 你在做什么
把 <上游项目名> 的中文文档（<结构描述>）复刻进 Hugo + OINK 站 `<site>/`。
上游 <N> 篇已重组为 <M> 篇目标文档；<你要写的就是这些目标文档的正文>。

已为你做完、不要重做也不要改动：
- 站点骨架、主题、配图（`static/picture/`）、`hugo.yaml` 全部就绪。
- 每个目标文件已存在，且只有 front matter（title/description/weight）。保留这三行原样，正文写在其后。
- 所有 `_index.md` 已生成，不要改。不要运行 hugo、不要装工具链。
- 不要动不属于你的文件；不要新建文件。

## 1. 必须先读的三份材料（都在技能目录内）
1. `<skill>/assets/scaffold/doc/技术文档编写规范.md` —— 风格与质检清单，逐条硬约束。
2. `<skill>/assets/scaffold/README.md` —— 站点结构与硬性门槛（站点里那份是它的副本）。
3. 分派给你的源文件（任务里的绝对路径清单）。**源文件是唯一事实来源。**

## 2. 事实纪律（最高优先级）
- 任何技术事实（默认值、限制数值、重试次数、版本号、命令与其输出、方法签名、异常语义）
  **只能在源文件里查到才能写**；查不到就不写，或写成「上游未给出」。
- 禁止按「同类 API 惯例」「一般中间件都是这样」推定内容；禁止编造运行输出。
- 上游代码示例可照搬与整理（补齐 import、注释、预期输出），但不得改动类名、方法名、参数名与数值。
- 上游表格（限制清单、参数清单、指标清单）**必须逐行保留**，不得抽样、不得「略」。
- 同一事实在正文/表格/代码注释/要点总结里的表述必须一致，写完自查。

## 3. 版本适用
- 只在某版本成立的结论，用 callout 标注：`> [!NOTE] 版本适用：…`
- 两版写法不同处，给同场景「旧写法 / 新写法」最小对照 + 逐维度对比表。
- 两版源文件逐字节相同的（任务单会点名），合并写一份，不重复。

## 4. 结构硬门槛（逐条自检）
1. 首个二级标题是 `## 为什么需要 X？（痛点引入）`，不是定义开头。
2. 开头一个 `> ### 💡 新人小结`，紧跟学习路线图；全文 ≥3 个新人小结。
3. ≥1 个 mermaid；≥2 组对比表格；≥1 个术语表（术语/全称/通俗含义/在本文中的角色）。
4. 每个核心概念 ≥1 个可运行代码或配置块，带注释、带 `# 输出:`、带 ✅/❌ 对照，块后紧跟参数解释表。
5. `## 要点总结`（3–5 条）+ 结尾总结性新人小结。
6. 正文 ≥260 行；源材料薄的靠类比、对比表、排查清单补信息量，不灌水。
禁止：方框字符画、省略式表达、TODO/待补充、「众所周知」「不言而喻」。

## 5. Mermaid 写法
节点标签与边标签一律加引号：`P["生产者"] -->|"发送"| Q["队列"]`；
时序图 `sequenceDiagram` + `participant C as "消费者"`；一图一事，节点 >12 就拆。
图前要有引导句，图后要有解读段，不许贴图了事。

## 6. 配图
- 绝对站内路径 `![说明](/picture/xxx.png)`；含空格/中文的按 URL 编码写。
- 只用任务单里的「可用配图清单」，清单外的图不存在，别猜。
  清单由 `picture_map.py --out <暂存>/image_map.md` 生成，逐篇列 `/picture/` 绝对路径；
  `missing_in_static` 与 `ambiguous_basename` 非零时先补图或人工裁决，再派写作。
- 控制台截图只用于操作类内容；架构与流程优先自画 mermaid。

## 7. 交付与自证（数字必须实测）
逐文件统计并贴进报告：行数、💡 小结数、mermaid 数、表格数、代码块数、
方框字符命中数、省略式表达命中数、以及 2–3 条数值断言的源文件出处。
统计一律用 python，不要用 `grep -c` 数中文或 emoji（见 pitfalls 第 1 条）。
```

私有任务单要给全五样，缺一样就会返工：

| 项 | 为什么必须有 |
|----|--------------|
| 目标文件绝对路径 + 该篇的 `sources` 全清单 | 少了清单，子代理会自己去猜归属 |
| 已验收样板文档的绝对路径 | 没有实物参照，风格必然漂 |
| 该篇可用配图清单（`picture_map.py` 的输出，绝对路径） | 没清单就会出现断链图片 |
| 技能内 `assets/scaffold/doc/技术文档编写规范.md` 的绝对路径 | 规范要读技能里那一份，不要指向站点副本，也不要贴在分派词里二手转述 |
| 交付格式：要求贴实测计数 | 没有计数就无法复核 |

**分派前自己先核一遍前提。** 本项目里分派词有三处前提写错，被子代理按源文件纠正回来：
某分类实际是 4 篇不是 5 篇、某分类实际 8 篇源不是 12 篇、以及「Broker 的 `listenPort` 默认 10911」
这条在上游根本不存在（原文说的是 `-b` 参数里 port 的默认值）。教训：**写进分派词的事实也要有出处**，
否则子代理会把你的错误当权威。

---

## 六、复核子代理报告的清单

| 复核项 | 手法 |
|--------|------|
| 报告的计数 | 自己重跑 `audit_structure.py`，逐项对数；子代理报的行数/图数与脚本不一致就以脚本为准 |
| 报告里的 `file:line` | 逐条 grep 复核，不许直接引用（见 pitfalls） |
| 「上游未给出」的标注 | 抽 2–3 条自己回源文件确认确实没有 |
| 新增的数值断言 | 用 `check_coverage.py` 的漏项清单反查，或直接在源文件里搜该数值 |
| 正文里的本地暂存路径 | `audit_structure.py` 的 `SCRATCH_PATH` 判据；截图验收时也肉眼扫一遍 |
| 报告说「全部通过」 | 要它贴 `verify_all.py` 的汇总表原文；`MANUAL` 项不算通过，`SKIP` 项要问为什么没跑 |
| 报告说图片都落地了 | 自己跑 `picture_map.py`，对 `mapped` 与 `missing_in_static` 两个数 |

---

## 七、批次与节奏

- 一批 4–8 篇，按**分类**切分而不是按字数平均：同一分类的术语与配图集中，子代理内部一致性更好。
- 每批交付后立刻跑 `audit_structure.py`（不建全量依赖），绿的才继续派下一批。
- 全部落位后跑一次 `verify_all.py`（含 `--hugo` 与 `--go-bin`）拿全量结论；
  `check_coverage.py` 的分诊表最后看，用来定位「哪篇承接得薄」。
- 判据脚本、夹具或矩阵 schema 一旦改动，**先重跑 `verify_all.py --selftest`** 再跑真实站点：
  站点绿不能证明判据没坏，夹具红才能。
- 多人/多会话共用一个暂存目录时，验收数字突变先查输入归属（见 pitfalls 第 18 条），别急着改站点。
