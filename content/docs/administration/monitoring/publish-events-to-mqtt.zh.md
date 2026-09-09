---
title: "将事件发布到 MQTT"

weight: 20
---

<a id="mqtt"></a>
<a id="minio-bucket-notifications-publish-mqtt"></a>

MinIO 支持将 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 事件发布到 [MQTT](https://www.mqtt.org/) server/broker 端点。

## 向 MinIO 部署添加 MQTT 端点 {#minio-mqtt}

以下过程会添加一个新的 MQTT 服务端点，以在 MinIO 部署中支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id2}

#### MQTT 3.1 或 3.1.1 服务器/代理 {#mqtt-3-1-3-1-1}

此过程假定已存在一个 MQTT 3.1 或 3.1.1 server/broker，且 MinIO 部署能够连接到它。有关兼容 MQTT 的 server/broker 列表，请参见 [mqtt.org software listing](https://mqtt.org/software/)。

如果 MQTT 服务需要身份验证，则在配置过程中 *必须* 提供适当的用户名和密码， 以授予 MinIO 访问该服务的权限。

#### MinIO `mc` 命令行工具 {#minio-mc}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 将 MQTT 端点添加到 MinIO {#mqtt-minio}

你可以通过环境变量 *或* 运行时配置设置来配置新的 MQTT 服务端点。

{{< tabs group="environment-variables-configuration-settings" >}}
{{< tab label="Environment Variables" value="environment-variables" >}}
MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-envvar-bucket-notification-mqtt) 指定 MQTT 服务端点及其相关 配置设置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下次启动时应用这些设置。

以下示例代码设置了与配置 MQTT 服务端点相关的 *全部* 环境变量。 *最少* 需要以下变量：

