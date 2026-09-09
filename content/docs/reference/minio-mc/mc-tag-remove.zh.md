---
title: "mc tag remove"

weight: 30
---

<a id="mc-tag-remove"></a>
<a id="minio-mc-tag-remove"></a>

<a id="command-mc.tag.remove"></a>

## 语法 {#id1}

[`mc tag remove`](#command-mc.tag.remove) 命令用于移除存储桶或对象上的所有标签。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会移除 `myminio` MinIO 部署中 `mydata` 存储桶的标签：

```shell
mc tag remove myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] tag remove                \
                 [--rewind "string"]       \
                 [--versions]              \
                 [--version-id "string"]*  \
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc tag remove --version-id`](#mc.tag.remove.-version-id) 与多个参数互斥。有关更多信息，请参阅参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.tag.remove.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要移除全部标签的对象完整路径 （例如存储桶和对象路径）。例如：

```text
mc tag remove myminio/mybucket/object.txt
```

##### `--recursive, r` {#mc.tag.remove.-recursive}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-04T18-10-16Z**

递归移除指定 [`ALIAS`](#mc.tag.remove.ALIAS) 下所有对象的全部标签。

##### `--rewind` {#mc.tag.remove.-rewind}

*mc-cmd*

*Optional*

指示 [`mc tag remove`](#command-mc.tag.remove) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.tag.remove.-rewind) 要求指定的 [`ALIAS`](#mc.tag.remove.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--versions` {#mc.tag.remove.-versions}

*mc-cmd*

*Optional*

指示 [`mc tag remove`](#command-mc.tag.remove) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.tag.remove.-versions) 要求指定的 [`ALIAS`](#mc.tag.remove.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

结合使用 [`--versions`](#mc.tag.remove.-versions) 和 [`--rewind`](#mc.tag.remove.-rewind)，可移除某个特定时间点存在的所有对象版本上的标签。

##### `--version-id, vid` {#mc.tag.remove.-version-id}

*mc-cmd*

*Optional*

指示 [`mc tag remove`](#command-mc.tag.remove) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.tag.remove.-version-id) 要求指定的 [`ALIAS`](#mc.tag.remove.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下参数互斥：

- [`--rewind`](#mc.tag.remove.-rewind)
- [`--versions`](#mc.tag.remove.-versions)

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 移除存储桶或对象上的标签 {#id5}

使用 [`mc tag remove`](#command-mc.tag.remove) 移除存储桶或对象上的标签：

```shell
mc tag remove ALIAS/PATH
```

- 将 [`ALIAS`](#mc.tag.remove.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.tag.remove.ALIAS) 替换为 MinIO 部署中存储桶 或对象的路径。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。