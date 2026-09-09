---
title: "mc replicate update"

weight: 40
---

<a id="mc-replicate-update"></a>
<a id="minio-mc-replicate-update"></a>
<a id="minio-mc-replicate-edit"></a>

<a id="command-mc.replicate.edit"></a>

<a id="command-mc.replicate.update"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc replicate update` 替代了 `mc admin bucket remote update` 命令。

> [!NOTE]
> **变更: RELEASE.2022-11-07T23-47-39Z**
>
> `mc replicate update` 替代了 `mc replicate edit` 命令。

## 语法 {#id2}

[`mc replicate update`](#command-mc.replicate.update) 命令用于修改现有的 [存储桶复制规则](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。

```shell
mc [GLOBALFLAGS] replicate update FLAGS [FLAGS] ARGUMENTS [ARGUMENTS]
```

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会修改 `myminio` MinIO 部署中 `mydata` 存储桶的一条现有复制规则：

```shell
mc replicate update --id "c76um9h4b0t1ijr36mug"           \
   --replicate "delete,delete-marker,existing-objects"  \
   myminio/mydata
```

新的复制配置会将所有版本化删除操作、删除标记创建以及现有对象 同步到远端 MinIO 部署。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] replicate update              \
                 --remote-bucket string          \
                 [--bandwidth "string"]            \
                 [--healthcheck-seconds integer]   \
                 [--id "string"]                   \
                 [--limit-upload "string"]         \
                 [--limit-download "string"]       \
                 [--path "string"]                 \
                 [--priority int]                  \
                 [--proxy]
                 [--replicate "string"]            \
                 [--state string]
                 [--storage-class "string"]        \
                 [--sync string]                          \
                 [--tags "string"]                 \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.replicate.update.ALIAS}

*mc-cmd*

*Required*

要修改复制规则的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及存储桶或存储桶前缀的完整路径。 例如：

```text
mc replicate update --id "c75nrap4b0talo3ipthg" [FLAGS]
```

##### `--id` {#mc.replicate.update.-id}

*mc-cmd*

*Required*

指定已配置复制规则的唯一 ID。 使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 命令列出存储桶的复制规则。

##### `--bandwidth` {#mc.replicate.update.-bandwidth}

*mc-cmd*

*Optional*

将带宽速率限制为不超过指定值，单位可为 KiB/s、MiB/s 或 GiB/s。 有效单位包括：

- `B` 表示 bytes
- `K` 表示 kilobytes
- `G` 表示 gigabytes
- `T` 表示 terabytes
- `Ki` 表示 kibibytes
- `Gi` 表示 gibibytes
- `Ti` 表示 tebibytes

例如，要将带宽速率限制为不超过 1 GiB/s，可使用：

```text
--limit-upload 1Gi
```

如果未指定，MinIO 不限制带宽速率。

##### `--healthcheck-seconds` {#mc.replicate.update.-healthcheck-seconds}

*mc-cmd*

*Optional*

远端存储桶健康状态检查之间的时间间隔（秒）。

如果未指定，MinIO 使用 60 秒间隔。

##### `--limit-download` {#mc.replicate.update.-limit-download}

*mc-cmd*

*Optional*

将下载速率限制为不超过指定值，单位可为 KiB/s、MiB/s 或 GiB/s。 有效单位包括：

- `B` 表示 bytes
- `K` 表示 kilobytes
- `G` 表示 gigabytes
- `T` 表示 terabytes
- `Ki` 表示 kibibytes
- `Gi` 表示 gibibytes
- `Ti` 表示 tebibytes

例如，要将下载速率限制为不超过 1 GiB/s，可使用：

```text
--limit-download 1G
```

如果未指定，MinIO 使用不限速下载。

##### `--limit-upload` {#mc.replicate.update.-limit-upload}

*mc-cmd*

*Optional*

将上传速率限制为不超过指定值，单位可为 KiB/s、MiB/s 或 GiB/s。 有效单位包括：

- `B` 表示 bytes
- `K` 表示 kilobytes
- `G` 表示 gigabytes
- `T` 表示 terabytes
- `Ki` 表示 kibibytes
- `Gi` 表示 gibibytes
- `Ti` 表示 tebibytes

例如，要将上传速率限制为不超过 1 GiB/s，可使用：

```text
--limit-upload 1G
```

如果未指定，MinIO 使用不限速上传。

##### `--path` {#mc.replicate.update.-path}

*mc-cmd*

*Optional*

为远端存储桶启用 path-style 查找支持。

有效值包括：

- `on` - 使用路径查找来定位远端存储桶
- `off` - 使用资源定位符样式（如域名或 IP 地址）查找来定位远端存储桶
- `auto` - 让 MinIO 自动识别用于定位远端存储桶的正确查找类型

未定义时，MinIO 使用 `auto` 值。

##### `--priority` {#mc.replicate.update.-priority}

*mc-cmd*

*Optional*

指定复制规则的整数优先级。 该值 *必须* 在源存储桶的所有其他规则中唯一。 数值越高，优先级越 *高*。

##### `--proxy` {#mc.replicate.update.-proxy}

*mc-cmd*

*Optional*

在存储桶之间定义 active-active 复制时，是否使用代理。

有效值包括：

- `enable` - 在 active-active 复制中启用代理。
- `disable` - 在 active-active 复制中禁用代理。

默认情况下，MinIO 默认为 `enable`。

##### `--remote-bucket` {#mc.replicate.update.-remote-bucket}

*mc-cmd*

*Optional*

指定远端位置的凭据、目标部署和存储桶。 值可以是 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 与存储桶，也可以是基于位置（IP 或 URL）或基于路径的形式。

例如，基于 URL 的目标可能如下：

```text
--remote-bucket https://user:secret@myminio.cloudprovider.tld:9001/bucket
```

基于 alias 的目标可能如下：

```text
--remote-bucket minio-target/my-bucket
```

##### `--replicate` {#mc.replicate.update.-replicate}

*mc-cmd*

*Optional*

指定由逗号分隔的以下值列表，以启用扩展复制功能：

- `delete` - 指示 MinIO 将 [DELETE operations](/docs/administration/object-management/object-delete/#minio-object-delete) 复制到目标存储桶。
- `delete-marker` - 指示 MinIO 将删除标记复制到目标存储桶。
- `replica-metadata-sync` - 指示 MinIO 将已复制对象上仅元数据的变更同步回源端。 该功能仅影响 [双向 active-active](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway) 复制配置。

  省略此值会使 MinIO 停止将仅元数据变更复制回源端。
- `existing-objects` - 指示 MinIO 复制在配置或启用复制之前已创建的对象。 默认情况下，MinIO *不会* 将现有对象同步到远端目标。

  更多信息参见 [现有对象的复制](/docs/administration/bucket-replication/#minio-replication-behavior-existing-objects)。

##### `--state` {#mc.replicate.update.-state}

*mc-cmd*

*Optional*

启用或禁用复制规则。 指定以下值之一：

- `"enable"` - 启用复制规则。
- `"disable"` - 禁用复制规则。

在复制被禁用期间创建的对象，在重新启用规则后不会立即具备复制资格。 你必须在传给 [`mc replicate update --replicate`](#mc.replicate.update.-replicate) 的复制功能列表中包含 `"existing-objects"`，以显式启用现有对象复制。

更多信息参见 [现有对象的复制](/docs/administration/bucket-replication/#minio-replication-behavior-existing-objects)。

##### `--storage-class` {#mc.replicate.update.-storage-class}

*mc-cmd*

*Optional*

指定要应用到已复制对象上的 MinIO [storage class](/docs/reference/minio-server/settings/storage-class/#minio-ec-storage-class)。

##### `--sync` {#mc.replicate.update.-sync}

*mc-cmd*

*Optional*

为此远端目标启用同步复制。

默认情况下，MinIO 使用异步复制。

##### `--tags` {#mc.replicate.update.-tags}

*mc-cmd*

*Optional*

指定一个或多个以与号 `&` 分隔的键值对标签，MinIO 使用这些标签来筛选待复制对象。例如：

```shell
mc replicate update --id "ID" --tags "TAG1=VALUE&TAG2=VALUE&TAG3=VALUE"
```

MinIO 会将复制规则应用到标签集中 包含指定复制标签的任何对象。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 修改现有复制规则 {#id6}

使用 [`mc replicate update`](#command-mc.replicate.update) 修改现有复制规则。

```shell
mc replicate update ALIAS/PATH \
   --id ID                     \
   [--FLAGS]
