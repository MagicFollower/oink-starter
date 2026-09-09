---
title: "mc admin accesskey ls"

weight: 60
---

<a id="mc-admin-accesskey-ls"></a>
<a id="minio-mc-admin-accesskey-list"></a>

<a id="command-mc.admin.accesskey.list"></a>

<a id="command-mc.admin.accesskey.ls"></a>

## 语法 {#id2}

[`mc admin accesskey ls`](#command-mc.admin.accesskey.ls) 命令列出 MinIO 部署管理的用户、访问密钥或临时 [security token service](/docs/developers/security-token-service/#minio-security-token-service) 密钥。

[`mc admin accesskey list`](#command-mc.admin.accesskey.list) 别名与 [`mc admin accesskey ls`](#command-mc.admin.accesskey.ls) 功能等效。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出别名为 `myminio` 的部署中，用户名为 `admin1` 的用户关联的所有访问密钥：

```shell
mc admin accesskey ls myminio admin1
```

输出如下所示：

```shell
   Access Key        | Expiry
5XF3ZHNZK6FBDWH9JMLX | 2023-06-24 07:00:00 +0000 UTC
F4V2BBUZSWY7UG96ED70 | 2023-12-24 18:00:00 +0000 UTC
FZVSEZ8NM9JRBEQZ7B8Q | no-expiry
HOXGL8ON3RG0IKYCHCUD | no-expiry
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] admin accesskey ls             \
                                 ALIAS          \
                                 [USER]         \
                                 [--all]        \
                                 [--self]       \
                                 [--temp-only]  \
                                 [--users-only]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.accesskey.ls.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USER` {#mc.admin.accesskey.ls.USER}

*mc-cmd*

*Optional*

要显示其访问密钥的用户名称。 多个用户名之间使用空格分隔。

##### `--all` {#mc.admin.accesskey.ls.-all}

*mc-cmd*

*Optional*

列出所有用户及其关联的任意访问密钥或临时 STS 密钥。 需要具有该部署的管理员权限。

此标志与该命令的其他可用标志互斥。

##### `--svcacc-only` {#mc.admin.accesskey.ls.-svcacc-only}

*mc-cmd*

*Optional*

列出部署上的临时 [Security Token Service (STS) keys](/docs/developers/security-token-service/#minio-security-token-service)。

此标志与该命令的其他可用标志互斥。

##### `--self` {#mc.admin.accesskey.ls.-self}

*mc-cmd*

*Optional*

列出当前已认证用户的访问密钥和 STS 密钥。

此标志与该命令的其他可用标志互斥。

##### `--temp-only` {#mc.admin.accesskey.ls.-temp-only}

*mc-cmd*

*Optional*

列出用户及其访问密钥。 仅返回已关联访问密钥的用户。

运行命令的用户必须具有管理员权限才能使用此标志。

此标志与该命令的其他可用标志互斥。

##### `--users-only` {#mc.admin.accesskey.ls.-users-only}

*mc-cmd*

*Optional*

列出该部署管理的 MinIO 用户。 与 [`--all`](#mc.admin.accesskey.ls.-all) 标志配合使用可列出部署上的所有用户。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出所有内置用户及其关联访问密钥 {#id6}

以下命令列出别名为 `myminio` 的 MinIO 部署所管理的所有用户，以及其关联的任意访问密钥或临时 STS 令牌。

```shell
mc admin accesskey list myminio/ --all
```

### 返回当前已认证用户的访问密钥列表 {#id7}

以下命令列出 `myminio` 部署中与当前已认证用户关联的访问密钥或临时 STS 令牌。

```shell
mc admin accesskey list myminio/ --self
```

### 列出由部署创建并管理的所有用户 {#id8}

以下命令返回当前部署上的所有用户列表。 该列表仅包含由 MinIO IDP 管理的用户，不包含通过 OpenID 或 Active Directory/LDAP 等协议由第三方工具管理的用户。

```shell
mc admin accesskey ls myminio/ --all --users-only
```

### 返回与用户 `miniouser1` 和 `miniouser2` 关联的访问密钥列表 {#miniouser1-miniouser2}

以下命令返回 `myminio` 部署上这两个用户的访问密钥列表。

```shell
mc admin accesskey ls myminio/ miniouser1 miniouser2
```

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。