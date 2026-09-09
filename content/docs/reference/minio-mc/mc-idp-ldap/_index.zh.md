---
title: "mc idp ldap"

weight: 140
icon: fa-solid fa-address-book
---

<a id="mc-idp-ldap"></a>
<a id="minio-mc-idp-ldap"></a>

<a id="command-mc.idp.ldap"></a>

> [!NOTE]
> **新增: RELEASE.2023-05-26T23-31-54Z**
>
> [`mc idp ldap`](#command-mc.idp.ldap) and its subcommands replace `mc admin idp ldap`.

## 描述 {#id2}

[`mc idp ldap`](#command-mc.idp.ldap) 命令用于管理第三方 [Active Directory 或 LDAP 身份与访问管理（IAM）集成](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 的配置。

[`mc idp ldap`](#command-mc.idp.ldap) 命令可作为在 [设置 AD/LDAP 连接](/docs/operations/external-iam/configure-ad-ldap-external-identity-management/#minio-authenticate-using-ad-ldap-generic) 时使用环境变量的替代方案。它们仅支持 MinIO 部署。

有关如何使用这些命令的教程，请参阅 [Active Directory / LDAP 访问管理](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap)。

> [!NOTE]
> **说明**
>
> MinIO [AD/LDAP 环境变量](/docs/reference/minio-server/settings/iam/ldap/#minio-server-envvar-external-identity-management-ad-ldap) 会覆盖通过此命令修改或设置的对应配置项。

[`mc idp ldap`](#command-mc.idp.ldap) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-add/#command-mc.idp.ldap.add"><code>mc idp ldap add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-add/#command-mc.idp.ldap.add"><code>mc idp ldap add</code></a> 命令用于创建 AD/LDAP IDP 服务器配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-disable/#command-mc.idp.ldap.disable"><code>mc idp ldap disable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-disable/#command-mc.idp.ldap.disable"><code>mc idp ldap disable</code></a> 命令用于禁用当前已配置的 AD/LDAP 提供程序。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-enable/#command-mc.idp.ldap.enable"><code>mc idp ldap enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-enable/#command-mc.idp.ldap.enable"><code>mc idp ldap enable</code></a> 命令用于启用当前已配置的 AD/LDAP 提供程序。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-info/#command-mc.idp.ldap.info"><code>mc idp ldap info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-info/#command-mc.idp.ldap.info"><code>mc idp ldap info</code></a> 命令输出指定 MinIO 部署上 AD/LDAP 提供程序的当前配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-ls/#command-mc.idp.ldap.ls"><code>mc idp ldap ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-ls/#command-mc.idp.ldap.ls"><code>mc idp ldap ls</code></a> 命令列出 AD/LDAP 提供方当前已有的配置集合。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy"><code>mc idp ldap policy</code></a> 子命令</p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy"><code>mc idp ldap policy</code></a> 命令用于显示策略与关联组或用户之间的映射关系。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-rm/#command-mc.idp.ldap.rm"><code>mc idp ldap rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-rm/#command-mc.idp.ldap.rm"><code>mc idp ldap rm</code></a> 命令移除 AD/LDAP 提供方的现有配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-update/#command-mc.idp.ldap.update"><code>mc idp ldap update</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-update/#command-mc.idp.ldap.update"><code>mc idp ldap update</code></a> 命令用于修改 AD/LDAP 提供程序的现有配置集。</p></td>
    </tr>
  </tbody>
</table>