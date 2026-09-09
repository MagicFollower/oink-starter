---
title: "mc idp ldap accesskey edit"

weight: 20
---

<a id="mc-idp-ldap-accesskey-edit"></a>
<a id="minio-mc-idp-ldap-accesskey-edit"></a>

<a id="command-mc.idp.ldap.accesskey.edit"></a>

## 说明 {#id2}

[`mc idp ldap accesskey edit`](#command-mc.idp.ldap.accesskey.edit) 在本地服务器上修改指定的 [access key](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
> 以下示例在 `minio` 部署上修改 access key `mykey` 的 secret：

```shell
mc idp ldap accesskey edit myminio/ mykey --secret-key 'xxxxxxx'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] idp ldap accesskey rm                        \
                                 ALIAS                        \
                                 KEY                          \
                                 [--secret-key <string>]      \
                                 [--policy <string>]          \
                                 [--name <string>]            \
                                 [--description <string>]     \
                                 [--expiry-duration <string>] \
                                 [--expiry <string>]
```

- 将 `ALIAS` 替换为已配置 AD/LDAP 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `KEY` 替换为要删除的 access key。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.accesskey.edit.ALIAS}

*mc-cmd*

*Required*

已配置 AD/LDAP 的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap accesskey ls minio
```

##### `KEY` {#mc.idp.ldap.accesskey.edit.KEY}

*mc-cmd*

*Required*

要删除的已配置 access key。

##### `--description` {#mc.idp.ldap.accesskey.edit.-description}

*mc-cmd*

*Optional*

为服务账户添加描述。 例如，可说明该 access key 的用途。

##### `--expiry` {#mc.idp.ldap.accesskey.edit.-expiry}

*mc-cmd*

*Optional*

access key 的过期日期。 请输入 YYYY-MM-DD 格式的日期。

例如，要让凭证在 2024 年 12 月 31 日后过期，输入 `2024-12-31`。

与 [`--expiry-duration`](#mc.idp.ldap.accesskey.edit.-expiry-duration) 互斥。

##### `--expiry-duration` {#mc.idp.ldap.accesskey.edit.-expiry-duration}

*mc-cmd*

*Optional*

access key 保持有效的时长，格式为 `#d#h#s`。

例如，`7d`、`24h`、`5d12h30s` 都是有效字符串。

与 [`--expiry`](#mc.idp.ldap.accesskey.edit.-expiry) 互斥。

##### `--name` {#mc.idp.ldap.accesskey.edit.-name}

*mc-cmd*

*Optional*

账号的人类可读名称。

##### `--policy` {#mc.idp.ldap.accesskey.edit.-policy}

*mc-cmd*

*Optional*

账号使用的 JSON 格式策略文件路径。

如果未指定，账号将使用与已认证用户相同的策略。

##### `--secret-key` {#mc.idp.ldap.accesskey.edit.-secret-key}

*mc-cmd*

*Optional*

账号使用的 secret。

### 示例 {#id4}

#### 修改 access key 的 secret {#access-key-secret}

在 `minio` 部署上修改 access key `mykey` 的 secret。

```shell
mc idp ldap accesskey edit myminio/ mykey --secret-key 'xxxxxxx'
```

#### 修改 access key 的过期时长 {#access-key}

在 `minio` 部署上修改 access key `mykey` 的过期时长。

```shell
mc idp ldap accesskey edit myminio/ mykey ---expiry-duration 24h
```

### 全局参数 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。