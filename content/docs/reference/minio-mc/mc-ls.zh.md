---
title: "mc ls"

weight: 220
---

<a id="mc-ls"></a>

<a id="command-mc.ls"></a>

## 语法 {#id1}

[`mc ls`](#command-mc.ls) 命令用于列出 MinIO 或其他 S3 兼容服务上的存储桶和对象。

你也可以对本地文件系统使用 [`mc ls`](#command-mc.ls)，生成与 `ls` 命令类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶内的所有对象 *及* 对象版本：

```shell
mc ls --recursive --versions myminio/mydata
```

输出类似如下：

```shell
[2022-11-08 11:30:24 PST]    52MB  STANDARD log-data.csv
[2022-11-09 12:20:18 PST]    120MB WARM videos/event-2022-11-09.mp4
```

- `STANDARD` 表示存储在 MinIO 部署上的对象
- `WARM` 表示存储在同名远端层中的对象
- `videos/` 表示对象的前缀
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] ls              \
                 [--incomplete]  \
                 [--recursive]   \
                 [--rewind]      \
                 [--versions]    \
                 [--summarize]   \
                 ALIAS [ALIAS ...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.ls.ALIAS}

*mc-cmd*

*必需* 要复制的一个或多个对象。

对于列出 MinIO 上的对象， 指定该对象的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整路径 （例如存储桶和对象路径）。例如：

```text
mc ls play/mybucket/object.txt
```

对于列出本地文件系统上的对象，指定该对象的完整路径。 例如：

```text
mc ls ~/mydata/object.txt
```

如果你在 [`ALIAS`](#mc.ls.ALIAS) 中指定的是目录或存储桶，则还必须 指定 [`--recursive`](#mc.ls.-recursive)，以递归列出该目录或存储桶的内容。 如果省略 `--recursive` 参数，[`ls`](#command-mc.ls) 仅列出指定目录或存储桶 顶层的对象。

##### `incomplete, -I` {#mc.ls.incomplete}

*mc-cmd*

*可选* 返回指定 [`ALIAS`](#mc.ls.ALIAS) 存储桶上的所有未完成上传。

##### `--recursive, r` {#mc.ls.-recursive}

*mc-cmd*

*可选* 递归列出 [`ALIAS`](#mc.ls.ALIAS) 中各存储桶或目录的内容。

##### `--rewind` {#mc.ls.-rewind}

*mc-cmd*

*Optional*

指示 [`mc ls`](#command-mc.ls) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.ls.-rewind) 要求指定的 [`ALIAS`](#mc.ls.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

同时使用 [`--rewind`](#mc.ls.-rewind) 和 [`--versions`](#mc.ls.-versions)，可显示在特定时间点存在的对象版本。

##### `--versions` {#mc.ls.-versions}

*mc-cmd*

*Optional*

指示 [`mc ls`](#command-mc.ls) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.ls.-versions) 要求指定的 [`ALIAS`](#mc.ls.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

同时使用 [`--versions`](#mc.ls.-versions) 和 [`--rewind`](#mc.ls.-rewind)，可显示在特定时间点存在的对象版本。

##### `--summarize` {#mc.ls.-summarize}

*mc-cmd*

*可选* 显示指定 `ALIAS` 路径的汇总信息。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 列出存储桶内容 {#id5}

使用 [`mc ls`](#mc.ls.ALIAS) 列出存储桶内容：

```shell
mc ls [--recursive] ALIAS/PATH
```

- 将 [`ALIAS`](#mc.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ls.ALIAS) 替换为 S3 兼容主机上 存储桶的路径。

  如果指定的是 S3 根路径（仅 `ALIAS`），请包含 [`--recursive`](#mc.ls.-recursive) 选项。

### 列出对象版本 {#id6}

使用 [`mc ls --versions`](#mc.ls.-versions) 列出对象的所有版本：

```shell
mc ls --versions ALIAS/PATH
```

- 将 [`ALIAS`](#mc.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ls.ALIAS) 替换为 S3 兼容主机上 存储桶或对象的路径。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc ls`](#command-mc.ls) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 列出某个时间点的存储桶内容 {#id7}

使用 [`mc ls --versions`](#mc.ls.-versions) 列出对象的所有版本：

```shell
mc ls --rewind DURATION ALIAS/PATH
```

- 将 [`ALIAS`](#mc.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ls.ALIAS) 替换为 S3 兼容主机上 存储桶或对象的路径。
- 将 [`DURATION`](#mc.ls.-rewind) 替换为过去的某个时间点， 命令将在该时间点返回对象。例如，指定 `30d` 以返回相对于当前日期 往前 30 天的对象版本。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc ls`](#command-mc.ls) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。