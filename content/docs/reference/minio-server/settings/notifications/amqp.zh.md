---
title: "AMQP 通知设置"

weight: 10
---

<a id="amqp"></a>
<a id="minio-server-config-bucket-notification-amqp"></a>
<a id="minio-server-envvar-bucket-notification-amqp"></a>

本文档说明了将 AMQP 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的相关设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 AMQP (RabbitMQ)](/docs/administration/monitoring/publish-events-to-amqp/#minio-bucket-notifications-publish-amqp)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 AMQP 目标 {#id2}

可以通过在顶层键后为每组相关 AMQP 设置追加唯一标识符 `_ID`，来指定多个 AMQP 服务端点。

### 示例 {#id3}

例如，以下命令分别将两个不同的 AMQP 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
export MINIO_NOTIFY_AMQP_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_AMQP_URL_PRIMARY="amqp://user:password@amqp-endpoint.example.net:5672"

export MINIO_NOTIFY_AMQP_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_AMQP_URL_SECONDARY="amqp://user:password@amqp-endpoint.example.net:5672"
```

例如，[`MINIO_NOTIFY_AMQP_ENABLE_PRIMARY`](#envvar.MINIO_NOTIFY_AMQP_ENABLE) 表示该环境变量关联到 ID 为 `PRIMARY` 的 AMQP 服务端点。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
```shell
mc admin config set notify_amqp:primary \
   url="user:password@amqp://amqp-endpoint.example.net:5672" [ARGUMENT=VALUE ...]

mc admin config set notify_amqp:secondary \
   url="user:password@amqp://amqp-endpoint.example.net:5672" [ARGUMENT=VALUE ...]
```

请注意，对于配置设置，唯一标识符仅追加到 `amqp`，而不是每个单独参数。
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id4}

### 启用 {#id5}

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_ENABLE` {#envvar.MINIO_NOTIFY_AMQP_ENABLE}

*envvar*

如果设置为 `on`，则必须指定 [`MINIO_NOTIFY_AMQP_URL`](#envvar.MINIO_NOTIFY_AMQP_URL)。

指定 `on` 以启用向 AMQP 端点发布存储桶通知。

默认值为 `off`。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp` {#mc-conf.notify_amqp}

*mc-conf*

用于定义 AMQP 服务端点以供 [MinIO 存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 使用的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 AMQP 服务端点。 对于每个目标，[`url`](#mc-conf.notify_amqp.url) 参数都是 *必需* 的。 以空白字符（`" "`）分隔的列表形式指定其他可选参数。

```shell
mc admin config set notify_amqp \
  url="amqp://user:password@endpoint:port" \
  [ARGUMENT="VALUE"] ...
```
{{< /tab >}}
{{< /tabs >}}

### URL {#url}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_URL` {#envvar.MINIO_NOTIFY_AMQP_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp url` {#mc-conf.notify_amqp.url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布存储桶事件的 AMQP 服务器端点。 例如，`amqp://myuser:mypassword@localhost:5672`。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### Exchange（交换机） {#exchange}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_EXCHANGE` {#envvar.MINIO_NOTIFY_AMQP_EXCHANGE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp exchange` {#mc-conf.notify_amqp.exchange}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要使用的 AMQP exchange 名称。

### Exchange 类型 {#id6}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_EXCHANGE_TYPE` {#envvar.MINIO_NOTIFY_AMQP_EXCHANGE_TYPE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp exchange_type` {#mc-conf.notify_amqp.exchange_type}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 AMQP exchange 的类型。

### 路由键 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_ROUTING_KEY` {#envvar.MINIO_NOTIFY_AMQP_ROUTING_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp routing_key` {#mc-conf.notify_amqp.routing_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于发布事件的 routing key。

### Mandatory（强制） {#mandatory}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_MANDATORY` {#envvar.MINIO_NOTIFY_AMQP_MANDATORY}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp mandatory` {#mc-conf.notify_amqp.mandatory}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `off` 以忽略消息未送达错误。 默认值为 `on`。

### 持久化 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_DURABLE` {#envvar.MINIO_NOTIFY_AMQP_DURABLE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp durable` {#mc-conf.notify_amqp.durable}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以在 broker 重启后保留消息队列。 默认值为 `off`。

### No Wait（不等待） {#no-wait}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_NO_WAIT` {#envvar.MINIO_NOTIFY_AMQP_NO_WAIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp no_wait` {#mc-conf.notify_amqp.no_wait}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以启用非阻塞消息投递。 默认值为 `off`。

### Internal（内部） {#internal}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_INTERNAL` {#envvar.MINIO_NOTIFY_AMQP_INTERNAL}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp internal` {#mc-conf.notify_amqp.internal}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以仅在 exchange 绑定到其他 exchanges 时使用该 exchange。 有关 AMQP exchange 绑定的更多信息，请参阅 RabbitMQ 文档中的 [Exchange to Exchange Bindings](https://www.rabbitmq.com/e2e.html)。

### 自动删除 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_AUTO_DELETED` {#envvar.MINIO_NOTIFY_AMQP_AUTO_DELETED}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp auto_deleted` {#mc-conf.notify_amqp.auto_deleted}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 以在没有消费者时自动删除消息队列。 默认值为 `off`。

### 投递模式 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_DELIVERY_MODE` {#envvar.MINIO_NOTIFY_AMQP_DELIVERY_MODE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp delivery_mode` {#mc-conf.notify_amqp.delivery_mode}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `1` 以将投递模式设置为非持久化队列。

指定 `2` 以将投递模式设置为持久化队列。

### 队列目录 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_QUEUE_DIR` {#envvar.MINIO_NOTIFY_AMQP_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp queue_dir` {#mc-conf.notify_amqp.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 对未送达消息的持久化事件存储，例如 `/opt/minio/events`。

当 AMQP 服务离线时，MinIO 会将未送达事件存储在指定存储中，并在连接恢复后重放这些已存储事件。

### 队列限制 {#id12}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_AMQP_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp queue_limit` {#mc-conf.notify_amqp.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未送达消息的最大数量限制。 默认值为 `100000`。

### 注释 {#id13}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_AMQP_COMMENT` {#envvar.MINIO_NOTIFY_AMQP_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_amqp comment` {#mc-conf.notify_amqp.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

为 AMQP 配置指定注释。