---
title: Maven 配置与 settings 详解 —— 采购代理的个人偏好
weight: 7
description: settings.xml 配置不生效？多环境切换困难？密码明文不安全？本文详解 settings.xml 的两级位置与合并规则，核心配置项（localRepository / servers / mirrors / profiles / activeProfiles），profile 的四种激活方式，密码加密（mvn --encrypt-password），代理配置（proxies），环境变量与内置属性，以及官方与社区最常遇到的配置问题。
---

## 为什么需要 settings.xml？

pom.xml 描述的是「项目」——这个项目需要什么依赖、怎么构建。但有些配置不属于任何项目，而是属于**运行 Maven 的人或机器**：

- 本地仓库放在哪个磁盘？
- 公司私服的地址和账号？
- 国内下载慢，用哪个镜像加速？
- 开发/测试/生产环境用不同的配置？

这些「跟项目无关、跟人/机器有关」的设置，放在 `settings.xml` 里。

> ### 💡 新人小结：settings.xml 是什么？
>
> 把 Maven 想象成**采购代理**：
> - `pom.xml` 是项目的采购清单——「这个项目需要什么材料」
> - `settings.xml` 是采购代理的**个人偏好**——「我喜欢去哪个市场买、仓库放哪、账号密码是什么」
>
> 换一个人（或换一台机器），项目不变，但代理的偏好可能不同。

**学习路线图**

```
两级位置 → 合并规则 → 核心配置项 → profile 详解 → 密码加密 → 代理配置 → 常见问题
在哪放      怎么合并    逐项拆解      多环境方案    安全存储    网络代理     怎么避坑
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| settings.xml | — | Maven 的用户/全局配置文件 | 采购代理的个人偏好设置 |
| Profile | — | 一组条件激活的配置变体 | 不同环境（开发/测试/生产）的切换方案 |
| Mirror | — | 仓库的替身，用于加速下载 | 代购点 |
| Server | — | 远程仓库的认证信息（用户名/密码） | 仓库的会员卡 |
| Proxy | — | 网络代理配置 | 公司内网访问外网的通道 |

---

## settings.xml 的两级位置

Maven 在两个地方查找 `settings.xml`：

| 级别 | 路径 | 作用范围 |
|------|------|---------|
| **全局（Global）** | `${maven.home}/conf/settings.xml`（Maven 安装目录下的 conf/） | 影响这台机器上的**所有用户** |
| **用户（User）** | `${user.home}/.m2/settings.xml`（用户主目录下的 .m2/） | 只影响**当前用户** |

```
全局：  /opt/apache-maven-3.9.16/conf/settings.xml
用户：  ~/.m2/settings.xml
```

> 如果两个文件都存在，Maven 会**合并**它们——用户级配置优先。

---

## 合并规则

当全局和用户级 settings.xml 同时存在时，合并规则如下：

| 配置项 | 合并行为 |
|--------|---------|
| `<localRepository>` | 用户级覆盖全局 |
| `<servers>` | **合并**（两个文件的 server 列表叠加）；id 相同时，用户级覆盖全局 |
| `<mirrors>` | **合并**；id 相同时，用户级覆盖全局 |
| `<proxies>` | **合并**；id 相同时，用户级覆盖全局 |
| `<profiles>` | **合并**；id 相同时，用户级覆盖全局 |
| `<activeProfiles>` | **合并**（两边的激活列表叠加） |

> **关键**：`<servers>`、`<mirrors>`、`<profiles>` 是按 `<id>` 匹配合并的——id 相同的条目，用户级覆盖全局；id 不同的条目，两边都保留。

### 查看合并后的结果

```bash
mvn help:effective-settings
```

这会输出合并后的完整 settings——配置不生效时，先跑这个命令看实际值。

---

## 核心配置项详解

一个典型的 `settings.xml` 长这样：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/settings/1.2.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/settings/1.2.0
                              https://maven.apache.org/xsd/settings-1.2.0.xsd">

    <!-- 本地仓库路径 -->
    <localRepository>D:\maven-repo</localRepository>

    <!-- 离线模式 -->
    <offline>false</offline>

    <!-- 交互模式（CI 环境建议关闭） -->
    <interactiveMode>true</interactiveMode>

    <!-- 远程仓库认证 -->
    <servers>...</servers>

    <!-- 镜像配置 -->
    <mirrors>...</mirrors>

    <!-- 网络代理 -->
    <proxies>...</proxies>

    <!-- 配置变体 -->
    <profiles>...</profiles>

    <!-- 激活的 profile -->
    <activeProfiles>...</activeProfiles>

</settings>
```

