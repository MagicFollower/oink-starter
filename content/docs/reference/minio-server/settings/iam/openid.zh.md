---
title: "OpenID 身份管理设置"

weight: 20
---

<a id="openid"></a>
<a id="minio-open-id-config-settings"></a>
<a id="minio-server-envvar-external-identity-management-openid"></a>

本页面记录了如何使用与 OpenID Connect (OIDC) 兼容的提供方来启用外部身份管理的相关设置。 有关如何使用这些设置的教程，请参见 [OpenID Connect 访问管理](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid)。

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

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
MINIO_IDENTITY_OPENID_CONFIG_URL="https://openid-provider.example.net/.well-known/openid-configuration"
```
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
#### `identity_openid` {#mc-conf.identity_openid}

*mc-conf*

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 设置或更新 OpenID 配置。 [`config_url`](#mc-conf.identity_openid.config_url) 参数为 *必需*。 其他可选参数请以空白字符（`" "`）分隔的列表形式指定。

```shell
mc admin config set identity_openid                                               \
  config_url="https://openid-provider.example.net/.well-known/openid-configuration" \
  [ARGUMENT="VALUE"] ...
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id3}

### 配置 URL {#url}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CONFIG_URL` {#envvar.MINIO_IDENTITY_OPENID_CONFIG_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid config_url` {#mc-conf.identity_openid.config_url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定与 <abbr title="OpenID Connect">OIDC</abbr> 兼容的 provider 的 [discovery document](https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig) URL。

<abbr title="OpenID Connect">OIDC</abbr> Discovery URL 通常类似于：

`https://openid-provider.example.net/.well-known/openid-configuration`

### 启用 {#id4}

*可选*

