---
title: "mc batch list"

weight: 40
---

<a id="mc-batch-list"></a>
<a id="minio-mc-batch-list"></a>

<a id="command-mc.batch.list"></a>

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2022-10-09T21-10-59Z or later

## 语法 {#id2}

[`mc batch list`](#command-mc.batch.list) 命令会输出部署中当前正在进行的批处理作业列表。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会输出 `myminio` alias 上当前正在进行的所有作业列表。

```shell
mc batch list myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] batch list TARGET           \
                            --type "string"
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.batch.list.TARGET}

*mc-cmd*

*Required*

要列出进行中作业的目标部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--type` {#mc.batch.list.-type}

*mc-cmd*

*Optional*

仅列出指定类型的批处理作业。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出所有 `replicate` 类型的批处理作业 {#replicate}

以下命令列出 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) `myminio` 所对应部署上的 `replicate` 类型作业：

```shell
mc batch list myminio --type "replicate"
```

- 将 `myminio` 替换为应运行该作业的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `replicate` 替换为要输出的作业类型。

  当前，[`mc batch`](/docs/reference/minio-mc/mc-batch/#command-mc.batch) 仅支持 `replicate` 作业类型。

上述命令的输出类似如下：

```shell
ID                      TYPE            USER            STARTED
E24HH4nNMcgY5taynaPfxu  replicate       minioadmin      1 minute ago
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 权限 {#id6}

你必须具有 [`admin:ListBatchJobs`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListBatchJobs) 权限，才能列出该部署上的作业。