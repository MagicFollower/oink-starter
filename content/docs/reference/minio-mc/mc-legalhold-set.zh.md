---
title: "mc legalhold set"

weight: 30
---

<a id="mc-legalhold-set"></a>
<a id="minio-mc-legalhold-set"></a>

<a id="command-mc.legalhold.set"></a>

## 语法 {#id2}

[`mc legalhold set`](#command-mc.legalhold.set) 命令可在单个或多个对象上启用 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 的一次写入多次读取（WORM）对象锁定。

[`mc legalhold`](/docs/reference/minio-mc/mc-legalhold/#command-mc.legalhold) *要求* 指定的存储桶已 [启用对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking)。你 **只能** 在创建存储桶时启用对象锁定。 有关创建已启用对象锁定的存储桶，请参见 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock) 文档。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` MinIO 部署中，对 `mydata` 存储桶内所有现有对象启用 legalhold WORM 锁定：

```shell
mc legalhold set --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] legalhold set  \
                 [--recursive]  \
                 [--rewind]     \
                 [--version-id] \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.legalhold.set.ALIAS}

*mc-cmd*

*Required*

MinIO [别名](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要启用 legal hold 的对象路径（可为单个或多个对象）。 例如：

```shell
mc legalhold set play/mybucket/myobjects/objects.txt
```

##### `--recursive, r` {#mc.legalhold.set.-recursive}

*mc-cmd*

*Optional*

将 legal hold 应用于 [`ALIAS`](#mc.legalhold.set.ALIAS) 指定存储桶或存储桶前缀下的 所有现有对象。

> [!NOTE]
> **`--recursive` 仅作用于现有对象**
>
> 若要为后续新建对象启用 legal hold，请在有新对象创建后周期性重复执行 [`mc legalhold`](/docs/reference/minio-mc/mc-legalhold/#command-mc.legalhold) 命令。

##### `--rewind` {#mc.legalhold.set.-rewind}

*mc-cmd*

*Optional*

指示 [`mc legalhold set`](#command-mc.legalhold.set) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.legalhold.set.-rewind) 要求指定的 [`ALIAS`](#mc.legalhold.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, vid` {#mc.legalhold.set.-version-id}

*mc-cmd*

*Optional*

指示 [`mc legalhold set`](#command-mc.legalhold.set) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.legalhold.set.-version-id) 要求指定的 [`ALIAS`](#mc.legalhold.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

使用 [`mc legalhold set`](#command-mc.legalhold.set) 为对象启用 legal hold：

```shell
mc legalhold set [--recursive] ALIAS/PATH
```

- 将 [`ALIAS`](#mc.legalhold.set.ALIAS) 替换为 S3 兼容主机的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.legalhold.set.ALIAS) 替换为 S3 兼容主机上的存储桶或对象路径。 如果指定的是存储桶或存储桶前缀路径，请包含 [`--recursive`](#mc.legalhold.set.-recursive) 选项。

## 行为 {#id6}

### Legal Hold 需要显式移除 {#legal-hold}

Legal hold 没有期限，并会对被锁定对象强制执行完全不可变。 只有具备 [`s3:PutObjectLegalHold`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutObjectLegalHold) 权限的特权用户才能设置或解除 legal hold。

### Legal Hold 与其他保留模式互补 {#id7}

Legal hold 与 [GOVERNANCE 模式](/docs/administration/object-management/object-retention/#minio-object-locking-governance) 和 [COMPLIANCE 模式](/docs/administration/object-management/object-retention/#minio-object-locking-compliance) 保留设置互补。若对象同时受 legal hold 和 `GOVERNANCE/COMPLIANCE` 保留规则约束，则在 legal hold 被解除且规则到期之前， 该对象会一直保持 WORM 锁定。

对于 `GOVERNANCE` 锁定对象，legal hold 会阻止对象被修改， *即使* 用户具备绕过保留策略所需的权限也是如此。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。