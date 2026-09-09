---
title: "Silo 访问管理插件设置"

weight: 40
---

<a id="minio"></a>
<a id="minio-server-envvar-external-access-management-plugin"></a>

本页说明如何配置 MinIO Access Management Plugin 以启用外部授权管理。 有关这些设置的使用教程，请参见 [MinIO 外部访问管理插件](/docs/administration/identity-access-management/pluggable-authorization/#minio-external-access-management-plugin)。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 示例 {#id2}

在设置 MinIO Access Management 插件时，至少必须定义所有 *Required* 设置。 此处示例展示了最小必需配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
MINIO_POLICY_PLUGIN_URL="https://authzservice.example.net:8080/authz"
```
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `policy_plugin` {#mc-conf.policy_plugin}

*mc-conf*

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 命令创建或更新访问管理插件配置。 `policy_plugin url` 参数为必填。 其他可选参数请以空白字符（” “）分隔的列表形式指定。

```shell
mc admin config set policy_plugin                     \
   url="https://authzservice.example.net:8080/authz"  \
   [ARGUMENT=VALUE] ...
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id3}

### URL {#url}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_POLICY_PLUGIN_URL` {#envvar.MINIO_POLICY_PLUGIN_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `policy_plugin url` {#mc-conf.policy_plugin.url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

外部访问管理服务的 webhook endpoint （`https://authzservice.example.net:8080/authz`）。

### 认证令牌 {#id4}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_POLICY_PLUGIN_AUTH_TOKEN` {#envvar.MINIO_POLICY_PLUGIN_AUTH_TOKEN}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `policy_plugin auth_token` {#mc-conf.policy_plugin.auth_token}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

提供给已配置 webhook endpoint 的认证令牌。

请以字符串形式指定受支持的 HTTP [Authentication scheme](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#authentication_schemes)， 例如 `"Bearer TOKEN"`。 MinIO 会通过 HTTP [Authorization](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) 头发送该令牌。

### HTTP2 {#http2}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_POLICY_PLUGIN_ENABLE_HTTP2` {#envvar.MINIO_POLICY_PLUGIN_ENABLE_HTTP2}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `policy_plugin enable_http2` {#mc-conf.policy_plugin.enable_http2}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

为连接已配置的 webhook 服务启用实验性的 HTTP2 支持。

默认值为 `off`

### 注释 {#id5}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_POLICY_PLUGIN_COMMENT` {#envvar.MINIO_POLICY_PLUGIN_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `policy_plugin comment` {#mc-conf.policy_plugin.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要附加到外部访问管理配置上的注释。