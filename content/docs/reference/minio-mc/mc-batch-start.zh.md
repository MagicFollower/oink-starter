---
title: "mc batch start"

weight: 50
---

<a id="mc-batch-start"></a>
<a id="minio-mc-batch-start"></a>

<a id="command-mc.batch.start"></a>

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2022-10-09T21-10-59Z or later

## 语法 {#id2}

[`mc batch start`](#command-mc.batch.start) 命令根据批处理作业 YAML 文件启动一个批处理作业。

批处理作业会运行一次直到完成（或达到文件中指定的最大重试次数）。 若要在完成后再次运行该批处理作业，必须重新启动它。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` 别名的 `mybucket` 存储桶上，为 replicate 作业创建一个基础 YAML 文件。

```shell
mc batch start myminio jobfile.yaml
```

上述命令的输出类似如下：

```shell
Successfully start 'replicate' job `B34HHqnNMcg1taynaPfxu` on '2022-10-24 17:19:06.296974771 -0700 PDT'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] batch start    \
                       ALIAS   \
                       JOBFILE
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.batch.start.ALIAS}

*mc-cmd*

*Required*

用于启动批处理作业的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc batch start myminio replicate.yaml
```

##### `JOBFILE` {#mc.batch.start.JOBFILE}

*mc-cmd*

*Required*

YAML 定义的批处理作业。 作业可按需包含任意数量的任务；没有预定义的限制。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 启动批处理作业 {#id6}

以下命令会在 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) `myminio` 对应的部署上，启动 `replication.yaml` 文件中定义的一批作业：

```shell
mc batch start myminio ./replication.yaml
```

- 将 `myminio` 替换为应运行该作业的 MinIO 部署 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `./replication.yaml` 替换为描述批处理作业的 YAML 格式文件。 使用相对于当前位置的文件路径。

上述命令的输出类似如下：

```shell
Successfully start 'replicate' job `E24HH4nNMcgY5taynaPfxu` on '2022-09-26 17:19:06.296974771 -0700 PDT'
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 权限 {#id7}

要启动作业，必须在该部署上具有 [`admin:StartBatchJob`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-StartBatchJob) 权限。