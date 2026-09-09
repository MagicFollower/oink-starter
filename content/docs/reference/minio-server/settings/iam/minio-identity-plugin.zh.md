---
title: "Silo 身份管理插件设置"

weight: 30
---

<a id="minio"></a>
<a id="minio-server-envvar-external-identity-management-plugin"></a>

本页介绍如何通过 MinIO Identity Management Plugin 启用外部身份管理的相关设置。 有关如何使用这些设置的教程，请参阅 [MinIO External Identity Management Plugin](/docs/administration/identity-access-management/pluggable-authentication/#minio-external-identity-management-plugin)。

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

配置 MinIO Identity Management Plugin 时，至少必须定义所有 *必需* 设置。 以下示例展示了最小必需配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
MINIO_IDENTITY_PLUGIN_URL="https://authservice.example.net:8080/auth"
MINIO_IDENTITY_PLUGIN_ROLE_POLICY="ConsoleUser"
```
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
#### `identity_plugin` {#mc-conf.identity_plugin}

*mc-conf*

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 创建或更新身份管理插件配置。 `identity_plugin url` 参数为必填项。 其他可选参数以空白字符（” “）分隔的列表形式指定。

```shell
mc admin config set identity_plugin                  \
   url="https://external-auth.example.net:8080/auth" \
   role_policy="consoleAdmin"                        \
   [ARGUMENT=VALUE] ...
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id3}

### URL {#url}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_PLUGIN_URL` {#envvar.MINIO_IDENTITY_PLUGIN_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin url` {#mc-conf.identity_plugin.url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

外部身份管理服务的 webhook endpoint （`https://authservice.example.net:8080/auth`）。

### 角色策略 {#id4}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_PLUGIN_ROLE_POLICY` {#envvar.MINIO_IDENTITY_PLUGIN_ROLE_POLICY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin role_policy` {#mc-conf.identity_plugin.role_policy}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要分配给已认证用户的 MinIO [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 列表，多个策略之间 使用逗号分隔。

### 启用 {#id5}

*可选*

{{< tabs group="tab1-tab2" default="tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
此设置不提供环境变量选项。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin enabled` {#mc-conf.identity_plugin.enabled}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

设置为 `false` 以禁用身份提供方配置。

如果设置为 `false`，应用程序将无法生成 STS 凭证，也无法通过已配置的提供方对 MinIO 进行身份验证。

默认为 `true` 或 “enabled”。

### 令牌 {#id6}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_PLUGIN_TOKEN` {#envvar.MINIO_IDENTITY_PLUGIN_TOKEN}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin token` {#mc-conf.identity_plugin.token}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

提供给已配置 webhook endpoint 的认证令牌。

请以字符串形式指定受支持的 HTTP [Authentication scheme](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#authentication_schemes)， 例如 `"Bearer TOKEN"`。 MinIO 会通过 HTTP [Authorization](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization) 头发送该令牌。

### 角色 ID {#id}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_PLUGIN_ROLE_ID` {#envvar.MINIO_IDENTITY_PLUGIN_ROLE_ID}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin role_id` {#mc-conf.identity_plugin.role_id}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 用于为该 identity manager 生成 ARN 的唯一 ID。 在生成 ARN 时，MinIO 会自动在指定 ID 前添加 `idmp-` 前缀。

如果省略此项，MinIO 会自动生成该 ID，并将完整 ARN 输出到 server 日志中。

### 注释 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_PLUGIN_COMMENT` {#envvar.MINIO_IDENTITY_PLUGIN_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_plugin comment` {#mc-conf.identity_plugin.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要附加到身份配置上的注释。