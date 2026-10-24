# 踩坑清单

这份文档只写**实际付过代价**的坑，每条给「现象 → 根因 → 对策」。
新项目复刻前先扫一遍，能省掉本项目里大约三分之一的返工。

---

## 1. 控制台编码：中文与 emoji 的计数根本不可信

| 项 | 内容 |
|----|------|
| 现象 | `grep -c '💡' 某文件.md` 恒为 0，哪怕文件里有 6 处；`grep` 出来的中文是乱码；子代理照这个数报验收结论 |
| 根因 | Git Bash 控制台默认 GBK 码页，emoji 与部分中文在管道里就断了；`grep -c` 数的还是**行数**而不是出现次数 |
| 对策 | 计数一律用 python：设 `PYTHONIOENCODING=utf-8`，用 `io.open(p, encoding="utf-8")` 读，`t.count("💡")` 统计；要「出现次数」用 `len(re.findall(...))`，不要用 `grep -c` |

写进分派词的一句话版本：**「统计一律用 python，不要用 `grep -c` 数中文或 emoji。」**

批量打印中文文件名到 stdout 时，即使设了 `PYTHONIOENCODING=utf-8`，仍可能在某条记录上抛
`OSError: [Errno 22] Invalid argument`，把后面的循环带走。对策：要统计的结果先落文件再读回，或分小批打印。

---

## 2. Bash 的 cwd 会漂，`/tmp` 也不是同一个

| 项 | 内容 |
|----|------|
| 现象 | 用 heredoc 往 `/tmp/x.py` 写脚本，紧接着 `python /tmp/x.py` 报文件不存在；跨命令 `cd` 后相对路径忽对忽不对，工具输出里出现 `Shell cwd was reset to …` |
| 根因 | Windows 上的 Git Bash `/tmp` 与 Windows python 看到的 `C:\tmp` 不是一个目录；每次 Bash 调用是新 shell，状态不保留 |
| 对策 | 脚本与产物一律写在工作区内（例如 `_work/`），命令里全部用**绝对路径**；不要依赖上一条 `cd` |

heredoc 还会把 `\\` 压成 `\`，导致写出来的 Python 正则语法错。对策：脚本里尽量不出现反斜杠，
路径处理交给 `os.path.join` / `os.sep`。

---

## 3. 判据自己会污染被检对象

| 项 | 内容 |
|----|------|
| 现象 | 审计报告里写着「方框字符」「省略式表达」，这些词被复制进交付文档；正文里还残留 7 处 `_work/src/…` 这类本地暂存路径，直到截图验收才看见 |
| 根因 | 判据描述与正文词汇没有隔离；暂存路径在写作阶段是方便的，交付时没人记得换 |
| 对策 | `audit_structure.py` 内置两条反向判据：`SELF_CHECK_LEAK`（正文出现判据字面量即报）、`SCRATCH_PATH`（正文出现暂存目录名即报）。引用出处统一写**上游仓库相对路径**，例如 `versioned_docs/version-5.0/01-introduction/02concepts.md` |

推论：**任何「扫到 0 处」的结论都要先用一个已知存在的样本证伪**，否则你不知道是扫描器有效还是扫描器根本没跑。

---

## 4. 浏览器探针的三类假红

| 现象 | 真相 | 正确手法 |
|------|------|----------|
| `img.complete === false` 判定「图挂了」 | 4/5 张其实是 `loading="lazy"`，没进视口就不会 complete | 用 `curl -o /dev/null -w "%{http_code}"` 逐个验 HTTP 200，或直接看构建产物里文件存在 |
| 站内搜索显示「0 results」 | 面板选择器取错 + 索引是异步加载的 | 读结果面板的文本而不是数节点；等索引就绪再判 |
| 离线搜索索引 404 | 文件名带内容哈希，`offline-search-index.zh.json` 本来就不存在 | 从构建产物目录里列真实文件名 |
| 隐藏页里 `requestAnimationFrame` 不推进 | 页面不可见时 rAF 被饿死 | 同步步进驱动，或把页面置前台再测 |

时间类测量不要开虚拟时间；无头一条腿里只要有一个 promise 不返回，整条腿就没有读数，
而它的同步副作用已经落盘了。

---

## 5. Mermaid 必须过真解析器

| 项 | 内容 |
|----|------|
| 现象 | 「图看起来配平了」不等于能渲染。`sequenceDiagram` 里 `A->>B:` 这种箭头含两个 `>`，用数尖括号的静态检查必然误判 |
| 根因 | mermaid 语法有自己的词法，中文标签、括号、冒号只有在引号内才安全 |
| 对策 | `validate_mermaid.py` 把主题自带的 `mermaid.min.js` 拷进解析台，页内 `MERMAID.parse()` 逐块判定；`--selftest` 注入一好一坏两块，输出必须同时出现「好的 ok、坏的 FAIL」，否则 `REAL_FAIL=0` 不算数 |
| 实测 | 本项目 `TOTAL=79 REAL_FAIL=0 SELFTEST=1/2 SELFTEST_PASS` |

解析台必须走 http（`file://` 下 `fetch('blocks.json')` 被拦）。

