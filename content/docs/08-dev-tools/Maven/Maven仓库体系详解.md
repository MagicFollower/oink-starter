---
title: Maven 仓库体系详解 —— 依赖从哪里来
weight: 5
description: jar 下载失败？SNAPSHOT 不更新？私服配置不生效？本文详解 Maven 的四层仓库体系（本地仓库、中央仓库、远程仓库、私服），依赖解析的完整流程，镜像（mirror）与仓库（repository）的区别，SNAPSHOT 更新策略，以及官方与社区最常遇到的仓库配置问题。
---

## 为什么需要仓库？

当你在 pom.xml 里声明了一个依赖，Maven 怎么找到这个 jar？它不可能凭空变出来——必须有一个地方存放这些构件。这个「存放构件的地方」就是**仓库**。

没有仓库的世界：每个开发者手动下载 jar，通过 U 盘或共享文件夹传递。版本混乱、来源不可追溯、换台电脑就找不到。

有了仓库：Maven 按 GAV 坐标自动去仓库查找、下载、缓存。你只需要声明「要什么」，不需要关心「从哪拿」。

> ### 💡 新人小结：仓库是什么？
>
> 把仓库想象成**建材市场的层级体系**：
> - **自家工具箱**（本地仓库 `~/.m2/repository`）：上次买剩的材料，下次直接用
> - **官方大卖场**（中央仓库 `repo.maven.apache.org`）：全球公开的构件库，什么都有
> - **公司专属仓库**（私服 Nexus/Artifactory）：公司内部共享，含商业组件
> - **代购点**（镜像 mirror）：官方大卖场在国内的代理，下载更快
>
> 一句话总结：**Maven 找依赖的顺序是：先看自家工具箱 → 再去公司仓库 → 最后去官方大卖场**。

**学习路线图**

```
四层仓库 → 解析流程 → 镜像配置 → SNAPSHOT → 私服搭建 → 常见问题
从哪找      怎么找的    加速下载    更新策略    企业级方案    怎么避坑
```

---

## 四层仓库

### 1. 本地仓库（Local Repository）

```
默认路径：
  Windows: C:\Users\<用户名>\.m2\repository
  Linux/macOS: ~/.m2/repository
```

本地仓库是 Maven 在**本机磁盘上的缓存目录**。每次从远程下载构件后，Maven 会在本地仓库存一份副本——下次再需要同一个构件时，直接从本地读取，不再走网络。

目录结构按 GAV 坐标组织：

```
~/.m2/repository/
└── org/
    └── springframework/
        └── spring-core/
            └── 5.3.20/
                ├── spring-core-5.3.20.jar
                ├── spring-core-5.3.20.pom
                ├── spring-core-5.3.20-sources.jar
                └── spring-core-5.3.20-javadoc.jar
```

**修改本地仓库路径**（在 `settings.xml` 中）：

```xml
<localRepository>D:\maven-repo</localRepository>
```

### 2. 中央仓库（Central Repository）

```
URL: https://repo.maven.apache.org/maven2
```

中央仓库是 Apache 维护的**全球公共仓库**——所有开源 Java 构件的官方发布地。Maven 默认配置了中央仓库，不需要你手动声明。

**注意**：2020 年 1 月起，中央仓库**不再支持 HTTP 协议**，必须使用 HTTPS。如果你的 `settings.xml` 或 `pom.xml` 里还配了 `http://repo1.maven.org/...`，会下载失败。

### 3. 远程仓库（Remote Repository）

在 pom.xml 中声明的自定义仓库——通常是公司内部的 Nexus/Artifactory，或第三方库的专属仓库：

```xml
<repositories>
    <repository>
        <id>company-nexus</id>
        <url>https://nexus.company.com/repository/maven-public/</url>
    </repository>
</repositories>
```

### 4. 私服（Private Repository）

