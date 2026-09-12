---
title: pom.xml 核心要素详解 —— 读懂 Maven 的「采购清单」
weight: 3
description: pom.xml 配置项太多不知从哪下手？本文逐项拆解 pom.xml 的核心要素：GAV 坐标（groupId/artifactId/version）、SNAPSHOT 与 RELEASE 语义、properties 属性、build 构建配置、plugins 与 pluginManagement 的区别，并提供一个完整可运行的 Spring Boot pom.xml 模板。覆盖官方与社区最常遇到的配置问题。
---

## 为什么需要 pom.xml？

一个 Maven 项目如果没有 `pom.xml`，Maven 就不知道：
- 这个项目叫什么、版本多少（无法被其他项目依赖）
- 需要哪些第三方库（无法下载依赖）
- 用什么 JDK 版本编译（可能编译出错的字节码）
- 打包成 jar 还是 war（不知道最终产物是什么）

`pom.xml`（Project Object Model）就是 Maven 项目的**身份证 + 采购清单 + 施工蓝图**——它告诉 Maven「这个项目是什么」以及「构建这个项目需要什么」。

> ### 💡 新人小结：pom.xml 是什么？
>
> 把 `pom.xml` 想象成一份**标准化的采购施工蓝图**：
> - **身份证**：项目名称（name）、编号（GAV 坐标）、负责人（developers）
> - **采购清单**：需要哪些材料（dependencies）
> - **施工蓝图**：怎么加工（build 配置、插件绑定）
>
> 一句话总结：**pom.xml 是 Maven 项目的唯一描述文件，Maven 的一切行为都从它推导**。

**学习路线图**

```
GAV 坐标 → 项目信息 → properties → 依赖声明 → build 配置 → 插件管理 → 完整模板
是什么编号   谁做的      统一变量     要什么材料    怎么加工      工具管理     长什么样
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| GAV | GroupId, ArtifactId, Version | 构件的三个坐标：谁生产的、叫什么、哪个版本 | pom.xml 的「身份证」部分 |
| SNAPSHOT | — | 快照版本，表示开发中的不稳定版本，每次构建可能不同 | 版本号的特殊后缀 |
| pluginManagement | — | 插件的「版本锁定区」：声明插件版本和默认配置，但不实际激活 | 工具采购清单（只列不买） |
| plugins | — | 实际激活的插件：Maven 构建时真正执行的插件 | 工具使用清单（实际启用） |
| properties | — | pom.xml 里的变量定义区，用于统一管理版本号、编码等 | 全局变量表 |
| packaging | — | 打包类型：jar / war / ear / pom 等 | 决定最终产物格式 |
| parent | — | 父 POM：子项目继承其配置 | 多模块项目的配置复用 |
| BOM | Bill of Materials | 物料清单：一种特殊的 POM，只管理版本号不引入依赖 | 版本统一管理方案 |

---

## GAV 坐标：构件的唯一标识

每个 Maven 构件（jar、war、pom 等）都由三个字段唯一确定：

```xml
<project>
    <groupId>com.example</groupId>       <!-- 谁生产的（通常是域名反写） -->
    <artifactId>user-service</artifactId> <!-- 叫什么（项目/模块名） -->
    <version>1.0.0</version>              <!-- 哪个版本 -->
