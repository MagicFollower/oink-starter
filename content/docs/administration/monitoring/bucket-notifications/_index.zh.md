---
title: "存储桶通知"

weight: 10
icon: fa-solid fa-bell
---

<a id="minio-bucket-notifications"></a>
<a id="id1"></a>

MinIO 存储桶通知允许管理员在特定对象或存储桶事件发生时，将通知发送到受支持的外部服务。 MinIO 支持与 [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) 类似的存储桶级和对象级 S3 事件。

## 支持的通知目标 {#id3}

MinIO 支持将事件通知发布到以下目标：

<table>
  <thead>
    <tr>
      <th><p>目标</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>AMQP (RabbitMQ)</p></td>
      <td><p>将通知发布到 AMQP 服务，例如
<a href="https://www.rabbitmq.com">RabbitMQ</a>.</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-amqp/#minio-bucket-notifications-publish-amqp">将事件发布到 AMQP (RabbitMQ)</a>。</p></td>
    </tr>
    <tr>
      <td><p>MQTT</p></td>
      <td><p>将通知发布到 <a href="https://www.mqtt.org/">MQTT</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-mqtt/#minio-bucket-notifications-publish-mqtt">将事件发布到 MQTT</a>。</p></td>
    </tr>
    <tr>
      <td><p>NATS</p></td>
      <td><p>将通知发布到 <a href="https://nats.io/">NATS</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-nats/#minio-bucket-notifications-publish-nats">将事件发布到 NATS</a>。</p></td>
    </tr>
    <tr>
      <td><p>NSQ</p></td>
      <td><p>将通知发布到 <a href="https://nsq.io/">NSQ</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-nsq/#minio-bucket-notifications-publish-nsq">将事件发布到 NSQ</a></p></td>
    </tr>
    <tr>
      <td><p>Elasticsearch</p></td>
      <td><p>将通知发布到 <a href="https://www.elastic.co/">Elasticsearch</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-elasticsearch/#minio-bucket-notifications-publish-elasticsearch">将事件发布到 Elasticsearch</a>。</p></td>
    </tr>
    <tr>
      <td><p>Kafka</p></td>
      <td><p>将通知发布到 <a href="https://kafka.apache.org/">Kafka</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-kafka/#minio-bucket-notifications-publish-kafka">将事件发布到 Kafka</a>。</p></td>
    </tr>
    <tr>
      <td><p>MySQL</p></td>
      <td><p>将通知发布到 <a href="https://www.mysql.com/">MySQL</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-mysql/#minio-bucket-notifications-publish-mysql">将事件发布到 MySQL</a>。</p></td>
    </tr>
    <tr>
      <td><p>PostgreSQL</p></td>
      <td><p>将通知发布到 <a href="https://www.postgresql.org/">PostgreSQL</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-postgresql/#minio-bucket-notifications-publish-postgresql">将事件发布到 PostgreSQL</a>。</p></td>
    </tr>
    <tr>
      <td><p>Redis</p></td>
      <td><p>将通知发布到 <a href="https://redis.io/">Redis</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-redis/#minio-bucket-notifications-publish-redis">将事件发布到 Redis</a>。</p></td>
    </tr>
    <tr>
      <td><p>webhook</p></td>
      <td><p>将通知发布到 <a href="https://en.wikipedia.org/wiki/Webhook">Webhook</a> 服务。</p><p>教程参见 <a href="/docs/administration/monitoring/publish-events-to-webhook/#minio-bucket-notifications-publish-webhook">将事件发布到 Webhook</a>。</p></td>
    </tr>
  </tbody>
</table>

## 异步与同步存储桶通知 {#id4}

> [!NOTE]
> **新增: RELEASE.2023-06-23T20-26-00Z**
>
> 对于 *所有* 远程目标，MinIO 支持异步（默认）或同步存储桶通知。

使用异步传递时，MinIO 会将事件发送到已配置的远程目标，并且在继续处理下一个事件之前 *不会* 等待响应。 异步存储桶通知优先保证发送速率，但如果远程目标在传输或处理期间出现瞬时问题，则存在部分事件丢失的风险。

使用同步传递时，MinIO 会将事件发送到已配置的远程目标，然后等待远程目标确认已成功接收后，才继续处理下一个事件。 同步存储桶通知优先保证事件可送达，但代价是事件发送速率较慢且队列更容易被填满。

要为 *所有已配置的远程目标* 启用同步存储桶通知，请使用以下任一设置：

