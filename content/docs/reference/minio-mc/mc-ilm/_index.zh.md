---
title: "mc ilm"

weight: 190
icon: fa-solid fa-clock-rotate-left
---

<a id="mc-ilm"></a>

<a id="command-mc.ilm"></a>

## 描述 {#id2}

[`mc ilm`](#command-mc.ilm) 命令用于管理 MinIO 部署中的 [对象生命周期管理规则](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 和分层。

使用这些命令可以：

- 创建层
- 创建 [分层](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 规则
- 管理存储桶中对象的 [过期](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 规则

## 子命令 {#id3}

[`mc ilm`](#command-mc.ilm) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-restore/#command-mc.ilm.restore"><code>restore</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-restore/#command-mc.ilm.restore"><code>mc ilm restore</code></a> 命令会为归档在远程层上的对象创建一个临时副本。
默认情况下，该副本会在 1 天后自动过期。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule/#command-mc.ilm.rule"><code>rule</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule/#command-mc.ilm.rule"><code>mc ilm rule</code></a> 命令及其子命令用于配置 MinIO 生命周期管理中对象在各存储层之间转换所使用的规则。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier"><code>tier</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier"><code>mc ilm tier</code></a> 命令及其子命令用于为 MinIO 的 <a href="/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration">生命周期管理：对象过渡（“分层”）</a> 配置受支持的远程 S3 兼容服务。</p></td>
    </tr>
  </tbody>
</table>