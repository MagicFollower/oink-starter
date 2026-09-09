---
title: "Redis 通知设置"

weight: 90
---

<a id="redis"></a>
<a id="minio-server-config-bucket-notification-redis"></a>
<a id="minio-server-envvar-bucket-notification-redis"></a>

本页记录了将 Redis 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标所需的设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 Redis](/docs/administration/monitoring/publish-events-to-redis/#minio-bucket-notifications-publish-redis)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 Redis 目标 {#id2}

你可以通过在每组相关 Redis 设置的顶层键末尾追加唯一标识符 `_ID` 来指定多个 Redis 服务端点。 例如，以下命令分别将两个不同的 Redis 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_NOTIFY_REDIS_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_REDIS_ADDRESS_PRIMARY="redis-endpoint.example.net:9200"
export MINIO_NOTIFY_REDIS_KEY_PRIMARY="bucketevents"
export MINIO_NOTIFY_REDIS_FORMAT_PRIMARY="namespace"


export MINIO_NOTIFY_REDIS_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_REDIS_REDIS_ADDRESS_SECONDARY="redis-endpoint2.example.net:9200"
export MINIO_NOTIFY_REDIS_KEY_SECONDARY="bucketevents"
export MINIO_NOTIFY_REDIS_FORMAT_SECONDARY="namespace"
```

```shell {tab="配置设置" value="tab2"}
mc admin config set notify_redis:primary              \
   address="redis-endpoint.example.net:9200"  \
   key="bucketevents"                                 \
   format="namespace"                                 \
   [ARGUMENT="VALUE"] ...                             \

mc admin config set notify_redis:secondary            \
   address="redis-endpoint2.example.net:9200" \
   key="bucketevents"                                 \
   format="namespace"                                 \
   [ARGUMENT="VALUE"] ...
```

## 设置 {#id3}

### 启用 {#id4}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_ENABLE` {#envvar.MINIO_NOTIFY_REDIS_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 Redis 服务端点。

默认为 `off`。

如果设置为 `on`，还必须指定以下附加环境变量：

- [`MINIO_NOTIFY_REDIS_ADDRESS`](#envvar.MINIO_NOTIFY_REDIS_ADDRESS)
- [`MINIO_NOTIFY_REDIS_KEY`](#envvar.MINIO_NOTIFY_REDIS_KEY)
- [`MINIO_NOTIFY_REDIS_FORMAT`](#envvar.MINIO_NOTIFY_REDIS_FORMAT)
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis` {#mc-conf.notify_redis}

*mc-conf*

用于定义 Redis server/broker 端点并供 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 使用的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 Redis server/broker 端点。 对于每个端点，以下参数为 *必需*：

- [`address`](#mc-conf.notify_redis.address)
- [`key`](#mc-conf.notify_redis.key)
- [`format`](#mc-conf.notify_redis.format)

将其他可选参数指定为以空白字符（`" "`）分隔的列表。

```shell
mc admin config set notify_redis \
   address="ENDPOINT" \
   key="<string>" \
   format="<string>" \
   [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### 地址 {#id5}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_ADDRESS` {#envvar.MINIO_NOTIFY_REDIS_ADDRESS}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis address` {#mc-conf.notify_redis.address}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布存储桶事件的 Redis 服务端点。 例如：`redis.example.com:6369`。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### 键 {#id6}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_KEY` {#envvar.MINIO_NOTIFY_REDIS_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis key` {#mc-conf.notify_redis.key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于存储和更新事件的 Redis 键。 如果该键不存在，Redis 会自动创建。

### 格式 {#id7}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_FORMAT` {#envvar.MINIO_NOTIFY_REDIS_FORMAT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis format` {#mc-conf.notify_redis.format}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定写入 Redis 服务端点的事件数据格式。 MinIO 支持以下取值：

**`namespace`**

> 对于每个存储桶事件，MinIO 会创建一个 JSON 文档，以事件中的存储桶名和对象名作为文档 ID，并将实际事件作为文档体的一部分。 对该对象的后续更新会修改该对象现有的索引条目。 同样，删除对象也会删除对应的索引条目。

**`access`**

> 对于每个存储桶事件，MinIO 会创建一个包含事件详情的 JSON 文档，并以 Redis 生成的随机 ID 将其追加到该键。 对对象的后续更新会产生新的索引条目，现有条目保持不变。

### 密码 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_PASSWORD` {#envvar.MINIO_NOTIFY_REDIS_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis password` {#mc-conf.notify_redis.password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Redis 服务器的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当该值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时，MinIO 会对其进行脱敏。

### 用户 {#id9}

*可选*

> [!NOTE]
> **新增: RELEASE.2024-03-21T23-13-43Z**

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_USER` {#envvar.MINIO_NOTIFY_REDIS_USER}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis user` {#mc-conf.notify_redis.user}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Redis 服务器的用户。

### 队列目录 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_QUEUE_DIR` {#envvar.MINIO_NOTIFY_REDIS_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis queue_dir` {#mc-conf.notify_redis.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 的持久化事件存储，用于保存未投递消息，例如 `/opt/minio/events`。

当 Redis server/broker 离线时，MinIO 会将未投递事件存储到指定存储中；连接恢复后，会重放这些已存储事件。

### 队列上限 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_REDIS_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis queue_limit` {#mc-conf.notify_redis.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认为 `100000`。

### 注释 {#id12}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_REDIS_COMMENT` {#envvar.MINIO_NOTIFY_REDIS_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_redis comment` {#mc-conf.notify_redis.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 Redis 配置关联的注释。