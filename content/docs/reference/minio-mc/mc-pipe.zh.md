---
title: "mc pipe"

weight: 280
---

<a id="mc-pipe"></a>

<a id="command-mc.pipe"></a>

## 语法 {#id2}

[`mc pipe`](#command-mc.pipe) 命令将内容从 [STDIN](https://www.gnu.org/software/libc/manual/html_node/Standard-Streams.html) 流式传输到目标对象。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令将 `STDIN` 的内容写入 S3 兼容存储。

```shell
echo "My Meeting Notes" | mc pipe s3/engineering/meeting-notes.txt
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] pipe                              \
                 TARGET                            \
                 [--attr "string"]                 \
                 [--checksum "string"]             \
                 [--enc-kms "string"]              \
                 [--enc-s3 "string"]               \
                 [--enc-c "string"]                \
                 [--storage-class, --sc "string"]  \
                 [--tags "string"]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **变更: RELEASE.2023-01-11T03-14-16Z**
>
> `mc pipe` 现已支持并发上传，以提升大流式数据的吞吐量。

### 参数 {#id3}

##### `TARGET` {#mc.pipe.TARGET}

*mc-cmd*

*Required*

命令应运行的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或前缀完整路径。

##### `--attr` {#mc.pipe.-attr}

*mc-cmd*

*Optional*

为对象添加自定义元数据。

将键值对指定为 `KEY=VALUE\;`，每对之间用反斜杠加分号（`\;`）分隔。 例如：`--attr key1=value1\;key2=value2\;key3=value3`。

##### `--checksum` {#mc.pipe.-checksum}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-10-02T08-27-28Z**

为上传的对象添加校验和。

有效值为： - `MD5` - `CRC32` - `CRC32C` - `SHA1` - `SHA256`

该标志依赖服务器 trailing headers，并可用于 AWS 或 MinIO 目标。

##### `--enc-kms` {#mc.pipe.-enc-kms}

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

##### `--enc-s3` {#mc.pipe.-enc-s3}

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

##### `--enc-c` {#mc.pipe.-enc-c}

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

##### `--storage-class, --sc` {#mc.pipe.-storage-class}

*mc-cmd*

*Optional*

为 [`TARGET`](#mc.pipe.TARGET) 处的新对象设置存储类别。

关于 S3 存储类别的更多信息，请参见 [Amazon 文档](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

##### `--tags` {#mc.pipe.-tags}

*mc-cmd*

*Optional*

为 TARGET 应用一个或多个标签。

将键值对列表指定为 `KEY1=VALUE1&KEY2=VALUE2`，其中每一对表示分配给对象的一个标签。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 将 `STDIN` 内容写入本地文件系统 {#stdin}

以下命令将 STDIN 的内容写入本地文件系统中的 `/tmp` 文件夹。

```shell
mc pipe /tmp/hello-world.go
```

### 将 ISO 镜像复制到 S3 存储 {#iso-s3}

以下命令先流式读取 Debian 的 ISO 镜像内容，然后使用该数据流在 S3 路径创建对象。

```shell
cat debian-live-11.5.0-amd64-mate.iso | mc pipe s3/opensource-isos/debian-11-5.iso
```

### 将 MySQL 数据库转储流式传输到 S3 {#mysql-s3}

以下命令先流式传输 MySQL 数据库，再通过 [`mc pipe`](#command-mc.pipe) 使用该数据流在 S3 上创建备份：

```shell
mysqldump -u root -p ******* accountsdb | mc pipe s3/sql-backups/backups/accountsdb-sep-28-2022.sql
```

### 将文件写入 Reduced Redundancy 存储类别 {#reduced-redundancy}

以下命令读取 STDIN 数据流，并在 S3 的 Reduced Redundancy 存储类别中创建对象。

```shell
 mc pipe --storage-class REDUCED_REDUNDANCY s3/personalbuck/meeting-notes.txt
```

### 将文件连同元数据复制到 MinIO 部署 {#minio}

以下命令将 MP3 文件上传到 ALIAS 为 `myminio`、存储桶为 `music` 的 MinIO 部署。 写入对象时附带 `Cache-Control` 和 `Artist` 元数据。

```shell
cat music.mp3 | mc pipe --attr "Cache-Control=max-age=90000,min-fresh=9000;Artist=Unknown" myminio/music/guitar.mp3
```

### 为上传对象设置标签 {#id6}

以下命令在 ALIAS 为 `myminio` 的 MinIO 部署中，于 `mybucket` 存储桶创建一个带两个标签的对象。 MinIO 支持为对象最多添加 10 个自定义标签。

```shell
tar cvf - . | mc pipe --tags "category=prod&type=backup" myminio/mybucket/backup.tar
```