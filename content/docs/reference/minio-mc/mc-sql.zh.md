---
title: "mc sql"

weight: 360
---

<a id="mc-sql"></a>

<a id="command-mc.sql"></a>

## 语法 {#id2}

[`mc sql`](#command-mc.sql) 命令提供 S3 Select 接口，用于对指定 MinIO 部署中的对象执行 SQL 查询。

有关 S3 Select 的行为和限制，请参阅 [Selecting content from objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/selecting-content-from-objects)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会查询 `myminio` MinIO 部署中 `mydata` 存储桶内的所有对象：

```shell
mc sql --recursive --query "select * from S3Object" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] mc sql                          \
                 --query "string"                \
                 [--csv-input "string"]          \
                 [--compression "string"]        \
                 [--csv-output "string"]         \
                 [--csv-output-header "string"]  \
                 [--enc-c "string"]              \
                 [--json-input "string"]         \
                 [--json-output "string"]        \
                 [--recursive]                   \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.sql.ALIAS}

*mc-cmd*

*Required*

要执行 SQL 查询的存储桶或对象的完整路径。 指定已配置 S3 服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 `ALIAS` 路径前缀。 例如：

```shell
mc sql [FLAGS] play/mybucket
```

##### `--query, e` {#mc.sql.-query}

*mc-cmd*

*Required*

在指定 [`ALIAS`](#mc.sql.ALIAS) 目录或对象上执行的 SQL 语句。 将完整 SQL 查询用双引号 `"` 包裹。

默认为 `"select * from S3Object"`。

##### `--csv-input` {#mc.sql.-csv-input}

*mc-cmd*

*Optional*

`.csv` 输入对象的数据格式。 指定由逗号分隔的 `key=value,...` 键值对字符串。 有效键的更多信息请参阅 [CSV 格式字段](#mc-sql-csv-format)。

##### `--compression` {#mc.sql.-compression}

*mc-cmd*

*Optional*

输入对象的压缩类型。 指定以下受支持值之一：

- `GZIP`
- `BZIP2`
- `NONE`（默认）

仅 MinIO 后端支持以下压缩方案：

- `ZSTD` [Zstandard](https://facebook.github.io/zstd/)
- `LZ4` [LZ4](https://lz4.github.io/lz4/) 流
- `S2` [S2](https://github.com/klauspost/compress/tree/master/s2#s2-compression) 帧流
- `SNAPPY` [Snappy](http://google.github.io/snappy/) 帧流

##### `--csv-output` {#mc.sql.-csv-output}

*mc-cmd*

*Optional*

`.csv` 输出的数据格式。 指定由逗号分隔的 `key=value,...` 键值对字符串。 有效键的更多信息请参阅 [CSV 格式字段](#mc-sql-csv-format)。

更多信息请参阅 S3 API [CSVOutput](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CSVOutput.html)。

##### `--csv-output-header` {#mc.sql.-csv-output-header}

*mc-cmd*

*Optional*

`.csv` 输出文件的表头行。 将逗号分隔的字段字符串指定为 `field1,field2,...`。

省略该参数则输出不包含表头行的 `.csv`。

##### `--enc-c` {#mc.sql.-enc-c}

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

##### `--json-input` {#mc.sql.-json-input}

*mc-cmd*

*Optional*

`.json` 或 `.ndjson` 输入对象的数据格式。 将 JSON 内容类型指定为 `type=<VALUE>`。 值可以是：

- `DOCUMENT` - JSON [document](https://www.json.org/json-en.html)。
- `LINES` - JSON [lines](http://jsonlines.org/)。

更多信息请参阅 S3 API [JSONInput](https://docs.aws.amazon.com/AmazonS3/latest/API/API_JSONInput.html)。

##### `--json-output` {#mc.sql.-json-output}

*mc-cmd*

*Optional*

`.json` 输出的数据格式。 支持 `rd=value` 键，其中 `rd` 是 JSON 文档的 `RecordDelimiter`。

省略该参数则使用默认换行符 `\n`。

更多信息请参阅 S3 API [JSONOutput](https://docs.aws.amazon.com/AmazonS3/latest/API/API_JSONOutput.html)。

##### `--recursive, r` {#mc.sql.-recursive}

*mc-cmd*

*Optional*

使用 [`--query`](#mc.sql.-query) SQL 语句递归搜索指定的 [`ALIAS`](#mc.sql.ALIAS) 目录。

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id7}

### 选择存储桶内所有对象的所有列 {#id8}

将 [`mc sql`](#command-mc.sql) 与 [`--recursive`](#mc.sql.-recursive) 和 [`--query`](#mc.sql.-query) 选项结合使用，可将查询应用到存储桶中的所有对象：

```shell
mc sql --recursive --query "select * from S3Object" ALIAS/PATH
```

- 将 [`ALIAS`](#mc.sql.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.sql.ALIAS) 替换为 MinIO 部署上存储桶的路径。

### 在对象上运行聚合查询 {#id9}

将 [`mc sql`](#command-mc.sql) 与 [`--query`](#mc.sql.-query) 选项结合使用，可查询 MinIO 部署上的对象：

```shell
mc sql --query "select count(s.power) from S3Object" ALIAS/PATH
```

- 将 [`ALIAS`](#mc.sql.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.sql.ALIAS) 替换为 MinIO 部署上对象的路径。

## 行为 {#id10}

### 输入格式 {#id11}

[`mc sql`](#command-mc.sql) 支持以下输入格式：

| 类型 | `content-type` 值 |
| --- | --- |
| `.csv` | `text/csv` |
| `.json` | `application/json` |
| `.parquet` | 无 |

对于 `.csv` 文件类型，使用 [`mc sql --csv-input`](#mc.sql.-csv-input) 指定 CSV 数据格式。 有关 CSV 格式字段的更多信息，请参阅 [CSV 格式字段](#mc-sql-csv-format)。

对于 `.json` 文件类型，使用 [`mc sql --json-input`](#mc.sql.-json-input) 指定 JSON 数据格式。

对于 `.parquet` 文件类型，[`mc sql`](#command-mc.sql) 会自动解析数据格式。

[`mc sql`](#command-mc.sql) 通过目标对象的文件扩展名判断类型。 例如，名为 `data.json` 的对象会被解释为 JSON 文件。

如果对象具有合适的 `content-type`，你也可以查询受支持类型但扩展名不同的数据。 更多信息请参阅 [`mc cp --attr`](/docs/reference/minio-mc/mc-cp/#mc.cp.-attr)。

<a id="mc-sql-csv-format"></a>

### CSV 格式字段 {#csv}

下表列出了可用于 [`mc sql --csv-input`](#mc.sql.-csv-input) 和 [`mc sql --csv-output`](#mc.sql.-csv-output) 的有效键值对。 某些键值对仅适用于 [`--csv-input`](#mc.sql.-csv-input)。 有关 S3 CSV 格式的更多信息，请参阅 S3 API [CSVInput](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CSVInput.html) 文档。

<table>
  <thead>
    <tr>
      <th><p>键</p></th>
      <th><p>仅 <code>--csv-input</code></p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>rd</code></p></td>
      <td></td>
      <td><p>用于分隔输入 <code>.csv</code> 文件中每条记录（行）的字符。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>RecordDelimiter</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>fd</code></p></td>
      <td></td>
      <td><p>用于分隔一条记录中各字段的字符。默认为 <code>,</code>。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>FieldDelimeter</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>qc</code></p></td>
      <td></td>
      <td><p>当 <code>fd</code> 字符是字段值的一部分时，用于转义的字符。默认为 <code>&quot;</code>。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>QuoteCharacter</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>qec</code></p></td>
      <td></td>
      <td><p>在已转义值内部，用于转义引号 <code>&quot;</code> 字符的字符。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>QuoteEscapeCharacter</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>fh</code></p></td>
      <td><p>是</p></td>
      <td><p><code>.csv</code> 文件第一行的内容类型。</p><p>指定以下受支持值之一：</p><ul><li><p><code>NONE</code> - 第一行不是表头。</p></li><li><p><code>IGNORE</code> - 忽略第一行。</p></li><li><p><code>USE</code> - 第一行是表头。</p></li></ul><p>对于 <code>NONE</code> 或 <code>IGNORE</code>，你必须在 <a href="#mc.sql.-query"><code>--query</code></a> 语句中指定列位置 <code>_#</code> 来标识列。</p><p>对于 <code>USE</code>，你可以在 <a href="#mc.sql.-query"><code>--query</code></a> 语句中指定表头值来标识列。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>FieldHeaderInfo</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>cc</code></p></td>
      <td><p>是</p></td>
      <td><p>用于指示应忽略某条记录的字符。
该字符 <em>必须</em> 出现在记录开头。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>Comment</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>qrd</code></p></td>
      <td><p>是</p></td>
      <td><p>指定 <code>TRUE</code> 表示字段中可以包含记录分隔符值（<code>rd</code>）。</p><p>默认为 <code>FALSE</code>。</p><p>对应 S3 API <code>CSVInput</code> 中的 <code>AllowQuotedRecordDelimiter</code>。</p></td>
    </tr>
  </tbody>
</table>

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。