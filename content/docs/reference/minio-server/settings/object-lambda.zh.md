---
title: "Object Lambda 函数设置"

weight: 110
---

<a id="object-lambda"></a>
<a id="minio-server-envvar-object-lambda-webhook"></a>

本页面介绍了可用于配置 MinIO 的设置，以便将数据发布到 HTTP webhook 端点并触发 Object Lambda 函数。 有关使用这些设置的更完整文档和教程，请参见 [使用 Object Lambda 进行转换](/docs/developers/transforms-with-object-lambda/#developers-object-lambda)。

你可以通过定义以下项来建立或修改设置：

- 在启动或重启 MinIO Server 之前，在主机系统上设置 *环境变量*。 有关如何定义环境变量，请参阅操作系统文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

某些设置仅提供环境变量或配置项中的一种，而非两者都提供。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 启用 {#id2}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_LAMBDA_WEBHOOK_ENABLE` {#envvar.MINIO_LAMBDA_WEBHOOK_ENABLE}

*envvar*

指定 `"on"` 以启用处理函数的 Object Lambda webhook 端点。

需要同时指定 [`MINIO_LAMBDA_WEBHOOK_ENDPOINT`](#envvar.MINIO_LAMBDA_WEBHOOK_ENDPOINT)。

你可以通过为每个 Object Lambda 函数追加唯一标识符，将多个 webhook 指定为 Lambda 目标。 例如，以下命令启用两个不同的 Object Lambda webhook 端点：

```shell
export MINIO_LAMBDA_WEBHOOK_ENABLE_myfunction="on"
export MINIO_LAMBDA_WEBHOOK_ENABLE_yourfunction="on"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `lambda_webhook enable` {#mc-conf.lambda_webhook.enable}

*mc-conf*

*可选*

指定 `"on"` 以启用处理函数的 Object Lambda webhook 端点。 需要同时指定 [`endpoint`](#mc-conf.lambda_webhook.endpoint)。

示例：

```shell
mc admin config set myminio lambda_webhook:myfunction endpoint="https://example.com/" enable=on
```
{{< /tab >}}
{{< /tabs >}}

## 端点 {#id3}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_LAMBDA_WEBHOOK_ENDPOINT` {#envvar.MINIO_LAMBDA_WEBHOOK_ENDPOINT}

*envvar*

处理函数的 lambda webhook HTTP 端点。

你可以通过为每个 Object Lambda 函数追加唯一标识符，将多个 webhook 端点指定为 Lambda 目标。 例如，以下命令设置两个不同的 Object Lambda webhook 端点：

```shell
export MINIO_LAMBDA_WEBHOOK_ENDPOINT_myfunction="http://webhook-1.example.com"
export MINIO_LAMBDA_WEBHOOK_ENDPOINT_yourfunction="http://webhook-2.example.com"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `lambda_webhook endpoint` {#mc-conf.lambda_webhook.endpoint}

*mc-conf*

*可选*

处理函数的 lambda webhook HTTP 端点。
{{< /tab >}}
{{< /tabs >}}

## 认证令牌 {#id4}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_LAMBDA_WEBHOOK_AUTH_TOKEN` {#envvar.MINIO_LAMBDA_WEBHOOK_AUTH_TOKEN}

*envvar*

指定用于向 lambda webhook 服务进行身份验证的不透明字符串或 JWT 授权令牌。

你可以通过为每个 Object Lambda 函数追加唯一标识符，为多个 Lambda 目标指定令牌。 例如，以下命令为两个不同的 Object Lambda webhook 端点配置令牌：

```shell
export MINIO_LAMBDA_WEBHOOK_AUTH_TOKEN_myfunction="1a2b3c4d5e"
export MINIO_LAMBDA_WEBHOOK_AUTH_TOKEN_yourfunction="1a2b3c4d5e"
```

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当该值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时，MinIO 会对其进行脱敏。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `lambda_webhook auth_token` {#mc-conf.lambda_webhook.auth_token}

*mc-conf*

*可选*

指定用于向 lambda webhook 服务进行身份验证的不透明字符串或 JWT 授权令牌。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当该值作为 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回结果的一部分时，MinIO 会对其进行脱敏。
{{< /tab >}}
{{< /tabs >}}

## 客户端证书 {#id5}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_LAMBDA_WEBHOOK_CLIENT_CERT` {#envvar.MINIO_LAMBDA_WEBHOOK_CLIENT_CERT}

*envvar*

指定用于向 lambda webhook 服务执行 mTLS 身份验证的客户端证书路径。

你可以通过为每个 Object Lambda 函数追加唯一标识符，为多个 Lambda 目标指定客户端证书。 例如，以下命令为两个不同的 Object Lambda webhook 端点配置证书：

```shell
export MINIO_LAMBDA_WEBHOOK_CLIENT_CERT_myfunction="/path/to/cert1"
export MINIO_LAMBDA_WEBHOOK_CLIENT_CERT_yourfunction="/path/to/cert2"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `lambda_webhook client_cert` {#mc-conf.lambda_webhook.client_cert}

*mc-conf*

*可选*

指定用于向 lambda webhook 服务执行 mTLS 身份验证的客户端证书路径。
{{< /tab >}}
{{< /tabs >}}

## 客户端密钥 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_LAMBDA_WEBHOOK_CLIENT_KEY` {#envvar.MINIO_LAMBDA_WEBHOOK_CLIENT_KEY}

*envvar*

指定用于向 lambda webhook 服务执行 mTLS 身份验证的私钥路径。

你可以通过为每个 Object Lambda 函数追加唯一标识符，为多个 Lambda 目标指定客户端私钥。 例如，以下命令为两个不同的 Object Lambda webhook 端点配置密钥：

```shell
export MINIO_LAMBDA_WEBHOOK_CLIENT_KEY_myfunction="/path/to/key1"
export MINIO_LAMBDA_WEBHOOK_CLIENT_KEY_yourfunction="/path/to/key2"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `lambda_webhook client_key` {#mc-conf.lambda_webhook.client_key}

*mc-conf*

*可选*

指定用于向 lambda webhook 服务执行 mTLS 身份验证的私钥路径。
{{< /tab >}}
{{< /tabs >}}