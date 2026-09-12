---
title: Maven 是什么 —— 从手动管 jar 到声明式构建的跨越
weight: 1
description: Maven 是什么？它解决了手动管理 jar 的哪些痛苦？本文从痛点出发，用采购代理类比讲清 Maven 的核心思想（约定优于配置、依赖管理、标准化生命周期），并对比 Ant / Gradle 的演进路线，覆盖官方与社区最常遇到的选型与使用问题。
---

## 为什么需要 Maven？

想象你刚入职一家公司，接手一个「老项目」。打开项目目录，你看到这样的场景：

```
my-project/
├── lib/
│   ├── spring-core-5.3.20.jar
│   ├── spring-web-5.3.20.jar
│   ├── commons-lang3-3.12.0.jar
│   ├── jackson-databind-2.13.3.jar
│   ├── jackson-core-2.13.3.jar
│   ├── jackson-annotations-2.13.3.jar
│   ├── slf4j-api-1.7.36.jar
│   ├── logback-classic-1.2.11.jar
│   └── ... 还有 30 多个 jar
├── src/
└── build.sh   ← 手写编译脚本，路径写死了
```

| 痛苦 | 没有 Maven 的世界 | 有了 Maven 之后 |
|------|-------------------|-----------------|
| **依赖获取** | 手动下载 jar 放进 lib/，版本对不对全靠肉眼 | 声明坐标，Maven 自动从仓库下载 |
| **版本冲突** | 两个 jar 依赖同一个库的不同版本，运行时才炸 | 依赖调解机制自动选版本，`dependency:tree` 一键排查 |
| **构建脚本** | 每个人写自己的 `build.sh`/`build.bat`，换台电脑就挂 | 标准生命周期，`mvn package` 一条命令跨平台通用 |
| **新人上手** | 「这个 jar 从哪下的？那个版本为什么不能用 3.x？」 | 读 `pom.xml` 就知道项目用了什么、版本多少 |
| **多模块协作** | 模块 A 改了代码，模块 B 手动替换 jar 才能联调 | `mvn install` 到本地仓库，兄弟模块自动拿到最新版 |

> ### 💡 新人小结：Maven 是什么？
>
> 把 Maven 想象成一个**采购代理 + 施工队**：
> - **采购代理**：你给它一张采购清单（`pom.xml`），它去建材市场（仓库）帮你把材料（jar）全部买齐，连材料 A 需要的辅料 B、C 也一并带回（传递依赖）
> - **施工队**：它按固定的施工流程（生命周期）帮你把材料加工成成品——清理场地 → 备料 → 施工 → 质检 → 打包 → 入库 → 发货
> - **统一编号**：每种材料有唯一的编号（GAV 坐标：厂商 + 产品名 + 版本号），不会买错
>
> 一句话总结：**Maven 让你用声明的方式管理依赖和构建，而不是用手动的方式**。

**学习路线图**

```
Maven 是什么 → 核心思想 → 演进对比 → 能力边界 → 常见问题
它解决什么      怎么想的     从哪来的     能做什么     怎么避坑
```

---

## 核心概念与专有名词

在深入之前，先把本文会用到的专有名词一次性讲清楚：

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| Maven | Apache Maven | Apache 基金会下的构建自动化工具，Java 生态最主流的构建与依赖管理工具 | 本文主角 |
| POM | Project Object Model | 项目对象模型，就是项目根目录下的 `pom.xml` 文件——Maven 的一切围绕它展开 | 采购清单，贯穿全文 |
| GAV | GroupId, ArtifactId, Version | 三个字段唯一确定一个构件：谁生产的（groupId）、叫什么（artifactId）、哪个版本（version） | 材料的唯一编号 |
| 构建工具 | Build Tool | 把源代码变成可运行产物的自动化工具（编译、测试、打包、部署） | Maven 的类别归属 |
| 依赖管理 | Dependency Management | 自动解析项目需要的第三方库及其版本，处理传递依赖与版本冲突 | Maven 的核心能力之一 |
| 生命周期 | Lifecycle | Maven 定义的标准化构建阶段序列（clean / default / site 三套） | Maven 的核心能力之三 |
| 插件 | Plugin | Maven 本身只定义流程，具体干活的是插件（compiler 编译、surefire 跑测试、jar 打包） | 施工队手里的工具 |
| 仓库 | Repository | 存放 jar 等构件的地方，分本地仓库、中央仓库、远程私服 | 建材市场 |
| 传递依赖 | Transitive Dependency | 你依赖 A，A 又依赖 B 和 C——B 和 C 就是传递依赖 | 买 A 附带的辅料 |

