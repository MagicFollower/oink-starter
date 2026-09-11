---
title: Java 可运行 JAR 包 —— 完整指南
description: 五种打包方案对比（assembly、shade、spring-boot、IDEA），含完整配置示例与常见问题排查。
weight: 1
---

> 整合自两篇笔记（2024 版、2025 版），结合社区与官方最佳实践。

---

## 一、需求分析

### 1.1 什么是可运行 JAR 包

可通过以下命令直接启动的 JAR 文件：

```bash
java -jar -Dfile.encoding=UTF-8 XXX.jar
```

核心要求：JAR 的 `META-INF/MANIFEST.MF` 中必须包含 `Main-Class` 属性，指定程序入口类。

### 1.2 核心问题

如何将项目本身及其所有第三方依赖，打包为一个可直接运行的 JAR 文件？

### 1.3 两大分类

| 分类 | 依赖存放形式 | 代表方案 |
|------|-------------|---------|
| **Fat JAR（uber-jar）** | 依赖被解压，所有 .class 文件平铺合并到同一个 JAR 中 | maven-shade-plugin、maven-assembly-plugin (jar-with-dependencies) |
| **Nested JAR** | 依赖以 .jar 形式嵌套存放在主 JAR 内部（如 `lib/` 或 `BOOT-INF/lib/`） | spring-boot-maven-plugin、maven-assembly-plugin (自定义 assembly.xml) |

> **注意**：标准 Java 类加载器无法加载嵌套在 JAR 内部的 JAR。Spring Boot 通过自定义 `LaunchedURLClassLoader` 解决了这一问题；而使用自定义 assembly.xml 时，需将 `lib/` 目录放在 JAR 外部，并通过 `Class-Path` manifest 属性指定依赖路径。

---

## 二、方案总览与对比分析

### 2.1 五种方案一览

| # | 方案 | 适用场景 | 依赖存放形式 | 关键插件/工具 |
|---|------|----------|-------------|--------------|
| 1 | maven-assembly-plugin (jar-with-dependencies) | 非 Spring 项目，简单场景 | .class 合并 | maven-assembly-plugin |
| 2 | maven-assembly-plugin (自定义 assembly.xml) | 需要 lib/ 目录独立存放依赖 jar | .jar 嵌套（JAR 外部） | maven-assembly-plugin + assembly.xml |
| 3 | maven-shade-plugin | 非 Spring 项目，需要类重命名/资源合并 | .class 合并（可重命名包） | maven-shade-plugin |
| 4 | spring-boot-maven-plugin | Spring Boot 项目 | .jar 嵌套（BOOT-INF/lib/） | spring-boot-maven-plugin |
| 5 | IDEA 工件（Artifact） | 非 Maven 项目或快速原型 | .jar 嵌套 | IntelliJ IDEA |

### 2.2 优劣势对比

| 维度 | assembly (jar-with-deps) | assembly (自定义) | shade | spring-boot | IDEA 工件 |
|------|-------------------------|-------------------|-------|-------------|-----------|
| `java -jar` 直接运行 | 可以 | 需 lib/ 在 JAR 外部 | 可以 | 可以 | 视配置而定 |
| 类路径冲突风险 | 高（class 平铺可能重名） | 无（独立 jar） | 低（可重命名包） | 无（嵌套 jar） | 无 |
| 资源文件合并能力 | 弱 | 无 | 强（Transformer 机制） | 不适用 | 无 |
| 配置复杂度 | 低 | 中（需额外 assembly.xml） | 中 | 极低 | 低（GUI 操作） |
| 产物体积 | 中等 | 较大（jar 有额外开销） | 中等 | 中等 | 较大 |
| 签名文件冲突 | 可能出现 | 无 | 需手动排除 | 不适用 | 可能出现 |
| Spring Boot 兼容 | 不推荐 | 不推荐 | 不推荐 | 首选 | 不推荐 |

---

## 三、各方案详细配置与最小示例

### 3.1 maven-assembly-plugin — jar-with-dependencies（lib 被编译为.class放进 fatjar）

**适用场景**：非 Spring 的普通 Maven 项目，希望快速打出一个包含所有依赖的 fat jar。

