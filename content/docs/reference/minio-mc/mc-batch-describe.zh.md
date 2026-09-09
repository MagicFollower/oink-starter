---
title: "mc batch describe"

weight: 20
---

<a id="mc-batch-describe"></a>
<a id="minio-mc-batch-describe"></a>

<a id="command-mc.batch.describe"></a>

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2022-10-09T21-10-59Z or later

## 语法 {#id1}

[`mc batch describe`](#command-mc.batch.describe) 命令会输出指定作业 ID 的作业定义。

必须指定作业 ID。 要查找作业 ID，请使用 [`mc batch list`](/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会输出标识为 `KwSysDpxcBU9FNhGkn2dCf` 的作业定义。

```shell
mc batch describe myminio KwSysDpxcBU9FNhGkn2dCf
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
此命令的语法如下：

```shell
mc [GLOBALFLAGS] batch describe TARGET           \
                                JOBID
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `TARGET` {#mc.batch.describe.TARGET}

*mc-cmd*

*Required*

用于查找作业 ID 的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `JOBID` {#mc.batch.describe.JOBID}

*mc-cmd*

*Required*

要描述的作业的唯一标识符。 要查找作业 ID，请使用 [`mc batch list`](/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list)。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 显示进行中批处理作业的定义 {#id5}

以下命令会输出 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) `myminio` 上特定作业的完整作业定义：

```shell
mc batch describe myminio KwSysDpxcBU9FNhGkn2dCf
```

- 将 `myminio` 替换为应运行该作业的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `KwSysDpxcBU9FNhGkn2dCf` 替换为要定义的作业 ID。

上述命令的输出类似如下：

```shell
mc batch describe myminio KwSysDpxcBU9FNhGkn2dCf
replicate:
  apiVersion: v1
...
```

注意，此示例已截断。 输出结果是指定作业的完整作业定义。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 权限 {#id6}

你必须具有 `admin:DescribeBatchJobs` 权限，才能描述该部署上的作业。