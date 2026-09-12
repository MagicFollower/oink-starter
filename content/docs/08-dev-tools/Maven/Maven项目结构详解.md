---
title: Maven 项目结构详解 —— 约定优于配置的最佳实践
weight: 2
description: Maven 项目的标准目录布局是什么？为什么源码放 src/main/java 而不是随便放？多模块项目怎么组织？archetype 骨架怎么用？本文从标准结构出发，讲清「约定」背后的设计理由，覆盖多模块、资源过滤、测试资源分离等实战场景与常见问题。
---

## 为什么需要标准项目结构？

接手一个新项目，你的第一反应是找源码——但如果每个项目的目录结构都不一样：

```
项目 A：src/com/example/Main.java
项目 B：source/Main.java
项目 C：code/src/Main.java
项目 D：trunk/src/main/java/com/example/Main.java
```

每次切换项目都要重新适应目录结构，IDE 配置也要跟着改。更糟糕的是，新人入职第一天就要问：「源码在哪？测试在哪？配置文件在哪？」

Maven 的做法是：**规定一个所有人都遵守的标准结构**。只要项目按这个结构组织，任何 IDE 都能一键导入，任何开发者都能立即上手，`mvn compile` 不需要额外告诉它源码在哪。

> ### 💡 新人小结：标准结构是什么？
>
> 把 Maven 项目想象成一个**标准仓库**：
> - **正门左手边**（`src/main/java`）：正式产品（主源码）
> - **正门右手边**（`src/main/resources`）：产品说明书（配置文件、模板等）
> - **后门左手边**（`src/test/java`）：质检车间（测试代码）
> - **后门右手边**（`src/test/resources`）：质检用的样品（测试配置、测试数据）
> - **出货区**（`target/`）：加工完成的成品（编译产物、打包文件）
>
> 一句话总结：**所有人按同一个仓库布局放东西，闭着眼睛都能找到**。

**学习路线图**

```
标准目录布局 → 为什么是这个结构 → 多模块项目 → archetype 骨架 → 资源处理 → 常见问题
长什么样        设计理由          怎么拆分       怎么快速创建      怎么过滤     怎么避坑
```

---

## 标准目录布局

一个典型的 Maven 单模块项目结构如下：

```
my-project/
├── pom.xml                          ← 项目描述文件（必须有）
├── src/
│   ├── main/
│   │   ├── java/                    ← 主源码（.java 文件）
│   │   │   └── com/example/
│   │   │       ├── App.java
│   │   │       └── service/
│   │   │           └── UserService.java
│   │   ├── resources/               ← 主资源文件（配置文件、模板等）
│   │   │   ├── application.yml
│   │   │   ├── logback.xml
│   │   │   └── templates/
│   │   │       └── email.html
│   │   ├── webapp/                  ← Web 应用资源（仅 war 项目）
│   │   │   ├── WEB-INF/
│   │   │   │   └── web.xml
│   │   │   └── index.jsp
│   │   └── filters/                 ← 资源过滤模板（少见）
│   └── test/
│       ├── java/                    ← 测试源码
│       │   └── com/example/
│       │       ├── AppTest.java
│       │       └── service/
│       │           └── UserServiceTest.java
│       └── resources/               ← 测试资源文件
│           └── test-data.json
└── target/                          ← 构建产物（自动生成，不提交到 Git）
    ├── classes/                     ← 编译后的 .class 文件
    ├── test-classes/                ← 编译后的测试 .class 文件
    ├── my-project-1.0.0.jar         ← 打包产物
    └── surefire-reports/            ← 测试报告
```

### 每个目录的职责

| 目录 | 职责 | 是否必须 | 打包时是否包含 |
|------|------|---------|--------------|
| `pom.xml` | 项目描述文件，Maven 的一切围绕它展开 | **必须** | — |
| `src/main/java` | 主源码 | 有源码则必须 | ✅ 编译后打入 jar/war |
| `src/main/resources` | 主资源（配置文件、模板等） | 可选 | ✅ 原样打入 jar/war 的 classpath 根 |
| `src/main/webapp` | Web 应用资源（JSP、静态文件） | 仅 war 项目 | ✅ 按 WAR 规范组织 |
| `src/test/java` | 测试源码 | 可选 | ❌ 不打入最终产物 |
| `src/test/resources` | 测试资源（测试数据、测试配置） | 可选 | ❌ 不打入最终产物 |
| `target/` | 构建输出目录 | 自动生成 | — |

> ### 💡 新人小结：target/ 为什么不应该提交到 Git？
>
> `target/` 里的所有文件都是 Maven **自动生成**的——编译产物、打包文件、测试报告。它们完全可以从源码重新生成，提交到 Git 只会增加仓库体积、制造合并冲突。在 `.gitignore` 里加一行 `target/` 就够了。

---

## 为什么是这个结构？

Maven 的标准目录结构不是拍脑袋决定的，每个选择都有理由：

### 1. `src/main` vs `src/test` 分离

