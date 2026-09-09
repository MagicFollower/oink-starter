---
title: "mc batch cancel"

weight: 10
---

<a id="mc-batch-cancel"></a>
<a id="minio-mc-batch-cancel"></a>

<a id="command-mc.batch.cancel"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-03-20T17-17-53Z

## 语法 {#id1}

[`mc batch cancel`](#command-mc.batch.cancel) 可停止正在进行的批处理作业。

您必须指定作业 ID。 要查找作业 ID，请使用 [`mc batch list`](/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会输出标识为 `KwSysDpxcBU9FNhGkn2dCf` 的作业定义。

```shell
mc batch cancel myminio KwSysDpxcBU9FNhGkn2dCf
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] batch cancel ALIAS JOBID
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.batch.cancel.ALIAS}

*mc-cmd*

*Required*

当前运行该作业的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `JOBID` {#mc.batch.cancel.JOBID}

*mc-cmd*

*Required*

要取消的批处理作业的唯一标识符。 要查找作业 ID，请使用 [`mc batch list`](/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list)。

### 全局参数 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 取消正在进行的批处理作业 {#id5}

以下命令会取消别名为 `myminio` 的部署上 ID 为 `KwSysDpxcBU9FNhGkn2dCf` 的作业：

```shell
mc batch cancel myminio KwSysDpxcBU9FNhGkn2dCf
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。