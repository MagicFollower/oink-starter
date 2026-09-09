---
title: "MySQL 通知设置"

weight: 50
---

<a id="mysql"></a>
<a id="minio-server-config-bucket-notification-mysql"></a>
<a id="minio-server-envvar-bucket-notification-mysql"></a>

本页记录了将 MySQL 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的相关设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 MySQL](/docs/administration/monitoring/publish-events-to-mysql/#minio-bucket-notifications-publish-mysql)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

> [!IMPORTANT]
> **SILO 要求完整 DSN**
>
> MySQL 通知必须使用 `dsn_string` 或 `MINIO_NOTIFY_MYSQL_DSN_STRING`。2020 年前的离散 `HOST`、`PORT`、`USERNAME`、`PASSWORD`、`DATABASE` 形式没有接入当前配置解析，也不会被自动迁移。
>
> 已启用但缺少 `dsn_string` 的旧 target 会让 SILO 以可操作错误中止启动。升级前请将其转换为完整 MySQL DSN，或禁用/删除该 target。兼容性决策与实现证据见 [DSN-only 设计归档](/blog/design/notify-url/)。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 MySQL 目标 {#id2}

你可以在顶层键后追加唯一标识符 `_ID`，为每组相关的 MySQL 设置指定多个 MySQL 服务端点。

### 示例 {#id3}

以下命令分别将两个不同的 MySQL 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
export MINIO_NOTIFY_MYSQL_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_MYSQL_DSN_STRING_PRIMARY="username:password@tcp(mysql.example.com:3306)/miniodb"
export MINIO_NOTIFY_MYSQL_TABLE_PRIMARY="minioevents"
export MINIO_NOTIFY_MYSQL_FORMAT_PRIMARY="namespace"

export MINIO_NOTIFY_MYSQL_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_MYSQL_DSN_STRING_SECONDARY="username:password@tcp(mysql.example.com:3306)/miniodb"
export MINIO_NOTIFY_MYSQL_TABLE_SECONDARY="minioevents"
export MINIO_NOTIFY_MYSQL_FORMAT_SECONDARY="namespace"
```

在这些设置中，[`MINIO_NOTIFY_MYSQL_ENABLE_PRIMARY`](#envvar.MINIO_NOTIFY_MYSQL_ENABLE) 表示该环境变量关联到 ID 为 `PRIMARY` 的 MySQL 服务端点。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
```shell
mc admin config set notify_mysql:primary \
   dsn_string="username:password@tcp(mysql.example.com:3306)/miniodb"
   table="minioevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]

mc admin config set notify_mysql:secondary \
   dsn_string="username:password@tcp(mysql.example.com:3306)/miniodb"
   table="minioevents" \
   format="namespace" \
   [ARGUMENT=VALUE ...]
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id4}

### 启用 {#id5}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_ENABLE` {#envvar.MINIO_NOTIFY_MYSQL_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 MySQL 服务端点。

默认为 `off`。

若设置为 `on`，则还必须指定以下环境变量：

- [`MINIO_NOTIFY_MYSQL_DSN_STRING`](#envvar.MINIO_NOTIFY_MYSQL_DSN_STRING)
- [`MINIO_NOTIFY_MYSQL_TABLE`](#envvar.MINIO_NOTIFY_MYSQL_TABLE)
- [`MINIO_NOTIFY_MYSQL_FORMAT`](#envvar.MINIO_NOTIFY_MYSQL_FORMAT)
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql` {#mc-conf.notify_mysql}

*mc-conf*

用于定义 MySQL 服务端点以配合 [MinIO bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 使用的顶层配置键。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 MySQL 服务端点。 每个目标都 *必需* 以下参数：

- [`dsn_string`](#mc-conf.notify_mysql.dsn_string)
- [`table`](#mc-conf.notify_mysql.table)
- [`format`](#mc-conf.notify_mysql.format)

其他可选参数请以空白字符（`" "`）分隔列表形式指定。

```shell
mc admin config set notify_mysql \
  dsn_string="username:password@tcp(mysql.example.com:3306)/miniodb"
  table="minioevents" \
  format="namespace" \
  [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### 数据源名称（DSN）字符串 {#dsn}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_DSN_STRING` {#envvar.MINIO_NOTIFY_MYSQL_DSN_STRING}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql dsn_string` {#mc-conf.notify_mysql.dsn_string}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MySQL 服务端点的数据源名称（DSN）。MinIO 期望使用以下格式：

`<user>:<password>@tcp(<host>:<port>)/<database>`

例如：

`"username:password@tcp(mysql.example.com:3306)/miniodb"`

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### 表 {#id6}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_TABLE` {#envvar.MINIO_NOTIFY_MYSQL_TABLE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql table` {#mc-conf.notify_mysql.table}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 发布事件通知到的 MySQL 表名。

### 格式 {#id7}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_FORMAT` {#envvar.MINIO_NOTIFY_MYSQL_FORMAT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql format` {#mc-conf.notify_mysql.format}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定写入 MySQL 服务端点的事件数据格式。 MinIO 支持以下取值：

**`namespace`**

> 对于每个存储桶事件，MinIO 会创建一个 JSON 文档，将事件中的存储桶和对象名称作为文档 ID，并将实际事件作为文档体的一部分。 对该对象的后续更新会修改该对象在表中的现有条目。 同样，删除该对象也会删除对应的表条目。

**`access`**

> 对于每个存储桶事件，MinIO 会创建一个包含事件详情的 JSON 文档，并以 MySQL 生成的随机 ID 追加到表中。 对对象的后续更新会产生新的索引条目，且现有条目保持不变。

### 最大打开连接数 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_MAX_OPEN_CONNECTIONS` {#envvar.MINIO_NOTIFY_MYSQL_MAX_OPEN_CONNECTIONS}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql max_open_connections` {#mc-conf.notify_mysql.max_open_connections}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 MySQL 数据库建立的最大打开连接数。

默认为 `2`。

### 队列目录 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_QUEUE_DIR` {#envvar.MINIO_NOTIFY_MYSQL_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql queue_dir` {#mc-conf.notify_mysql.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径，以启用 MinIO 对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 MySQL 服务器/代理离线时，MinIO 会将未投递事件存储在指定位置；连接恢复后会重放这些已存储事件。

### 队列上限 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_MYSQL_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql queue_limit` {#mc-conf.notify_mysql.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。默认为 `100000`。

### 注释 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MYSQL_COMMENT` {#envvar.MINIO_NOTIFY_MYSQL_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_mysql comment` {#mc-conf.notify_mysql.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 MySQL 配置关联的注释。