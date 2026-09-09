---
title: "Webhook 服务通知设置"

weight: 100
---

<a id="webhook"></a>
<a id="minio-server-config-bucket-notification-webhook"></a>
<a id="minio-server-envvar-bucket-notification-webhook"></a>
<a id="minio-server-envvar-bucket-notification-webhook-service"></a>

本页记录了将 Webhook 服务配置为 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 目标所需的设置。 有关如何使用这些设置的教程，请参见 [将事件发布到 Webhook](/docs/administration/monitoring/publish-events-to-webhook/#minio-bucket-notifications-publish-webhook)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 多个 Webhook 服务目标 {#id2}

可通过在顶层键后为每组相关 Webhook 设置追加唯一标识符 `_ID` 来指定多个 Webhook 服务端点。 例如，以下命令分别将两个不同的 Webhook 服务端点设置为 `PRIMARY` 和 `SECONDARY`：

```shell {tab="环境变量" group="tab1-tab2" value="tab1"}
export MINIO_NOTIFY_WEBHOOK_ENABLE_PRIMARY="on"
export MINIO_NOTIFY_WEBHOOK_ENDPOINT_PRIMARY="https://webhook1.example.net"

export MINIO_NOTIFY_WEBHOOK_ENABLE_SECONDARY="on"
export MINIO_NOTIFY_WEBHOOK_ENDPOINT_SECONDARY="https://webhook1.example.net"
```

```shell {tab="配置设置" value="tab2"}
mc admin config set notify_webhook:primary \
   endpoint="https://webhook1.example.net"
   [ARGUMENT=VALUE ...]

mc admin config set notify_webhook:secondary \
   endpoint="https://webhook2.example.net
   [ARGUMENT=VALUE ...]
```

## 设置 {#id3}

### 启用 {#id4}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_ENABLE` {#envvar.MINIO_NOTIFY_WEBHOOK_ENABLE}

*envvar*

指定 `on` 以启用将存储桶通知发布到 Webhook 服务端点。

默认为 `off`。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook` {#mc-conf.notify_webhook}

*mc-conf*

用于定义 Webhook 服务端点的顶层配置键，可用于 [MinIO 存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 Webhook 服务端点。 [`endpoint`](#mc-conf.notify_webhook.endpoint) 参数对每个目标均为 *必需*。 将其他可选参数指定为以空白字符（`" "`）分隔的列表。

```shell
mc admin config set notify_webhook \
  endpoint="https://webhook.example.net"
  [ARGUMENT="VALUE"] ... \
```
{{< /tab >}}
{{< /tabs >}}

### 端点 {#id5}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_ENDPOINT` {#envvar.MINIO_NOTIFY_WEBHOOK_ENDPOINT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook endpoint` {#mc-conf.notify_webhook.endpoint}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Webhook 服务的 URL。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 在添加目标之前，如果指定的 URL 可解析且可达， MinIO 会先检查其健康状态。 如果现有目标处于离线状态，MinIO 也不再阻止添加新的通知目标。

### 认证令牌 {#id6}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN` {#envvar.MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN}

*envvar*

适用于该端点类型的认证令牌。 对于不需要认证的端点可省略。

为支持多种令牌类型，MinIO 会使用 *完全按所给内容* 的值来构造请求认证头。 根据端点要求，你可能需要包含额外信息。

例如，对于 Bearer 令牌，请在前面加上 `Bearer`：

```shell
export MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN_myendpoint="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。 自定义认证格式可能类似如下：

```shell
export MINIO_NOTIFY_WEBHOOK_AUTH_TOKEN_xyz="ServiceXYZ 1a2b3c4f5e"
```

更多详情请查阅目标服务的文档。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook auth_token` {#mc-conf.notify_webhook.auth_token}

*mc-conf*

适用于该端点类型的认证令牌。 对于不需要认证的端点可省略。

为支持多种令牌类型，MinIO 会使用 *完全按所给内容* 的值来构造请求认证头。 根据端点要求，你可能需要包含额外信息。

例如，对于 Bearer 令牌，请在前面加上 `Bearer`：

```shell
   mc admin config set myminio notify_webhook   \
   endpoint="https://webhook-1.example.net"  \
      auth_token="Bearer 1a2b3c4f5e"
```

请根据端点要求调整该值。 自定义认证格式可能类似如下：

```shell
   mc admin config set myminio notify_webhook   \
      endpoint="https://webhook-1.example.net"  \
      auth_token="ServiceXYZ 1a2b3c4f5e"
```

更多详情请查阅目标服务的文档。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**

当该值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 的返回内容的一部分时，MinIO 会将其打码。
{{< /tab >}}
{{< /tabs >}}

### 队列目录 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_QUEUE_DIR` {#envvar.MINIO_NOTIFY_WEBHOOK_QUEUE_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook queue_dir` {#mc-conf.notify_webhook.queue_dir}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定目录路径以启用 MinIO 针对未投递消息的持久化事件存储，例如 `/opt/minio/events`。

当 Webhook 服务离线时，MinIO 会将未投递事件存储到指定存储中，并在连接恢复后重放这些已存储事件。

### 队列上限 {#id8}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_QUEUE_LIMIT` {#envvar.MINIO_NOTIFY_WEBHOOK_QUEUE_LIMIT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook queue_limit` {#mc-conf.notify_webhook.queue_limit}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定未投递消息的最大上限。 默认为 `100000`。

### 客户端证书 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_CLIENT_CERT` {#envvar.MINIO_NOTIFY_WEBHOOK_CLIENT_CERT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook client_cert` {#mc-conf.notify_webhook.client_cert}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于向 Webhook 服务执行 mTLS 认证的客户端证书路径。

### 客户端密钥 {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_NOTIFY_WEBHOOK_CLIENT_KEY` {#envvar.MINIO_NOTIFY_WEBHOOK_CLIENT_KEY}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `notify_webhook client_key` {#mc-conf.notify_webhook.client_key}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于向 Webhook 服务执行 mTLS 认证的客户端私钥路径。