### localRepository

```xml
<localRepository>D:\maven-repo</localRepository>
```

默认路径是 `~/.m2/repository`。如果 C 盘空间紧张，可以改到其他磁盘。修改后需要手动把旧仓库内容迁移到新路径，否则 Maven 会重新下载所有依赖。

### offline

```xml
<offline>true</offline>
```

设为 `true` 后，Maven 不会访问任何远程仓库——只从本地仓库取构件。适合断网环境。等价于命令行加 `-o`。

### interactiveMode

```xml
<interactiveMode>false</interactiveMode>
```

设为 `false` 后，Maven 不会显示交互式提示（如进度条）。CI/CD 环境建议关闭。

---

## servers：远程仓库认证

当远程仓库需要用户名密码时，在 `<servers>` 中配置：

```xml
<servers>
    <server>
        <id>company-nexus</id>              <!-- 必须与仓库/镜像的 id 一致 -->
        <username>deployer</username>
        <password>secret123</password>
        <!-- 可选：私钥认证 -->
        <privateKey>${user.home}/.ssh/id_rsa</privateKey>
        <passphrase>key-passphrase</passphrase>
    </server>
</servers>
```

**`<id>` 必须与仓库的 `<id>` 完全匹配**——Maven 通过 id 关联认证信息和仓库地址。

> ⚠️ **密码明文存储不安全**——任何能读取 settings.xml 的人都能看到密码。生产环境应使用密码加密。

---

## mirrors：镜像配置

镜像是仓库的「替身」——Maven 访问目标仓库时，实际走镜像的 URL：

```xml
<mirrors>
    <mirror>
        <id>aliyun</id>
        <name>阿里云 Maven 镜像</name>
        <url>https://maven.aliyun.com/repository/public</url>
        <mirrorOf>central</mirrorOf>
    </mirror>
</mirrors>
```

`<mirrorOf>` 的匹配规则（详见第五篇《Maven 仓库体系详解》）：

| 值 | 含义 |
|----|------|
| `central` | 只替代中央仓库 |
| `*` | 替代所有仓库 |
| `*,!company-nexus` | 替代所有仓库，排除 company-nexus |
| `external:*` | 替代所有非本地（文件协议）的仓库 |

---

## profiles：多环境配置变体

Profile 是 settings.xml 最强大的功能——它允许你定义**多套配置**，按条件激活不同的一套。

### Profile 的结构

```xml
<profiles>
    <profile>
        <id>dev</id>
        <properties>
            <env>development</env>
            <db.url>jdbc:mysql://localhost:3306/dev_db</db.url>
        </properties>
        <repositories>
            <repository>
                <id>dev-nexus</id>
                <url>https://dev-nexus.company.com/repository/maven-public/</url>
            </repository>
        </repositories>
    </profile>

    <profile>
        <id>prod</id>
        <properties>
            <env>production</env>
            <db.url>jdbc:mysql://prod-db:3306/prod_db</db.url>
        </properties>
    </profile>
</profiles>
```

### 四种激活方式

Profile 可以通过以下方式激活：

**方式一：命令行 `-P`**

```bash
mvn package -P prod          # 激活 id 为 prod 的 profile
mvn package -P dev,prod      # 同时激活多个
```

**方式二：`<activeByDefault>`**

```xml
<profile>
    <id>dev</id>
    <activation>
        <activeByDefault>true</activeByDefault>    <!-- 默认激活 -->
    </activation>
</profile>
```

> 当没有任何 profile 被显式激活时，`activeByDefault=true` 的 profile 自动激活。一旦用 `-P` 显式激活了其他 profile，`activeByDefault` 就失效了。

**方式三：JDK 版本匹配**

```xml
<profile>
    <id>jdk17-profile</id>
    <activation>
        <jdk>[17,)</jdk>       <!-- JDK 17 及以上时自动激活 -->
    </activation>
</profile>
```

**方式四：属性/环境变量匹配**