---

## Maven 的核心思想

Maven 的设计围绕三个核心思想，理解了这三点，后面所有配置和命令都是自然推出来的。

### 思想一：约定优于配置（Convention over Configuration）

没有 Maven 时，你需要写 `build.sh` 告诉编译器源码在哪、输出放哪、classpath 怎么拼。每个项目都写一遍，内容大同小异。

Maven 的做法是：**直接规定好**。

```
my-project/
├── src/
│   ├── main/
│   │   ├── java/        ← 源码默认放这里
│   │   └── resources/   ← 配置文件默认放这里
│   └── test/
│       ├── java/        ← 测试代码默认放这里
│       └── resources/   ← 测试配置默认放这里
├── target/              ← 构建产物默认输出到这里
└── pom.xml              ← 项目描述文件
```

只要你的项目按这个结构放，Maven 不需要你告诉它「源码在哪」——它**默认知道**。只有当你偏离约定时（比如源码放在 `source/` 而不是 `src/main/java/`），才需要在 `pom.xml` 里显式配置。

> ### 💡 新人小结：约定优于配置
>
> 就像快递柜——你不需要告诉柜子系统「我的快递放在哪一格」，系统默认按大小分配格子。只有超大件才需要人工干预。约定就是那个「默认分配规则」，省掉了 90% 的配置工作。

### 思想二：依赖管理（Dependency Management）

这是 Maven 最核心的能力。你只需要在 `pom.xml` 里声明「我需要什么」：

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-web</artifactId>
    <version>5.3.20</version>
</dependency>
```

Maven 会自动完成：
1. 去仓库下载 `spring-web-5.3.20.jar`
2. 读取它的 POM，发现它还依赖 `spring-core`、`spring-beans` 等
3. 递归下载所有传递依赖
4. 如果多个依赖引入了同一个库的不同版本，按「最近优先」原则调解

详细的依赖管理机制参见本板块第四篇《Maven 依赖管理实战》。

### 思想三：标准化生命周期

Maven 定义了三套标准生命周期，每套由若干阶段组成：

| 生命周期 | 用途 | 常用阶段 |
|---------|------|---------|
| **clean** | 清理上一次构建的产物 | `pre-clean` → `clean` → `post-clean` |
| **default** | 核心构建流程（编译→测试→打包→部署） | `validate` → `compile` → `test` → `package` → `install` → `deploy`（共 23 个阶段） |
| **site** | 生成项目文档站点 | `pre-site` → `site` → `post-site` → `site-deploy` |

日常最常用的命令 `mvn clean package` 就是先执行 clean 生命周期清理产物，再执行 default 生命周期到 package 阶段（包括前面所有阶段：验证→编译→测试→打包）。

完整的生命周期阶段列表参见本板块第六篇《Maven 命令与生命周期》。

---

## 演进对比：从手动到声明式

Maven 不是凭空出现的，它解决的是前代工具的痛点。下面按时间线展示构建工具的演进：

### 阶段一：手动管理（2000 年以前）

```bash
#!/bin/bash
# build.sh —— 每个项目都要手写
javac -cp lib/spring-core.jar:lib/commons-lang3.jar \
      -d target/classes \
      src/main/java/com/example/**/*.java
jar cf target/my-app.jar -C target/classes .
```

**痛点**：路径硬编码、跨平台困难、jar 手动下载、无版本管理。

### 阶段二：Apache Ant（2000-2004）

```xml
<!-- build.xml -->
<project name="my-app" default="compile">
    <path id="classpath">
        <fileset dir="lib" includes="*.jar"/>
    </path>
    <target name="compile">
        <javac srcdir="src/main/java" destdir="target/classes" classpathref="classpath"/>
    </target>
    <target name="jar" depends="compile">
        <jar destfile="target/my-app.jar" basedir="target/classes"/>
    </target>
</project>
```

**改进**：用 XML 描述构建过程，跨平台。
**痛点**：仍然是「命令式」——你必须告诉 Ant 每一步怎么做（编译→打包→复制），没有依赖管理，jar 还是要手动下载。

### 阶段三：Apache Maven（2004 至今）

```xml
<!-- pom.xml —— 只声明「要什么」 -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-web</artifactId>
            <version>5.3.20</version>
        </dependency>
    </dependencies>
