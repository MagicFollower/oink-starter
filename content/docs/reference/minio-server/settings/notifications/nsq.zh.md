---
title: "NSQ 通知设置"

weight: 70
---

<a id="nsq"></a>
<a id="minio-server-config-bucket-notification-nsq"></a>
<a id="minio-server-envvar-bucket-notification-nsq"></a>

本页面记录了将 NSQ 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标时所使用的设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 NSQ](/docs/administration/monitoring/publish-events-to-nsq/#minio-bucket-notifications-publish-nsq)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 NSQ 目标 {#id2}

你可以通过在每组相关 NSQ 设置的顶层键末尾附加唯一标识符 `_ID`，指定多个 NSQ 服务端点。 例如，以下命令分别将两个不同的 NSQ 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_NOTIFY_NSQ_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_NSQ_NSQD_ADDRESS_PRIMARY="https://user:password@nsq-endpoint.example.net:9200"
export MINIO_NOTIFY_NSQ_TOPIC_PRIMARY="bucketevents"

export MINIO_NOTIFY_NSQ_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_NSQ_NSQD_ADDRESS_SECONDARY="https://user:password@nsq-endpoint.example.net:9200"
export MINIO_NOTIFY_NSQ_TOPIC_SECONDARY="bucketevents"
```

```shell {tab="配置项" value="tab2"}
mc admin config set notify_nsq:primary \
   nsqd_address="ENDPOINT" \
   topic="<string>" \
   [ARGUMENT="VALUE"] ... \

mc admin config set notify_nsq:secondary \
   nsqd_address="ENDPOINT" \
   topic="<string>" \
   [ARGUMENT="VALUE"] ... \
```

## 设置 {#id3}

### 启用 {#id4}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_ENABLE` {#envvar.MINIO_NOTIFY_NSQ_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 NSQ 端点。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq` {#mc-conf.notify_nsq}

*mc-conf*

用于定义 NSQ server/broker 端点的顶层配置键，供 [MinIO 存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 使用。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 NSQ server/broker 端点。 每个端点都 *必须* 包含以下参数：

- [`nsqd_address`](#mc-conf.notify_nsq.nsqd_address)
- [`topic`](#mc-conf.notify_nsq.topic)

其他可选参数以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set notify_nsq                          \
   nsqd_address="https://nsq-endpoint.example.net:4150" \
   topic="<string>"                                     \
   [ARGUMENT="VALUE"] ...
```
{{< /tab >}}
{{< /tabs >}}

### NSQ Daemon 服务器地址 {#nsq-daemon}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_NSQD_ADDRESS` {#envvar.MINIO_NOTIFY_NSQ_NSQD_ADDRESS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq nsqd_address` {#mc-conf.notify_nsq.nsqd_address}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 NSQ Daemon 运行所在的 NSQ 服务器地址。 例如：

`https://nsq-endpoint.example.net:4150`

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### 主题 {#id5}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_TOPIC` {#envvar.MINIO_NOTIFY_NSQ_TOPIC}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq topic` {#mc-conf.notify_nsq.topic}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 向 broker 发布事件时使用的 NSQ topic 名称。

### TLS {#tls}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_TLS` {#envvar.MINIO_NOTIFY_NSQ_TLS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq tls` {#mc-conf.notify_nsq.tls}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用到 NSQ service broker 的 TLS 连接。

### TLS 跳过校验 {#id6}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_TLS_SKIP_VERIFY` {#envvar.MINIO_NOTIFY_NSQ_TLS_SKIP_VERIFY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq tls_skip_verify` {#mc-conf.notify_nsq.tls_skip_verify}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

启用或禁用对 NSQ service broker TLS 证书的 TLS 校验。

- 指定 `on` 可禁用 TLS 校验（默认）。
- 指定 `off` 可启用 TLS 校验。

### 队列目录 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_QUEUE_DIR` {#envvar.MINIO_NOTIFY_NSQ_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq queue_dir` {#mc-conf.notify_nsq.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 NSQ server/broker 离线时，MinIO 会将未投递事件存储在指定存储中，并在连接恢复后重放这些已存储事件。

### 队列上限 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_NSQ_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq queue_limit` {#mc-conf.notify_nsq.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认值为 `100000`。

### 备注 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_NSQ_COMMENT` {#envvar.MINIO_NOTIFY_NSQ_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_nsq comment` {#mc-conf.notify_nsq.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 NSQ 配置关联的备注。