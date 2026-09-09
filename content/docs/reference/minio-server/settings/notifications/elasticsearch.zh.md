---
title: "Elasticsearch 通知设置"

weight: 20
---

<a id="elasticsearch"></a>
<a id="minio-server-config-bucket-notification-elasticsearch"></a>
<a id="minio-server-envvar-bucket-notification-elasticsearch"></a>

本文档介绍如何配置 Elasticsearch 服务作为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 的目标。 有关如何使用这些设置的教程，请参阅 [将事件发布到 Elasticsearch](/docs/administration/monitoring/publish-events-to-elasticsearch/#minio-bucket-notifications-publish-elasticsearch)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 Elasticsearch 目标 {#id2}

可通过为每组相关设置追加唯一标识符 `_ID` 来指定多个 Elasticsearch 服务端点。 例如，以下命令分别将两个不同的 Elasticsearch 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

### 示例 {#id3}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
export MINIO_NOTIFY_ELASTICSEARCH_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_ELASTICSEARCH_URL_PRIMARY="https://user:password@elasticsearch-endpoint.example.net:9200"
export MINIO_NOTIFY_ELASTICSEARCH_INDEX_PRIMARY="bucketevents"
export MINIO_NOTIFY_ELASTICSEARCH_FORMAT_PRIMARY="namespace"

export MINIO_NOTIFY_ELASTICSEARCH_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_ELASTICSEARCH_URL_SECONDARY="https://user:password@elasticsearch-endpoint.example.net:9200"
export MINIO_NOTIFY_ELASTICSEARCH_INDEX_SECONDARY="bucketevents"
export MINIO_NOTIFY_ELASTICSEARCH_FORMAT_SECONDARY="namespace"
```
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
```shell
mc admin config set notify_elasticsearch:primary \
   url="user:password@https://elasticsearch-endpoint.example.net:9200" \
   index="bucketevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]

mc admin config set notify_elasticsearch:secondary \
   url="user:password@https://elasticsearch-endpoint.example.net:9200" \
   index="bucketevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]
```

注意，对于配置设置，唯一标识符只追加到 `notify_elasticsearch`，而不是每个单独参数。
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id4}

### 启用 {#id5}

*必需*

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_ENABLE` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 Elasticsearch 服务端点。

默认为 `off`。

如果设置为 `on`，则还必须指定以下环境变量：

- [`MINIO_NOTIFY_ELASTICSEARCH_URL`](#envvar.MINIO_NOTIFY_ELASTICSEARCH_URL)
- [`MINIO_NOTIFY_ELASTICSEARCH_INDEX`](#envvar.MINIO_NOTIFY_ELASTICSEARCH_INDEX)
- [`MINIO_NOTIFY_ELASTICSEARCH_FORMAT`](#envvar.MINIO_NOTIFY_ELASTICSEARCH_FORMAT)
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch` {#mc-conf.notify_elasticsearch}

*mc-conf*

用于定义 Elasticsearch 服务端点以配合 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 使用的顶级配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 Elasticsearch 服务端点。 对于每个目标，以下参数为 *必需*：

- [`url`](#mc-conf.notify_elasticsearch.url)
- [`index`](#mc-conf.notify_elasticsearch.index)
- [`format`](#mc-conf.notify_elasticsearch.format)

其他可选参数以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set notify_elasticsearch \
  url="https://user:password@elasticsearch.example.com:9200" \
  [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### URL {#url}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_URL` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch url` {#mc-conf.notify_elasticsearch.url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 将存储桶事件发布到的 Elasticsearch 服务端点。 例如：`https://elasticsearch.example.com:9200`。

MinIO 支持通过 URL 参数传递认证信息，格式为 `PROTOCOL://USERNAME:PASSWORD@HOSTNAME:PORT`。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### Index {#index}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_INDEX` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_INDEX}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch index` {#mc-conf.notify_elasticsearch.index}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于存储或更新 MinIO 存储桶事件的 Elasticsearch index 名称。 如果 index 不存在，Elasticsearch 会自动创建。

### Format {#format}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_FORMAT` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_FORMAT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch format` {#mc-conf.notify_elasticsearch.format}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定写入 Elasticsearch index 的事件数据格式。 MinIO 支持以下取值：

**`namespace`**

> 对于每个存储桶事件，MinIO 会创建一个 JSON 文档，以事件中的存储桶名和对象名作为文档 ID，并将实际事件作为文档正文的一部分。 对该对象的后续更新会修改该对象在 index 中的现有条目。 同样，删除该对象也会删除对应的 index 条目。

**`access`**

> 对于每个存储桶事件，MinIO 会创建一个包含事件详情的 JSON 文档，并以 Elasticsearch 生成的随机 ID 将其追加到 index。 对对象的后续更新会产生新的 index 条目，而现有条目保持不变。

### Username {#username}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_USERNAME` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_USERNAME}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch username` {#mc-conf.notify_elasticsearch.username}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于连接启用了认证的 Elasticsearch 服务端点的用户名。

### Password {#password}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_PASSWORD` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch password` {#mc-conf.notify_elasticsearch.password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于连接启用了认证的 Elasticsearch 服务端点的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当该值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 的返回内容一部分时，MinIO 会对其进行脱敏。

### 队列目录 {#id6}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_QUEUE_DIR` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch queue_dir` {#mc-conf.notify_elasticsearch.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 针对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 Elasticsearch 服务离线时，MinIO 会将未投递事件存储在指定存储中，并在连接恢复后重放这些已存储事件。

### 队列上限 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch queue_limit` {#mc-conf.notify_elasticsearch.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认为 `100000`。

### 注释 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_ELASTICSEARCH_COMMENT` {#envvar.MINIO_NOTIFY_ELASTICSEARCH_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_elasticsearch comment` {#mc-conf.notify_elasticsearch.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 Elasticsearch 配置关联的注释。