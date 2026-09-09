---
title: "mc batch"

weight: 40
icon: fa-solid fa-layer-group
---

<a id="mc-batch"></a>

<a id="command-mc.batch"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-03-20T17-17-53Z
>
> 新增了通过 [`mc batch cancel`](/docs/reference/minio-mc/mc-batch-cancel/#command-mc.batch.cancel) 命令取消作业的能力。

## 描述 {#id2}

[`mc batch`](#command-mc.batch) 命令允许您在 MinIO 部署上运行一个或多个作业任务。

## 子命令 {#id3}

[`mc batch`](#command-mc.batch) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-cancel/#command-mc.batch.cancel"><code>cancel</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-cancel/#command-mc.batch.cancel"><code>mc batch cancel</code></a> 可停止正在进行的批处理作业。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-describe/#command-mc.batch.describe"><code>describe</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-describe/#command-mc.batch.describe"><code>mc batch describe</code></a> 命令会输出指定作业 ID 的作业定义。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate"><code>generate</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate"><code>mc batch generate</code></a> 命令会为指定作业类型创建一个基础的 YAML 格式模板文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list"><code>list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list"><code>mc batch list</code></a> 命令会输出部署中当前正在进行的批处理作业列表。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-start/#command-mc.batch.start"><code>start</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-start/#command-mc.batch.start"><code>mc batch start</code></a> 命令根据批处理作业 YAML 文件启动一个批处理作业。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-status/#command-mc.batch.status"><code>status</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch-status/#command-mc.batch.status"><code>mc batch status</code></a> 命令会输出 MinIO 服务器上作业事件的汇总信息。</p><aside class="alert alert-info"><p><strong>变更: mc</strong></p><p>RELEASE.2024-07-03T20-17-25Z</p><p>Batch status 会显示活动且正在进行的作业，或前 3（三）天内已完成的任意批处理作业的汇总信息。</p></aside></td>
    </tr>
  </tbody>
</table>