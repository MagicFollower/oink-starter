---
title: "mc idp ldap accesskey"

weight: 150
icon: fa-solid fa-key
---

<a id="mc-idp-ldap-accesskey"></a>
<a id="minio-mc-idp-ldap-accesskey"></a>

<a id="command-mc.idp.ldap.accesskey"></a>

> [!NOTE]
> **新增: RELEASE.2023-10-30T18-43-32Z**

## 说明 {#id2}

[`mc idp ldap accesskey`](#command-mc.idp.ldap.accesskey) 命令可用于列出、删除或显示 LDAP 访问密钥对的信息。

[`mc idp ldap accesskey`](#command-mc.idp.ldap.accesskey) 命令仅支持 MinIO 部署。

此命令适用于 AD/LDAP 用户在通过 MinIO 完成身份验证后创建的 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)。

使用 [`mc idp ldap accesskey create`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create) 命令创建 AD/LDAP 服务账户。

MinIO 支持使用 [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) 通过 [Security Token Service](/docs/developers/security-token-service/#minio-security-token-service) 生成临时访问密钥。

[`mc idp ldap accesskey`](#command-mc.idp.ldap.accesskey) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create"><code>mc idp ldap accesskey create</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create"><code>mc idp ldap accesskey create</code></a> 允许添加 LDAP 访问密钥对。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-disable/#command-mc.idp.ldap.accesskey.disable"><code>mc idp ldap accesskey disable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-disable/#command-mc.idp.ldap.accesskey.disable"><code>mc idp ldap accesskey disable</code></a> 会在 MinIO 部署上禁用指定的 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys">access key</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-edit/#command-mc.idp.ldap.accesskey.edit"><code>mc idp ldap accesskey edit</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-edit/#command-mc.idp.ldap.accesskey.edit"><code>mc idp ldap accesskey edit</code></a> 在本地服务器上修改指定的 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys">access key</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-enable/#command-mc.idp.ldap.accesskey.enable"><code>mc idp ldap accesskey enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-enable/#command-mc.idp.ldap.accesskey.enable"><code>mc idp ldap accesskey enable</code></a> 在本地服务器上启用指定的 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys">access key</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-info/#command-mc.idp.ldap.accesskey.info"><code>mc idp ldap accesskey info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-info/#command-mc.idp.ldap.accesskey.info"><code>mc idp ldap accesskey info</code></a> 输出指定访问密钥（一个或多个）的信息。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-ls/#command-mc.idp.ldap.accesskey.ls"><code>mc idp ldap accesskey ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-ls/#command-mc.idp.ldap.accesskey.ls"><code>mc idp ldap accesskey ls</code></a> 用于显示 LDAP 访问密钥对列表。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-rm/#command-mc.idp.ldap.accesskey.rm"><code>mc idp ldap accesskey rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-rm/#command-mc.idp.ldap.accesskey.rm"><code>mc idp ldap accesskey rm</code></a> 从本地服务器中删除指定的访问密钥。</p></td>
    </tr>
  </tbody>
</table>