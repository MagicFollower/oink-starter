---
title: "将事件发布到 MySQL"

weight: 70
---

<a id="mysql"></a>
<a id="minio-bucket-notifications-publish-mysql"></a>

MinIO 支持将 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [MySQL](https://www.mysql.com/) 服务端点。MinIO *仅* 支持 MySQL 5.7.8 及更高版本。

## 向 MinIO 部署添加 MySQL 端点 {#minio-mysql}

以下过程会向 MinIO 部署添加一个新的 MySQL 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 先决条件 {#id2}

#### MySQL 5.7.8 及更高版本 {#mysql-5-7-8}

MinIO 依赖于 MySQL 5.7.8 中引入的功能。

#### MinIO `mc` 命令行工具 {#minio-mc}

此过程会在某些操作中使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参阅 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 将 MySQL 端点添加到 MinIO {#mysql-minio}

你可以使用环境变量 *或* 设置运行时配置设置来配置新的 MySQL 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-envvar-bucket-notification-mysql) 指定 MySQL 服务端点及其相关 配置设置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次启动时应用指定的设置。

以下示例代码设置了与配置 MySQL 服务端点相关的 *所有* 环境变量。最少的 *必需* 变量为：

- [`MINIO_NOTIFY_MYSQL_ENABLE`](/docs/reference/minio-server/settings/notifications/mysql/#envvar.MINIO_NOTIFY_MYSQL_ENABLE)
- [`MINIO_NOTIFY_MYSQL_DSN_STRING`](/docs/reference/minio-server/settings/notifications/mysql/#envvar.MINIO_NOTIFY_MYSQL_DSN_STRING)
- [`MINIO_NOTIFY_MYSQL_TABLE`](/docs/reference/minio-server/settings/notifications/mysql/#envvar.MINIO_NOTIFY_MYSQL_TABLE)
- [`MINIO_NOTIFY_MYSQL_FORMAT`](/docs/reference/minio-server/settings/notifications/mysql/#envvar.MINIO_NOTIFY_MYSQL_FORMAT)

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_MYSQL_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_MYSQL_DSN_STRING_<IDENTIFIER>="user:password@tcp(hostname:port)/database"
>    set MINIO_NOTIFY_MYSQL_TABLE_<IDENTIFIER>="minio-events"
>    set MINIO_NOTIFY_MYSQL_FORMAT_<IDENTIFIER>="namespace|access"
>    set MINIO_NOTIFY_MYSQL_MAX_OPEN_CONNECTIONS_<IDENTIFIER>="2"
>    set MINIO_NOTIFY_MYSQL_QUEUE_DIR_<IDENTIFIER>="/opt/minio/events"
>    set MINIO_NOTIFY_MYSQL_QUEUE_LIMIT_<IDENTIFIER>="100000"
>    set MINIO_NOTIFY_MYSQL_COMMENT_<IDENTIFIER>="MySQL Event Notification Logging for MinIO"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_MYSQL_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_MYSQL_DSN_STRING_<IDENTIFIER>="user:password@tcp(hostname:port)/database"
>    export MINIO_NOTIFY_MYSQL_TABLE_<IDENTIFIER>="minio-events"
>    export MINIO_NOTIFY_MYSQL_FORMAT_<IDENTIFIER>="namespace|access"
>    export MINIO_NOTIFY_MYSQL_MAX_OPEN_CONNECTIONS_<IDENTIFIER>="2"
>    export MINIO_NOTIFY_MYSQL_QUEUE_DIR_<IDENTIFIER>="/opt/minio/events"
>    export MINIO_NOTIFY_MYSQL_QUEUE_LIMIT_<IDENTIFIER>="100000"
>    export MINIO_NOTIFY_MYSQL_COMMENT_<IDENTIFIER>="MySQL Event Notification Logging for MinIO"
> ```

- 将 `<IDENTIFIER>` 替换为该 MySQL 服务端点的唯一描述性字符串。对于与新目标服务端点相关的所有环境变量，请使用相同的 `<IDENTIFIER>` 值。 以下示例假定标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的 MySQL 服务 端点匹配，则新设置会 *覆盖* 该端点的任何现有设置。使用 [`mc admin config get notify_mysql`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前配置的 MySQL 端点。
- 将 `<ENDPOINT>` 替换为 MySQL 服务端点的 DSN。 MinIO 期望采用以下格式：

  `<user>:<password>@tcp(<host>:<port>)/<database>`

  例如：

  `"username:password@tcp(mysql.example.com:3306)/miniodb"`

有关每个环境变量的完整文档，请参阅 [用于存储桶通知的 MySQL 服务](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-envvar-bucket-notification-mysql)。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令 和 [`notify_mysql`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql) 配置键添加或更新 MySQL 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用任何新增或更新的配置设置。

以下示例代码设置了与配置 MySQL 服务端点相关的 *所有* 设置。最少的 *必需* 设置为：

- [`notify_mysql dsn_string`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.dsn_string)
- [`notify_mysql table`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.table)
- [`notify_mysql format`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.format)

```shell
mc admin config set ALIAS/ notify_mysql:IDENTIFIER \
   dsn_string="<ENDPOINT>" \
   table="<string>" \
   format="<string>" \
   max_open_connections="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为该 MySQL 服务端点的唯一描述性字符串。 本过程中的以下示例假定标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的 MySQL 服务 端点匹配，则新设置会 *覆盖* 该端点的任何现有设置。使用 [`mc admin config get notify_mysql`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前配置的 MySQL 端点。
- 将 `<ENDPOINT>` 替换为 MySQL 服务端点的 DSN。 MinIO 期望采用以下格式：

  `<user>:<password>@tcp(<host>:<port>)/<database>`

  例如：

  `"username:password@tcp(mysql.example.com:3306)/miniodb"`

有关每项设置的完整文档，请参阅 [MySQL 存储桶通知配置设置](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-config-bucket-notification-mysql)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署才能应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 MySQL 目标输出一行，类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:mysql
```

当将关联的 MySQL 部署配置为目标时，你必须在配置存储桶通知时指定该 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:mysql`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:mysql`。

### 3) 使用 MySQL 端点作为目标配置存储桶通知 {#id3}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令添加新的存储桶通知事件，并将已配置的 MySQL 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:mysql \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要在其中配置事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会在这些事件发生时触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标上已配置的所有存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:mysql
```

### 4) 验证已配置的事件 {#id4}

对已配置新事件的存储桶执行某个操作，并检查 MySQL 服务中的通知数据。 所需的操作取决于在配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建一个新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 MySQL 端点 {#id5}

以下过程会更新 MinIO 部署中现有的 MySQL 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 先决条件 {#id6}

#### MySQL 5.7.8 及更高版本 {#id7}

MinIO 依赖于 MySQL 5.7.8 中引入的功能。

#### MinIO `mc` 命令行工具 {#id8}

此过程会在某些操作中使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参阅 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 MySQL 端点 {#id9}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 MySQL 服务端点：

```shell
mc admin config get ALIAS/ notify_mysql
```

将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_mysql:primary format="namespace" table="minio_images" dsn_string="user:pass@tcp(mysql.example.com:3306)/miniodb"
notify_mysql:secondary format="namespace" table="minio_images" dsn_string="user:pass@tcp(mysql.example.com:3306)/miniodb"
```

[`notify_mysql`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql) 键是 [MySQL 通知设置](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-config-bucket-notification-mysql) 的顶级配置键。 [`dsn_string`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.dsn_string) 键指定给定 *notify_mysql* 键对应的 MySQL 服务端点。`notify_mysql:<IDENTIFIER>` 后缀描述该 MySQL 服务端点的唯一标识符。

记下你要在下一步更新的 MySQL 服务端点标识符。

### 2) 更新 MySQL 端点 {#id10}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 MySQL 服务端点设置新的配置：

```shell
mc admin config set ALIAS/ notify_mysql:IDENTIFIER \
   dsn_string="<ENDPOINT>" \
   table="<string>" \
   format="<string>" \
   max_open_connections="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

以下配置设置是 MySQL 服务端点的 *最小必需* 项：

- [`notify_mysql dsn_string`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.dsn_string)
- [`notify_mysql table`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.table)
- [`notify_mysql format`](/docs/reference/minio-server/settings/notifications/mysql/#mc-conf.notify_mysql.format)

所有其他配置设置均为 *可选*。有关 MySQL 配置设置的完整列表，请参阅 [MySQL 通知设置](/docs/reference/minio-server/settings/notifications/mysql/#minio-server-config-bucket-notification-mysql)。

### 3) 重启 MinIO 部署 {#id11}

你必须重启 MinIO 部署才能应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 MySQL 目标输出一行，类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:mysql
```

### 4) 验证更改 {#id12}

对一个事件配置使用了更新后 MySQL 服务端点的存储桶执行某个操作，并检查 MySQL 服务中的通知数据。所需的操作取决于在配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建一个新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```