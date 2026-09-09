---
title: "mc cat"

weight: 50
---

<a id="mc-cat"></a>
<a id="minio-mc-cat"></a>

<a id="command-mc.cat"></a>

## 语法 {#id2}

[`mc cat`](#command-mc.cat) 命令将文件或对象的内容连接到另一个文件或对象。 你也可以使用该命令将指定文件或对象的内容输出到 `STDOUT`。 [`cat`](#command-mc.cat) 的功能与 `cat` 类似。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将 MinIO 部署中某个对象的内容输出到 `STDOUT`：

```shell
mc cat play/mybucket/myobject.txt
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc cat`](#command-mc.cat) 命令语法如下：

```shell
mc [GLOBALFLAGS] cat                       \
                 ALIAS [ALIAS ...]         \
                 [--enc-c "value"]         \
                 [--offset "int"]          \
                 [--part-number "int"]     \
                 [--rewind]                \
                 [--tail "int"]            \
                 [--version-id "string"]   \
                 [--zip]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

你也可以将 [`mc cat`](#command-mc.cat) 用于本地文件系统，以获得与 `cat` 命令行工具类似的结果。

### 参数 {#id3}

##### `ALIAS` {#mc.cat.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及对象的完整路径。例如：

```shell
mc cat myminio/mybucket/myobject.txt
```

你可以指定同一或不同 MinIO 部署中的多个对象。例如：

```shell
mc cat myminio/mybucket/object.txt myminio/myotherbucket/object.txt
```

对于本地文件系统上的对象，请指定该对象的完整路径。例如：

```shell
mc cat ~/data/object.txt
```

##### `--enc-c` {#mc.cat.-enc-c}

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

##### `--offset` {#mc.cat.-offset}

*mc-cmd*

*Optional*

指定一个整数，表示命令输出的字节偏移位置。

与 [`--part-number`](#mc.cat.-part-number) 标志互斥。

##### `--part-number` {#mc.cat.-part-number}

*mc-cmd*

*Optional*

下载分段上传中的指定分段编号。 指定要下载的分段编号整数值。

与 [`--offset`](#mc.cat.-offset) 和 [`--tail`](#mc.cat.-tail) 标志互斥。

##### `--rewind` {#mc.cat.-rewind}

*mc-cmd*

*Optional*

指示 [`mc cat`](#command-mc.cat) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.cat.-rewind) 要求指定的 [`ALIAS`](#mc.cat.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--tail` {#mc.cat.-tail}

*mc-cmd*

*Optional*

指定一个整数，表示命令从该字节数开始裁剪输出。

与 [`--part-number`](#mc.cat.-part-number) 标志互斥。

##### `--version-id, vid` {#mc.cat.-version-id}

*mc-cmd*

*Optional*

指示 [`mc cat`](#command-mc.cat) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.cat.-version-id) 要求指定的 [`ALIAS`](#mc.cat.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--zip` {#mc.cat.-zip}

*mc-cmd*

*Optional*

将源端 zip 文件中的内容提取到远端。 要求源 `ALIAS` 为 MinIO 部署。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 查看 S3 对象 {#s3}

使用 [`mc cat`](#command-mc.cat) 返回对象：

```shell
mc cat ALIAS/PATH
```

- 将 [`ALIAS`](#mc.cat.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cat.ALIAS) 替换为对象在 S3 兼容主机上的路径。

### 按时间点查看 S3 对象 {#id6}

使用 [`mc cat --rewind`](#mc.cat.-rewind) 返回过去某个特定时间点的对象：

```shell
mc cat ALIAS/PATH --rewind DURATION
```

- 将 [`ALIAS`](#mc.cat.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cat.ALIAS) 替换为对象在 S3 兼容主机上的路径。
- 将 [`DURATION`](#mc.cat.-rewind) 替换为命令返回对象时对应的 过去时间点。例如，指定 `30d` 可返回当前日期前 30 天的对象版本。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc cat`](#command-mc.cat) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 查看 S3 对象的指定版本 {#id7}

使用 [`mc cat --version-id`](#mc.cat.-version-id) 返回对象的特定版本：

```shell
mc cat ALIAS/PATH --version-id VERSION
```

- 将 [`ALIAS`](#mc.cat.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cat.ALIAS) 替换为对象在 S3 兼容主机上的路径。
- 将 [`VERSION`](#mc.cat.-version-id) 替换为要返回的对象特定版本。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc cat`](#command-mc.cat) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 下载特定分段 {#id8}

使用 [`mc cat --part-number`](#mc.cat.-part-number) 下载分段上传中的特定分段：

```shell
mc cat ALIAS/PATH --part-number=#
```

- 将 [`ALIAS`](#mc.cat.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cat.ALIAS) 替换为对象在 S3 兼容主机上的路径。
- 将 `#` 替换为要下载的分段编号整数值。 例如，要下载一个 16 段分段文件中的第 3 段，使用 `--part-number=3`。

如果使用了 `--offset` 或 `--tail` 标志，则不能使用 `--part-number` 标志。

## 行为 {#id9}

### S3 兼容性 {#id10}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。