私服是公司内部搭建的 Maven 仓库（常用 Nexus 或 Artifactory），作用：
- **代理缓存**：代理中央仓库，内网下载速度快
- **内部发布**：公司内部的 jar 发布到私服，其他项目可以依赖
- **权限控制**：控制谁能发布、谁能下载
- **安全扫描**：自动检测依赖的安全漏洞

---

## 依赖解析流程

当 Maven 需要一个构件时，按以下顺序查找：

```
① 本地仓库
   │
   ├─ 找到 → 直接使用 ✅
   │
   └─ 没找到 ↓
② settings.xml 中配置的镜像/仓库
   │
   ├─ 找到 → 下载到本地仓库 → 使用 ✅
   │
   └─ 没找到 ↓
③ pom.xml 中声明的远程仓库
   │
   ├─ 找到 → 下载到本地仓库 → 使用 ✅
   │
   └─ 没找到 ↓
④ 中央仓库（默认已配置）
   │
   ├─ 找到 → 下载到本地仓库 → 使用 ✅
   │
   └─ 没找到 → 构建失败 ❌
```

> ### 💡 新人小结：解析流程
>
> 就像**找一份文件**：
> 1. 先看自己桌上有没有（本地仓库）
> 2. 没有就去公司文件柜找（私服/远程仓库）
> 3. 还没有就去公共图书馆找（中央仓库）
> 4. 图书馆也没有——那就真找不到了

---

## 镜像（Mirror）vs 仓库（Repository）

这是最容易搞混的概念：

| 对比维度 | Repository（仓库） | Mirror（镜像） |
|---------|-------------------|---------------|
| 作用 | 存放构件的地方 | 某个仓库的「替身」 |
| 配置位置 | pom.xml 的 `<repositories>` | settings.xml 的 `<mirrors>` |
| 典型用途 | 声明额外的构件来源 | 加速/替换默认中央仓库 |
| 匹配规则 | 按 id 匹配 | 按 `<mirrorOf>` 匹配目标仓库 |

**镜像配置示例**（settings.xml）：

```xml
<mirrors>
    <mirror>
        <id>aliyun</id>
        <name>阿里云 Maven 镜像</name>
        <url>https://maven.aliyun.com/repository/public</url>
        <mirrorOf>central</mirrorOf>    <!-- 替代中央仓库 -->
    </mirror>
</mirrors>
```

**`<mirrorOf>` 的匹配规则**：

| 值 | 含义 |
|----|------|
| `central` | 只替代中央仓库 |
| `*` | 替代所有仓库 |
| `*,!company-nexus` | 替代所有仓库，但排除 company-nexus |
| `external:*` | 替代所有非本地（文件协议）的仓库 |

> 国内项目几乎都需要配阿里云或腾讯云镜像——中央仓库在国内访问慢，镜像可以大幅加速下载。

---

## SNAPSHOT 更新策略

SNAPSHOT 版本的构件**每次构建都可能不同**——Maven 需要定期检查远程是否有更新。

### 检查频率

| 场景 | 检查行为 |
|------|---------|
| 默认 | 每天检查一次（`updatePolicy: daily`） |
| `mvn -U` | 强制检查所有 SNAPSHOT 更新 |
| `updatePolicy: always` | 每次构建都检查 |
| `updatePolicy: never` | 从不检查（只用本地缓存） |
| `updatePolicy: interval:N` | 每 N 分钟检查一次 |

### 配置方式

```xml
<!-- 在 settings.xml 的仓库配置中 -->
<repository>
    <id>snapshots-repo</id>
    <url>https://nexus.company.com/repository/snapshots/</url>
    <snapshots>
        <enabled>true</enabled>
        <updatePolicy>always</updatePolicy>    <!-- 每次构建都检查更新 -->
    </snapshots>
</repository>
```

> ### 💡 新人小结：SNAPSHOT 更新
>
> SNAPSHOT 就像**连载漫画**——作者随时更新。Maven 默认每天去书店（仓库）看一次有没有新章节。如果你急着追更新，用 `mvn -U` 强制刷新。

