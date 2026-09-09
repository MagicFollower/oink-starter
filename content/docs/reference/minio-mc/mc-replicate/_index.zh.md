---
title: "mc replicate"

weight: 320
icon: fa-solid fa-copy
---

<a id="mc-replicate"></a>

<a id="command-mc.replicate"></a>

## 说明 {#id2}

[`mc replicate`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 命令用于为 MinIO 部署配置和管理 [服务端存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)，包括 [双活复制配置](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway) 和 [重新同步](/docs/administration/bucket-replication/#minio-replication-behavior-resync)。

> [!NOTE]
> **说明**
>
> 对于多站点复制，请参见 [`mc admin replicate`](/docs/reference/minio-mc-admin/mc-admin-replicate/#command-mc.admin.replicate)。

## 子命令 {#id3}

[`mc replicate`](#command-mc.replicate) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add"><code>mc replicate add</code></a> 命令会为 MinIO 部署中的存储桶创建一条新的 <a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">服务端复制</a> 规则。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-backlog/#command-mc.replicate.backlog"><code>backlog</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-backlog/#command-mc.replicate.backlog"><code>mc replicate backlog</code></a> 显示尚未复制的新建或已删除对象列表。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-export/#command-mc.replicate.export"><code>export</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-export/#command-mc.replicate.export"><code>mc replicate export</code></a> 命令将 MinIO 存储桶的 JSON 格式
<a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">复制规则</a> 导出到 <code>STDOUT</code>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-import/#command-mc.replicate.import"><code>import</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-import/#command-mc.replicate.import"><code>mc replicate import</code></a> 命令从 <code>STDIN</code> 为 MinIO 存储桶导入 JSON 格式的
<a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">replication rules</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls"><code>mc replicate ls</code></a> 命令列出 MinIO 存储桶上的所有
<a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">复制规则</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-resync/#command-mc.replicate.resync"><code>resync</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-resync/#command-mc.replicate.resync"><code>mc replicate resync</code></a> 命令会将指定 MinIO 存储桶中的所有对象，
重新同步到远端 <a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">replication</a> 目标。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm"><code>mc replicate rm</code></a> 命令用于从 MinIO 存储桶中删除
<a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">replication rule</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-status/#command-mc.replicate.status"><code>status</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-status/#command-mc.replicate.status"><code>mc replicate status</code></a> 命令显示 MinIO 存储桶的 <a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">复制状态</a>。
该状态还会列出远程目标路径或位置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update"><code>update</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update"><code>mc replicate update</code></a> 命令用于修改现有的
<a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">存储桶复制规则</a>。</p></td>
    </tr>
  </tbody>
</table>