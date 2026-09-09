---
title: "mc quota"

weight: 70
icon: fa-solid fa-box-archive
---

<a id="mc-quota"></a>

<a id="command-mc.quota"></a>

> [!NOTE]
> **变更: RELEASE.2024-07-31T15-58-33Z**
>
> `mc quota` 及其子命令已弃用。

## 说明 {#id2}

[`mc quota`](#command-mc.quota) 命令用于为存储桶配置、显示或移除配额限制。

对于已配置配额的存储桶，当其达到指定限制时（由 MinIO object scanner 判定），MinIO 会拒绝该存储桶后续的 `PUT` 请求。

每当 MinIO [object scanner](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 扫描存储桶中待处理的 [object lifecycle transitions](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 时，也会检查该存储桶是否超出已配置的配额。

> [!NOTE]
> **配额执行并非即时生效**
>
> 存储桶配额的设计目的不是对存储桶大小施加严格的硬限制。 如果存储桶在两次扫描之间超出配额，MinIO 仍会继续接受该存储桶的 `PUT` 请求，直到下一次扫描识别出配额违规 _之后_ 才会拒绝。

## 子命令 {#id3}

[`mc quota`](#command-mc.quota) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/deprecated/mc-quota-clear/#command-mc.quota.clear"><code>clear</code></a></p></td>
      <td><p><a href="/docs/reference/deprecated/mc-quota-clear/#command-mc.quota.clear"><code>mc quota clear</code></a> 命令会移除存储桶上已配置的存储配额。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/deprecated/mc-quota-info/#command-mc.quota.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/deprecated/mc-quota-info/#command-mc.quota.info"><code>mc quota info</code></a> 命令显示存储桶当前配置的配额。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/deprecated/mc-quota-set/#command-mc.quota.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/deprecated/mc-quota-set/#command-mc.quota.set"><code>mc quota set</code></a> 为存储桶分配硬配额限制，超过该限制后 MinIO 不再允许写入。</p></td>
    </tr>
  </tbody>
</table>