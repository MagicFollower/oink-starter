---
title: "mc replicate backlog"

weight: 20
---

<a id="mc-replicate-backlog"></a>
<a id="minio-mc-replicate-backlog"></a>
<a id="minio-mc-replicate-diff"></a>

<a id="command-mc.replicate.diff"></a>

<a id="command-mc.replicate.backlog"></a>

> [!NOTE]
> **变更: mc.RELEASE.2023-07-18T21-05-38Z**
>
> `mc replicate diff` 已重命名为 `mc replicate backlog`。 功能未发生变化。

## 描述 {#id2}

[`mc replicate backlog`](#command-mc.replicate.backlog) 显示尚未复制的新建或已删除对象列表。

你可以列出特定远程目标的对象复制状态。 为此，你必须具有该远程目标的 ARN。 你可以使用 [检索为存储桶配置的远程目标](/docs/reference/deprecated/mc-admin-bucket-remote/#minio-retrieve-remote-bucket-targets) 查找 ARN。

## 语法 {#id3}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 `myminio` 别名下 `notes` 存储桶中 `teamorange/projects` 前缀里尚未复制到特定远程目标存储桶的新建或已删除对象。 该远程目标的 ARN 为 `arn:minio:replication::3bb8c736-4014-42c5-b3cb-d64e3ebaa75e:notes`。

```shell
mc replicate backlog myminio/notes/teamorange/projects --arn arn:minio:replication::3bb8c736-4014-42c5-b3cb-d64e3ebaa75e:notes
```

如果存在尚未复制的新建或已删除对象，命令输出类似如下：

```shell
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:59 UTC]          478efe49-aa9d-46ab-8268-45b70cc4c341 PUT agenda.docx
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:15 UTC]          b283bf43-319f-455a-a779-3c2e669fad88 PUT budget-meeting.docx
```

在输出中，`PUT` 对应新建对象。 已删除对象或版本会显示为 `DEL`。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] replicate backlog   \
                 [--arn "string"]    \
                 TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id4}

##### `TARGET` {#mc.replicate.backlog.TARGET}

*mc-cmd*

*Required*

指向别名、前缀或对象的路径。

##### `arn` {#mc.replicate.backlog.arn}

*mc-cmd*

*Optional*

远程存储桶的 ARN，用于检查尚未复制的新建或已删除对象。

指定后，该命令返回尚未复制到远程目标的所有新建或已删除对象列表。 未指定时，该命令返回源部署上尚未复制到任何远程目标的新建或已删除对象列表。

### 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id6}

### 查看某个前缀下对象的未复制版本 {#id7}

显示某个前缀下未复制的 `PUT` 和 `DELETE` 操作：

```shell
mc replicate backlog myminio/mybucket/path/to/prefix
```

- 将 `myminio/mybucket` 替换为 [`ALIAS`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.ALIAS) 以及 需要创建复制配置的完整存储桶路径。
- 将 `path/to/prefix` 替换为请求要使用的前缀或对象。

如果存在未复制对象，输出会返回一个操作列表，列出在该前缀下创建或删除对象且尚未复制到远程目标的操作：

```shell
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:59 UTC]          478efe49-aa9d-46ab-8268-45b70cc4c341 PUT agenda.docx
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:15 UTC]          b283bf43-319f-455a-a779-3c2e669fad88 PUT budget-meeting.docx
```

### 查看特定远程目标上的未复制对象 {#id8}

以下 [`mc replicate backlog`](#command-mc.replicate.backlog) 命令显示特定远程目标在某个 alias/bucket/prefix 路径上的未复制对象：

```shell
mc replicate backlog myminio/mybucket/path/to/prefix --arn <remote-arn>
```

- 将 `myminio/mybucket` 替换为 [`ALIAS`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.ALIAS) 以及 需要显示未复制对象的完整存储桶路径。
- 将 `path/to/prefix` 替换为所需的前缀或对象路径。
- 将 `<remote-arn>` 替换为特定远程目标的资源编号。

如果存在未复制对象，输出会返回一个操作列表，列出创建或删除对象且尚未复制到远程目标的操作：

```shell
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:59 UTC]          478efe49-aa9d-46ab-8268-45b70cc4c341 PUT agenda.docx
[0001-01-01 00:00:00 UTC] [2022-10-06 17:18:15 UTC]          b283bf43-319f-455a-a779-3c2e669fad88 PUT budget-meeting.docx
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。