---
title: "将事件发布到 AMQP (RabbitMQ)"

weight: 10
---

<a id="amqp-rabbitmq"></a>
<a id="minio-bucket-notifications-publish-amqp"></a>

MinIO 支持将 [bucket notification](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [AMQP 0-9-1](https://www.amqp.org/) 服务端点，例如 [RabbitMQ](https://www.rabbitmq.com)。

MinIO 依赖 [https://github.com/streadway/amqp](https://github.com/streadway/amqp) 项目实现 AMQP 连接。该项目主要针对 [RabbitMQ](https://www.rabbitmq.com/) 部署进行测试，但其他兼容 [AMQP 0-9-1](https://www.amqp.org/) 的服务也可能可以使用。本页中的步骤假定服务端点为使用 AMQP 0-9-1 协议的 RabbitMQ 部署。

## 向 MinIO 部署添加 AMQP 端点 {#minio-amqp}

以下步骤用于向 MinIO 部署添加一个新的 AMQP 服务端点，以支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### AMQP 0-9-1 服务端点 {#amqp-0-9-1}

MinIO 依赖 [https://github.com/streadway/amqp](https://github.com/streadway/amqp) 项目实现 AMQP 连接。该项目主要针对 [RabbitMQ](https://www.rabbitmq.com/) 部署进行测试，但其他兼容 [AMQP 0-9-1-compatible](https://www.amqp.org/) 的服务也可能可以使用。 本步骤假定服务端点为使用 0-9-1 协议的 RabbitMQ 部署。

如果 AMQP 服务要求身份验证，则你必须在配置过程中提供相应的用户名和密码，以授权 MinIO 访问该服务。

#### MinIO `mc` 命令行工具 {#minio-mc}

本步骤在部分操作中使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 向 MinIO 添加 AMQP 端点 {#id3}

你可以使用环境变量或运行时配置设置来配置新的 AMQP 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [environment variables](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-envvar-bucket-notification-amqp) 指定 AMQP 服务端点及其关联配置设置。 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下一次启动时应用这些设置。

以下示例代码设置了配置 AMQP 服务端点相关的全部环境变量。 必需的最小变量为 [`MINIO_NOTIFY_AMQP_ENABLE`](/docs/reference/minio-server/settings/notifications/amqp/#envvar.MINIO_NOTIFY_AMQP_ENABLE) 和 [`MINIO_NOTIFY_AMQP_URL`](/docs/reference/minio-server/settings/notifications/amqp/#envvar.MINIO_NOTIFY_AMQP_URL)：

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_AMQP_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_AMQP_URL_<IDENTIFIER>="<ENDPOINT>"
>    set MINIO_NOTIFY_AMQP_EXCHANGE_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_EXCHANGE_TYPE_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_ROUTING_KEY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_MANDATORY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_DURABLE_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_NO_WAIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_INTERNAL_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_AUTO_DELETED_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_DELIVERY_MODE_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_AMQP_COMMENT_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_AMQP_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_AMQP_URL_<IDENTIFIER>="<ENDPOINT>"
>    export MINIO_NOTIFY_AMQP_EXCHANGE_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_EXCHANGE_TYPE_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_ROUTING_KEY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_MANDATORY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_DURABLE_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_NO_WAIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_INTERNAL_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_AUTO_DELETED_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_DELIVERY_MODE_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_AMQP_COMMENT_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为该 AMQP 服务端点的唯一描述性字符串。与新 AMQP 服务端点相关的所有环境变量都应使用相同的 `<IDENTIFIER>` 值。以下示例假定标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的某个 AMQP 服务端点匹配，则新设置会覆盖该端点的任何现有设置。使用 [`mc admin config get notify_amqp`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前已配置的 AMQP 端点。
- 将 `<ENDPOINT>` 替换为 AMQP 服务端点的 URL。 例如：

  `amqp://user:password@hostname:port`

参见 [AMQP Service for 存储桶通知](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-envvar-bucket-notification-amqp)，获取每个环境变量的完整文档。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上，使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_amqp`](/docs/reference/minio-server/settings/notifications/amqp/#mc-conf.notify_amqp) 配置键来添加或更新 AMQP 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用任何新增或更新的配置设置。

以下示例代码设置了配置 AMQP 服务端点相关的全部设置。 必需的最小设置为 [`notify_amqp url`](/docs/reference/minio-server/settings/notifications/amqp/#mc-conf.notify_amqp.url)：

```shell
mc admin config set ALIAS/ notify_amqp:IDENTIFIER \
  url="ENDPOINT" \
  exchange="<string>" \
  exchange_type="<string>" \
  routing_key="<string>" \
  mandatory="<string>" \
  durable="<string>" \
  no_wait="<string>" \
  internal="<string>" \
  auto_deleted="<string>" \
  delivery_mode="<string>" \
  queue_dir="<string>" \
  queue_limit="<string>" \
  comment="<string>"
```

- 将 `IDENTIFIER` 替换为该 AMQP 服务端点的唯一描述性字符串。本步骤中的后续示例假定标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的某个 AMQP 服务端点匹配，则新设置会覆盖该端点的任何现有设置。使用 [`mc admin config get notify_amqp`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前已配置的 AMQP 端点。
- 将 `ENDPOINT` 替换为 AMQP 服务端点的 URL。 例如：

  `amqp://user:password@hostname:port`

参见 [AMQP Bucket Notification Configuration Settings](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-config-bucket-notification-amqp)，获取每个设置的完整文档。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 AMQP 目标打印一行类似如下的内容：

```shell
SQS ARNs: arn:minio:sqs::primary:amqp
```

在将关联的 AMQP 部署配置为目标时，你必须在 bucket notification 配置中指定该 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:amqp`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:amqp`。

### 3) 使用 AMQP 端点作为目标配置 存储桶通知 {#amqp}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令新增 bucket notification 事件，并将已配置的 AMQP 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:amqp \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [events](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会在这些事件发生时触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标上已配置的所有 bucket 事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:amqp
```

### 4) 验证已配置的事件 {#id4}

对配置了新事件的存储桶执行一个操作，并检查 AMQP 服务中的通知数据。所需的具体操作取决于配置 bucket notification 时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果 bucket notification 配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在该存储桶中创建一个新对象，并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 AMQP 端点 {#id5}

以下步骤用于更新 MinIO 部署中现有的 AMQP 服务端点，以支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id6}

#### AMQP 0-9-1 服务端点 {#id7}

MinIO 依赖 [https://github.com/streadway/amqp](https://github.com/streadway/amqp) 项目实现 AMQP 连接。该项目主要针对 [RabbitMQ](https://www.rabbitmq.com/) 部署进行测试，但其他兼容 [AMQP 0-9-1-compatible](https://www.amqp.org/) 的服务也可能可以使用。 本步骤假定服务端点为 RabbitMQ 部署。

如果 AMQP 服务要求身份验证，则你必须在配置过程中提供相应的用户名和密码，以授权 MinIO 访问该服务。

#### MinIO `mc` 命令行工具 {#id8}

本步骤在部分操作中使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 AMQP 端点 {#id9}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 AMQP 服务端点：

```shell
mc admin config get ALIAS/ notify_amqp
```

将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_amqp:primary delivery_mode="0" exchange_type="" no_wait="off" queue_dir="" queue_limit="0"  url="amqp://user:password@hostname:port" auto_deleted="off" durable="off" exchange="" internal="off" mandatory="off" routing_key=""
notify_amqp:secondary delivery_mode="0" exchange_type="" no_wait="off" queue_dir="" queue_limit="0"  url="amqp://user:password@hostname:port" auto_deleted="off" durable="off" exchange="" internal="off" mandatory="off" routing_key=""
```

[`notify_amqp`](/docs/reference/minio-server/settings/notifications/amqp/#mc-conf.notify_amqp) 键是 [AMQP 通知设置](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-config-bucket-notification-amqp) 的顶层配置键。 [`url`](/docs/reference/minio-server/settings/notifications/amqp/#mc-conf.notify_amqp.url) 键为给定的 *notify_amqp* 键指定 AMQP 服务端点。 `notify_amqp:<IDENTIFIER>` 后缀表示该 AMQP 服务端点的唯一标识符。

记下你要更新的 AMQP 服务端点标识符，以供下一步使用。

### 2) 更新 AMQP 端点 {#id10}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为该 AMQP 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_amqp:<IDENTIFIER> \
   url="amqp://user:password@hostname:port" \
   exchange="<string>" \
   exchange_type="<string>" \
   routing_key="<string>" \
   mandatory="<string>" \
   durable="<string>" \
   no_wait="<string>" \
   internal="<string>" \
   auto_deleted="<string>" \
   delivery_mode="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

[`notify_amqp url`](/docs/reference/minio-server/settings/notifications/amqp/#mc-conf.notify_amqp.url) 配置设置是 AMQP 服务端点所需的最小配置。其他所有配置设置都是可选的。参见 [AMQP 通知设置](/docs/reference/minio-server/settings/notifications/amqp/#minio-server-config-bucket-notification-amqp)，获取完整的 AMQP 配置设置列表。

### 3) 重启 MinIO 部署 {#id11}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 AMQP 目标打印一行类似如下的内容：

```shell
SQS ARNs: arn:minio:sqs::primary:amqp
```

### 4) 验证更改 {#id12}

对某个使用已更新 AMQP 服务端点配置事件的存储桶执行一个操作，并检查 AMQP 服务中的通知数据。所需的具体操作取决于配置 bucket notification 时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果 bucket notification 配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在该存储桶中创建一个新对象，并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```