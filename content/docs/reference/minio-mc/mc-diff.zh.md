---
title: "mc diff"

weight: 70
---

<a id="mc-diff"></a>
<a id="minio-mc-diff"></a>

<a id="command-mc.diff"></a>

## 语法 {#id2}

[`mc diff`](#command-mc.diff) 命令用于计算两个文件系统目录或 MinIO 存储桶之间的差异。 [`mc diff`](#command-mc.diff) 仅列出缺失的对象或大小不同的对象。[`mc diff`](#command-mc.diff) **不会** 比较对象内容。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令用于比较本地文件系统中的一个对象与 `myminio` MinIO 部署中 `mydata` 存储桶内一个对象之间的差异：

```shell
mc diff ~/mydata/myobject.txt myminio/mydata/myobject.txt
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc diff`](#command-mc.diff) 命令语法如下：

```shell
mc [GLOBALFLAGS] diff SOURCE TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id5}

##### `SOURCE` {#mc.diff.SOURCE}

*mc-cmd*

*必需* 要与 `TARGET` 比较的对象。

对于来自 MinIO 的对象， 指定 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 以及该对象的完整路径 （例如存储桶和对象路径）。例如：

```text
mc diff play/mybucket/object.txt ~/mydata/object.txt
```

对于来自本地文件系统的对象，指定该对象的完整路径。例如：

```text
mc diff ~/mydata/object.txt play/mybucket/object.txt
```

##### `TARGET` {#mc.diff.TARGET}

*mc-cmd*

*必需* 要与 `SOURCE` 比较的对象。

对于来自 MinIO 的对象， 指定 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 以及该对象的完整路径 （例如存储桶和对象路径）。例如：

```text
mc diff play/mybucket/object.txt ~/mydata/object.txt
```

对于来自本地文件系统的对象，指定该对象的完整路径。例如：

```text
mc diff ~/mydata/object.txt play/mybucket/object.txt
```

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id7}

以下示例假定 `play` 别名已存在于 [`mc`](/docs/reference/minio-mc/#command-mc) [配置文件](/docs/reference/minio-mc/#mc-configuration) 中。你可以将 `play` 替换为 你首选 S3 兼容部署的别名。

有关别名的更多信息，请参阅 [`mc alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

```shell
mc diff play/bucket1 play/bucket2
```

## 行为 {#id8}

### 输出图例 {#id9}

[`mc diff`](#command-mc.diff) 在格式化 diff 输出时使用以下图例：

```text
FIRST < SECOND - 对象仅存在于 FIRST
FIRST > SECOND - 对象仅存在于 SECOND
FIRST ! SECOND - FIRST 中存在较新的对象
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。