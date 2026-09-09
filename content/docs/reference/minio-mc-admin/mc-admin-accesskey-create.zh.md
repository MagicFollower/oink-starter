---
title: "mc admin accesskey create"

weight: 10
---

<a id="mc-admin-accesskey-create"></a>
<a id="minio-mc-admin-accesskey-create"></a>

<a id="command-mc.admin.accesskey.create"></a>

## 语法 {#id2}

[`mc admin accesskey create`](#command-mc.admin.accesskey.create) 命令为现有 MinIO 用户添加新的 access key 和 secret key 对。

> [!NOTE]
> **OpenID Connect 或 AD/LDAP 用户的访问密钥**
>
> 此命令用于为直接在 MinIO 部署上创建、且不由第三方方案管理的用户创建访问密钥。
>
> 要为 [Active Directory/LDAP users](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 生成访问密钥，请使用 [`mc idp ldap accesskey create`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会创建一个与现有 MinIO 用户关联的新访问密钥：

```shell
mc admin accesskey create        \
   myminio/ myuser               \
   --access-key myuseraccesskey  \
   --secret-key myusersecretkey  \
   --policy /path/to/policy.json
```

该命令会返回新账户的 access key 和 secret key。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin accesskey create                    \
                                 ALIAS                     \
                                 [USER]                    \
                                 [--access-key string]     \
                                 [--secret-key string]     \
                                 [--policy path]           \
                                 [--name string]           \
                                 [--description string]    \
                                 [--expiry-duration value] \
                                 [--expiry date]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.accesskey.create.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USER` {#mc.admin.accesskey.create.USER}

*mc-cmd*

*Optional*

MinIO 要为其添加新访问密钥的用户名。 如果未指定，MinIO 会为已认证用户生成 access key/secret key 对。

##### `--access-key` {#mc.admin.accesskey.create.-access-key}

*mc-cmd*

*Optional*

作为此账户 access key 使用的字符串。 若省略，MinIO 会自动生成一个随机的 20 字符值。

Access Key 名称在所有用户之间 *必须* 唯一。

##### `--description` {#mc.admin.accesskey.create.-description}

*mc-cmd*

*Optional*

为访问密钥添加描述。 例如，可以说明该访问密钥存在的原因。

##### `--expiry` {#mc.admin.accesskey.create.-expiry}

*mc-cmd*

*Optional*

为访问密钥设置过期日期。 该日期必须是未来时间。 不可设置已经过去的过期日期。

允许的日期和时间格式：

- `2024-10-24`
- `2024-10-24T10:00`
- `2024-10-24T10:00:00`
- `2024-10-24T10:00:00Z`
- `2024-10-24T10:00:00-07:00`

与 [`--expiry-duration`](#mc.admin.accesskey.create.-expiry-duration) 互斥。

##### `--expiry-duration` {#mc.admin.accesskey.create.-expiry-duration}

*mc-cmd*

*Optional*

access key 保持有效的时长。 有效时间单位为 “ns”、”us”（或 “µs”）、”ms”、”s”、”m”、”h”。

以下示例会让凭证在 30 天后过期：

```text
--expiry-duration 720h
```

与 [`--expiry`](#mc.admin.accesskey.create.-expiry) 互斥。

##### `--name` {#mc.admin.accesskey.create.-name}

*mc-cmd*

*Optional*

为访问密钥添加人类可读名称。

##### `--policy` {#mc.admin.accesskey.create.-policy}

*mc-cmd*

*Optional*

要附加到新访问密钥上的 [policy document](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 的可读路径，最大大小为 2048 字符。 所附加策略不得授予父用户策略或组策略未明确允许的任何操作或资源访问权限。

##### `--secret-key` {#mc.admin.accesskey.create.-secret-key}

*mc-cmd*

*Optional*

与新账户关联的 secret key。 若省略，MinIO 会自动生成一个随机的 40 字符值。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 为已认证用户创建 access key / secret key 对 {#access-key-secret-key}

以下命令会为当前登录到别名为 `myminio` 的 MinIO 部署的用户生成新的随机 access key 和 secret key 对。 该 access key 和 secret key 与已认证用户具有相同的访问策略。

```shell
mc admin accesskey create myminio/
```

### 为已认证用户创建自定义 access key / secret key 对 {#id6}

以下命令会为当前登录到别名为 `myminio` 的 MinIO 的用户创建新的 access key 和 secret key 对。 该 access key 和 secret key 与已认证用户具有相同的访问策略。

```shell
mc admin accesskey create myminio/ --access-key myaccesskey --secret-key mysecretkey
```

### 为另一位用户创建有时长限制的 access key / secret key 对 {#id7}

以下命令会为别名 `myminio` 上的用户 `miniouser` 创建新的 access key 和 secret key 对。 该 access key 和 secret key 与 `miniouser` 具有相同的访问策略。 这些凭证在创建后 24 小时内有效。

```shell
mc admin accesskey create myminio/ miniouser --expiry-duration 24h
```

### 为已认证用户创建会过期的 access key / secret key 对 {#id8}

以下命令会为当前登录到别名 `myminio` 的 MinIO 部署的用户生成新的随机 access key 和随机 secret key 对。 该 access key 和 secret key 与已认证用户具有相同的访问策略。 这些凭证将于 2025 年 1 月 15 日过期。

```shell
mc admin accesskey create myminio/ --expiry 2025-01-15
```

指定的日期 **必须** 是未来日期。 有关有效的日期时间格式，请参见 [`--expiry`](#mc.admin.accesskey.create.-expiry) 标志。

### 为不同用户创建具有自定义访问权限的 access key / secret key 对 {#id9}

以下命令会为别名 `myminio` 上的用户 `miniouser` 创建新的 access key 和 secret key 对。 该 access key 和 secret key 的访问权限比 `miniouser` 更受限，具体由策略 JSON 文件指定。

```shell
mc admin accesskey create myminio/ miniouser --policy /path/to/policy.json
```

指定的策略文件 **不得** 授予 `miniouser` 当前尚未拥有的任何访问权限。

## 行为 {#id10}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。