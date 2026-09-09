---
title: "mc head"

weight: 130
---

<a id="mc-head"></a>
<a id="minio-mc-head"></a>

<a id="command-mc.head"></a>

## 语法 {#id2}

[`mc head`](#command-mc.head) 命令显示对象的前 `n` 行， 其中 `n` 是传递给该命令的参数。

[`mc head`](#command-mc.head) 不会对对象内容执行任何转换或格式化来提升可读性。 你也可以将 [`mc head`](#command-mc.head) 用于本地文件系统，以获得与 `head` 命令行工具类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回 `myminio` MinIO 部署中 `mydata` 存储桶内某个对象的前 10 行：

```shell
mc head myminio/mydata/myobject.txt
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] head                     \
                 [--lines int]            \
                 [--rewind "string"]      \
                 [--version-id "string"]  \
                 [--enc-c "string"]       \
                 ALIAS [ALIAS ...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.head.ALIAS}

*mc-cmd*

*Required*

要输出的一个或多个对象。

对于 MinIO 上的对象，请指定 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和该对象的完整路径 （例如存储桶和对象路径）。例如：

```text
mc head play/mybucket/object.txt
```

你可以在同一个或不同的 MinIO 部署上指定多个对象。例如：

```text
mc head ~/mydata/object.txt myminio/mydata/object.txt
```

对于本地文件系统上的对象，请指定该对象的完整路径。 例如：

```text
mc head ~/mydata/object.txt
```

##### `--lines, n` {#mc.head.-lines}

*mc-cmd*

*Optional*

要输出的行数。

默认为 `10`。

##### `--enc-c` {#mc.head.-enc-c}

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

##### `--rewind` {#mc.head.-rewind}

*mc-cmd*

*Optional*

指示 [`mc head`](#command-mc.head) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.head.-rewind) 要求指定的 [`ALIAS`](#mc.head.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, vid` {#mc.head.-version-id}

*mc-cmd*

*Optional*

指示 [`mc head`](#command-mc.head) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.head.-version-id) 要求指定的 [`ALIAS`](#mc.head.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 查看对象的部分内容 {#id6}

使用 [`mc head`](#command-mc.head) 返回对象的前 10 行：

```shell
mc head ALIAS/PATH
```

- 将 [`ALIAS`](#mc.head.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.head.ALIAS) 替换为该对象在 S3 兼容主机上的路径。

### 查看对象在某个时间点的部分内容 {#id7}

使用 [`mc head --rewind`](#mc.head.-rewind) 返回对象在过去特定时间点的前 10 行：

```shell
mc head ALIAS/PATH --rewind DURATION
```

- 将 [`ALIAS`](#mc.head.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.head.ALIAS) 替换为该对象在 S3 兼容主机上的路径。
- 将 [`DURATION`](#mc.head.-rewind) 替换为过去的某个时间点， 命令会返回该时间点对应的对象。例如，指定 `30d` 可返回当前日期前 30 天的对象版本。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc head`](#command-mc.head) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 查看对象指定版本的部分内容 {#id8}

使用 [`mc head --version-id`](#mc.head.-version-id) 返回对象特定版本的前 10 行：

```shell
mc head ALIAS/PATH --version-id VERSION
```

- 将 [`ALIAS`](#mc.head.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.head.ALIAS) 替换为该对象在 S3 兼容主机上的路径。
- 将 [`VERSION`](#mc.head.-version-id) 替换为对象版本。 例如，指定 `30d` 可返回当前日期前 30 天的对象版本。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc head`](#command-mc.head) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。