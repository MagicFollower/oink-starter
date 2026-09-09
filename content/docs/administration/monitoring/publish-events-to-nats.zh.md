---
title: "将事件发布到 NATS"

weight: 30
---

<a id="nats"></a>
<a id="minio-bucket-notifications-publish-nats"></a>

MinIO 支持将 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [NATS](https://nats.io/) 服务端点。

> [!NOTE]
> **NATS Streaming 已弃用**
>
> NATS Streaming 已弃用。 请改为迁移到 [JetStream](https://docs.nats.io/nats-concepts/jetstream)。
>
> 相关的 MinIO 配置选项和环境变量也已弃用。

## 向 MinIO 部署添加 NATS 端点 {#minio-nats}

以下过程会在 MinIO 部署中添加一个新的 NATS 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### MinIO `mc` 命令行工具 {#minio-mc}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 将 NATS 端点添加到 MinIO {#nats-minio}

你可以通过环境变量 *或* 运行时配置设置来配置新的 NATS 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/notifications/nats/#minio-server-envvar-bucket-notification-nats) 指定 NATS 服务端点及其相关配置设置。 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次启动时应用这些指定设置。

以下示例代码设置了与配置 NATS 服务端点相关的 *全部* 环境变量。 最低 *必需* 的变量是 [`MINIO_NOTIFY_NATS_ADDRESS`](/docs/reference/minio-server/settings/notifications/nats/#envvar.MINIO_NOTIFY_NATS_ADDRESS) 和 [`MINIO_NOTIFY_NATS_SUBJECT`](/docs/reference/minio-server/settings/notifications/nats/#envvar.MINIO_NOTIFY_NATS_SUBJECT)：

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_NATS_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_NATS_ADDRESS_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_SUBJECT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_USERNAME_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_PASSWORD_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_TOKEN_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_TLS_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_TLS_SKIP_VERIFY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_PING_INTERVAL_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_CERT_AUTHORITY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_CLIENT_CERT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_CLIENT_KEY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_COMMENT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_NATS_JETSTREAM_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_NATS_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_NATS_ADDRESS_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_SUBJECT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_USERNAME_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_PASSWORD_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_TOKEN_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_TLS_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_TLS_SKIP_VERIFY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_PING_INTERVAL_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_CERT_AUTHORITY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_CLIENT_CERT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_CLIENT_KEY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_COMMENT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_NATS_JETSTREAM_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为该 NATS 服务端点的唯一描述性字符串。 对新目标服务端点相关的所有环境变量使用相同的 `<IDENTIFIER>` 值。 以下示例假设标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的 NATS 服务端点匹配，新设置将 *覆盖* 该端点的任何现有设置。 使用 [`mc admin config get notify_nats`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署中当前配置的 NATS 端点。
- 将 `<ENDPOINT>` 替换为 NATS 服务端点的主机名和端口。 例如：`nats-endpoint.example.com:4222`

有关每个环境变量的完整文档，请参见 [用于存储桶通知的 NATS 服务](/docs/reference/minio-server/settings/notifications/nats/#minio-server-envvar-bucket-notification-nats)。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在正在运行的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_nats`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats) 配置键来添加或更新 NATS 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用任何新增或更新的配置 设置。

以下示例代码设置了与配置 NATS 服务端点相关的 *全部* 设置。 最低 *必需* 的设置是 [`notify_nats address`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats.address) 和 [`notify_nats subject`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats.subject)：

```shell
mc admin config set ALIAS/ notify_nats:IDENTIFIER \
   address="HOSTNAME" \
   subject="<string>" \
   username="<string>" \
   password="<string>" \
   token="<string>" \
   nats_jetstream="<string>" \
   tls="<string>" \
   tls_skip_verify="<string>" \
   ping_interval="<string>" \
   cert_authority="<string>" \
   client_cert="<string>" \
   client_key="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为该 NATS 服务端点的唯一描述性字符串。 本过程中的以下示例假设标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的 NATS 服务端点匹配，新设置将 *覆盖* 该端点的任何现有设置。 使用 [`mc admin config get notify_nats`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署中当前配置的 NATS 端点。
- 将 `ENDPOINT` 替换为 NATS 服务端点的主机名和端口。 例如：`nats-endpoint.example.com:4222`。

有关每个设置的完整文档，请参见 [NATS 存储桶通知配置设置](/docs/reference/minio-server/settings/notifications/nats/#minio-server-config-bucket-notification-nats)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 NATS 目标输出一行内容，类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:nats
```

将相关 NATS 部署配置为目标时，你必须在配置存储桶通知时指定 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:nats`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:nats`。

### 3) 将 NATS 端点作为目标来配置存储桶通知 {#id3}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令添加新的存储桶通知事件，并将已配置的 NATS 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:nats \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表， MinIO 会针对这些事件触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标的所有已配置存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:nats
```

### 4) 验证已配置的事件 {#id4}

对已配置新事件的存储桶执行某个操作，并检查 NATS 服务中的通知数据。 所需操作取决于在配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 你可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 NATS 端点 {#id5}

以下过程会更新 MinIO 部署中现有的 NATS 服务端点，以支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id6}

#### MinIO `mc` 命令行工具 {#id7}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 NATS 端点 {#id8}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前配置的 NATS 服务端点：

```shell
mc admin config get ALIAS/ notify_nats
```

将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_nats:primary password="yoursecret" subject="" address="nats-endpoint.example.com:4222"  token="" username="yourusername" ping_interval="0" queue_limit="0" tls="off" tls_skip_verify="off" queue_dir="" streaming_enable="on" nats_jetstream="on"
notify_nats:secondary password="yoursecret" subject="" address="nats-endpoint.example.com:4222"  token="" username="yourusername" ping_interval="0" queue_limit="0" tls="off" tls_skip_verify="off" queue_dir="" streaming_enable="on" nats_jetstream="on"
```

[`notify_nats`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats) 键是 [NATS 通知设置](/docs/reference/minio-server/settings/notifications/nats/#minio-server-config-bucket-notification-nats) 的顶层配置键。 [`address`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats.address) 键为给定的 `notify_nats` 键指定 NATS 服务端点。 `notify_nats:<IDENTIFIER>` 后缀表示该 NATS 服务端点的唯一标识符。

记下你要更新的 NATS 服务端点标识符，以便在下一步中使用。

### 2) 更新 NATS 端点 {#id9}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 NATS 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_nats:IDENTIFIER \
   address="HOSTNAME" \
   subject="<string>" \
   username="<string>" \
   password="<string>" \
   token="<string>" \
   tls="<string>" \
   tls_skip_verify="<string>" \
   ping_interval="<string>" \
   nats_jetstream="<string>" \
   cert_authority="<string>" \
   client_cert="<string>" \
   client_key="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

[`notify_nats address`](/docs/reference/minio-server/settings/notifications/nats/#mc-conf.notify_nats.address) 配置设置是 NATS 服务端点的 *最低* 必需项。 所有其他配置设置均为 *可选*。 有关 NATS 配置设置的完整列表，请参见 [NATS 通知设置](/docs/reference/minio-server/settings/notifications/nats/#minio-server-config-bucket-notification-nats)。

### 3) 重启 MinIO 部署 {#id10}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 NATS 目标输出一行内容，类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:nats
```

### 4) 验证更改 {#id11}

对使用更新后 NATS 服务端点进行事件配置的存储桶执行某个操作， 并检查 NATS 服务中的通知数据。 所需操作取决于在配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 你可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```