---

## 6. 下载通道：HEAD 通不代表能下载

| 现象 | 对策 |
|------|------|
| 直连 GitHub 下载 23.5 MB 主题包，180 s 超时且只落 17.4 MB（截断） | 走 `https://gh-proxy.com/<原 URL>`，本项目同一文件 3.08 s 完成 |
| npmmirror 404 | 它是**逐项目白名单**，不在名单就没有 |
| tuna 403 | 别当成网络抖动重试 |
| Go 工具链 | `golang.google.cn` 可用 |
| `HEAD` 返回 200 | 证不住 `GET` 能下完，要真下真校验（`fetch_source.py` 按 tree 里的 size 逐文件核对） |
| 上游仓库 404 | `apache/rocketmq-website` 不存在，实为 `apache/rocketmq-site`，默认分支 `new-official-website` |
| 解压 zip 后中文名乱码 | bsdtar 会按 OEM 码页写文件名；改名要按 manifest 逐条核对 |

---

## 7. Hugo 与主题的构建约束

| 项 | 内容 |
|----|------|
| 必须 Extended 版 | 主题用 `css.Sass`；非 Extended 构建直接失败 |
| 工具链与代理 | `GOTOOLCHAIN=local`、`GOPROXY=off`，Go 版本要和 `go.mod` 的 `go` 指令精确对齐，否则去联网拉 toolchain 并失败 |
| Go 不在 PATH | Hugo 报 `ERROR failed to load modules: failed to download modules: binary with name "go" not found in PATH`。这句看着像模块/内容错，实际是**环境错**：本地 module replace 仍要调 `go` 解析。实测：Git Bash 里用 `PATH="C:/…/go/bin:$PATH" hugo …` 这种内联前缀**不生效**（同一命令仍报找不到 go），改成 `export PATH="/c/…/go/bin:$PATH"` 后立刻通过——即 PATH 要用 POSIX 形式导出，别用内联的 Windows 形式（机理未单独隔离，结论按实测用）。或者干脆给 `verify_all.py` 传 `--go-bin <go的bin目录>`，它按 Windows 形式拼进子进程环境，实测可用 |
| 那条 libsass WARN | `css.Sass: libsass was deprecated…` 是主题固有的，**不是构建失败**；本项目构建成功时依然会打这条 |
| `enableGitInfo` | 未纳入 Git 或内网环境保持 `false`，否则 dubious ownership 会中断构建 |
| 主题本地化的落点 | `scaffold.py` 把 `assets/theme/oink-main` 整目录拷到 `<site>/oink-main`，得到 `<site>/oink-main/oink-main`，正好匹配 `go.mod` 里的 `replace github.com/pgsty/oink => ./oink-main/oink-main` |
| 语言目录 | `locale: zh-CN`（0.168 下 `locale: zh` 亦可，主题 AGENTS.md 记着 0.160.x 的行为差异） |
| 实测 | 骨架填完占位后 `Pages 197`，`Total in 1280 ms`，0 ERROR |

---

## 8. `relativeURLs: true` 的利与两个坑

利：构建产物可直接 `file://` 打开，也能挂任意子路径；图片 `/picture/x.png` 会被改写成 `../../../../picture/x.png`。

坑：

1. `check_links.py` 不能按源文件里的 `/picture/x.png` 判存在，必须以 `public/` 里的真实产物判；
   Hugo 还会把 URL 小写化，中文路径要 URL 解码后再比。
2. 站内绝对链接（`/docs/xxx/`）在 `file://` 直开时会指到磁盘根，验证「双击 index.html 能用」时别把它当缺陷。

---

## 9. 替换模板占位符的正则会吃掉换行

