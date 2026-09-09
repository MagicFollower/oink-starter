---
title: "mc mirror"

weight: 240
---

<a id="mc-mirror"></a>

<a id="command-mc.mirror"></a>

## 语法 {#id2}

[`mc mirror`](#command-mc.mirror) 命令用于将内容同步到 MinIO 部署，类似于 `rsync` 工具。 [`mc mirror`](#command-mc.mirror) 支持以文件系统、MinIO 部署和其他 S3 兼容主机作为同步源。

> [!NOTE]
> **说明**
>
> [`mc mirror`](#command-mc.mirror) 仅同步当前对象，不包含任何版本信息或元数据。 若要同步对象的版本历史和元数据，可考虑对 [bucket replication](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 使用 [`mc replicate`](/docs/reference/minio-mc/mc-replicate/#command-mc.replicate)，或对 [site replication](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview) 使用 [`mc admin replicate`](/docs/reference/minio-mc-admin/mc-admin-replicate/#command-mc.admin.replicate)。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令将本地文件系统目录中的内容同步到 `myminio` MinIO 部署上的 `mydata` 存储桶。

```shell
mc mirror --watch ~/mydata myminio/mydata
```

该命令会“监视”本地文件系统中新增或删除的文件，并将这些操作同步到 MinIO，直到显式终止。

[`mc mirror --watch`](#mc.mirror.-watch) 会把本地文件系统中发生变更的文件更新到 MinIO（参见 [`--overwrite`](#mc.mirror.-overwrite)）。 `--watch` 不会删除 MinIO 中本地文件系统不存在的其他文件（参见 [`--remove`](#mc.mirror.-remove)）。
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] mirror                            \
                 [--active-active]                 \
                 [--attr "string"]                 \
                 [--checksum "value"]              \
                 [--disable-multipart]             \
                 [--dry-run]                       \
                 [--enc-kms "string"]              \
                 [--enc-s3 "string"]               \
                 [--enc-c "string"]                \
                 [--exclude "string"]              \
                 [--exclude-bucket "string"]       \
                 [--exclude-storageclass "string"] \
                 [--limit-download string]         \
                 [--limit-upload string]           \
                 [--md5]                           \
                 [--monitoring-address "string"]   \
                 [--newer-than "string"]           \
                 [--older-than "string"]           \
                 [--overwrite]                     \
                 [--preserve]                      \
                 [--region "string"]               \
                 [--remove]                        \
                 [--retry]                         \
                 [--skip-errors]                   \
                 [--storage-class "string"]        \
                 [--summary]                       \
                 [--watch]                         \
                 SOURCE                            \
                 TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `SOURCE` {#mc.mirror.SOURCE}

*mc-cmd*

*Required*

要同步到 [`TARGET`](#mc.mirror.TARGET) S3 主机的文件或对象。

对于 S3 兼容主机上的对象，请将对象路径指定为 `ALIAS/PATH`，其中：

- `ALIAS` 是已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，*并且*
- `PATH` 是存储桶或对象路径。若指定存储桶，[`mc mirror`](#command-mc.mirror) 会同步该存储桶中的所有对象。

```shell
mc mirror [FLAGS] play/mybucket/ myminio/mybucket
```

对于文件系统中的文件，请指定文件或目录的完整文件系统路径：

```shell
mc mirror [FLAGS] ~/data/ myminio/mybucket
```

若指定的是目录，[`mc mirror`](#command-mc.mirror) 会同步该目录中的所有文件。

##### `TARGET` {#mc.mirror.TARGET}

*mc-cmd*

*Required*

[`mc mirror`](#command-mc.mirror) 用于同步 SOURCE 对象的目标存储桶完整路径。将 `TARGET` 指定为 `ALIAS/PATH`，其中：

- `ALIAS` 是已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，*并且*
- `PATH` 是存储桶路径。

```shell
mc mirror SOURCE play/mybucket
```

[`mc mirror`](#command-mc.mirror) 在同步到 `TARGET` 存储桶时，会使用 [`SOURCE`](#mc.mirror.SOURCE) 中对象或文件的名称。

##### `--active-active` {#mc.mirror.-active-active}

*mc-cmd*

*Optional*

在两个站点之间建立 active-active 镜像活动。 必须在每个站点上重复执行该命令。

例如：

在站点 A 上，将 A 镜像到 B

```text
mc mirror --active-active siteA siteB
```

在站点 B 上，将 B 镜像到 A

```text
mc mirror --active-active siteB siteA
```

##### `--attr` {#mc.mirror.-attr}

*mc-cmd*

*Optional*

为镜像对象添加自定义元数据。将键值对指定为 `KEY=VALUE\;`。 例如：`--attr key1=value1\;key2=value2\;key3=value3`。

##### `--checksum` {#mc.mirror.-checksum}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-10-02T08-27-28Z**

为上传对象添加校验和。

有效值为： - `MD5` - `CRC32` - `CRC32C` - `SHA1` - `SHA256`

该标志要求服务端支持 trailing headers，并适用于 AWS 或 MinIO 目标。

##### `--disable-multipart` {#mc.mirror.-disable-multipart}

*mc-cmd*

*Optional*

为本次同步会话禁用 multipart 上传。

##### `--dry-run` {#mc.mirror.-dry-run}

*mc-cmd*

*Optional*

执行一次模拟镜像操作。 使用该操作可测试 [`mc mirror`](#command-mc.mirror) 是否只会镜像预期的对象或存储桶。

##### `--enc-kms` {#mc.mirror.-enc-kms}

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

##### `--enc-s3` {#mc.mirror.-enc-s3}

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

##### `--enc-c` {#mc.mirror.-enc-c}

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

##### `--exclude` {#mc.mirror.-exclude}

*mc-cmd*

*Optional*

排除 [`SOURCE`](#mc.mirror.SOURCE) 路径中与指定对象 [name pattern](/docs/reference/minio-mc/#minio-wildcard-matching) 匹配的对象。

##### `--exclude-bucket` {#mc.mirror.-exclude-bucket}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-03-03T00-13-08Z

排除 [`SOURCE`](#mc.mirror.SOURCE) 路径中与指定存储桶 [name pattern](/docs/reference/minio-mc/#minio-wildcard-matching) 匹配的存储桶。

##### `--exclude-storageclass` {#mc.mirror.-exclude-storageclass}

*mc-cmd*

*Optional*

排除 [`SOURCE`](#mc.mirror.SOURCE) 上具有指定存储类的对象。 可在同一命令中多次使用该标志，以排除多个存储类中的对象。

可用于排除需要重新水化或恢复的存储类对象，例如从 AWS S3 存储桶迁移时，某些对象使用 `GLACIER` 或 `DEEP_ARCHIVE` 存储类。

##### `--limit-download` {#mc.mirror.-limit-download}

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

##### `--limit-upload` {#mc.mirror.-limit-upload}

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

##### `--md5` {#mc.mirror.-md5}

*mc-cmd*

*Optional*

强制所有上传计算 MD5 校验和。

##### `--monitoring-address` {#mc.mirror.-monitoring-address}

*mc-cmd*

*Optional*

创建一个用于监控镜像活动的 [Prometheus](https://prometheus.io/) endpoint。 指定创建抓取 endpoint 的本地网络适配器和端口地址。 默认为 `localhost:8081`)。

##### `--newer-than` {#mc.mirror.-newer-than}

*mc-cmd*

*Optional*

仅镜像比指定天数更新的对象。 以 `#d#hh#mm#ss` 格式指定字符串 例如：`--newer-than 1d2hh3mm4ss`。

##### `--older-than` {#mc.mirror.-older-than}

*mc-cmd*

*Optional*

仅镜像早于指定时间阈值的对象。 以 `#d#hh#mm#ss` 格式指定字符串。 例如：`--older-than 1d2hh3mm4ss`。

默认为 `0`（所有对象）。

##### `--overwrite` {#mc.mirror.-overwrite}

*mc-cmd*

*Optional*

覆盖 [`TARGET`](#mc.mirror.TARGET) 上的对象。

例如，设想一个正在运行的 `mc mirror --overwrite`，将内容从 Source 同步到 Destination。

如果 Source 上的对象发生变更，`mc mirror --overwrite` 会同步并覆盖 Destination 上的同名文件。

如果不使用 `--overwrite`，当对象已存在于 Destination 时，镜像进程将无法同步该对象。 `mc mirror` 会记录错误并继续同步其他对象。

##### `--preserve, a` {#mc.mirror.-preserve}

*mc-cmd*

*Optional*

在 [`TARGET`](#mc.mirror.TARGET) 上保留 [`SOURCE`](#mc.mirror.SOURCE) 的文件系统属性和存储桶策略规则。

##### `--region` {#mc.mirror.-region}

*mc-cmd*

*Optional*

在目标端创建新存储桶时，指定 `string` 区域。

默认为 `"us-east-1"`。

##### `--remove` {#mc.mirror.-remove}

*mc-cmd*

*Optional*

删除 Target 上 Source 中不存在的对象。

使用 `--remove` 标志可使 Source 和 Target 拥有相同的对象列表。

例如，Source 上存在对象 A、B、C。 Target 上存在对象 C、D、E。

运行 `mc mirror --remove` 时，对象 A 和 B 会同步到 Target，对象 D 和 E 会从 Target 删除。 由于对象 C 在两端都已存在，不会有任何内容从 Source 移动到 Target。

操作完成后，Source 和 Target 上都只存在对象 A、B、C。

`mc mirror --remove` 不会校验对象 C 在 Source 和 Target 上的内容是否一致，只检查两端是否都存在名为 *C* 的对象。 若要确保 Source 与 Target 上对象的名称和内容都一致，请使用 [`--overwrite`](#mc.mirror.-overwrite) 或 [`--watch`](#mc.mirror.-watch)。

> [!NOTE]
> **变更: RELEASE.2023-05-04T18-10-16Z**
>
> 如果目标路径是不存在的本地文件系统目录，`mc mirror --remove` 会返回错误。
>
> 在早期版本中，如果 `directory` 不存在，指定 `/path/to/directory` 会导致删除 `/path/to` 文件夹。

##### `--retry` {#mc.mirror.-retry}

*mc-cmd*

*Optional*

镜像过程中出现错误时，对每个出错对象执行重试。

##### `--storage-class, sc` {#mc.mirror.-storage-class}

*mc-cmd*

*Optional*

为 [`TARGET`](#mc.mirror.TARGET) 上的新对象设置存储类。

有关 S3 存储类的更多信息，请参阅 Amazon 文档：[Storage Classes](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-class-intro.html)。

##### `--skip-errors` {#mc.mirror.-skip-errors}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-01-28T16-23-14Z

跳过镜像过程中产生错误的对象。

##### `--summary` {#mc.mirror.-summary}

*mc-cmd*

*Optional*

完成后输出已同步数据的摘要。

##### `--watch, w` {#mc.mirror.-watch}

*mc-cmd*

*Optional*

使用 `--watch` 标志可将对象从 Source 镜像到 Target，且 Target 也可以包含 Source 中不存在的其他对象。

- `--watch` 会持续将文件从 Source 同步到 Target，直到显式终止
- Target 可以包含 Source 中不存在的文件
- 若 Source 中存在同名对象，`--watch` 会覆盖 Target 上的对象，行为类似 [`--overwrite`](#mc.mirror.-overwrite)

默认为 `0`（所有对象）。

例如，被监视的 Source 上存在对象 A 和 B。 被监视的 Target 上存在对象 A、B、C。

某客户端向 Source 写入对象 D，并删除对象 B。

操作后，Source 上存在对象 A 和 D。 Target 上存在对象 A、C、D。

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id9}

### 将本地目录镜像到 S3 兼容主机 {#s3}

使用 [`mc mirror`](#command-mc.mirror) 将文件从文件系统镜像到 S3 主机：

```text
mc mirror FILEPATH ALIAS/PATH
```

- 将 [`FILEPATH`](#mc.mirror.SOURCE) 替换为要镜像目录的完整文件路径。
- 将 [`ALIAS`](#mc.mirror.TARGET) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.mirror.TARGET) 替换为目标存储桶。

### 持续将本地目录镜像到 S3 兼容主机 {#id10}

将 [`mc mirror`](#command-mc.mirror) 与 [`--watch`](#mc.mirror.-watch) 一起使用，可持续将文件从文件系统镜像到 S3 兼容主机；文件系统中新增或删除的对象会在主机端同步新增或删除：

```text
mc mirror --watch FILEPATH ALIAS/PATH
```

- 将 [`FILEPATH`](#mc.mirror.SOURCE) 替换为要镜像目录的完整文件路径。
- 将 [`ALIAS`](#mc.mirror.TARGET) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.mirror.TARGET) 替换为目标存储桶。

### 持续将 S3 存储桶镜像到 S3 兼容主机 {#s3-s3}

将 [`mc mirror`](#command-mc.mirror) 与 [`--watch`](#mc.mirror.-watch) 一起使用，可持续将一个 S3 兼容主机上某个存储桶中的对象镜像到另一个 S3 兼容主机；存储桶中新增或删除的对象会同步到目标主机。

```text
mc mirror --watch SRCALIAS/SRCPATH TGTALIAS/TGTPATH
```

- 将 [`SRCALIAS`](#mc.mirror.SOURCE) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.mirror.SOURCE) 替换为要镜像的存储桶。
- 将 [`TGTALIAS`](#mc.mirror.TARGET) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.mirror.TARGET) 替换为目标存储桶。

### 将对象从 AWS S3 镜像到 MinIO，并跳过 GLACIER 中的对象 {#aws-s3-minio-glacier}

将 [`mc mirror`](#command-mc.mirror) 与 [`--exclude-storageclass`](#mc.mirror.-exclude-storageclass) 一起使用，可将对象从 AWS S3 镜像到 MinIO，同时不镜像 GLACIER 或 DEEP_ARCHIVE 存储中的对象。

```text
mc mirror --exclude-storageclass GLACIER  \
   --exclude-storageclass DEEP_ARCHIVE SRCALIAS/SRCPATH TGALIAS/TGPATH
```

- 将 [`SRCALIAS`](#mc.mirror.SOURCE) 替换为已配置 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`SRCPATH`](#mc.mirror.SOURCE) 替换为要镜像的存储桶。
- 将 [`TGTALIAS`](#mc.mirror.TARGET) 替换为已配置 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TGTPATH`](#mc.mirror.TARGET) 替换为目标存储桶。

## 行为 {#id11}

### 对象失败时镜像继续执行 {#id12}

如果目标上存在同名对象，MinIO 会为重复对象输出错误。 发生错误后，`mc mirror` 会继续将其他对象从源端镜像到目标端。

### 对象删除时 MinIO 会裁剪空前缀 {#minio}

[`mc mirror --watch`](#mc.mirror.-watch) 命令会持续同步源端和目标端中新增与删除的对象。 这也包括在源端删除对象时，自动删除目标端对应对象。

如需将源端更新的对象同步更新到目标端，请使用 *–overwrite*。 如需删除目标端中源端不存在的对象，请使用 *–remove*。

[`mc mirror --watch`](#mc.mirror.-watch) 依赖 [`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 来移除对象。在删除存储桶前缀中的最后一个对象时， [`mc`](/docs/reference/minio-mc/#command-mc) 还会递归删除直到存储桶根为止的每一个空前缀。[`mc`](/docs/reference/minio-mc/#command-mc) 只会对在对象写入 操作过程中 *隐式* 创建的前缀执行这种递归删除，也就是说，该前缀不是通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 这类显式目录创建命令创建的。

例如，假设存储桶 `photos` 中有以下对象前缀：

- `photos/2021/january/myphoto.jpg`
- `photos/2021/february/myotherphoto.jpg`
- `photos/NYE21/NewYears.jpg`

`photos/NYE21` 是 *唯一* 通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 显式创建的前缀。其余所有前缀 都是在向该前缀写入对象时 *隐式* 创建的。

如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `myphoto.jpg`，删除 API 会自动裁剪空的 `/january` 前缀。如果后续某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令又删除了 `myotherphoto.jpg`， 删除 API 会自动裁剪 `/february` 前缀，以及此时已经为空的 `/2021` 前缀。 如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `NewYears.jpg`，由于 `/NYE21` 是 *显式* 创建的，因此该前缀会保留不变。

如果将 [`mc mirror --watch`](#mc.mirror.-watch) 用于文件系统操作，[`mc`](/docs/reference/minio-mc/#command-mc) 也会采用相同行为，递归裁剪直到 根目录的所有空目录。不过，[`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 无法区分某个目录路径是显式 创建的，还是隐式创建的。如果 [`mc mirror --watch`](#mc.mirror.-watch) 删除了某个文件系统路径上的最后一个对象， [`mc`](/docs/reference/minio-mc/#command-mc) 会在删除过程中递归删除从该路径向上直到根目录的所有空目录。

### S3 兼容性 {#id13}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。