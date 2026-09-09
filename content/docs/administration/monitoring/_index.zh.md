---
title: "监控存储桶与对象事件"

weight: 130
icon: fa-solid fa-bell
---

<a id="id1"></a>

## 存储桶通知 {#id3}

MinIO 存储桶通知允许管理员在特定对象或存储桶事件发生时，将通知发送到受支持的外部服务。 MinIO 支持与 [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) 类似的存储桶级和对象级 S3 事件。

在某些受支持的事件上，MinIO 支持将存储桶或对象事件发布到以下受支持的目标。

- [将事件发布到 AMQP (RabbitMQ)](/docs/administration/monitoring/publish-events-to-amqp/#minio-bucket-notifications-publish-amqp)
- [将事件发布到 MQTT](/docs/administration/monitoring/publish-events-to-mqtt/#minio-bucket-notifications-publish-mqtt)
- [将事件发布到 NATS](/docs/administration/monitoring/publish-events-to-nats/#minio-bucket-notifications-publish-nats)
- [将事件发布到 NSQ](/docs/administration/monitoring/publish-events-to-nsq/#minio-bucket-notifications-publish-nsq)
- [将事件发布到 Elasticsearch](/docs/administration/monitoring/publish-events-to-elasticsearch/#minio-bucket-notifications-publish-elasticsearch)
- [将事件发布到 Kafka](/docs/administration/monitoring/publish-events-to-kafka/#minio-bucket-notifications-publish-kafka)
- [将事件发布到 MySQL](/docs/administration/monitoring/publish-events-to-mysql/#minio-bucket-notifications-publish-mysql)
- [将事件发布到 PostgreSQL](/docs/administration/monitoring/publish-events-to-postgresql/#minio-bucket-notifications-publish-postgresql)
- [将事件发布到 Redis](/docs/administration/monitoring/publish-events-to-redis/#minio-bucket-notifications-publish-redis)
- [将事件发布到 Webhook](/docs/administration/monitoring/publish-events-to-webhook/#minio-bucket-notifications-publish-webhook)

有关 MinIO 存储桶通知的更完整文档，请参见 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

## 部署指标 {#id4}

MinIO 提供兼容 Prometheus 的端点，以支持对指标进行时间序列查询。

## 服务日志 {#id5}

MinIO 提供以下接口用于远程读取服务日志：

- [`mc admin logs`](/docs/reference/minio-mc-admin/mc-admin-logs/#command-mc.admin.logs) 命令会返回指定服务器的控制台输出。
- MinIO 支持将服务日志推送到 HTTP webhook，以便进一步采集。 更多信息请参见 [将服务日志发布到 HTTP Webhook](/docs/operations/monitoring/minio-logging/#minio-logging-publish-server-logs)。