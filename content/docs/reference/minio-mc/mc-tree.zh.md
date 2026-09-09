---
title: "mc tree"

weight: 400
---

<a id="mc-tree"></a>

<a id="command-mc.tree"></a>

## 语法 {#id2}

[`mc tree`](#command-mc.tree) 命令以树形格式列出 MinIO 存储桶中的所有前缀。 该命令还可选支持在每个前缀处列出存储桶内的所有对象，包括存储桶根。

你也可以将 [`mc tree`](#command-mc.tree) 用于本地文件系统目录， 获得与 `tree` 命令行工具类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会打印 `myminio` MinIO 部署中 `mydata` 存储桶内 任意深度的全部对象树：

```shell
mc tree --files myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] tree                 \
                 [--depth int]        \
                 [--files]            \
                 [--rewind "string"]  \
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.tree.ALIAS}

*mc-cmd*

*必需* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶的完整路径， 用于列出树形层级。例如：

```shell
mc tree myminio/mybucket
```

你可以为 [`mc tree`](#command-mc.tree) 命令指定多个目标。例如：

```shell
mc tree myminio/mybucket myminio/myotherbucket
```

如需获取本地文件系统目录的树形层级， 请指定该目录的完整路径。例如：

```shell
mc tree ~/minio/mydata/
```

##### `--depth, d` {#mc.tree.-depth}

*mc-cmd*

*可选* 将树深度限制为指定的整数值。

默认为 `-1`，即不限制深度。

##### `--files, f` {#mc.tree.-files}

*mc-cmd*

*可选* 在 [`mc tree`](#command-mc.tree) 输出中包含对象或目录中的文件。

##### `--rewind` {#mc.tree.-rewind}

*mc-cmd*

*Optional*

指示 [`mc tree`](#command-mc.tree) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.tree.-rewind) 要求指定的 [`ALIAS`](#mc.tree.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

## 示例 {#id4}

```shell
mc tree ALIAS/PATH
```

- 将 [`ALIAS`](#mc.tree.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.tree.ALIAS) 替换为 MinIO 部署上存储桶的路径。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。