</project>
```

### groupId 的命名约定

| 场景 | 推荐格式 | 示例 |
|------|---------|------|
| 公司项目 | 域名反写 | `com.alibaba`、`org.apache` |
| 个人开源 | 域名反写或 `io.github.xxx` | `io.github.zhangsan` |
| Spring 生态 | `org.springframework.boot` | 官方固定 |

**不是强制要求**，但遵守约定能避免命名冲突。

### version 的版本号规范

推荐使用**语义化版本**（Semantic Versioning）：`主版本.次版本.修订号`

| 版本号 | 含义 | 示例 |
|--------|------|------|
| `1.0.0` | 正式版（GA = General Availability） | 首次发布 |
| `1.1.0` | 新增功能，向后兼容 | 加了新接口 |
| `1.1.1` | 修 bug，向后兼容 | 修了空指针 |
| `2.0.0` | 不兼容的变更 | 删了旧接口 |

### SNAPSHOT 与 RELEASE

| 版本后缀 | 含义 | Maven 行为 |
|---------|------|-----------|
| `1.0.0-SNAPSHOT` | 开发中的快照版本 | 每次 `mvn deploy` 都会覆盖远程仓库的同名构件；本地构建时 Maven 会检查是否有更新 |
| `1.0.0` 或 `1.0.0-RELEASE` | 正式发布版本 | 一旦发布不可更改（同名版本再发布会被拒绝） |

> ### 💡 新人小结：SNAPSHOT 是什么？
>
> SNAPSHOT 就像**连载中的漫画**——作者随时可能更新最新章节，读者每次去书店（仓库）都可能拿到不同的内容。而正式版就像**已完结的单行本**——印好了就不会再改。
>
> 开发阶段用 SNAPSHOT，发布时用正式版。

---

## 项目信息段

```xml
<project>
    <groupId>com.example</groupId>
    <artifactId>user-service</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>           <!-- 打包类型，默认 jar -->

    <name>User Service</name>            <!-- 人类可读的项目名 -->
    <description>用户管理微服务</description>
    <url>https://github.com/example/user-service</url>

    <licenses>...</licenses>             <!-- 许可证（开源项目必填） -->
    <developers>...</developers>         <!-- 开发者列表 -->
    <scm>...</scm>                       <!-- 源码管理地址 -->
</project>
```

这些信息不影响构建，但会出现在仓库页面和发布说明中。开源项目尤其重要。

---

## properties：统一变量管理

`<properties>` 是 pom.xml 里的**全局变量表**——把重复出现的值提取成变量，修改时只改一处。

```xml
<properties>
    <!-- 编码设置（几乎所有项目都要设） -->
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <maven.compiler.encoding>UTF-8</maven.compiler.encoding>

    <!-- JDK 版本 -->
    <java.version>17</java.version>
    <maven.compiler.source>${java.version}</maven.compiler.source>
    <maven.compiler.target>${java.version}</maven.compiler.target>

    <!-- 统一版本号 -->
    <spring-boot.version>3.2.0</spring-boot.version>
    <mybatis-plus.version>3.5.5</mybatis-plus.version>
    <hutool.version>5.8.25</hutool.version>
</properties>
```

使用变量：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>${spring-boot.version}</version>    <!-- 引用变量 -->
</dependency>
```

### 内置属性

Maven 自带一些内置属性，可以直接引用：

| 属性 | 含义 | 示例值 |
|------|------|--------|
| `${project.version}` | 当前项目版本 | `1.0.0` |
| `${project.groupId}` | 当前项目 groupId | `com.example` |
| `${project.artifactId}` | 当前项目 artifactId | `user-service` |
| `${project.basedir}` | pom.xml 所在目录的绝对路径 | `/home/user/my-project` |
| `${user.home}` | 用户主目录 | `/home/user` |
| `${java.home}` | JDK 安装目录 | `/usr/lib/jvm/java-17` |

---

## 依赖声明

依赖声明是 pom.xml 最核心的部分（详细的依赖管理机制参见第四篇《Maven 依赖管理实战》）：

```xml
<dependencies>
    <!-- 最简形式：GAV 三要素 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>3.2.0</version>
    </dependency>

    <!-- 带 scope -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.30</version>
        <scope>provided</scope>          <!-- 编译时需要，运行时容器提供 -->
    </dependency>

    <!-- 带 exclusion（排除传递依赖） -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>some-lib</artifactId>
        <version>2.0.0</version>
        <exclusions>
            <exclusion>
                <groupId>commons-logging</groupId>   <!-- 排除不想要的传递依赖 -->
                <artifactId>commons-logging</artifactId>
            </exclusion>
        </exclusions>
    </dependency>

    <!-- 测试依赖 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.1</version>
        <scope>test</scope>              <!-- 只在测试时使用 -->
    </dependency>
</dependencies>
```

