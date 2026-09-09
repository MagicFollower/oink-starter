---
title: "将事件发布到 Kafka"

weight: 60
---

<a id="kafka"></a>
<a id="minio-bucket-notifications-publish-kafka"></a>

MinIO 支持将 [bucket notification](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [Kafka](https://kafka.apache.org/) 服务端点。

MinIO 依赖 [https://github.com/Shopify/sarama](https://github.com/Shopify/sarama) 项目实现 Kafka 连接能力， 并共享该项目对 Kafka 的支持。更多信息请参见 `sarama` 的 [Compatibility and API stability](https://github.com/Shopify/sarama/#compatibility-and-api-stability) 章节。

## 向 MinIO 部署添加 Kafka 端点 {#minio-kafka}

以下过程会在 MinIO 部署中添加一个新的 Kafka 服务端点， 用于支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### Kafka 最低版本与支持版本 {#id3}

MinIO 依赖 [https://github.com/Shopify/sarama](https://github.com/Shopify/sarama) 项目实现 Kafka 连接能力， 并共享该项目对 Kafka 的支持。更多信息请参见 `sarama` 的 [Compatibility and API stability](https://github.com/Shopify/sarama/#compatibility-and-api-stability) 章节。

#### MinIO `mc` 命令行工具 {#minio-mc}

该过程的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 向 MinIO 添加 Kafka 端点 {#id4}

你可以使用环境变量，*或* 通过设置运行时配置项，来配置新的 Kafka 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [environment variables](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-envvar-bucket-notification-kafka) 指定 Kafka 服务端点及其相关配置项。 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次启动时应用这些配置。

以下示例代码设置了配置 Kafka 服务端点相关的 *全部* 环境变量。 最低 *必需* 的变量是 [`MINIO_NOTIFY_KAFKA_ENABLE`](/docs/reference/minio-server/settings/notifications/kafka/#envvar.MINIO_NOTIFY_KAFKA_ENABLE) 和 [`MINIO_NOTIFY_KAFKA_BROKERS`](/docs/reference/minio-server/settings/notifications/kafka/#envvar.MINIO_NOTIFY_KAFKA_BROKERS)：

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_KAFKA_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_KAFKA_BROKERS_<IDENTIFIER>="<ENDPOINT>"
>    set MINIO_NOTIFY_KAFKA_TOPIC_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_SASL_USERNAME_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_SASL_PASSWORD_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_SASL_MECHANISM_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_TLS_CLIENT_AUTH_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_SASL_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_TLS_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_TLS_SKIP_VERIFY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_CLIENT_TLS_CERT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_CLIENT_TLS_KEY_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_VERSION_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_KAFKA_COMMENT_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_KAFKA_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_KAFKA_BROKERS_<IDENTIFIER>="<ENDPOINT>"
>    export MINIO_NOTIFY_KAFKA_TOPIC_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_SASL_USERNAME_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_SASL_PASSWORD_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_SASL_MECHANISM_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_TLS_CLIENT_AUTH_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_SASL_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_TLS_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_TLS_SKIP_VERIFY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_CLIENT_TLS_CERT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_CLIENT_TLS_KEY_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_VERSION_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_KAFKA_COMMENT_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为该 Kafka 服务端点的唯一描述性字符串。 与新目标服务端点相关的所有环境变量都应使用相同的 `<IDENTIFIER>` 值。 以下示例假定标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中已有的 Kafka 服务端点匹配， 新配置会 *覆盖* 该端点的现有配置。 使用 [`mc admin config get notify_kafka`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前已配置的 Kafka 端点。
- 将 `<ENDPOINT>` 替换为逗号分隔的 Kafka broker 列表。 例如：

  `"kafka1.example.com:2021,kafka2.example.com:2021"`

有关每个环境变量的完整说明，请参见 [用于存储桶通知的 Kafka 服务](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-envvar-bucket-notification-kafka)。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上， 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_kafka`](/docs/reference/minio-server/settings/notifications/kafka/#mc-conf.notify_kafka) 配置键来新增或更新 Kafka 端点。 你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用新增或更新后的配置项。

以下示例代码设置了配置 Kafka 服务端点相关的 *全部* 配置项。 最低 *必需* 的配置项是 [`notify_kafka brokers`](/docs/reference/minio-server/settings/notifications/kafka/#mc-conf.notify_kafka.brokers)：

```shell
mc admin config set ALIAS/ notify_kafka:IDENTIFIER \
   brokers="<ENDPOINT>" \
   topic="<string>" \
   sasl_username="<string>" \
   sasl_password="<string>" \
   sasl_mechanism="<string>" \
   tls_client_auth="<string>" \
   tls="<string>" \
   tls_skip_verify="<string>" \
   client_tls_cert="<string>" \
   client_tls_key="<string>" \
   version="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为该 Kafka 服务端点的唯一描述性字符串。 本过程中的以下示例假定标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中已有的 Kafka 服务端点匹配， 新配置会 *覆盖* 该端点的现有配置。 使用 [`mc admin config get notify_kafka`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署当前已配置的 Kafka 端点。
- 将 `ENDPOINT` 替换为逗号分隔的 Kafka broker 列表。 例如：

  `"kafka1.example.com:2021,kafka2.example.com:2021"`

有关每个配置项的完整说明，请参见 [Kafka 存储桶通知配置项](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-config-bucket-notification-kafka)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署才能应用这些配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 Kafka 目标打印一行输出， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:kafka
```

在将关联的 Kafka 部署配置为目标时， 你必须在配置存储桶通知时指定该 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:kafka`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:kafka`。

### 3) 使用 Kafka 端点作为目标配置存储桶通知 {#id5}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令新增存储桶通知事件， 并将已配置的 Kafka 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:kafka \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置该事件的存储桶名称。
- 将 `EVENTS` 替换为逗号分隔的 [events](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会在这些事件发生时触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标上配置的所有存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:kafka
```

### 4) 验证已配置的事件 {#id6}

对配置了新事件的存储桶执行某项操作， 然后在 Kafka 服务中检查通知数据。 所需操作取决于配置存储桶通知时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建一个新对象，以触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 Kafka 端点 {#id7}

以下过程会更新 MinIO 部署中现有的 Kafka 服务端点， 用于支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id8}

#### Kafka 最低版本与支持版本 {#id9}

MinIO 依赖 [https://github.com/Shopify/sarama](https://github.com/Shopify/sarama) 项目实现 Kafka 连接能力， 并共享该项目对 Kafka 的支持。更多信息请参见 `sarama` 的 [Compatibility and API stability](https://github.com/Shopify/sarama/#compatibility-and-api-stability) 章节。

#### MinIO `mc` 命令行工具 {#id10}

该过程的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 Kafka 端点 {#id11}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 Kafka 服务端点：

```shell
mc admin config get ALIAS/ notify_kafka
```

将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_kafka:primary tls_skip_verify="off"  queue_dir="" queue_limit="0" sasl="off" sasl_password="" sasl_username="" tls_client_auth="0" tls="off" brokers="" topic="" client_tls_cert="" client_tls_key="" version=""
notify_kafka:secondary tls_skip_verify="off"  queue_dir="" queue_limit="0" sasl="off" sasl_password="" sasl_username="" tls_client_auth="0" tls="off" brokers="" topic="" client_tls_cert="" client_tls_key="" version=""
```

[`notify_kafka`](/docs/reference/minio-server/settings/notifications/kafka/#mc-conf.notify_kafka) 键是 [Kafka 通知设置](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-config-bucket-notification-kafka) 的顶层配置键。 [`brokers`](/docs/reference/minio-server/settings/notifications/kafka/#mc-conf.notify_kafka.brokers) 键指定给定 *notify_kafka* 键所对应的 Kafka 服务端点。 `notify_kafka:<IDENTIFIER>` 后缀描述了该 Kafka 服务端点的唯一标识符。

记下你要在下一步中更新的 Kafka 服务端点标识符。

### 2) 更新 Kafka 端点 {#id12}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 Kafka 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_kafka:<IDENTIFIER> \
   brokers="https://kafka1.example.net:9200, https://kafka2.example.net:9200" \
   topic="<string>" \
   sasl_username="<string>" \
   sasl_password="<string>" \
   sasl_mechanism="<string>" \
   tls_client_auth="<string>" \
   tls="<string>" \
   tls_skip_verify="<string>" \
   client_tls_cert="<string>" \
   client_tls_key="<string>" \
   version="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

[`notify_kafka brokers`](/docs/reference/minio-server/settings/notifications/kafka/#mc-conf.notify_kafka.brokers) 配置项 是 Kafka 服务端点的 *最低* 必需项。 所有其他配置项均为可选。 有关 Kafka 配置项的完整列表，请参见 [Kafka 通知设置](/docs/reference/minio-server/settings/notifications/kafka/#minio-server-config-bucket-notification-kafka)。

### 3) 重启 MinIO 部署 {#id13}

你必须重启 MinIO 部署才能应用这些配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 Kafka 目标打印一行输出， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:kafka
```

### 4) 验证更改 {#id14}

对某个使用已更新 Kafka 服务端点配置了事件的存储桶执行某项操作， 然后在 Kafka 服务中检查通知数据。 所需操作取决于配置存储桶通知时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建一个新对象，以触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```