```xml
<profile>
    <id>os-windows</id>
    <activation>
        <os>
            <family>windows</family>
        </os>
    </activation>
</profile>

<profile>
    <id>custom-env</id>
    <activation>
        <property>
            <name>custom.flag</name>
            <value>activate</value>
        </property>
    </activation>
</profile>
```

属性匹配可以通过命令行传值触发：

```bash
mvn package -Dcustom.flag=activate
```

### 默认激活的 profile 列表

除了 profile 内部的 `<activation>`，还可以在 `<activeProfiles>` 中集中列出默认激活的 profile：

```xml
<activeProfiles>
    <activeProfile>dev</activeProfile>
</activeProfiles>
```

效果与 `<activeByDefault>true</activeByDefault>` 类似，但更集中、更清晰。

> ### 💡 新人小结：Profile 是什么？
>
> Profile 就像**施工方案的不同变体**：
> - 开发环境（dev）：连本地数据库、用快照仓库
> - 测试环境（test）：连测试数据库、用测试仓库
> - 生产环境（prod）：连生产数据库、用正式仓库
>
> 同一份代码，切换 profile 就能适配不同环境——不需要改 pom.xml。

---

## 密码加密

settings.xml 中的密码默认是明文——任何能读取文件的人都能看到。Maven 提供了密码加密功能：

### 步骤一：生成主密码

```bash
mvn --encrypt-password
# 输入明文密码后，输出加密结果，如：
# {jSMOPuzN2cFb...加密字符串...}
```

### 步骤二：替换明文密码

```xml
<server>
    <id>company-nexus</id>
    <username>deployer</username>
    <password>{jSMOPuzN2cFb...加密字符串...}</password>
</server>
```

### 步骤三：创建 settings-security.xml

加密后的密码需要一个「主密码」来解密。这个主密码存放在 `~/.m2/settings-security.xml`：

```xml
<settingsSecurity>
    <master>{主密码加密字符串}</master>
</settingsSecurity>
```

生成主密码的方式与加密密码相同：`mvn --encrypt-password`，输入一个主密码短语，将输出的加密字符串放入 `settings-security.xml`。

> **安全建议**：`settings-security.xml` 的权限应设为仅当前用户可读（Linux: `chmod 600`）。

---

## proxies：网络代理

如果公司网络需要通过代理才能访问外网，在 settings.xml 中配置：

```xml
<proxies>
    <proxy>
        <id>company-proxy</id>
        <active>true</active>
        <protocol>http</protocol>
        <host>proxy.company.com</host>
        <port>8080</port>
        <username>proxy-user</username>
        <password>proxy-pass</password>
        <nonProxyHosts>localhost|nexus.company.com</nonProxyHosts>
    </proxy>
</proxies>
```

| 字段 | 含义 |
|------|------|
| `<host>` | 代理服务器地址 |
| `<port>` | 代理端口 |
| `<nonProxyHosts>` | 不走代理的地址列表（用 `|` 分隔） |

> 大多数现代公司网络不需要配置 Maven 代理——直接配镜像（mirror）就够了。代理配置主要用于严格管控网络的企业环境。

---

## 环境变量与内置属性

settings.xml 和 pom.xml 中可以引用以下内置属性：

| 属性 | 含义 | 示例值 |
|------|------|--------|
| `${user.home}` | 用户主目录 | `C:\Users\zhangsan` 或 `/home/zhangsan` |
| `${java.home}` | JDK 安装目录 | `/usr/lib/jvm/java-17` |
| `${env.M2_HOME}` | Maven 安装目录（环境变量） | `/opt/apache-maven-3.9.16` |
| `${settings.localRepository}` | settings.xml 中配置的本地仓库路径 | `D:\maven-repo` |
| `${env.JAVA_HOME}` | JAVA_HOME 环境变量 | 同 `${java.home}` |
| `${project.basedir}` | 当前 pom.xml 所在目录 | `/home/user/my-project` |
| `${project.version}` | 当前项目版本 | `1.0.0` |

在 settings.xml 中使用：

