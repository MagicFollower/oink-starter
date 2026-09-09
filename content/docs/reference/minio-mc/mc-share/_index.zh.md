---
title: "mc share"

weight: 350
icon: fa-solid fa-share-nodes
---

<a id="mc-share"></a>

<a id="command-mc.share"></a>

## 说明 {#id2}

使用 [`mc share`](#command-mc.share) 命令管理预签名 URL，以便下载和上传 MinIO 存储桶中的对象。

## 子命令 {#id3}

[`mc share`](#command-mc.share) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-share-download/#command-mc.share.download"><code>download</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-share-download/#command-mc.share.download"><code>mc share download</code></a> 命令会生成一个临时的预签名 URL，并集成访问凭证，
用于从 MinIO 存储桶下载对象。该临时 URL 会在可配置的时间限制后过期。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-share-list/#command-mc.share.list"><code>list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-share-list/#command-mc.share.ls"><code>mc share ls</code></a> 命令会显示由 <a href="/docs/reference/minio-mc/mc-share-upload/#command-mc.share.upload"><code>mc share upload</code></a> 或
<a href="/docs/reference/minio-mc/mc-share-download/#command-mc.share.download"><code>mc share download</code></a> 生成的所有未过期预签名 URL。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-share-upload/#command-mc.share.upload"><code>upload</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-share-upload/#command-mc.share.upload"><code>mc share upload</code></a> 命令会生成一个临时的预签名 URL，并集成用于将对象上传到 MinIO 存储桶的访问凭证。该临时 URL 会在可配置的时间限制后过期。</p></td>
    </tr>
  </tbody>
</table>