| 项 | 内容 |
|----|------|
| 现象 | 用 `【[^】]*】` 批量替换 `【站点标题】`，结果 `hugo.yaml` 里 `title: &siteTitle …` 整行被吞掉，Hugo 报 `could not find alias "siteTitle"` |
| 根因 | `[^】]` 含 `\n`，模板注释里那个孤立的左括号一直匹配到下一个右括号，跨了两行 |
| 对策 | 正则写 `【[^】\n]*】`；模板注释里不要留孤立的占位符字面量（已修掉 `hugo.yaml` 模板里的 `grep -c '【'` 提示语）。落地判据用 `scaffold.py` 的 `placeholders_remaining=0`，而不是肉眼看 |

---

## 10. 骨架阶段 check_links 报 broken 是待办不是缺陷

`scaffold.py` 之后有两处占位链接：`content/docs/_index.md` 的卡片导航，以及 `data/home/zh.yaml` 里
hero/cards/cta 的 `url:`。填成真实分类目录之前，`check_links.py` 实测会报：

```
links_checked=9 external_or_anchor=0 home_urls=6 broken=8 unmapped=0 uglyURLs=False lowercase=True
  BROKEN content/docs/_index.md -> /docs/01-【目录A】/    （共 3 条，对应模板里 3 行示例卡片）
  BROKEN data/home/zh.yaml      -> /docs/01-【首个一级分类目录】/  （共 5 条；第 6 个 url 指向 docs/ 本身，构建后已存在）
```

这 8 条是「还没写完的导航」清单。**别把它当误报忽略，也别在骨架阶段就拿 broken=0 交差。**

首页 `url:` 曾是检查盲区：旧版只扫 `content/docs/**` 里的 markdown 链接，分类目录一改名，
最先断的恰恰是首页卡片，却照样报 broken=0。现在 `data/home/*.yaml` 的块式与流式
（`- { label: x, url: y }`）两种写法都会扫，整行注释掉的 `# url:` 不计入 `home_urls`；
判据是夹具里的 `home_urls=2 broken=3` 那组样本。

同一版还修掉一个假红：`content/docs/_index.md` 的落地清单写在 HTML 注释里，注释中的示例路径
`/docs/NN-目录名/` 曾被当成断链（`broken` 因此是 9 而不是 8）。现在注释、围栏代码块、行内代码
里的 `[文本](目标)` 一律先剥掉再扫，见第 17 条。

---
## 11. 批量重写：写进分派词的事实也要有出处

本项目分派词里有三处前提写错，被子代理按源文件纠正回来：

- 某分类实际是 4 篇不是 5 篇；
- 某分类实际 8 篇源不是 12 篇；
- 「Broker 的 `listenPort` 默认 10911」这条上游根本不存在（原文讲的是 `-b` 参数里 port 的默认值）。

子代理不是权威备份，它是你的第二双眼睛——但它只在**你给了源文件路径**的前提下才能纠错。
反过来，子代理报告里的 `file:line` 必须逐条 grep 复核后才能写进自己的文档。

---

## 12. 改 Markdown 表格的正则陷阱

全文级正则（例如「把所有 `## X` 改成 `## Y`」）会顺手把表格分隔行 `|------|------|` 改坏，
也会让「扫到 0 处」这类结论失真。改表格内容要按行定位到具体表格，改完立刻跑一次
`audit_structure.py`（它有 `FEW_TABLES` 判据，表格被打断会当场报）。

`zip` 条目名用反斜杠分隔时，按正斜杠写的判据会**假阴性**——校验包内文件存在时要两种分隔符都比。

---

## 13. 主题 partial 覆盖必须同名，带说明性后缀的文件名是死文件

| 项 | 内容 |
|----|------|
| 现象 | 站点 `layouts/_partials/shell/` 下放了一个 2,256 字节的 `root-menu-entries（侧边栏下拉卡片列表选中置顶效果）.html`，文件名承诺「选中项置顶」，产物里当前页的 `td-is-active` 却排在第 11 位 |
| 根因 | Hugo 按**精确模板名**解析 partial：主题调用的是 `partial "shell/root-menu-entries.html"`。文件名里多出的说明性后缀让它注册成另一个模板，永远不会被调用 |
| 对策 | 覆盖主题 partial 时文件名必须与主题里的完全一致；想保留说明就写在文件头注释里，不要写进文件名。判据：`grep -rn 'partial "shell/<名字>.html"' <主题>/layouts` 能找到调用点，且构建产物里能看到你的改动 |

