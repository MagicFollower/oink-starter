---
title: "mc find"

weight: 110
---

<a id="mc-find"></a>
<a id="minio-mc-find"></a>

<a id="command-mc.find"></a>

## 语法 {#id2}

[`mc find`](#command-mc.find) 命令支持在 MinIO 部署上搜索对象。 你也可以使用该命令在文件系统上搜索文件。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令会在 `myminio` MinIO 部署的 `mydata` 存储桶中， 搜索所有匹配指定模式的对象：

```shell
mc find myminio/mydata --name "*.jpg"
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] find                    \
                 [--exec "string"]       \
                 [--ignore "string"]     \
                 [--larger "string"]     \
                 [--maxdepth "string"]   \
                 [--metadata "string"]   \
                 [--name "string"]       \
                 [--newer-than "string"] \
                 [--older-than "string"] \
                 [--path "string"]       \
                 [--print "string"]      \
                 [--regex "string"]      \
                 [--smaller "string"]    \
                 [--tags "string"]`      \
                 [--versions]            \
                 [--watch]               \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.find.ALIAS}

*mc-cmd*

*Required*

对于 MinIO 或 S3 兼容主机上的对象，指定 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整搜索路径（例如存储桶与前缀）。 例如：

```text
mc find play/mydata/
```

对于文件系统上的对象，指定要搜索的完整路径。 例如：

```shell
mc find ~/mydata/
```