```

- 将 [`ALIAS`](#mc.replicate.update.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.update.ALIAS) 替换为该规则所在存储桶或存储桶前缀的路径。
- 将 [`ID`](#mc.replicate.update.-id) 替换为要修改规则的唯一标识符。 使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 获取该存储桶上的复制规则列表及其对应标识符。

> [!NOTE]
> **说明**
>
> 修改复制配置规则不会影响已经复制的对象。 例如，修改 [`--tags`](#mc.replicate.update.-tags) 过滤器不会删除不满足过滤条件的已复制对象。

### 更新现有复制规则的凭据 {#id7}

使用 [`mc replicate update`](#command-mc.replicate.update) 修改现有复制规则。

```shell
mc replicate update ALIAS/PATH \
   --id ID                     \
   --remote-bucket https://user:secret@minio.mycloud.tld:9001/mybucket
```

- 将 [`ALIAS`](#mc.replicate.update.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.update.ALIAS) 替换为该规则所在存储桶或存储桶前缀的路径。
- 将 [`ID`](#mc.replicate.update.-remote-bucket) 替换为更新后的凭据、路径和存储桶。

### 禁用或启用现有复制规则 {#id8}

使用带 [`--state`](#mc.replicate.update.-state) 标志的 [`mc replicate update`](#command-mc.replicate.update) 来禁用或启用复制规则。

```shell
mc replicate update ALIAS/PATH \
   --id ID \
   --state "disable"|"enable"