这条一度被当成资产复制进技能骨架，等于把缺陷制度化——骨架里已删除该文件。

---

## 14. 主题配置的注释可能与代码不一致，读代码不读注释

| 项 | 内容 |
|----|------|
| 现象 | 主题 `hugo.yaml` 里 `offline_search_index: content # content | summary`，照注释以为只有两个取值 |
| 根因 | 实际消费方 `assets/json/offline-search-index.json` 的 `warnf` 写着允许 `title | heading | summary | content` 四个值——注释落后于代码 |
| 对策 | 任何「某配置项接受哪些值」的结论，都去消费它的模板/脚本里找 `warnf`、`in`、`slice` 白名单，不要引用配置文件旁的注释 |

---

## 15. fnmatch 的 `**` 不是递归通配

| 项 | 内容 |
|----|------|
| 现象 | 用 `--include "docs/**/*.md"` 取源，`docs/FAQ.md` 这类**根层文件取不到**，而且不报错，只在最后发现少了几篇 |
| 根因 | `fnmatch` 里没有 `**` 语义：`*` 本来就跨 `/`，`**` 只是两个 `*` 叠着，中间的 `/` 仍是字面量，于是要求至少一层子目录 |
| 对策 | `fetch_source.py` 已改成严格 glob（`*` 不跨 `/`、`**/` 吃零或多层），并逐个 pattern 打印命中数、命中 0 直接 WARN。自证：`python scripts/fetch_source.py --selftest`，9 条用例含 `docs/**/*.md` vs `docs/FAQ.md` |

通用教训：**任何按 pattern 取文件的步骤，都要打印每个 pattern 的命中数**。命中 0 是静默漏文件的唯一可见信号。

---

## 16. 交付前自证清单

先跑判据自证（不依赖任何真实站点，一条命令）：

```
python scripts/verify_all.py --selftest
```

自证的临时目录在**当前工作目录的 `.tmp/`**（环境变量 `REPLICATE_TMP` 可改指他处）。别改回系统
`%TEMP%`：Windows 沙箱（DSH 等）托管 Temp 根时，Python 在里面 `mkdir` 子目录会被直接拒绝
（WinError 5，ACL 本身完好），selftest 第一步 `copytree` 就会炸；`--selftest` 失败且保留的
夹具副本路径指向 `%TEMP%` 时，先怀疑这个再怀疑判据。

要求末行是 `SELFTEST_PASS`，且这几组读数不能掉：`mismatch=0`、`其中被误报=0`、
`可达判据代码=22`、matrix_check 红路 `codes=8`、`--skip-prefix` 的两对成对读数。
数字掉了说明有判据变成死的了——**先修判据，再谈站点绿不绿**。

再跑真实站点，逐条对：

| 项 | 判据来源 | 本项目最近一次实测 |
|----|----------|--------------------|
| 构建 | `verify_all.py --hugo … --go-bin …` | `Pages=223 Static files=172 ERROR=0 rc=0` |
| 矩阵 | `matrix_check.py` | `categories=11 sections=22 articles=39 source_refs=127 on_disk=119 UNCOVERED=0 DUPLICATED=0 NONEXISTENT=0 out_of_scope=8 problems=0` |
| 结构 | `audit_structure.py` | `articles=38 expected=39 dirs=34 problems=13`，13 条**全部**落在并行工作流正在写的 `content/docs/11-springboot-integration/`；先交付的 01~10 分类 0 条 |
| 链接 | `check_links.py` | `links_checked=168 external_or_anchor=81 home_urls=6 broken=0 unmapped=0` |
| 配图 | `picture_map.py` | `articles=39 refs=184 mapped=184 missing_in_static=0 ambiguous_basename=0` |
| 覆盖 | `check_coverage.py` | 分诊表 `triage_below_80pct=66 error_rows=3 rows=122 out_of_scope=5`（低覆盖逐条人工判定） |
| 图解析 | `validate_mermaid.py` | `blocks=96`，解析台已生成；真解析属 MANUAL，要在浏览器里读回 `REAL_FAIL=0` |

最后两行不能省：**只有「成品绿 + 夹具红」同时成立，这张表才是结论**；
MANUAL 项没有结论，别把它算进通过数。

---

## 17. 注释与代码块里的链接不是链接