### RELEASE 版本的更新策略

与 SNAPSHOT 不同，**RELEASE 版本一旦下载到本地，永远不会自动检查更新**：

| 版本类型 | 本地已存在时的行为 | 原因 |
|---------|------------------|------|
| `1.0.0-SNAPSHOT` | 按 `updatePolicy` 检查远程是否有更新 | SNAPSHOT 内容可能随时变化 |
| `1.0.0`（RELEASE） | 直接使用本地缓存，不检查远程 | RELEASE 内容不可变，同名版本不会改变 |

这意味着：如果远程仓库的 `1.0.0` 被人为替换了内容（不规范操作），Maven 不会感知——你需要手动删除本地缓存后重新下载。

> **最佳实践**：永远不要覆盖已发布的 RELEASE 版本。如果需要修改，发布一个新版本（如 `1.0.1`）。

---

## 本地仓库的元数据文件

打开本地仓库目录，你会看到 jar 之外还有一些辅助文件：

```
~/.m2/repository/com/example/some-lib/1.0.0/
├── some-lib-1.0.0.jar              ← 构件本体
├── some-lib-1.0.0.pom              ← POM 描述文件
├── some-lib-1.0.0.jar.sha1         ← SHA1 校验和
├── _remote.repositories            ← 记录该构件来自哪个仓库
└── maven-metadata-local.xml        ← 本地元数据（列出所有已下载版本）
```

**`_remote.repositories`** 记录了构件的来源仓库 id。如果该文件存在，Maven 认为这个构件是「从远程下载的合法副本」；如果被删除或损坏，Maven 可能会重新下载。

**`_maven.repositories`**（Maven 3.x 中文件名以 `_` 开头）控制 Maven 是否检查构件的完整性——**不要手动修改这些文件**。

---

## 手动安装 jar 到本地仓库

有些 jar 不在任何远程仓库中（比如公司内部的旧系统 jar），可以手动安装到本地仓库：

```bash
mvn install:install-file \
    -Dfile=/path/to/legacy-lib-1.0.jar \
    -DgroupId=com.company.legacy \
    -DartifactId=legacy-lib \
    -Dversion=1.0 \
    -Dpackaging=jar
```

执行后，Maven 会把 jar 复制到 `~/.m2/repository/com/company/legacy/legacy-lib/1.0/` 目录下，之后就可以在 pom.xml 中正常声明依赖：

```xml
<dependency>
    <groupId>com.company.legacy</groupId>
    <artifactId>legacy-lib</artifactId>
    <version>1.0</version>
</dependency>
```

> 这比 `system` scope 好得多——不绑定特定机器路径，项目可以在任何开发者的机器上构建（前提是大家都手动安装了该 jar）。

---

## 仓库认证与 deploy 配置

### 私服认证（servers）

如果私服需要用户名密码，在 `settings.xml` 中配置：

```xml
<servers>
    <server>
        <id>company-nexus</id>           <!-- 必须与仓库/镜像的 id 一致 -->
        <username>deployer</username>
        <password>secret123</password>   <!-- ⚠️ 明文密码，生产环境应加密 -->
    </server>
</servers>
```

**`<id>` 必须与仓库的 `<id>` 完全匹配**——Maven 通过 id 关联认证信息和仓库地址。如果 id 对不上，会报 401 Unauthorized。

### 发布到远程仓库（distributionManagement）

`mvn deploy` 把构件发布到哪里？在 pom.xml 中配置：

