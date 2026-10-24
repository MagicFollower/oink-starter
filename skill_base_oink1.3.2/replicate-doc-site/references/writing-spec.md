# 写作规范：判据索引

规范全文**不在这里**，在技能内的 `assets/scaffold/doc/技术文档编写规范.md`
（445 行 / 19,067 字节 / MD5 前 10 位 `92e30761fb`，三个数用来校验这份文件没被改坏）。
`scaffold.py` 会把它拷进新站的 `doc/`，那是给站点读者的**交付物**；
派写作子代理时给的是**技能内那条绝对路径**——骨架还没落地时站点副本根本不存在。

本文只登记两件事：**规范条目 ↔ `audit_structure.py` 判据的映射**，以及三处必须显式声明的口径差异。

---

## 一、判据映射

| 规范原则 | 落成的机器判据 | 阈值 |
|----------|----------------|------|
| 原则一 问题驱动叙事 | `NO_PAIN_OPEN` | 首个真实 H2（跳过代码块内的 `##`）必须含「为什么」 |
| 原则二 新人小结模块 | `FEW_NEWBIE` | `💡 新人小结` ≥ 3 处 |
| 原则三 结构化信息 | `NO_MERMAID` / `FEW_TABLES` | mermaid ≥ 1；以 `|` 开头的行数 ÷ 2 ≥ 2 |
| 原则四 代码规范 | `NO_CODE` | 带语言标注的 fence ≥ 1 |
| 原则六 内容完整性 | `SKIP_LANGUAGE` | 命中「限于篇幅 / 此处从略 / 自行查阅 / 待补充 / TODO / 感兴趣请 / 众所周知 / 不言而喻」即报 |
| 原则六 + 图表格式规范 | `BOX_CHARS` | 正文出现 `┌┐└┘├┤┬┴┼` 任一字符即报 |
| 结构模板 | `NO_SUMMARY` | 必须出现「要点总结」 |
| front matter | `NO_FRONT_MATTER` / `FM_FIELD` / `THIN_DESC` | `title`/`description`/`weight` 齐；description ≥ 20 字 |
| 排版语言 | `ENGLISH_HEADING` | H2 含 ≥4 连续字母且无汉字 |
| 复刻专属：源路径纪律 | `SCRATCH_PATH` | 正文出现本地暂存目录名即报（应改为上游仓库相对路径） |
| 复刻专属：验收自净化 | `SELF_CHECK_LEAK` | 正文出现判据名或判据描述词（「方框字符」「省略式表达」等）即报 |
| 矩阵一致性 | `NOT_WRITTEN` / `UNLISTED` / `MISSING_INDEX` | 磁盘文件集必须与 matrix 严格相等 |
| 导航一致性 | `DUP_WEIGHT` / `WEIGHT_GAP` | 同目录 weight 恰为 1..N |

另有几条只能靠**跑起来或比对矩阵**证明，不在静态审计里：

| 判据 | 由谁执行 | 结论形态 |
|------|----------|----------|
| mermaid 语法可解析 | `validate_mermaid.py` 用主题自带解析器逐块 `parse()` | 解析台生成属自动，真渲染属 MANUAL（要在浏览器里读回 `REAL_FAIL=0`） |
| 站内链接可达 | `check_links.py`，以构建产物 `public/` 为判据 | `broken` / `unmapped`；`unmapped` 非零时 `broken` 不可信 |
| 配图路径都落地 | `picture_map.py`，按 basename 对 `static/picture/` | `mapped` / `missing_in_static` / `ambiguous_basename` |
| 一篇源都没漏 | `matrix_check.py`，矩阵与源树做集合运算 | `UNCOVERED` / `NONEXISTENT` / `DUPLICATED` + 两组同名查重 |
| 术语与数值承接 | `check_coverage.py` | 分诊表，是线索不是结论；加 `--gate` 才当闸门 |

一条命令串起来：`verify_all.py`（先跑它的 `--selftest` 证明判据会红）。

**这份规范只适用于 Step 0 选了「按规范重写」的场合。** 若用户选的是「完整复制原文」，
上面第一张表里有 10 条判据整组不适用（`audit_structure.py --mode copy` 会自动跳过，
即 `GENRE_CODES`：`BOX_CHARS`、`SKIP_LANGUAGE`、`TOO_SHORT`、`FEW_NEWBIE`、`NO_MERMAID`、
`FEW_TABLES`、`NO_CODE`、`NO_SUMMARY`、`NO_PAIN_OPEN`、`ENGLISH_HEADING`）——
上游原文本来就不满足「痛点开场 / ≥260 行 / ≥3 个新人小结 / ≥1 个 mermaid」，报了只是噪音。
剩下的 12 条与内容形态无关，两种模式都生效：矩阵一致性三条、导航一致性两条、
front matter 三条（`NO_FRONT_MATTER`/`FM_FIELD`/`THIN_DESC`）、`BROKEN_IMAGE`、
`SCRATCH_PATH`、`SELF_CHECK_LEAK`、`NON_ZH_FILE`。10 + 12 = 22，正好是全部判据代码，
两组互为补集，所以划错边界会被 `--selftest` 当场报出来。

本文余下两节（口径差异、判据自污染）在两种模式下都成立。

---

## 二、三处口径差异（照抄规范原文会撞判据）

| 规范原文写法 | 本技能执行口径 | 原因 |
|--------------|----------------|------|
| 「形式二：决策树」示例用 `│ ├ └` 画分支 | 决策树一律改用 `mermaid flowchart`；文本箭头只允许 `→ ↓ ① ②` 这类不依赖字符对齐的符号 | `BOX_CHARS` 命中 `├`、`└`，照抄示例必报问题 |
| 「文档长度：每个主题至少覆盖 200 行以上」 | 成品默认门槛 260 行（`--min-lines`），骨架与样章不受此约束 | 复刻站一篇承接 3–8 篇上游原文，200 行装不下 |
| 「禁止方框字符」只写在质检清单里 | 升级为逐字符机器判据，**代码块内也扫** | 中文环境对齐不可靠，没有「修一修就能对齐」的余地 |

第三条有副作用要记牢：规范原文自己那张「❌ 反例」方框图**不能出现在复刻产物里**，判据不区分「示例」与「正文」。
要表达「不要这样写」，改用文字描述 + mermaid 正例。

---

## 三、判据自身的污染问题

`audit_structure.py` 的报告和本文都含有「方框字符」「省略式表达」这些词。
因此判据只扫 `content/docs/**` 的**文章正文**，并用 `SELF_CHECK_LEAK` 反向检查：
一旦这些字面量被顺手抄进交付文档，当场报出。

两条判据都是被真实事故逼出来的：
`SCRATCH_PATH` 源于截图验收时发现 7 处本地暂存路径（形如 `_work/src/…`）泄漏进了正文，应改为上游仓库相对路径；
`SELF_CHECK_LEAK` 源于审计报告自身的措辞被复制进交付物。写文档时不要复制审计报告里的措辞。