---

## build 配置

`<build>` 控制「怎么加工」——编译选项、资源处理、插件绑定。

```xml
<build>
    <!-- 最终产物文件名（不含后缀） -->
    <finalName>${project.artifactId}-${project.version}</finalName>

    <!-- 资源处理 -->
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>          <!-- 开启资源过滤（替换占位符） -->
            <includes>
                <include>**/*.yml</include>      <!-- 只过滤 yml 文件 -->
                <include>**/*.properties</include>
            </includes>
        </resource>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>false</filtering>         <!-- 其他资源不过滤 -->
            <excludes>
                <exclude>**/*.yml</exclude>
                <exclude>**/*.properties</exclude>
            </excludes>
        </resource>
    </resources>

    <!-- 插件声明 -->
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <version>${spring-boot.version}</version>
            <executions>
                <execution>
                    <goals>
                        <goal>repackage</goal>   <!-- 打包为可执行 jar -->
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

---

## plugins vs pluginManagement

这是新手最容易搞混的地方：

| 对比维度 | `<pluginManagement>` | `<plugins>` |
|---------|---------------------|-------------|
| 作用 | **声明**插件的版本和默认配置 | **激活**插件（真正执行） |
| 类比 | 工具采购清单（列了但没买） | 工具使用清单（实际在用） |
| 子模块继承 | ✅ 子模块自动继承版本和配置 | ✅ 子模块自动继承激活状态 |
| 典型使用位置 | 父 POM（统一版本） | 子模块或父 POM（需要立即执行） |

### 正确用法

```xml
<!-- 父 POM：统一管理插件版本 -->
<build>
    <pluginManagement>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>
</build>

<!-- 子模块：只声明使用，不重复写版本和配置 -->
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <!-- 不需要 version —— 从 pluginManagement 继承 -->
            <!-- 不需要 configuration —— 从 pluginManagement 继承 -->
        </plugin>
    </plugins>
</build>
```

> ### 💡 新人小结：pluginManagement vs plugins
>
> `pluginManagement` 是**菜单**——列出了餐厅有哪些菜、什么价格；`plugins` 是**点单**——你实际点了哪些菜。菜单上有的菜你不一定点（pluginManagement 里有的插件不一定激活），但你点的菜一定在菜单上（plugins 里引用的插件版本来自 pluginManagement）。

---

## dependencyManagement vs dependencies

与插件类似，依赖也有「管理」和「使用」两个区域：

| 对比维度 | `<dependencyManagement>` | `<dependencies>` |
|---------|-------------------------|-----------------|
| 作用 | 声明依赖的**版本**，但不实际引入 | 实际引入依赖 |
| 子模块效果 | 子模块引用同名依赖时**不需要写版本号** | 子模块直接继承（自动引入） |
| 典型使用位置 | 父 POM / BOM | 子模块 / 当前项目 |

```xml
<!-- 父 POM：统一版本 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>my-app-common</artifactId>
            <version>1.0.0</version>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- 子模块：只写 GAV 中的 GA，版本从父 POM 继承 -->
<dependencies>
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>my-app-common</artifactId>
        <!-- 不需要 version -->
    </dependency>
</dependencies>
```

---

## parent：继承父 POM

```xml
<project>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>user-service</artifactId>
    <version>1.0.0</version>
    <!-- 不需要 packaging —— 默认 jar -->
    <!-- 不需要 properties 里的 JDK 版本 —— 从 parent 继承 -->
