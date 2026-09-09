---
title: "mc put"

weight: 290
---

<a id="mc-put"></a>

<a id="command-mc.put"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-02-24T01-33-20Z

## 语法 {#id2}

[`mc put`](#command-mc.put) 将对象从本地文件系统上传到目标 S3 部署中的存储桶。

与 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 或 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror) 相比，`mc put` 为文件上传提供了更简化的接口。 `mc put` 使用单向上传机制，以牺牲效率为代价换取相较其他命令更低的复杂度。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例将本地文件系统路径 `~/images/collateral/` 下的文件 `logo.png` 上传到别名为 `minio` 的 MinIO 部署中名为 `marketing` 的存储桶。

```shell
mc put ~/images/collateral/logo.png minio/marketing
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] put                            \
                 TARGET                         \
                 [--checksum value]             \
                 [--disable-multipart]          \
                 [--enc-kms value]              \
                 [--enc-s3 value]               \
                 [--enc-c value]                \
                 [--if-not-exists]              \
                 [--parallel, -P integer]       \
                 [--part-size, -s string]       \
                 [--storage-class, -sc string]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.put.TARGET}

*mc-cmd*

*Required*

命令应执行位置的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或前缀的完整路径。 TARGET *必须* 包含 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和 `bucket` 名称。

TARGET 还可以包含以下可选组成部分： - 对象应上传到的 PREFIX - 用于替代文件名的 OBJECT-NAME

有效的 TARGET 可以采用以下任一形式： - `ALIAS/BUCKET` - `ALIAS/BUCKET/PREFIX` - `ALIAS/BUCKET/OBJECT-NAME` - `ALIAS/BUCKET/PREFIX/OBJECT-NAME`

##### `--checksum` {#mc.put.-checksum}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-10-02T08-27-28Z**

为上传对象添加校验和。

可选值包括： - `MD5` - `CRC32` - `CRC32C` - `SHA1` - `SHA256`

该标志需要服务器支持 trailing headers，并可用于 AWS 或 MinIO 目标。

##### `--disable-multipart` {#mc.put.-disable-multipart}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-10-02T08-27-28Z**

禁用分段上传，并指示 `mc` 通过单次 `PUT` 操作发送对象。

##### `--enc-kms` {#mc.put.-enc-kms}

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

##### `--enc-s3` {#mc.put.-enc-s3}

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

##### `--enc-c` {#mc.put.-enc-c}

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

##### `--parallel, --P` {#mc.put.-parallel}

*mc-cmd*

*Optional*

对于分段上传，指定对象分段并行上传的数量。

如未定义，默认值为 `4`。

##### `--part-size, -s` {#mc.put.-part-size}

*mc-cmd*

*Optional*

指定分段上传中每个分段使用的大小。

如未定义，默认值为 `16MiB`。

##### `--storage-class, -sc` {#mc.put.-storage-class}

*mc-cmd*

*Optional*

为上传对象设置存储类。

有关存储类的更多信息，请参见 [Standard Storage Class](/docs/reference/minio-server/settings/storage-class/#minio-ec-storage-class-standard)。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 上传文件并指定对象名称 {#id6}

以下命令将本地文件系统中的文件 `logo.png` 上传到 `minio` 部署的 `business` 存储桶，并在目标端命名为 `company-logo.png`。

```shell
mc put images/collateral/logo.png minio/business/company-logo.png
```

### 按指定分段大小并行上传分段对象 {#id7}

以下命令以每段 20MiB 的分块方式上传文件，并行上传其中 8 个分段。 系统会持续按批次上传 8 个分段，直到对象的所有分段均上传完成。

```shell
mc put ~/videos/collateral/splash-page.mp4 minio/business --parallel 8 --part-size 20MiB
```