- 将 [`MINIO_API_SYNC_EVENTS`](/docs/reference/minio-server/settings/notifications/#envvar.MINIO_API_SYNC_EVENTS) 环境变量设置为 `on`，然后重启 MinIO 部署。
- 将 [`api.sync_events`](/docs/reference/minio-server/settings/notifications/#mc-conf.api.sync_events) 配置项设置为 `on`，然后重启 MinIO 部署。

> [!NOTE]
> **说明**
>
> 对于同步和异步事件，MinIO 都会为每个远程目标维护一个队列，用于存储尚未发送和待处理的事件。 队列上限默认为 `100000`。
>
> 队列已满时，MinIO 会丢弃新事件。
>
> 可按需增大队列大小，以更好地适配 MinIO 部署与远程目标的事件发送和处理速率。 使用对应通知方法的 `QUEUE_LIMIT` 环境变量或配置项来修改该限制。
>
> 对于异步事件，MinIO 最多允许 `50000` 个并发 `send` 调用。

<a id="minio-bucket-notifications-event-types"></a>

## 支持的 S3 事件类型 {#s3}

MinIO 存储桶通知与 [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) 兼容。 本节列出所有受支持的事件。

### 对象事件 {#id5}

MinIO 支持在以下 S3 对象事件上触发通知：

<a id="data.s3:ObjectAccessed:Get"></a>

##### `s3:ObjectAccessed:Get` {#data.s3-ObjectAccessed-Get}

*data*

<a id="data.s3:ObjectAccessed:GetLegalHold"></a>

##### `s3:ObjectAccessed:GetLegalHold` {#data.s3-ObjectAccessed-GetLegalHold}

*data*

<a id="data.s3:ObjectAccessed:GetRetention"></a>

##### `s3:ObjectAccessed:GetRetention` {#data.s3-ObjectAccessed-GetRetention}

*data*

<a id="data.s3:ObjectAccessed:Head"></a>

##### `s3:ObjectAccessed:Head` {#data.s3-ObjectAccessed-Head}

*data*

<a id="data.s3:ObjectCreated:CompleteMultipartUpload"></a>

##### `s3:ObjectCreated:CompleteMultipartUpload` {#data.s3-ObjectCreated-CompleteMultipartUpload}

*data*

<a id="data.s3:ObjectCreated:Copy"></a>

##### `s3:ObjectCreated:Copy` {#data.s3-ObjectCreated-Copy}

*data*

<a id="data.s3:ObjectCreated:DeleteTagging"></a>

##### `s3:ObjectCreated:DeleteTagging` {#data.s3-ObjectCreated-DeleteTagging}

*data*

<a id="data.s3:ObjectCreated:Post"></a>

##### `s3:ObjectCreated:Post` {#data.s3-ObjectCreated-Post}

*data*

<a id="data.s3:ObjectCreated:Put"></a>

##### `s3:ObjectCreated:Put` {#data.s3-ObjectCreated-Put}

*data*

<a id="data.s3:ObjectCreated:PutLegalHold"></a>

##### `s3:ObjectCreated:PutLegalHold` {#data.s3-ObjectCreated-PutLegalHold}

*data*

<a id="data.s3:ObjectCreated:PutRetention"></a>

##### `s3:ObjectCreated:PutRetention` {#data.s3-ObjectCreated-PutRetention}

*data*

<a id="data.s3:ObjectCreated:PutTagging"></a>

##### `s3:ObjectCreated:PutTagging` {#data.s3-ObjectCreated-PutTagging}

*data*

<a id="data.s3:ObjectRemoved:Delete"></a>

##### `s3:ObjectRemoved:Delete` {#data.s3-ObjectRemoved-Delete}

*data*

<a id="data.s3:ObjectRemoved:DeleteMarkerCreated"></a>

##### `s3:ObjectRemoved:DeleteMarkerCreated` {#data.s3-ObjectRemoved-DeleteMarkerCreated}

*data*

指定通配符 `*` 可选择与某个前缀相关的所有事件：

<a id="data.s3:ObjectAccessed:*"></a>

##### `s3:ObjectAccessed:*` {#data.s3-ObjectAccessed}

*data*

选择所有以 `s3:ObjectAccessed` 为前缀的事件。

<a id="data.s3:ObjectCreated:*"></a>

##### `s3:ObjectCreated:*` {#data.s3-ObjectCreated}

*data*

选择所有以 `s3:ObjectCreated` 为前缀的事件。

<a id="data.s3:ObjectRemoved:*"></a>

##### `s3:ObjectRemoved:*` {#data.s3-ObjectRemoved}

*data*

选择所有以 `s3:ObjectRemoved` 为前缀的事件。

### 复制事件 {#id6}

MinIO 支持在以下 S3 复制事件上触发通知：

<a id="data.s3:Replication:OperationCompletedReplication"></a>

##### `s3:Replication:OperationCompletedReplication` {#data.s3-Replication-OperationCompletedReplication}

*data*

<a id="data.s3:Replication:OperationFailedReplication"></a>

##### `s3:Replication:OperationFailedReplication` {#data.s3-Replication-OperationFailedReplication}

*data*

<a id="data.s3:Replication:OperationMissedThreshold"></a>

##### `s3:Replication:OperationMissedThreshold` {#data.s3-Replication-OperationMissedThreshold}

*data*

<a id="data.s3:Replication:OperationNotTracked"></a>

##### `s3:Replication:OperationNotTracked` {#data.s3-Replication-OperationNotTracked}

*data*

<a id="data.s3:Replication:OperationReplicatedAfterThreshold"></a>

##### `s3:Replication:OperationReplicatedAfterThreshold` {#data.s3-Replication-OperationReplicatedAfterThreshold}

*data*

指定通配符 `*` 可选择所有 `s3:Replication` 事件：

<a id="data.s3:Replication:*"></a>

##### `s3:Replication:*` {#data.s3-Replication}

*data*

### ILM 转换事件 {#ilm}

MinIO 支持在以下 S3 ILM 转换事件上触发通知：

<a id="data.s3:ObjectRestore:Post"></a>

##### `s3:ObjectRestore:Post` {#data.s3-ObjectRestore-Post}

*data*

<a id="data.s3:ObjectRestore:Completed"></a>

##### `s3:ObjectRestore:Completed` {#data.s3-ObjectRestore-Completed}

*data*

<a id="data.s3:ObjectTransition:Failed"></a>

##### `s3:ObjectTransition:Failed` {#data.s3-ObjectTransition-Failed}

*data*

<a id="data.s3:ObjectTransition:Complete"></a>

##### `s3:ObjectTransition:Complete` {#data.s3-ObjectTransition-Complete}

*data*

指定通配符 `*` 可选择与某个前缀相关的所有事件：

<a id="data.s3:ObjectTransition:*"></a>

##### `s3:ObjectTransition:*` {#data.s3-ObjectTransition}

*data*

选择所有以 `s3:ObjectTransition` 为前缀的事件。

<a id="data.s3:ObjectRestore:*"></a>

##### `s3:ObjectRestore:*` {#data.s3-ObjectRestore}

*data*

选择所有以 `s3:ObjectRestore` 为前缀的事件。

### Scanner 事件 {#scanner}

MinIO 支持在以下 S3 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 转换事件上触发通知：

<a id="data.s3:Scanner:ManyVersions"></a>

##### `s3:Scanner:ManyVersions` {#data.s3-Scanner-ManyVersions}

*data*

[Scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 发现具有超过 1,000 个版本的对象。

<a id="data.s3:Scanner:BigPrefix"></a>

##### `s3:Scanner:BigPrefix` {#data.s3-Scanner-BigPrefix}

*data*

[Scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 发现具有超过 50,000 个子文件夹的前缀。

### 全局事件 {#id7}

MinIO 支持在以下全局事件上触发通知。 只能通过 [ListenNotification](https://pkg.go.dev/github.com/minio/minio-go/v7#Client.ListenNotification) API 监听这些事件：

<a id="data.s3:BucketCreated"></a>

##### `s3:BucketCreated` {#data.s3-BucketCreated}

*data*

<a id="data.s3:BucketRemoved"></a>

##### `s3:BucketRemoved` {#data.s3-BucketRemoved}

*data*

## 负载模式 {#id8}

所有通知负载都使用相同的整体模式。 根据通知类型的不同，某些字段可能会省略或为 null。

```json
{
    "eventVersion": "string",
    "eventSource": "string",
    "awsRegion": "string",
    "eventTime": "string",
    "eventName": "string",
    "userIdentity": {
        "principalId": "string"
    },
    "requestParameters": {
        "key": "value"
    },
    "responseElements": {
        "key": "value"
    },
    "s3": {
        "s3SchemaVersion": "string",
        "configurationId": "string",
        "bucket": {
            "name": "string",
            "ownerIdentity": {
                "principalId": "string"
            },
            "arn": "string"
        },
        "object": {
            "key": "string",
            "size": 10000,
            "eTag": "string",
            "contentType": "string",
            "userMetadata": {
                "key": "string"
            },
            "versionId": "string",
            "sequencer": "string"
        }
    },
    "source": {
        "host": "string",
        "port": "string",
        "userAgent": "string"
    }
}
```

### 示例 {#id9}

以下示例是 `s3:ObjectCreated:Put` 事件的通知：

```json
{
  "EventName": "s3:ObjectCreated:Put",
  "Key": "test-bucket/image.jpg",
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "minio:s3",
      "awsRegion": "",
      "eventTime": "2025-02-06T01:04:31.998Z",
      "eventName": "s3:ObjectCreated:Put",
      "userIdentity": {
        "principalId": "access_key"
      },
      "requestParameters": {
        "principalId": "access_key",
        "region": "",
        "sourceIPAddress": "192.168.1.10"
      },
      "responseElements": {
        "x-amz-id-2": "dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8",
        "x-amz-request-id": "182178E8B36AC9DF",
        "x-minio-deployment-id": "2369dcb4-348b-4d30-8fc9-61ab089ba4bc",
        "x-minio-origin-endpoint": "https://minio.test.svc.cluster.local"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "Config",
        "bucket": {
          "name": "test-bucket",
          "ownerIdentity": {
            "principalId": "access_key"
          },
          "arn": "arn:aws:s3:::test-bucket"
        },
        "object": {
          "key": "image.jpg",
          "size": 84452,
          "eTag": "eb52f8e46f60a27a8a1a704e25757f30",
          "contentType": "image/jpeg",
          "userMetadata": {
            "content-type": "image/jpeg"
          },
          "sequencer": "182178E8B3728CAC"
        }
      },
      "source": {
        "host": "192.168.1.10",
        "port": "",
        "userAgent": "MinIO (linux; amd64) minio-go/v7.0.83"
      }
    }
  ]
}
```