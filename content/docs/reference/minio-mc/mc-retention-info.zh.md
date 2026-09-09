---
title: "mc retention info"

weight: 20
---

<a id="mc-retention-info"></a>

<a id="command-mc.retention.info"></a>

## 语法 {#id2}

[`mc retention info`](#command-mc.retention.info) 命令用于为对象或存储桶中的对象配置 [Write-Once Read-Many (WORM) locking](/docs/administration/object-management/object-retention/#minio-object-locking) 设置。 你还可以为存储桶设置默认对象锁定设置，未显式配置对象锁定的对象会继承该存储桶默认值。

如需基于 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 锁定对象， 请使用 [`mc legalhold set`](/docs/reference/minio-mc/mc-legalhold-set/#command-mc.legalhold.set)。

[`mc retention info`](#command-mc.retention.info) *要求* 指定存储桶已启用对象锁定。 你 **只能** 在创建存储桶时启用对象锁定。有关创建启用对象锁定的存储桶，请参见 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock) 文档。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回 `myminio` MinIO 部署中 `mydata` 存储桶的默认对象锁定配置：

```shell
mc retention info --default myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] retention info            \
                 [--default]               \
                 [--recursive]             \
                 [--rewind "string"]       \
                 [--version-id "string"]*  \
                 [--versions]              \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc retention info --version-id`](#mc.retention.info.-version-id) 与多个其他参数互斥。 更多信息请参见参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.retention.info.ALIAS}

*mc-cmd*

*Required*

要检索对象锁定配置的对象完整路径。 将已配置的 S3 兼容服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 `ALIAS` 存储桶路径前缀。 例如：

```shell
mc retention info play/mybucket/object.txt
```

- **如果 `ALIAS` 指定的是存储桶或存储桶前缀，请添加**

  > [`--recursive`](#mc.retention.info.-recursive)，以返回该存储桶或前缀下所有对象的对象锁定设置。
- **如果 `ALIAS` 存储桶已启用版本控制，**

  > [`mc retention info`](#command-mc.retention.info) 默认仅作用于对象的最新版本。 使用 [`--version-id`](#mc.retention.info.-version-id) 或 [`--versions`](#mc.retention.info.-versions) 可返回特定版本或对象全部版本的对象锁定设置。

##### `--default` {#mc.retention.info.-default}

*mc-cmd*

*Optional*

返回 [`ALIAS`](#mc.retention.info.ALIAS) 指定存储桶的默认对象锁定设置。

如果指定 [`--default`](#mc.retention.info.-default)， [`mc retention info`](#command-mc.retention.info) 会忽略所有其他标志。

##### `--recursive, r` {#mc.retention.info.-recursive}

*mc-cmd*

*Optional*

递归返回指定 [`ALIAS`](#mc.retention.info.ALIAS) 路径下所有对象的对象锁定设置。

与 [`--version-id`](#mc.retention.info.-version-id) 互斥。

##### `--rewind` {#mc.retention.info.-rewind}

*mc-cmd*

*Optional*

指示 [`mc retention info`](#command-mc.retention.info) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.retention.info.-rewind) 要求指定的 [`ALIAS`](#mc.retention.info.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, vid` {#mc.retention.info.-version-id}

*mc-cmd*

*Optional*

指示 [`mc retention info`](#command-mc.retention.info) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.retention.info.-version-id) 要求指定的 [`ALIAS`](#mc.retention.info.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下任一标志互斥：

- [`--versions`](#mc.retention.info.-versions)
- [`--rewind`](#mc.retention.info.-rewind)
- [`--recursive`](#mc.retention.info.-recursive)

##### `--versions` {#mc.retention.info.-versions}

*mc-cmd*

*Optional*

指示 [`mc retention info`](#command-mc.retention.info) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.retention.info.-versions) 要求指定的 [`ALIAS`](#mc.retention.info.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

同时使用 [`--versions`](#mc.retention.info.-versions) 和 [`--rewind`](#mc.retention.info.-rewind)，可检索某个特定时间点存在的所有对象版本的 保留设置。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 检索单个或多个对象的对象锁定设置 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="指定对象" value="tab1" >}}
```shell
mc retention info ALIAS/PATH
```

- 将 [`ALIAS`](#mc.retention.info.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.info.ALIAS) 替换为对象路径。
{{< /tab >}}
{{< tab label="多个对象" value="tab2" >}}
将 [`mc retention info`](#command-mc.retention.info) 与 [`--recursive`](#mc.retention.info.-recursive) 一起使用，以检索存储桶中所有对象的保留设置：

```shell
mc retention info --recursive ALIAS/PATH
```

- 将 [`ALIAS`](#mc.retention.info.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.info.ALIAS) 替换为存储桶路径。
{{< /tab >}}
{{< /tabs >}}

> 要使用此命令，存储桶 *必须* 启用对象锁定。 只能在创建存储桶时启用对象锁定。有关创建已启用对象锁定的存储桶的更多信息， 请参阅 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock)。

### 检索存储桶的默认对象锁定设置 {#id7}

将 [`mc retention info`](#command-mc.retention.info) 与 [`--default`](#mc.retention.info.-default) 一起使用，以检索存储桶的默认对象锁定设置：

```shell
mc retention info --default ALIAS/PATH
```

- **将 [`ALIAS`](#mc.retention.info.ALIAS) 替换为已配置 S3 兼容主机的**

  > [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.info.ALIAS) 替换为存储桶路径。

> 要使用此命令，存储桶 *必须* 启用对象锁定。 只能在创建存储桶时启用对象锁定。有关创建已启用对象锁定的存储桶的更多信息， 请参阅 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock)。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。