- [`MINIO_NOTIFY_MQTT_ENABLE`](/docs/reference/minio-server/settings/notifications/mqtt/#envvar.MINIO_NOTIFY_MQTT_ENABLE)
- [`MINIO_NOTIFY_MQTT_BROKER`](/docs/reference/minio-server/settings/notifications/mqtt/#envvar.MINIO_NOTIFY_MQTT_BROKER)
- [`MINIO_NOTIFY_MQTT_TOPIC`](/docs/reference/minio-server/settings/notifications/mqtt/#envvar.MINIO_NOTIFY_MQTT_TOPIC)
- [`MINIO_NOTIFY_MQTT_USERNAME`](/docs/reference/minio-server/settings/notifications/mqtt/#envvar.MINIO_NOTIFY_MQTT_USERNAME) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*
- [`MINIO_NOTIFY_MQTT_PASSWORD`](/docs/reference/minio-server/settings/notifications/mqtt/#envvar.MINIO_NOTIFY_MQTT_PASSWORD) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*

> [!NOTE]
> **Windows**
>
> ```shell
>    set MINIO_NOTIFY_MQTT_ENABLE_<IDENTIFIER>="on"
>    set MINIO_NOTIFY_MQTT_BROKER_<IDENTIFIER>="ENDPOINT"
>    set MINIO_NOTIFY_MQTT_TOPIC_<IDENTIFIER>="TOPIC"
>    set MINIO_NOTIFY_MQTT_USERNAME_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_PASSWORD_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_QOS_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_KEEP_ALIVE_INTERVAL_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_RECONNECT_INTERVAL_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_QUEUE_DIR_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    set MINIO_NOTIFY_MQTT_COMMENT_<IDENTIFIER>="<string>"
> ```

> [!NOTE]
> **Linux 与 macOS**
>
> ```shell
>    export MINIO_NOTIFY_MQTT_ENABLE_<IDENTIFIER>="on"
>    export MINIO_NOTIFY_MQTT_BROKER_<IDENTIFIER>="ENDPOINT"
>    export MINIO_NOTIFY_MQTT_TOPIC_<IDENTIFIER>="TOPIC"
>    export MINIO_NOTIFY_MQTT_USERNAME_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_PASSWORD_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_QOS_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_KEEP_ALIVE_INTERVAL_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_RECONNECT_INTERVAL_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_QUEUE_DIR_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_QUEUE_LIMIT_<IDENTIFIER>="<string>"
>    export MINIO_NOTIFY_MQTT_COMMENT_<IDENTIFIER>="<string>"
> ```

- 将 `<IDENTIFIER>` 替换为 MQTT 服务端点的唯一描述性字符串。 对所有与新 MQTT 服务端点相关的环境变量都使用相同的 `<IDENTIFIER>` 值。以下示例假定标识符为 `PRIMARY`。

  如果指定的 `<IDENTIFIER>` 与 MinIO 部署中现有的 MQTT 服务端点匹配， 新设置将 *覆盖* 该端点的任何现有设置。使用 [`mc admin config get notify_mqtt`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前配置的 MQTT 端点。
- 将 `<ENDPOINT>` 替换为 MQTT 服务端点的 URL。例如：

  `tcp://hostname:port`
- 将 `TOPIC` 替换为 MQTT topic，MinIO 会将发布到 server/broker 的 事件关联到该 topic。

有关每个环境变量的完整文档，请参见 [用于存储桶通知的 MQTT 服务](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-envvar-bucket-notification-mqtt)。
{{< /tab >}}
{{< tab label="Configuration Settings" value="configuration-settings" >}}
MinIO 支持在运行中的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程上使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令和 [`notify_mqtt`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt) 配置键添加或更新 MQTT 端点。你必须重启 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程，才能应用任何新增或更新的配置设置。

以下示例代码设置了与配置 MQTT 服务端点相关的 *全部* 设置。 对于 MQTT server/broker 端点，以下配置设置是 *最少* 必需项：

- [`broker`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.broker)
- [`topic`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.topic)
- [`username`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.username) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*
- [`password`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.password) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*

```shell
mc admin config set ALIAS/ notify_mqtt:IDENTIFIER \
   broker="ENDPOINT" \
   topic="TOPIC" \
   username="username" \
   password="password" \
   qos="<integer>" \
   keep_alive_interval="60s|m|h|d"
   reconnect_interval="60s|m|h|d"
   queue_dir="<string>" \
   queue_limit="<string>" \
   comment="<string>"
```

- 将 `IDENTIFIER` 替换为 MQTT 服务端点的唯一描述性字符串。 本过程后续示例假定标识符为 `PRIMARY`。

  如果指定的 `IDENTIFIER` 与 MinIO 部署中现有的 MQTT 服务端点匹配， 新设置将 *覆盖* 该端点的任何现有设置。使用 [`mc admin config get notify_mqtt`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 查看 MinIO 部署上当前配置的 MQTT 端点。
- 将 `ENDPOINT` 替换为 MQTT 服务端点的 URL。例如：

  `tcp://hostname:port`
- 将 `TOPIC` 替换为 MQTT topic，MinIO 会将发布到 server/broker 的 事件关联到该 topic。

有关每个设置的完整文档，请参见 [MQTT 存储桶通知配置设置](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-config-bucket-notification-mqtt)。
{{< /tab >}}
{{< /tabs >}}

### 1) 重启 MinIO 部署 {#minio}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 MQTT 目标打印一行类似如下的内容：

```shell
SQS ARNs: arn:minio:sqs::primary:mqtt
```

将关联的 MQTT 部署配置为目标时，你必须在配置存储桶通知时指定 ARN 资源。

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
>    例如，`arn:minio:sqs::primary:mqtt`。
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
>    该命令会返回用于通知的 ARN，例如 `arn:minio:sqs::primary:mqtt`。

### 1) 将 MQTT 端点配置为存储桶通知目标 {#id3}

使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 命令添加新的存储桶通知事件，并将已配置的 MQTT 服务作为目标：

```shell
mc event add ALIAS/BUCKET arn:minio:sqs::primary:mqtt \
  --event EVENTS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要配置该事件的存储桶名称。
- 将 `EVENTS` 替换为以逗号分隔的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events) 列表，MinIO 会为这些事件触发通知。

使用 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 查看给定通知目标已配置的所有存储桶事件：

```shell
mc event ls ALIAS/BUCKET arn:minio:sqs::primary:MQTT
```

### 4) 验证已配置的事件 {#id4}

对已配置新事件的存储桶执行某个操作，并检查 MQTT 服务中的通知数据。 所需操作取决于配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```

## 更新 MinIO 部署中的 MQTT 端点 {#id5}

以下过程会更新现有 MQTT 服务端点，以在 MinIO 部署中支持 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 前提条件 {#id6}

#### MQTT 3.1 或 3.1.1 服务器/代理端点 {#id7}

此过程假定已存在一个 MQTT 3.1 或 3.1.1 server/broker，且 MinIO 部署能够连接到它。有关兼容 MQTT 的 server/broker 列表，请参见 [mqtt.org software listing](https://mqtt.org/software/)。

如果 MQTT 服务需要身份验证，则在配置过程中 *必须* 提供适当的用户名和密码， 以授予 MinIO 访问该服务的权限。

#### MinIO `mc` 命令行工具 {#id8}

此过程中的某些操作需要使用 [`mc`](/docs/reference/minio-mc/#command-mc) 命令行工具。 安装说明请参见 `mc` [快速入门](/docs/reference/minio-mc/#mc-install)。

### 1) 列出部署中已配置的 MQTT 端点 {#id9}

使用 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 命令列出该部署中当前已配置的 MQTT 服务端点：

```shell
mc admin config get ALIAS/ notify_mqtt
```

将 `ALIAS` 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

命令输出类似如下：

```shell
notify_mqtt:primary  broker="tcp://mqtt-primary.example.net:port" password="" queue_dir="" queue_limit="0" reconnect_interval="0s"  keep_alive_interval="0s" qos="0" topic="" username=""
notify_mqtt:secondary  broker="tcp://mqtt-primary.example.net:port" password="" queue_dir="" queue_limit="0" reconnect_interval="0s"  keep_alive_interval="0s" qos="0" topic="" username=""
```

[`notify_mqtt`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt) 键是 [MQTT 通知设置](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-config-bucket-notification-mqtt) 的顶层配置键。 [`broker`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.broker) 键为给定的 *notify_mqtt* 键指定 MQTT server/broker 端点。`notify_mqtt:<IDENTIFIER>` 后缀描述该 MQTT 服务端点的唯一标识符。

记下要更新的 MQTT 服务端点标识符，供下一步使用。

### 2) 更新 MQTT 端点 {#id10}

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令为 MQTT 服务端点设置新配置：

```shell
mc admin config set ALIAS/ notify_mqtt:<IDENTIFIER> \
   url="MQTT://user:password@hostname:port" \
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

以下配置设置是 MQTT server/broker 端点的 *最少* 必需项：

- [`broker`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.broker)
- [`topic`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.topic)
- [`username`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.username) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*
- [`password`](/docs/reference/minio-server/settings/notifications/mqtt/#mc-conf.notify_mqtt.password) *如果 MQTT server/broker 强制要求身份验证/授权，则必需*

所有其他配置设置均为 *可选*。有关 MQTT 配置设置的完整列表，请参见 [MQTT 通知设置](/docs/reference/minio-server/settings/notifications/mqtt/#minio-server-config-bucket-notification-mqtt)。

### 3) 重启 MinIO 部署 {#id11}

你必须重启 MinIO 部署以应用配置更改。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程在启动时会为每个已配置的 MQTT 目标打印一行类似如下的内容：

```shell
SQS ARNs: arn:minio:sqs::primary:mqtt
```

### 3) 验证更改 {#id12}

对某个使用已更新 MQTT 服务端点进行事件配置的存储桶执行某个操作， 并检查 MQTT 服务中的通知数据。所需操作取决于配置存储桶通知时指定了哪些 [`事件`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.-event)。

例如，如果存储桶通知配置包含 `s3:ObjectCreated:Put` 事件， 则可以使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 命令在存储桶中创建新对象并触发通知。

```shell
mc cp ~/data/new-object.txt ALIAS/BUCKET
```