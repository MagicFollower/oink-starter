---
title: "MQTT 通知设置"

weight: 40
---

<a id="mqtt"></a>
<a id="minio-server-config-bucket-notification-mqtt"></a>
<a id="minio-server-envvar-bucket-notification-mqtt"></a>

本页面记录了将 MQTT 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标的相关设置。 有关如何使用这些设置的教程，请参阅 [将事件发布到 MQTT](/docs/administration/monitoring/publish-events-to-mqtt/#minio-bucket-notifications-publish-mqtt)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 MQTT 目标 {#id2}

你可以在顶层键后为每组相关 MQTT 设置追加一个唯一标识符 `_ID`，以指定多个 MQTT 服务端点。 例如，以下命令分别将两个不同的 MQTT 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_NOTIFY_MQTT_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_MQTT_BROKER_PRIMARY="tcp://user:password@mqtt-endpoint.example.net:1883"

export MINIO_NOTIFY_MQTT_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_MQTT_BROKER_SECONDARY="tcp://user:password@mqtt-endpoint.example.net:1883"
```

```shell {tab="配置项" value="tab2"}
mc admin config set notify_mqtt:primary \
   broker="tcp://endpoint:port" \
   topic="minio/bucket-name/events/" \
   username="username" \
   password="password" \
   [ARGUMENT="VALUE"] ... \

mc admin config set notify_mqtt:secondary \
   broker="tcp://endpoint:port" \
   topic="minio/bucket-name/events/" \
   username="username" \
   password="password" \
   [ARGUMENT="VALUE"] ... \
```

在这些设置中，[`MINIO_NOTIFY_MQTT_ENABLE_PRIMARY`](#envvar.MINIO_NOTIFY_MQTT_ENABLE) 表示该环境变量与 ID 为 `PRIMARY` 的 MQTT 服务端点关联。

## 设置 {#id3}

### 启用 {#id4}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_ENABLE` {#envvar.MINIO_NOTIFY_MQTT_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 MQTT 端点。

默认为 `off`。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt` {#mc-conf.notify_mqtt}

*mc-conf*

用于定义 MQTT server/broker 端点的顶层配置键，可用于 [MinIO 存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 MQTT server/broker 端点。 每个端点都 *必须* 包含以下参数：

- [`broker`](#mc-conf.notify_mqtt.broker)
- [`topic`](#mc-conf.notify_mqtt.topic)
- [`username`](#mc-conf.notify_mqtt.username) *如果 MQTT server/broker 不强制认证/授权，则为可选*
- [`password`](#mc-conf.notify_mqtt.password) *如果 MQTT server/broker 不强制认证/授权，则为可选*

其他可选参数请以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set notify_mqtt \
   broker="tcp://endpoint:port" \
   topic="minio/bucket-name/events/" \
   username="username" \
   password="password" \
   [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### Broker {#broker}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_BROKER` {#envvar.MINIO_NOTIFY_MQTT_BROKER}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt broker` {#mc-conf.notify_mqtt.broker}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MQTT server/broker 端点。 MinIO 支持通过 TCP、TLS 或 Websocket 连接到 server/broker URL。 例如：

- `tcp://mqtt.example.net:1883`
- `tls://mqtt.example.net:1883`
- `ws://mqtt.example.net:1883`

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### Topic {#topic}

*必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_TOPIC` {#envvar.MINIO_NOTIFY_MQTT_TOPIC}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt topic` {#mc-conf.notify_mqtt.topic}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MQTT topic 名称，用于关联 MinIO 发布到 MQTT 端点的事件。

### Username {#username}

*如果 MQTT server/broker 强制认证/授权，则必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_USERNAME` {#envvar.MINIO_NOTIFY_MQTT_USERNAME}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt username` {#mc-conf.notify_mqtt.username}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 用于向 MQTT server/broker 进行身份认证的 MQTT 用户名。

### Password {#password}

*如果 MQTT server/broker 强制认证/授权，则必填*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_PASSWORD` {#envvar.MINIO_NOTIFY_MQTT_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt password` {#mc-conf.notify_mqtt.password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 用于向 MQTT server/broker 进行身份认证的 MQTT 用户名对应的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时，MinIO 会对该值进行脱敏处理。

### 服务质量（QoS） {#qos}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_QOS` {#envvar.MINIO_NOTIFY_MQTT_QOS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt qos` {#mc-conf.notify_mqtt.qos}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定已发布事件的 Quality of Service 优先级。

默认为 `0`。

### Keep Alive 间隔 {#keep-alive}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_KEEP_ALIVE_INTERVAL` {#envvar.MINIO_NOTIFY_MQTT_KEEP_ALIVE_INTERVAL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt keep_alive_interval` {#mc-conf.notify_mqtt.keep_alive_interval}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MQTT 连接的 keep-alive 间隔。MinIO 支持以下时间单位：

- `s` - 秒，例如 “60s”
- `m` - 分钟，例如 “60m”
- `h` - 小时，例如 “24h”
- `d` - 天，例如 “7d”

### 重连间隔 {#id5}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_RECONNECT_INTERVAL` {#envvar.MINIO_NOTIFY_MQTT_RECONNECT_INTERVAL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt reconnect_interval` {#mc-conf.notify_mqtt.reconnect_interval}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MQTT 连接的重连间隔。MinIO 支持以下时间单位：

- `s` - 秒，例如 “60s”
- `m` - 分钟，例如 “60m”
- `h` - 小时，例如 “24h”
- `d` - 天，例如 “7d”

### 队列目录 {#id6}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_QUEUE_DIR` {#envvar.MINIO_NOTIFY_MQTT_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt queue_dir` {#mc-conf.notify_mqtt.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 的持久化事件存储，用于保存未投递消息，例如 `/opt/minio/events`。

当 MQTT server/broker 离线时，MinIO 会将未投递事件存储在指定位置；连接恢复后会重放这些已存储事件。

### 队列上限 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_MQTT_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt queue_limit` {#mc-conf.notify_mqtt.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认为 `100000`。

### 注释 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_MQTT_COMMENT` {#envvar.MINIO_NOTIFY_MQTT_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `notify_mqtt comment` {#mc-conf.notify_mqtt.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 MQTT 配置关联的注释。