**完整 pom.xml 最小示例**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>simple-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>org.example.Main</mainClass>
                        </manifest>
                    </archive>
                    <descriptorRefs>
                        <!-- 将所有依赖编译为 class 平铺打入 -->
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                </configuration>
                <executions>
                    <execution>
                        <id>make-assembly</id>
                        <phase>package</phase>
                        <goals>
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

**构建与验证**：

```bash
mvn clean package

# 产物：target/simple-demo-1.0-SNAPSHOT-jar-with-dependencies.jar
java -jar target/simple-demo-1.0-SNAPSHOT-jar-with-dependencies.jar
```

---

### 3.2 maven-assembly-plugin — 自定义 assembly.xml（lib 目录模式）

**适用场景**：希望依赖以独立 jar 形式存放在 `lib/` 目录中，便于查看或替换单个依赖。

**assembly.xml**（放在项目根目录）：

```xml
<assembly>
    <id>custom-assembly</id>
    <formats>
        <format>jar</format>
    </formats>
    <includeBaseDirectory>false</includeBaseDirectory>
    <!-- 将项目编译后的 class 文件放在 JAR 根目录 -->
    <fileSets>
        <fileSet>
            <directory>${project.build.outputDirectory}</directory>
            <outputDirectory>/</outputDirectory>
        </fileSet>
    </fileSets>
    <!-- 将依赖 jar 放在 lib/ 子目录 -->
    <dependencySets>
        <dependencySet>
            <outputDirectory>lib</outputDirectory>
            <useProjectArtifact>false</useProjectArtifact>
            <unpack>false</unpack>
        </dependencySet>
    </dependencySets>
</assembly>
```

**pom.xml 插件配置**：

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-assembly-plugin</artifactId>
            <version>3.6.0</version>
            <configuration>
                <appendAssemblyId>false</appendAssemblyId>
                <finalName>${project.artifactId}-${project.version}</finalName>
                <archive>
                    <manifest>
                        <mainClass>org.example.Main</mainClass>
                    </manifest>
                    <!-- 关键：指定 Class-Path，让 JVM 找到 lib/ 下的依赖 jar -->
                    <manifestEntries>
                        <Class-Path>lib/gson-2.10.1.jar</Class-Path>
                    </manifestEntries>
                </archive>
                <descriptors>
                    <descriptor>assembly.xml</descriptor>
                </descriptors>
            </configuration>
            <executions>
                <execution>
                    <id>make-assembly</id>
                    <phase>package</phase>
                    <goals>
                        <goal>single</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

> **重要提示**：使用此方式时，`lib/` 目录必须在 JAR 文件外部（同级目录），否则标准类加载器无法加载嵌套在 JAR 内的 jar 文件。

**产物目录结构**：

```
target/
├── simple-demo-1.0-SNAPSHOT.jar   （主 JAR）
└── lib/
    └── gson-2.10.1.jar             （依赖 jar）
```

**构建与验证**：

```bash
mvn clean package

# 必须在 target/ 目录下运行（因为 lib/ 与 jar 同级）
cd target
java -jar simple-demo-1.0-SNAPSHOT.jar
```

---

### 3.3 maven-shade-plugin（lib 被编译为.class放进 fatjar）

**适用场景**：非 Spring 项目，需要处理类/资源冲突（如多个 jar 包含同名 SPI 文件），或需要对依赖包进行重命名（shade）。

