---
title: "mc cp"

weight: 60
---

<a id="mc-cp"></a>
<a id="minio-mc-cp"></a>

<a id="command-mc.cp"></a>

## 语法 {#id2}

[`mc cp`](#command-mc.cp) 命令用于在 MinIO 部署与本地文件系统之间复制对象， 其中源端可以是 MinIO *或* 本地文件系统。

你也可以将 [`mc cp`](#command-mc.cp) 用于本地文件系统，达到与 `cp` 命令行工具 类似的效果。

> [!NOTE]
> **说明**
>
> [`mc cp`](#command-mc.cp) 仅复制对象的最新版本或指定版本，不包含任何版本信息或修改日期。 要复制所有版本、版本信息及相关元数据，请使用 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 或 [`mc admin replicate`](/docs/reference/minio-mc-admin/mc-admin-replicate/#command-mc.admin.replicate)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将文件从本地文件系统目录复制到 `myminio` MinIO 部署中的 `mydata` 存储桶：

```shell
mc cp --recursive ~/mydata/ myminio/mydata/
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc cp`](#command-mc.cp) 命令的语法如下：

```shell
mc [GLOBALFLAGS] cp                                                        \
                 [--attr "string"]                                         \
                 [--disable-multipart]                                     \
                 [--enc-kms "string"]                                      \
                 [--enc-s3 "string"]                                       \
                 [--enc-c "string"]                                        \
                 [--legal-hold "on"]                                       \
                 [--limit-download string]                                 \
                 [--limit-upload string]                                   \
                 [--md5]                                                   \
                 [--newer-than "string"]                                   \
                 [--older-than "string"]                                   \
                 [--preserve]                                              \
                 [--recursive]                                             \
                 [--retention-mode "string" --retention-duration "string"] \
                 [--rewind "string"]                                       \
                 [--storage-class "string"]                                \
                 [--tags "string"]                                         \
                 [--version-id "string"]                                   \
                 [--zip]                                                   \
                 SOURCE [SOURCE ...]                                       \
                 TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `SOURCE` {#mc.cp.SOURCE}

*mc-cmd*

*Required*

要复制的对象。

如需从 MinIO 复制对象，请指定该对象的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整路径 （例如存储桶和对象路径）。 例如：

```text
mc cp play/mybucket/object.txt ~/mydata/object.txt
```

指定多个 `SOURCE` 路径可将多个对象复制到指定的 [`TARGET`](#mc.cp.TARGET)。 [`mc cp`](#command-mc.cp) 将最后一个指定的 alias 或文件系统路径视为 `TARGET`。 例如：

```text
mc cp ~/data/object.txt myminio/mydata/object.txt play/mydata/
```

如需从本地文件系统复制对象，请指定该对象的完整路径。 例如：

```text
mc cp ~/mydata/object.txt play/mybucket/object.txt
```

如果在 [`SOURCE`](#mc.cp.SOURCE) 中指定的是目录或存储桶， 还必须指定 [`--recursive`](#mc.cp.-recursive) 以递归复制该目录或存储桶中的内容。 如果省略 `--recursive` 参数，[`cp`](#command-mc.cp) 仅复制指定目录或存储桶顶层中的对象。

##### `TARGET` {#mc.cp.TARGET}

*mc-cmd*

*Required*

[`mc cp`](#command-mc.cp) 复制对象的目标完整路径。

如需将对象复制到 MinIO， 请指定该对象的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 和完整路径 （例如存储桶和对象路径）。例如：

```text
mc cp ~/mydata/object.txt play/mybucket/object.txt
```

如需将对象复制到本地文件系统，请指定该对象的完整 路径。例如：

```text
mc cp play/mybucket/object.txt ~/mydata/object.txt
```

##### `--attr` {#mc.cp.-attr}

*mc-cmd*

*Optional*

为对象添加自定义元数据。 以 `KEY=VALUE\;` 格式指定键值对。 例如，`--attr key1=value1\;key2=value2\;key3=value3`。

##### `--checksum` {#mc.cp.-checksum}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-10-02T08-27-28Z**

为上传对象添加校验和。

有效值包括： - `MD5` - `CRC32` - `CRC32C` - `SHA1` - `SHA256`

该标志依赖服务端 trailing headers，适用于 AWS 或 MinIO 目标。

##### `--disable-multipart` {#mc.cp.-disable-multipart}

*mc-cmd*

*Optional*

为本次复制会话禁用分片上传。

##### `--enc-kms` {#mc.cp.-enc-kms}

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

##### `--enc-s3` {#mc.cp.-enc-s3}

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

##### `--enc-c` {#mc.cp.-enc-c}

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

##### `--legal-hold` {#mc.cp.-legal-hold}

*mc-cmd*

*Optional*

为复制后的对象启用无限期的 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 对象锁定。

指定 `on`。

##### `--limit-download` {#mc.cp.-limit-download}

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

##### `--limit-upload` {#mc.cp.-limit-upload}

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

##### `--md5` {#mc.cp.-md5}

*mc-cmd*

*Optional*

> [!NOTE]
> **变更: RELEASE.2024-10-02T08-27-28Z**
>
> 已由 [`--checksum`](#mc.cp.-checksum) 标志替代。

强制所有上传计算 MD5 校验和。

##### `--newer-than` {#mc.cp.-newer-than}

*mc-cmd*

*Optional*

复制比指定天数更新的对象。 以 `#d#hh#mm#ss` 格式指定字符串。 例如：`--older-than 1d2hh3mm4ss`

默认为 `0`（所有对象）。

##### `--older-than` {#mc.cp.-older-than}

*mc-cmd*

*Optional*

复制早于指定时间限制的对象。 以 `#d#hh#mm#ss` 格式指定字符串。 例如：`--older-than 1d2hh3mm4ss`

默认为 `0`（所有对象）。

##### `--preserve, a` {#mc.cp.-preserve}

*mc-cmd*

*Optional*

在 [`TARGET`](#mc.cp.TARGET) 存储桶中保留来自 [`SOURCE`](#mc.cp.SOURCE) 目录、存储桶和对象的文件系统属性及存储桶策略规则。

##### `--recursive, r` {#mc.cp.-recursive}

*mc-cmd*

*Optional*

将每个 [`SOURCE`](#mc.cp.SOURCE) 存储桶或目录中的内容递归复制到 [`TARGET`](#mc.cp.TARGET) 存储桶。

##### `--retention-duration` {#mc.cp.-retention-duration}

*mc-cmd*

*Optional*

要应用于复制对象的 [WORM retention mode](/docs/administration/object-management/object-retention/#minio-object-locking-retention-modes) 持续时间。

以 `#d#hh#mm#ss` 格式的字符串指定持续时间。 例如：`--retention-duration "1d2hh3mm4ss"`。

需要同时指定 [`--retention-mode`](#mc.cp.-retention-mode)。

##### `--retention-mode` {#mc.cp.-retention-mode}

*mc-cmd*

*Optional*

在复制对象上启用 [object locking mode](/docs/administration/object-management/object-retention/#minio-object-locking-retention-modes)。 支持以下取值：

- `GOVERNANCE`
- `COMPLIANCE`

需要同时指定 [`--retention-duration`](#mc.cp.-retention-duration)。

##### `--rewind` {#mc.cp.-rewind}

*mc-cmd*

*Optional*

指示 [`mc cp`](#command-mc.cp) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.cp.-rewind) 要求指定的 [`SOURCE`](#mc.cp.SOURCE) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--storage-class, sc` {#mc.cp.-storage-class}

*mc-cmd*

*Optional*

为 [`TARGET`](#mc.cp.TARGET) 上的新对象设置存储类。

有关 S3 存储类的更多信息，请参见 [https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

##### `--tags` {#mc.cp.-tags}

*mc-cmd*

*Optional*

为复制后的对象应用一个或多个标签。

以 `KEY1=VALUE1&KEY2=VALUE2` 形式指定由与号分隔的键值对， 其中每一对代表分配给对象的一个标签。

##### `--version-id, vid` {#mc.cp.-version-id}

*mc-cmd*

*Optional*

指示 [`mc cp`](#command-mc.cp) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.cp.-version-id) 要求指定的 [`SOURCE`](#mc.cp.SOURCE) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--zip` {#mc.cp.-zip}

*mc-cmd*

*Optional*

在复制期间，从 *.zip* 归档中提取文件。 仅当源归档文件位于 MinIO 部署中时生效。

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id9}

### 将对象复制到 S3 {#s3}

使用 [`mc cp`](#command-mc.cp) 将对象复制到 S3 兼容主机：

{{< tabs group="s3-s3-s3" >}}
{{< tab label="文件系统到 S3" value="s3" >}}
```shell
mc cp SOURCE ALIAS/PATH
```

- 将 [`SOURCE`](#mc.cp.SOURCE) 替换为对象的文件系统路径。
- 将 [`ALIAS`](#mc.cp.TARGET) 替换为已配置的 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cp.TARGET) 替换为 S3 兼容主机上的对象路径。 你可以指定不同的对象名称，以便在复制时“重命名”对象。
{{< /tab >}}
{{< tab label="S3 到 S3" value="s3-s3" >}}
```shell
mc cp SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`SRCALIAS`](#mc.cp.SOURCE) 替换为源 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.cp.SOURCE) 替换为 S3 兼容主机上对象的路径。
- 将 [`TGTALIAS`](#mc.cp.TARGET) 替换为目标 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.cp.TARGET) 替换为目标 S3 兼容主机上对象的路径。 省略对象名称可使用 `SRCPATH` 的对象名称。
{{< /tab >}}
{{< /tabs >}}

### 递归复制对象到 S3 {#id10}

使用 [`mc cp --recursive`](#mc.cp.-recursive) 将对象递归复制到 S3 兼容主机：

{{< tabs group="s3-s3-s3" >}}
{{< tab label="文件系统到 S3" value="s3" >}}
```shell
mc cp --recursive SOURCE ALIAS/PATH
```

- 将 [`SOURCE`](#mc.cp.SOURCE) 替换为包含文件的目录路径。
- 将 [`ALIAS`](#mc.cp.TARGET) 替换为已配置的 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.cp.TARGET) 替换为 S3 兼容主机上的对象路径。 [`mc cp`](#command-mc.cp) 在目标主机创建对象时会使用 `SOURCE` 的文件名。
{{< /tab >}}
{{< tab label="S3 到 S3" value="s3-s3" >}}
```shell
mc cp --recursive SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`SRCALIAS`](#mc.cp.SOURCE) 替换为源 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.cp.SOURCE) 替换为源 S3 兼容主机上的 存储桶或存储桶前缀路径。
- 将 [`TGTALIAS`](#mc.cp.TARGET) 替换为目标 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.cp.TARGET) 替换为目标 S3 兼容主机上的对象路径。 [`mc cp`](#command-mc.cp) 在目标主机创建对象时会使用 `SRCPATH` 的对象名称。
{{< /tab >}}
{{< /tabs >}}

### 复制对象的时间点版本 {#id11}

使用 [`mc cp --rewind`](#mc.cp.-rewind) 复制对象在某个特定时间点的状态。 该命令仅适用于 S3 到 S3 复制。

```shell
mc cp --rewind DURATION SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`DURATION`](#mc.cp.-rewind) 替换为要回溯复制对象的过去时间点。 例如，指定 `30d` 可复制当前日期前 30 天的对象版本。
- 将 [`SRCALIAS`](#mc.cp.SOURCE) 替换为源 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.cp.SOURCE) 替换为源 S3 兼容主机上对象的路径。
- 将 [`TGTALIAS`](#mc.cp.TARGET) 替换为目标 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.cp.TARGET) 替换为目标 S3 兼容主机上对象的路径。 省略对象名称可使用 `SRCPATH` 的对象名称。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc cp`](#command-mc.cp) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 复制对象的特定版本 {#id12}

使用 [`mc cp --version-id`](#mc.cp.-version-id) 复制对象的特定版本。 该命令仅适用于 S3 到 S3 复制。

```shell
mc cp --version-id VERSION SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`VERSION`](#mc.cp.-rewind) 替换为要复制的对象版本。
- 将 [`SRCALIAS`](#mc.cp.SOURCE) 替换为源 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.cp.SOURCE) 替换为源 S3 兼容主机上对象的路径。
- 将 [`TGTALIAS`](#mc.cp.TARGET) 替换为目标 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.cp.TARGET) 替换为目标 S3 兼容主机上对象的路径。 省略对象名称可使用 `SRCPATH` 的对象名称。

> [!NOTE]
> **需要版本控制**
>
> 要使用此功能，[`mc cp`](#command-mc.cp) 需要启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 在存储桶上启用版本控制。

### 添加 `content-type` 值 {#content-type}

使用 [`mc cp --attr`](#mc.cp.-attr) 添加 `content-type` 值。 该命令仅适用于 S3 到 S3 复制。

```shell
mc cp --attr="content-type=CONTENT-TYPE" SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 `CONTENT-TYPE` 替换为所需的 content type（也称为 [media type](https://www.iana.org/assignments/media-types/media-types.xhtml)）。
- 将 [`SRCALIAS`](#mc.cp.SOURCE) 替换为源 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.cp.SOURCE) 替换为源 S3 兼容主机上对象的路径。
- 将 [`TGTALIAS`](#mc.cp.TARGET) 替换为目标 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.cp.TARGET) 替换为目标 S3 兼容主机上对象的路径。 省略对象名称可使用 `SRCPATH` 的对象名称。

以下示例将 `content-type` 设置为 `application/json`：

```text
 mc cp data.ndjson --attr="content-type=application/json" myminio/mybucket
```

## 行为 {#id13}

[`mc cp`](#command-mc.cp) 使用 MD5SUM 校验和验证所有到对象存储的复制操作。

### S3 兼容性 {#id14}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。