```xml
<distributionManagement>
    <repository>
        <id>company-releases</id>
        <url>https://nexus.company.com/repository/releases/</url>
    </repository>
    <snapshotRepository>
        <id>company-snapshots</id>
        <url>https://nexus.company.com/repository/snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

`distributionManagement` 中的 `<id>` 同样需要与 `settings.xml` 中 `<server>` 的 `<id>` 匹配。

---

## 国内常用镜像一览

| 镜像名称 | URL | 说明 |
|---------|-----|------|
| 阿里云（公共） | `https://maven.aliyun.com/repository/public` | 最常用，代理中央仓库 + JCenter |
| 阿里云 Spring | `https://maven.aliyun.com/repository/spring` | 代理 Spring 专属仓库 |
| 腾讯云 | `https://mirrors.cloud.tencent.com/nexus/repository/maven-public/` | 腾讯维护 |
| 华为云 | `https://repo.huaweicloud.com/repository/maven/` | 华为维护 |
| 清华大学 | `https://repo.maven.apache.org/maven2`（官方，非镜像） | 教育网访问可能更快 |

> **推荐配置**：阿里云公共镜像覆盖中央仓库，大多数 Spring Boot 项目的依赖都能命中。

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **jar 下载失败（连接超时）** | 网络问题或中央仓库在国内访问慢 | 配置阿里云镜像（见上文配置示例） |
| **jar 下载失败（401 Unauthorized）** | 私服需要认证但 settings.xml 没配 server | 在 settings.xml 的 `<servers>` 中配置用户名密码 |
| **SNAPSHOT 不更新** | Maven 默认每天检查一次，今天已经检查过了 | 使用 `mvn -U clean package` 强制更新 |
| **本地仓库损坏** | 下载中断导致 jar 不完整 | 删除本地仓库中对应目录，让 Maven 重新下载 |
| **HTTP 仓库被拒绝** | 2020 年起中央仓库不再支持 HTTP | 将所有仓库 URL 改为 HTTPS |
| **镜像配了但没生效** | `<mirrorOf>` 的值与仓库 id 不匹配 | 检查 mirrorOf 是否覆盖了目标仓库（用 `central` 或 `*`） |
| **离线环境构建失败** | 本地仓库没有缓存且无法联网 | 提前在有网环境执行 `mvn dependency:go-offline` 缓存所有依赖 |

---

## Q&A / 踩坑

**Q1：本地仓库占了很大磁盘空间，可以清理吗？**

可以。手动删除 `~/.m2/repository` 中不需要的目录，或使用 `mvn dependency:purge-local-repository` 清理当前项目不需要的依赖。但完全删除本地仓库意味着下次构建要重新下载所有依赖。

**Q2：阿里云镜像和中央仓库内容一样吗？**

阿里云镜像是中央仓库的**实时同步副本**，内容完全一致，只是服务器在国内，下载速度快。部分非常新的构件可能有几分钟的同步延迟。

**Q3：`mvn install` 和 `mvn deploy` 的区别？**

`install` 把构件安装到**本地仓库**（`~/.m2/repository`），供本机其他项目使用。`deploy` 把构件发布到**远程仓库**（私服），供团队所有人使用。

**Q4：为什么 pom.xml 里配的仓库和 settings.xml 里配的镜像会冲突？**

镜像的优先级高于仓库。如果镜像的 `<mirrorOf>` 匹配了某个仓库，Maven 会用镜像 URL 替代仓库 URL。确保 mirrorOf 的值正确覆盖了你想要替代的仓库。

---

## 要点总结

1. **四层仓库**：本地仓库（缓存）→ 私服/远程仓库（公司级）→ 中央仓库（全球公共）
2. **解析顺序**：本地 → 镜像/远程 → 中央仓库，找到即缓存到本地
3. **镜像加速**：国内项目必配阿里云/腾讯云镜像，`<mirrorOf>central</mirrorOf>` 替代中央仓库
4. **SNAPSHOT 更新**：默认每天检查一次；`mvn -U` 强制刷新；`updatePolicy` 控制检查频率
5. **mirror vs repository**：mirror 是仓库的替身（settings.xml），repository 是额外的构件来源（pom.xml）
6. **离线构建**：提前 `mvn dependency:go-offline` 缓存依赖，或配好本地仓库后使用 `-o` 模式

