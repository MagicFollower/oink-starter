---
title: "批处理框架"

weight: 170
icon: fa-solid fa-layer-group
---

<a id="minio-batch-framework"></a>
<a id="id1"></a>

## 概述 {#id3}

MinIO 批处理框架允许使用 YAML 格式的作业定义文件（“batch file”）来创建、管理、监控和执行作业。 批处理作业直接在 MinIO 部署上运行，从而利用服务端处理能力，而不受运行 [MinIO Client](/docs/reference/minio-mc/#minio-client) 的本地机器限制。

一个批处理文件定义一个作业任务。

启动后，MinIO 会开始处理该作业。 完成所需时间取决于部署可用的资源。

如果作业的任何部分失败，MinIO 会按照作业定义中指定的次数上限重试该作业。

MinIO 批处理框架支持以下作业类型：

| 作业类型 | 说明 |
| --- | --- |
| [replicate](/docs/administration/batch-framework-job-replicate/#minio-batch-framework-replicate-job) | 执行一次性复制流程，将数据从一个 MinIO 位置复制到另一个 MinIO 位置。 |
| [keyrotate](/docs/administration/batch-framework-job-keyrotate/#minio-batch-framework-keyrotate-job) | 执行一次性流程，轮换对象上的 [sse-s3 or sse-kms](/docs/operations/server-side-encryption/#minio-sse-data-encryption) 加密密钥。 |
| [expire](/docs/administration/batch-framework-job-expire/#minio-batch-framework-expire-job) | 对存储桶中的对象执行一次性立即过期操作。 |

## MinIO 批处理 CLI {#minio-cli}

- 安装 [MinIO Client](/docs/reference/minio-mc/#minio-client)
- 为 MinIO 部署定义一个 [`alias`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set)

[`mc batch`](/docs/reference/minio-mc/mc-batch/#command-mc.batch) 命令包括：

<table>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate"><code>mc batch generate</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate"><code>mc batch generate</code></a> 命令会为指定作业类型创建一个基础的 YAML 格式模板文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-start/#command-mc.batch.start"><code>mc batch start</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-start/#command-mc.batch.start"><code>mc batch start</code></a> 命令根据批处理作业 YAML 文件启动一个批处理作业。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list"><code>mc batch list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list"><code>mc batch list</code></a> 命令会输出部署中当前正在进行的批处理作业列表。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-status/#command-mc.batch.status"><code>mc batch status</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-status/#command-mc.batch.status"><code>mc batch status</code></a> 命令会输出 MinIO 服务器上作业事件的汇总信息。</p><aside class="alert alert-info"><p><strong>变更: mc</strong></p><p>RELEASE.2024-07-03T20-17-25Z</p><p>Batch status 会显示活动且正在进行的作业，或前 3（三）天内已完成的任意批处理作业的汇总信息。</p></aside></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-describe/#command-mc.batch.describe"><code>mc batch describe</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-describe/#command-mc.batch.describe"><code>mc batch describe</code></a> 命令会输出指定作业 ID 的作业定义。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-cancel/#command-mc.batch.cancel"><code>mc batch cancel</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-cancel/#command-mc.batch.cancel"><code>mc batch cancel</code></a> 可停止正在进行的批处理作业。</p></td>
    </tr>
  </tbody>
</table>

<a id="minio-batch-framework-access"></a>

## `mc batch` 的访问权限 {#mc-batch}

每个批处理作业都使用批处理定义中指定的凭证执行。 批处理作业能否成功，取决于这些凭证是否具有执行所有请求操作所需的适当 [权限](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

执行批处理作业的用户必须具有以下权限。 也可以通过阻止或限制对这些操作的访问，来限制用户使用这些功能：

**`admin:ListBatchJobs`**

> 授予用户查看当前正在处理的批处理作业的能力。

**`admin:DescribeBatchJobs`**

> 授予用户查看当前正在处理的批处理作业定义详情的能力。

**`admin:StartBatchJob`**

> 授予用户启动批处理作业的能力。 该作业还可能受到其用于访问源部署或目标部署的凭证进一步限制。

**`admin:CancelBatchJob`**

> 允许用户停止当前正在进行的批处理作业。

可以将这些操作中的任意一个单独分配给用户，也可以任意组合分配。

内置的 `ConsoleAdmin` 策略包含执行所有这些类型批处理作业操作所需的充分访问权限。

<a id="minio-batch-local"></a>

## `Local` 部署 {#local}

可通过向 [`mc batch`](/docs/reference/minio-mc/mc-batch/#command-mc.batch) 命令传递一个 `alias`，对特定部署运行批处理作业。 命令中指定的部署会在该批处理作业的上下文中成为 `local` 部署。