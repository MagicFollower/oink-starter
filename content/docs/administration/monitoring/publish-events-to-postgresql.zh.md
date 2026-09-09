---
title: "将事件发布到 PostgreSQL"

weight: 80
---

<a id="postgresql"></a>
<a id="minio-bucket-notifications-publish-postgresql"></a>

MinIO 支持将 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [PostgreSQL](https://www.postgresql.org/)。MinIO 仅支持 PostgreSQL 9.5 及以上版本。

## 向 MinIO 部署添加 PostgreSQL 端点 {#minio-postgresql}

以下过程将为 MinIO 部署新增一个 PostgreSQL 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### PostgreSQL 9.5 及以上版本 {#postgresql-9-5}

MinIO 依赖 PostgreSQL 9.5 引入的特性。

#### MinIO `mc` 命令行工具 {#minio-mc}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 向 MinIO 添加 PostgreSQL 端点 {#id3}

你可以使用环境变量 *或* 运行时配置设置来配置新的 PostgreSQL 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-envvar-bucket-notification-postgresql) 指定 PostgreSQL 服务端点及其相关 配置设置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次启动时应用这些设置。

下面的示例代码设置了与配置 PostgreSQL 服务端点相关的 *全部* 环境变量。 最低 *必需* 的变量如下：

- [`MINIO_NOTIFY_POSTGRES_CONNECTION_STRING`](/docs/reference/minio-server/settings/notifications/postgresql/#envvar.MINIO_NOTIFY_POSTGRES_CONNECTION_STRING)
- [`MINIO_NOTIFY_POSTGRES_TABLE`](/docs/reference/minio-server/settings/notifications/postgresql/#envvar.MINIO_NOTIFY_POSTGRES_TABLE)
- [`MINIO_NOTIFY_POSTGRES_FORMAT`](/docs/reference/minio-server/settings/notifications/postgresql/#envvar.MINIO_NOTIFY_POSTGRES_FORMAT)

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_POSTGRES_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_POSTGRES_CONNECTION_STRING_<IDENTIFIER>="host=postgresql-endpoint.example.net port=4222"
>    set MINIO_NOTIFY_POSTGRES_TABLE_<IDENTIFIER>="minioevents"
>    set MINIO_NOTIFY_POSTGRES_FORMAT_<IDENTIFIER>="namespace|access"
>    set MINIO_NOTIFY_POSTGRES_MAX_OPEN_CONNECTIONS_<IDENTIFIER>="2"
>    set MINIO_NOTIFY_POSTGRES_QUEUE_DIR_<IDENTIFIER>="/opt/minio/events"
>    set MINIO_NOTIFY_POSTGRES_QUEUE_LIMIT_<IDENTIFIER>="100000"
>    set MINIO_NOTIFY_POSTGRES_COMMENT_<IDENTIFIER>="PostgreSQL Notification Event Logging for MinIO"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_POSTGRES_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_POSTGRES_CONNECTION_STRING_<IDENTIFIER>="host=postgresql-endpoint.example.net port=4222"
>    export MINIO_NOTIFY_POSTGRES_TABLE_<IDENTIFIER>="minioevents"
>    export MINIO_NOTIFY_POSTGRES_FORMAT_<IDENTIFIER>="namespace|access"
>    export MINIO_NOTIFY_POSTGRES_MAX_OPEN_CONNECTIONS_<IDENTIFIER>="2"
>    export MINIO_NOTIFY_POSTGRES_QUEUE_DIR_<IDENTIFIER>="/opt/minio/events"
>    export MINIO_NOTIFY_POSTGRES_QUEUE_LIMIT_<IDENTIFIER>="100000"
>    export MINIO_NOTIFY_POSTGRES_COMMENT_<IDENTIFIER>="PostgreSQL Notification Event Logging for MinIO"
> ```

- 将 `<IDENTIFIER>` 替换为 PostgreSQL 服务端点的唯一描述性字符串。 对于与新目标服务端点相关的所有环境变量，请使用相同的 `<IDENTIFIER>` 值。 以下示例假定标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署上现有的 PostgreSQL 服务 端点匹配，则新设置会 *覆盖* 该端点的现有设置。使用 [`mc admin config get notify_postgres`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前配置的 PostgreSQL 端点。
- 将 `<ENDPOINT>` 替换为 PostgreSQL 服务端点的 [PostgreSQL 连接字符串](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。MinIO 支持连接字符串使用 `key=value` 格式。 例如：

  `"host=https://postgresql.example.com port=5432 ..."`

  有关受支持的 PostgreSQL 连接字符串参数的完整文档，请参见 [PostgreSQL 连接字符串](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。

各环境变量的完整文档请参见 [用于存储桶通知的 PostgreSQL 服务](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-envvar-bucket-notification-postgresql)。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在正在运行的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上，使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_postgres`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres) 配置键 来新增或更新 PostgreSQL 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程， 才能应用任何新增或更新的配置设置。

下面的示例代码设置了与配置 PostgreSQL 服务端点相关的 *全部* 设置。 最低 *必需* 的设置如下：

- [`notify_postgres connection_string`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.connection_string)
- [`notify_postgres table`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.table)
- [`notify_postgres format`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.format)

```shell
mc admin config set ALIAS/ notify_postgres:IDENTIFIER \
   connection_string="ENDPOINT" \
   table="<string>" \
   format="<string>" \
   max_open_connections="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为 PostgreSQL 服务端点的唯一描述性字符串。 本过程后续示例假定标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署上现有的 PostgreSQL 服务端点 匹配，则新设置会 *覆盖* 该端点的现有设置。使用 [`mc admin config get notify_postgres`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前配置的 PostgreSQL 端点。
- 将 `<ENDPOINT>` 替换为 PostgreSQL 服务端点的 [PostgreSQL URI 连接字符串](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。 MinIO 支持 PostgreSQL 连接字符串使用 `key=value` 格式。例如：

  `"host=https://postgresql.example.com port=5432 ..."`

  有关受支持的 PostgreSQL 连接字符串参数的完整文档，请参见 [PostgreSQL 连接字符串](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)。

各设置的完整文档请参见 [PostgreSQL 存储桶通知配置设置](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-config-bucket-notification-postgresql)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署才能应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 PostgreSQL 目标输出一行内容， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:postgresql
```

当将关联的 PostgreSQL 部署作为目标配置存储桶通知时，你必须指定该 ARN 资源。

> [!NOTE]
> **识别存储桶通知的 ARN**
>
> 此前创建端点时，你已定义 `<IDENTIFIER>`，用于分配给存储桶通知目标 ARN。 以下步骤会返回该部署上已配置的 ARN。 请通过查找你指定的 `<IDENTIFIER>` 来识别此前创建的 ARN。
>
> **查看 JSON 输出**
>
> 1. 复制并运行以下命令，将 `ALIAS` 替换为该部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
>
>    ```shell
>    mc admin info --json ALIAS
>    ```
>
> 2. 在 JSON 输出中，查找 `info.sqsARN` 键。
>
>    你需要的 ARN 就是该键中与所指定 `<IDENTIFIER>` 匹配的那个值。
>
>    例如，`arn:minio:sqs::primary:postgresql`。
>
> **使用 jq 从 JSON 中解析该值**
>
> 1. [安装 jq](https://stedolan.github.io/jq/)<a id="jq"></a>
> 2. 复制并运行以下命令，将 `ALIAS` 替换为该部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
>
>    ```shell
>    mc admin info --json ALIAS | jq  .info.sqsARN
>    ```
>
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:postgresql`。

### 3) 将 PostgreSQL 端点作为目标配置存储桶通知 {#id4}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令新增一个以已配置 PostgreSQL 服务为目标的 存储桶通知事件：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:postgresql \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置该事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 将在这些事件发生时触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标当前配置的所有存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:postgresql
```

### 4) 验证已配置的事件 {#id5}

对你为其配置了新事件的存储桶执行一个操作，并检查 PostgreSQL 服务中的通知数据。 所需执行的操作取决于配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中新建对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 在 MinIO 部署中更新 PostgreSQL 端点 {#id6}

以下过程将更新 MinIO 部署中现有的 PostgreSQL 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id7}

#### PostgreSQL 9.5 及以上版本 {#id8}

MinIO 依赖 PostgreSQL 9.5 引入的特性。

#### MinIO `mc` 命令行工具 {#id9}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 PostgreSQL 端点 {#id10}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 PostgreSQL 服务端点：

```shell
mc admin config get ALIAS/ notify_postgres
```

将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_postgres:primary queue_dir="" connection_string="postgresql://" queue_limit="0"  table="" format="namespace"
notify_postgres:secondary queue_dir="" connection_string="" queue_limit="0"  table="" format="namespace"
```

[`notify_postgres`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres) 键是 [PostgreSQL 通知设置](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-config-bucket-notification-postgresql) 的顶层配置键。 [`connection_string`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.connection_string) 键为给定的 `notify_postgres` 键指定 PostgreSQL 服务端点。 `notify_postgres:<IDENTIFIER>` 后缀描述该 PostgreSQL 服务端点的唯一标识符。

记下你要更新的 PostgreSQL 服务端点标识符，以便下一步使用。

### 2) 更新 PostgreSQL 端点 {#id11}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令设置 PostgreSQL 服务端点的新配置：

```shell
mc admin config set ALIAS/ notify_postgres:IDENTIFIER \
   connection_string="ENDPOINT" \
   table="<string>" \
   format="<string>" \
   max_open_connections="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

以下配置设置是 PostgreSQL 服务端点的 *最低* 必需项：

- [`notify_postgres connection_string`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.connection_string)
- [`notify_postgres table`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.table)
- [`notify_postgres format`](/docs/reference/minio-server/settings/notifications/postgresql/#mc-conf.notify_postgres.format)

其他所有配置设置均为 *可选*。 完整的 PostgreSQL 配置设置列表请参见 [PostgreSQL 通知设置](/docs/reference/minio-server/settings/notifications/postgresql/#minio-server-config-bucket-notification-postgresql)。

### 3) 重启 MinIO 部署 {#id12}

你必须重启 MinIO 部署才能应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 PostgreSQL 目标输出一行内容， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:postgresql
```

### 4) 验证变更 {#id13}

对某个使用已更新 PostgreSQL 服务端点进行事件配置的存储桶执行操作，并检查 PostgreSQL 服务中的通知数据。所需执行的操作取决于配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中新建对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```