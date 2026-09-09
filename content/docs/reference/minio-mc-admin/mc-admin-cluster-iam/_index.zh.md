---
title: "mc admin cluster iam"

weight: 30
icon: fa-solid fa-users-gear
---

<a id="mc-admin-cluster-iam"></a>
<a id="minio-mc-admin-cluster-iam"></a>

<a id="command-mc.admin.cluster.iam"></a>

## 描述 {#id2}

> [!NOTE]
> **新增: RELEASE.2022-06-26T18-51-48Z**

[`mc admin cluster iam`](#command-mc.admin.cluster.iam) 命令及其子命令提供了用于手动导入和导出 MinIO [身份与访问管理（IAM）](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 元数据的工具。

如需将部署中的所有 IAM 配置自动同步到远程站点，请使用 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview)。

[`mc admin cluster iam`](#command-mc.admin.cluster.iam) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-import/#command-mc.admin.cluster.iam.import"><code>import</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-import/#command-mc.admin.cluster.iam.import"><code>mc admin cluster iam import</code></a> 命令导入由 <a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export"><code>mc admin cluster iam export</code></a> 命令创建的 <a href="/docs/administration/identity-access-management/#minio-authentication-and-identity-management">IAM</a> 元数据。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export"><code>export</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export"><code>mc admin cluster iam export</code></a> 命令导出 <a href="/docs/administration/identity-access-management/#minio-authentication-and-identity-management">IAM</a> 元数据，以供 <a href="/docs/reference/minio-mc-admin/mc-admin-cluster-iam-import/#command-mc.admin.cluster.iam.import"><code>mc admin cluster iam import</code></a> 命令使用。</p></td>
    </tr>
  </tbody>
</table>