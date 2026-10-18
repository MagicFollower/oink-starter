# RocketMQ 文档站复刻 — AI Agent 操作规范

本项目是基于 [Hugo](https://gohugo.io/) + [OINK](https://oink.psty.com/) 主题的 **Apache RocketMQ 中文文档复刻站**。仅简体中文，主题本地化在 `oink-main/`，可完全离线构建。

内容来源为 `apache/rocketmq-site`（分支 `new-official-website`）的官方中文文档：**5.0 版 69 篇 + 4.x 版 50 篇，共 119 篇**，按知识板块重组为 **38 篇**重写文档（24,548 行 / 1,813,304 字节，行数按 `\n` 计数）。逐篇归属见 [doc/复刻覆盖矩阵.md](doc/复刻覆盖矩阵.md)，写作风格契约见 [doc/技术文档编写规范.md](doc/技术文档编写规范.md)，环境与构建的逐步操作见 [doc/运行与构建（T0Level）.md](doc/运行与构建（T0Level）.md)。

在此之外还有 **7 篇「与 Spring Boot 的集成」**（`11-springboot-integration/`，4,221 行 / 388,666 字节）：核心是六种消息（普通、批量、延时、定时、顺序、事务）在 Spring Boot Web 2.7.18 + JDK 8 + RocketMQ 4.9.8 下的用法案例。这一分类**不对应任何上游页面**，因此不计入 119 → 38 的覆盖统计，只在矩阵末尾单列；它的证据口径与 01~10 分类不同，见第四章第 6 步的「官方取证类」说明。

全站正文合计 45 篇 / 28,769 行 / 2,201,970 字节，再加 34 个 `_index.md`（507 行）共 79 个 md 文件。

读取本文件后，AI 应能自主完成新增文档的归类、格式化、放置、关联更新与构建验证。

---

## 一、项目结构

```text
rocket-mq-docs/
├── content/
│   ├── _index.md                  # 首页
│   └── docs/                      # 文档主区域（编号递增的一级分类）
│       ├── _index.md              # 文档总览页（卡片导航）
│       ├── 01-overview/           # 产品认知与选型
│       ├── 02-core-concepts/      # 核心概念与领域模型
│       ├── 03-quickstart/         # 快速开始
│       ├── 04-message-features/   # 消息类型与发送
│       ├── 05-consumption/        # 消费行为
│       ├── 06-operations/         # 部署与运维
│       ├── 07-configuration/      # 配置参考
│       ├── 08-best-practice/      # 最佳实践与安全
│       ├── 09-sdk-ecosystem/      # SDK 与生态组件
│       ├── 10-community/          # 社区与常见问题
│       └── 11-springboot-integration/  # 与 Spring Boot 的集成（官方源码与文档取证，非上游复刻）
├── static/picture/                # 官方配图 150 张（源自上游 picture 目录，按原相对路径合并）
├── data/home/zh.yaml              # 首页数据（hero、cards、cta）
├── hugo.yaml                      # 站点唯一配置文件
├── go.mod / go.sum                # Go 模块（主题走 replace 本地化）
├── oink-main/oink-main/           # 本地化主题（勿修改）
├── layouts/_partials/             # 站点级局部覆盖（侧边栏根选择器）
├── doc/                           # 写作规范与复刻映射
└── README.md                      # 本文件
```

每个一级分类内部结构与通用 Hugo 站点一致：一级分类目录 → 中文命名的知识板块子目录 → 中文命名的文章文件；每级目录都必须有自己的 `_index.md`。

---

## 二、内容分类体系

| 目录 | 分类名 | 知识板块 |
|------|--------|--------|
| `01-overview/` | 产品认知与选型 | 认识 RocketMQ、版本演进与限制 |
| `02-core-concepts/` | 核心概念与领域模型 | 领域模型、角色与订阅 |
| `03-quickstart/` | 快速开始 | 单机部署、容器与云原生部署 |
| `04-message-features/` | 消息类型与发送 | 消息类型、发送可靠性与存储 |
| `05-consumption/` | 消费行为 | 消费模型、均衡进度与重试 |
| `06-operations/` | 部署与运维 | 集群与容灾、命令行工具、可观测与控制台 |
| `07-configuration/` | 配置参考 | 参数与日志配置 |
| `08-best-practice/` | 最佳实践与安全 | 使用规范与调优、安全与访问控制 |
| `09-sdk-ecosystem/` | SDK 与生态组件 | 多语言客户端、生态组件 |
| `10-community/` | 社区与常见问题 | 贡献与发布、常见问题 |
| `11-springboot-integration/` | 与 Spring Boot 的集成（官方取证专题） | 集成基线、六种消息实战 |

> **新增一级分类规则**：优先归入现有分类；确认无法归属时按编号递增创建，并同步更新本表与 `content/docs/_index.md` 的卡片链接。

**归类原则**：一篇文档只归属一个板块。判断依据是「读者在什么场景下需要它」而非「上游放在哪个目录」：讲机制原理的进 `04/05`，讲怎么搭集群的进 `06`，讲参数默认值的进 `07`，讲踩坑约束的进 `08`。

---

## 三、命名与 Front Matter

| 层级 | 命名方式 | 示例 |
|------|---------|------|
| 一级分类目录 | 英文编号前缀 + 短横线 | `04-message-features/` |
| 二级子目录（板块） | 中文命名 | `消息类型/` |
| 文章文件 | 中文命名，不含空格 | `普通消息与定时延时消息.md` |

不使用 `.zh.md` / `.en.md` 后缀；`defaultContentLanguage: zh` 下 `.md` 即中文。

文章 front matter（三字段缺一不可）：

```yaml
---
title: 文章标题
description: 一句话说明本文解决什么问题。
weight: 1
---
```

一级分类 `_index.md` 必须带 `type: docs`、`icon`、`sidebar_root_for: self`、`sidebar_root_link_self: true` 与 `cascade`；板块 `_index.md` 只需 `title`、`linkTitle`、`description`、`weight`，`type: docs` 由一级分类 `cascade` 继承。模板见 `doc/复刻覆盖矩阵.md` 末尾与任一现有 `_index.md`。

---

## 四、AI 操作流程

1. **判断归属**：对照第二章分类表选定一级分类与板块；确认该主题是否已有文档——已有则扩写，不新开同义文档。
2. **确定路径**：`content/docs/{一级}/{板块}/{文件名}.md`。
3. **写 Front Matter**：`weight` 取同目录现有最大值 + 1；`description` 要能被侧边栏卡片直接引用，不写「本文介绍」这类空话。
4. **新建板块时成对操作**：先建板块 `_index.md`，再在该一级分类 `_index.md` 的 `## 知识板块` 列表末尾追加 `- **板块名** — 覆盖内容`。板块已存在则不动任何 `_index.md`。
5. **正文按 `doc/技术文档编写规范.md` 写**，硬性门槛：
   - 以「为什么需要 X？」开头，遵循 痛点 → 设计 → 流程 三段式；
   - 全文 ≥ 3 个「💡 新人小结」（开头 / 复杂概念处 / 结尾），结尾必须有「要点总结」；
   - 架构、流程、状态机用 **Mermaid**；轻量线性流程可用文本箭头；**严禁** `┌─┐│└┘├┤┬┴┼` 方框字符；
   - 专有名词与缩写（如 Proxy、LiteTopic、SQL92、ACL、DLedger）首次出现处给通俗解释，并配「在本文中的角色」；
   - 有 4.x / 5.0 行为差异时，用版本适用标注 + 差异对比表，禁止把某一版行为写成通用结论；
   - 代码块必须可运行、带关键注释、附运行输出，并给出 ✅ 推荐 / ❌ 不推荐对照；
   - 禁用「限于篇幅」「此处从略」等省略表达，禁用 TODO/待补充。

   **原文照录类文章例外（当前无成员）**：`_work/matrix.py` 里可给文章标 `verbatim=True`，被标中的文章是把外部既有文档逐字节照录进来、不是重写产物，因此**不参与重写体裁判据**——首标题句式、💡 小结条数、「要点总结」章节、方框字符、省略表达、行数下限全部豁免。仍生效的判据有四项：front matter 三件套、站内相对路径可用、所引用配图真实存在、`weight` 在同目录内连续。`_work/audit_structure.py` 用 `VERBATIM` 集合实现该豁免，且必须同时证明「不加豁免时会报错」，避免把豁免写成静默放行。**本轮第 11 分类重建后，矩阵里已没有任何 `verbatim=True` 文章，`VERBATIM` 集合为空，全站 45 篇一律按完整重写体裁判据度量**（`problems=0` 就是这个空集合下的实测结果）；豁免机制本身仍留在脚本里，将来再加照录篇时按上述四条判据验收。

6. **技术事实来源分两类**：
   - **上游文档类**（分类 1-10）：上游为 `apache/rocketmq-site` 分支 `new-official-website`，中文正文在 `docs/`（4.x）与 `versioned_docs/version-5.0/`（5.0）；逐篇归属见 `doc/复刻覆盖矩阵.md`。正文引用出处一律写**上游仓库相对路径**（如 `docs/06-parameterConfiguration/01local.md`、`versioned_docs/version-5.0/04-featureBehavior/02delaymessage.md`），不写本地暂存目录。逐条对照，不得按「同类 API 惯例」推定默认值、版本号、超时值或异常行为。上游没写的，就不写，或显式写「上游未给出」。
   - **官方取证类**（分类 11）：`_work/matrix.py` 中 sources 以 `ref:` 开头的文章，技术事实来自三处一手材料——`rocketmq-spring` 仓库 tag `rocketmq-spring-all-2.2.3` 的源码与 `rocketmq-spring-boot-samples` 官方示例（正文写文件相对路径 + tag + 行号）、上游 `apache/rocketmq-site` 的 4.x/5.0 中文文档、`rocketmq-all-4.9.8-bin-release` 发行包内 jar 的类结构与常量池**静态取证**。这一类不认领单一上游页面，也不参与 119 篇覆盖率统计（`_work/check_coverage.py` 对 `ref:` 源单独出一行说明）。本轮**不搭建、不运行任何工程**，因此正文严禁出现运行读数（毫秒、吞吐、msgId 字面量、队列分布、回查秒数）；代码块的输出行统一写 `// 预期输出:` 并注明按源码签名与文档结构推定；凡正文用到「实测」二字，须在该篇开头用 `[!NOTE] 证据口径` 标注「实测＝静态取证」。与运行无关的数值断言（默认值、上限、档位表、异常类型与文案）仍要逐条指出源码行号或上游文档路径。
7. **配图引用**：官方图片已落地在 `static/picture/`，正文用绝对路径引用，例如 `![消费位点示意](/picture/消费位点.png)`；带空格或中文的文件名需 URL 编码。可用清单见 `_work/image_map.md`。
8. **构建验证**：见下章命令，要求 0 ERROR；WARN 仅允许主题侧的 `css.Sass: libsass was deprecated` 一条。

---

## 五、构建与环境

| 工具 | 版本 | 本机路径 |
|------|------|--------|
| Hugo | v0.168.0 **Extended** | `C:\Users\webtu\tools\hugo\hugo.exe` |
| Go | 1.25.4 | `C:\Users\webtu\tools\go\bin\go.exe` |

```powershell
# PowerShell
$env:PATH = "C:\Users\webtu\tools\go\bin;C:\Users\webtu\tools\hugo;" + $env:PATH
$env:GOTOOLCHAIN = "local"; $env:GOPROXY = "off"
hugo --cleanDestinationDir          # 验证构建
hugo server -D                      # 本地预览
hugo --cleanDestinationDir --gc --minify   # 生产构建
```

`GOTOOLCHAIN=local` 与 `GOPROXY=off` 是硬要求：默认值会让 Hugo 尝试联网下载工具链与远程模块，离线环境会直接卡死（上游同类问题见 `oink-starter/doc/问题001`、`问题003`）。主题必须 Extended 版才能编译 SCSS（`问题004`）。

---

## 六、约束与禁止事项

1. 不可修改 `oink-main/` 主题目录下任何文件。
2. 不可添加非中文内容文件，不可改动 `hugo.yaml` 的语言配置。
3. 新建板块必须同时创建其 `_index.md` 并更新父级分类的「知识板块」列表；目录与索引成对出现。
4. 不可删除已有 `_index.md`；不可让文章缺失 front matter。
5. 不可改写上游的技术事实（参数默认值、限制数值、命令与输出）；重组结构与补充类比、图示、对比是本职。
6. 一篇文档只属于一个板块；跨板块的关联用正文内的相对链接，不复制正文。
