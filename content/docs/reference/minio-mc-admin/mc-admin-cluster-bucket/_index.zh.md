---
title: "mc admin cluster bucket"

weight: 20
icon: fa-solid fa-boxes-stacked
---

<a id="mc-admin-cluster-bucket"></a>
<a id="minio-mc-admin-cluster-bucket"></a>

<a id="command-mc.admin.cluster.bucket"></a>

## 说明 {#id2}

> [!NOTE]
> **新增: RELEASE.2022-06-17T02-52-50Z**

[`mc admin cluster bucket`](#command-mc.admin.cluster.bucket) 命令及其子命令提供了用于手动导入和导出 MinIO 存储桶元数据的工具。

这些元数据包含与 [生命周期管理规则](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 等功能相关的配置。 你可以将这些元数据作为存储桶配置的快照，用于后续恢复，例如作为 <abbr title="Business Continuity / Disaster Recovery">BC/DR</abbr> 或备份/恢复操作的一部分。

你可以将此命令用于单个存储桶，*或* 用于 MinIO 部署中的所有存储桶。 如需将部署中的所有存储桶自动同步到远端站点，请使用 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview)。

[`mc admin cluster bucket`](#command-mc.admin.cluster.bucket) 命令包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-import/#command-mc.admin.cluster.bucket.import"><code>import</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-import/#command-mc.admin.cluster.bucket.import"><code>mc admin cluster bucket import</code></a> 命令用于导入由 <a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export"><code>mc admin cluster bucket export</code></a> 命令生成的存储桶元数据。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export"><code>export</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export"><code>mc admin cluster bucket export</code></a> 命令会导出存储桶元数据，以供 <a href="/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-import/#command-mc.admin.cluster.bucket.import"><code>mc admin cluster bucket import</code></a> 命令使用。</p></td>
    </tr>
  </tbody>
</table>