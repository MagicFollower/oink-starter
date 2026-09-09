---
title: "mc legalhold info"

weight: 20
---

<a id="mc-legalhold-info"></a>
<a id="minio-mc-legalhold-info"></a>

<a id="command-mc.legalhold.info"></a>

## 语法 {#id1}

[`mc legalhold info`](#command-mc.legalhold.info) 命令返回一个或多个对象的当前 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 设置。

[`mc legalhold`](/docs/reference/minio-mc/mc-legalhold/#command-mc.legalhold) *要求* 指定的存储桶已启用对象锁定。 你 **只能** 在创建存储桶时启用对象锁定。有关创建启用对象锁定的存储桶，请参阅 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock) 文档。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令检索 `myminio` MinIO 部署中 `mydata` 存储桶内对象的当前 legal hold 状态：

```shell
mc legalhold info --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] legalhold info  \
                 [--recursive]   \
                 [--rewind]      \
                 [--version-id]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.legalhold.info.ALIAS}

*mc-cmd*

*Required*

MinIO [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及要为其启用 legal hold 的对象路径（或多个对象路径）。例如：

```shell
mc legalhold info play/mybucket/myobjects/objects.txt
```

##### `--recursive, r` {#mc.legalhold.info.-recursive}

*mc-cmd*

*Optional*

返回 [`ALIAS`](#mc.legalhold.info.ALIAS) 中存储桶或存储桶前缀下全部对象的 legal hold 状态。

##### `--rewind` {#mc.legalhold.info.-rewind}

*mc-cmd*

*Optional*

指示 [`mc legalhold info`](#command-mc.legalhold.info) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.legalhold.info.-rewind) 要求指定的 [`ALIAS`](#mc.legalhold.info.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, vid` {#mc.legalhold.info.-version-id}

*mc-cmd*

*Optional*

指示 [`mc legalhold info`](#command-mc.legalhold.info) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.legalhold.info.-version-id) 要求指定的 [`ALIAS`](#mc.legalhold.info.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

### 全局参数 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 获取对象的 Legal Hold 状态 {#legal-hold}

使用 [`mc legalhold info`](#command-mc.legalhold.info) 获取对象的 legal hold 状态。 添加 [`--recursive`](#mc.legalhold.info.-recursive) 以返回存储桶内容的 legal hold 状态：

```shell
mc legalhold clear [--recursive] ALIAS/PATH
```

- 将 [`ALIAS`](#mc.legalhold.info.ALIAS) 替换为 S3 兼容主机的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.legalhold.info.ALIAS) 替换为 S3 兼容主机上的存储桶或对象路径。 如果指定的是存储桶路径或存储桶前缀，请包含 [`--recursive`](#mc.legalhold.info.-recursive) 选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。