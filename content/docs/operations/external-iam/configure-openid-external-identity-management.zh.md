---
title: "配置 Silo 使用 OpenID 进行认证"

weight: 30
---

<a id="minio-openid"></a>
<a id="minio-authenticate-using-openid-generic"></a>

## 概览 {#id2}

MinIO 支持使用兼容 OpenID Connect (OIDC) 的 Identity Provider (IDP) 来管理外部用户身份，例如 Okta、KeyCloak、Dex、Google 或 Facebook。

本页提供了在 Kubernetes 和裸金属基础设施上的 MinIO 部署中配置 OIDC 的流程。

本流程包括：

- 为 MinIO 集群配置外部 OIDC 提供方
- 使用 MinIO `AssumeRoleWithWebIdentity` Security Token Service (STS) API 生成供应用程序使用的临时凭证

本流程是面向兼容 OIDC 提供方的通用配置流程。 有关认证与 JWT 获取的具体说明，请以你所选 OIDC 提供方的文档为准。

## 前提条件 {#id3}

### 兼容 OpenID-Connect (OIDC) 的 Identity Provider {#openid-connect-oidc-identity-provider}

本流程假定你已经拥有一个现成的 OIDC 提供方，例如 Okta、KeyCloak、Dex、Google 或 Facebook。 这些服务本身的配置不在本流程范围内。

MinIO 集群必须与 OIDC 提供方保持双向连通。

### 检查访问管理行为 {#id4}

请确保每个打算与 MinIO 配合使用的用户身份，都配置了合适的 [claim](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control)，以便 MinIO 能将认证用户关联到某个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。 未分配任何策略的 OpenID 用户，无权访问 MinIO 集群中的任何操作或资源。

对于基于 JWT claim 的认证，MinIO 仅支持使用 [OpenID Authorization Code Flow](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth) 的 OIDC 流程。

### 访问 MinIO 集群 {#minio}

本流程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 对 MinIO 集群执行操作。 请在一台能够访问该集群网络的机器上安装 `mc`。 关于如何下载和安装 `mc`，请参见 `mc` [安装快速开始](/docs/reference/minio-mc/#mc-install)。 本流程假定已为 MinIO 集群配置 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

<a id="id5"></a>

## 为 MinIO 配置 OpenID 外部身份管理 {#minio-external-identity-management-openid-configure}

1. 创建新的 OpenID 配置

   使用 [`mc idp openid add`](/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.add) 命令为 MinIO 集群创建新的 OIDC 配置。 以下示例命令假定你使用 OIDC 提供方返回的 JWT claims，来实现 [基于策略分配的授权](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control)。

   ```shell
   mc idp openid add ALIAS \
     client_id=minio-oidc-client-id \
     client_secret=minio-oidc-client-secret \
     config_url="https://openid-provider.example.net/REALM/.well-known/openid-configuration" \
     claim_name="minio-policies" \
     scopes="openid,groups"
   ```

   你也可以配置基于 `RoleArn` 的功能，让所有认证用户都使用由 `role_policy` 设置指定的单一策略。 例如，将 `role_policy="readOnly"` 设置为所有认证用户分配内置只读策略。
2. 检查 MinIO Server 日志

   MinIO 进程会在应用新配置时重启。 请检查日志，确认 OIDC 配置已成功持久化。

   如果你为一个或多个配置设置了 `role_policy`，输出中会包含一个可供 STS API 使用的 ARN。
3. 使用 OIDC 凭证生成兼容 S3 的临时凭证

   MinIO 要求客户端使用 [AWS Signature Version 4 protocol](https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html) 进行认证，同时保留对已弃用 Signature Version 2 协议的支持。 具体来说，客户端必须提供有效的 access key 和 secret key，才能访问任何 S3 或 MinIO 管理 API，例如 `PUT`、`GET` 和 `DELETE` 操作。

   应用程序可以按需使用 [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) Security Token Service (STS) API 端点，以及 <abbr title="OpenID Connect">OIDC</abbr> 提供方返回的 JSON Web Token (JWT)，生成临时访问凭证。

   应用程序必须提供一个工作流，用于登录 <abbr title="OpenID Connect">OIDC</abbr> 提供方，并获取与该认证会话关联的 JSON Web Token (JWT)。 关于认证成功后如何获取和解析 JWT token，请以提供方文档为准。MinIO 提供了一个示例 Go 应用 [web-identity.go](https://github.com/minio/minio/blob/master/docs/sts/web-identity.go)，展示了如何管理这一工作流。

   应用程序获取到 JWT token 后，使用 `AssumeRoleWithWebIdentity` 端点生成临时凭证：

   ```shell
   POST https://minio.example.net?Action=AssumeRoleWithWebIdentity
   &WebIdentityToken=TOKEN
   &Version=2011-06-15
   &DurationSeconds=86400
   &Policy=Policy
   ```

   - 将 `TOKEN` 替换为上一步返回的 JWT token。
   - 将 `DurationSeconds` 替换为临时凭证过期前的秒数。上例指定了 `86400` 秒，即 24 小时。
   - 将 `Policy` 替换为内联、经过 URL 编码的 JSON [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)，用于进一步收紧临时凭证对应权限。

     如果省略，则使用该 OpenID 用户 [policy claim](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control) 中关联的策略。

   你也可以加入 `RoleArn` 参数（可选），并填写目标单策略 OIDC 配置对应的 ARN 字符串。

   API 响应是一个 XML 文档，其中包含 access key、secret key、session token 和过期时间。 应用程序可以使用 access key 和 secret key 来访问并操作 MinIO。

   参考文档请参见 [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity)。