---
title: "OpenID Connect 访问管理"

weight: 20
---

<a id="openid-connect"></a>
<a id="minio-external-identity-management-openid-access-control"></a>
<a id="minio-external-identity-management-openid"></a>

MinIO 支持使用兼容 OpenID Connect (OIDC) 的 Identity Provider (IDP)，例如 Okta、KeyCloak、Dex、Google 或 Facebook，来进行外部用户身份管理。

对于由外部 OpenID Connect (OIDC) 兼容提供方管理的身份，MinIO 可以通过以下两种方式之一，将策略分配给已认证用户。

1. 使用 OIDC 认证流程返回的 [JSON Web Token claim](https://datatracker.ietf.org/doc/html/rfc7519#section-4)，识别需要分配给已认证用户的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。
2. 使用授权请求中指定的 `RoleArn`，分配附加到该提供方 RolePolicy 的策略。

默认情况下，MinIO 会拒绝访问用户已分配或继承的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 中未显式允许的任何操作或资源。 由 OIDC 提供方管理的用户必须在 JWT claim 中指定所需策略。如果用户的 JWT claim 没有与之匹配的 MinIO 策略，则该用户无权访问 MinIO 部署中的任何操作或资源。

MinIO 要检查的具体 claim 需要在 [使用 OIDC 身份管理部署集群](/docs/operations/external-iam/#minio-external-iam-oidc) 时进行配置。本页重点介绍如何创建与已配置 OIDC claims 匹配的 MinIO 策略。

## 认证与授权流程 {#id2}

MinIO 支持两种 OIDC 认证与授权流程：

1. RolePolicy 流在 MinIO 配置中设置已认证用户的分配策略。

   MinIO 建议在与 OpenID 提供方集成认证时使用 RolePolicy 方法。
2. JWT 流将已认证用户的分配策略作为 OIDC 配置的一部分进行设置。

MinIO 支持多个 OIDC 提供方配置。 但是，每个部署只能配置 **一个** 基于 JWT claim 的 OIDC 提供方。 所有其他提供方都必须使用 RolePolicy。

### RolePolicy 与 RoleArn {#rolepolicy-rolearn}

使用 RolePolicy 时，所有通过给定 RoleArn 生成 STS 凭证的客户端，都会获得与该 RoleArn 的 RolePolicy 配置关联的 [一个或多个策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

你可以使用 [OpenID 策略变量](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-variables-oidc) 创建策略，以编程方式控制每个用户可访问的内容。

应用程序使用 <abbr title="OpenID Connect">OIDC</abbr> 凭证并采用 RolePolicy claim 流时，其登录流程如下：

1. 创建 OIDC 配置。
2. 记录分配给该配置的 RoleArn，可在创建时或 MinIO 启动时获取。 将此 RoleArn 与 [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) STS API 一起使用。
3. 创建与该 RoleArn 配套使用的 RolePolicy。 使用 [`MINIO_IDENTITY_OPENID_ROLE_POLICY`](/docs/reference/minio-server/settings/iam/openid/#envvar.MINIO_IDENTITY_OPENID_ROLE_POLICY) 环境变量或 [`identity_openid role_policy`](/docs/reference/minio-server/settings/iam/openid/#mc-conf.identity_openid.role_policy) 配置项，定义该提供方要使用的策略列表
4. 用户在登录 MinIO 时选择已配置的 OIDC 提供方。
5. 用户完成对已配置 <abbr title="OpenID Connect">OIDC</abbr> 提供方的认证，并重定向回 MinIO。

   MinIO 仅支持 [OpenID Authorization Code Flow](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)。 不支持使用 Implicit Flow 进行认证。
6. MinIO 验证 API 调用中的 `RoleArn`，并检查要使用的 [RolePolicy](#minio-external-identity-management-openid-access-control)。 任何携带该 RoleArn 的认证请求都会获得相同的策略访问权限。
7. MinIO 在 STS API 响应中返回临时凭证，形式为 access key、secret key 和 session token。 这些凭证的权限与 RolePolicy 中指定的策略一致。
8. 应用程序使用 STS 端点返回的临时凭证，在 MinIO 上执行已认证的 S3 操作。

### JSON Web Token Claim {#json-web-token-claim}

使用 JSON Web Token 可以为不同用户单独分配策略。 但使用 Web Token 也意味着需要为不同 claim 管理多份策略，管理成本会更高。

应用程序使用 <abbr title="OpenID Connect">OIDC</abbr> 凭证并采用 JSON Web Token Claim 流时，其登录流程如下：

1. 对已配置的 <abbr title="OpenID Connect">OIDC</abbr> 提供方进行认证，并获取 [JSON Web Token (JWT)](https://jwt.io/introduction)。

   MinIO 仅支持 [OpenID Authorization Code Flow](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)。 不支持使用 Implicit Flow 进行认证。
2. 将 <abbr title="JSON Web Token">JWT</abbr> 提交到 MinIO Security Token Service (STS) [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) API 端点。

   MinIO 会根据已配置的 OIDC 提供方验证 <abbr title="JSON Web Token">JWT</abbr>。

   如果 JWT 有效，MinIO 会检查其中的 [claim](#minio-external-identity-management-openid-access-control)，该 claim 指定了要分配给已认证用户的一个或多个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 列表。MinIO 默认检查 `policy` claim。
3. MinIO 在 STS API 响应中返回临时凭证，形式为 access key、secret key 和 session token。这些凭证的权限与 JWT claim 中指定的策略一致。
4. 应用程序使用 STS 端点返回的临时凭证，在 MinIO 上执行已认证的 S3 操作。

MinIO 提供了一个示例 Go 应用 [web-identity.go](https://github.com/minio/minio/blob/master/docs/sts/web-identity.go)，用于处理完整登录流程。

#### 识别 JWT Claim 值 {#jwt-claim}

MinIO 使用 OIDC 认证流程返回的 JWT token，识别要分配给已认证用户的具体策略。

你可以使用 [JWT Debugging tool](https://jwt.io/) 对返回的 JWT token 进行解码，并验证用户属性中是否包含所需 claims。

有关 JWT claim 的更多信息，请参见 [RFC 7519: JWT Claim](https://datatracker.ietf.org/doc/html/rfc7519#section-4)。

关于如何配置用户 claims，请参见你所选 OIDC 提供方的文档。

## 创建与 Claims 匹配的策略 {#claims}

使用 [`mc admin policy`](/docs/reference/minio-mc-admin/mc-admin-policy/#command-mc.admin.policy) 命令创建与一个或多个 claim 值匹配的策略。

## OIDC 策略变量 {#oidc}

下表列出了用于授权 [OIDC 管理用户](#minio-external-identity-management-openid) 的受支持策略变量。

每个变量都对应认证用户 JWT token 中返回的一项 claim：

| 变量 | 说明 |
| --- | --- |
| `jwt:sub` | 返回用户的 `sub` claim。 |
| `jwt:iss` | 返回 ID token 中的 Issuer Identifier claim。 |
| `jwt:aud` | 返回 ID token 中的 Audience claim。 |
| `jwt:jti` | 返回客户端认证信息中的 JWT ID claim。 |
| `jwt:upn` | 返回客户端认证信息中的 User Principal Name claim。 |
| `jwt:name` | 返回用户的 `name` claim。 |
| `jwt:groups` | 返回用户的 `groups` claim。 |
| `jwt:given_name` | 返回用户的 `given_name` claim。 |
| `jwt:family_name` | 返回用户的 `family_name` claim。 |
| `jwt:middle_name` | 返回用户的 `middle_name` claim。 |
| `jwt:nickname` | 返回用户的 `nickname` claim。 |
| `jwt:preferred_username` | 返回用户的 `preferred_username` claim。 |
| `jwt:profile` | 返回用户的 `profile` claim。 |
| `jwt:picture` | 返回用户的 `picture` claim。 |
| `jwt:website` | 返回用户的 `website` claim。 |
| `jwt:email` | 返回用户的 `email` claim。 |
| `jwt:gender` | 返回用户的 `gender` claim。 |
| `jwt:birthdate` | 返回用户的 `birthdate` claim。 |
| `jwt:phone_number` | 返回用户的 `phone_number` claim。 |
| `jwt:address` | 返回用户的 `address` claim。 |
| `jwt:scope` | 返回用户的 `scope` claim。 |
| `jwt:client_id` | 返回用户的 `client_id` claim。 |

关于这些 scope 的更多信息，请参阅 [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) 文档。 你所选的 OIDC 提供方也可能有更具体的补充文档。

例如，以下策略使用变量将认证用户的 `preferred_username` 替换到 `Resource` 字段中， 使该用户只能访问与其用户名匹配的前缀：

```json
{
"Version": "2012-10-17",
"Statement": [
      {
         "Action": ["s3:ListBucket"],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket"],
         "Condition": {"StringLike": {"s3:prefix": ["${jwt:preferred_username}/*"]}}
      },
      {
         "Action": [
         "s3:GetObject",
         "s3:PutObject"
         ],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket/${jwt:preferred_username}/*"]
      }
   ]
}
```

MinIO 会将 `Resource` 字段中的 `${jwt:preferred_username}` 变量， 替换为 JWT token 中 `preferred_username` 的值。 随后，MinIO 会评估该策略，并对请求的 API 和资源授予或撤销访问权限。