# Java 笔记站点 — AI Agent 操作规范

本项目是一个基于 [Hugo](https://gohugo.io/) + [OINK](https://oink.pgsty.com/) 主题的 **中文 Java 笔记站点**。仅支持简体中文，主题已本地化在 `oink-main/` 目录，可完全离线运行。

本文档面向 AI Agent：读取本文件后，给定任意 Java 相关文档，AI 应能自主完成归类、格式化、放置、关联更新和构建验证。

---

## 一、项目结构

```text
Java-Doc-Site/
├── content/                    # 内容目录（所有笔记都在这里）
│   ├── _index.md               # 首页
│   ├── docs/                   # 笔记主区域（按编号递增的一级分类）
│   │   ├── _index.md           # 笔记总览页
│   │   ├── 01-java-base/       # Java 基础
│   │   ├── 02-collections/     # 集合框架
│   │   ├── 03-concurrency/     # 并发编程
│   │   ├── 04-jvm/             # JVM
│   │   ├── 05-spring/          # Spring 生态
│   │   ├── 06-data-access/     # 数据访问
│   │   ├── 07-middleware/      # 中间件
│   │   ├── 08-dev-tools/       # 开发工具
│   │   ├── 09-design/          # 设计与实践
│   │   ├── 10-algorithms/      # 算法与数据结构
│   │   └── ...                 # 可按需新增（编号递增）
│   ├── blog/                   # 博客（预留，当前为空）
│   │   ├── _index.md
│   │   └── post/_index.md
│   └── book/                   # 书籍（预留，当前为空）
│       └── _index.md
├── data/home/zh.yaml           # 首页数据（hero、卡片、CTA）
├── hugo.yaml                   # 站点唯一配置文件
├── go.mod                      # Go 模块依赖
├── oink-main/oink-main/        # 本地化主题（勿修改）
├── static/                     # 静态资源
└── doc/                        # 项目开发问题归档
```

每个一级分类目录（`01-java-base/` 等）内部结构：

```text
08-dev-tools/
├── _index.md                   # 分类入口页（必须存在）
└── 构建与打包/                 # 二级子目录（按知识板块创建，中文命名）
    └── 可运行JAR包.md          # 具体文章
```

---

## 二、内容分类体系

一级分类目录按编号递增组织，当现有分类无法覆盖新内容时可新增。每个分类下有若干知识板块，对应二级子目录。

| 目录 | 分类名 | 知识板块 |
|------|--------|--------|
| `01-java-base/` | Java 基础 | 语言语法、面向对象、泛型与反射、异常处理、IO 与 NIO |
| `02-collections/` | 集合框架 | List、Map、Set、Queue 与 Deque、源码分析 |
| `03-concurrency/` | 并发编程 | 线程基础、锁机制、JUC 工具、线程池、异步编程、并发模型 |
| `04-jvm/` | JVM | 内存模型、垃圾回收、类加载、字节码、调优实战 |
| `05-spring/` | Spring 生态 | IoC 容器、AOP、Spring Boot、Spring MVC、Spring Cloud |
| `06-data-access/` | 数据访问 | JDBC、MyBatis、JPA/Hibernate、事务管理、连接池 |
| `07-middleware/` | 中间件 | 消息队列、Redis、Elasticsearch、Nginx、注册中心 |
| `08-dev-tools/` | 开发工具 | Maven、Gradle、Git、日志框架、单元测试、构建与打包、IDE 技巧 |
| `09-design/` | 设计与实践 | 设计模式、架构设计、编码规范、性能优化、面试专题 |
| `10-algorithms/` | 算法与数据结构 | 基本排序、高阶排序 |

> **新增一级分类规则**：优先归入现有分类；确认无法归属时，按编号递增创建新分类目录，同步更新本表和 `docs/_index.md` 的卡片链接。

---

## 三、文件命名与格式规范

### 命名规则

| 层级 | 命名方式 | 示例 |
|------|---------|------|
| 一级分类目录 | 英文编号前缀 + 英文短横线 | `01-java-base/`、`08-dev-tools/` |
| 二级子目录 | **中文命名**，按知识板块 | `构建与打包/`、`锁机制/` |
| 文章文件 | **中文命名** | `可运行JAR包.md`、`HashMap源码分析.md` |

- 不使用 `.zh.md` 后缀。`defaultContentLanguage: zh` 下 `.md` 即中文。
- 不使用 `.fr.md` 或 `.en.md`。本站仅中文。

### 文章 Front Matter 模板

每篇文章必须在文件开头包含以下 YAML front matter：

```yaml
---
title: 文章标题
description: 一句话描述文章内容。
weight: 1
---
```

| 字段 | 说明 |
|------|------|
| `title` | 文章标题，显示在页面顶部和侧边栏 |
| `description` | 一句话摘要，显示在分类卡片和 SEO 元数据中 |
| `weight` | 排序权重，同目录下从 1 开始递增，数字越小越靠前 |

---

## 四、AI 操作流程

当接收到一份 Java 相关文档时，严格按以下步骤执行：

### 步骤 1：分析内容，判断归属

阅读文档内容，依次判断：

1. 属于现有分类中的**哪一个**？参考第二章分类体系表。如果无法归入现有分类，按编号递增新建一级分类。
2. 属于该分类下**哪个知识板块**（二级子目录）？
3. 如果该板块已有对应子目录 → 直接放入；如果没有 → 需要新建子目录。

### 步骤 2：确定文件路径

路径格式：

```
content/docs/{一级目录}/{二级子目录}/{文件名}.md
```

示例：
- 一篇关于 HashMap 源码的文章 → `content/docs/02-collections/Map/HashMap源码分析.md`
- 一篇关于 synchronized 的文章 → `content/docs/03-concurrency/锁机制/synchronized详解.md`
- 一篇关于 Spring Boot 自动配置的文章 → `content/docs/05-spring/Spring Boot/自动配置原理.md`

### 步骤 3：添加 Front Matter 并写入文件

为文章添加 front matter，保留原文正文内容不变：

```yaml
---
title: 从原文提取或概括的标题
description: 用一句话概括文章核心内容。
weight: 1
---

（原文正文内容保持不变）
```

`weight` 值：查看目标目录下已有文件的 weight，新文件取最大值 + 1。如果目录为空则从 1 开始。

### 步骤 4：更新父级 _index.md（仅新建子目录时）

**如果步骤 2 中新建了二级子目录**，必须同步更新该一级分类的 `_index.md`：

在 `## 知识板块` 列表末尾追加一行：

```markdown
- **新板块名称** — 简短描述该板块覆盖的内容
```

例如，在 `08-dev-tools/_index.md` 中添加「构建与打包」板块：

```markdown
- **构建与打包** — 可运行 JAR 打包、Fat JAR vs Nested JAR、插件对比与排错
```

如果二级子目录已存在，则**不需要**修改 `_index.md`。

### 步骤 5：构建验证

执行以下命令确认站点构建正常：

```powershell
hugo --cleanDestinationDir
```

验证要点：
- 构建成功，无 `ERROR` 或 `WARN` 输出
- 页面数（Pages）比之前增加了预期数量（新建子目录 +1，新增文章 +1）

---

## 五、操作示例

以「Java 可运行 JAR 包」文章为例，演示完整流程：

**输入**：一份关于 Maven 打包 JAR 的详细文档。

**步骤 1 — 判断归属**：
- 内容是 Maven 打包相关 → 一级分类：`08-dev-tools/`（开发工具）
- 具体是 JAR 打包方案 → 知识板块：「构建与打包」
- 检查 `08-dev-tools/` 下是否已有 `构建与打包/` 目录 → 当前没有，需新建

**步骤 2 — 确定路径**：
```
content/docs/08-dev-tools/构建与打包/可运行JAR包.md
```

**步骤 3 — 添加 front matter 并写入**：
```yaml
---
title: Java 可运行 JAR 包 —— 完整指南
description: 五种打包方案对比（assembly、shade、spring-boot、IDEA），含完整配置示例与常见问题排查。
weight: 1
---

（原文 740 行内容...）
```

**步骤 4 — 更新 `08-dev-tools/_index.md`**：

在 `## 知识板块` 列表末尾追加：
```markdown
- **构建与打包** — 可运行 JAR 打包、Fat JAR vs Nested JAR、插件对比与排错
```

**步骤 5 — 构建验证**：
```powershell
hugo --cleanDestinationDir
# 输出：Pages: 64（+2），0 errors
```

---

## 六、一级分类 _index.md 模板

每个一级分类目录下必须存在 `_index.md`，格式如下：

```yaml
---
title: 分类名称
linkTitle: 分类名称
description: 一句话描述该分类覆盖的知识范围。
type: docs
icon: fa-solid fa-xxx
weight: N
sidebar_root_for: self
sidebar_root_link_self: true
cascade:
  type: docs
  footer_style: slim
---

一句话介绍该分类的定位。

## 知识板块

- **板块A** — 描述
- **板块B** — 描述
- **板块C** — 描述
```

| 字段 | 说明 |
|------|------|
| `type` | 必须为 `docs` |
| `icon` | FontAwesome 图标类名 |
| `weight` | 与目录编号对应（01=1, 02=2, ..., 10=10, 递增） |
| `cascade` | 级联到子页面，不可省略 |

---

## 七、侧边栏根选择器（下拉卡片列表）

侧边栏顶部的下拉按钮会列出所有顶级栏目，读者可一键切换。每个卡片显示图标的、标题和描述。

### 数据来源

下拉列表由两类页面自动汇聚，按 `weight` 排序：

| 来源 | 说明 | 当前条目 |
|------|------|--------|
| 顶层内容目录 | `content/` 下的一级目录（`blog/`、`book/`、`docs/`） | 博客、书籍、笔记 |
| `sidebar_root_for: self` | 在 `_index.md` front matter 中声明的自根页面 | 10 个 docs 子分类 |

### 卡片内容取自 front matter

| 字段 | 用途 | 示例 |
|------|------|------|
| `icon` | 卡片左侧图标（FontAwesome 类名） | `fa-solid fa-code` |
| `linkTitle` | 卡片标题（优先于 `title`） | `Java 基础` |
| `description` | 卡片下方灰色描述文字 | `语言语法、面向对象、泛型、反射、异常处理与 IO。` |

### 配置开关

| 层级 | 字段 | 默认值 | 说明 |
|------|------|--------|------|
| 全局（`hugo.yaml`） | `params.ui.sidebar_root_menu` | `true` | 设为 `false` 可完全关闭下拉菜单 |
| 单页面（front matter） | `sidebar_root_menu` | 继承全局 | 设为 `false` 可将该条目从下拉列表中隐藏 |

### 新增一级分类时的同步操作

当新建一个一级分类（如 `11-xxx/`）时，下拉列表会**自动出现**新卡片（因为顶层目录自动纳入）。但需确保：

1. 新分类的 `_index.md` 包含 `icon`、`linkTitle`、`description` 三个字段 — 否则卡片显示不完整
2. 新分类的 `_index.md` 设置 `sidebar_root_for: self` — 使其成为独立的侧边栏根
3. 更新 `docs/_index.md` 的卡片导航链接 — 保持首页入口同步

---

## 八、构建与环境

### 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Go | >= 1.25.4 | Hugo 模块依赖管理 |
| Hugo | >= 0.160.1 **Extended** | 必须 Extended 版，标准版无法编译 SCSS |

### 常用命令

```powershell
# 开发预览（含草稿）
hugo serve -D

# 生产构建
hugo --cleanDestinationDir --gc --minify

# 验证构建是否正常
hugo --cleanDestinationDir
```

### 离线环境

主题已通过 `go.mod` 的 `replace` 指令本地化到 `oink-main/oink-main/`，无需联网即可构建。

---

## 九、约束与禁止事项

以下操作 **严格禁止**：

1. **新增一级分类时必须同步更新关联文件** — 更新分类体系表、`docs/_index.md` 卡片链接
2. **不可添加非中文文件** — 禁止创建 `.fr.md`、`.en.md` 等文件
3. **不可修改语言配置** — `hugo.yaml` 中 `languages` 和 `defaultContentLanguage` 不可更改
4. **不可修改主题目录** — `oink-main/` 下任何文件不可动
5. **新建二级子目录时必须同步更新父级 `_index.md`** — 在「知识板块」列表中添加新条目
6. **不可删除已有 `_index.md`** — 每个分类目录的入口文件不可缺失
7. **文章必须包含 front matter** — 缺少 `title`/`description`/`weight` 会导致页面异常
