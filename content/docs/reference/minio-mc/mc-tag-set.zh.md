---
title: "mc tag set"

weight: 10
---

<a id="mc-tag-set"></a>
<a id="minio-mc-tag-set"></a>

<a id="command-mc.tag.set"></a>

## 语法 {#id2}

[`mc tag set`](#command-mc.tag.set) 命令可为存储桶或对象设置一个或多个标签。

MinIO 支持为对象最多添加 10 个自定义标签。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` MinIO 部署中的 `mydata` 存储桶设置标签：

```shell
mc tag set myminio/mydata "tag1=value1&tag2=value2"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] tag set                   \
                 [--rewind "string"]       \
                 [--versions]              \
                 [--version-id "string"]*  \
                 ALIAS                     \
                 "TAGS"
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc tag set --version-id`](#mc.tag.set.-version-id) 与多个参数互斥。更多信息请参阅参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.tag.set.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要应用标签的对象完整路径（例如存储桶和对象路径）。例如：

```text
mc tag set myminio/mybucket/object.txt
```

##### `TAGS` {#mc.tag.set.TAGS}

*mc-cmd*

*Required*

使用与号（`&`）分隔的键值对（`KEY=VALUE`）列表，其中每一对表示要分配给对象的一个标签。例如：

```text
mc tag set myminio/mybucket/object.txt "key1=value1&key2=value2"
```

##### `--exclude-folders` {#mc.tag.set.-exclude-folders}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-01-11T05-49-32Z**

与 [`--recursive`](#mc.tag.set.-recursive) 一起使用时，[`mc tag set`](#command-mc.tag.set) 将 **不会** 遍历子前缀。 标签仅应用于指定路径下的对象。 需要 [`--recursive`](#mc.tag.set.-recursive)。

以下示例将 `destination=international` 标签应用到 `vacation-photos/cancun/` 下的对象，但不应用到 `vacation-photos/cancun/ocean/` 或其他前缀。

例如，上述命令会将标签添加到 `vacation-photos/cancun/pretty-beach.jpg`，但不会添加到 `vacation-photos/cancun/ocean/tropical-fish.jpg`。

```shell
mc tag set myminio/vacation-photos/cancun "destination=international" --exclude-folders --recursive
```

##### `--recursive, r` {#mc.tag.set.-recursive}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-04T18-10-16Z**

递归地将标签应用到 [`ALIAS`](#mc.tag.set.ALIAS) 指定路径下的所有对象。

##### `--rewind` {#mc.tag.set.-rewind}

*mc-cmd*

*Optional*

指示 [`mc tag set`](#command-mc.tag.set) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.tag.set.-rewind) 要求指定的 [`ALIAS`](#mc.tag.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--versions` {#mc.tag.set.-versions}

*mc-cmd*

*Optional*

指示 [`mc tag set`](#command-mc.tag.set) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.tag.set.-versions) 要求指定的 [`ALIAS`](#mc.tag.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.tag.set.-versions) 与 [`--rewind`](#mc.tag.set.-rewind) 一起使用，可将标签应用到某个特定时间点存在的所有对象版本。

##### `--version-id, --vid` {#mc.tag.set.-version-id}

*mc-cmd*

*Optional*

指示 [`mc tag set`](#command-mc.tag.set) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.tag.set.-version-id) 要求指定的 [`ALIAS`](#mc.tag.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下参数互斥：

- [`--rewind`](#mc.tag.set.-rewind)
- [`--versions`](#mc.tag.set.-versions)

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 将标签应用到存储桶或对象 {#id6}

使用 [`mc tag set`](#command-mc.tag.set) 将标签应用到存储桶或对象：

```shell
mc tag set ALIAS/PATH "TAGS"
```

- 将 [`ALIAS`](#mc.tag.set.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.tag.set.ALIAS) 替换为 MinIO 部署中存储桶 或对象的路径。
- 将 [`TAGS`](#mc.tag.set.TAGS) 替换为一个或多个用与号分隔（`&`）的键值对， 每个键值对表示一个标签及其对应值。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。