```xml
<localRepository>${user.home}/custom-maven-repo</localRepository>
```

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **settings.xml 配置不生效** | 文件放错了位置（不在 `~/.m2/` 或 Maven 安装目录的 `conf/` 下） | 确认文件路径正确；跑 `mvn help:effective-settings` 查看实际值 |
| **全局和用户级配置冲突** | 两边都配了同一个 id 的 server/mirror，不知道谁生效 | 用户级覆盖全局；用 `effective-settings` 确认 |
| **activeProfiles 配了但 profile 没激活** | `<activeProfiles>` 中的 id 与 `<profiles>` 中的 id 不匹配（拼写错误） | 检查 id 是否完全一致 |
| **多环境切换麻烦** | 每次都要改 settings.xml | 使用 profile + 命令行 `-P` 切换；或在 CI 中用环境变量触发 |
| **密码明文不安全** | settings.xml 被提交到 Git 或被其他用户读取 | 使用 `mvn --encrypt-password` 加密；设文件权限 600 |
| **镜像配了但下载还是慢** | 镜像只代理了中央仓库，但 pom.xml 声明了其他远程仓库不走镜像 | 将 `<mirrorOf>` 改为 `*` 或 `*,!company-nexus` |
| **代理配了但连不上** | `<nonProxyHosts>` 包含了目标仓库地址 | 检查 nonProxyHosts 列表，确保目标仓库不在排除列表中 |
| **`<localRepository>` 改了但依赖还在旧目录** | 只改了配置但没迁移旧仓库文件 | 手动将旧仓库内容复制到新路径，或删除旧目录让 Maven 重新下载 |

---

## Q&A / 踩坑

**Q1：settings.xml 和 pom.xml 都能配 `<repositories>`，有什么区别？**

`settings.xml` 中的 `<repositories>` 放在 `<profiles>` 内，属于**用户级配置**——跟项目无关，换个人/机器可能不同。`pom.xml` 中的 `<repositories>` 属于**项目级配置**——跟着代码走，所有人共享。通常镜像配在 settings.xml，特殊仓库配在 pom.xml。

**Q2：IDEA/Eclipse 用的是哪个 settings.xml？**

IDE 通常使用自己内置的 Maven 或你指定的 Maven 安装目录的全局 settings.xml。如果 IDE 的 Maven 设置与命令行不一致，可能是 IDE 用了不同的 settings 文件。在 IDEA 中检查：Settings → Build → Maven → User settings file。

**Q3：`settings-security.xml` 可以跟 settings.xml 放一起吗？**

不建议。`settings-security.xml` 包含主密码，应该与 `settings.xml` 分开存放，且权限更严格。如果 settings.xml 被提交到 Git，settings-security.xml 绝对不能一起提交。

**Q4：profile 里能配 `<dependencies>` 吗？**

可以，但**不推荐**。profile 中的依赖会按条件激活，增加构建的不可预测性。推荐用 profile 管理 properties 和 repositories，依赖声明尽量放在 pom.xml 的 `<dependencies>` 中。

---

## 要点总结

1. **两级位置**：全局（`conf/settings.xml`，影响所有用户）+ 用户级（`~/.m2/settings.xml`，只影响当前用户），用户级优先
2. **合并规则**：servers/mirrors/profiles 按 id 合并，id 相同时用户级覆盖全局
3. **核心配置**：localRepository（本地仓库路径）、servers（认证）、mirrors（镜像）、profiles（多环境）、activeProfiles（默认激活）
4. **Profile 四种激活方式**：命令行 `-P`、activeByDefault、JDK 版本匹配、属性/环境变量匹配
5. **密码加密**：`mvn --encrypt-password` 加密密码，配合 `settings-security.xml` 存储主密码
6. **调试利器**：`mvn help:effective-settings` 查看合并后的实际配置
7. **安全建议**：settings.xml 不提交到 Git；settings-security.xml 权限设为 600

---

> ### 💡 新人小结：settings 配置学完了，记住这 3 点
>
> 1. **国内必配镜像**——settings.xml 加一行阿里云镜像，下载速度提升 10 倍
> 2. **配置不生效就查 effective-settings**——`mvn help:effective-settings` 看合并后的真实值
> 3. **多环境用 profile**——开发/测试/生产各一套 profile，`-P` 一键切换
>
> 至此，Maven 七篇文档全部学完。从「Maven 是什么」到「settings 怎么配」，你已经掌握了 Maven 的核心知识体系。遇到构建问题，回到对应的章节查阅即可。
