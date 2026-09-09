---
title: "mc stat"

weight: 370
---

<a id="mc-stat"></a>

<a id="command-mc.stat"></a>

## 语法 {#id2}

[`mc stat`](#command-mc.stat) 命令用于显示 MinIO 存储桶中对象的信息，包括对象元数据。 你也可以使用它来检索存储桶元数据。

你可以对本地文件系统使用 [`mc stat`](#command-mc.stat)，以获得与 `stat` 命令行工具类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 `myminio` MinIO 部署中 `mydata` 存储桶内所有对象的信息：

```shell
mc stat --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] stat                      \
                 [--enc-c "value"]         \
                 [--no-list]               \
                 [--recursive]             \
                 [--rewind "string"]       \
                 [--versions]              \
                 [--version-id "string"]*  \
                 ALIAS [ALIAS ...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc stat --version-id`](#mc.stat.-version-id) 与多个参数互斥。更多信息请参阅参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.stat.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要检索详细信息的对象完整路径。例如：

```shell
mc stat myminio/mybucket/myobject.txt
```

你可以在同一个或不同的 MinIO 部署上指定多个对象：

```shell
mc stat myminio/mybucket/myobject.txt myminio/mybucket/myobject.txt
```

如果指定的是存储桶路径或存储桶前缀路径，则 **必须** 包含 [`mc stat --recursive`](#mc.stat.-recursive) 标志：

```shell
mc stat --recursive myminio/mybucket/
```

要检索本地文件系统中文件的信息，请指定该文件的完整路径：

```shell
mc stat ~/data/myobject.txt
```

##### `--enc-c` {#mc.stat.-enc-c}

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

##### `--no-list` {#mc.stat.-no-list}

*mc-cmd*

*Optional*

如果目标不存在，则禁用所有 `LIST` 操作。

##### `--recursive, r` {#mc.stat.-recursive}

*mc-cmd*

*Optional*

递归地对 [`ALIAS`](#mc.stat.ALIAS) 指定的 MinIO 存储桶内容执行 [`mc stat`](#command-mc.stat)。

##### `--rewind` {#mc.stat.-rewind}

*mc-cmd*

*Optional*

指示 [`mc stat`](#command-mc.stat) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.stat.-rewind) 要求指定的 [`ALIAS`](#mc.stat.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--versions` {#mc.stat.-versions}

*mc-cmd*

*Optional*

指示 [`mc stat`](#command-mc.stat) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.stat.-versions) 要求指定的 [`ALIAS`](#mc.stat.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.stat.-versions) 与 [`--rewind`](#mc.stat.-rewind) 一起使用，可移除某个特定时间点存在的所有对象版本。

##### `--version-id, vid` {#mc.stat.-version-id}

*mc-cmd*

*Optional*

指示 [`mc stat`](#command-mc.stat) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.stat.-version-id) 要求指定的 [`ALIAS`](#mc.stat.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下任一标志互斥：

- [`--versions`](#mc.stat.-versions)
- [`--rewind`](#mc.stat.-rewind)
- [`--recursive`](#mc.stat.-recursive)

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 显示对象详情 {#id6}

以下示例显示存储桶 `mybucket` 中对象 `myfile.txt` 的详细信息：

```shell
mc stat myminio/mybucket/myfile.txt
```

输出类似如下：

```shell
Name      : myfile.txt
Date      : 2024-07-16 15:40:02 MDT
Size      : 6.0 KiB
ETag      : 3b38f7b05a0c42acdc377e60b2a74ddf
Type      : file
Metadata  :
  Content-Type: text/plain
```

你可以通过添加多个路径来指定多个对象：

```shell
mc stat myminio/mybucket/file1.txt myminio/yourbucket/file2.txt
```

要显示存储桶中所有对象的详细信息，请使用 [`--recursive`](#mc.stat.-recursive)。 以下示例显示存储桶 `mybucket` 中所有对象的详细信息：

```shell
mc stat --recursive myminio/mybucket
```

输出类似如下：

```shell
Name      : file1.txt
Date      : 2024-07-16 15:40:02 MDT
Size      : 6.0 KiB
ETag      : 3b38f7b05a0c42acdc377e60b2a74ddf
Type      : file
Metadata  :
  Content-Type: text/plain

Name      : file2.txt
Date      : 2024-07-26 10:45:19 MDT
Size      : 6.0 KiB
ETag      : 3b38f7b05a0c42acdc377e60b2a74ddf
Type      : file
Metadata  :
  Content-Type: text/plain
```

### 显示存储桶详情 {#id7}

以下示例显示 `myminio` MinIO 部署上存储桶 `mybucket` 的信息：

```shell
mc stat myminio/mybucket
```

输出类似如下：

```shell
Name      : mybucket
Date      : 2024-07-26 10:56:43 MDT
Size      : N/A
Type      : folder

Properties:
  Versioning: Un-versioned
  Location: us-east-1
  Anonymous: Disabled
  ILM: Disabled

Usage:
      Total size: 6.0 KiB
   Objects count: 1
  Versions count: 0

Object sizes histogram:
   1 object(s) BETWEEN_1024B_AND_1_MB
   1 object(s) BETWEEN_1024_B_AND_64_KB
   0 object(s) BETWEEN_10_MB_AND_64_MB
   0 object(s) BETWEEN_128_MB_AND_512_MB
   0 object(s) BETWEEN_1_MB_AND_10_MB
   0 object(s) BETWEEN_256_KB_AND_512_KB
   0 object(s) BETWEEN_512_KB_AND_1_MB
   0 object(s) BETWEEN_64_KB_AND_256_KB
   0 object(s) BETWEEN_64_MB_AND_128_MB
   0 object(s) GREATER_THAN_512_MB
   0 object(s) LESS_THAN_1024_B
```

### 存储桶中的对象数量 {#id8}

要显示存储桶中的对象数量，请使用 `--json` 并通过 JSON 解析器提取 `objectsCount` 的值：

以下示例使用 [jq](https://jqlang.github.io/jq/) 工具：

```shell
mc stat myminio/mybucket --json | jq '.Usage.objectsCount'
```

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。