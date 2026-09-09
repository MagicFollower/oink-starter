---
title: "mc tag list"

weight: 20
---

<a id="mc-tag-list"></a>
<a id="minio-mc-tag-list"></a>

<a id="command-mc.tag.list"></a>

## 语法 {#id1}

[`mc tag list`](#command-mc.tag.list) 命令列出存储桶或对象上的所有标签。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶的标签：

```shell
mc tag list myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] tag set                   \
                 [--rewind "string"]       \
                 [--versions]              \
                 [--version-id "string"]*  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc tag list --version-id`](#mc.tag.list.-version-id) 与多个参数互斥。更多信息请参见参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.tag.list.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要列出全部标签的对象完整路径 （例如存储桶和对象路径）。例如：

```text
mc tag list myminio/mybucket/object.txt
```

##### `--recursive, r` {#mc.tag.list.-recursive}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-04T18-10-16Z**

递归列出 [`ALIAS`](#mc.tag.list.ALIAS) 指定路径下所有对象的标签。

##### `--rewind` {#mc.tag.list.-rewind}

*mc-cmd*

*Optional*

指示 [`mc tag list`](#command-mc.tag.list) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.tag.list.-rewind) 要求指定的 [`ALIAS`](#mc.tag.list.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--versions` {#mc.tag.list.-versions}

*mc-cmd*

*Optional*

指示 [`mc tag list`](#command-mc.tag.list) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.tag.list.-versions) 要求指定的 [`ALIAS`](#mc.tag.list.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.tag.list.-versions) 与 [`--rewind`](#mc.tag.list.-rewind) 组合使用，可列出特定时间点存在的 所有对象版本的标签。

##### `--version-id, vid` {#mc.tag.list.-version-id}

*mc-cmd*

*Optional*

指示 [`mc tag list`](#command-mc.tag.list) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.tag.list.-version-id) 要求指定的 [`ALIAS`](#mc.tag.list.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下参数互斥：

- [`--rewind`](#mc.tag.list.-rewind)
- [`--versions`](#mc.tag.list.-versions)

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 列出存储桶或对象的标签 {#id5}

使用 [`mc tag list`](#command-mc.tag.list) 列出存储桶或对象的标签：

```shell
mc tag list ALIAS/PATH
```

- 将 [`ALIAS`](#mc.tag.list.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.tag.list.ALIAS) 替换为 MinIO 部署中存储桶或对象的路径。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。