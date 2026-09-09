---
title: "配置 Silo 使用 Keycloak 进行认证"

weight: 20
---

<a id="minio-keycloak"></a>
<a id="minio-authenticate-using-keycloak"></a>

## 概览 {#id2}

本流程将 MinIO 配置为通过 OpenID Connect (OIDC) 协议，使用 [Keycloak](https://www.keycloak.org/) 作为外部 Identity Provider (IDP) 来认证用户。

本页提供了在 Kubernetes 和裸金属 基础设施上的 MinIO 部署中配置 OIDC 的流程。

请选择与你基础设施对应的标签页，在不同说明集之间切换。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
对于使用 [MinIO Kubernetes Operator](/docs/operations/deployments/kubernetes/#minio-kubernetes) 部署的 MinIO Tenant，本流程包括：

- 配置 Keycloak 以配合 MinIO 认证与授权
- 配置新的或现有的 MinIO Tenant，使其使用 Keycloak 作为 OIDC 提供方
- 创建用于控制 Keycloak 认证用户访问权限的策略
- 使用 SSO 和 Keycloak 托管身份登录 MinIO Tenant Console
- 使用 `AssumeRoleWithWebIdentity` Security Token Service (STS) API 生成临时 S3 访问凭证
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
对于部署在裸金属基础设施上的 MinIO，本流程包括：

- 配置 Keycloak 以配合 MinIO 认证与授权
- 配置新的或现有的 MinIO 集群，使其使用 Keycloak 作为 OIDC 提供方
- 创建用于控制 Keycloak 认证用户访问权限的策略
- 使用 SSO 和 Keycloak 托管身份登录 MinIO Console
- 使用 `AssumeRoleWithWebIdentity` Security Token Service (STS) API 生成临时 S3 访问凭证
{{< /tab >}}
{{< /tabs >}}

本流程基于 Keycloak `21.0.0` 编写并完成测试。 这些说明也可能适用于其他 Keycloak 版本。 本流程假定你已经具备 Keycloak 的使用经验，并已阅读 [其文档](https://www.keycloak.org/documentation)，以获取部署、配置和管理该服务的指导和最佳实践。

## 前提条件 {#id3}

### Keycloak 部署与 Realm 配置 {#keycloak-realm}

本流程假定你已经拥有一个现成的 Keycloak 部署，并且具备其管理访问权限。 具体来说，你必须拥有在该 Keycloak 部署上创建和配置 Realms、Clients、Client Scopes、Realm Roles、Users 和 Groups 的权限。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
对于与 MinIO Tenant 位于同一 Kubernetes 集群内的 Keycloak 部署，本流程假定 Keycloak 与 MinIO 的 pods/services 之间具备双向访问能力。 对于位于 Kubernetes 集群外部的 Keycloak 部署，本流程假定已经存在用于管理 MinIO Tenant 入站和出站访问的 Ingress、Load Balancer 或类似 Kubernetes 网络控制组件。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
MinIO 部署必须与目标 OIDC 服务保持双向访问。
{{< /tab >}}
{{< /tabs >}}

请确保每个打算与 MinIO 配合使用的用户身份，都配置了合适的 [claim](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control)，以便 MinIO 能将认证用户关联到某个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。 未分配任何策略的 OpenID 用户，无权访问 MinIO 集群中的任何操作或资源。

### 访问 MinIO 集群 {#minio}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
你必须能够访问 MinIO Operator Console Web UI。 你可以使用自己偏好的 Kubernetes 路由组件暴露 MinIO Operator Console Service，也可以通过临时端口转发，在本地机器上暴露 Console Service 端口。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
本流程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 对 MinIO 集群执行操作。 请在一台能够访问该集群网络的机器上安装 `mc`。 关于如何下载和安装 `mc`，请参见 `mc` [安装快速开始](/docs/reference/minio-mc/#mc-install)。

本流程假定已为 MinIO 集群配置 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
{{< /tab >}}
{{< /tabs >}}

<a id="id4"></a>

## 为 MinIO 配置 Keycloak 身份管理 {#minio-external-identity-management-keycloak-configure}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
1. 配置或创建用于访问 Keycloak 的 Client

   认证到 Keycloak **Administrative Console**，然后进入 **Clients**。

   选择 **Create client**，按照提示为 MinIO 创建一个新的 Keycloak client。 按如下方式填写指定输入项：

   <table>
     <tbody>
       <tr>
         <td><p>Client ID</p></td>
         <td><p>设置为 MinIO 的唯一标识符（<code>minio</code>）</p></td>
       </tr>
       <tr>
         <td><p>Client type</p></td>
         <td><p>设置为 <code>OpenID Connect</code></p></td>
       </tr>
       <tr>
         <td><p>Always display in console</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Client authentication</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Authentication flow</p></td>
         <td><p>打开 <code>Standard flow</code></p></td>
       </tr>
       <tr>
         <td><p>（可选）<em>Authentication flow</em></p></td>
         <td><p>打开 <code>Direct access grants</code> （API 测试）</p></td>
       </tr>
     </tbody>
   </table>

   Keycloak 会以一组默认配置值部署该 client。 请根据你的 Keycloak 环境和期望行为按需修改这些值。 下表提供了一组可用于配置的基线设置和值：

   <table>
     <tbody>
       <tr>
         <td><p>Root URL</p></td>
         <td><p>设置为 <code>${authBaseUrl}</code></p></td>
       </tr>
       <tr>
         <td><p>Home URL</p></td>
         <td><p>设置为 MinIO 要使用的 Realm（<code>/realms/master/account/</code>）</p></td>
       </tr>
       <tr>
         <td><p>Valid Redirect URI</p></td>
         <td><p>设置为 <code>*</code></p></td>
       </tr>
       <tr>
         <td><p>Keys -&gt; Use JWKS URL</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Advanced -&gt; Advanced Settings -&gt; Access Token Lifespan</p></td>
         <td><p>设置为 <code>1 Hour</code>。</p></td>
       </tr>
     </tbody>
   </table>
2. 为 MinIO Client 创建 Client Scope

   Client scope 允许 Keycloak 在认证请求返回的 JSON Web Token（JWT）中映射用户属性。 这样 MinIO 就可以在向用户分配策略时引用这些属性。 这一步会创建在 Keycloak 认证成功后支持 MinIO 授权所需的 client scope。

   进入 **Client scopes** 视图，为 MinIO 授权创建一个新的 client scope：

   <table>
     <tbody>
       <tr>
         <td><p>Name</p></td>
         <td><p>设置为任意易识别的策略名称（<code>minio-authorization</code>）</p></td>
       </tr>
       <tr>
         <td><p>Include in token scope</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
     </tbody>
   </table>

   创建完成后，从列表中选中该 scope，并进入 **Mappers**。

   选择 **Configure a new mapper** 创建新的映射：

   <table>
     <tbody>
       <tr>
         <td><p>User Attribute</p></td>
         <td><p>选择 Mapper Type</p></td>
       </tr>
       <tr>
         <td><p>Name</p></td>
         <td><p>设置为任意易识别的映射名称（<code>minio-policy-mapper</code>）</p></td>
       </tr>
       <tr>
         <td><p>User Attribute</p></td>
         <td><p>设置为 <code>policy</code></p></td>
       </tr>
       <tr>
         <td><p>Token Claim Name</p></td>
         <td><p>设置为 <code>policy</code></p></td>
       </tr>
       <tr>
         <td><p>Add to ID token</p></td>
         <td><p>设置为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Claim JSON Type</p></td>
         <td><p>设置为 <code>String</code></p></td>
       </tr>
       <tr>
         <td><p>Multivalued</p></td>
         <td><p>设置为 <code>On</code></p><p>这样可以在单个 claim 中设置多个 <code>policy</code> 值。</p></td>
       </tr>
       <tr>
         <td><p>Aggregate attribute values</p></td>
         <td><p>设置为 <code>On</code></p><p>这样用户就可以继承其所属 Group 中设置的任意 <code>policy</code>。</p></td>
       </tr>
     </tbody>
   </table>

   创建完成后，将该 Client Scope 分配给 MinIO client。

   1. 进入 **Clients** 并选择 MinIO client。
   2. 选择 **Client scopes**，然后选择 **Add client scope**。
   3. 选择先前创建的 scope，并将 **Assigned type** 设置为 `default`。
3. 将所需属性应用到 Keycloak Users/Groups

   你必须为 Keycloak Users 或 Groups 分配一个名为 `policy` 的属性。 将其值设置为 MinIO 部署上的任意 [policy](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

   对于 Users，进入 **Users** 并选择或创建 User：

   <table>
     <tbody>
       <tr>
         <td><p>Credentials</p></td>
         <td><p>如果尚未设置，将用户密码设置为永久值</p></td>
       </tr>
       <tr>
         <td><p>Attributes</p></td>
         <td><p>创建一个新属性，键为 <code>policy</code>，值为 MinIO 部署上的任意 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a> （<code>consoleAdmin</code>）</p></td>
       </tr>
     </tbody>
   </table>

   对于 Groups，进入 **Groups** 并选择或创建 Group：

   <table>
     <tbody>
       <tr>
         <td><p>Attributes</p></td>
         <td><p>创建一个新属性，键为 <code>policy</code>，值为 MinIO 部署上的任意 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a> （<code>consoleAdmin</code>）</p></td>
       </tr>
     </tbody>
   </table>

   你可以将用户加入组，使其继承指定的 `policy` 属性。 如果 Mapper 设置中启用了 **Aggregate attribute values**， Keycloak 会在已认证用户的 JWT token 中包含聚合后的策略数组。 MinIO 可以在为用户授权时使用这份策略列表。

   你可以使用 Keycloak API 测试某个用户配置的策略：

   ```shell
   curl -d "client_id=minio" \
        -d "client_secret=secretvalue" \
        -d "grant_type=password" \
        -d "username=minio-user-1" \
        -d "password=minio-user-1-password" \
        http://keycloak-service.keycloak-namespace.svc.cluster-domain.example/realms/REALM/protocol/openid-connect/token
   ```

   如果成功，`access_token` 中会包含调用 MinIO [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) STS API 并生成 S3 凭证所需的 JWT。

   你可以使用 JWT 解码器检查其载荷，确认其中包含 `policy` 键， 且列出了一个或多个 MinIO policy。
4. 为 Keycloak 认证配置 MinIO

你可以使用 [`mc idp openid add`](/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.add) 命令为 Keycloak 服务创建新配置。 该命令接受所有受支持的 [OpenID Configuration Settings](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings)：

```shell
mc idp openid add ALIAS PRIMARY_IAM \
   client_id=MINIO_CLIENT \
   client_secret=MINIO_CLIENT_SECRET \
   config_url="https://keycloak-service.keycloak-namespace.svc.cluster-domain.example/realms/REALM/.well-known/openid-configuration" \
   display_name="SSO_IDENTIFIER"
   scopes="openid,email,preferred_username" \
   redirect_uri_dynamic="on"
```

<table>
  <tbody>
    <tr>
      <td><p><code>PRIMARY_IAM</code></p></td>
      <td><p>设置为该 Keycloak 服务的唯一标识符，例如 <code>keycloak_primary</code></p></td>
    </tr>
    <tr>
      <td><code>MINIO_CLIENT</code><br /><code>MINIO_CLIENT_SECRET</code><br /></td>
      <td><p>设置为步骤 1 中配置的 Keycloak client ID 和 secret</p></td>
    </tr>
    <tr>
      <td><p><code>config_url</code></p></td>
      <td><p>设置为 Keycloak OpenID 配置文档的地址（keycloak-service.keycloak-namespace.svc.cluster-domain.example）</p></td>
    </tr>
    <tr>
      <td><p><code>display_name</code></p></td>
      <td><p>设置为 MinIO Console 在单点登录（SSO）流程中向用户显示的该 Keycloak 服务名称</p></td>
    </tr>
    <tr>
      <td><p><code>scopes</code></p></td>
      <td><p>设置为你希望包含在 JWT 中的 OpenID scope 列表，例如 <code>preferred_username</code> 或 <code>email</code></p></td>
    </tr>
    <tr>
      <td><p><code>redirect_uri_dynamic</code></p></td>
      <td><p>设置为 <code>on</code></p><p>这会将客户端所使用的 MinIO Console 地址替换到 Keycloak 重定向 URI 中。
Keycloak 会使用提供的 URI 将已认证用户返回到 Console。</p><p>对于位于反向代理、负载均衡器或类似网络控制平面之后的 MinIO Console 部署，
你也可以使用 <a href="/docs/reference/minio-server/settings/console/#envvar.MINIO_BROWSER_REDIRECT_URL"><code>MINIO_BROWSER_REDIRECT_URL</code></a> 变量设置 Keycloak 应使用的重定向地址。</p></td>
    </tr>
  </tbody>
</table>

重启 MinIO 部署以应用这些更改。

检查 MinIO 日志，确认启动成功，且没有与 OIDC 配置相关的错误。

1. 使用 Security Token Service（STS）生成应用程序凭证

   使用 S3 兼容 SDK 的应用程序必须以 Access Key 和 Secret Key 的形式提供凭证。 MinIO [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) API 会使用 Keycloak 在认证后返回的 JWT 返回所需的临时凭证， 其中包括必须提供的 session token。

   你可以使用以下 HTTP 调用序列和 `curl` 工具测试这一工作流：

   1. 以 Keycloak 用户身份认证并获取 JWT token

      ```shell
      curl -X POST "https://keycloak-service.keycloak-namespace.svc.cluster-domain.example/realms/REALM/protocol/openid-connect/token" \
           -H "Content-Type: application/x-www-form-urlencoded" \
           -d "username=USER" \
           -d "password=PASSWORD" \
           -d "grant_type=password" \
           -d "client_id=CLIENT" \
           -d "client_secret=SECRET"
      ```

      - 将 `USER` 和 `PASSWORD` 替换为 `REALM` 中某个 Keycloak 用户的凭证。
      - 将 `CLIENT` 和 `SECRET` 替换为该 `REALM` 中 MinIO 专用 Keycloak client 的 ID 和 secret。

      你可以使用 `jq` 或类似的 JSON 格式化工具处理返回结果。 提取 `access_token` 字段以获取所需的访问 token。 同时关注 `expires_in` 字段，以了解 token 过期前还剩多少秒。
   2. 使用 `AssumeRoleWithWebIdentity` API 生成 MinIO 凭证

      ```shell
      curl -X POST "https://minio.minio-tenant.svc.cluster-domain.example" \
           -H "Content-Type: application/x-www-form-urlencoded" \
           -d "Action=AssumeRoleWithWebIdentity" \
           -d "Version=2011-06-15" \
           -d "DurationSeconds=86000" \
           -d "WebIdentityToken=TOKEN"
      ```

      将 `TOKEN` 替换为 Keycloak 返回的 `access_token` 值。

      API 成功时会返回一个 XML 文档，其中包含以下键：

      - `Credentials.AccessKeyId` - Keycloak 用户的 Access Key
      - `Credentials.SecretAccessKey` - Keycloak 用户的 Secret Key
      - `Credentials.SessionToken` - Keycloak 用户的 Session Token
      - `Credentials.Expiration` - 生成凭证的过期时间
   3. 测试这些凭证

      使用你偏好的 S3 兼容 SDK，利用生成的凭证连接到 MinIO。

      例如，下面的 Python 代码使用 MinIO [Python SDK](/docs/developers/python/minio-py/#minio-python-quickstart) 连接到 MinIO 部署并返回存储桶列表：

      ```python
      from minio import Minio

      client = MinIO(
         "minio.minio-tenant.svc.cluster-domain.example",
         access_key = "ACCESS_KEY",
         secret_key = "SECRET_KEY",
         session_token = "SESSION_TOKEN"
         secure = True
      )

      client.list_buckets()
      ```

2. 后续步骤

应用程序应使用其选择的 [SDK](/docs/developers/minio-drivers/#minio-drivers) 实现 [STS AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) 流程。 当 STS 凭证过期时，应用程序应具备在重试并继续操作之前重新生成 JWT token、 STS token 和 MinIO 凭证的逻辑。

或者，用户也可以通过 MinIO Console 使用其 Keycloak 凭证生成 [access keys](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)， 以创建类似长期 API key 的访问方式。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
1. 配置或创建用于访问 Keycloak 的 Client

   认证到 Keycloak **Administrative Console**，然后进入 **Clients**。

   选择 **Create client**，按照提示为 MinIO 创建一个新的 Keycloak client。 按如下方式填写指定输入项：

   <table>
     <tbody>
       <tr>
         <td><p>Client ID</p></td>
         <td><p>设置为 MinIO 的唯一标识符（<code>minio</code>）</p></td>
       </tr>
       <tr>
         <td><p>Client type</p></td>
         <td><p>设置为 <code>OpenID Connect</code></p></td>
       </tr>
       <tr>
         <td><p>Always display in console</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Client authentication</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Authentication flow</p></td>
         <td><p>打开 <code>Standard flow</code></p></td>
       </tr>
       <tr>
         <td><p>（可选）<em>Authentication flow</em></p></td>
         <td><p>打开 <code>Direct access grants</code> （API 测试）</p></td>
       </tr>
     </tbody>
   </table>

   Keycloak 会以一组默认配置值部署该 client。 请根据你的 Keycloak 环境和期望行为按需修改这些值。 下表提供了一组可用于配置的基线设置和值：

   <table>
     <tbody>
       <tr>
         <td><p>Root URL</p></td>
         <td><p>设置为 <code>${authBaseUrl}</code></p></td>
       </tr>
       <tr>
         <td><p>Home URL</p></td>
         <td><p>设置为 MinIO 要使用的 Realm（<code>/realms/master/account/</code>）</p></td>
       </tr>
       <tr>
         <td><p>Valid Redirect URI</p></td>
         <td><p>设置为 <code>*</code></p></td>
       </tr>
       <tr>
         <td><p>Keys -&gt; Use JWKS URL</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Advanced -&gt; Advanced Settings -&gt; Access Token Lifespan</p></td>
         <td><p>设置为 <code>1 Hour</code>。</p></td>
       </tr>
     </tbody>
   </table>
2. 为 MinIO Client 创建 Client Scope

   Client Scope 允许 Keycloak 在认证请求返回的 JSON Web Token（JWT）中映射用户属性。 这样 MinIO 就可以在向用户分配策略时引用这些属性。 此步骤会创建在 Keycloak 认证成功后支持 MinIO 授权所需的 Client Scope。

   进入 **Client scopes** 视图，为 MinIO 授权创建一个新的 client scope：

   <table>
     <tbody>
       <tr>
         <td><p>Name</p></td>
         <td><p>设置为任意易识别的策略名称（<code>minio-authorization</code>）</p></td>
       </tr>
       <tr>
         <td><p>Include in token scope</p></td>
         <td><p>切换为 <code>On</code></p></td>
       </tr>
     </tbody>
   </table>

   创建完成后，从列表中选中该 scope，并进入 **Mappers**。

   选择 **Configure a new mapper** 创建新的映射：

   <table>
     <tbody>
       <tr>
         <td><p>User Attribute</p></td>
         <td><p>选择 Mapper Type</p></td>
       </tr>
       <tr>
         <td><p>Name</p></td>
         <td><p>设置为任意易识别的映射名称（<code>minio-policy-mapper</code>）</p></td>
       </tr>
       <tr>
         <td><p>User Attribute</p></td>
         <td><p>设置为 <code>policy</code></p></td>
       </tr>
       <tr>
         <td><p>Token Claim Name</p></td>
         <td><p>设置为 <code>policy</code></p></td>
       </tr>
       <tr>
         <td><p>Add to ID token</p></td>
         <td><p>设置为 <code>On</code></p></td>
       </tr>
       <tr>
         <td><p>Claim JSON Type</p></td>
         <td><p>设置为 <code>String</code></p></td>
       </tr>
       <tr>
         <td><p>Multivalued</p></td>
         <td><p>设置为 <code>On</code></p><p>这样可以在单个 claim 中设置多个 <code>policy</code> 值。</p></td>
       </tr>
       <tr>
         <td><p>Aggregate attribute values</p></td>
         <td><p>设置为 <code>On</code></p><p>这样用户就可以继承其所属 Group 中设置的任意 <code>policy</code>。</p></td>
       </tr>
     </tbody>
   </table>

   创建完成后，将该 Client Scope 分配给 MinIO client。

   1. 进入 **Clients** 并选择 MinIO client。
   2. 选择 **Client scopes**，然后选择 **Add client scope**。
   3. 选择先前创建的 scope，并将 **Assigned type** 设置为 `default`。
3. 将所需属性应用到 Keycloak Users/Groups

   必须为 Keycloak Users 或 Groups 分配一个名为 `policy` 的属性。 将其值设置为 MinIO 部署上的任意 [policy](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

   对于 Users，进入 **Users** 并选择或创建 User：

   <table>
     <tbody>
       <tr>
         <td><p>Credentials</p></td>
         <td><p>如果尚未设置，将用户密码设置为永久值</p></td>
       </tr>
       <tr>
         <td><p>Attributes</p></td>
         <td><p>创建一个新属性，键为 <code>policy</code>，值为 MinIO 部署上的任意 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a> （<code>consoleAdmin</code>）</p></td>
       </tr>
     </tbody>
   </table>

   对于 Groups，进入 **Groups** 并选择或创建 Group：

   <table>
     <tbody>
       <tr>
         <td><p>Attributes</p></td>
         <td><p>创建一个新属性，键为 <code>policy</code>，值为 MinIO 部署上的任意 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a> （<code>consoleAdmin</code>）</p></td>
       </tr>
     </tbody>
   </table>

   你可以将用户加入组，使其继承指定的 `policy` 属性。 如果 Mapper 设置中启用了 **Aggregate attribute values**， Keycloak 会在已认证用户的 JWT token 中包含聚合后的策略数组。 MinIO 可以在为用户授权时使用这份策略列表。

   你可以使用 Keycloak API 测试某个用户配置的策略：

   ```shell
   curl -d "client_id=minio" \
        -d "client_secret=secretvalue" \
        -d "grant_type=password" \
        -d "username=minio-user-1" \
        -d "password=minio-user-1-password" \
        http://keycloak-url.example.net:8080/realms/REALM/protocol/openid-connect/token
   ```

   如果成功，`access_token` 中会包含调用 MinIO [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) STS API 并生成 S3 凭证所需的 JWT。

   你可以使用 JWT 解码器检查其载荷，确认其中包含 `policy` 键， 且列出了一个或多个 MinIO policy。
4. 为 Keycloak 认证配置 MinIO

   MinIO 支持多种配置 Keycloak 认证的方法：

   - 使用终端/shell 以及 [`mc idp openid`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 命令
   - 使用在启动 MinIO 之前设置的环境变量

   {{< tabs group="cli-tab2" >}}
   {{< tab label="CLI" value="cli" >}}
   你可以使用 [`mc idp openid add`](/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.add) 命令为 Keycloak 服务创建新配置。 该命令接受所有受支持的 [OpenID Configuration Settings](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings)：

   ```shell
   mc idp openid add ALIAS PRIMARY_IAM \
      client_id=MINIO_CLIENT \
      client_secret=MINIO_CLIENT_SECRET \
      config_url="https://keycloak-url.example.net:8080/realms/REALM/.well-known/openid-configuration" \
      display_name="SSO_IDENTIFIER"
      scopes="openid,email,preferred_username" \
      redirect_uri_dynamic="on"
   ```

   <table>
     <tbody>
       <tr>
         <td><p><code>PRIMARY_IAM</code></p></td>
         <td><p>设置为该 Keycloak 服务的唯一标识符，例如 <code>keycloak_primary</code></p></td>
       </tr>
       <tr>
         <td><code>MINIO_CLIENT</code><br /><code>MINIO_CLIENT_SECRET</code><br /></td>
         <td><p>设置为步骤 1 中配置的 Keycloak client ID 和 secret</p></td>
       </tr>
       <tr>
         <td><p><code>config_url</code></p></td>
         <td><p>设置为 Keycloak OpenID 配置文档的地址（keycloak-url.example.net:8080）</p></td>
       </tr>
       <tr>
         <td><p><code>display_name</code></p></td>
         <td><p>设置为 MinIO Console 在单点登录（SSO）流程中向用户显示的该 Keycloak 服务名称</p></td>
       </tr>
       <tr>
         <td><p><code>scopes</code></p></td>
         <td><p>设置为你希望包含在 JWT 中的 OpenID scope 列表，例如 <code>preferred_username</code> 或 <code>email</code></p></td>
       </tr>
       <tr>
         <td><p><code>redirect_uri_dynamic</code></p></td>
         <td><p>设置为 <code>on</code></p><p>这会将客户端所使用的 MinIO Console 地址替换到 Keycloak 重定向 URI 中。
   Keycloak 会使用提供的 URI 将已认证用户返回到 Console。</p><p>对于位于反向代理、负载均衡器或类似网络控制平面之后的 MinIO Console 部署，
   你也可以使用 <a href="/docs/reference/minio-server/settings/console/#envvar.MINIO_BROWSER_REDIRECT_URL"><code>MINIO_BROWSER_REDIRECT_URL</code></a> 变量设置 Keycloak 应使用的重定向地址。</p></td>
       </tr>
     </tbody>
   </table>
   {{< /tab >}}
   {{< tab label="环境变量" value="tab2" >}}
   在使用 `-e ENVVAR=VALUE` 标志启动容器之前， 设置以下 [环境变量](/docs/reference/minio-server/settings/iam/openid/#minio-server-envvar-external-identity-management-openid)。

   下面的示例代码设置了将 Keycloak 配置为外部身份管理提供者所需的最小环境变量集合。

   ```shell
   MINIO_IDENTITY_OPENID_CONFIG_URL_PRIMARY_IAM="https://keycloak-url.example.net:8080/realms/REALM/.well-known/openid-configuration"
   MINIO_IDENTITY_OPENID_CLIENT_ID_PRIMARY_IAM="MINIO_CLIENT"
   MINIO_IDENTITY_OPENID_CLIENT_SECRET_PRIMARY_IAM="MINIO_CLIENT_SECRET"
   MINIO_IDENTITY_OPENID_DISPLAY_NAME_PRIMARY_IAM="SSO_IDENTIFIER"
   MINIO_IDENTITY_OPENID_SCOPES_PRIMARY_IAM="openid,email,preferred_username"
   MINIO_IDENTITY_OPENID_REDIRECT_URI_DYNAMIC_PRIMARY_IAM="on"
   ```

   <table>
     <tbody>
       <tr>
         <td><p><code>_PRIMARY_IAM</code></p></td>
         <td><p>将后缀 <code>_PRIMARY_IAM</code> 替换为该 Keycloak 配置的唯一标识符。
   例如，<code>MINIO_IDENTITY_OPENID_CONFIG_URL_KEYCLOAK_PRIMARY</code>。</p><p>如果你只打算为该部署配置单个 OIDC 提供者，也可以省略该后缀。</p></td>
       </tr>
       <tr>
         <td><p><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_CONFIG_URL"><code>CONFIG_URL</code></a></p></td>
         <td><p>指定 Keycloak OpenID 配置文档的地址（keycloak-url.example.net:8080）</p><p>确保其中的 <code>REALM</code> 与你希望用于 MinIO 用户认证的 Keycloak realm 一致</p></td>
       </tr>
       <tr>
         <td><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_CLIENT_ID"><code>CLIENT_ID</code></a><br /><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_CLIENT_SECRET"><code>CLIENT_SECRET</code></a><br /></td>
         <td><p>指定步骤 1 中配置的 Keycloak client ID 和 secret</p></td>
       </tr>
       <tr>
         <td><p><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_DISPLAY_NAME"><code>DISPLAY_NAME</code></a></p></td>
         <td><p>指定 MinIO Console 在单点登录（SSO）流程中向用户显示的该 Keycloak 服务名称</p></td>
       </tr>
       <tr>
         <td><p><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_SCOPES"><code>OPENID_SCOPES</code></a></p></td>
         <td><p>指定你希望包含在 JWT 中的 OpenID scope，例如 <code>preferred_username</code> 或 <code>email</code></p></td>
       </tr>
       <tr>
         <td><p><a href="/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_REDIRECT_URI_DYNAMIC"><code>REDIRECT_URI_DYNAMIC</code></a></p></td>
         <td><p>设置为 <code>on</code></p><p>这会将客户端所使用的 MinIO Console 地址替换到 Keycloak 重定向 URI 中。
   Keycloak 会使用提供的 URI 将已认证用户返回到 Console。</p><p>对于位于反向代理、负载均衡器或类似网络控制平面之后的 MinIO Console 部署，
   你也可以使用 <a href="/docs/reference/minio-server/settings/console/#envvar.MINIO_BROWSER_REDIRECT_URL"><code>MINIO_BROWSER_REDIRECT_URL</code></a> 变量设置 Keycloak 应使用的重定向地址。</p></td>
       </tr>
     </tbody>
   </table>

   有关这些变量的完整文档，请参见 [OpenID 身份管理设置](/docs/reference/minio-server/settings/iam/openid/#minio-server-envvar-external-identity-management-openid)
   {{< /tab >}}
   {{< /tabs >}}

   重启 MinIO 部署以应用这些更改。

   检查 MinIO 日志，确认启动成功，且没有与 OIDC 配置相关的错误。

   如果尝试通过 Console 登录，现在应能看到一个使用已配置 **Display Name** 的（SSO）按钮。

   指定一个已配置的用户并尝试登录。 MinIO 应自动将您重定向到 Keycloak 登录页面。 认证成功后，Keycloak 应使用原始 Console URL 或已配置的 **Redirect URI** 将您重定向回 MinIO Console。
5. 使用 Security Token Service（STS）生成应用程序凭证

   使用 S3 兼容 SDK 的应用程序必须以 Access Key 和 Secret Key 的形式提供凭证。 MinIO [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) API 会使用 Keycloak 在认证后返回的 JWT 返回所需的临时凭证， 其中包括必须提供的 session token。

   你可以使用以下 HTTP 调用序列和 `curl` 工具测试这一工作流：

   1. 以 Keycloak 用户身份认证并获取 JWT token

      ```shell
      curl -X POST "https://keycloak-url.example.net:8080/realms/REALM/protocol/openid-connect/token" \
           -H "Content-Type: application/x-www-form-urlencoded" \
           -d "username=USER" \
           -d "password=PASSWORD" \
           -d "grant_type=password" \
           -d "client_id=CLIENT" \
           -d "client_secret=SECRET"
      ```

      - 将 `USER` 和 `PASSWORD` 替换为 `REALM` 中某个 Keycloak 用户的凭证。
      - 将 `CLIENT` 和 `SECRET` 替换为该 `REALM` 中 MinIO 专用 Keycloak client 的 ID 和 secret。

      你可以使用 `jq` 或类似的 JSON 格式化工具处理返回结果。 提取 `access_token` 字段以获取所需的访问 token。 同时关注 `expires_in` 字段，以了解 token 过期前还剩多少秒。
   2. 使用 `AssumeRoleWithWebIdentity` API 生成 MinIO 凭证

      ```shell
      curl -X POST "https://minio-url.example.net:9000" \
           -H "Content-Type: application/x-www-form-urlencoded" \
           -d "Action=AssumeRoleWithWebIdentity" \
           -d "Version=2011-06-15" \
           -d "DurationSeconds=86000" \
           -d "WebIdentityToken=TOKEN"
      ```

      将 `TOKEN` 替换为 Keycloak 返回的 `access_token` 值。

      API 成功时会返回一个 XML 文档，其中包含以下键：

      - `Credentials.AccessKeyId` - Keycloak 用户的 Access Key
      - `Credentials.SecretAccessKey` - Keycloak 用户的 Secret Key
      - `Credentials.SessionToken` - Keycloak 用户的 Session Token
      - `Credentials.Expiration` - 生成凭证的过期时间
   3. 测试这些凭证

      使用你偏好的 S3 兼容 SDK，利用生成的凭证连接到 MinIO。

      例如，下面的 Python 代码使用 MinIO [Python SDK](/docs/developers/python/minio-py/#minio-python-quickstart) 连接到 MinIO 部署并返回存储桶列表：

      ```python
      from minio import Minio

      client = MinIO(
         "minio-url.example.net:9000",
         access_key = "ACCESS_KEY",
         secret_key = "SECRET_KEY",
         session_token = "SESSION_TOKEN"
         secure = True
      )

      client.list_buckets()
      ```

6. 后续步骤

   应用程序应使用所选 [SDK](/docs/developers/minio-drivers/#minio-drivers) 实现 [STS AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) 流程。 当 STS 凭证过期时，应用程序应具备在重试并继续操作之前重新生成 JWT token、 STS token 和 MinIO 凭证的逻辑。

   或者，用户也可以通过 MinIO Console 使用其 Keycloak 凭证生成 [access keys](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)， 以创建类似长期 API key 的访问方式。
{{< /tab >}}
{{< /tabs >}}

## 启用 Keycloak Admin REST API {#keycloak-admin-rest-api}

MinIO 支持使用 Keycloak Admin REST API 检查认证用户是否存在，*以及* 该用户是否在 Keycloak realm 中处于启用状态。 这一功能使 MinIO 可以更快地撤销此前已经认证过的 Keycloak 用户访问权限。 如果没有这项功能，MinIO 对已禁用或已删除用户最早能够生效的访问撤销时间点，只能等到最后一次获取的认证 token 过期。

本流程假定你已经拥有一个现成的 MinIO 部署，并已将 Keycloak 配置为外部身份管理器。

### 1) 创建所需的 Client Scopes {#client-scopes}

进入 **Client scopes** 视图并创建一个新的 scope：

<table>
  <tbody>
    <tr>
      <td><p>Name</p></td>
      <td><p>将 scope 名称设置为一个易于识别的名字（<code>minio-admin-API-access</code>）</p></td>
    </tr>
    <tr>
      <td><p>Mappers</p></td>
      <td><p>选择 Configure a new mapper</p></td>
    </tr>
    <tr>
      <td><p>Audience</p></td>
      <td><p>将 Name 设置为一个易于识别的映射名称（<code>minio-admin-api-access-mapper</code>）</p></td>
    </tr>
    <tr>
      <td><p>Included Client Audience</p></td>
      <td><p>设置为 <code>security-admin-console</code>。</p></td>
    </tr>
  </tbody>
</table>

进入 **Clients**，并选择 MinIO client

1. 在 **Service account roles** 中，选择 **Assign role** 并分配 `admin` 角色
2. 在 **Client scopes** 中，选择 **Add client scope** 并添加前面创建的 scope

进入 **Settings**，并确保 **Authentication flow** 中包含 `Service accounts roles`。

### 2) 验证 Admin API 访问 {#admin-api}

你可以使用 MinIO client 凭证调用 Admin REST API，以获取 bearer token 和用户数据，从而验证该功能：

1. 获取 bearer token：

   ```shell
   curl -d "client_id=minio" \
        -d "client_secret=secretvalue" \
        -d "grant_type=password" \
        http://keycloak-url:port/admin/realms/REALM/protocol/openid-connect/token
   ```

2. 使用返回结果中的 `access_token` 访问 Admin API：

   ```shell
   curl -H "Authentication: Bearer ACCESS_TOKEN_VALUE" \
        http://keycloak-url:port/admin/realms/REALM/users/UUID
   ```

   将 `UUID` 替换为你要查询用户的唯一 ID。 响应应类似如下：

   ```json
   {
      "id": "954de141-781b-4eaf-81bf-bf3751cdc5f2",
      "createdTimestamp": 1675866684976,
      "username": "minio-user-1",
      "enabled": true,
      "totp": false,
      "emailVerified": false,
      "firstName": "",
      "lastName": "",
      "attributes": {
         "policy": [
            "readWrite"
         ]
      },
      "disableableCredentialTypes": [],
      "requiredActions": [],
      "notBefore": 0,
      "access": {
         "manageGroupMembership": true,
         "view": true,
         "mapRoles": true,
         "impersonate": true,
         "manage": true
      }
   }
   ```

   如果返回值中的 enabled 为 false 或 null（用户已从 Keycloak 中移除），MinIO 会撤销该认证用户的访问权限。

### 3) 在 MinIO 上启用 Keycloak Admin 支持 {#minio-keycloak-admin}

MinIO 支持多种方式来配置 Keycloak Admin API 支持：

- 使用终端 / shell 以及 [`mc idp openid`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 命令
- 使用在启动 MinIO 之前设置的环境变量

{{< tabs group="cli-environment-variables" >}}
{{< tab label="CLI" value="cli" >}}
你可以使用 [`mc idp openid update`](/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.update) 命令修改现有 Keycloak 服务的配置项。 如果是首次配置 Keycloak，也可以直接在初始设置时包含以下配置项。 该命令接受所有受支持的 [OpenID 配置项](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings)：

```shell
mc idp openid update ALIAS KEYCLOAK_IDENTIFIER \
   vendor="keycloak" \
   keycloak_admin_url="https://keycloak-url:port/admin"
   keycloak_realm="REALM"
```

- 将 `KEYCLOAK_IDENTIFIER` 替换为已配置 Keycloak IDP 的名称。 你可以使用 [`mc idp openid ls`](/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.ls) 查看 MinIO 部署上所有已配置的 IDP 项
- 在 [`keycloak_admin_url`](/docs/reference/minio-server/settings/iam/openid/#mc-conf.identity_openid.keycloak_admin_url) 配置项中指定 Keycloak admin URL
- 在 [`keycloak_realm`](/docs/reference/minio-server/settings/iam/openid/#mc-conf.identity_openid.keycloak_realm) 中指定 Keycloak Realm 名称
{{< /tab >}}
{{< tab label="Environment Variables" value="environment-variables" >}}
在合适的配置位置（例如 `/etc/default/minio`）设置以下 [环境变量](/docs/reference/minio-server/settings/iam/openid/#minio-server-envvar-external-identity-management-openid)。

以下示例代码设置了在现有 Keycloak 配置上启用 Keycloak Admin API 所需的最小环境变量集合。 请将后缀 `_PRIMARY_IAM` 替换为目标 Keycloak 配置的唯一标识符。

```shell
MINIO_IDENTITY_OPENID_VENDOR_PRIMARY_IAM="keycloak"
MINIO_IDENTITY_OPENID_KEYCLOAK_ADMIN_URL_PRIMARY_IAM="https://keycloak-url:port/admin"
MINIO_IDENTITY_OPENID_KEYCLOAK_REALM_PRIMARY_IAM="REALM"
```

- 在 [`MINIO_IDENTITY_OPENID_KEYCLOAK_ADMIN_URL`](/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_KEYCLOAK_ADMIN_URL) 中指定 Keycloak admin URL
- 在 [`MINIO_IDENTITY_OPENID_KEYCLOAK_REALM`](/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_KEYCLOAK_REALM) 中指定 Keycloak Realm 名称
{{< /tab >}}
{{< /tabs >}}