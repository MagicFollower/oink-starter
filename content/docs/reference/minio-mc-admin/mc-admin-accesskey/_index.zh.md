---
title: "mc admin accesskey"

weight: 10
icon: fa-solid fa-key
---

<a id="mc-admin-accesskey"></a>
<a id="minio-mc-admin-accesskey"></a>

<a id="command-mc.admin.accesskey"></a>

> [!NOTE]
> **新增: MinIO客户端版本RELEASE.2024-10-08T09-37-26Z**

这些命令用于替代 [`mc admin user svcacct`](/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct) 命令及其子命令中的 MinIO IDP 功能。

## 描述 {#id2}

[`mc admin accesskey`](#command-mc.admin.accesskey) 命令及其子命令用于为 MinIO 部署中内部管理的用户创建和管理 [Access Keys](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account)。

每个访问密钥都关联到一个 [用户身份](/docs/administration/identity-access-management/#minio-authentication-and-identity-management)，并继承其父用户直接附加的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) *或* 父用户所属组的策略。 每个访问密钥还支持可选的内联策略，可进一步将访问限制为父用户可用操作和资源的一个子集。

[`mc admin user svcacct`](/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct) 仅支持为 [MinIO-managed](/docs/administration/identity-access-management/minio-user-management/#minio-users) 账户创建访问密钥。

要为 [Active Directory/LDAP-managed](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 账户创建访问密钥，请使用 [`mc idp ldap accesskey`](/docs/reference/minio-mc/mc-idp-ldap-accesskey/#command-mc.idp.ldap.accesskey) 及其子命令。 要管理 [OpenID Connect-managed users](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 的访问密钥，请登录 [MinIO Console](/docs/administration/minio-console/#minio-console) 并通过 UI 生成访问密钥。

[`mc admin accesskey`](#command-mc.admin.accesskey) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-create/#command-mc.admin.accesskey.create"><code>create</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-create/#command-mc.admin.accesskey.create"><code>mc admin accesskey create</code></a> 命令为现有 MinIO 用户添加新的 access key 和 secret key 对。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-disable/#command-mc.admin.accesskey.disable"><code>disable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-disable/#command-mc.admin.accesskey.disable"><code>mc admin accesskey disable</code></a> 命令用于禁用 MinIO IDP 用户的现有访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-edit/#command-mc.admin.accesskey.edit"><code>edit</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-edit/#command-mc.admin.accesskey.edit"><code>mc admin accesskey edit</code></a> 命令用于修改与指定用户关联的访问密钥配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-enable/#command-mc.admin.accesskey.enable"><code>enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-enable/#command-mc.admin.accesskey.enable"><code>mc admin accesskey enable</code></a> 命令用于启用现有访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-info/#command-mc.admin.accesskey.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-info/#command-mc.admin.accesskey.info"><code>mc admin accesskey info</code></a> 命令返回指定 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys">access key(s)</a> 的描述信息。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-list/#command-mc.admin.accesskey.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-list/#command-mc.admin.accesskey.ls"><code>mc admin accesskey ls</code></a> 命令列出 MinIO 部署管理的用户、访问密钥或临时 <a href="/docs/developers/security-token-service/#minio-security-token-service">security token service</a> 密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-remove/#command-mc.admin.accesskey.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-accesskey-remove/#command-mc.admin.accesskey.rm"><code>mc admin accesskey rm</code></a> 命令用于删除部署中与某个用户关联的访问密钥。</p></td>
    </tr>
  </tbody>
</table>