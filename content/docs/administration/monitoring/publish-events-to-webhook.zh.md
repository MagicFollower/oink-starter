---
title: "将事件发布到 Webhook"

weight: 100
---

<a id="webhook"></a>
<a id="minio-bucket-notifications-publish-webhook"></a>

MinIO 支持将 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [Webhook](https://en.wikipedia.org/wiki/Webhook) 服务端点。

## 向 MinIO 部署添加 Webhook 端点 {#minio-webhook}

以下过程会为 MinIO 部署新增一个 Webhook 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### MinIO `mc` 命令行工具 {#minio-mc}

本过程中的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 向 MinIO 添加 Webhook 端点 {#id3}

你可以使用环境变量，或通过设置运行时配置项来配置新的 Webhook 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-envvar-bucket-notification-webhook) 指定 Webhook 服务端点及其相关配置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下一次启动时 应用这些设置。

以下示例代码设置了配置 Webhook 服务端点所需的 *全部* 环境变量。 最低 *必需* 变量为 [`MINIO_NOTIFY_WEBHOOK_ENABLE`](/docs/reference/minio-server/settings/notifications/webhook-service/#envvar.MINIO_NOTIFY_WEBHOOK_ENABLE) 和 [`MINIO_NOTIFY_WEBHOOK_ENDPOINT`](/docs/reference/minio-server/settings/notifications/webhook-service/#envvar.MINIO_NOTIFY_WEBHOOK_ENDPOINT)：

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_WEBHOOK_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_WEBHOOK_ENDPOINT_<IDENTIFIER>="ENDPOINT"
>    set MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_WEBHOOK_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_WEBHOOK_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_WEBHOOK_CLIENT_CERT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_WEBHOOK_CLIENT_KEY_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_WEBHOOK_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_WEBHOOK_ENDPOINT_<IDENTIFIER>="ENDPOINT"
>    export MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_WEBHOOK_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_WEBHOOK_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_WEBHOOK_CLIENT_CERT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_WEBHOOK_CLIENT_KEY_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为该 Webhook 服务端点的唯一描述性字符串。 对于与新目标服务端点相关的所有环境变量，请使用相同的 `<IDENTIFIER>` 值。以下示例假设该标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的 Webhook 服务端点匹配，新设置会 *覆盖* 该端点的任何现有设置。可使用 [`mc admin config get notify_webhook`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前配置的 Webhook 端点。
- 将 `<ENDPOINT>` 替换为 Webhook 服务端点的 URL。例如：

  `https://webhook.example.com`

有关每个环境变量的完整文档，请参见 [用于存储桶通知的 Webhook 服务](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-envvar-bucket-notification-webhook)。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上，使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_webhook`](/docs/reference/minio-server/settings/notifications/webhook-service/#mc-conf.notify_webhook) 配置键来添加或更新 Webhook 端点。 你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用任何新增或更新的 配置设置。

以下示例代码设置了配置 Webhook 服务端点所需的 *全部* 设置。 最低 *必需* 设置为 [`notify_webhook endpoint`](/docs/reference/minio-server/settings/notifications/webhook-service/#mc-conf.notify_webhook.endpoint)：

```shell
mc admin config set ALIAS/ notify_webhook:IDENTIFIER \
   endpoint="<ENDPOINT>" \
   auth_token="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   client_cert="<string>" \
   client_key="<string>"
```

- 将 `IDENTIFIER` 替换为该 Webhook 服务端点的唯一描述性字符串。 本过程后续示例假设该标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的 Webhook 服务端点匹配，新设置会 *覆盖* 该端点的任何现有设置。可使用 [`mc admin config get notify_webhook`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前配置的 Webhook 端点。
- 将 `ENDPOINT` 替换为 Webhook 服务端点的 URL。例如：

  `https://webhook.example.com`

有关每个设置的完整文档，请参见 [Webhook 存储桶通知配置设置](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-config-bucket-notification-webhook)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 Webhook 目标打印一行， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:webhook
```

在将关联的 Webhook 部署配置为目标时，你必须在配置存储桶通知时指定该 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:webhook`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:webhook`。

### 3) 使用 Webhook 端点作为目标来配置存储桶通知 {#id4}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令添加新的存储桶通知事件，并将已配置的 Webhook 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:webhook \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置该事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会针对这些事件触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 可查看给定通知目标的所有已配置存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:webhook
```

### 4) 验证已配置的事件 {#id5}

对配置了新事件的存储桶执行相应操作，并检查 Webhook 服务中的通知数据。 所需操作取决于在配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 你可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象，从而触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 Webhook 端点 {#id6}

以下过程会更新 MinIO 部署中现有的 Webhook 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id7}

#### MinIO `mc` 命令行工具 {#id8}

本过程中的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 Webhook 端点 {#id9}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 Webhook 服务端点：

```shell
mc admin config get ALIAS/ notify_webhook
```

将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

该命令输出类似如下：

```shell
notify_webhook:primary endpoint="https://webhook.example.com" auth_token="" queue_limit="0" queue_dir="" client_cert="" client_key=""
notify_webhook:secondary endpoint="https://webhook.example.com" auth_token="" queue_limit="0" queue_dir="" client_cert="" client_key=""
```

[`notify_webhook`](/docs/reference/minio-server/settings/notifications/webhook-service/#mc-conf.notify_webhook) 键是 [Webhook 服务通知设置](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-config-bucket-notification-webhook) 的顶层配置键。 [`endpoint`](/docs/reference/minio-server/settings/notifications/webhook-service/#mc-conf.notify_webhook.endpoint) 键为给定的 *notify_webhook* 键指定 Webhook 服务端点。`notify_webhook:<IDENTIFIER>` 后缀描述该 Webhook 服务端点的唯一标识符。

记下你想在下一步更新的 Webhook 服务端点标识符。

### 2) 更新 Webhook 端点 {#id10}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 Webhook 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_webhook:IDENTIFIER \
   endpoint="<ENDPOINT>" \
   auth_token="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   client_cert="<string>" \
   client_key="<string>"
```

[`notify_webhook endpoint`](/docs/reference/minio-server/settings/notifications/webhook-service/#mc-conf.notify_webhook.endpoint) 配置设置 是 Webhook 服务端点的 *最低* 必需项。其他所有配置设置均为 *可选*。 有关 Webhook 配置设置的完整列表，请参见 [Webhook 服务通知设置](/docs/reference/minio-server/settings/notifications/webhook-service/#minio-server-config-bucket-notification-webhook)。

### 3) 重启 MinIO 部署 {#id11}

你必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 Webhook 目标打印一行， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:webhook
```

### 4) 验证变更 {#id12}

对某个使用已更新 Webhook 服务端点进行事件配置的存储桶执行相应操作， 并检查 Webhook 服务中的通知数据。所需操作取决于在配置存储桶通知时 指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 你可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象，从而触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```