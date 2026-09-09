---
title: "mc legalhold clear"

weight: 10
---

<a id="mc-legalhold-clear"></a>
<a id="minio-mc-legalhold-clear"></a>

<a id="command-mc.legalhold.clear"></a>

## 语法 {#id1}

[`mc legalhold clear`](#command-mc.legalhold.clear) 命令会移除一个或多个对象当前的 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 设置。

移除对象的 legal hold *不会* 移除对象上已有的其他 [GOVERNANCE 模式](/docs/administration/object-management/object-retention/#minio-object-locking-governance) 和 [COMPLIANCE 模式](/docs/administration/object-management/object-retention/#minio-object-locking-compliance) 保留设置。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令会移除 `myminio` MinIO 部署中 `mydata` 存储桶内 所有对象的 legal hold：

```shell
mc legalhold clear --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] legalhold clear \
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

##### `ALIAS` {#mc.legalhold.clear.ALIAS}

*mc-cmd*

*Required*

MinIO [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及要移除 legal hold 的对象路径（可为单个或多个对象）。例如：

```shell
mc legalhold clear play/mybucket/myobjects/objects.txt
```

##### `--recursive, r` {#mc.legalhold.clear.-recursive}

*mc-cmd*

*Optional*

移除 [`ALIAS`](#mc.legalhold.clear.ALIAS) 指定存储桶或存储桶前缀下 所有对象的 legal hold。

##### `--rewind` {#mc.legalhold.clear.-rewind}

*mc-cmd*

*Optional*

指示 [`mc legalhold clear`](#command-mc.legalhold.clear) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.legalhold.clear.-rewind) 要求指定的 [`ALIAS`](#mc.legalhold.clear.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, vid` {#mc.legalhold.clear.-version-id}

*mc-cmd*

*Optional*

指示 [`mc legalhold clear`](#command-mc.legalhold.clear) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.legalhold.clear.-version-id) 要求指定的 [`ALIAS`](#mc.legalhold.clear.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 获取对象的 Legal Hold 状态 {#legal-hold}

使用 [`mc legalhold clear`](#command-mc.legalhold.clear) 获取对象的 legal hold 状态。 包含 [`--recursive`](#mc.legalhold.clear.-recursive) 可返回存储桶内容的 legal hold 状态：

```shell
mc legalhold clear [--recursive] ALIAS/PATH
```

- 将 [`ALIAS`](#mc.legalhold.clear.ALIAS) 替换为 S3 兼容主机的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.legalhold.clear.ALIAS) 替换为 S3 兼容主机上的 存储桶或对象路径。若指定的是存储桶或存储桶前缀路径，请包含 [`--recursive`](#mc.legalhold.clear.-recursive) 选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。