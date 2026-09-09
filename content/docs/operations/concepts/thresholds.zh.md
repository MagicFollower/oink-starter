---
title: "阈值与限制"

weight: 60
math: true
---

<a id="minio-server-limits"></a>
<a id="id1"></a>

本页列出了适用于 MinIO 的阈值与限制。

有关相关建议和要求，请参阅 [hardware](/docs/operations/checklists/hardware/#minio-hardware-checklist) 和 [software](/docs/operations/checklists/software/#minio-software-checklists)。

## S3 API 限制 {#s3-api}

<table>
  <thead>
    <tr>
      <th><p>项目</p></th>
      <th><p>规格</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>最大对象大小</p></td>
      <td><p>50 TiB</p></td>
    </tr>
    <tr>
      <td><p>最小对象大小</p></td>
      <td><p>0 B</p></td>
    </tr>
    <tr>
      <td><p>单次 PUT 操作的最大对象大小</p></td>
      <td>非 multipart upload 为 5 TiB<br />multipart upload 为 50 TiB<br /></td>
    </tr>
    <tr>
      <td><p>每次上传的最大分片数</p></td>
      <td><p>10,000</p></td>
    </tr>
    <tr>
      <td><p>分片大小范围</p></td>
      <td><p>5 MiB 到 5 GiB。最后一个分片可为 0 B 到 5 GiB</p></td>
    </tr>
    <tr>
      <td><p>每次 list parts 请求返回的最大分片数</p></td>
      <td><p>10,000</p></td>
    </tr>
    <tr>
      <td><p>每次 list objects 请求返回的最大对象数</p></td>
      <td><p>1,000</p></td>
    </tr>
    <tr>
      <td><p>每次 list multipart uploads 请求返回的最大 multipart upload 数</p></td>
      <td><p>1,000</p></td>
    </tr>
    <tr>
      <td><p>存储桶名称最大长度</p></td>
      <td><p>63</p></td>
    </tr>
    <tr>
      <td><p>对象名称最大长度</p></td>
      <td><p>1024</p></td>
    </tr>
    <tr>
      <td><p>对象名称中每个以 <code>/</code> 分隔段的最大长度</p></td>
      <td><p>255</p></td>
    </tr>
    <tr>
      <td><p>单个唯一对象允许的最大版本数</p></td>
      <td><p>10000（可配置）</p></td>
    </tr>
  </tbody>
</table>

## 纠删码限制 {#id3}

| 项目 | 规格 |
| --- | --- |
| 每个集群的最大服务器数 | 无限制 |
| 最小服务器数 | 1 |
| 当服务器数为 1 时，每台服务器的最少驱动器数 | 1（适用于 <abbr title="单机单盘">SNSD</abbr> 部署，此类部署不提供额外可靠性或可用性） |
| 当服务器数为 2 或更多时，每台服务器的最少驱动器数 | 1 |
| 每台服务器的最大驱动器数 | 无限制 |
| 读仲裁 | \(N/2\) |
| 写仲裁 | \((N/2)+1\) |

## 对象名称限制 {#id4}

### 文件系统和操作系统限制 {#id5}

MinIO 中的对象名称主要受本地操作系统和文件系统限制。 Windows 和某些其他操作系统会限制包含特定特殊字符的文件系统名称，例如 `^`、`*`、`|`、`\`、`/`、`&`、`"` 或 `;`。

此列表并不完整，也不一定适用于你的操作系统和文件系统组合。

在类 Unix 操作系统上，路径名为 `.`、`..` 或 `/` 的对象会返回 `file access denied` 错误。

请查阅你的操作系统供应商或文件系统文档，以获得适用于当前环境的完整列表。

MinIO 建议生产工作负载使用基于 XFS 文件系统的 Linux 操作系统。

### 冲突对象 {#id6}

应用必须为所有对象分配不冲突的唯一键。 这包括避免创建与父对象或同级对象名称发生冲突的对象。 当名称发生冲突时，MinIO 在该位置的 LIST 操作会返回空结果集。

例如，以下操作会创建命名空间冲突：

```text
PUT data/invoices/2024/january/vendors.csv
PUT data/invoices/2024/january <- collides with existing object prefix
```

```text
PUT data/invoices/2024/january
PUT data/invoices/2024/january/vendors.csv <- collides with existing object
```

虽然你仍然可以对这些对象执行 GET 或 HEAD 操作，但名称冲突会导致在 `/invoices/2024/january` 路径上的 LIST 操作返回空结果集。