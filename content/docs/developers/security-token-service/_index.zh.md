---
title: "Security Token Service (STS)"

weight: 200
icon: fa-solid fa-key
---

<a id="security-token-service-sts"></a>
<a id="minio-security-token-service"></a>

MinIO Security Token Service (STS) APIs 允许应用程序生成用于访问 MinIO 部署的临时凭证。

对于配置为使用外部身份管理器的 MinIO 部署，STS API 是 *必需* 的，因为该 API 可将外部 IDP 凭证转换为兼容 AWS Signature v4 的凭证。

## STS API 端点 {#sts-api}

MinIO 支持以下 STS API 端点：

| 端点 | 支持的 IDP | 说明 |
| --- | --- | --- |
| [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) | OpenID Connect | 使用 OIDC 提供方返回的 JWT token 生成 access key 和 secret key |
| [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) | Active Directory / LDAP | 使用为该 API 端点指定的 AD/LDAP 凭证生成 access key 和 secret key。 |
| [AssumeRoleWithCustomToken](/docs/developers/security-token-service/AssumeRoleWithCustomToken/#minio-sts-assumerolewithcustomtoken) | MinIO Identity Plugin | 生成一个 token，用于外部身份提供方和 [MinIO Identity Plugin](/docs/administration/identity-access-management/pluggable-authentication/#minio-external-identity-management-plugin)。 |