---

> ### 💡 新人小结：仓库体系学完了，记住这 3 点
>
> 1. **下载慢就配镜像**——阿里云一行配置解决 90% 的下载问题
> 2. **SNAPSHOT 不更新就加 `-U`**——`mvn clean package -U` 强制拉最新版
> 3. **本地仓库是缓存**——删了不心疼，下次构建会重新下载
>
> 接下来，翻开第六篇《Maven 命令与生命周期》，看看 Maven 的「施工流程」到底分几步。

---

## 附录：Nexus 私服搭建与 Maven 接入完整实战（从 0 到 1）

> 本节是一份完整的实操档案——从一台空白服务器开始，搭建 Nexus 私服，配置 Maven 客户端接入，实现团队内部依赖的发布与共享。全程可复现。

### 环境准备

| 项目 | 要求 |
|------|------|
| 服务器 | CentOS 7+ / Ubuntu 18.04+ / 任意 Linux，最低 2GB 内存 |
| JDK | Nexus 3.x 自带 JDK，无需单独安装 |
| Docker（推荐） | Docker 20.10+ / Docker Compose v2+ |
| Maven 客户端 | Maven 3.6+（本地开发机） |

### Step 1：Docker 部署 Nexus

```bash
# 创建数据持久化目录
mkdir -p /opt/nexus-data

# 启动 Nexus（后台运行）
docker run -d \
  --name nexus \
  --restart=always \
  -p 8081:8081 \
  -v /opt/nexus-data:/nexus-data \
  sonatype/nexus3:3.70.1
```

启动后等待 1-2 分钟（Nexus 首次启动较慢），检查状态：

```bash
# 查看日志，确认出现 "Started Sonatype Nexus"
docker logs -f nexus

# 检查端口监听
curl -s http://localhost:8081/service/rest/v1/status | head
# 输出 "ready" 表示启动成功
```

### Step 2：初始化 Nexus

**首次登录**：

```
浏览器打开：http://<服务器IP>:8081
点击右上角 "Sign in"
用户名：admin
密码：从容器内读取（见下方命令）
```

```bash
# 获取初始管理员密码
docker exec nexus cat /nexus-data/admin.password
# 输出类似：xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

登录后立即修改密码。Nexus 会引导你完成：设置新密码 → 开启匿名访问 → 完成向导。

### Step 3：认识 Nexus 默认仓库

Nexus 安装后自带以下仓库：

| 仓库名 | 类型 | 用途 |
|---------|------|------|
| maven-central | proxy | 代理中央仓库（缓存中央仓库的构件） |
| maven-public | group | 公共组（聚合 maven-central + 自定义 hosted） |
| maven-releases | hosted | 存放 RELEASE 版本（不可覆盖） |
| maven-snapshots | hosted | 存放 SNAPSHOT 版本（可覆盖） |

> **关键概念**：`maven-public` 是一个 **group 仓库**，它聚合了 `maven-central`（代理中央仓库）和 `maven-releases`（内部正式版）。Maven 客户端只需指向 `maven-public` 一个地址，就能同时下载开源依赖和内部组件。

### Step 4：创建自定义 Hosted 仓库（可选）

如果公司需要隔离不同团队的构件，可以创建额外的 hosted 仓库：

```
Nexus 管理界面 → Repository → Repositories → Create repository
类型：hosted
名称：team-backend-releases
Format：maven2
Version policy：Release（不允许 SNAPSHOT）
```

### Step 5：创建部署用户

在 Nexus 中创建一个专门用于 `mvn deploy` 的用户：

```
Nexus 管理界面 → Security → Users → Create local user
用户名：deployer
密码：your-secure-password
角色：nx-deployment（内置的部署角色）
```

### Step 6：配置 Maven 客户端（settings.xml）

在开发机的 `~/.m2/settings.xml` 中添加以下配置：

```xml
<settings>
    <!-- 私服认证 -->
    <servers>
        <server>
            <id>nexus-releases</id>
            <username>deployer</username>
            <password>your-secure-password</password>
        </server>
        <server>
            <id>nexus-snapshots</id>
            <username>deployer</username>
            <password>your-secure-password</password>
        </server>
    </servers>

    <!-- 镜像配置：用私服代理所有仓库 -->
    <mirrors>
        <mirror>
            <id>nexus-public</id>
            <name>Nexus 公共组仓库（代理中央仓库 + 内部仓库）</name>
            <url>http://<服务器IP>:8081/repository/maven-public/</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>