{{< tabs group="tab1-tab2" default="tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
此设置没有环境变量选项。 请改用配置项。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid enabled` {#mc-conf.identity_openid.enabled}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

设置为 `false` 可禁用 OpenID 配置。

如果设置为 `false`，应用程序将无法使用已配置的提供方生成 STS 凭证或通过其他方式向 MinIO 认证。

默认值为 `true`（即“启用”）。

### 客户端 ID {#id}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CLIENT_ID` {#envvar.MINIO_IDENTITY_OPENID_CLIENT_ID}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid client_id` {#mc-conf.identity_openid.client_id}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在使用与 <abbr title="OpenID Connect">OIDC</abbr> 兼容的 provider 验证用户凭证时 所使用的唯一公开标识符。

### 客户端密钥 {#id7}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CLIENT_SECRET` {#envvar.MINIO_IDENTITY_OPENID_CLIENT_SECRET}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid client_secret` {#mc-conf.identity_openid.client_secret}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在使用与 <abbr title="OpenID Connect">OIDC</abbr> 兼容的 provider 验证用户凭证时 所使用的 client secret。根据 provider 的不同，此字段可能是可选的。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当通过 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回此值时，MinIO 会将其脱敏。

### 角色策略 {#id8}

*可选*

此设置与 `Claim Name` 设置互斥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_ROLE_POLICY` {#envvar.MINIO_IDENTITY_OPENID_ROLE_POLICY}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid role_policy` {#mc-conf.identity_openid.role_policy}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定逗号分隔的 [策略名称](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 列表，用于该 provider 的所有认证请求 中的 `RoleArn`。指定的一个或多个策略必须已经存在于 MinIO Server 上。

要使用此 OIDC 配置，你必须在 STS 请求体中指定对应的 [RoleArn](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-assumerolewithwebidentity-query-parameters)。

### 声明名称 {#id9}

*可选*

此设置与 `Role Policy` 设置互斥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CLAIM_NAME` {#envvar.MINIO_IDENTITY_OPENID_CLAIM_NAME}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid claim_name` {#mc-conf.identity_openid.claim_name}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 [JWT Claim](https://datatracker.ietf.org/doc/html/rfc7519#section-4) 的名称，MinIO 使用该 Claim 来识别应附加到已认证用户上的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

该 Claim 可以包含一个或多个逗号分隔的策略名称，以附加给用户。该 Claim *至少* 必须包含一个策略，否则该用户在 MinIO server 上将没有任何权限。

默认值为 `policy`。

### 声明前缀 {#id10}

*可选*

此设置已弃用，并已在 [RELEASE.2024-07-13T01-46-15Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-07-13T01-46-15Z) 起移除。 请改用 [`MINIO_IDENTITY_OPENID_CLAIM_NAME`](#envvar.MINIO_IDENTITY_OPENID_CLAIM_NAME)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CLAIM_PREFIX` {#envvar.MINIO_IDENTITY_OPENID_CLAIM_PREFIX}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid claim_prefix` {#mc-conf.identity_openid.claim_prefix}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定应用到所给 Claim 名称上的 [JWT Claim](https://datatracker.ietf.org/doc/html/rfc7519#section-4) 命名空间前缀。

### 显示名称 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_DISPLAY_NAME` {#envvar.MINIO_IDENTITY_OPENID_DISPLAY_NAME}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid display_name` {#mc-conf.identity_openid.display_name}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO Console 在登录页面上显示给用户的名称。

### 作用域 {#id12}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_SCOPES` {#envvar.MINIO_IDENTITY_OPENID_SCOPES}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid scopes` {#mc-conf.identity_openid.scopes}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定逗号分隔的 [scopes](https://datatracker.ietf.org/doc/html/rfc6749#section-3.3) 列表。 默认使用 discovery document 中公布的 scopes。

### 重定向 URI {#uri}

*可选*

此设置已弃用，并已在 [RELEASE.2024-07-13T01-46-15Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-07-13T01-46-15Z) 起移除。 请改用 [`MINIO_BROWSER_REDIRECT_URL`](/docs/reference/minio-server/settings/console/#envvar.MINIO_BROWSER_REDIRECT_URL)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_REDIRECT_URI` {#envvar.MINIO_IDENTITY_OPENID_REDIRECT_URI}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid redirect_uri` {#mc-conf.identity_openid.redirect_uri}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

> [!WARNING]
> **重要**
>
> 该参数已在 [RELEASE.2023-02-27T18-10-45Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-02-27T18-10-45Z) 中移除。 请改用 [`MINIO_BROWSER_REDIRECT_URL`](/docs/reference/minio-server/settings/console/#envvar.MINIO_BROWSER_REDIRECT_URL) [环境变量](/docs/reference/minio-server/settings/#minio-server-environment-variables)。

MinIO Console 默认使用发起认证请求的节点主机名。 对于位于负载均衡器或反向代理之后的 MinIO 部署，请指定该字段，以确保 OIDC provider 将认证响应返回到正确的 MinIO Console URL。 其中应包含 Console 主机名、端口以及 `/oauth_callback`：

```shell
http://minio.example.net:consoleport/oauth_callback
```

请确保在启动 MinIO Server 时使用 [`--console-address`](/docs/reference/minio-server/#minio.server.-console-address) 选项，以设置固定的 Console 监听端口。 如果省略该选项，默认行为是在启动时随机选择端口号。

指定的 URI *必须* 与 provider 上批准的某个 redirect / callback URI 匹配。 更多信息请参见 OpenID [Authentication Request](https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest)。

### 动态 URI 重定向 {#id13}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_REDIRECT_URI_DYNAMIC` {#envvar.MINIO_IDENTITY_OPENID_REDIRECT_URI_DYNAMIC}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid redirect_uri_dynamic` {#mc-conf.identity_openid.redirect_uri_dynamic}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

MinIO Console 默认会将发起认证请求的节点主机名作为重定向 URI 的一部分， 并将其提供给 OIDC provider。 对于位于使用轮询协议的负载均衡器之后的 MinIO 部署，这可能导致负载均衡器将响应 返回给与原始客户端不同的 MinIO 节点。

将此选项指定为 `on`，可让 MinIO Console 使用原始请求中的 `Host` 头来构造 传递给 OIDC provider 的重定向 URI。 默认值为 `off`。

### 用户信息 {#id14}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_CLAIM_USERINFO` {#envvar.MINIO_IDENTITY_OPENID_CLAIM_USERINFO}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid claim_userinfo` {#mc-conf.identity_openid.claim_userinfo}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

允许 MinIO 从已认证用户的 [UserInfo Endpoint](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo) 获取 claims。

有效值为 `on` 或 `off`。

### 提供方 {#id15}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_VENDOR` {#envvar.MINIO_IDENTITY_OPENID_VENDOR}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid vendor` {#mc-conf.identity_openid.vendor}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 OIDC Vendor，以启用该 vendor 的特定受支持行为。

支持以下值：

- `keycloak`

### Keycloak Realm {#keycloak-realm}

*可选*

此设置要求将 `OpenID Vendor` 设置定义为 `keycloak`。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_KEYCLOAK_REALM` {#envvar.MINIO_IDENTITY_OPENID_KEYCLOAK_REALM}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid keycloak_realm` {#mc-conf.identity_openid.keycloak_realm}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于 Keycloak Admin API 操作的 Keycloak Realm，例如 `main`。

### Keycloak 管理 URL {#keycloak-url}

*可选*

此设置要求将 `OpenID Vendor` 设置定义为 `keycloak`。

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_KEYCLOAK_ADMIN_URL` {#envvar.MINIO_IDENTITY_OPENID_KEYCLOAK_ADMIN_URL}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid keycloak_admin_url` {#mc-conf.identity_openid.keycloak_admin_url}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Keycloak Admin API URL。 如果配置为定期校验已认证的 Keycloak 用户是否处于激活 / 存在状态，MinIO 可以 使用该 URL。 例如，`https://keycloak-endpoint:port/admin/`。

### 注释 {#id16}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_OPENID_COMMENT` {#envvar.MINIO_IDENTITY_OPENID_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `identity_openid comment` {#mc-conf.identity_openid.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要附加到与 <abbr title="OpenID Connect">OIDC</abbr> 兼容 provider 配置上的注释。