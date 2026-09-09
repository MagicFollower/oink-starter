---
title: "mc mv"

weight: 250
---

<a id="mc-mv"></a>

<a id="command-mc.mv"></a>

## 语法 {#id2}

[`mc mv`](#command-mc.mv) 命令将对象从源移动到目标，例如在不同 MinIO 部署之间移动，*或* 在同一 MinIO 部署的不同存储桶之间移动。 [`mc mv`](#command-mc.mv) 还支持在本地文件系统与 MinIO 之间移动对象。

你也可以对本地文件系统使用 [`mc mv`](#command-mc.mv)，以获得与 `mv` 命令行工具类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将对象从 `mydata` 存储桶移动到 `myminio` MinIO 部署上的 `archive` 存储桶：

```shell
mc mv --recursive myminio/mydata myminio/archive
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] mv         \
[--attr "string"]           \
[--disable-multipart]       \
[--enc-kms "string"]        \
[--enc-s3 "string"]         \
[--enc-c "string"]          \
[--limit-download string]   \
[--limit-upload string]     \
[--newer-than "string"]     \
[--older-than "string"]     \
[--preserve]                \
[--recursive]               \
[--storage-class "string"]  \
SOURCE [SOURCE...]          \
TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `SOURCE` {#mc.mv.SOURCE}

*mc-cmd*

##### `:required:` {#mc.mv.-required}

*mc-cmd*

要移动的一个或多个对象。

> 若要从 MinIO 存储桶移动对象，请指定 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及对象的完整路径（例如存储桶和对象路径）。例如：
>
> ```shell
> mc mv play/mybucket/object.txt play/myotherbucket/object.txt
> ```
>
> 若要从本地文件系统移动对象，请指定该对象的完整路径。例如：
>
> ```shell
> mc mv ~/mydata/object.txt play/mybucket/object.txt
> ```
>
> 指定多个 `SOURCE` 路径可将多个对象移动到指定的 [`TARGET`](#mc.mv.TARGET)。[`mc rm`](/docs/reference/minio-mc/mc-rm/#command-mc.rm) 将 *最后一个* 指定的 alias 或文件系统路径 视为 `TARGET`。例如：
>
> ```shell
> mc mv ~/mydata/object.txt play/mydata/otherobject.txt myminio/mydata
> ```
>
> 如果你为 [`SOURCE`](#mc.mv.SOURCE) 指定的是目录或存储桶， 则还必须指定 [`--recursive`](#mc.mv.-recursive) 以递归移动该目录内容。 如果省略 [`--recursive`](#mc.mv.-recursive) 参数，[`mv`](#command-mc.mv) 仅会移动 指定目录或存储桶顶层中的对象。

##### `TARGET` {#mc.mv.TARGET}

*mc-cmd*

*Required*

命令会将指定 [`SOURCE`](#mc.mv.SOURCE) 的对象移动到该存储桶， 这里填写该存储桶的完整路径。请将已配置 S3 服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 [`TARGET`](#mc.mv.TARGET) 路径前缀。

若要从 MinIO 移动对象，请指定 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及对象的完整路径（例如存储桶和对象路径）。例如：

```shell
mc mv play/mybucket/object.txt play/myotherbucket/object.txt
```

若要从本地文件系统移动对象，请指定该对象的完整路径。例如：

```shell
mc mv ~/mydata/object.txt play/mybucket/object.txt
```

`TARGET` 对象名可以不同于 `SOURCE`， 以便在移动操作中同时“重命名”对象。

如果以 [`--recursive`](#mc.mv.-recursive) 选项运行 [`mc mv`](#command-mc.mv)， [`mc mv`](#command-mc.mv) 会将 `TARGET` 视为 `SOURCE` 下所有对象的存储桶前缀。

##### `--attr` {#mc.mv.-attr}

*mc-cmd*

*Optional*

为对象添加自定义元数据。将键值对指定为 `KEY=VALUE\;`。 例如，`--attr key1=value1\;key2=value2\;key3=value3`。

##### `--disable-multipart` {#mc.mv.-disable-multipart}

*mc-cmd*

*Optional*

禁用 multipart upload 功能。

Multipart upload 会将对象拆分为多个独立分片。 每个分片可独立上传，且顺序不限。 如果任一分片上传失败，MinIO 会仅重试该分片而不影响其他分片。 上传完成后，这些分片会合并还原为原始对象。

MinIO 建议对大于 100 MB 的对象使用 multipart upload。 有关 multipart upload 的更多信息，请参阅 [Amazon S3 documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)

##### `--enc-kms` {#mc.mv.-enc-kms}

*mc-cmd*

使用客户端管理的密钥，通过服务端 [SSE-KMS 加密](/docs/administration/server-side-encryption/#minio-sse) 对对象进行加密或解密。

该参数接受格式为 `KEY=VALUE` 的键值对。

<table>
  <tbody>
    <tr>
      <td><p><code>KEY</code></p></td>
      <td><p>对象的完整路径，格式为 <code>alias/bucket/path/object.ext</code>。</p><p>你也可以只指定顶层路径，以便对该路径下的所有操作使用同一个加密密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>VALUE</code></p></td>
      <td><p>指定外部 KMS 上已有的数据密钥。</p><p>关于如何创建数据密钥，请参见 <a href="/docs/reference/minio-mc-admin/mc-admin-kms-key/#mc.admin.kms.key.create"><code>mc admin kms key create</code></a> 参考文档。</p></td>
    </tr>
  </tbody>
</table>

例如：

```shell
--enc-kms "myminio/mybucket/prefix/object.obj=mybucketencryptionkey"
```

你可以通过重复该参数来指定多个加密密钥。

也可以指定某个前缀路径，对该路径下所有匹配对象应用加密：

```shell
--enc-kms "myminio/mybucket/prefix/=mybucketencryptionkey"
```

##### `--enc-s3` {#mc.mv.-enc-s3}

*mc-cmd*

*Optional*

使用 KMS 管理的密钥，通过服务端 [SSE-S3 加密](/docs/administration/server-side-encryption/#minio-sse) 对对象进行加密或解密。 指定对象的完整路径，格式为 `alias/bucket/prefix/object`。

例如：

```shell
--enc-s3 "myminio/mybucket/prefix/object.obj"
```

你可以多次指定该参数，以表示不同的待加密对象：

```shell
--enc-s3 "myminio/mybucket/foo/fooobject.obj" --enc-s3 "myminio/mybucket/bar/barobject.obj"
```

也可以指定某个前缀路径，对该路径下所有匹配对象应用加密：

```shell
--enc-s3 "myminio/mybucket/foo"
```

##### `--enc-c` {#mc.mv.-enc-c}

*mc-cmd*

*Optional*

使用客户端管理的密钥，通过服务端 [SSE-C 加密](/docs/administration/server-side-encryption/#minio-sse) 对对象进行加密或解密。

该参数接受格式为 `KEY=VALUE` 的键值对。

<table>
  <tbody>
    <tr>
      <td><p><code>KEY</code></p></td>
      <td><p>对象的完整路径，格式为 <code>alias/bucket/path/object.ext</code>。</p><p>你也可以只指定顶层路径，以便对该路径下的所有操作使用同一个加密密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>VALUE</code></p></td>
      <td><p>指定用于 SSE-C 加密的密钥，可以是 32 字节 RawBase64 编码密钥，
<em>也可以是</em> 64 字节十六进制编码密钥。</p><p>Raw Base64 编码 <strong>不接受</strong> 带 <code>=</code> 填充的密钥。
请去掉填充，或使用支持 RAW 格式的 Base64 编码器。</p></td>
    </tr>
  </tbody>
</table>

- `KEY` - 对象的完整路径，格式为 `alias/bucket/path/object`。
- `VALUE` - 用于加密对象的 32 字节 RAW Base64 编码数据密钥。

例如：

```shell
# RawBase64-Encoded string "mybucket32byteencryptionkeyssec"
--enc-c "myminio/mybucket/prefix/object.obj=bXlidWNrZXQzMmJ5dGVlbmNyeXB0aW9ua2V5c3NlYwo"
```

你可以通过重复该参数来指定多个加密密钥。

也可以指定某个前缀路径，对该路径下所有匹配对象应用加密：

```shell
--enc-c "myminio/mybucket/prefix/=bXlidWNrZXQzMmJ5dGVlbmNyeXB0aW9ua2V5c3NlYwo"
```

> [!NOTE]
> **说明**
>
> MinIO 强烈不建议在生产负载中使用 SSE-C 加密。 请改用 `--enc-kms` 参数启用 SSE-KMS，或使用 `--enc-s3` 参数启用 SSE-S3。

##### `--limit-download` {#mc.mv.-limit-download}

*mc-cmd*

*Optional*

将客户端侧下载速率限制为不超过指定值，单位可以是 KiB/s、MiB/s 或 GiB/s。 这只影响下载到运行 MinIO Client 的本地设备的速度。 有效单位包括：

- `B` 表示字节
- `K` 表示千字节
- `M` 表示兆字节
- `G` 表示吉字节
- `T` 表示太字节
- `Ki` 表示二进制千字节
- `Mi` 表示二进制兆字节
- `Gi` 表示二进制吉字节
- `Ti` 表示二进制太字节

例如，如需将下载速率限制为不超过 1 GiB/s，请使用以下命令：

```text
--limit-download 1G
```

如果未指定，MinIO 将使用不受限制的下载速率。

##### `--limit-upload` {#mc.mv.-limit-upload}

*mc-cmd*

*Optional*

将客户端侧上传速率限制为不超过指定值，单位可以是 KiB/s、MiB/s 或 GiB/s。 这只影响从运行 MinIO Client 的本地设备发起的上传速度。 有效单位包括：

- `B` 表示字节
- `K` 表示千字节
- `M` 表示兆字节
- `G` 表示吉字节
- `T` 表示太字节
- `Ki` 表示二进制千字节
- `Mi` 表示二进制兆字节
- `Gi` 表示二进制吉字节
- `Ti` 表示二进制太字节

例如，如需将上传速率限制为不超过 1 GiB/s，请使用以下命令：

```text
--limit-upload 1G
```

如果未指定，MinIO 将使用不受限制的上传速率。

##### `--newer-than` {#mc.mv.-newer-than}

*mc-cmd*

*Optional*

删除比指定天数更新的对象。指定格式为 `##d#hh#mm#ss` 的字符串。例如： `--newer-than 1d2hh3mm4ss`。

默认为 `0`（所有对象）。

##### `--older-than` {#mc.mv.-older-than}

*mc-cmd*

*Optional*

删除早于指定时间限制的对象。指定格式为 `#d#hh#mm#ss` 的字符串。例如：`--older-than 1d2hh3mm4ss`。

默认为 `0`（所有对象）。

##### `--preserve, a` {#mc.mv.-preserve}

*mc-cmd*

*Optional*

保留 [`SOURCE`](#mc.mv.SOURCE) 目录、存储桶和对象在文件系统上的属性 以及存储桶策略规则，并应用到 [`TARGET`](#mc.mv.TARGET) 存储桶。

##### `--recursive, r` {#mc.mv.-recursive}

*mc-cmd*

*Optional*

将每个 [`SOURCE`](#mc.mv.SOURCE) 存储桶或目录的内容 递归移动到 [`TARGET`](#mc.mv.TARGET) 存储桶。

##### `--storage-class` {#mc.mv.-storage-class}

*mc-cmd*

*Optional*

为 [`TARGET`](#mc.mv.TARGET) 上的新对象设置存储类别。

有关 S3 storage class 的更多信息，请参阅 Amazon 文档 [Storage Classes](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id9}

### 将文件从文件系统移动到 S3-Compatible Host {#s3-compatible-host}

```shell
mc mv [--recursive] FILEPATH ALIAS/PATH
```

- 将 [`FILEPATH`](#mc.mv.SOURCE) 替换为要移动文件的完整文件路径。

  如果指定的是目录路径，请包含 [`--recursive`](#mc.mv.-recursive) 标志。

  [`mc mv`](#command-mc.mv) 在成功移动到目标后，会从源中 *移除* 这些文件。
- 将 [`ALIAS`](#mc.mv.TARGET) 替换为已配置 S3-compatible host 的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.mv.TARGET) 替换为目标存储桶。

### 将文件从文件系统移动到 S3-Compatible Host 并附带自定义元数据 {#id10}

使用带 [`--attr`](#mc.mv.-attr) 选项的 [`mc mv`](#command-mc.mv)， 可为文件设置自定义属性。

```shell
mc mv --attr "ATTRIBUTES" FILEPATH ALIAS/PATH
```

- 将 [`FILEPATH`](#mc.mv.SOURCE) 替换为要移动文件的完整文件路径。 [`mc mv`](#command-mc.mv) 在成功移动到目标后，会从源中 *移除* 该文件。
- 将 [`ALIAS`](#mc.mv.TARGET) 替换为已配置 S3-compatible host 的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.mv.TARGET) 替换为目标存储桶。
- 将 [`ATTRIBUTES`](#mc.mv.-attr) 替换为一个或多个逗号分隔的 键值对 `KEY=VALUE`。每个键值对表示一个属性键及其值。

### 在 S3-Compatible 服务之间移动存储桶 {#s3-compatible}

```shell
 mc mv --recursive SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`SRCALIAS`](#mc.mv.SOURCE) 替换为已配置 S3-compatible host 的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.mv.SOURCE) 替换为存储桶路径。 [`mc mv`](#command-mc.mv) 在成功移动到目标后，会从源中 *移除* 该存储桶及其内容。
- 将 [`TGTALIAS`](#mc.mv.TARGET) 替换为已配置 S3-compatible host 的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.mv.TARGET) 替换为存储桶路径。

### 将文件移动到 S3-Compatible Host 并指定存储类别 {#id11}

使用带 [`--storage-class`](#mc.mv.-storage-class) 选项的 [`mc mv`](#command-mc.mv)， 可在目标 S3-compatible host 上设置存储类别。

```shell
mc mv --storage-class CLASS FILEPATH ALIAS/PATH
```

- 将 [`CLASS`](#mc.mv.-storage-class) 替换为要 关联到文件的存储类别。
- 将 [`FILEPATH`](#mc.mv.SOURCE) 替换为要移动文件的完整文件路径。 [`mc mv`](#command-mc.mv) 在成功移动到目标后，会从源中 *移除* 该文件。
- 将 [`ALIAS`](#mc.mv.TARGET) 替换为已配置 S3-compatible host 的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.mv.TARGET) 替换为目标存储桶。
- 将 [`ATTRIBUTES`](#mc.mv.-attr) 替换为一个或多个逗号分隔的 键值对 `KEY=VALUE`。每个键值对表示一个属性键及其值。

  > mc mv –storage-class REDUCED_REDUNDANCY myobject.txt play/mybucket

## 行为 {#id12}

### 移动时的对象名称 {#id13}

如果未显式指定目标对象名，在将对象移动到 [`TARGET`](#mc.mv.TARGET) 时，MinIO 会使用 [`SOURCE`](#mc.mv.SOURCE) 的对象名。

你可以在相同对象路径下，为 [`TARGET`](#mc.mv.TARGET) 指定不同的对象名，以在移动时“重命名”对象。例如：

```shell
mc mv play/mybucket/object.txt play/mybucket/myobject.txt
```

对于递归移动操作（[`mc mv --recursive`](#mc.mv.-recursive)），MinIO 会将 `TARGET` 路径视为 `SOURCE` 上对象的前缀。

### 校验和验证 {#id14}

[`mc mv`](#command-mc.mv) 使用 MD5SUM 校验和验证所有到对象存储的移动操作。

### MinIO 在对象删除时会裁剪空前缀 {#minio}

[`mc mv`](#command-mc.mv) 依赖 [`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 来移除对象。在删除存储桶前缀中的最后一个对象时， [`mc`](/docs/reference/minio-mc/#command-mc) 还会递归删除直到存储桶根为止的每一个空前缀。[`mc`](/docs/reference/minio-mc/#command-mc) 只会对在对象写入 操作过程中 *隐式* 创建的前缀执行这种递归删除，也就是说，该前缀不是通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 这类显式目录创建命令创建的。

例如，假设存储桶 `photos` 中有以下对象前缀：

- `photos/2021/january/myphoto.jpg`
- `photos/2021/february/myotherphoto.jpg`
- `photos/NYE21/NewYears.jpg`

`photos/NYE21` 是 *唯一* 通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 显式创建的前缀。其余所有前缀 都是在向该前缀写入对象时 *隐式* 创建的。

如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `myphoto.jpg`，删除 API 会自动裁剪空的 `/january` 前缀。如果后续某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令又删除了 `myotherphoto.jpg`， 删除 API 会自动裁剪 `/february` 前缀，以及此时已经为空的 `/2021` 前缀。 如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `NewYears.jpg`，由于 `/NYE21` 是 *显式* 创建的，因此该前缀会保留不变。

如果将 [`mc mv`](#command-mc.mv) 用于文件系统操作，[`mc`](/docs/reference/minio-mc/#command-mc) 也会采用相同行为，递归裁剪直到 根目录的所有空目录。不过，[`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 无法区分某个目录路径是显式 创建的，还是隐式创建的。如果 [`mc mv`](#command-mc.mv) 删除了某个文件系统路径上的最后一个对象， [`mc`](/docs/reference/minio-mc/#command-mc) 会在删除过程中递归删除从该路径向上直到根目录的所有空目录。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。