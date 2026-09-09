---
title: "PostgreSQL 通知设置"

weight: 80
---

<a id="postgresql"></a>
<a id="minio-server-config-bucket-notification-postgresql"></a>
<a id="minio-server-envvar-bucket-notification-postgresql"></a>

本页记录了将 PostgreSQL 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 PostgreSQL](/docs/administration/monitoring/publish-events-to-postgresql/#minio-bucket-notifications-publish-postgresql)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

> [!IMPORTANT]
> **SILO 要求完整连接串**
>
> PostgreSQL 通知必须使用 `connection_string` 或 `MINIO_NOTIFY_POSTGRES_CONNECTION_STRING`。2020 年前的离散 `HOST`、`PORT`、`USERNAME`、`PASSWORD`、`DATABASE` 形式没有接入当前配置解析，也不会被自动迁移。
>
> 已启用但缺少 `connection_string` 的旧 target 会让 SILO 以可操作错误中止启动。升级前请将其转换为完整 libpq 连接串，或禁用/删除该 target。兼容性决策与实现证据见 [DSN-only 设计归档](/blog/design/notify-url/)。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 PostgreSQL 目标 {#id2}

你可以通过在顶层键后追加唯一标识符 `_ID`，为每组相关 PostgreSQL 设置指定多个 PostgreSQL 服务端点。 例如，以下命令分别将两个不同的 PostgreSQL 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_NOTIFY_POSTGRES_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_POSTGRES_CONNECTION_STRING_PRIMARY="host=postgresql-endpoint.example.net port=4222..."
export MINIO_NOTIFY_POSTGRES_TABLE_PRIMARY="minioevents"
export MINIO_NOTIFY_POSTGRES_FORMAT_PRIMARY="namespace"

export MINIO_NOTIFY_POSTGRES_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_POSTGRES_CONNECTION_STRING_SECONDARY="host=postgresql-endpoint.example.net port=4222..."
export MINIO_NOTIFY_POSTGRES_TABLE_SECONDARY="minioevents"
export MINIO_NOTIFY_POSTGRES_FORMAT_SECONDARY="namespace"
```

```shell {tab="配置设置" value="tab2"}
mc admin config set notify_postgres:primary \
   connection_string="host=postgresql.example.com port=5432..."
   table="minioevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]

mc admin config set notify_postgres:secondary \
   connection_string="host=postgresql.example.com port=5432..."
   table="minioevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]
```

在这些设置中，[`MINIO_NOTIFY_POSTGRES_ENABLE_PRIMARY`](#envvar.MINIO_NOTIFY_POSTGRES_ENABLE) 表示该环境变量关联到 ID 为 `PRIMARY` 的 PostgreSQL 服务端点。

## 设置 {#id3}

### 启用 {#id4}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_ENABLE` {#envvar.MINIO_NOTIFY_POSTGRES_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 PostgreSQL 服务端点。

默认为 `off`。

如果设置为 `on`，则还必须指定以下环境变量：

- [`MINIO_NOTIFY_POSTGRES_CONNECTION_STRING`](#envvar.MINIO_NOTIFY_POSTGRES_CONNECTION_STRING)
- [`MINIO_NOTIFY_POSTGRES_TABLE`](#envvar.MINIO_NOTIFY_POSTGRES_TABLE)
- [`MINIO_NOTIFY_POSTGRES_FORMAT`](#envvar.MINIO_NOTIFY_POSTGRES_FORMAT)
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres` {#mc-conf.notify_postgres}

*mc-conf*

用于定义 PostgreSQL 服务端点的顶层配置键，可用于 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 PostgreSQL 服务端点。 每个目标都 *必须* 提供以下参数：

- [`connection_string`](#mc-conf.notify_postgres.connection_string)
- [`table`](#mc-conf.notify_postgres.table)
- [`format`](#mc-conf.notify_postgres.format)

其他可选参数以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set notify_postgres                            \
  connection_string="host=postgresql.example.com port=5432..." \
  table="minioevents"                                          \
  format="namespace"                                           \
  [ARGUMENT="VALUE"] ...
```
{{< /tab >}}
{{< /tabs >}}

### 连接字符串 {#id5}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_CONNECTION_STRING` {#envvar.MINIO_NOTIFY_POSTGRES_CONNECTION_STRING}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres connection_string` {#mc-conf.notify_postgres.connection_string}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 PostgreSQL 服务端点的 [URI connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。 MinIO 支持 `key=value` 格式的 PostgreSQL 连接字符串。 例如：

`"host=postgresql.example.com port=5432 dbname=minioevents user=postgres password=secret sslmode=disable"`

有关受支持 PostgreSQL 连接字符串参数的完整文档，请参阅 [PostgreSQL Connection Strings documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### 表 {#id6}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_TABLE` {#envvar.MINIO_NOTIFY_POSTGRES_TABLE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres table` {#mc-conf.notify_postgres.table}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布事件通知的 PostgreSQL 表名称。

### 格式 {#id7}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_FORMAT` {#envvar.MINIO_NOTIFY_POSTGRES_FORMAT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres format` {#mc-conf.notify_postgres.format}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定写入 PostgreSQL 服务端点的事件数据格式。 MinIO 支持以下取值：

**`namespace`**

> 对于每个存储桶事件，MinIO 会创建一个 JSON 文档，使用事件中的存储桶和对象名称作为文档 ID，并将实际事件作为文档内容的一部分。 对该对象的后续更新会修改该对象在表中的现有条目。 同样，删除该对象也会删除对应的表条目。

**`access`**

> 对于每个存储桶事件，MinIO 会创建包含事件详情的 JSON 文档，并以 PostgreSQL 生成的随机 ID 将其追加到表中。 对对象的后续更新会产生新的索引条目，现有条目保持不变。

### 最大打开连接数 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_MAX_OPEN_CONNECTIONS` {#envvar.MINIO_NOTIFY_POSTGRES_MAX_OPEN_CONNECTIONS}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres max_open_connections` {#mc-conf.notify_postgres.max_open_connections}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 PostgreSQL 数据库建立的最大打开连接数。

默认为 `2`。

### 队列目录 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_QUEUE_DIR` {#envvar.MINIO_NOTIFY_POSTGRES_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres queue_dir` {#mc-conf.notify_postgres.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 的持久化事件存储，用于保存未投递消息，例如 `/opt/minio/events`。

当 PostgreSQL server/broker 离线时，MinIO 会将未投递事件存储在指定存储中，并在连接恢复后重放这些已存储事件。

### 队列上限 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_POSTGRES_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres queue_limit` {#mc-conf.notify_postgres.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的数量上限。 默认为 `100000`。

### 注释 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_POSTGRES_COMMENT` {#envvar.MINIO_NOTIFY_POSTGRES_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_postgres comment` {#mc-conf.notify_postgres.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 PostgreSQL 配置关联的注释。