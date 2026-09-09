---
title: "mc idp ldap accesskey create-with-login"

weight: 160
---

<a id="mc-idp-ldap-accesskey-create-with-login"></a>
<a id="minio-mc-idp-ldap-accesskey-create-with-login"></a>

<a id="command-mc.idp.ldap.accesskey.create-with-login"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-04-18T16-45-29Z

## 描述 {#id2}

[`mc idp ldap accesskey create-with-login`](#command-mc.idp.ldap.accesskey.create-with-login) 使用基于终端的交互式提示与外部 AD/LDAP 服务器进行身份验证，并生成可供 MinIO 使用的访问密钥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
> 以下示例会提示用户提供其 AD/LDAP 凭证。 然后使用与该 AD/LDAP 用户关联的一个或多个策略生成新的访问密钥对。

```shell
mc idp ldap accesskey create-with-login https://minio.example.net/
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] idp ldap accesskey create-with-login        \
                                 URL                         \
                                 [--access-key <value>]      \
                                 [--secret-key <value>]      \
                                 [--policy <value>]          \
                                 [--name <value>]            \
                                 [--description <value>]     \
                                 [--expiry <value>]          \
                                 [--expiry-duration <value>]
```

- 将 `URL` 替换为已配置 AD/LDAP 集成的 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr>。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `URL` {#mc.idp.ldap.accesskey.create-with-login.URL}

*mc-cmd*

*Required*

已配置 AD/LDAP 集成的 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr>。

例如：

```text
mc idp ldap accesskey create-with-login https://minio.example.net
```

##### `--access-key` {#mc.idp.ldap.accesskey.create-with-login.-access-key}

*mc-cmd*

*Optional*

成功完成身份验证后要使用的访问密钥。 省略此项则由 MinIO 随机生成一个值。

访问密钥不能包含 `=`（等号）或 `,`（逗号）字符。

需要同时指定 [`--secret-key`](#mc.idp.ldap.accesskey.create-with-login.-secret-key)

##### `--secret-key` {#mc.idp.ldap.accesskey.create-with-login.-secret-key}

*mc-cmd*

*Optional*

成功完成身份验证后要使用的 secret key。 省略此项则由 MinIO 随机生成一个值。

需要同时指定 [`--access-key`](#mc.idp.ldap.accesskey.create-with-login.-access-key)

##### `--policy` {#mc.idp.ldap.accesskey.create-with-login.-policy}

*mc-cmd*

*Optional*

账户要使用的 JSON 格式 [policy](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 文件路径。 该策略_不能_授予超出已认证 AD/LDAP 用户关联权限范围之外的额外权限。

省略此项则使用 AD/LDAP 用户关联策略。

##### `--name` {#mc.idp.ldap.accesskey.create-with-login.-name}

*mc-cmd*

*Optional*

为创建的访问密钥指定一个便于识别的名称。

##### `--description` {#mc.idp.ldap.accesskey.create-with-login.-description}

*mc-cmd*

*Optional*

为服务账户创建描述。 例如，你可以说明该访问密钥存在的原因。

##### `--expiry-duration` {#mc.idp.ldap.accesskey.create-with-login.-expiry-duration}

*mc-cmd*

*Optional*

访问密钥对保持可用的时长，格式为 `#d#h#s`。

例如，`7d`、`24h`、`5d12h30s` 都是有效字符串。

与 [`--expiry`](#mc.idp.ldap.accesskey.create-with-login.-expiry) 互斥。

##### `--expiry` {#mc.idp.ldap.accesskey.create-with-login.-expiry}

*mc-cmd*

*Optional*

访问密钥的过期日期。 以 `YYYY-MM-DD` 格式输入日期。

例如，要让凭证在 2024 年 12 月 31 日后过期，输入 `2024-12-31`。

与 [`--expiry-duration`](#mc.idp.ldap.accesskey.create-with-login.-expiry-duration) 互斥。

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 示例 {#id10}

### 为已认证用户创建新的访问密钥对 {#id11}

以下命令为 `minio` 别名下当前已认证用户创建新的访问密钥对。 该命令会输出随机生成的 access key 和 secret key。

```shell
mc idp ldap accesskey create-with-login https://minio.example.net
```

### 使用自定义 access key 和 secret key 创建新的访问密钥对 {#access-key-secret-key}

以下命令为 `minio` 别名下当前已认证用户创建新的访问密钥对，其中 access key 和 secret key 都由你指定。

```shell
mc idp ldap accesskey create-with-login https://minio.example.net/ --access-key my-access-key-change-me --secret-key my-secret-key-change-me
```

### 创建 24 小时后过期的新访问密钥对 {#id12}

以下命令为 `minio` 别名下当前已认证用户创建新的访问密钥对。 该凭证会在 24 小时后过期。

该命令会输出随机生成的 access key 和 secret key。

```shell
mc idp ldap accesskey create-with-login https://minio.example.net --expiry-duration 24h
```

### 创建在指定日期后过期的新访问密钥对 {#id13}

以下命令为 `minio` 别名下当前已认证用户创建新的访问密钥对。 该凭证会在 2025 年 2 月 28 日后过期。

该命令会输出随机生成的 access key 和 secret key。

```shell
mc idp ldap accesskey create-with-login https://minio.example.net --expiry 2025-02-28
```