</project>
```

```bash
mvn clean package   # 一条命令搞定构建
```

**改进**：声明式依赖管理、传递依赖自动解析、标准化生命周期、中央仓库。
**痛点**：XML 冗长、灵活性不如脚本（Groovy/Kotlin 脚本能做的事 Maven 要做很多配置）。

### 阶段四：Gradle（2012 至今）

```groovy
// build.gradle
plugins {
    id 'java'
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework:spring-web:5.3.20'
}
```

**改进**：DSL 更简洁、构建速度更快（增量构建 / 构建缓存 / 守护进程）、灵活性更强。
**痛点**：学习曲线陡（Groovy/Kotlin DSL + 插件 API）、生态不如 Maven 成熟（部分老库的 Maven 插件没有 Gradle 等价物）。

### 四代对比总表

| 对比维度 | 手动脚本 | Ant | Maven | Gradle |
|---------|---------|-----|-------|--------|
| 依赖管理 | ❌ 手动下载 | ❌ 手动下载 | ✅ 自动解析 | ✅ 自动解析 |
| 构建描述 | Shell/Bat 脚本 | XML（命令式） | XML（声明式） | Groovy/Kotlin DSL |
| 标准化 | ❌ 各自为政 | ❌ 各自定义 target | ✅ 标准生命周期 | ✅ 兼容 Maven 约定 |
| 学习曲线 | 低 | 中 | 中 | 高 |
| 构建速度 | 快（但功能少） | 快（但功能少） | 中 | 快（增量+缓存） |
| 社区生态 | 无 | 衰退 | 最成熟 | 快速增长 |
| 当前定位 | 教学/极小项目 | 遗留项目维护 | **Java 项目主流选择** | 新项目热门选择 |

---

## 快速上手：安装与第一个项目

### 安装 Maven

1. 确保已安装 JDK 8+（`java -version` 验证）
2. 从 [Maven 官方下载页](https://maven.apache.org/download.cgi) 下载最新稳定版（当前 **3.9.16**）的 Binary zip/tar.gz
3. 解压到任意目录（如 `C:\dev\apache-maven-3.9.16`）
4. 配置环境变量：
   - `MAVEN_HOME` = 解压目录
   - `PATH` 追加 `%MAVEN_HOME%\bin`
5. 验证安装：

```bash
mvn -version
# 输出示例：
# Apache Maven 3.9.16 (...)
# Maven home: C:\dev\apache-maven-3.9.16
# Java version: 17.0.8, vendor: Oracle Corporation
# Default locale: zh_CN, platform encoding: UTF-8
```

### 5 分钟跑通第一个 Maven 项目

不需要手写 `pom.xml`——Maven 提供了 archetype（项目骨架）快速生成：

```bash
# 用 archetype 生成一个标准 Maven 项目
mvn archetype:generate \
    -DgroupId=com.example \
    -DartifactId=hello-maven \
    -DarchetypeArtifactId=maven-archetype-quickstart \
    -DinteractiveMode=false

cd hello-maven
```

生成的目录结构：

```
hello-maven/
├── pom.xml
├── src/
│   ├── main/
│   │   └── java/
│   │       └── com/example/
│   │           └── App.java        ← 主类（含 main 方法）
│   └── test/
│       └── java/
│           └── com/example/
│               └── AppTest.java    ← 单元测试
```

```bash
# 编译 + 测试 + 打包，一条命令
mvn clean package

