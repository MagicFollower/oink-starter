---
title: "mc encrypt"

weight: 90
icon: fa-solid fa-lock
---

<a id="mc-encrypt"></a>

<a id="command-mc.encrypt"></a>

## 描述 {#id2}

[`mc encrypt`](#command-mc.encrypt) 命令用于设置、更新或禁用存储桶默认的服务端加密（SSE）模式。 MinIO 会使用指定的 SSE 模式自动加密对象。

## 子命令 {#id3}

[`mc encrypt`](#command-mc.encrypt) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-clear/#command-mc.encrypt.clear"><code>clear</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-clear/#command-mc.encrypt.clear"><code>mc encrypt clear</code></a> 命令用于移除存储桶当前的默认加密设置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-info/#command-mc.encrypt.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-info/#command-mc.encrypt.info"><code>mc encrypt info</code></a> 命令返回存储桶当前的默认加密设置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set"><code>mc encrypt set</code></a> 加密命令用于设置或更新存储桶默认的
<a href="/docs/administration/server-side-encryption/#minio-sse">服务端加密（SSE）模式</a>。MinIO 会使用指定的 SSE 模式
自动加密写入该存储桶的对象。</p></td>
    </tr>
  </tbody>
</table>