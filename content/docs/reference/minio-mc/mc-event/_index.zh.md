---
title: "mc event"

weight: 100
icon: fa-solid fa-bell
---

<a id="mc-event"></a>

<a id="command-mc.event"></a>

## 描述 {#id2}

[`mc event`](#command-mc.event) 命令支持添加、删除和列出存储桶事件通知。

MinIO 会自动将触发的事件发送到已配置的通知目标。 MinIO 支持 AMQP (RabbitMQ)、Redis、ElasticSearch、NATS 和 PostgreSQL 等通知目标。 有关更多信息，请参阅 [MinIO 存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

## 子命令 {#id3}

[`mc event`](#command-mc.event) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-event-add/#command-mc.event.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-event-add/#command-mc.event.add"><code>mc event add</code></a> 命令为存储桶添加事件通知触发器。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls"><code>mc event ls</code></a> 命令列出某个存储桶的所有事件通知触发器。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-event-remove/#command-mc.event.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-event-remove/#command-mc.event.rm"><code>mc event rm</code></a> 命令用于从存储桶中移除事件通知触发器。</p></td>
    </tr>
  </tbody>
</table>