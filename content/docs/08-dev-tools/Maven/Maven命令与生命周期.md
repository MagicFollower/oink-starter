---
title: Maven 命令与生命周期 —— 构建流程的每个阶段
weight: 6
description: 命令太多记不住？生命周期不理解导致构建行为不符合预期？本文详解 Maven 的三套生命周期（clean / default / site），default 生命周期的完整 23 个阶段，常用命令速查表，-DskipTests 与 -Dmaven.test.skip 的区别，-P / -U / -T / -o / -pl / -am 等参数详解，以及官方与社区最常遇到的命令问题。
---

## 为什么需要理解生命周期？

你可能已经用过 `mvn clean package`、`mvn install`——但你知道 `clean` 到底删了什么？`package` 之前经历了哪些步骤？`install` 和 `deploy` 的区别到底在哪？

不理解生命周期的后果：
- 以为 `mvn clean` 会删除所有临时文件，结果 `generated-sources` 目录还在
- 以为 `mvn test` 会打包，结果 target 目录里什么都没有
- 以为 `-DskipTests` 跳过了所有测试相关的工作，结果测试代码还是被编译了

> ### 💡 新人小结：生命周期是什么？
>
> 把 Maven 的生命周期想象成**施工流程**：
> 1. **清理场地**（clean）：拆掉旧建筑（删除 target 目录）
> 2. **备料**（validate → generate-sources）：检查图纸、准备材料
> 3. **施工**（compile）：按图纸加工主代码
> 4. **质检**（test）：测试员检验产品质量
> 5. **打包**（package）：装进箱子（jar / war）
> 6. **入库**（install）：放进自家仓库
> 7. **发货**（deploy）：发到远程仓库供他人使用
>
> 每个阶段都有固定任务，跳阶段 = 跳工序 = 出问题。

**学习路线图**

