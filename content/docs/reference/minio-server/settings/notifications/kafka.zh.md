---
title: "Kafka 通知设置"

weight: 30
---

<a id="kafka"></a>
<a id="minio-server-config-bucket-notification-kafka"></a>
<a id="minio-server-envvar-bucket-notification-kafka"></a>

本页面记录了将 Kafka 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的相关设置。 有关如何使用这些设置的教程，请参见 [将事件发布到 Kafka](/docs/administration/monitoring/publish-events-to-kafka/#minio-bucket-notifications-publish-kafka)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 Kafka 目标 {#id2}

你可以在顶层键后附加唯一标识符 `_ID`，为每组相关的 Kafka 设置指定多个 Kafka 服务端点。

### 示例 {#id3}

例如，以下命令分别将两个不同的 Kafka 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
```shell
export MINIO_NOTIFY_KAFKA_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_KAFKA_BROKERS_PRIMARY="https://kafka1.example.net:9200, https://kafka2.example.net:9200"

export MINIO_NOTIFY_KAFKA_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_KAFKA_BROKERS_SECONDARY="https://kafka1.example.net:9200, https://kafka2.example.net:9200"
```
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
```shell
mc admin config set notify_kafka:primary \
   brokers="https://kafka1.example.net:9200, https://kafka2.example.net:9200"
   [ARGUMENT=VALUE ...]

mc admin config set notify_kafka:secondary \
   brokers="https://kafka1.example.net:9200, https://kafka2.example.net:9200"
   [ARGUMENT=VALUE ...]
```

请注意，对于配置设置，唯一标识符只附加到 `notify_kafka`，而不是附加到每个单独参数。
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id4}

### 启用 {#id5}

