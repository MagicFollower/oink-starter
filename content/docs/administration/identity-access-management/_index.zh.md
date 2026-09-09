---
title: "身份与访问管理"

weight: 140
icon: fa-solid fa-users-gear
---

<a id="minio-authentication-and-identity-management"></a>
<a id="id1"></a>

MinIO 要求客户端在每次发起新操作时同时完成认证与授权。

**Authentication**

> 用于验证连接客户端身份的过程。 MinIO 要求客户端使用 [AWS Signature Version 4 protocol](https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html) 进行认证，同时支持已弃用的 Signature Version 2 协议。 具体来说，客户端必须提供有效的 access key 和 secret key，才能访问任何 S3 或 MinIO 管理 API，例如 `PUT`、`GET` 和 `DELETE` 操作。

**Authorization**

> 用于限制已认证客户端在部署上可执行操作及可访问资源的过程。 MinIO 使用 基于策略的访问控制 (PBAC)，其中每个策略描述一条或多条规则，用于定义某个用户或某组用户的权限。 MinIO 在创建策略时支持 S3 特定的 [actions](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-actions) 和 [conditions](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-conditions)。 默认情况下，MinIO 会 *拒绝* 访问用户已分配或继承策略中未显式引用的操作或资源。

## Identity Management {#identity-management}

MinIO 同时支持内部和外部身份管理：

| IDentity Provider (IDP) | 说明 |
| --- | --- |
| [MinIO Internal IDP](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp) | 提供内置身份管理功能。 |
| [OpenID](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) | 支持通过兼容 OpenID Connect (OIDC) 的服务管理身份。 |
| [MinIO Authentication Plugin](/docs/administration/identity-access-management/pluggable-authentication/#minio-external-identity-management-plugin) | 支持使用 MinIO Authentication Plugin 扩展对接自定义外部身份管理器。 |
| [Active Directory / LDAP](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) | 支持通过 Active Directory 或 LDAP 服务管理身份。 |
| [Access Management Plugin](/docs/administration/identity-access-management/pluggable-authorization/#minio-external-access-management-plugin) | 支持使用 MinIO Access Management Plugin 扩展对接自定义外部访问管理器。 |

完成认证后，MinIO 会根据该已认证身份是否 *有权* 对指定资源执行该操作，决定允许还是拒绝客户端请求。

<a id="minio-access-management"></a>

## Access Management {#access-management}

MinIO 使用 基于策略的访问控制 (PBAC) 来定义已认证用户可访问的授权操作和资源。每个策略描述一条或多条 [actions](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-actions) 与 [conditions](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-conditions)，用于说明某个 [user](/docs/administration/identity-access-management/minio-user-management/#minio-users) 或 [group](/docs/administration/identity-access-management/minio-group-management/#minio-groups) 的权限。

MinIO 负责策略的创建与存储。将策略分配给用户或组的具体流程取决于所配置的 [IDentity Provider (IDP)](#minio-authentication-and-identity-management)。

使用 [MinIO Internal IDP](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp) 的 MinIO 部署，要求使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 命令将一个或多个策略显式关联到用户。用户也可以继承其所属 [groups](/docs/administration/identity-access-management/minio-group-management/#minio-groups) 上附加的策略。

默认情况下，MinIO 会 *拒绝* 访问附加或继承策略未显式允许的操作或资源。未被显式分配策略且未继承任何策略的用户，无法执行任何 S3 或 MinIO 管理 API 操作。

对于使用外部 IDP 的 MinIO 部署，策略分配方式取决于所选 IDP：

<table>
  <tbody>
    <tr>
      <td><p><a href="/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid">OpenID Connect (OIDC)</a></p></td>
      <td><p>MinIO 会检查 JSON Web Token (JWT) claim（默认是 <code>policy</code>），其中包含要附加到已认证用户的一个或多个策略名称。如果这些策略不存在，则该用户无法在 MinIO 部署上执行任何操作。</p><p>MinIO 不支持将 OIDC 用户身份分配到 <a href="/docs/administration/identity-access-management/minio-group-management/#minio-groups">groups</a>。因此，IDP 管理员必须将所有必需策略分配到用户的 policy claim 中。</p><p>更多信息请参见 <a href="/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control">外部托管身份的访问控制</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap">Active Directory / LDAP (AD/LDAP)</a></p></td>
      <td><p>MinIO 会检查是否存在某个策略，其名称与已认证 AD/LDAP 用户的 Distinguished Name (DN) 匹配。</p><p>MinIO 还支持查询已认证 AD/LDAP 用户的组成员关系。对于每个返回的组，MinIO 都会分配名称与该组 DN 匹配的策略。</p><p>如果没有任何策略与用户 DN <em>或</em> 用户任一组 DN 匹配，则该用户无法在 MinIO 部署上执行任何操作。</p><p>更多信息请参见 <a href="/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-access-control">外部托管身份的访问控制</a>。</p></td>
    </tr>
  </tbody>
</table>

MinIO PBAC 在设计上兼容 AWS IAM 策略语法、结构和行为。MinIO 文档会尽力覆盖 IAM 特定行为和功能。若需要更完整的 IAM、IAM 策略或 IAM JSON 语法文档，请参考 [IAM documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/)。

> [!NOTE]
> **`Deny` overrides `Allow`**
>
> MinIO 遵循 AWS IAM 策略求值规则，即在同一操作/资源上，`Deny` 规则会覆盖 `Allow` 规则。例如，如果某个用户被显式分配的策略对某个操作/资源包含 `Allow` 规则，而其所属某个组被分配的策略对同一操作/资源包含 `Deny` 规则，则 MinIO 只会应用 `Deny` 规则。
>
> 有关 IAM 策略求值逻辑的更多信息，请参见 IAM 文档中的 [Determining Whether a Request is Allowed or Denied Within an Account](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html#policy-eval-denyallow)。