**理由**：主代码和测试代码的「生命周期」不同。
- 主代码打入最终产物（jar/war），测试代码不打入
- 测试代码可以依赖测试专用的库（JUnit、Mockito），这些库不应该出现在生产环境
- 分离后，`mvn compile` 只编译主代码，`mvn test-compile` 才编译测试代码

### 2. `java/` vs `resources/` 分离

**理由**：源码需要编译，资源不需要。
- `java/` 下的 `.java` 文件会被 `javac` 编译成 `.class` 文件
- `resources/` 下的文件**原样复制**到输出目录（classpath 根路径）
- 分离后，Maven 可以对资源文件做**过滤**（替换占位符、排除敏感配置）

### 3. 包目录与 GAV 的 groupId 对应

```
groupId: com.example
artifactId: user-service

src/main/java/com/example/user/service/UserService.java
```

虽然不是强制要求，但约定包名与 groupId 对应，能让项目结构一目了然。

### 4. `target/` 而不是 `build/` 或 `out/`

Maven 选择了 `target/` 作为输出目录名。Gradle 用 `build/`，IDEA 默认用 `out/`。这是各工具的约定不同，不要混用。

---

## 多模块项目

当项目规模增大，一个 Maven 项目不够用时，就需要**多模块项目**——一个父项目 + 若干子模块。

### 典型的多模块结构

```
my-app/                              ← 父项目（聚合 POM）
├── pom.xml                          ← 父 POM（packaging=pom）
├── my-app-common/                   ← 公共模块
│   ├── pom.xml
│   └── src/main/java/...
├── my-app-service/                  ← 业务模块
│   ├── pom.xml
│   └── src/main/java/...
├── my-app-web/                      ← Web 模块
│   ├── pom.xml
│   └── src/main/java/...
└── my-app-starter/                  ← 启动模块
    ├── pom.xml
    └── src/main/java/...
```

### 父 POM 的关键配置

```xml
<!-- 父 pom.xml -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>        <!-- 父项目不产出 jar，packaging 必须是 pom -->

    <modules>                         <!-- 声明子模块 -->
        <module>my-app-common</module>
        <module>my-app-service</module>
        <module>my-app-web</module>
        <module>my-app-starter</module>
    </modules>

    <properties>                      <!-- 统一版本号 -->
        <java.version>17</java.version>
        <spring-boot.version>3.2.0</spring-boot.version>
    </properties>

    <dependencyManagement>            <!-- 统一管理依赖版本 -->
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-dependencies</artifactId>
                <version>${spring-boot.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

### 子模块 POM

```xml
<!-- my-app-service/pom.xml -->
<project>
    <modelVersion>4.0.0</modelVersion>

    <parent>                          <!-- 继承父 POM -->
        <groupId>com.example</groupId>
        <artifactId>my-app</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>my-app-service</artifactId>
    <!-- 不需要写 version —— 从父 POM 继承 -->
    <!-- 不需要写 groupId —— 从父 POM 继承 -->

    <dependencies>
        <dependency>                  <!-- 不需要写 version —— 从 dependencyManagement 继承 -->
            <groupId>com.example</groupId>
            <artifactId>my-app-common</artifactId>
        </dependency>
    </dependencies>
</project>
```

> ### 💡 新人小结：多模块项目
>
> 多模块项目就像一个**集团公司**：
> - **父 POM** = 集团总部：定规矩（统一版本号、统一依赖管理）、管协调（声明子模块列表）
> - **子模块** = 子公司：各管各的业务，但遵守总部的规矩（继承 version、groupId、dependencyManagement）
> - **`mvn install`** = 集团统一发货：在父目录执行一条命令，所有子模块按依赖顺序编译打包

### 多模块的构建顺序

Maven 会自动分析模块间的依赖关系，决定构建顺序：

```
my-app-common      ← 无依赖，先构建
    ↓
my-app-service     ← 依赖 common，第二构建
    ↓
my-app-web         ← 依赖 service，第三构建
    ↓
my-app-starter     ← 依赖 web，最后构建
```

不需要手动指定顺序——Maven 的 **reactor** 机制会自动拓扑排序。

---

## archetype：项目骨架

`archetype` 是 Maven 的「项目模板」机制——类似于 IDE 的「New Project」向导，但更灵活。

### 常用 archetype

| archetype | 用途 | 生成内容 |
|-----------|------|---------|
| `maven-archetype-quickstart` | 最基础的 Java 项目 | 一个 App.java + 一个 AppTest.java |
| `maven-archetype-webapp` | 基础 Web 项目 | webapp 目录 + web.xml + index.jsp |
| Spring Initializr | Spring Boot 项目 | 完整的 Spring Boot 项目结构（推荐用 [start.spring.io](https://start.spring.io)） |

### 使用 archetype 创建项目

```bash
# 交互式创建
mvn archetype:generate

# 非交互式创建（指定所有参数）
mvn archetype:generate \
    -DgroupId=com.example \
    -DartifactId=my-service \
    -DarchetypeArtifactId=maven-archetype-quickstart \
    -DinteractiveMode=false
