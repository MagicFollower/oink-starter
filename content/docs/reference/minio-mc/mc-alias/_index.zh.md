---
title: "mc alias"

weight: 20
icon: fa-solid fa-link
---

<a id="mc-alias"></a>

<a id="command-mc.alias"></a>

## 说明 {#id2}

[`mc alias`](#command-mc.alias) 命令提供了一个便捷接口，用于管理 [`mc`](/docs/reference/minio-mc/#command-mc) 可连接并执行操作的 S3 兼容主机列表。

> [!WARNING]
> **重要**
>
> 对 S3 兼容服务执行操作的 [`mc`](/docs/reference/minio-mc/#command-mc) 命令 *必须* 为该服务指定一个别名。

## 子命令 {#id3}

[`mc alias`](#command-mc.alias) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-list/#command-mc.alias.list"><code>list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-list/#command-mc.alias.list"><code>mc alias list</code></a> 命令列出本地 <strong>mc</strong> 配置中的所有别名。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-remove/#command-mc.alias.remove"><code>remove</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-remove/#command-mc.alias.remove"><code>mc alias remove</code></a> 从本地 <strong>mc</strong> 配置中移除一个已存在的别名。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set"><code>mc alias set</code></a> 命令用于在本地 <strong>mc</strong> 配置中添加或更新别名。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-import/#command-mc.alias.import"><code>import</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-import/#command-mc.alias.import"><code>mc alias import</code></a> 命令从 JSON 文档中导入别名配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-export/#command-mc.alias.export"><code>export</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias-export/#command-mc.alias.export"><code>mc alias export</code></a> 命令从现有的 <a href="/docs/reference/minio-mc/#mc-configuration">configuration</a> 中导出别名配置。</p></td>
    </tr>
  </tbody>
</table>