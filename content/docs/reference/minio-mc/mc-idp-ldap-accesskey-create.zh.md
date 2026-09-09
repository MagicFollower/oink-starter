---
title: "mc idp ldap accesskey create"

weight: 9262
toc_hide: true
---

<a id="mc-idp-ldap-accesskey-create"></a>
<a id="minio-mc-idp-ldap-accesskey-create"></a>

<a id="command-mc.idp.ldap.accesskey.create"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-23T08-47-21Z

## 描述 {#id1}

[`mc idp ldap accesskey create`](#command-mc.idp.ldap.accesskey.create) 允许添加 LDAP 访问密钥对。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
> 以下示例在 `minio` [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 上创建一个新的访问密钥对，并使用与已认证用户相同的策略：

```shell
mc idp ldap accesskey create minio/
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] idp ldap accesskey create                   \
                                 ALIAS                       \
                                 [--access-key <value>]      \
                                 [--secret-key <value>]      \
                                 [--policy <value>]          \
                                 [--name <value>]            \
                                 [--description <value>]     \
                                 [--expiry <value>]          \
                                 [--expiry-duration <value>]
```

- 将 `ALIAS` 替换为已配置 AD/LDAP 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.idp.ldap.accesskey.create.ALIAS}

*mc-cmd*

*Required*

已配置 AD/LDAP 的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap accesskey create minio
```

##### `--access-key` {#mc.idp.ldap.accesskey.create.-access-key}

*mc-cmd*

*Optional*

用于该账户的访问密钥。 访问密钥不能包含 `=`（等号）或 `,`（逗号）字符。

需要 [`--secret-key`](#mc.idp.ldap.accesskey.create.-secret-key)

##### `--secret-key` {#mc.idp.ldap.accesskey.create.-secret-key}

*mc-cmd*

*Optional*

用于该账户的密钥。

需要 [`--access-key`](#mc.idp.ldap.accesskey.create.-access-key)

##### `--policy` {#mc.idp.ldap.accesskey.create.-policy}

*mc-cmd*

*Optional*

账户要使用的 JSON 格式策略文件路径。

如果未指定，账户将使用与已认证用户相同的策略。

##### `--name` {#mc.idp.ldap.accesskey.create.-name}

*mc-cmd*

*Optional*

用于该账户的人类可读名称。

##### `--description` {#mc.idp.ldap.accesskey.create.-description}

*mc-cmd*

*Optional*

为服务账户添加描述。 例如，你可以说明创建该访问密钥的原因。

##### `--expiry-duration` {#mc.idp.ldap.accesskey.create.-expiry-duration}

*mc-cmd*

*Optional*

访问密钥对保持有效的时长，格式为 `#d#h#s`。

例如，`7d`、`24h`、`5d12h30s` 都是有效字符串。

与 [`--expiry`](#mc.idp.ldap.accesskey.create.-expiry) 互斥。

##### `--expiry` {#mc.idp.ldap.accesskey.create.-expiry}

*mc-cmd*

*Optional*

访问密钥在该日期之后过期。 日期请使用 YYYY-MM-DD 格式输入。

例如，要使凭证在 2024 年 12 月 31 日之后过期，请输入 `2024-12-31`。

与 [`--expiry-duration`](#mc.idp.ldap.accesskey.create.-expiry-duration) 互斥。

##### `--login` {#mc.idp.ldap.accesskey.create.-login}

*mc-cmd*

*Optional*

> [!CAUTION]
> **已弃用: RELEASE.2024-04-18T16-45-29Z**
>
> 使用 [`mc idp ldap accesskey create-with-login`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create-with-login/#command-mc.idp.ldap.accesskey.create-with-login) 获取此前由该参数提供的功能。

提示用户使用 LDAP 凭证登录以生成访问密钥。 指定用于登录提示的、已配置 LDAP 的 MinIO Server URL。

需要交互式终端。

### 全局标志 {#id7}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 示例 {#id9}

### 为已认证用户创建新的访问密钥对 {#id10}

以下命令会为 `minio` alias 上当前已认证用户创建一个新的访问密钥对。 该命令会输出随机生成的访问密钥和密钥。

```shell
mc idp ldap accesskey create minio
```

### 使用自定义访问密钥和密钥创建新的访问密钥对 {#id11}

以下命令会为 `minio` alias 上当前已认证用户创建一个新的访问密钥对，其中访问密钥和密钥都由你指定。

```shell
mc idp ldap accesskey create minio/ --access-key my-access-key-change-me --secret-key my-secret-key-change-me
```

### 创建 24 小时后过期的新访问密钥对 {#id12}

以下命令会为 `minio` alias 上当前已认证用户创建一个新的访问密钥对。 该凭证会在 24 小时后过期。

该命令会输出随机生成的访问密钥和密钥。

```shell
mc idp ldap accesskey create minio --expiry-duration 24h
```

### 创建新的访问密钥并提示以该用户身份登录 {#id13}

以下命令会创建一个新的访问密钥对。 MinIO Client 会先要求你在 `minio.example.com` 上已配置 LDAP 的 MinIO 站点中，以该访问密钥所属用户身份登录。

该命令会输出随机生成的访问密钥和密钥。

```shell
mc idp ldap accesskey create minio --login minio.example.com
```

### 创建在指定日期后过期的新访问密钥对 {#id14}

以下命令会为 `minio` alias 上当前已认证用户创建一个新的访问密钥对。 该凭证会在 2024 年 2 月 29 日之后过期。

该命令会输出随机生成的访问密钥和密钥。

```shell
mc idp ldap accesskey create minio --expiry 2024-02-29
```