```
三套生命周期 → default 完整阶段 → 常用命令速查 → 参数详解 → 跳过测试 → 常见问题
clean/default/site   23 个阶段      日常够用      进阶控制    三种方式      怎么避坑
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| Lifecycle | — | 生命周期：Maven 构建的完整阶段序列 | 施工流程的总称 |
| Phase | — | 阶段：生命周期中的每一步 | 施工流程的一个环节 |
| Goal | — | 目标：插件中的一个具体任务 | 一个工人干的活 |
| Plugin | — | 插件：执行具体构建任务的工具 | 施工工具 |
| Binding | — | 绑定：phase 和 goal 的对应关系 | 哪个阶段用哪个工具 |

---

## 三套生命周期

Maven 有三套**相互独立**的生命周期，每套负责不同的构建方面：

| 生命周期 | 包含阶段 | 职责 |
|---------|---------|------|
| **clean** | pre-clean → clean → post-clean | 清理上一次构建的产物 |
| **default** | validate → ... → deploy（23 个阶段） | 核心构建流程：编译、测试、打包、部署 |
| **site** | pre-site → site → post-site → site-deploy | 生成项目文档站点 |

> 调用任何一套生命周期中的某个阶段时，该阶段之前的所有阶段都会**自动按顺序执行**。例如执行 `mvn package`，Maven 会先跑完 validate → compile → test 等所有前置阶段。

---

## Clean 生命周期

最简单的生命周期，只有 3 个阶段：

| 阶段 | 绑定的插件目标 | 作用 |
|------|---------------|------|
| pre-clean | — | 清理前的准备工作（通常不用） |
| clean | maven-clean-plugin:clean | 删除 `target/` 目录及其内容 |
| post-clean | — | 清理后的收尾工作（通常不用） |

```bash
mvn clean            # 只执行 clean 生命周期
mvn clean package    # 先清理，再执行 default 生命周期的 package
```

> **注意**：`mvn clean` **只删除 `target/` 目录**——不会删除 `.class` 缓存以外的任何文件。如果你期望它清理 `node_modules/`、`.idea/` 之类的目录，需要额外配置 maven-clean-plugin。

---

## Default 生命周期：完整 23 个阶段

这是最核心的生命周期。完整阶段列表如下：

| # | 阶段名 | 作用 | 典型绑定插件 |
|---|--------|------|-------------|
| 1 | validate | 验证 pom.xml 是否正确、必要元素是否齐全 | — |
| 2 | initialize | 初始化构建属性、设置 `${maven.build.timestamp}` 等 | — |
| 3 | generate-sources | 生成主代码的源代码（如 ANTLR、protobuf） | antlr3-maven-plugin 等 |
| 4 | process-sources | 处理生成的源代码（如过滤、转换） | — |
| 5 | generate-resources | 生成主资源文件 | — |
| 6 | process-resources | **复制并过滤主资源**到 `target/classes` | maven-resources-plugin:resources |
| 7 | compile | **编译主源代码**到 `target/classes` | maven-compiler-plugin:compile |
| 8 | process-classes | 对编译后的 class 文件做后处理（如字节码增强） | — |
| 9 | generate-test-sources | 生成测试代码的源代码 | — |
| 10 | process-test-sources | 处理生成的测试源代码 | — |
| 11 | generate-test-resources | 生成测试资源文件 | — |
| 12 | process-test-resources | **复制并过滤测试资源**到 `target/test-classes` | maven-resources-plugin:testResources |
| 13 | test-compile | **编译测试代码**到 `target/test-classes` | maven-compiler-plugin:testCompile |
| 14 | process-test-classes | 对编译后的测试 class 做后处理 | — |
| 15 | test | **执行单元测试** | maven-surefire-plugin:test |
| 16 | prepare-package | 打包前的准备工作（如生成 MANIFEST.MF） | — |
| 17 | package | **将编译产物打包**为 jar / war / ear 等 | maven-jar-plugin / maven-war-plugin |
| 18 | pre-integration-test | 集成测试前的准备（如启动容器） | — |
| 19 | integration-test | 执行集成测试 | maven-failsafe-plugin |
| 20 | post-integration-test | 集成测试后的清理（如停止容器） | — |
| 21 | verify | 验证打包结果是否合法（如运行检查） | maven-verifier-plugin 等 |
| 22 | install | **安装到本地仓库**（`~/.m2/repository`） | maven-install-plugin:install |
| 23 | deploy | **发布到远程仓库**（私服） | maven-deploy-plugin:deploy |

> ### 💡 新人小结：23 个阶段怎么记？
>
> 不需要记住全部 23 个！日常开发只用到其中几个关键节点：
> ```
> 编译 → 测试 → 打包 → 安装 → 发布
> compile → test → package → install → deploy
> ```
> 其他阶段大多是自动化插件的钩子，你几乎不需要手动干预。

### 常用命令对应的阶段

| 命令 | 实际执行的阶段范围 | 说明 |
|------|-------------------|------|
| `mvn validate` | 1 | 只验证 pom.xml |
| `mvn compile` | 1-7 | 到编译完成 |
| `mvn test` | 1-15 | 到测试完成 |
| `mvn package` | 1-17 | 到打包完成 |
| `mvn verify` | 1-21 | 到验证完成 |
| `mvn install` | 1-22 | 到安装本地仓库 |
| `mvn deploy` | 1-23 | 完整流程，发布到远程 |

---

## Site 生命周期

用于生成项目文档站点（基于 `src/site/` 目录下的内容）：

| 阶段 | 作用 |
|------|------|
| pre-site | 生成站点前的准备 |
| site | 生成站点文件 |
| post-site | 生成后的收尾 |
| site-deploy | 将站点部署到远程服务器 |

```bash
mvn site            # 生成本地站点到 target/site/
mvn site-deploy     # 将站点发布到配置的服务器
```

> 大多数项目不常用 site 生命周期——JavaDoc 和 README 通常就够用了。

---

## 常用命令速查表

| 命令 | 用途 | 典型场景 |
|------|------|---------|
| `mvn clean` | 删除 target/ | 构建前清理旧产物 |
| `mvn compile` | 编译主代码 | 快速检查编译错误 |
| `mvn test` | 编译 + 运行测试 | 提交前验证 |
| `mvn package` | 编译 + 测试 + 打包 | 生成 jar/war |
| `mvn install` | 编译 + 测试 + 打包 + 安装到本地仓库 | 本机调试多模块依赖 |
| `mvn deploy` | 完整流程 + 发布到远程仓库 | CI/CD 发布 |
| `mvn site` | 生成项目文档站点 | 生成 API 文档 |
| `mvn validate` | 只验证 pom.xml | 排查 pom.xml 配置错误 |
| `mvn clean compile -X` | 编译并输出调试日志 | 排查构建问题 |

---

## 命令参数详解

### 常用参数一览

| 参数 | 含义 | 示例 |
|------|------|------|
| `-DskipTests` | 跳过测试**执行**（但编译测试代码） | `mvn package -DskipTests` |
| `-Dmaven.test.skip=true` | 跳过测试编译和执行 | `mvn package -Dmaven.test.skip=true` |
| `-P <profile>` | 激活指定 profile | `mvn package -P prod` |
| `-U` | 强制检查 SNAPSHOT 更新 | `mvn clean install -U` |
| `-e` | 显示错误堆栈 | `mvn compile -e` |
| `-X` | 输出调试日志（极详细） | `mvn compile -X` |
| `-o` | 离线模式（不走网络） | `mvn compile -o` |
| `-pl <module>` | 只构建指定模块 | `mvn install -pl user-service` |
| `-am` | 同时构建依赖的模块 | `mvn install -pl user-service -am` |
| `-T <n>` | 并行构建（n 个线程） | `mvn install -T 4` |
| `-q` | 安静模式（只输出错误） | `mvn package -q` |
| `-B` | 批处理模式（不显示进度条，CI 推荐） | `mvn install -B` |
| `-f <file>` | 指定 pom.xml 路径 | `mvn compile -f sub-module/pom.xml` |

### -DskipTests vs -Dmaven.test.skip

这是最容易搞混的参数：

| 参数 | 编译测试代码 | 执行测试 | 说明 |
|------|------------|---------|------|
| 不传（默认） | ✅ | ✅ | 正常编译和运行测试 |
| `-DskipTests` | ✅ | ❌ | 测试代码编译了但不运行——适合测试代码有编译错误但不影响主代码的场景 |
| `-Dmaven.test.skip=true` | ❌ | ❌ | 完全不碰测试——编译更快，但如果测试代码有编译错误，`mvn install` 也不会发现 |

> **推荐**：日常开发用 `-DskipTests`（保证测试代码至少能编译通过），CI 环境不要用任何跳过参数。

### -pl 和 -am 的配合

多模块项目中，这两个参数经常一起使用：

```bash
# 只构建 user-service 模块
mvn install -pl user-service