**完整 pom.xml 最小示例**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>shade-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>8</maven.compiler.source>
        <maven.compiler.target>8</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.github.albfernandez</groupId>
            <artifactId>juniversalchardet</artifactId>
            <version>2.5.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.6.0</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <finalName>${project.artifactId}-${project.version}</finalName>
                            <!-- 不生成 dependency-reduced-pom.xml -->
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                            <transformers>
                                <!-- 指定主类 -->
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>org.example.Main</mainClass>
                                </transformer>
                                <!-- 合并 META-INF/services 文件（SPI 必需） -->
                                <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                            </transformers>
                            <!-- 排除签名文件，避免 SecurityException -->
                            <filters>
                                <filter>
                                    <artifact>*:*</artifact>
                                    <excludes>
                                        <exclude>META-INF/*.SF</exclude>
                                        <exclude>META-INF/*.DSA</exclude>
                                        <exclude>META-INF/*.RSA</exclude>
                                    </excludes>
                                </filter>
                            </filters>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

**构建与验证**：

```bash
mvn clean package

# 产物：target/shade-demo-1.0-SNAPSHOT.jar
java -jar target/shade-demo-1.0-SNAPSHOT.jar
```

---

### 3.4 spring-boot-maven-plugin

**适用场景**：Spring Boot 项目（首选且推荐的方式）。

**完整 pom.xml 最小示例**：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>springboot-demo</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <mainClass>com.example.MainApplication</mainClass>
                    <jvmArguments>
                        -Dfile.encoding=UTF-8
                    </jvmArguments>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>repackage</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

**`repackage` goal 的作用**：在 `package` 阶段之后，将原始 JAR 重命名为 `*.jar.original`，然后生成一个新的可执行 fat jar（内含 `BOOT-INF/classes/`、`BOOT-INF/lib/`、`org/springframework/boot/loader/` 等结构）。

**产物目录结构**：

```
springboot-demo-1.0-SNAPSHOT.jar
├── BOOT-INF/
│   ├── classes/          （项目编译后的 class + 资源文件）
│   └── lib/              （所有依赖 jar）
├── META-INF/
│   └── MANIFEST.MF       （Main-Class 指向 JarLauncher）
└── org/springframework/boot/loader/  （Spring Boot 自定义类加载器）
```

**构建与验证**：

```bash
mvn clean package

java -jar target/springboot-demo-1.0-SNAPSHOT.jar
```

---

### 3.5 maven-shade-plugin 用于 Spring Boot 项目（不推荐）

**为什么不推荐**：

1. Spring Boot 使用嵌套 JAR 结构（`BOOT-INF/lib/`），而 shade 插件会将所有 class 平铺，破坏 Spring Boot 的类加载机制。
2. 在 Spring 项目中使用 `ManifestResourceTransformer` 指定主类时，可能报错：
   ```
   Cannot find 'resource' in class org.apache.maven.plugins.shade.resource.ManifestResourceTransformer
   ```
   原因通常是 shade 插件版本与 Spring Boot 内部依赖冲突，或配置写法有误。
3. 即使打包成功，Spring MVC 的 `@Controller` 注解扫描、自动配置等机制可能失效。

**如必须使用 shade 打包 Spring 项目**，需注意：
- 不要使用 `ManifestResourceTransformer`，改为通过 `maven-jar-plugin` 单独设置 `Main-Class`。
- 手动排除签名文件（`*.SF`, `*.DSA`, `*.RSA`）。
- 确保 Spring 的 `spring.factories` / `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 等资源文件被正确合并。

**结论**：Spring Boot 项目请始终使用 `spring-boot-maven-plugin`。

---

### 3.6 IDEA 工件（Artifact）方式

**适用场景**：非 Maven 项目、快速原型、或不想编写 Maven 插件配置时。

**操作步骤**：

1. 打开 `File > Project Structure > Artifacts`
2. 点击 `+` 号，选择 `JAR > From modules with dependencies...`
3. 在弹出对话框中：
   - 选择主类（Main Class）
   - 选择依赖的存放方式：
     - **copy to the output directory and link via manifest**（推荐）：依赖 jar 复制到输出目录的 `lib/` 下，manifest 中通过 `Class-Path` 引用
     - **copy to a sub-directory ...**：类似效果
4. 点击 `OK` 完成配置
5. 通过 `Build > Build Artifacts...` 构建

**产物结构**（选择"copy to output directory"时）：

```
out/artifacts/
├── MyApp.jar
└── lib/
    ├── dependency-a.jar
    └── dependency-b.jar
```

**运行**：

```bash
cd out/artifacts
java -jar MyApp.jar
```

> **注意**：此方式要求 `lib/` 与主 JAR 在同一目录下。如果将 `lib/` 打进 JAR 内部，则 `java -jar` 无法加载嵌套的 jar。

---

## 四、常见问题与解决方案

### 4.1 maven-shade-plugin: "Cannot find 'resource' in class ManifestResourceTransformer"

**错误信息**：

```
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-shade-plugin:3.6.0:shade
Unable to parse configuration of mojo ... for parameter resource:
Cannot find 'resource' in class org.apache.maven.plugins.shade.resource.ManifestResourceTransformer
```

**根因**：

- 在 Spring Boot 项目中使用 shade 插件时，Spring Boot 的依赖可能引入了与 shade 插件不兼容的类。
- 或者 transformer 的 `implementation` 属性拼写错误 / XML 结构不正确。

**解决方案**：

1. **Spring 项目**：改用 `spring-boot-maven-plugin`，这是最可靠的方式。
2. **非 Spring 项目**：检查 shade 插件版本（推荐 3.5.x 或 3.6.0），确认 XML 配置结构正确：
   ```xml
   <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
       <mainClass>org.example.Main</mainClass>
   </transformer>
   ```
3. 如果问题仍然存在，尝试升级 shade 插件到最新稳定版本。

---

### 4.2 签名文件冲突导致 SecurityException

**错误信息**：

```
java.lang.SecurityException: Invalid signature file digest for Manifest main attributes
```

**根因**：

多个依赖 jar 包含各自的数字签名文件（`.SF`、`.DSA`、`.RSA`），合并后签名校验与实际内容不匹配。

**解决方案**：

在 shade 插件中排除签名文件：

```xml
<filters>
    <filter>
        <artifact>*:*</artifact>
        <excludes>
            <exclude>META-INF/*.SF</exclude>
            <exclude>META-INF/*.DSA</exclude>
            <exclude>META-INF/*.RSA</exclude>
        </excludes>
    </filter>
</filters>
```

对于 maven-assembly-plugin，通常不会遇到此问题（因为 class 平铺时签名文件不会被合并）。

---

### 4.3 SPI 服务文件覆盖（META-INF/services）

**问题描述**：

多个依赖 jar 中包含同名的 `META-INF/services/` 文件（如 `java.util.spi.LocaleServiceProvider`），合并时只有一个文件被保留，导致 SPI 机制失效。

**解决方案**：

使用 shade 插件的 `ServicesResourceTransformer`，它会自动合并所有同名 services 文件：

```xml
<transformers>
    <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
</transformers>
```

> 这是社区强烈推荐的最佳实践，尤其是当项目依赖使用了 Java SPI 机制时（如 JDBC 驱动、SLF4J 绑定等）。

---

### 4.4 自定义 assembly.xml 中依赖 jar 无法被加载

**问题描述**：

使用自定义 assembly.xml 将依赖 jar 放入 `lib/` 目录后，运行 `java -jar` 报 `ClassNotFoundException`。

**根因**：

JVM 的 `Class-Path` manifest 属性未配置，或配置的路径与实际目录结构不匹配。

**解决方案**：

1. **lib/ 在 JAR 外部**（推荐）：在 `pom.xml` 的 `<archive><manifestEntries>` 中配置 `Class-Path`：
   ```xml
   <manifestEntries>
       <Class-Path>lib/gson-2.10.1.jar lib/commons-lang3-3.12.0.jar</Class-Path>
   </manifestEntries>
   ```
   或使用 `maven-jar-plugin` 的 `addClasspath` 选项自动生成：
   ```xml
   <plugin>
       <groupId>org.apache.maven.plugins</groupId>
       <artifactId>maven-jar-plugin</artifactId>
       <configuration>
           <archive>
               <manifest>
                   <addClasspath>true</addClasspath>
                   <classpathPrefix>lib/</classpathPrefix>
                   <mainClass>org.example.Main</mainClass>
               </manifest>
           </archive>
       </configuration>
   </plugin>
   ```

2. **lib/ 在 JAR 内部**：标准 Java 不支持，需改用 Spring Boot 的 `LaunchedURLClassLoader` 或第三方库（如 OneJar）。

---

### 4.5 Spring Boot 项目使用 shade 导致 Controller 无法映射

**问题描述**：

使用 maven-shade-plugin 打包 Spring Boot 项目后，启动成功但所有 `@Controller` / `@RestController` 均返回 404。

**根因**：

shade 将所有 class 平铺后，Spring Boot 的自动配置和组件扫描机制依赖的元数据（如 `spring.factories`、`AutoConfiguration.imports`）未被正确合并。

**解决方案**：

1. **首选**：改用 `spring-boot-maven-plugin`。
2. **如必须用 shade**：
   - 添加 `SpringBootAppender` transformer（如果可用）。
   - 手动合并 `META-INF/spring.factories` 文件。
   - 使用 `AppendingTransformer` 合并 `spring.factories`：
     ```xml
     <transformer implementation="org.apache.maven.plugins.shade.resource.AppendingTransformer">
         <resource>META-INF/spring.factories</resource>
     </transformer>
     ```

---

## 五、方案选择决策树

```
是否 Spring Boot 项目？
├── 是 → 使用 spring-boot-maven-plugin（首选，无需犹豫）
│
└── 否 → 是否存在类/资源冲突需要重命名或合并？
          ├── 是 → 使用 maven-shade-plugin
          │         （配合 ServicesResourceTransformer + 签名排除）
          │
          └── 否 → 是否需要依赖以独立 jar 形式存放？
                    ├── 是 → maven-assembly-plugin + 自定义 assembly.xml
                    │         （注意 lib/ 必须在 JAR 外部 + 配置 Class-Path）
                    │
                    └── 否 → maven-assembly-plugin (jar-with-dependencies)
                              （最简单，一行 descriptorRef 搞定）
```

---

## 六、社区最佳实践与扩展

### 6.1 shade 插件推荐配置清单

```xml
<configuration>
    <!-- 1. 不生成 dependency-reduced-pom.xml -->
    <createDependencyReducedPom>false</createDependencyReducedPom>

    <transformers>
        <!-- 2. 指定主类 -->
        <transformer implementation="...ManifestResourceTransformer">
            <mainClass>org.example.Main</mainClass>
        </transformer>
        <!-- 3. 合并 SPI services 文件 -->
        <transformer implementation="...ServicesResourceTransformer"/>
    </transformers>

    <!-- 4. 排除签名文件 -->
    <filters>
        <filter>
            <artifact>*:*</artifact>
            <excludes>
                <exclude>META-INF/*.SF</exclude>
                <exclude>META-INF/*.DSA</exclude>
                <exclude>META-INF/*.RSA</exclude>
            </excludes>
        </filter>
    </filters>
</configuration>
```

### 6.2 Spring Boot 自定义 ClassLoader（layout=ZIP）

Spring Boot 支持通过 `layout=ZIP` 配置，使用自定义的 `PropertiesLauncher` 替代默认的 `JarLauncher`，从而允许在启动时通过 `LOADER_PATH` 环境变量动态指定外部依赖路径：

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <layout>ZIP</layout>
    </configuration>
</plugin>
```

启动时：

```bash
java -Dloader.path=/path/to/extra/lib -jar myapp.jar
```

### 6.3 jpackage — 原生安装包分发（JDK 14+）

对于桌面应用或需要分发给非技术用户的场景，可使用 `jpackage`（JDK 14+ 引入，JDK 16+ 正式稳定）生成平台原生安装包：

- Windows: `.msi` / `.exe`
- macOS: `.dmg` / `.pkg`
- Linux: `.deb` / `.rpm`

目标机器**无需安装 JRE**，因为 jpackage 会捆绑一个裁剪后的 JRE。

```bash
# 1. 使用 jlink 创建精简 JRE
jlink --module-path $JAVA_HOME/jmods \
      --add-modules java.base,java.desktop,java.sql \
      --output target/runtime

# 2. 使用 jpackage 生成安装包
jpackage --name MyApp \
         --app-version 1.0.0 \
         --vendor "MyCompany" \
         --runtime-image target/runtime \
         --main-jar myapp.jar \
         --main-class org.example.Main \
         --dest target/installer
```

> 注意：jpackage 必须在目标平台上运行（跨平台需分别在 Windows/macOS/Linux 上构建）。

### 6.4 多 Maven Profile 策略

可以在同一个 `pom.xml` 中通过 Maven Profile 定义不同的打包方式，按需激活：

```xml
<profiles>
    <profile>
        <id>fat-jar</id>
        <build>
            <plugins>
                <!-- shade 或 assembly 配置 -->
            </plugins>
        </build>
    </profile>
    <profile>
        <id>thin-jar</id>
        <build>
            <plugins>
                <!-- 仅打包项目本身，依赖外置 -->
            </plugins>
        </build>
    </profile>
</profiles>
```

激活方式：

```bash
mvn clean package -P fat-jar
mvn clean package -P thin-jar
```

---

END.
