---
title: "mc event add"

weight: 10
---

<a id="mc-event-add"></a>
<a id="minio-mc-event-add"></a>

<a id="command-mc.event.add"></a>

## 语法 {#id2}

[`mc event add`](#command-mc.event.add) 命令为存储桶添加事件通知触发器。

MinIO 会将已触发的事件自动发送到已配置的 [notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令为 `myminio` MinIO 部署中的 `mydata` 存储桶上的 所有 `PUT` 和 `DELETE` 操作创建新的事件通知触发器：

```shell
mc event add --event "put,delete" myminio/mydata arn:aws:sqs::primary:target
```

指定的 ARN 对应 `myminio` 部署上已配置的 [bucket notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] event add \
                 [--event "string"]  \
                 [--ignore-existing] \
                 [--prefix "string"] \
                 [--suffix "string"] \
                 ALIAS               \
                 ARN
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.event.add.ALIAS}

*mc-cmd*

*Required*

要添加新事件通知的 MinIO [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶。 例如：

```shell
mc event add play/mybucket
```

##### `ARN` {#mc.event.add.ARN}

*mc-cmd*

*Required*

通知目标的 [Amazon Resource Name (ARN)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns)。

MinIO 服务器启动时会为每个已配置的通知目标输出一个 ARN。 更多信息请参见 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

##### `--event` {#mc.event.add.-event}

*mc-cmd*

*Optional*

MinIO 生成存储桶通知所依据的事件。

支持以下取值：

- `put`
- `get`
- `delete`

使用逗号 `,` 分隔可指定多个值。 值之间不要添加空白字符。

如果未指定，默认值为 `put,delete,get`。

各支持值对应的 S3 事件详见 [支持的存储桶事件](#mc-event-supported-events)。

##### `ignore-existing, p` {#mc.event.add.ignore-existing}

*mc-cmd*

*Optional*

如果已存在匹配的触发器，则指示 MinIO 忽略指定的事件触发器。

##### `--prefix` {#mc.event.add.-prefix}

*mc-cmd*

*Optional*

指定可由 [`--event`](#mc.event.add.-event) 触发存储桶通知的存储桶前缀。

例如，若 [`ALIAS`](#mc.event.add.ALIAS) 为 `play/mybucket` 且 [`--prefix`](#mc.event.add.-prefix) 为 `photos`，则只有 `play/mybucket/photos` 中的事件会触发存储桶通知。

省略该参数时，存储桶中所有前缀和对象的事件都可触发通知。

##### `--suffix` {#mc.event.add.-suffix}

*mc-cmd*

*Optional*

指定可由 [`--event`](#mc.event.add.-event) 触发存储桶通知的存储桶后缀。

例如，若 [`ALIAS`](#mc.event.add.ALIAS) 为 `play/mybucket` 且 [`--suffix`](#mc.event.add.-suffix) 为 `.jpg`，则只有 `play/mybucket/*.jpg` 中的事件会触发存储桶通知。

省略该参数时，无论后缀为何，所有对象的事件都可触发通知。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 为存储桶添加事件通知 {#id6}

{{< tabs group="example-syntax" >}}
{{< tab label="Example" value="example" >}}
以下命令为某个存储桶上的所有 S3 `PUT`、`GET` 和 `DELETE` 操作添加新的事件通知触发器。该命令假设 MinIO 部署中至少已配置一个 [bucket notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)：

```shell
mc event add myminio/mydata arn:minio:sqs::primary:webhook
```
{{< /tab >}}
{{< tab label="Syntax" value="syntax" >}}
```shell
mc event add ALIAS ARN
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和要添加 存储桶通知事件的存储桶。例如：

  `myminio/mydata`
- 将 `ARN` 替换为通知目标 [`ARN`](#mc.event.add.ARN)。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

<a id="id8"></a>

### 支持的存储桶事件 {#mc-event-supported-events}

下表列出了 [`mc event add`](#command-mc.event.add) 支持的取值及其对应的 [S3 events](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications-event-types)：

<table>
  <thead>
    <tr>
      <th><p>Supported Value</p></th>
      <th><p>对应的 S3 事件</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>put</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-CompleteMultipartUpload"><code>s3:ObjectCreated:CompleteMultipartUpload</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-Copy"><code>s3:ObjectCreated:Copy</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-DeleteTagging"><code>s3:ObjectCreated:DeleteTagging</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-Post"><code>s3:ObjectCreated:Post</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-Put"><code>s3:ObjectCreated:Put</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-PutLegalHold"><code>s3:ObjectCreated:PutLegalHold</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-PutRetention"><code>s3:ObjectCreated:PutRetention</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectCreated-PutTagging"><code>s3:ObjectCreated:PutTagging</code></a><br /></td>
    </tr>
    <tr>
      <td><p><code>get</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectAccessed-Head"><code>s3:ObjectAccessed:Head</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectAccessed-Get"><code>s3:ObjectAccessed:Get</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectAccessed-GetRetention"><code>s3:ObjectAccessed:GetRetention</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectAccessed-GetLegalHold"><code>s3:ObjectAccessed:GetLegalHold</code></a><br /></td>
    </tr>
    <tr>
      <td><p><code>delete</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectRemoved-Delete"><code>s3:ObjectRemoved:Delete</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectRemoved-DeleteMarkerCreated"><code>s3:ObjectRemoved:DeleteMarkerCreated</code></a><br /></td>
    </tr>
    <tr>
      <td><p><code>replica</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Replication-OperationCompletedReplication"><code>s3:Replication:OperationCompletedReplication</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Replication-OperationFailedReplication"><code>s3:Replication:OperationFailedReplication</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Replication-OperationMissedThreshold"><code>s3:Replication:OperationMissedThreshold</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Replication-OperationNotTracked"><code>s3:Replication:OperationNotTracked</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Replication-OperationReplicatedAfterThreshold"><code>s3:Replication:OperationReplicatedAfterThreshold</code></a><br /></td>
    </tr>
    <tr>
      <td><p><code>ilm</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectTransition-Failed"><code>s3:ObjectTransition:Failed</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectTransition-Complete"><code>s3:ObjectTransition:Complete</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectRestore-Post"><code>s3:ObjectRestore:Post</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-ObjectRestore-Completed"><code>s3:ObjectRestore:Completed</code></a><br /></td>
    </tr>
    <tr>
      <td><p><code>scanner</code></p></td>
      <td><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Scanner-ManyVersions"><code>s3:Scanner:ManyVersions</code></a><br /><a href="/docs/administration/monitoring/bucket-notifications/#data.s3-Scanner-BigPrefix"><code>s3:Scanner:BigPrefix</code></a><br /></td>
    </tr>
  </tbody>
</table>

有关上述 S3 事件的更完整文档，请参见 [S3 Supported Event Types](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html#notification-how-to-event-types-and-destinations)。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。