---
title: "Silo 客户端设置"

weight: 10
---

<a id="minio"></a>
<a id="minio-server-envvar-mc"></a>

本页面介绍 [MinIO Client](/docs/reference/minio-mc/#minio-client) 的设置。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

## 设置 {#id2}

### 主机凭证 {#id3}

使用此设置可为 *mc* 命令添加一个临时别名。 例如，可用于脚本场景。

该临时别名使用 [AWS s3v4 signature](https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html)。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
<a id="envvar.MC_HOST_&lt;ALIAS&gt;"></a>

##### `MC_HOST_<ALIAS>` {#envvar.MC_HOST_-ALIAS}

*envvar*

将环境变量末尾的 `<ALIAS>` 替换为要设置主机的 `alias`。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。

使用 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 配置 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

#### 示例 {#id4}

**静态凭证**

```shell {tab="语法" group="tab1-tab2" value="tab1"}
export MC_HOST_<alias>=https://<Access Key>:<Secret Key>@<YOUR-S3-ENDPOINT>
```

```shell {tab="示例" value="tab2"}
export MC_HOST_myalias=https://Q3AM3UQ867SPQQA43P2F:zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG@play.min.io
```

**Security Token Service (STS) 凭证**

```shell {tab="语法" group="tab1-tab2" value="tab1"}
export MC_HOST_<alias>=https://<Access Key>:<Secret Key>:<Session Token>@<YOUR-S3-ENDPOINT>
```

```shell {tab="示例" value="tab2"}
export MC_HOST_myalias=https://Q3AM3UQ867SPQQA43P2F:zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG:eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NLZXkiOiJOVUlCT1JaWVRWMkhHMkJNUlNYUiIsImF1ZCI6IlBvRWdYUDZ1Vk80NUlzRU5SbmdEWGo1QXU1WWEiLCJhenAiOiJQb0VnWFA2dVZPNDVJc0VOUm5nRFhqNUF1NVlhIiwiZXhwIjoxNTM0ODk2NjI5LCJpYXQiOjE1MzQ4OTMwMjksImlzcyI6Imh0dHBzOi8vbG9jYWxob3N0Ojk0NDMvb2F1dGgyL3Rva2VuIiwianRpIjoiNjY2OTZjZTctN2U1Ny00ZjU5LWI0MWQtM2E1YTMzZGZiNjA4In0.eJONnVaSVHypiXKEARSMnSKgr-2mlC2Sr4fEGJitLcJF_at3LeNdTHv0_oHsv6ZZA3zueVGgFlVXMlREgr9LXA@play.min.io
```

### STS 服务 {#sts}

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-11-06T04-19-23Z

使用此设置可添加一个用于 *mc* 命令的 STS endpoint。

> [!NOTE]
> **变更: mc**
>
> RELEASE.2023-12-02T02-03-28Z

支持按 alias 添加多个环境变量。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
<a id="envvar.MC_STS_ENDPOINT_&lt;alias&gt;"></a>

##### `MC_STS_ENDPOINT_<alias>` {#envvar.MC_STS_ENDPOINT_-alias}

*envvar*

```shell
export MC_STS_ENDPOINT_myalias=https://sts.minio-operator.svc.cluster.local:4223/sts/ns-1
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### Web Token Identity {#web-token-identity}

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-11-06T04-19-23Z

使用此设置可添加一个用于 *mc* 命令的 Web Token Identity。

> [!NOTE]
> **变更: mc**
>
> RELEASE.2023-12-02T02-03-28Z

支持按 alias 添加多个环境变量。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
<a id="envvar.MC_WEB_IDENTITY_TOKEN_&lt;alias&gt;"></a>

##### `MC_WEB_IDENTITY_TOKEN_<alias>` {#envvar.MC_WEB_IDENTITY_TOKEN_-alias}

*envvar*

```shell
export MC_WEB_IDENTITY_TOKEN_FILE_myalias=/var/run/secrets/kubernetes.io/serviceaccount/token
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 配置目录 {#id5}

指定 MinIO Client 应使用的配置目录路径。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_CONFIG_DIR` {#envvar.MC_CONFIG_DIR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 进度条 {#id6}

禁用 MinIO Client 进度条。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_QUIET` {#envvar.MC_QUIET}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### Pager {#pager}

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-04-29T09-56-05Z

在 CLI 中禁用 MinIO Client 的分页器功能。 使用该设置后，输出将改为直接打印到原始 `STDOUT`。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_DISABLE_PAGER` {#envvar.MC_DISABLE_PAGER}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 颜色主题 {#id7}

禁用 MinIO Client 输出使用的颜色主题。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_NO_COLOR` {#envvar.MC_NO_COLOR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### JSON {#json}

启用将输出格式化为 JSON lines。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_JSON` {#envvar.MC_JSON}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 调试 {#id8}

启用调试输出。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_DEBUG` {#envvar.MC_DEBUG}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 禁用 SSL {#ssl}

禁用 SSL 证书校验。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_INSECURE` {#envvar.MC_INSECURE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### 限制下载带宽 {#id9}

限制 MinIO Client 在某些命令中使用的下载带宽。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_LIMIT_DOWNLOAD` {#envvar.MC_LIMIT_DOWNLOAD}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

若未指定，MinIO Client 使用全部可用带宽。

将客户端侧下载速率限制为不超过指定值（KiB/s、MiB/s 或 GiB/s）。该设置仅影响运行 MinIO Client 的本地设备发起的下载。支持的单位包括：

- B 表示 bytes
- K 表示 kilobytes
- M 表示 megabytes
- G 表示 gigabytes
- Ki 表示 kibibytes
- Mi 表示 mibibytes
- Gi 表示 gibibytes

例如，要将下载速率限制为不超过 1 GiB/s，可在 Linux 系统上使用以下命令：

```shell
export MC_LIMIT_DOWNLOAD=1G
```

在非 Linux 系统上，请参考你的操作系统文档使用等效命令。

### 限制上传带宽 {#id10}

限制 MinIO Client 在某些命令中使用的上传带宽。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_LIMIT_UPLOAD` {#envvar.MC_LIMIT_UPLOAD}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

若未指定，MinIO Client 使用全部可用带宽。

将客户端侧上传速率限制为不超过指定值（KiB/s、MiB/s 或 GiB/s）。该设置仅影响运行 MinIO Client 的本地设备发起的上传。支持的单位包括：

- B 表示 bytes
- K 表示 kilobytes
- M 表示 megabytes
- G 表示 gigabytes
- Ki 表示 kibibytes
- Mi 表示 mibibytes
- Gi 表示 gibibytes

例如，要将上传速率限制为不超过 1 GiB/s，可在 Linux 系统上使用以下命令：

```shell
export MC_LIMIT_UPLOAD=1G
```

在非 Linux 系统上，请参考你的操作系统文档使用等效命令。

### SSE-KMS 加密 {#sse-kms}

使用服务端管理密钥通过 [SSE-KMS](/docs/operations/server-side-encryption/#minio-sse-data-encryption) 对选项进行加密和解密。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_ENC_KMS` {#envvar.MC_ENC_KMS}

*envvar*

使用 [`MC_ENC_KMS`](#envvar.MC_ENC_KMS) 环境变量指定密钥。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

### SSE-S3 加密 {#sse-s3}

使用服务端管理密钥通过 [SSE-KMS](/docs/operations/server-side-encryption/#minio-sse-data-encryption) 对选项进行加密和解密。

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MC_ENC_S3` {#envvar.MC_ENC_S3}

*envvar*

指定执行 SSE-S3 加密时使用的密钥。 指定值必须与 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 中设置的加密密钥匹配。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}