```

> 实际开发中，Spring Boot 项目更推荐用 [start.spring.io](https://start.spring.io) 或 IDE 的 Spring Initializr 插件生成，比 archetype 更方便。

---

## 资源处理

### 资源过滤（Resource Filtering）

Maven 可以在复制资源文件时替换占位符——常用于把版本号、环境信息注入配置文件：

```xml
<!-- pom.xml -->
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>    <!-- 开启资源过滤 -->
        </resource>
    </resources>
</build>

<properties>
    <app.version>${project.version}</app.version>
</properties>
```

```properties
# src/main/resources/application.properties
app.version=@app.version@
```

构建后 `target/classes/application.properties` 中 `@app.version@` 会被替换为实际的版本号。

### 排除敏感资源

```xml
<resources>
    <resource>
        <directory>src/main/resources</directory>
        <excludes>
            <exclude>**/application-local.yml</exclude>   <!-- 排除本地配置 -->
            <exclude>**/*.key</exclude>                    <!-- 排除密钥文件 -->
        </excludes>
    </resource>
</resources>
```

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **资源文件没被打入 jar** | 资源放错了目录（放在了 `src/main/java` 下而不是 `src/main/resources`） | 非 `.java` 文件放 `src/main/resources`；如果必须放 `java` 目录，需要在 `<resources>` 里显式声明 |
| **资源过滤不生效** | `<filtering>` 没设为 `true` | 在 `<build><resources>` 里对目标 resource 目录设置 `<filtering>true</filtering>` |
| **测试代码找不到测试资源** | 测试资源放在了 `src/main/resources` 而不是 `src/test/resources` | 测试专用数据放 `src/test/resources`，Maven 会自动加入测试 classpath |
| **多模块构建顺序不对** | 模块间存在循环依赖 | Maven reactor 会报错 `Dependency cycle detected`；需要重新设计模块拆分，消除循环依赖 |
| **子模块找不到父 POM** | 父 POM 没有 `mvn install` 到本地仓库 | 先在父目录执行 `mvn install`，再进子模块构建；或直接在父目录构建所有模块 |
| **target/ 被提交到 Git** | `.gitignore` 没配置 | 项目根目录 `.gitignore` 加 `target/` |
| **IDE 报红但命令行能构建** | IDE 的 Maven 索引没刷新 | IntelliJ IDEA：点击 Maven 面板的「Reload All Maven Projects」按钮 |

---

## Q&A / 踩坑

**Q1：可以把源码放在 `src/main/java` 以外的目录吗？**

可以，但需要在 `pom.xml` 里显式配置 `<build><sourceDirectory>`。除非有历史包袱，否则不建议偏离约定——偏离意味着每个新人都要多问一句「源码到底放哪了」。

**Q2：`src/main/resources` 里的文件和 `src/main/java` 里的同名文件冲突吗？**

不冲突——它们会被合并到同一个 classpath 根目录。但如果有同名文件，后处理的会覆盖先处理的。建议避免同名。

**Q3：多模块项目一定要用 `<parent>` 继承吗？**

不一定。也可以用 `<dependencyManagement>` + BOM import 的方式共享版本管理，不建立继承关系。继承关系会让子模块耦合到父 POM 的生命周期，BOM import 更灵活。详见第三篇《pom.xml 核心要素详解》。

**Q4：`src/main/webapp` 只有 war 项目才需要吗？**

是的。`jar` 项目不需要 `webapp` 目录。如果你在做 Spring Boot 项目，静态资源通常放在 `src/main/resources/static/` 而不是 `webapp`。

---

## 要点总结

1. **标准目录布局是 Maven 的「约定」**：`src/main/java`（源码）、`src/main/resources`（资源）、`src/test/java`（测试）、`target/`（产物）——遵守约定 = 零配置
2. **`target/` 是自动生成的**：永远不要手动编辑 `target/`，永远不要把 `target/` 提交到 Git
3. **多模块 = 父 POM 聚合 + 子模块继承**：父 POM 的 `packaging` 必须是 `pom`，通过 `<modules>` 声明子模块，通过 `<dependencyManagement>` 统一版本
4. **资源过滤可以注入变量**：`<filtering>true</filtering>` + `@property@` 占位符，构建时自动替换
5. **archetype 是项目模板**：`maven-archetype-quickstart` 适合纯 Java 项目，Spring Boot 项目推荐用 start.spring.io
6. **偏离约定需要显式配置**：源码放别处、资源需要过滤、排除敏感文件——都要在 `pom.xml` 的 `<build>` 段里声明

---

> ### 💡 新人小结：项目结构学完了，记住这 3 点
>
> 1. **源码放 `src/main/java`，配置放 `src/main/resources`**——别问为什么，所有 Maven 项目都这样
> 2. **多模块项目在父目录 `mvn install`**——Maven 自动按依赖顺序构建所有子模块
> 3. **`target/` 是临时的**——`mvn clean` 随时清掉重建，不心疼
>
> 接下来，翻开第三篇《pom.xml 核心要素详解》，看看这张「采购清单」到底怎么写。
