---
title: "mc od"

weight: 260
---

<a id="mc-od"></a>

<a id="command-mc.od"></a>

## 语法 {#id2}

[`mc od`](#command-mc.od) 命令将本地文件按指定的分片数量与分片大小复制到远程位置。 该命令会输出上传该文件所耗费的时间。

使用 [`mc od`](#command-mc.od) 可模拟 Linux `dd` 命令的功能。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将文件的 200MiB 上传到存储桶中，分为 5 个 40MiB 的分片。 输出会显示上传结果，包括完成上传所用的时长。

```shell
mc od if=file.zip of=myminio/mybucket/file.zip size=40MiB parts=5
```

如果传入 `--json` [全局参数](/docs/reference/minio-mc/#minio-mc-global-options)，命令输出类似如下：

```json
{
  "source": "home/user/file.zip"
  "target": "myminio/mybucket/file.zip"
  "partSize": 41943040
  "totalSize": 209715200
  "parts": 5
  "elapsed": "314ms"
}
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] od                                            \
                 if=<path of source file to upload>            \
                 of=<target MinIO path to upload to>           \
                 [size=<size of file>]                         \
                 [parts=<number of parts to split file into>]  \
                 [skip=<number of parts to skip>]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `if` {#mc.od.if}

*mc-cmd*

*Required*

用于上传的源对象路径。 使用相对于当前位置的完整路径。

```text
mc od if=file.zip of=myminio/mybucket/file.zip
```

##### `of` {#mc.od.of}

*mc-cmd*

*Required*

上传对象的完整目标路径。

##### `size` {#mc.od.size}

*mc-cmd*

*Optional*

文件上传时每个分片的大小。 如未指定，MinIO 会根据源流确定分片大小。

##### `parts` {#mc.od.parts}

*mc-cmd*

*Optional*

上传时将对象拆分成的分片数量。 如未指定，MinIO 会根据源流大小确定分片数量。

##### `skip` {#mc.od.skip}

*mc-cmd*

*Optional*

上传过程中要跳过的文件分片数量。 例如，可使用该选项仅上传对象的一部分分片，以测试一个大文件（分片较多）的上传速度。

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 以 40MiB 分片上传完整文件 {#mib}

使用 [`mc od`](#command-mc.od) 可按指定大小的一组分片将文件上传到 MinIO。 [`size`](#mc.od.size) 选项用于指定期望的分片大小。

```shell
mc od if=file.zip of=myminio/mybucket/file.zip size=40MiB
```

- 将 `myminio/mybucket/file.zip` 替换为要上传的对象或文件流路径。
- 将 [`size`](#mc.od.size) 替换为期望的对象分片大小。

MinIO 会检查源文件并将其拆分为所需数量的分片，确保没有任何分片超过指定的 40MiB 分片大小。

### 上传文件的前五个 40 MiB 分片 {#id6}

使用 [`mc od`](#command-mc.od) 可按指定分片大小，将文件的部分分片上传到 MinIO。 [`size`](#mc.od.size) 选项用于指定期望的分片大小。 [`parts`](#mc.od.parts) 选项用于指定该对象要使用的总分片数。

```shell
mc od if=file.zip of=myminio/mybucket/file.zip size=40MiB parts=5
```

- 将 `myminio/mybucket/file.zip` 替换为要上传的对象或文件流路径。
- 将 [`size`](#mc.od.size) 替换为期望的对象分片大小。
- 将 [`parts`](#mc.od.parts) 替换为该对象期望使用的分片数。

在该命令示例中，如果源对象流大于 200MiB（40MiB × 5 个分片），则仅上传文件的前 200MiB。

> [!WARNING]
> **重要**
>
> 以这种方式使用该命令可能无法上传对象的全部内容。

### 将完整文件分 5 个分片上传 {#id7}

将源文件拆分为指定数量的分片，然后把文件的所有分片上传到 MinIO 目标位置。

```shell
mc od if=file.zip of=myminio/mybucket/file.zip parts=5
```

上述命令会将源文件均分为五个分片，然后上传这些分片。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。