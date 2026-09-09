---
title: "存储桶通知设置"

weight: 70
icon: fa-solid fa-bell
---

<a id="minio-server-config-logging-logs"></a>
<a id="minio-server-envvar-notifications"></a>
<a id="id1"></a>

本页介绍用于控制 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 相关行为的设置。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 同步事件 {#id3}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_API_SYNC_EVENTS` {#envvar.MINIO_API_SYNC_EVENTS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `api sync_events` {#mc-conf.api.sync_events}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

启用同步 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

指定 `on` 可让 MinIO 在远端目标收到事件并返回成功之后，再继续处理后续事件。

默认值为 `off`，即异步存储桶通知。在这种模式下，MinIO 不会等待远端目标在收到 事件后返回成功。

## 支持的通知目标 {#id4}

通知需要一个用于接收事件的目标。 MinIO 支持多种通知目标。 每种目标类型的设置位于各自独立的页面。 请根据实际使用的目标类型，选择下方对应链接。

- [AMQP 通知设置](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-envvar-bucket-notification-amqp)
- [Elasticsearch 通知设置](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-envvar-bucket-notification-elasticsearch)
- [Kafka 通知设置](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-envvar-bucket-notification-kafka)
- [MQTT 通知设置](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-envvar-bucket-notification-mqtt)
- [MySQL 通知设置](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-envvar-bucket-notification-mysql)
- [NATS 通知设置](/docs/reference/minio-server/settings/notifications/nats/#minio-server-envvar-bucket-notification-nats)
- [NSQ 通知设置](/docs/reference/minio-server/settings/notifications/nsq/#minio-server-envvar-bucket-notification-nsq)
- [PostgreSQL 通知设置](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-envvar-bucket-notification-postgresql)
- [Redis 通知设置](/docs/reference/minio-server/settings/notifications/redis/#minio-server-envvar-bucket-notification-redis)
- [Webhook 服务通知设置](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-envvar-bucket-notification-webhook)