# 构建 user-service 模块，以及它依赖的其他模块
mvn install -pl user-service -am
```

```
my-project/
├── common/            ← user-service 依赖它
├── user-service/      ← 要构建的目标
└── order-service/     ← 不参与构建
```

`-pl user-service -am`：只构建 common + user-service，跳过 order-service。

### 并行构建（-T）

多模块项目可以用多线程加速构建：

```bash
# 使用 4 个线程并行构建
mvn install -T 4

# 每个 CPU 核心 1 个线程
mvn install -T 1C

# 指定每个线程的内存上限（Maven 3.9+）
mvn install -T 2C --builder smart
```

> **注意**：并行构建可能导致日志交错。配合 `-B`（批处理模式）可以减少进度条干扰。

---

## 插件绑定：Phase 与 Goal 的关系

Maven 的核心设计是**生命周期驱动**——每个 phase 预绑定了特定 packaging 对应的插件 goal：

| Packaging | 关键绑定 |
|-----------|--------|
| jar | compile → maven-compiler-plugin:compile；package → maven-jar-plugin:jar；test → maven-surefire-plugin:test |
| war | compile → maven-compiler-plugin:compile；package → maven-war-plugin:war；test → maven-surefire-plugin:test |
| pom | 几乎不绑定任何插件（只用于聚合/父 POM） |

查看当前项目的所有绑定：

```bash
mvn help:effective-pom
```

这会输出合并了父 POM、插件默认配置后的完整 pom.xml——可以看到每个 phase 绑定了哪些 goal。

### 常用插件 Goal 速查

| 插件 | 常用 Goal | 作用 |
|------|----------|------|
| maven-compiler-plugin | compile / testCompile | 编译主代码 / 测试代码 |
| maven-surefire-plugin | test | 运行单元测试 |
| maven-failsafe-plugin | integration-test / verify | 运行集成测试 |
| maven-jar-plugin | jar | 打包为 jar |
| maven-war-plugin | war | 打包为 war |
| maven-resources-plugin | resources / testResources | 复制并过滤资源文件 |
| maven-install-plugin | install | 安装到本地仓库 |
| maven-deploy-plugin | deploy | 发布到远程仓库 |
| maven-clean-plugin | clean | 删除 target 目录 |
| maven-dependency-plugin | tree / analyze / copy | 分析、复制依赖 |

---

## 查看有效配置

Maven 的「有效配置」是多层合并后的结果：超级 POM → 父 POM → 当前 POM → 命令行参数。

| 命令 | 用途 |
|------|------|
| `mvn help:effective-pom` | 查看合并后的完整 pom.xml |
| `mvn help:effective-settings` | 查看合并后的 settings.xml |
| `mvn help:describe -Dplugin=compiler` | 查看某个插件的所有参数和默认值 |
| `mvn help:describe -Dplugin=compiler -Ddetail` | 查看详细信息（含参数类型和默认值） |

> **调试技巧**：遇到配置不生效时，先跑 `mvn help:effective-pom`，看合并后的实际值是否与你预期一致。如果 effective-pom 里的值是对的但行为还是不对，检查是否是插件版本问题——不同版本的插件参数可能不同。

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **`mvn clean` 后 target 还在** | 只删除 `target/` 目录本身，不删其他目录 | 这是正常行为；如需清理其他目录，配置 maven-clean-plugin 的 `<filesets>` |
| **`-DskipTests` 后测试代码编译报错** | `-DskipTests` 只跳过执行，不跳过编译 | 改用 `-Dmaven.test.skip=true` 完全跳过测试 |
| **`mvn install` 很慢** | 每次都跑全量测试 | 开发阶段用 `mvn install -DskipTests`；CI 用完整流程 |
| **多模块构建顺序不对** | Maven 按依赖关系自动排序，循环依赖会导致失败 | 检查模块间依赖是否有环（`mvn dependency:tree`） |
| **并行构建（-T）日志混乱** | 多线程输出交错 | 加 `-B`（批处理模式）；或不用 `-T` |
| **`mvn deploy` 报 401** | 私服认证失败 | 检查 `settings.xml` 的 `<server>` 的 `<id>` 是否与 `distributionManagement` 匹配 |
| **`mvn compile` 报「找不到符号」** | 依赖没下载或版本错误 | `mvn clean compile -U` 强制更新依赖 |
| **`mvn test` 没有运行任何测试** | surefire 默认只找 `*Test.java` 和 `Test*.java` | 检查测试类命名是否符合约定，或配置 surefire 的 `<includes>` |

---

## Q&A / 踩坑

**Q1：`mvn clean package` 和 `mvn package` 的区别？**

`mvn package` 不会先清理 target 目录——如果上次构建残留了旧文件，可能混入本次构建。`mvn clean package` 先删 target 再打包，更干净。**推荐总是加 `clean`**。

**Q2：`mvn install` 和 `mvn deploy` 的区别？**

`install` 把构件安装到**本地仓库**（`~/.m2/repository`），只有本机能用。`deploy` 把构件发布到**远程仓库**（私服），团队所有人都能下载。`deploy` 包含 `install` 的所有步骤。

**Q3：`mvn -o` 离线模式有什么用？**

断网环境下，Maven 无法从远程仓库下载依赖。`-o` 告诉 Maven「不要尝试联网」，只从本地仓库取构件。如果本地仓库已经缓存了所有需要的依赖，离线模式可以正常构建——且速度更快。

**Q4：`-T 1C` 是什么意思？**

`1C` 表示「每个 CPU 核心 1 个线程」。如果你的电脑是 8 核，`-T 1C` 会启动 8 个构建线程。比固定数字更灵活——在不同机器上自动适配。

**Q5：为什么 `mvn test` 找不到我的测试类？**

Surefire 插件默认按命名约定查找测试类：`*Test.java`、`Test*.java`、`*Tests.java`、`*TestCase.java`。如果你的测试类不遵循这些命名（比如 `MySpec.java`），需要在 surefire 配置中显式指定 `<includes>`。

---

## 要点总结

1. **三套生命周期**：clean（清理）、default（核心构建，23 阶段）、site（文档站点）
2. **阶段递进执行**：执行某阶段时，之前的所有阶段自动先执行（`mvn package` 会先 compile、test）
3. **日常五大命令**：compile（编译）→ test（测试）→ package（打包）→ install（安装本地）→ deploy（发布远程）
4. **跳过测试**：`-DskipTests` 跳过执行但编译；`-Dmaven.test.skip=true` 全跳过
5. **多模块利器**：`-pl` 指定模块 + `-am` 连带依赖模块；`-T` 并行加速
6. **调试构建**：`-e` 显示错误堆栈；`-X` 输出全部调试日志；`-o` 离线模式
7. **CI 推荐**：`mvn clean deploy -B -U`（清理 + 发布 + 批处理 + 强制更新 SNAPSHOT）

---

> ### 💡 新人小结：命令与生命周期学完了，记住这 3 点
>
> 1. **日常只用 5 个命令**：`clean`、`compile`、`test`、`package`、`install`——其他的按需学
> 2. **`mvn clean package` 是万金油**——加 `clean` 避免旧文件干扰
> 3. **出了问题加 `-X`**——调试日志会告诉你 Maven 在每一步做了什么
>
> 接下来，翻开第七篇《Maven 配置与 settings 详解》，看看 Maven 的「个人偏好设置」到底怎么配。