</project>
```

继承 `spring-boot-starter-parent` 后自动获得：
- JDK 编译版本设置
- 常用插件的默认版本和配置
- 资源过滤配置（`@...@` 占位符替换）
- 大量常用依赖的版本管理

---

## 完整 pom.xml 模板

一个典型的 Spring Boot 项目 pom.xml：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" ...>
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>                  <!-- 不从本地文件系统查找父 POM -->
    </parent>

    <groupId>com.example</groupId>
    <artifactId>user-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <java.version>17</java.version>
        <mybatis-plus.version>3.5.5</mybatis-plus.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>   <!-- 不需要 version -->
        </dependency>
        <dependency>
            <groupId>com.baomidou</groupId>
            <artifactId>mybatis-plus-spring-boot3-starter</artifactId>
            <version>${mybatis-plus.version}</version>         <!-- 用 properties 变量 -->
        </dependency>
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>                             <!-- 运行时才需要 -->
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>                          <!-- 可选，不传递给下游 -->
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>                                <!-- 仅测试用 -->
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **properties 里的版本号不生效** | 用了 `${...}` 但属性名拼错或定义顺序不对 | 检查属性名拼写；properties 按声明顺序解析，被引用的属性必须先定义 |
| **pluginManagement 里配了但插件没执行** | pluginManagement 只是声明，不会激活插件 | 在 `<plugins>` 里也声明该插件（不需要重复 version 和 configuration） |
| **子模块继承不到父 POM 的属性** | 子模块的 `<parent>` 配置有误（groupId/artifactId/version 不匹配） | 确认 parent 的 GAV 与父 POM 完全一致；父 POM 必须先 `mvn install` |
| **SNAPSHOT 版本不更新** | Maven 默认每天检查一次 SNAPSHOT 更新 | 使用 `mvn -U` 强制更新；或在仓库配置中设 `<updatePolicy>always</updatePolicy>` |
| **打包后配置文件里的中文乱码** | 编码设置不一致 | 确保 `<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>` 且 IDE 文件编码也是 UTF-8 |
| **`<scope>system</scope>` 报找不到 jar** | system scope 需要指定 `systemPath` 且路径必须存在 | 不推荐用 system scope——把 jar 部署到私服，用 compile scope |

---

## Q&A / 踩坑

**Q1：`<optional>true</optional>` 和 `<scope>provided</scope>` 有什么区别？**

`optional` 表示「这个依赖是可选的」——其他项目依赖你的项目时，不会自动引入这个 optional 依赖。`provided` 表示「运行时由容器提供」——不打入最终产物。Lombok 用 optional（其他项目不需要你的 Lombok），Servlet API 用 provided（Tomcat 自带）。

**Q2：`<relativePath/>` 空标签是什么意思？**

告诉 Maven 不要从本地文件系统查找父 POM，直接从仓库下载。如果不加，Maven 会先在 `../pom.xml` 找父项目，找不到再去仓库——可能导致意外的继承关系。

**Q3：为什么 Spring Boot 项目的 Lombok 不需要写 version？**

因为 `spring-boot-starter-parent` 的 `dependencyManagement` 里已经声明了 Lombok 的版本。继承 parent 后，子项目引用 Lombok 就不需要写版本了。

---

## 要点总结

1. **GAV 坐标是构件的唯一标识**：groupId（谁）+ artifactId（什么）+ version（哪个版本），SNAPSHOT 表示开发版、正式版不可覆盖
2. **properties 是全局变量表**：统一管版本号、编码设置，修改一处全局生效
3. **pluginManagement 声明、plugins 激活**：父 POM 用 pluginManagement 锁版本，子模块用 plugins 激活
4. **dependencyManagement 管版本、dependencies 实际引入**：与插件的 pluginManagement/plugins 关系完全对称
5. **继承 parent 获得默认配置**：Spring Boot parent 提供 JDK 版本、插件默认配置、资源过滤、依赖版本管理
6. **完整模板可直接复用**：本文提供的 Spring Boot pom.xml 模板覆盖了 Web + MyBatis-Plus + MySQL + Lombok + Hutool + 测试

---

> ### 💡 新人小结：pom.xml 学完了，记住这 3 点
>
> 1. **GAV 是身份证**：groupId + artifactId + version 三个字段缺一不可
> 2. **properties 管版本**：所有第三方库的版本号都放 properties 里，改版本只改一行
> 3. **parent 给默认值**：继承了 Spring Boot parent，大部分依赖都不需要写版本号
>
> 接下来，翻开第四篇《Maven 依赖管理实战》，深入理解传递依赖、scope、冲突解决。