*必需*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_ENABLE` {#envvar.MINIO_NOTIFY_KAFKA_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 Kafka 服务端点。

默认为 `off`。
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka` {#mc-conf.notify_kafka}

*mc-conf*

用于定义 Kafka 服务端点并与 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 配合使用的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 Kafka 服务端点。 对于每个目标，[`brokers`](#mc-conf.notify_kafka.brokers) 参数都是 *必需* 的。 其他可选参数请以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set notify_kafka \
  brokers="https://kafka1.example.net:9200, https://kafka2.example.net:9200"
  [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### Brokers {#brokers}

*必需*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_BROKERS` {#envvar.MINIO_NOTIFY_KAFKA_BROKERS}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka brokers` {#mc-conf.notify_kafka.brokers}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定以逗号分隔的 Kafka broker 地址列表。 例如：

`"kafka1.example.com:2021,kafka2.example.com:2021"`

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### Topic {#topic}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_TOPIC` {#envvar.MINIO_NOTIFY_KAFKA_TOPIC}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka topic` {#mc-conf.notify_kafka.topic}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布存储桶事件的 Kafka topic 名称。

### SASL {#sasl}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_SASL` {#envvar.MINIO_NOTIFY_KAFKA_SASL}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka sasl` {#mc-conf.notify_kafka.sasl}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用 SASL 身份验证。

### SASL Username {#sasl-username}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_SASL_USERNAME` {#envvar.MINIO_NOTIFY_KAFKA_SASL_USERNAME}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka sasl_username` {#mc-conf.notify_kafka.sasl_username}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于对 Kafka broker 执行 SASL/PLAIN 或 SASL/SCRAM 身份验证的用户名。

### SASL Password {#sasl-password}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_SASL_PASSWORD` {#envvar.MINIO_NOTIFY_KAFKA_SASL_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka sasl_password` {#mc-conf.notify_kafka.sasl_password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于对 Kafka broker 执行 SASL/PLAIN 或 SASL/SCRAM 身份验证的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当此值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时，MinIO 会对其进行脱敏。

### SASL Mechanism {#sasl-mechanism}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_SASL_MECHANISM` {#envvar.MINIO_NOTIFY_KAFKA_SASL_MECHANISM}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka sasl_mechanism` {#mc-conf.notify_kafka.sasl_mechanism}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于对 Kafka broker 进行身份验证的 SASL 机制。 MinIO 支持以下机制：

- `PLAIN`（默认）
- `SHA256`
- `SHA512`

### TLS Client Auth {#tls-client-auth}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_TLS_CLIENT_AUTH` {#envvar.MINIO_NOTIFY_KAFKA_TLS_CLIENT_AUTH}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka tls_client_auth` {#mc-conf.notify_kafka.tls_client_auth}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Kafka broker 的客户端身份验证类型。 下表列出了支持的取值及其映射关系

| 值 | 身份验证类型 |
| --- | --- |
| 0 | `NoClientCert` |
| 1 | `RequestClientCert` |
| 2 | `RequireAnyClientCert` |
| 3 | `VerifyClientCertIfGiven` |
| 4 | `RequireAndVerifyClientCert` |

有关各客户端身份验证类型的更多信息，请参见 [ClientAuthType](https://golang.org/pkg/crypto/tls/#ClientAuthType)。

### TLS {#tls}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_TLS` {#envvar.MINIO_NOTIFY_KAFKA_TLS}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka tls` {#mc-conf.notify_kafka.tls}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用与 Kafka broker 的 TLS 连接。

### TLS Skip Verify {#tls-skip-verify}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_TLS_SKIP_VERIFY` {#envvar.MINIO_NOTIFY_KAFKA_TLS_SKIP_VERIFY}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka tls_skip_verify` {#mc-conf.notify_kafka.tls_skip_verify}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

启用或禁用对 NATS 服务端点 TLS 证书的 TLS 验证。

- 指定 `on` 以禁用 TLS 验证（*默认*）。
- 指定 `off` 以启用 TLS 验证。

### Client TLS Cert {#client-tls-cert}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_CLIENT_TLS_CERT` {#envvar.MINIO_NOTIFY_KAFKA_CLIENT_TLS_CERT}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka client_tls_cert` {#mc-conf.notify_kafka.client_tls_cert}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定客户端证书路径，用于对 Kafka broker 执行 mTLS 身份验证。

### Client TLS Key {#client-tls-key}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_CLIENT_TLS_KEY` {#envvar.MINIO_NOTIFY_KAFKA_CLIENT_TLS_KEY}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka client_tls_key` {#mc-conf.notify_kafka.client_tls_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定客户端私钥路径，用于对 Kafka broker 执行 mTLS 身份验证。

### Version {#version}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_VERSION` {#envvar.MINIO_NOTIFY_KAFKA_VERSION}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka version` {#mc-conf.notify_kafka.version}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定在对 Kafka 集群执行操作时假定的 Kafka 集群版本。 有关此字段行为的更多信息，请参见 [sarama reference documentation](https://github.com/shopify/sarama/blob/v1.20.1/config.go#L327)。

### Batch Size {#batch-size}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_BATCH_SIZE` {#envvar.MINIO_NOTIFY_KAFKA_BATCH_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka batch_size` {#mc-conf.notify_kafka.batch_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定整数值，作为向 Kafka 发送记录时的 [batch size](https://kafka.apache.org/documentation/#producerconfigs_batch.size)。

> [!NOTE]
> **变更: RELEASE.2023-12-02T10-51-33Z**
>
> MinIO 先前将此值限制为 `100`。

### Queue Directory {#queue-directory}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_QUEUE_DIR` {#envvar.MINIO_NOTIFY_KAFKA_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka queue_dir` {#mc-conf.notify_kafka.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 Kafka server/broker 离线时，MinIO 会将未投递事件存储在指定存储中，并在连接恢复后重放这些已存储事件。

### Queue Limit {#queue-limit}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_KAFKA_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka queue_limit` {#mc-conf.notify_kafka.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大限制。 默认为 `100000`。

### Comment {#comment}

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_COMMENT` {#envvar.MINIO_NOTIFY_KAFKA_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka comment` {#mc-conf.notify_kafka.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 Kafka 配置关联的注释。

### Compression Codec {#compression-codec}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2023-12-09T18-17-51Z

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_PRODUCER_COMPRESSION_CODEC` {#envvar.MINIO_NOTIFY_KAFKA_PRODUCER_COMPRESSION_CODEC}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka compression_codec` {#mc-conf.notify_kafka.compression_codec}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定向 Kafka 发送记录时使用的压缩编解码器。

支持以下取值：

- `none`
- `snappy`
- `gzip`
- `lz4`
- `zstd`

### Compression Level {#compression-level}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2023-12-09T18-17-51Z

*可选*

{{< tabs group="environment-variable-configuration-setting" >}}
{{< tab label="Environment Variable" value="environment-variable" >}}
##### `MINIO_NOTIFY_KAFKA_PRODUCER_COMPRESSION_LEVEL` {#envvar.MINIO_NOTIFY_KAFKA_PRODUCER_COMPRESSION_LEVEL}

*envvar*
{{< /tab >}}
{{< tab label="Configuration Setting" value="configuration-setting" >}}
##### `notify_kafka compression_level` {#mc-conf.notify_kafka.compression_level}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

根据已配置的压缩编解码器控制应用的压缩级别。

指定大于或等于 `0` 的整数值。 该值的效果取决于所选编解码器。