# 运行
java -cp target/hello-maven-1.0-SNAPSHOT.jar com.example.App
# 输出: Hello World!
```

> ### 💡 新人小结：第一个项目跑通了
>
> 注意你**没有**写编译脚本、**没有**手动下载 JUnit——Maven 自动从中央仓库下载了 JUnit（因为 archetype 生成的 `pom.xml` 里声明了 JUnit 依赖），自动编译、自动跑测试、自动打包。这就是「声明式构建」的威力。

---

## Maven 能做什么 / 不能做什么

### 能做什么

| 能力 | 说明 |
|------|------|
| 依赖管理 | 自动下载、解析传递依赖、调解版本冲突 |
| 标准化构建 | 编译→测试→打包→部署的标准流程 |
| 多模块管理 | parent pom + modules 聚合构建 |
| 插件生态 | 数千个插件覆盖代码生成、静态检查、打包、部署等 |
| 项目信息标准化 | 统一的坐标体系，任何 Maven 项目都能被任何 Maven 仓库识别 |
| 与 IDE 深度集成 | IntelliJ IDEA / Eclipse / VS Code 一键导入 Maven 项目 |

### 不能做什么

| 局限 | 说明 |
|------|------|
| 不是代码生成器 | Maven 本身不生成业务代码（但可以通过插件如 MyBatis Generator 间接实现） |
| 不是部署工具 | `mvn deploy` 只是把构件发布到 Maven 仓库，不是部署到服务器（需要 cargo / docker / kubernetes 插件） |
| 不是 CI/CD 工具 | Maven 不管理流水线（但 Jenkins / GitLab CI 可以调用 Maven 命令） |
| 构建速度不是最快 | 相比 Gradle 的增量构建和守护进程，Maven 的全量构建更慢 |
| 灵活性有限 | 复杂自定义构建逻辑需要写 Maven 插件（Java），不如 Gradle 的脚本灵活 |

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **Maven vs Gradle 怎么选？** | 新项目纠结构建工具 | Spring Boot 官方默认 Maven，企业项目 Maven 生态更成熟；追求构建速度和 DSL 灵活性选 Gradle。两者能力等价，选团队更熟悉的 |
| **离线环境能用 Maven 吗？** | 内网无法访问中央仓库 | 搭建内部私服（Nexus/Artifactory），或提前把依赖同步到本地仓库后使用 `-o`（offline 模式） |
| **Maven 一定要联网吗？** | 首次构建需要下载依赖和插件 | 首次必须联网；之后依赖缓存在本地仓库（`~/.m2/repository`），只要不换新依赖就不需要联网 |
| **Maven 4 什么时候正式发布？** | 关注版本演进 | Maven 4.0.0-rc-6 仍在预览阶段，要求 JDK 17+。生产环境继续使用 3.9.x（最新 3.9.16，要求 JDK 8+） |
| **Maven Daemon（mvnd）值得用吗？** | 构建速度慢想优化 | mvnd 1.0.6 是官方推荐的加速方案，通过守护进程避免 JVM 重复启动，大项目构建速度提升 3-5 倍。与 Maven 命令完全兼容 |
| **pom.xml 报红但能构建？** | IDE 索引与本地仓库不一致 | 在 IntelliJ IDEA 中点击「Reload All Maven Projects」刷新索引 |

---

## Q&A / 踩坑

**Q1：Maven 和 Ant 能一起用吗？**

技术上可以（Ant 插件 `maven-antrun-plugin` 可以在 Maven 生命周期中执行 Ant 任务），但不推荐。新项目直接用 Maven 原生插件，遗留 Ant 脚本可以逐步迁移。

**Q2：为什么 Maven 的 groupId 通常写成域名反写（如 `com.example`）？**

这是约定而非强制。域名反写能保证全局唯一性（`com.alibaba` 不会和 `org.apache` 冲突）。你也可以用 `io.github.yourname`，但不建议用中文或特殊字符。

**Q3：一个项目可以有多个 pom.xml 吗？**

多模块项目中，每个子模块有自己的 `pom.xml`，同时有一个父 `pom.xml` 通过 `<modules>` 聚合。子模块通过 `<parent>` 继承父 POM 的配置。详见第三篇《pom.xml 核心要素详解》。

**Q4：Maven 支持 Kotlin / Scala / Groovy 等非 Java 语言吗？**

支持，但需要对应的编译插件（如 `kotlin-maven-plugin`、`scala-maven-plugin`）。Maven 本身是语言无关的——它只管理生命周期和依赖，编译什么语言由插件决定。

---

## 要点总结

1. **Maven = 采购代理 + 施工队**：你声明「要什么」（pom.xml），它负责去仓库下载（依赖管理）并按标准流程加工（生命周期）
2. **三大核心思想**：约定优于配置（标准目录结构）、依赖管理（自动解析传递依赖）、标准化生命周期（clean / default / site）
3. **GAV 坐标是唯一标识**：groupId（谁）+ artifactId（什么）+ version（哪个版本），任何构件都靠这三个字段定位
4. **演进路线**：手动脚本 → Ant（命令式 XML）→ Maven（声明式 XML + 依赖管理）→ Gradle（DSL + 增量构建），Maven 仍是当前 Java 生态最主流的选择
5. **Maven 不是万能的**：它管构建和依赖，不管部署、CI/CD、代码生成——这些需要配合其他工具
6. **当前版本**：生产环境用 Maven 3.9.16（JDK 8+），4.0.x 尚在预览（JDK 17+）；追求构建速度可搭配 Maven Daemon（mvnd 1.0.6）

---

> ### 💡 新人小结：Maven 学完了，记住这 3 点
>
> 1. **pom.xml 是采购清单**：你只管写「我要 spring-web 5.3.20」，Maven 帮你搞定一切
> 2. **目录结构是约定**：源码放 `src/main/java`，测试放 `src/test/java`，别改——改了就要多写配置
> 3. **`mvn clean package` 是万能入口**：清理→编译→测试→打包，一条命令全搞定
>
> 接下来，翻开第二篇《Maven 项目结构详解》，看看这个「约定」到底约定了什么。
