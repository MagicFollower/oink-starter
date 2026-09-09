---
title: "NATS 通知设置"

weight: 60
---

<a id="nats"></a>
<a id="minio-server-config-bucket-notification-nats"></a>
<a id="minio-server-envvar-bucket-notification-nats"></a>

> [!NOTE]
> **NATS Streaming 已弃用**
>
> NATS Streaming 已弃用。 请迁移到 [JetStream](https://docs.nats.io/nats-concepts/jetstream)。
>
> 相关的 MinIO 配置选项和环境变量也已弃用。

本页面说明了将 NATS 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的设置。 有关如何使用这些设置的教程，请参见 [将事件发布到 NATS](/docs/administration/monitoring/publish-events-to-nats/#minio-bucket-notifications-publish-nats)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 NATS 目标 {#id2}

你可以在顶层键后追加唯一标识符 `_ID`，为每组相关的 NATS 设置指定多个 NATS 服务端点。

### 示例 {#id3}

例如，以下命令分别将两个不同的 NATS 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
export MINIO_NOTIFY_NATS_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_NATS_ADDRESS_PRIMARY="nats-endpoint.example.net:4222"

export MINIO_NOTIFY_NATS_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_NATS_ADDRESS_SECONDARY="nats-endpoint.example.net:4222"
```

在这些设置中，[`MINIO_NOTIFY_NATS_ENABLE_PRIMARY`](#envvar.MINIO_NOTIFY_NATS_ENABLE) 表示该环境变量关联到 ID 为 `PRIMARY` 的 NATS 服务端点。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
```shell
mc admin config set notify_nats:primary \
   address="nats-endpoint.example.com:4222" \
   subject="minioevents" \
   [ARGUMENT=VALUE ...]

mc admin config set notify_nats:secondary \
   address="nats-endpoint.example.com:4222" \
   subject="minioevents" \
   [ARGUMENT=VALUE ...]
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id4}

### 启用 {#id5}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_ENABLE` {#envvar.MINIO_NOTIFY_NATS_ENABLE}

*envvar*

指定 `on` 以启用向 NATS 服务端点发布存储桶通知。

默认为 `off`。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats` {#mc-conf.notify_nats}

*mc-conf*

用于定义 NATS 服务端点并将其用于 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 NATS 服务端点。 对于每个目标，[`address`](#mc-conf.notify_nats.address) 和 [`subject`](#mc-conf.notify_nats.subject) 参数均为 *必填*。 其他可选参数请使用空白字符（`" "`）分隔的列表指定。

```shell
mc admin config set notify_nats \
  address="nats-endpoint.example.com:4222" \
  subject="minioevents" \
  [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### 地址 {#id6}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_ADDRESS` {#envvar.MINIO_NOTIFY_NATS_ADDRESS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats address` {#mc-conf.notify_nats.address}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布存储桶事件到的 NATS 服务端点。 例如：`nats-endpoint.example.com:4222`。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### Subject {#subject}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_SUBJECT` {#envvar.MINIO_NOTIFY_NATS_SUBJECT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats subject` {#mc-conf.notify_nats.subject}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在 NATS 端点上关联已发布事件的订阅。

### 用户名 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_USERNAME` {#envvar.MINIO_NOTIFY_NATS_USERNAME}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats username` {#mc-conf.notify_nats.username}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定连接到 NATS 服务端点时使用的用户名。

### 密码 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_PASSWORD` {#envvar.MINIO_NOTIFY_NATS_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats password` {#mc-conf.notify_nats.password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定连接到 NATS 服务端点时使用的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> MinIO 在作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时会对该值进行脱敏。

### Token {#token}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_TOKEN` {#envvar.MINIO_NOTIFY_NATS_TOKEN}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats token` {#mc-conf.notify_nats.token}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定连接到 NATS 服务端点时使用的 token。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> MinIO 在作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时会对该值进行脱敏。

### 用户凭证文件 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_USER_CREDENTIALS` {#envvar.MINIO_NOTIFY_NATS_USER_CREDENTIALS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats user_credentials` {#mc-conf.notify_nats.user_credentials}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于连接 NATS 服务端点的 [user credentials file](https://docs.nats.io/using-nats/developer/connecting/creds)。

### TLS {#tls}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_TLS` {#envvar.MINIO_NOTIFY_NATS_TLS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats tls` {#mc-conf.notify_nats.tls}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用到 NATS 服务端点的 TLS 连接。

### TLS Skip Verify {#tls-skip-verify}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_TLS_SKIP_VERIFY` {#envvar.MINIO_NOTIFY_NATS_TLS_SKIP_VERIFY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats tls_skip_verify` {#mc-conf.notify_nats.tls_skip_verify}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

启用或禁用对 NATS 服务端点 TLS 证书的 TLS 校验。

- 指定 `on` 以禁用 TLS 校验（默认）。
- 指定 `off` 以启用 TLS 校验。

### Ping Interval {#ping-interval}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_PING_INTERVAL` {#envvar.MINIO_NOTIFY_NATS_PING_INTERVAL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats ping_interval` {#mc-conf.notify_nats.ping_interval}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定客户端向 NATS 服务器发送 ping 的时间间隔。 MinIO 支持以下时间单位：

- `s` - 秒，`"60s"`
- `m` - 分钟，`"5m"`
- `h` - 小时，`"1h"`
- `d` - 天，`"1d"`

### Jetstream {#jetstream}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_JETSTREAM` {#envvar.MINIO_NOTIFY_NATS_JETSTREAM}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats jetstream` {#mc-conf.notify_nats.jetstream}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用 JetStream 支持，将事件流式传输到 NATS JetStream 服务端点。

### Streaming {#streaming}

*已弃用*

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_STREAMING` {#envvar.MINIO_NOTIFY_NATS_STREAMING}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats streaming` {#mc-conf.notify_nats.streaming}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用向 NATS 服务端点异步发布事件。

### Streaming Async {#streaming-async}

*已弃用*

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_STREAMING_ASYNC` {#envvar.MINIO_NOTIFY_NATS_STREAMING_ASYNC}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats streaming_async` {#mc-conf.notify_nats.streaming_async}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用向 NATS 服务端点异步发布事件。

### Max ACK Responses In Flight {#max-ack-responses-in-flight}

*已弃用*

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_STREAMING_MAX_PUB_ACKS_IN_FLIGHT` {#envvar.MINIO_NOTIFY_NATS_STREAMING_MAX_PUB_ACKS_IN_FLIGHT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats streaming_max_pub_acks_in_flight` {#mc-conf.notify_nats.streaming_max_pub_acks_in_flight}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定在等待 NATS 服务端点 ACK 响应之前可发布的消息数量。

### Streaming Cluster ID {#streaming-cluster-id}

*已弃用*

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_STREAMING_CLUSTER_ID` {#envvar.MINIO_NOTIFY_NATS_STREAMING_CLUSTER_ID}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats streaming_cluster_id` {#mc-conf.notify_nats.streaming_cluster_id}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 NATS Streaming 集群的唯一 ID。

### Cert Authority {#cert-authority}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_CERT_AUTHORITY` {#envvar.MINIO_NOTIFY_NATS_CERT_AUTHORITY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats cert_authority` {#mc-conf.notify_nats.cert_authority}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于签署 NATS 服务端点 TLS 证书的 Certificate Authority 证书链路径。

### Client Cert {#client-cert}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_CLIENT_CERT` {#envvar.MINIO_NOTIFY_NATS_CLIENT_CERT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats client_cert` {#mc-conf.notify_nats.client_cert}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于执行到 NATS 服务端点 mTLS 认证的客户端证书路径。

### Client Key {#client-key}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_CLIENT_KEY` {#envvar.MINIO_NOTIFY_NATS_CLIENT_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats client_key` {#mc-conf.notify_nats.client_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于执行到 NATS 服务端点 mTLS 认证的客户端私钥路径。

### Queue Directory {#queue-directory}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_QUEUE_DIR` {#envvar.MINIO_NOTIFY_NATS_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats queue_dir` {#mc-conf.notify_nats.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 NATS server/broker 离线时，MinIO 会将未投递事件存储在指定存储中，并在连接恢复后重放已存储事件。

### Queue Limit {#queue-limit}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_NATS_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats queue_limit` {#mc-conf.notify_nats.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认为 `100000`。

### Comment {#comment}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NATS_COMMENT` {#envvar.MINIO_NOTIFY_NATS_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nats comment` {#mc-conf.notify_nats.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 NATS 配置关联的注释。