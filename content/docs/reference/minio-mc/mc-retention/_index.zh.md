---
title: "mc retention"

weight: 330
icon: fa-solid fa-hourglass-half
---

<a id="mc-retention"></a>

<a id="command-mc.retention"></a>

## 描述 {#id2}

[`mc retention`](#command-mc.retention) 命令用于为存储桶中的一个或多个对象配置 [Write-Once Read-Many (WORM) locking](/docs/administration/object-management/object-retention/#minio-object-locking) 设置。 你还可以为存储桶设置默认的对象锁定设置；未显式配置对象锁定设置的所有对象都会继承该存储桶默认值。

## 子命令 {#id3}

[`mc retention`](#command-mc.retention) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-clear/#command-mc.retention.clear"><code>clear</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-clear/#command-mc.retention.clear"><code>mc retention clear</code></a> 命令可移除存储桶中一个或多个对象的
<a href="/docs/administration/object-management/object-retention/#minio-object-locking">Write-Once Read-Many (WORM) locking</a> 设置。
你还可以移除存储桶的默认对象锁定设置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-info/#command-mc.retention.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-info/#command-mc.retention.info"><code>mc retention info</code></a> 命令用于为对象或存储桶中的对象配置 <a href="/docs/administration/object-management/object-retention/#minio-object-locking">Write-Once Read-Many (WORM)
locking</a> 设置。
你还可以为存储桶设置默认对象锁定设置，未显式配置对象锁定的对象会继承该存储桶默认值。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-set/#command-mc.retention.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-retention-set/#command-mc.retention.set"><code>mc retention set</code></a> 命令用于为存储桶中的一个或多个对象配置
<a href="/docs/administration/object-management/object-retention/#minio-object-locking">Write-Once Read-Many (WORM) locking</a> 设置。
你还可以为存储桶设置默认对象锁定设置，使未显式配置对象锁定的所有对象继承该存储桶默认值。</p></td>
    </tr>
  </tbody>
</table>