| 项 | 内容 |
|----|------|
| 现象 | 骨架 `content/docs/_index.md` 的落地清单写在 `<!-- -->` 里，其中一条示例 `/docs/NN-目录名/` 被 `check_links.py` 判成断链；模板注释只要不删，这条假红就永远在 |
| 根因 | 判据直接对正文跑 `[…](…)` 正则，没区分「会被渲染成链接的文本」与「说明文本」 |
| 对策 | 扫之前先剥三类：HTML 注释、围栏代码块（``` / ~~~ 成对 toggling）、行内代码；YAML 侧跳过整行注释。自证方式是在夹具的合规样本里塞进这四条坏链接（注释/围栏/行内各一，加一条注释掉的 `# url:`），判据必须**看不见**它们——实测 `未剥离 LINK 命中 = 5 / 剥离后 = 1`，被剥掉的正是那 4 条 |

通用教训：**红样本证明判据会响，沉默样本证明判据不乱响，两者缺一都是假绿。**

---

## 18. 共享暂存目录会被并行工作流覆盖

| 项 | 内容 |
|----|------|
| 现象 | 同一条验收命令，前一次 `categories=10 articles=31 problems=0`，几小时后变成 `categories=11 articles=39`、还冒出没声明过的 `local:` 前缀，`Pages` 从 197 跳到 223 |
| 根因 | 暂存目录（本项目是 `_work/`）里既有我的判据脚本副本，也有另一条工作流的矩阵生成器；对方重跑生成器就把共享的 `matrix.json` 整个换掉了，站点 `content/docs/` 下也多出一个正在写的新分类 |
| 对策 | 验收数字突变时**先查输入归属，别先改站点**。三步：① 看矩阵顶层与前缀是否还是自己那套；② 看多出来的目录属于谁、写了几个文件；③ 确认后再决定是重生成自己的基线，还是把对方的素材纳入判据。属于别人的文件不要删、不要覆盖 |
| 附带收益 | 这次冲突正好暴露出判据缺一个表达能力：矩阵里的源可以合法地不在上游文档树内。现在三个脚本都支持 `--skip-prefix <tag>`，树外源只计入 `out_of_scope`，未声明的未知前缀仍报错 |

---

## 19. 数载荷用 `os.walk`，不要用 `glob`

| 项 | 内容 |
|----|------|
| 现象 | 同一个 `assets/theme/` 目录，`os.walk` 数出 1,196 个文件 / 21,257,008 字节，`glob('assets/theme/**', recursive=True)` 只数出 1,189 个 / 21,239,566 字节；`assets/scaffold/` 同样少 1 个 |
| 根因 | `glob` 的 `*`/`**` **不匹配以点开头的路径段**，`.gitignore`、`.github/` 之类整棵子树被静默跳过 |
| 对策 | 凡是「N 个文件 / M 字节」这种要写进文档的计数，一律 `os.walk` 逐文件 `getsize` 累加；`glob` 只用来按扩展名挑要处理的文件。同一份载荷两种口径数出两个值时，以 `os.walk` 为准 |

---

## 20. 源码里别写「字体没有字形」的码位

| 项 | 内容 |
|----|------|
| 现象 | 判据里表示汉字范围的 `[一-鿿]` 在编辑器/文档里显示成豆腐块，看着像文件编码坏了 |
| 根因 | 末端码位 `U+9FFF` 是 CJK 基本区最后一格，Unicode 13.0（2020）才分配，绝大多数字体没有字形。文件本身是合法 UTF-8，坏的是显示 |
| 对策 | 字符范围一律写 `\u` 转义：`"[\u4e00-\u9fff]"`。**用非 raw 字符串**，转义由 Python 编译期解析，编译出的 `pattern` 与字面量写法逐字节相同（实测码位 `0x5b 0x4e00 0x2d 0x9fff 0x5d`），所以是纯可读性修复、零行为变化。写 raw 字符串 `r"[\u4e00-\u9fff]"` 也能工作（`re` 自己解析 `\u`），但 `pattern` 里会留字面反斜杠，比对时容易误判 |
| 排查手法 | 别靠眼睛。用 python 扫码位区间找生僻字：`re.compile(r'[\u3400-\u4dbf\uf900-\ufaff\u9fff\u2e80-\u2eff]')` 逐文件逐行打印 `U+%04X`，一次扫清 |

同一类问题的另一面：`BOX_CHARS`（`┌┐└┘├┤┬┴┼`）必须写字面量——它是「正文里出现即报」的黑名单，写成转义就失去可读性，而这九个字符常见字体都有字形。判据是：**这个字符是给人看的还是给机器比的**。

