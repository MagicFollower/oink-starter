---
title: "mc admin policy"

weight: 110
icon: fa-solid fa-file-shield
---

<a id="mc-admin-policy"></a>

<a id="command-mc.admin.policy"></a>

> [!NOTE]
> **变更: mc**
>
> RELEASE.2023-03-20T17-17-53Z
>
> 以下命令已弃用：
>
> - `mc admin policy add` 请改用 [`mc admin policy create`](/docs/reference/minio-mc-admin/mc-admin-policy-create/#command-mc.admin.policy.create)
> - `mc admin policy set` 请改用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach)
> - `mc admin policy unset` 请改用 [`mc admin policy detach`](/docs/reference/minio-mc-admin/mc-admin-policy-detach/#command-mc.admin.policy.detach)
> - `mc admin policy update` 请改用 [`attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 或 [`detach`](/docs/reference/minio-mc-admin/mc-admin-policy-detach/#command-mc.admin.policy.detach)
>
> 新增以下命令：
>
> - [`mc admin policy entities`](/docs/reference/minio-mc-admin/mc-admin-policy-entities/#command-mc.admin.policy.entities)

## 说明 {#id2}

[`mc admin policy`](#command-mc.admin.policy) 命令用于管理可与 [MinIO 基于策略的访问控制](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) (PBAC) 配合使用的策略。 MinIO PBAC 使用与 IAM 兼容的策略 JSON 文档来定义访问 MinIO 服务器资源的规则。

有关 MinIO PBAC 的完整文档（包括策略文档 JSON 结构与语法），请参阅 [访问管理](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。要管理使用 LDAP 认证的部署中的策略，请参阅 [`mc idp ldap policy`](/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy)。

## 子命令 {#id3}

[`mc admin policy`](#command-mc.admin.policy) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach"><code>attach</code></a></p></td>
      <td><p>将一个或多个 IAM 策略附加到 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-users">MinIO 管理的用户或组</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-create/#command-mc.admin.policy.create"><code>create</code></a></p></td>
      <td><p>在目标 MinIO 部署上创建一个新策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-detach/#command-mc.admin.policy.detach"><code>detach</code></a></p></td>
      <td><p>从 <a href="/docs/administration/identity-access-management/minio-user-management/#minio-users">MinIO 管理的用户或组</a> 中移除一个或多个 IAM 策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-entities/#command-mc.admin.policy.entities"><code>entities</code></a></p></td>
      <td><p>列出目标 MinIO 部署中与策略、用户或组关联的实体。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-info/#command-mc.admin.policy.info"><code>info</code></a></p></td>
      <td><p>如果目标 MinIO 部署上存在指定策略，则以 JSON 格式返回该策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-list/#command-mc.admin.policy.ls"><code>ls</code></a></p></td>
      <td><p>列出目标 MinIO 部署上的所有策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-policy-remove/#command-mc.admin.policy.rm"><code>rm</code></a></p></td>
      <td><p>从目标 MinIO 部署中移除 IAM 策略。</p></td>
    </tr>
  </tbody>
</table>