</settings>
```

> **`<server>` 的 id 必须与后续 `<distributionManagement>` 中的 `<id>` 一致**——Maven 通过 id 关联认证信息和仓库地址。

### Step 7：配置项目 pom.xml（发布到私服）

在项目的 `pom.xml` 中添加发布配置：

```xml
<distributionManagement>
    <!-- RELEASE 版本发布到这里 -->
    <repository>
        <id>nexus-releases</id>
        <url>http://<服务器IP>:8081/repository/maven-releases/</url>
    </repository>
    <!-- SNAPSHOT 版本发布到这里 -->
    <snapshotRepository>
        <id>nexus-snapshots</id>
        <url>http://<服务器IP>:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
```

### Step 8：发布与验证

**发布 SNAPSHOT**：

```bash
# 确保 version 带 -SNAPSHOT 后缀，如 1.0.0-SNAPSHOT
mvn clean deploy -DskipTests

# 输出中应看到：
# [INFO] Uploading to nexus-snapshots: http://.../maven-snapshots/...
# [INFO] Uploaded: xxx KB
```

**发布 RELEASE**：

```bash
# 去掉 -SNAPSHOT 后缀，如 1.0.0
mvn clean deploy -DskipTests

# 输出中应看到：
# [INFO] Uploading to nexus-releases: http://.../maven-releases/...
```

**在 Nexus 界面验证**：

```
Nexus 管理界面 → Browse → 选择对应仓库
→ 找到 com/your-group/your-artifact/版本号/
→ 确认 jar、pom、sha1 文件均已上传
```

**其他开发者拉取**：

配置了同样的 `settings.xml` 镜像后，其他开发者只需在 pom.xml 中声明依赖：

```xml
<dependency>
    <groupId>com.your-company</groupId>
    <artifactId>your-artifact</artifactId>
    <version>1.0.0</version>
</dependency>
```

执行 `mvn compile`，Maven 会自动从 Nexus 私服下载——因为 `maven-public` 组仓库包含了 `maven-releases`。

### Step 9：生产环境加固清单

| 加固项 | 操作 |
|---------|------|
| **HTTPS** | 在 Nexus 前加 Nginx 反向代理，配置 SSL 证书；或将 Nexus 端口映射到 443 |
| **密码加密** | 用 `mvn --encrypt-password` 加密 settings.xml 中的密码（参见第七篇） |
| **备份** | 定期备份 `/opt/nexus-data` 目录（包含所有构件和配置） |
| **清理策略** | Nexus → Repositories → 对应仓库 → Clean up policies，设置 SNAPSHOT 保留天数 |
| **LDAP/SSO** | 企业环境可对接 LDAP/Active Directory 统一认证 |
| **匿名访问** | 生产环境建议关闭匿名访问，强制认证后下载 |

### 完整流程速查

```
① Docker 启动 Nexus          → docker run -d -p 8081:8081 ...
② 浏览器登录并修改初始密码    → http://IP:8081
③ settings.xml 配 servers    → 认证信息（id 必须对应）
④ settings.xml 配 mirrors    → 下载走私服代理
⑤ pom.xml 配 distributionManagement → 发布地址
⑥ mvn deploy                 → 发布到私服
⑦ 其他开发者 mvn compile     → 自动从私服拉取
```
