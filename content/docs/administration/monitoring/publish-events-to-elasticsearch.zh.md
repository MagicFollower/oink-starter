---
title: "将事件发布到 Elasticsearch"

weight: 50
---

<a id="elasticsearch"></a>
<a id="minio-bucket-notifications-publish-elasticsearch"></a>

MinIO 支持将 [bucket notification](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [Elasticsearch](https://www.elastic.co/) 服务端点。

MinIO 依赖 [https://github.com/elastic/go-elasticsearch](https://github.com/elastic/go-elasticsearch) v7 项目连接 Elastic。

## 为 MinIO 部署添加 Elasticsearch 端点 {#minio-elasticsearch}

以下步骤为 MinIO 部署添加一个新的 Elasticsearch 服务端点，以支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### Elasticsearch v7.0 及更高版本 {#elasticsearch-v7-0}

MinIO 依赖 [https://github.com/olivere/elastic](https://github.com/olivere/elastic) v7 项目连接 Elastic。`elastic/v7` 库专门面向 Elasticsearch v7.0，与更早版本的 Elasticsearch 不兼容。

#### MinIO `mc` 命令行工具 {#minio-mc}

本步骤中的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 将 Elasticsearch 端点添加到 MinIO {#elasticsearch-minio}

你可以使用环境变量，*或* 通过设置运行时配置项来配置新的 Elasticsearch 服务端点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
MinIO 支持使用 [environment variables](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-envvar-bucket-notification-elasticsearch) 指定 Elasticsearch 服务端点及其相关配置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次 启动时应用这些设置。

以下示例代码设置了配置 Elasticsearch 服务端点所需的 *全部* 环境变量。 最少 *必须* 设置的变量包括：

- [`MINIO_NOTIFY_ELASTICSEARCH_ENABLE`](/docs/reference/minio-server/settings/notifications/elasticsearch/#envvar.MINIO_NOTIFY_ELASTICSEARCH_ENABLE)
- [`MINIO_NOTIFY_ELASTICSEARCH_URL`](/docs/reference/minio-server/settings/notifications/elasticsearch/#envvar.MINIO_NOTIFY_ELASTICSEARCH_URL)
- [`MINIO_NOTIFY_ELASTICSEARCH_INDEX`](/docs/reference/minio-server/settings/notifications/elasticsearch/#envvar.MINIO_NOTIFY_ELASTICSEARCH_INDEX)
- [`MINIO_NOTIFY_ELASTICSEARCH_FORMAT`](/docs/reference/minio-server/settings/notifications/elasticsearch/#envvar.MINIO_NOTIFY_ELASTICSEARCH_FORMAT)

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_ELASTICSEARCH_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_ELASTICSEARCH_URL_<IDENTIFIER>="<ENDPOINT>"
>    set MINIO_NOTIFY_ELASTICSEARCH_INDEX_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_FORMAT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_USERNAME_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_PASSWORD_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_ELASTICSEARCH_COMMENT_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_ELASTICSEARCH_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_ELASTICSEARCH_URL_<IDENTIFIER>="<ENDPOINT>"
>    export MINIO_NOTIFY_ELASTICSEARCH_INDEX_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_FORMAT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_USERNAME_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_PASSWORD_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_ELASTICSEARCH_COMMENT_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为目标服务端点的唯一描述性字符串。 与新目标服务端点相关的所有环境变量都应使用相同的 `<IDENTIFIER>` 值。 以下示例假定该标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的 Elasticsearch 服务端点匹配，则新设置会 *覆盖* 该端点的现有设置。使用 [`mc admin config get notify_elasticsearch`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署中当前已配置的 Elasticsearch 端点。
- 将 `<ENDPOINT>` 替换为 Elasticsearch 服务端点的 URL。 例如：

有关各环境变量的完整说明，请参见 [Elasticsearch Service for 存储桶通知](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-envvar-bucket-notification-elasticsearch)。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上，使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_elasticsearch`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch) 配置键来添加或更新 Elasticsearch 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用新增或更新后的配置项。

以下示例代码设置了配置 Elasticsearch 服务端点相关的 *全部* 配置项。 最少 *必须* 设置的配置项包括：

- [`url`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch.url)
- [`index`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch.index)
- [`format`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch.format)

```shell
mc admin config set ALIAS/ notify_elasticsearch:IDENTIFIER \
   url="ENDPOINT" \
   index="<string>" \
   format="<string>" \
   username="<string>" \
   password="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为 Elasticsearch 服务端点的唯一描述性字符串。 本步骤中的后续示例假定该标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的 Elasticsearch 服务 端点匹配，则新设置会 *覆盖* 该端点的现有设置。使用 [`mc admin config get notify_elasticsearch`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署中当前已配置的 Elasticsearch 端点。
- 将 `ENDPOINT` 替换为 Elasticsearch 服务端点的 URL。 例如：

  `https://user:password@hostname:port`

有关各配置项的完整说明，请参见 [Elasticsearch Bucket Notification Configuration Settings](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-config-bucket-notification-elasticsearch)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为需要重启的部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 Elasticsearch 目标输出一行， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:elasticsearch
```

在将关联的 Elasticsearch 部署配置为存储桶通知目标时，你必须指定该 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:elasticsearch`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:elasticsearch`。

### 3) 将 Elasticsearch 端点配置为存储桶通知目标 {#id3}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令新增存储桶通知事件，并将已配置的 Elasticsearch 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:elasticsearch \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置该事件的存储桶名称。
- 将 `EVENTS` 替换为一个以逗号分隔的 [events](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会针对这些事件触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标已配置的所有存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:elasticsearch
```

### 4) 验证已配置的事件 {#id4}

对已配置新事件的存储桶执行某项操作，然后检查 Elasticsearch 服务中的通知数据。 所需执行的操作取决于配置存储桶通知时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 Elasticsearch 端点 {#id5}

以下步骤更新 MinIO 部署中现有的 Elasticsearch 服务端点，以支持 [bucket notifications](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id6}

#### Elasticsearch v7.0 及更高版本 {#id7}

MinIO 依赖 [https://github.com/olivere/elastic](https://github.com/olivere/elastic) v7 项目连接 Elastic。`elastic/v7` 库专门面向 Elasticsearch v7.0，与更早版本的 Elasticsearch 不兼容。

#### MinIO `mc` 命令行工具 {#id8}

本步骤中的部分操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [Quickstart](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 Elasticsearch 端点 {#id9}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出部署中当前已配置的 Elasticsearch 服务端点：

```shell
mc admin config get ALIAS/ notify_elasticsearch
```

将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_elasticsearch:primary  queue_dir="" queue_limit="0"  url="https://user:password@hostname:port" format="namespace" index=""
notify_elasticsearch:secondary queue_dir="" queue_limit="0"  url="https://user:password@hostname:port" format="namespace" index=""
```

[`notify_elasticsearch`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch) 键是 [Elasticsearch 通知设置](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-config-bucket-notification-elasticsearch) 的顶层配置键。 [`url`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch.url) 键指定给定 *notify_elasticsearch* 键对应的 Elasticsearch 服务端点。 `notify_elasticsearch:<IDENTIFIER>` 后缀表示该 Elasticsearch 服务端点的 唯一标识符。

记下你要更新的 Elasticsearch 服务端点标识符，以便下一步使用。

### 2) 更新 Elasticsearch 端点 {#id10}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 Elasticsearch 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_elasticsearch:<IDENTIFIER> \
   url="https://user:password@hostname:port" \
   index="<string>" \
   format="<string>" \
   username="<string>" \
   password="<string>" \
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

[`notify_elasticsearch url`](/docs/reference/minio-server/settings/notifications/elasticsearch/#mc-conf.notify_elasticsearch.url) 配置项是 Elasticsearch 服务端点 *最少* 必须设置的项。其他所有配置项均为 *可选*。 完整的 Elasticsearch 配置项列表，请参见 [Elasticsearch 通知设置](/docs/reference/minio-server/settings/notifications/elasticsearch/#minio-server-config-bucket-notification-elasticsearch)。

### 3) 重启 MinIO 部署 {#id11}

你必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为需要重启的部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在启动时为每个已配置的 Elasticsearch 目标输出一行， 类似如下：

```shell
SQS ARNs: arn:minio:sqs::primary:elasticsearch
```

### 4) 验证变更 {#id12}

对某个已使用更新后 Elasticsearch 服务端点配置事件的存储桶执行操作，然后检查 Elasticsearch 服务中的通知数据。所需执行的操作取决于配置存储桶通知时指定了哪些 [`events`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件，则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```