```

- 将 [`ALIAS`](#mc.replicate.update.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.update.ALIAS) 替换为该规则所在存储桶或存储桶前缀的路径。
- 将 [`ID`](#mc.replicate.update.-id) 替换为要修改规则的唯一标识符。 使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 获取该存储桶上的复制规则列表及其对应标识符。
- 在 [`--state`](#mc.replicate.update.-state) 标志中指定 `"disable"` 或 `"enable"`，以禁用或启用复制规则。

> [!NOTE]
> **说明**
>
> MinIO 需要启用 [现有对象复制](/docs/administration/bucket-replication/#minio-replication-behavior-existing-objects)，才能同步在禁用复制规则后写入或删除的对象。
>
> 对于 *未* 启用现有对象复制的规则，MinIO 仅同步复制规则处于 *启用* 状态期间发生的写入或删除操作。

## 行为 {#id9}

### 所需权限 {#id10}

MinIO 强烈建议创建专门用于支持存储桶复制操作的用户。 有关向 MinIO 部署添加用户和策略的更完整文档，请参见 [`mc admin user`](/docs/reference/minio-mc-admin/mc-admin-user/#command-mc.admin.user) 和 [`mc admin policy`](/docs/reference/minio-mc-admin/mc-admin-policy/#command-mc.admin.policy)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="复制管理员" value="tab1" >}}
以下策略提供在部署上配置并启用复制所需的权限。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "admin:SetBucketTarget",
                "admin:GetBucketTarget",
                "admin:ListBatchJobs",
                "admin:DescribeBatchJob",
                "admin:StartBatchJob",
                "admin:CancelBatchJob"
            ],
            "Effect": "Allow",
            "Sid": "EnableRemoteBucketConfiguration"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:GetBucketLocation",
                "s3:GetBucketVersioning",
                "s3:GetObjectRetention",
                "s3:GetObjectLegalHold",
                "s3:PutReplicationConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicationRuleConfiguration"
        }
    ]
}

```

- `"EnableRemoteBucketConfiguration"` 语句授予创建远端目标以支持复制的权限。
- `"EnableReplicationRuleConfiguration"` 语句授予在存储桶上创建复制规则的权限。`"arn:aws:s3:::*` 资源将复制权限应用到源部署上的 *任意* 存储桶。你可以按需将用户策略限制到特定存储桶。

使用 [`mc admin policy create`](/docs/reference/minio-mc-admin/mc-admin-policy-create/#command-mc.admin.policy.create) 将该策略添加到每个作为复制源的部署。使用 [`mc admin user add`](/docs/reference/minio-mc-admin/mc-admin-user-add/#command-mc.admin.user.add) 在部署上创建用户，并使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 将该策略关联到该新用户。
{{< /tab >}}
{{< tab label="复制远端用户" value="tab2" >}}
以下策略提供将复制数据同步 *到* 该部署所需的权限。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:GetBucketLocation",
                "s3:GetBucketVersioning",
                "s3:GetBucketObjectLockConfiguration",
                "s3:GetEncryptionConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicationOnBucket"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ReplicateTags",
                "s3:AbortMultipartUpload",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetObjectVersionTagging",
                "s3:PutObject",
                "s3:PutObjectRetention",
                "s3:PutBucketObjectLockConfiguration",
                "s3:PutObjectLegalHold",
                "s3:DeleteObject",
                "s3:ReplicateObject",
                "s3:ReplicateDelete"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicatingDataIntoBucket"
        }
    ]
}
```

- `"EnableReplicationOnBucket"` 语句授予远端目标检索存储桶级配置的权限，以支持对 MinIO 部署中 *所有* 存储桶执行复制操作。 若要将策略限制到特定存储桶，可在 `Resource` 数组中以 `"arn:aws:s3:::bucketName"` 形式指定这些存储桶。
- `"EnableReplicatingDataIntoBucket"` 语句授予远端目标将数据同步到 MinIO 部署中 *任意* 存储桶的权限。 若要将策略限制到特定存储桶，可在 `Resource` 数组中以 `"arn:aws:s3:::bucketName/*"` 形式指定这些存储桶。

使用 [`mc admin policy create`](/docs/reference/minio-mc-admin/mc-admin-policy-create/#command-mc.admin.policy.create) 将该策略添加到每个作为复制目标的部署。使用 [`mc admin user add`](/docs/reference/minio-mc-admin/mc-admin-user-add/#command-mc.admin.user.add) 在部署上创建用户，并使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 将该策略关联到该新用户。
{{< /tab >}}
{{< /tabs >}}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。