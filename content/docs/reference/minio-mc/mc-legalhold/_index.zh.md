---
title: "mc legalhold"

weight: 200
icon: fa-solid fa-gavel
---

<a id="mc-legalhold"></a>

<a id="command-mc.legalhold"></a>

## 描述 {#id1}

[`mc legalhold`](#command-mc.legalhold) 命令用于为一个或多个对象设置、移除或获取 [object legal hold (WORM)](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 配置。

## 子命令 {#id2}

[`mc legalhold`](#command-mc.legalhold) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-clear/#command-mc.legalhold.clear"><code>clear</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-clear/#command-mc.legalhold.clear"><code>mc legalhold clear</code></a> 命令会移除一个或多个对象当前的
<a href="/docs/administration/object-management/object-retention/#minio-object-locking-legalhold">legal hold</a> 设置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-info/#command-mc.legalhold.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-info/#command-mc.legalhold.info"><code>mc legalhold info</code></a> 命令返回一个或多个对象的当前 <a href="/docs/administration/object-management/object-retention/#minio-object-locking-legalhold">legal hold</a> 设置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-set/#command-mc.legalhold.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold-set/#command-mc.legalhold.set"><code>mc legalhold set</code></a> 命令可在单个或多个对象上启用
<a href="/docs/administration/object-management/object-retention/#minio-object-locking-legalhold">legal hold</a> 的一次写入多次读取（WORM）对象锁定。</p></td>
    </tr>
  </tbody>
</table>