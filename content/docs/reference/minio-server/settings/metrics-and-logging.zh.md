---
title: "指标与日志设置"

weight: 60
---

<a id="minio-server-envvar-metrics-logging"></a>
<a id="id1"></a>

本页面介绍用于控制 MinIO 指标与日志相关行为的设置。 更多信息请参见 [指标与告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)。

这些设置用于将常规 [`minio server`](/docs/reference/minio-server/#command-minio.server) 日志和审计日志发布到 HTTP webhook。 更完整的文档请参见 [将服务日志或审计日志发布到外部服务](/docs/operations/monitoring/minio-logging/#minio-logging)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

- [服务器日志](#minio-server-envvar-logging-regular)
- [Webhook 审计日志](#minio-server-envvar-logging-audit)
- [Kafka 审计日志](#minio-server-envvar-logging-audit-kafka)

## Prometheus 认证 {#prometheus}

此设置控制 MinIO 如何向 Prometheus 进行认证。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_PROMETHEUS_AUTH_TYPE` {#envvar.MINIO_PROMETHEUS_AUTH_TYPE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

指定 Prometheus [抓取端点](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts) 的认证模式。

- **`jwt` - *默认* MinIO 要求抓取客户端提供 JWT token 以认证请求。**

  > 使用 [`mc admin prometheus generate`](/docs/reference/minio-mc-admin/mc-admin-prometheus-generate/#command-mc.admin.prometheus.generate) 生成所需的 JWT bearer token。
- `public` MinIO 不要求抓取客户端对其请求进行认证。

<a id="minio-server-envvar-logging-regular"></a>
<a id="id3"></a>

## 服务器日志 {#minio-server-config-logging-regular}

以下部分介绍将 [`minio server`](/docs/reference/minio-server/#command-minio.server) 日志发布到 HTTP webhook 端点的 MinIO 配置设置。 有关这些设置的更完整文档和使用教程，请参见 [将服务日志发布到 HTTP Webhook](/docs/operations/monitoring/minio-logging/#minio-logging-publish-server-logs)。

### 定义多个端点 {#id4}

你可以通过为每组相关日志环境变量追加唯一标识符 `_ID`，将多个 webhook 端点指定为日志目标。 例如，以下设置定义了两个不同的服务器日志 webhook 端点：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_LOGGER_WEBHOOK_ENABLE_PRIMARY="on"
export MINIO_LOGGER_WEBHOOK_AUTH_TOKEN_PRIMARY="TOKEN"
export MINIO_LOGGER_WEBHOOK_ENDPOINT_PRIMARY="http://webhook-1.example.net"

export MINIO_LOGGER_WEBHOOK_ENABLE_SECONDARY="on"
export MINIO_LOGGER_WEBHOOK_AUTH_TOKEN_SECONDARY="TOKEN"
export MINIO_LOGGER_WEBHOOK_ENDPOINT_SECONDARY="http://webhook-2.example.net"
```

```shell {tab="配置项" value="tab2"}
mc admin config set logger_webhook:primary \
   endpoint="http://webhook-01.example.net" [ARGUMENTS=VALUE ...]

mc admin config set logger_webhook:secondary \
   endpoint="http://webhook-02.example.net" [ARGUMENTS=VALUE ...]
```

### 设置 {#id5}

#### Enable {#enable}

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_ENABLE` {#envvar.MINIO_LOGGER_WEBHOOK_ENABLE}

*envvar*

指定 `"on"` 以启用将 [`minio server`](/docs/reference/minio-server/#command-minio.server) 日志发布到 HTTP webhook 端点。

需要同时指定 [`MINIO_LOGGER_WEBHOOK_ENDPOINT`](#envvar.MINIO_LOGGER_WEBHOOK_ENDPOINT)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook` {#mc-conf.logger_webhook}

*mc-conf*

用于配置将日志发送到 HTTP webhook 端点的顶层配置键。
{{< /tab >}}
{{< /tabs >}}

#### 端点 {#id6}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_ENDPOINT` {#envvar.MINIO_LOGGER_WEBHOOK_ENDPOINT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook endpoint` {#mc-conf.logger_webhook.endpoint}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

webhook 的 HTTP 端点。

#### 认证 Token {#token}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_AUTH_TOKEN` {#envvar.MINIO_LOGGER_WEBHOOK_AUTH_TOKEN}

*envvar*

端点所需类型的认证 token。 对于不需要认证的端点可省略。

为支持多种 token 类型，MinIO 会使用 *完全按原样指定* 的值构造请求认证头。 具体端点可能要求你附加额外信息。

例如：对于 Bearer token，请添加前缀 `Bearer`：

```shell
export MINIO_LOGGER_WEBHOOK_AUTH_TOKEN_myendpoint="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。 自定义认证格式可能类似如下：

```shell
export MINIO_LOGGER_WEBHOOK_AUTH_TOKEN_xyz="ServiceXYZ 1a2b3c4f5e"
```

详情请参阅目标服务的文档。

该环境变量对应 [`logger_webhook auth_token`](#mc-conf.logger_webhook.auth_token) 配置项。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook auth_token` {#mc-conf.logger_webhook.auth_token}

*mc-conf*

端点所需类型的认证 token。 对于不需要认证的端点可省略。

为支持多种 token 类型，MinIO 会使用 *完全按原样指定* 的值构造请求认证头。 具体端点可能要求你附加额外信息。

例如：对于 Bearer token，请添加前缀 `Bearer`：

```shell
   mc admin config set myminio logger_webhook   \
      endpoint="https://webhook-1.example.net"  \
      auth_token="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。 自定义认证格式可能类似如下：

```shell
   mc admin config set myminio logger_webhook   \
      endpoint="https://webhook-1.example.net"  \
      auth_token="ServiceXYZ 1a2b3c4f5e"
```

详情请参阅目标服务的文档。
{{< /tab >}}
{{< /tabs >}}

#### 批大小 {#id7}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2024-03-10T02-53-48Z

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_BATCH_SIZE` {#envvar.MINIO_LOGGER_WEBHOOK_BATCH_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook batch_size` {#mc-conf.logger_webhook.batch_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

按批次收集并发送指定数量的事件到 webhook。 如果未设置，MinIO 每个请求发送一个事件。

#### 客户端证书 {#id8}

*可选*

还需要同时设置 *Client Key*。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_CLIENT_CERT` {#envvar.MINIO_LOGGER_WEBHOOK_CLIENT_CERT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook client_cert` {#mc-conf.logger_webhook.client_cert}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于向 webhook logger 认证的 mTLS 证书路径。

#### 客户端密钥 {#id9}

*可选*

如果定义了 *Client Certificate*，则为必填。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_CLIENT_KEY` {#envvar.MINIO_LOGGER_WEBHOOK_CLIENT_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook client_key` {#mc-conf.logger_webhook.client_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于向 webhook logger 服务认证的 mTLS 证书密钥路径。

#### 代理 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_PROXY` {#envvar.MINIO_LOGGER_WEBHOOK_PROXY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook proxy` {#mc-conf.logger_webhook.proxy}

*mc-conf*

> [!NOTE]
> **新增: MinIO**
>
> RELEASE.2023-02-22T18-23-45Z
{{< /tab >}}
{{< /tabs >}}

定义在 MinIO 与外部 webhook 通信时供 webhook logger 使用的代理。

#### 队列目录 {#id11}

*可选*

> [!NOTE]
> **新增: RELEASE.2023-05-18T00-05-36Z**

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_QUEUE_DIR` {#envvar.MINIO_LOGGER_WEBHOOK_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook queue_dir` {#mc-conf.logger_webhook.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径（例如 `/opt/minio/events`）以启用 MinIO 对未投递消息的持久事件存储。 MinIO 进程必须对指定目录具有读取、写入和列举权限。

当 webhook 服务离线时，MinIO 会将未投递事件存储到指定存储中，并在连接恢复后回放这些事件。

#### 队列大小 {#id12}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_LOGGER_WEBHOOK_QUEUE_SIZE` {#envvar.MINIO_LOGGER_WEBHOOK_QUEUE_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `logger_webhook queue_size` {#mc-conf.logger_webhook.queue_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于 logger webhook 目标队列大小的整数值。

<a id="minio-server-config-logging-audit"></a>
<a id="minio-server-envvar-logging-audit"></a>

## Webhook 审计日志 {#webhook}

以下部分介绍用于将审计日志发布到 HTTP webhook 端点的 MinIO 环境变量。 有关这些环境变量的更完整文档和使用教程，请参见 [将审计日志发布到 HTTP Webhook](/docs/operations/monitoring/minio-logging/#minio-logging-publish-audit-logs)。

### 多个目标 {#id13}

你可以通过为每组相关日志设置追加唯一标识符 `_ID`，将多个 webhook 端点指定为审计日志目标。

例如，以下命令设置了两个不同的审计日志 webhook 端点：

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
export MINIO_AUDIT_WEBHOOK_ENABLE_PRIMARY="on"
export MINIO_AUDIT_WEBHOOK_AUTH_TOKEN_PRIMARY="TOKEN"
export MINIO_AUDIT_WEBHOOK_ENDPOINT_PRIMARY="http://webhook-1.example.net"
export MINIO_AUDIT_WEBHOOK_CLIENT_CERT_SECONDARY="/tmp/cert.pem"
export MINIO_AUDIT_WEBHOOK_CLIENT_KEY_SECONDARY="/tmp/key.pem"

export MINIO_AUDIT_WEBHOOK_ENABLE_SECONDARY="on"
export MINIO_AUDIT_WEBHOOK_AUTH_TOKEN_SECONDARY="TOKEN"
export MINIO_AUDIT_WEBHOOK_ENDPOINT_SECONDARY="http://webhook-1.example.net"
export MINIO_AUDIT_WEBHOOK_CLIENT_CERT_SECONDARY="/tmp/cert.pem"
export MINIO_AUDIT_WEBHOOK_CLIENT_KEY_SECONDARY="/tmp/key.pem"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `audit_webhook` {#mc-conf.audit_webhook}

*mc-conf*

用于定义 HTTP webhook 目标并发布 [MinIO audit logs](/docs/operations/monitoring/minio-logging/#minio-logging) 的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 HTTP webhook 目标。 以空格（`" "`）分隔列表的形式指定其他可选参数。

```shell
mc admin config set audit_webhook \
   endpoint="http://webhook.example.net" [ARGUMENTS=VALUE ...]
```

你可以通过在顶层键后追加 `[:name]` 来指定多个 HTTP webhook 目标。 例如，以下命令分别将两个不同的 HTTP webhook 目标设置为 `primary` 和 `secondary`：

```shell
mc admin config set audit_webhook:primary \
   endpoint="http://webhook-01.example.net" [ARGUMENTS=VALUE ...]


mc admin config set audit_webhook:secondary \
   endpoint="http://webhook-02.example.net" [ARGUMENTS=VALUE ...]
```
{{< /tab >}}
{{< /tabs >}}

### 设置 {#id14}

#### Enable {#id15}

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_ENABLE` {#envvar.MINIO_AUDIT_WEBHOOK_ENABLE}

*envvar*

指定 `"on"` 以启用向 HTTP webhook 端点发布审计日志。

需要同时指定 [`MINIO_AUDIT_WEBHOOK_ENDPOINT`](#envvar.MINIO_AUDIT_WEBHOOK_ENDPOINT)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
配置一个 audit webhook 即表示启用该目标。 不存在单独的 `enable` 配置项。
{{< /tab >}}
{{< /tabs >}}

#### 端点 {#id16}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_ENDPOINT` {#envvar.MINIO_AUDIT_WEBHOOK_ENDPOINT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook endpoint` {#mc-conf.audit_webhook.endpoint}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

webhook 的 HTTP 端点。

#### 认证 Token {#id17}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_AUTH_TOKEN` {#envvar.MINIO_AUDIT_WEBHOOK_AUTH_TOKEN}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook auth_token` {#mc-conf.audit_webhook.auth_token}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

端点所需类型的认证 token。 对于不需要认证的端点可省略。

为支持多种 token 类型，MinIO 会使用 *完全按原样指定* 的值构造请求认证头。 具体端点可能要求你附加额外信息。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
例如，对于 Bearer token，请添加前缀 `Bearer`：

```shell
export MINIO_AUDIT_WEBHOOK_AUTH_TOKEN_myendpoint="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。

自定义认证格式可能类似如下：

```shell
export MINIO_AUDIT_WEBHOOK_AUTH_TOKEN_xyz="ServiceXYZ 1a2b3c4f5e"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
```shell
mc admin config set myminio audit_webhook       \
         endpoint="http://webhook.example.net"  \
         auth_token="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。

自定义认证格式的命令可能类似如下：

```shell
mc admin config set myminio audit_webhook       \
         endpoint="http://webhook.example.net"  \
         auth_token="ServiceXYZ 1a2b3c4f5e"
```
{{< /tab >}}
{{< /tabs >}}

详情请参阅目标服务的文档。

#### 批大小 {#id18}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2024-03-10T02-53-48Z

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_BATCH_SIZE` {#envvar.MINIO_AUDIT_WEBHOOK_BATCH_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook batch_size` {#mc-conf.audit_webhook.batch_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

按批次收集并发送指定数量的事件到 webhook。 如果未设置，MinIO 每个请求发送一个事件。

#### 客户端证书 {#id19}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_CLIENT_CERT` {#envvar.MINIO_AUDIT_WEBHOOK_CLIENT_CERT}

*envvar*

还需要同时指定 [`MINIO_AUDIT_WEBHOOK_CLIENT_KEY`](#envvar.MINIO_AUDIT_WEBHOOK_CLIENT_KEY)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook client_cert` {#mc-conf.audit_webhook.client_cert}

*mc-conf*

还需要同时指定 [`client_key`](#mc-conf.audit_webhook.client_key)。
{{< /tab >}}
{{< /tabs >}}

提交给 HTTP webhook 的 x.509 客户端证书。 对于不要求客户端提供已知 TLS 证书的 webhook 可省略。

#### 客户端密钥 {#id20}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_CLIENT_KEY` {#envvar.MINIO_AUDIT_WEBHOOK_CLIENT_KEY}

*envvar*

还需要同时指定 [`MINIO_AUDIT_WEBHOOK_CLIENT_CERT`](#envvar.MINIO_AUDIT_WEBHOOK_CLIENT_CERT)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook client_key` {#mc-conf.audit_webhook.client_key}

*mc-conf*

需要指定 [`client_cert`](#mc-conf.audit_webhook.client_cert)。
{{< /tab >}}
{{< /tabs >}}

提交给 HTTP webhook 的 x.509 私钥。 对于不要求客户端提供已知 TLS 证书的 webhook 可省略。

#### 队列目录 {#id21}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_QUEUE_DIR` {#envvar.MINIO_AUDIT_WEBHOOK_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook queue_dir` {#mc-conf.audit_webhook.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **新增: RELEASE.2023-05-18T00-05-36Z**

指定目录路径（例如 `/opt/minio/events`）以启用 MinIO 对未投递消息的持久事件存储。 MinIO 进程必须对指定目录具有读取、写入和列举权限。

当 webhook 服务离线时，MinIO 会将未投递事件存储到指定存储中，并在连接恢复后回放这些事件。

#### 队列大小 {#id22}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_WEBHOOK_QUEUE_SIZE` {#envvar.MINIO_AUDIT_WEBHOOK_QUEUE_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_webhook queue_size` {#mc-conf.audit_webhook.queue_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于 audit webhook 目标队列大小的整数值。 默认值为 `100000` 个事件。

<a id="minio-server-config-logging-kafka-audit"></a>
<a id="minio-server-envvar-logging-audit-kafka"></a>

## Kafka 审计日志 {#kafka}

以下部分介绍用于将审计日志发布到 Kafka broker 的 MinIO 环境变量。

#### `audit_kafka` {#mc-conf.audit_kafka}

*mc-conf*

用于定义 Kafka broker 目标并发布 [MinIO audit logs](/docs/operations/monitoring/minio-logging/#minio-logging) 的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 Kafka 审计目标。 以空格（`" "`）分隔列表的形式指定其他可选参数。

```shell
mc admin config set audit_kafka \
   brokers="https://kafka-endpoint.example.net:9092" [ARGUMENTS=VALUE ...]
```

### 设置 {#id23}

#### Enable {#id24}

*必填*

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_ENABLE` {#envvar.MINIO_AUDIT_KAFKA_ENABLE}

*envvar*

设置为 `"on"` 以启用该目标。

设置为 `"off"` 以禁用该目标。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
该值没有对应的配置项。 使用环境变量可禁用已配置的 audit webhook 目标。
{{< /tab >}}
{{< /tabs >}}

#### Brokers {#brokers}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_BROKERS` {#envvar.MINIO_AUDIT_KAFKA_BROKERS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka brokers` {#mc-conf.audit_kafka.brokers}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

Kafka broker 地址的逗号分隔列表：

```shell
brokers="https://kafka-1.example.net:9092,https://kafka-2.example.net:9092"
```

至少必须有一个 broker 在线且 MinIO server 可达，才能初始化并发送审计日志事件。 MinIO 会按指定顺序检查每个 broker。

#### Topic {#topic}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_TOPIC` {#envvar.MINIO_AUDIT_KAFKA_TOPIC}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka topic` {#mc-conf.audit_kafka.topic}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

与 MinIO 审计日志事件关联的 Kafka topic 名称。

#### TLS {#tls}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_TLS` {#envvar.MINIO_AUDIT_KAFKA_TLS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka tls` {#mc-conf.audit_kafka.tls}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

设置为 `"on"` 以启用到指定 Kafka brokers 的 TLS 连接。

默认值为 `"off"`。

#### TLS Skip Verify {#tls-skip-verify}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_TLS_SKIP_VERIFY` {#envvar.MINIO_AUDIT_KAFKA_TLS_SKIP_VERIFY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka tls_skip_verify` {#mc-conf.audit_kafka.tls_skip_verify}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

设置为 `"on"` 以指示 MinIO 跳过对 Kafka broker TLS 证书的校验。

你可以使用该选项连接使用未知签发方 TLS 证书的 Kafka brokers，例如自签名证书或企业内部 CA（Certificate Authorities）签发的证书。

默认情况下，MinIO 会同时使用系统信任库 *以及* MinIO [CA directory](/docs/operations/network-encryption/#minio-tls) 中的内容来校验远端客户端 TLS 证书。

默认值为 `"off"`，即严格校验 TLS 证书。

#### SASL {#sasl}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_SASL` {#envvar.MINIO_AUDIT_KAFKA_SASL}

*envvar*

需要指定 [`MINIO_AUDIT_KAFKA_SASL_USERNAME`](#envvar.MINIO_AUDIT_KAFKA_SASL_USERNAME) 和 [`MINIO_AUDIT_KAFKA_SASL_PASSWORD`](#envvar.MINIO_AUDIT_KAFKA_SASL_PASSWORD)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka sasl` {#mc-conf.audit_kafka.sasl}

*mc-conf*

需要指定 [`sasl_username`](#mc-conf.audit_kafka.sasl_username) 和 [`sasl_password`](#mc-conf.audit_kafka.sasl_password)。
{{< /tab >}}
{{< /tabs >}}

设置为 `"on"` 以指示 MinIO 使用 SASL 对 Kafka brokers 进行认证。

#### SASL Username {#sasl-username}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_SASL_USERNAME` {#envvar.MINIO_AUDIT_KAFKA_SASL_USERNAME}

*envvar*

需要指定 [`MINIO_AUDIT_KAFKA_SASL`](#envvar.MINIO_AUDIT_KAFKA_SASL) 和 [`MINIO_AUDIT_KAFKA_SASL_PASSWORD`](#envvar.MINIO_AUDIT_KAFKA_SASL_PASSWORD)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka sasl_username` {#mc-conf.audit_kafka.sasl_username}

*mc-conf*

需要指定 [`sasl`](#mc-conf.audit_kafka.sasl) 和 [`sasl_password`](#mc-conf.audit_kafka.sasl_password)。
{{< /tab >}}
{{< /tabs >}}

MinIO 用于对 Kafka brokers 进行认证的 SASL 用户名。

#### SASL Password {#sasl-password}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_SASL_PASSWORD` {#envvar.MINIO_AUDIT_KAFKA_SASL_PASSWORD}

*envvar*

需要指定 [`MINIO_AUDIT_KAFKA_SASL`](#envvar.MINIO_AUDIT_KAFKA_SASL) 和 [`MINIO_AUDIT_KAFKA_SASL_USERNAME`](#envvar.MINIO_AUDIT_KAFKA_SASL_USERNAME)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka sasl_password` {#mc-conf.audit_kafka.sasl_password}

*mc-conf*

需要指定 [`sasl`](#mc-conf.audit_kafka.sasl) 和 [`sasl_username`](#mc-conf.audit_kafka.sasl_username)。
{{< /tab >}}
{{< /tabs >}}

MinIO 用于对 Kafka brokers 进行认证的 SASL 密码。

#### SASL Mechanism {#sasl-mechanism}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_SASL_MECHANISM` {#envvar.MINIO_AUDIT_KAFKA_SASL_MECHANISM}

*envvar*

> [!WARNING]
> **重要**
>
> `PLAIN` 认证机制会以明文形式在网络中传输凭据。 使用 [`MINIO_AUDIT_KAFKA_TLS`](#envvar.MINIO_AUDIT_KAFKA_TLS) 以启用到 Kafka brokers 的 TLS 连接，并确保 SASL 凭据安全传输。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka sasl_mechanism` {#mc-conf.audit_kafka.sasl_mechanism}

*mc-conf*

> [!WARNING]
> **重要**
>
> `PLAIN` 认证机制会以明文形式在网络中传输凭据。 使用 [`tls`](#mc-conf.audit_kafka.tls) 以启用到 Kafka brokers 的 TLS 连接，并确保 SASL 凭据安全传输。
{{< /tab >}}
{{< /tabs >}}

MinIO 用于对 Kafka brokers 进行认证的 SASL 机制。

默认值为 `plain`。

#### TLS Client Auth {#tls-client-auth}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_TLS_CLIENT_AUTH` {#envvar.MINIO_AUDIT_KAFKA_TLS_CLIENT_AUTH}

*envvar*

需要指定 [`MINIO_AUDIT_KAFKA_CLIENT_TLS_CERT`](#envvar.MINIO_AUDIT_KAFKA_CLIENT_TLS_CERT) 和 [`MINIO_AUDIT_KAFKA_CLIENT_TLS_KEY`](#envvar.MINIO_AUDIT_KAFKA_CLIENT_TLS_KEY)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka tls_client_auth` {#mc-conf.audit_kafka.tls_client_auth}

*mc-conf*

需要指定 [`client_tls_cert`](#mc-conf.audit_kafka.client_tls_cert) 和 [`client_tls_key`](#mc-conf.audit_kafka.client_tls_key)。
{{< /tab >}}
{{< /tabs >}}

设置为 `"on"` 以指示 MinIO 使用 mTLS 对 Kafka brokers 进行认证。

#### Client TLS Certificate {#client-tls-certificate}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_CLIENT_TLS_CERT` {#envvar.MINIO_AUDIT_KAFKA_CLIENT_TLS_CERT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka client_tls_cert` {#mc-conf.audit_kafka.client_tls_cert}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于 mTLS 认证的 TLS 客户端证书路径。

#### Client TLS Key {#client-tls-key}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_CLIENT_TLS_KEY` {#envvar.MINIO_AUDIT_KAFKA_CLIENT_TLS_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka client_tls_key` {#mc-conf.audit_kafka.client_tls_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于 mTLS 认证的 TLS 客户端私钥路径。

#### Version {#version}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_VERSION` {#envvar.MINIO_AUDIT_KAFKA_VERSION}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka version` {#mc-conf.audit_kafka.version}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

MinIO 在指定端点期望的 Kafka broker 版本。

如果 Kafka broker 版本与此设置指定的不匹配，MinIO 会返回错误。

#### Comment {#comment}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_COMMENT` {#envvar.MINIO_AUDIT_KAFKA_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka comment` {#mc-conf.audit_kafka.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

与该配置关联的注释。

#### 队列目录 {#id25}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_QUEUE_DIR` {#envvar.MINIO_AUDIT_KAFKA_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka queue_dir` {#mc-conf.audit_kafka.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径（例如 `/opt/minio/events`）以启用 MinIO 对未投递消息的持久事件存储。

当 Kafka 服务离线时，MinIO 会将未投递事件存储到指定存储中，并在连接恢复后回放这些事件。

#### 队列大小 {#id26}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
###### `MINIO_AUDIT_KAFKA_QUEUE_SIZE` {#envvar.MINIO_AUDIT_KAFKA_QUEUE_SIZE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
###### `audit_kafka queue_size` {#mc-conf.audit_kafka.queue_size}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认值为 `100000`。