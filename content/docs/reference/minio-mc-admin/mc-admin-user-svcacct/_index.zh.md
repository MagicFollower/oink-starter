---
title: "mc admin user svcacct"

weight: 80
icon: fa-solid fa-user-tag
---

<a id="mc-admin-user-svcacct"></a>
<a id="minio-mc-admin-user-svcacct"></a>

<a id="command-mc.admin.user.svcacct"></a>

> [!WARNING]
> **重要**
>
> 这些命令已被替代，并将在未来的 MinIO 客户端版本中弃用。
>
> 自 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，与内置 MinIO IDP 用户及其访问密钥或 STS 令牌相关的功能，请使用 [`mc admin accesskey`](/docs/reference/minio-mc-admin/mc-admin-accesskey/#command-mc.admin.accesskey) 命令及其子命令。
>
> 对于 AD/LDAP 用户的访问密钥，请使用 [`mc idp ldap accesskey`](/docs/reference/minio-mc/mc-idp-ldap-accesskey/#command-mc.idp.ldap.accesskey) 命令及其子命令。

## 描述 {#id2}

[`mc admin user svcacct`](#command-mc.admin.user.svcacct) 命令及其子命令用于在 MinIO 部署上创建和管理 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account)。

自 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，这些命令已由 [`mc admin accesskey`](/docs/reference/minio-mc-admin/mc-admin-accesskey/#command-mc.admin.accesskey) 和 [`mc idp ldap accesskey`](/docs/reference/minio-mc/mc-idp-ldap-accesskey/#command-mc.idp.ldap.accesskey) 取代。 该命令及其子命令将在未来的 MinIO 客户端版本中弃用。

每个访问密钥都关联到一个 [用户身份](/docs/administration/identity-access-management/#minio-authentication-and-identity-management)，并继承其父用户所附加的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) *或* 父用户所属组的策略。 每个访问密钥还支持可选的内联策略，用于进一步将访问限制在父用户可用操作和资源的子集范围内。

[`mc admin user svcacct`](#command-mc.admin.user.svcacct) 仅支持为 [MinIO 托管](/docs/administration/identity-access-management/minio-user-management/#minio-users) 和 [Active Directory/LDAP 托管](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 账户创建访问密钥。

如需为 [OpenID Connect 托管用户](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 创建访问密钥，请登录 [MinIO Console](/docs/administration/minio-console/#minio-console) 并通过 UI 生成访问密钥。

[`mc admin user svcacct`](#command-mc.admin.user.svcacct) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-add/#command-mc.admin.user.svcacct.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-add/#command-mc.admin.user.svcacct.add"><code>mc admin user svcacct add</code></a> 命令为现有 MinIO 或 AD/LDAP 用户添加新的访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-disable/#command-mc.admin.user.svcacct.disable"><code>disable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-disable/#command-mc.admin.user.svcacct.disable"><code>mc admin user svcacct disable</code></a> 命令用于禁用现有访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-edit/#command-mc.admin.user.svcacct.edit"><code>edit</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-edit/#command-mc.admin.user.svcacct.edit"><code>mc admin user svcacct edit</code></a> 命令用于修改与指定用户关联的访问密钥配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-enable/#command-mc.admin.user.svcacct.enable"><code>enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-enable/#command-mc.admin.user.svcacct.enable"><code>mc admin user svcacct enable</code></a> 命令用于启用现有访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-info/#command-mc.admin.user.svcacct.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-info/#command-mc.admin.user.svcacct.info"><code>mc admin user svcacct info</code></a> 命令返回指定 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys">access key</a> 的描述信息。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-list/#command-mc.admin.user.svcacct.list"><code>list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-list/#command-mc.admin.user.svcacct.ls"><code>mc admin user svcacct ls</code></a> 命令列出与指定用户关联的所有访问密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-remove/#command-mc.admin.user.svcacct.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct-remove/#command-mc.admin.user.svcacct.rm"><code>mc admin user svcacct rm</code></a> 命令会删除部署中与某个用户关联的访问密钥。</p></td>
    </tr>
  </tbody>
</table>