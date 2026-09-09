---
title: "mc replicate status"

weight: 70
---

<a id="mc-replicate-status"></a>
<a id="minio-mc-replicate-status"></a>

<a id="command-mc.replicate.status"></a>

## 语法 {#id1}

[`mc replicate status`](#command-mc.replicate.status) 命令显示 MinIO 存储桶的 [复制状态](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。 该状态还会列出远程目标路径或位置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 `myminio` MinIO 部署上 `mydata` 存储桶的当前复制状态：

```shell
mc replicate status myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] replicate status TARGET
                           [--limit-upload value]
                           [--limit-download value]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.replicate.status.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要显示复制状态的存储桶或存储桶前缀的完整路径。 例如：

```text
mc replicate status myminio/mybucket
```

##### `--limit-download` {#mc.replicate.status.-limit-download}

*mc-cmd*

*Optional*

将下载速率限制为不超过指定值，单位可为 KiB/s、MiB/s 或 GiB/s。 有效单位包括：

- `B` 表示 bytes
- `K` 表示 kilobytes
- `G` 表示 gigabytes
- `T` 表示 terabytes
- `Ki` 表示 kibibytes
- `Gi` 表示 gibibytes
- `Ti` 表示 tebibytes

例如，要将下载速率限制为不超过 1 GiB/s，可使用以下参数：

```text
--limit-download 1G
```

如果未指定，MinIO 使用不限速的下载速率。

##### `--limit-upload` {#mc.replicate.status.-limit-upload}

*mc-cmd*

*Optional*

将上传速率限制为不超过指定值，单位可为 KiB/s、MiB/s 或 GiB/s。 有效单位包括：

- `B` 表示 bytes
- `K` 表示 kilobytes
- `G` 表示 gigabytes
- `T` 表示 terabytes
- `Ki` 表示 kibibytes
- `Gi` 表示 gibibytes
- `Ti` 表示 tebibytes

例如，要将上传速率限制为不超过 1 GiB/s，可使用以下参数：

```text
--limit-upload 1G
```

如果未指定，MinIO 使用不限速的上传速率。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 显示复制状态 {#id5}

使用 [`mc replicate status`](#command-mc.replicate.status) 显示存储桶复制状态：

```shell
mc replicate status ALIAS/PATH
```

- 将 [`ALIAS`](#mc.replicate.status.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.status.ALIAS) 替换为存储桶或存储桶前缀路径。

## 行为 {#id6}

### 移除并重新添加的 ARN {#arn}

> [!NOTE]
> **变更: mc**
>
> RELEASE.2023-03-20T17-17-53Z

该命令的标准输出不会显示此前已从复制配置中移除的 ARN。

如需列出所有 ARN（包括不再属于当前复制配置的 ARN），请使用 `--json` 标志。 `json` 输出会持续显示在旧 ARN 下复制的数据。 如果某个 ARN 在同一存储桶上被移除后又重新添加，这些信息会很有价值。

新的 ARN **不会** 触发对先前已同步对象的重新复制。