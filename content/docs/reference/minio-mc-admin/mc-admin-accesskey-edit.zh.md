---
title: "mc admin user accesskey edit"

weight: 30
---

<a id="mc-admin-user-accesskey-edit"></a>
<a id="minio-mc-admin-accesskey-edit"></a>

<a id="command-mc.admin.accesskey.edit"></a>

## 语法 {#id2}

[`mc admin accesskey edit`](#command-mc.admin.accesskey.edit) 命令用于修改与指定用户关联的访问密钥配置。

该命令要求访问密钥至少有一个属性发生变更。 否则，命令会报错退出。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` 部署上的 `myuserserviceaccount` 访问密钥应用新的策略和 secret key：

```shell
mc admin accesskey edit                                             \
                   myminio myuserserviceaccount                     \
                   --secret-key "myuserserviceaccountnewsecretkey"  \
                   --policy "/path/to/new/policy.json"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin accesskey edit                      \
                                 ALIAS                     \
                                 ACCESSKEY                 \
                                 [--description string]    \
                                 [--expiry-duration value] \
                                 [--expiry value]          \
                                 [--name string]           \
                                 [--policy path]           \
                                 [--secret-key string]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.accesskey.edit.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `ACCESSKEY` {#mc.admin.accesskey.edit.ACCESSKEY}

*mc-cmd*

*Required*

要修改的访问密钥。

##### `--description` {#mc.admin.accesskey.edit.-description}

*mc-cmd*

*Optional*

为访问密钥添加或修改描述。 例如，可用于说明该访问密钥的用途。

##### `--expiry` {#mc.admin.accesskey.edit.-expiry}

*mc-cmd*

*Optional*

设置或修改访问密钥的过期日期。 日期必须为未来时间，不能设置已过去的过期日期。

允许的日期和时间格式：

- `2023-06-24`
- `2023-06-24T10:00`
- `2023-06-24T10:00:00`
- `2023-06-24T10:00:00Z`
- `2023-06-24T10:00:00-07:00`

与 [`--expiry-duration`](#mc.admin.accesskey.edit.-expiry-duration) 互斥。

##### `--expiry-duration` {#mc.admin.accesskey.edit.-expiry-duration}

*mc-cmd*

*Optional*

访问密钥保持有效的时长。 有效时间单位为 “ns”、”us”（或 “µs”）、”ms”、”s”、”m”、”h”。

若要让凭证在 30 天后过期，请使用：

```text
--expiry-duration 720h
```

与 [`--expiry`](#mc.admin.accesskey.edit.-expiry) 互斥。

##### `--name` {#mc.admin.accesskey.edit.-name}

*mc-cmd*

*Optional*

为访问密钥添加或修改一个便于识别的名称。

##### `--policy` {#mc.admin.accesskey.edit.-policy}

*mc-cmd*

*Optional*

要附加到新访问密钥的 [策略文档](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 路径，最大长度为 2048 个字符。 附加策略不能授予父用户策略中未显式允许的任何操作或资源访问权限。

新策略会覆盖此前附加的任何策略。

##### `--secret-key` {#mc.admin.accesskey.edit.-secret-key}

*mc-cmd*

*Optional*

要与新访问密钥关联的 secret key。 会覆盖先前的 secret key。 使用该访问密钥的应用 *必须* 更新为新凭证，才能继续执行操作。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 修改访问密钥的 secret key {#secret-key}

以下命令修改 `myminio` 部署上 `myuseraccesskey` 访问密钥的 secret key。

```shell
mc admin accesskey edit myminio/ myuseraccesskey --secret-key 'new-secret-key-change-me'
```

### 修改访问密钥的过期设置 {#id6}

以下命令修改 `myminio` 部署上 `myuseraccesskey` 访问密钥的过期值。

```shell
mc admin accesskey edit myminio/ myuseraccesskey --expiry-duration 24h
```

如果访问密钥已设置 [`--expiry`](#mc.admin.accesskey.edit.-expiry)，则不能再添加 [`--expiry-duration`](#mc.admin.accesskey.edit.-expiry-duration)。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。