执行 [`mc find ALIAS`](#mc.find.ALIAS) 且不带其他参数时，会返回指定路径下 *所有* 对象或文件的列表，行为类似 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls)。

##### `--exec` {#mc.find.-exec}

*mc-cmd*

*Optional*

对 [`mc find`](#command-mc.find) 返回的每个对象启动一个外部进程。 支持对输出进行 [替换格式化](#mc-find-substitution-format)。

##### `--ignore` {#mc.find.-ignore}

*mc-cmd*

*Optional*

排除名称匹配指定 [通配符模式](/docs/reference/minio-mc/#minio-wildcard-matching) 的对象。

##### `--larger` {#mc.find.-larger}

*mc-cmd*

*Optional*

匹配所有大于指定大小的对象，大小单位见 [units](#mc-find-units)。

##### `--maxdepth` {#mc.find.-maxdepth}

*mc-cmd*

*Optional*

将目录遍历限制为指定深度。

##### `--metadata` {#mc.find.-metadata}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-04-12T02-21-51Z

**仅用于 MinIO 部署。**

返回元数据匹配指定 `key=value` 的对象。 使用格式 `--metadata="KEY=value"`。

你可以传入值为空的 key。 在这种情况下，`mc find` 会匹配不包含该元数据 key 的对象，或该元数据 key 的值为空的对象。

你可以多次使用该选项，以匹配更多元数据 key。 要返回对象，该对象必须在所有元数据 key 上都匹配。

##### `--name` {#mc.find.-name}

*mc-cmd*

*Optional*

返回名称匹配指定 [通配符模式](/docs/reference/minio-mc/#minio-wildcard-matching) 的对象。

##### `--newer-than` {#mc.find.-newer-than}

*mc-cmd*

*Optional*

匹配晚于指定天数的对象。 指定 `#d#hh#mm#ss` 格式的字符串。 例如：`--older-than 1d2hh3mm4ss`

> [!NOTE]
> **变更: RELEASE.2025-02-04T04-57-50Z**
>
> 日期时间也可以使用 `YYYY-MM-DD HH:MM:SS TMZ` 格式的绝对时间指定。 例如，`mc find --newer-than="2025-01-22 09:57:00 CET" minioalias/mybucket`。

##### `--older-than` {#mc.find.-older-than}

*mc-cmd*

*Optional*

匹配早于指定时间限制的对象。指定 `#d#hh#mm#ss` 格式的字符串。 例如：`--older-than 1d2hh3mm4ss`

> [!NOTE]
> **变更: RELEASE.2025-02-04T04-57-50Z**
>
> 日期时间也可以使用 `YYYY-MM-DD HH:MM:SS TMZ` 格式的绝对时间指定。 例如，`mc find --newer-than="2025-01-22 09:57:00 CET" minioalias/mybucket`。

默认为 `0`（所有对象）。

##### `--path` {#mc.find.-path}

*mc-cmd*

*Optional*

返回名称匹配指定 [通配符模式](/docs/reference/minio-mc/#minio-wildcard-matching) 的目录内容。

##### `--print` {#mc.find.-print}

*mc-cmd*

*Optional*

将结果打印到 `STDOUT`。 支持对输出进行 [替换格式化](#mc-find-substitution-format)。

##### `--regex` {#mc.find.-regex}

*mc-cmd*

*Optional*

返回名称匹配指定 PCRE 正则表达式模式的对象 或目录内容。

##### `--tags` {#mc.find.-tags}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-04-12T02-21-51Z

**仅用于 MinIO 部署。**

返回标签匹配指定 [RE2 RegEx pattern](https://github.com/google/re2/wiki/Syntax) 的对象。 使用格式 `--tag="KEY=regexValue"`。

你可以传入值为空的 key。 在这种情况下，`mc find` 会匹配不包含该元数据 key 的对象，或该元数据 key 的值为空的对象。

你可以多次使用该选项，以匹配更多标签。 要返回对象，该对象必须在所有标签上都匹配。

##### `--smaller` {#mc.find.-smaller}

*mc-cmd*

*Optional*

匹配所有小于指定大小的对象， 大小单位见 [units](#mc-find-units)。

##### `--versions` {#mc.find.-versions}

*mc-cmd*

*Optional*

在结果中包含对象的所有版本。

##### `--watch` {#mc.find.-watch}

*mc-cmd*

*Optional*

持续监控 [`ALIAS`](#mc.find.ALIAS)，并返回任何 匹配指定条件的新对象。

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id7}

### 在存储桶中查找特定对象 {#id8}

```shell
mc find ALIAS/PATH --name NAME
```

- 将 [`ALIAS`](#mc.find.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.find.ALIAS) 替换为 S3 兼容主机上的存储桶路径。 省略该路径可从 S3 主机根路径开始搜索。
- 将 [`NAME`](#mc.find.-name) 替换为对象。

### 在存储桶中按文件扩展名查找对象 {#id9}

```shell
mc find ALIAS/PATH --name *.EXTENSION
```

- 将 [`ALIAS`](#mc.find.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.find.ALIAS) 替换为 S3 兼容主机上的存储桶路径。
- 将 [`EXTENSION`](#mc.find.-name) 替换为对象的文件扩展名。

### 查找所有匹配文件并复制到 S3 服务 {#s3}

将 [`mc find`](#command-mc.find) 与 [`--exec`](#mc.find.-exec) 选项结合使用，可在本地文件系统中查找 文件，并将其传递给 **`mc`** 命令进行进一步处理。以下示例使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 将 [`mc find`](#command-mc.find) 的输出复制到 S3 兼容主机。

```shell
mc find FILEPATH --name "*.EXTENSION" --exec "mc cp {} ALIAS/PATH"
```

- 将 [`FILEPATH`](#mc.find.ALIAS) 替换为要搜索目录的 完整文件路径。
- 将 [`EXTENSION`](#mc.find.-name) 替换为对象的文件扩展名。
- 将 [`ALIAS`](#mc.find.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.find.ALIAS) 替换为 S3 兼容主机上的存储桶路径。

如需持续监视指定目录并复制新对象， 请添加 [`--watch`](#mc.find.-watch) 参数：

```shell
mc find --watch FILEPATH --name "*.EXTENSION" --exec "mc cp {} ALIAS/PATH"
```

### 查找具有匹配标签的对象 {#id10}

> [!NOTE]
> **说明**
>
> 标签匹配仅适用于 MinIO 部署。

```shell
mc find --tags="key=v*" ALIAS/BUCKET/
```

- 将 `key` 替换为要匹配的标签键名。
- 将 `v*` 替换为要用于匹配的 RE2 正则表达式。
- 将 `ALIAS` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `BUCKET` 替换为要搜索的存储桶或前缀。

你可以添加更多 `--tags="key=RegExpression"` 标志进行匹配。 匹配对象必须满足所有包含的标签条件。

### 查找具有匹配元数据的对象 {#id11}

> [!NOTE]
> **说明**
>
> 元数据匹配仅适用于 MinIO 部署。

```shell
mc find --json --metadata="content-type=text/csv" ALIAS/BUCKET/
```

- 将 `content-type=text/csv` 替换为要匹配的元数据字段和值的键值对。
- 将 `ALIAS` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `BUCKET` 替换为要搜索的存储桶或前缀。

你可以添加更多 `--tags="metadata=value"` 标志进行匹配。 匹配对象必须满足所有包含的元数据字段条件。

## 行为 {#id12}

<a id="id13"></a>

### 计量单位 {#mc-find-units}

[`mc find --smaller`](#mc.find.-smaller) 和 [`mc find --larger`](#mc.find.-larger) 标志 接受以下不区分大小写的后缀，用于表示指定大小值的单位：

| 后缀 | 单位大小 |
| --- | --- |
| `k` | KB（千字节，1000 字节） |
| `m` | MB（兆字节，1000 千字节） |
| `g` | GB（吉字节，1000 兆字节） |
| `t` | TB（太字节，1000 吉字节） |
| `ki` | KiB（Kibibyte，1024 字节） |
| `mi` | MiB（Mebibyte，1024 Kibibytes） |
| `gi` | GiB（Gibibyte，1024 Mebibytes） |
| `ti` | TiB（Tebibyte，1024 Gibibytes） |

省略后缀时默认单位为 `bytes`。

<a id="id14"></a>

### 替换格式 {#mc-find-substitution-format}

[`mc find --exec`](#mc.find.-exec) 和 [`mc find --print`](#mc.find.-print) 命令 支持字符串替换，对以下关键字具有特殊解释。

以下关键字同时适用于文件系统和 S3 服务目标：

- `{}` - 替换为完整路径。
- `{base}` - 替换为路径的 basename。
- `{dir}` - 替换为路径的 dirname。
- `{size}` - 替换为路径对应对象的大小。
- `{time}` - 替换为路径对应对象的修改时间。

以下关键字仅适用于 S3 服务目标：

- `{url}` - 替换为路径的可共享 URL。

### S3 兼容性 {#id15}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。