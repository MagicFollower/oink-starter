---
title: "组管理"

weight: 20
---

<a id="minio-groups"></a>
<a id="id1"></a>

## 概述 {#id3}

*组* 是 [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 的集合。每个组 都可以分配一个或多个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)， 这些策略会显式列出允许或拒绝组成员访问的操作和资源。

例如，考虑以下几个组。每个组都分配了一个 [内置策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-built-in) 或受支持的 [策略操作](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-actions)。每个组还分配了一个或 多个用户。每个用户的完整权限集合由其 显式分配的权限 *以及* 从其所属各组继承的权限共同组成。 对于用户被分配或继承的策略中未显式允许的任何资源或操作，MinIO 默认都会 *拒绝* 访问。

<table>
  <thead>
    <tr>
      <th><p>组</p></th>
      <th><p>策略</p></th>
      <th><p>成员</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>Operations</code></p></td>
      <td><code>finance</code> 存储桶上的 <a href="/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readwrite"><code>readwrite</code></a><br /><code>audit</code> 存储桶上的 <a href="/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readonly"><code>readonly</code></a><br /></td>
      <td><p><code>john.doe</code>, <code>jane.doe</code></p></td>
    </tr>
    <tr>
      <td><p><code>Auditing</code></p></td>
      <td><code>audit</code> 存储桶上的 <a href="/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readonly"><code>readonly</code></a><br /></td>
      <td><p><code>jen.doe</code>, <code>joe.doe</code></p></td>
    </tr>
    <tr>
      <td><p><code>Admin</code></p></td>
      <td><p><a href="/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin"><code>admin:*</code></a></p></td>
      <td><p><code>greg.doe</code>, <code>jen.doe</code></p></td>
    </tr>
  </tbody>
</table>

组为具有相同访问模式和工作负载的用户之间管理共享权限提供了一种更简便的方法。 客户端 *不能* 使用组作为身份向 MinIO 部署进行认证。

[`mc admin group`](/docs/reference/minio-mc-admin/mc-admin-group/#command-mc.admin.group) 命令支持在 MinIO 部署上创建和管理组。 有关用法示例，请参阅该命令的参考文档。