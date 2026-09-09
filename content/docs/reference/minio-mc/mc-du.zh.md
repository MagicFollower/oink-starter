---
title: "mc du"

weight: 80
---

<a id="mc-du"></a>
<a id="minio-mc-du"></a>

<a id="command-mc.du"></a>

## 语法 {#id2}

[`mc du`](#command-mc.du) 命令用于汇总存储桶和文件夹的磁盘使用量。 你也可以对本地文件系统使用 [`du`](#command-mc.du)，以生成与 `du` 命令类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令打印 `myminio` MinIO 部署中 `mybucket` 存储桶的磁盘使用量：

```shell
mc du play/mybucket
```

输出类似如下：

```shell
825KiB 3 objects        mybucket
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc du`](#command-mc.du) 命令语法如下：

```shell
mc [GLOBALFLAGS] du                    \
                 [--depth]             \
                 [--recursive]         \
                 [--rewind]            \
                 [--versions]          \
                 ALIAS [ALIAS ...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.du.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及文件夹的完整路径。例如：

```shell
mc du myminio/mybucket
```

你可以在同一个或不同的 MinIO 部署上指定多个存储桶和文件夹。例如：

```shell
mc du myminio/mybucket myminio/myotherbucket/myfolder
```

对于本地文件系统中的文件夹，请指定该文件夹的完整路径。例如：

```shell
mc du ~/data/images
```

[`mc du`](#command-mc.du) 完成所需时间取决于目标存储桶和文件夹的大小。大型存储桶可能需要一些时间来生成磁盘使用量摘要。

##### `--depth, d` {#mc.du.-depth}

*mc-cmd*

*Optional*

打印命令中指定路径下 N 层及以内所有文件夹的总计值。默认值为 0，仅统计指定路径本身。

##### `--recursive, r` {#mc.du.-recursive}

*mc-cmd*

*Optional*

递归打印每个存储桶或子文件夹的总计值。

##### `--rewind` {#mc.du.-rewind}

*mc-cmd*

*Optional*

指示 [`mc du`](#command-mc.du) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.du.-rewind) 要求指定的 [`ALIAS`](#mc.du.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--rewind`](#mc.du.-rewind) 与 [`--versions`](#mc.du.-versions) 一起使用，可显示特定时间点存在的对象版本的磁盘使用量。

##### `--versions` {#mc.du.-versions}

*mc-cmd*

*Optional*

指示 [`mc du`](#command-mc.du) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.du.-versions) 要求指定的 [`ALIAS`](#mc.du.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.du.-versions) 与 [`--rewind`](#mc.du.-rewind) 一起使用，可显示特定时间点存在的对象版本的磁盘使用量。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 查看存储桶或文件夹的磁盘使用量 {#id6}

使用 [`mc du`](#command-mc.du) 打印存储桶或文件夹的磁盘使用量摘要：

```shell
mc du ALIAS/PATH
```

- 将 `ALIAS` 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上存储桶或文件夹的路径。

### 查看某个时间点的磁盘使用量 {#id7}

使用 [`mc du --rewind`](#mc.du.-rewind) 打印过去某个特定时间点的磁盘使用量摘要：

```shell
mc du --rewind DURATION ALIAS/PATH
```

- 将 `DURATION` 替换为所需的过去时间点。例如，指定 `30d` 以显示当前日期前 30 天的磁盘使用量。
- 将 `ALIAS` 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上存储桶或文件夹的路径。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc du`](#command-mc.du) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 递归查看磁盘使用量 {#id8}

使用 [`mc du --recursive`](#mc.du.-recursive) 递归打印每个文件夹的摘要：

```shell
mc du --recursive ALIAS/PATH
```

- 将 `ALIAS` 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上存储桶或文件夹的路径。

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。