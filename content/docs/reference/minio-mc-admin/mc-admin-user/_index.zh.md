---
title: "mc admin user"

weight: 190
icon: fa-solid fa-users
---

<a id="mc-admin-user"></a>

<a id="command-mc.admin.user"></a>

## 说明 {#id2}

[`mc admin user`](#command-mc.admin.user) 命令及其子命令用于管理 [MinIO 用户](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp)。

客户端 *必须* 使用与该部署中某个用户关联的 access key 和 secret key 对 MinIO 部署进行认证。 MinIO 用户是 MinIO 身份与访问管理中的关键组成部分。

要管理使用第三方 IDP 进行认证的用户，请使用对应提供方的命令：

- 对于 AD/LDAP，请使用 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)
- 对于兼容 OpenID Connect (OIDC) 的提供方，请使用 [`mc idp openid`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid)

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc idp` 命令**
>
> [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 和 [`mc idp openid`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 及其子命令仅支持对 MinIO 部署使用。

## 子命令 {#id3}

[`mc admin user`](#command-mc.admin.user) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-add/#command-mc.admin.user.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-add/#command-mc.admin.user.add"><code>mc admin user add</code></a> 命令会在目标 MinIO 部署中添加一个新的 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-disable/#command-mc.admin.user.disable"><code>disable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-disable/#command-mc.admin.user.disable"><code>mc admin user disable</code></a> 命令用于在目标 MinIO 部署上禁用 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-enable/#command-mc.admin.user.enable"><code>enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-enable/#command-mc.admin.user.enable"><code>mc admin user enable</code></a> 命令用于在目标 MinIO 部署上启用 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-info/#command-mc.admin.user.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-info/#command-mc.admin.user.info"><code>mc admin user info</code></a> 命令返回目标 MinIO 部署中某个 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>的详细信息。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-list/#command-mc.admin.user.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-list/#command-mc.admin.user.ls"><code>mc admin user ls</code></a> 命令会列出目标 MinIO 部署上的所有 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-remove/#command-mc.admin.user.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-remove/#command-mc.admin.user.rm"><code>mc admin user rm</code></a> 命令用于在目标 MinIO 部署上移除 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO 用户</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-sts-info/#command-mc.admin.user.sts.info"><code>sts info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-sts-info/#command-mc.admin.user.sts.info"><code>mc admin user sts info</code></a> 命令用于检索指定 STS 凭证的信息，例如生成该凭证的父 <a href="/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp">MinIO user</a>、关联策略和过期时间。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct"><code>svcacct</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct"><code>mc admin user svcacct</code></a> 命令及其子命令用于在 MinIO 部署上创建和管理 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account">访问密钥</a>。</p><p>自 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，这些命令已由 <a href="/docs/reference/minio-mc-admin/mc-admin-accesskey/#command-mc.admin.accesskey"><code>mc admin accesskey</code></a> 和 <a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey/#command-mc.idp.ldap.accesskey"><code>mc idp ldap accesskey</code></a> 取代。
该命令及其子命令将在未来的 MinIO 客户端版本中弃用。</p></td>
    </tr>
  </tbody>
</table>