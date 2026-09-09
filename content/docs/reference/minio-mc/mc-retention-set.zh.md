---
title: "mc retention set"

weight: 10
---

<a id="mc-retention-set"></a>
<a id="minio-bucket-locking"></a>

<a id="command-mc.retention.set"></a>

## 语法 {#id2}

[`mc retention set`](#command-mc.retention.set) 命令用于为存储桶中的一个或多个对象配置 [Write-Once Read-Many (WORM) locking](/docs/administration/object-management/object-retention/#minio-object-locking) 设置。 你还可以为存储桶设置默认对象锁定设置，使未显式配置对象锁定的所有对象继承该存储桶默认值。

要在 [legal hold](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold) 下锁定对象， 请使用 [`mc legalhold set`](/docs/reference/minio-mc/mc-legalhold-set/#command-mc.legalhold.set)。

[`mc retention set`](#command-mc.retention.set) *要求* 指定存储桶已启用对象锁定。 你 **只能** 在创建存储桶时启用对象锁定。有关启用对象锁定创建存储桶的文档，请参见 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` MinIO 部署中的 `mydata` 存储桶上， 设置默认 30 天的 [GOVERNANCE](/docs/administration/object-management/object-retention/#minio-object-locking-governance) 对象锁：

```shell
mc retention set --default GOVERNANCE "30d" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] retention set                         \
                 [--bypass]                            \
                 [--default]                           \
                 [--recursive]                         \
                 [--rewind "string"]                   \
                 [--versions]                          \
                 [--version-id "string"]*              \
                 MODE                                  \
                 "VALIDITY"                            \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc retention set --version-id`](#mc.retention.set.-version-id) 与多个其他参数互斥。 更多信息请参见参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `MODE` {#mc.retention.set.MODE}

*mc-cmd*

*Required*

设置 [`ALIAS`](#mc.retention.set.ALIAS) 的锁定模式。 指定以下支持值之一：

- `governance`
- `compliance`

有关支持模式的更多信息，请参见 AWS S3 文档 [Object Lock Overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html)。

需要指定 [`VALIDITY`](#mc.retention.set.VALIDITY)。

##### `VALIDITY` {#mc.retention.set.VALIDITY}

*mc-cmd*

*Required*

指定对象在创建后保持在 [`MODE`](#mc.retention.set.MODE) 中的持续时间。

- **按天计时，指定格式为 `Nd` 的字符串。例如，**

  > `30d` 表示对象创建后 30 天。
- **按年计时，指定格式为 `Ny` 的字符串。例如，**

  > `1y` 表示对象创建后 1 年。

##### `ALIAS` {#mc.retention.set.ALIAS}

*mc-cmd*

*Required*

需要设置对象锁定配置的对象或对象集合的完整路径。 指定 MinIO 或兼容 S3 服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及存储桶完整路径。 例如：

```shell
mc retention set play/mybucket/object.txt MODE VALIDITY
```

- 如果 `ALIAS` 指定的是存储桶或存储桶前缀，请包含 [`--recursive`](#mc.retention.set.-recursive) 以将对象锁定设置应用到 存储桶内容。
- [`mc retention set`](#command-mc.retention.set) 默认仅应用到对象的最新版本。 使用 [`--version-id`](#mc.retention.set.-version-id) 或 [`--versions`](#mc.retention.set.-versions) 可分别将对象锁定设置 应用于指定版本或对象的所有版本。

##### `--bypass` {#mc.retention.set.-bypass}

*mc-cmd*

*Optional*

允许具有 `s3:BypassGovernanceRetention` 权限的用户 修改对象。需要 `governance` 保留 [`MODE`](#mc.retention.set.MODE)

##### `--default` {#mc.retention.set.-default}

*mc-cmd*

*Optional*

使用 [`MODE`](#mc.retention.set.MODE) 和 [`VALIDITY`](#mc.retention.set.VALIDITY)， 为 [`ALIAS`](#mc.retention.set.ALIAS) 指定的存储桶设置默认对象锁定设置。 在该存储桶中创建的任何对象都会继承默认对象锁定设置， 除非使用 [`mc retention set`](#command-mc.retention.set) 显式覆盖。

如果指定 [`--default`](#mc.retention.set.-default)， [`mc retention set`](#command-mc.retention.set) 会忽略所有其他标志。

##### `--recursive, --r` {#mc.retention.set.-recursive}

*mc-cmd*

*Optional*

递归将对象锁定设置应用到 [`ALIAS`](#mc.retention.set.ALIAS) 路径下的所有对象。

与 [`--version-id`](#mc.retention.set.-version-id) 互斥。

##### `--rewind` {#mc.retention.set.-rewind}

*mc-cmd*

*Optional*

指示 [`mc retention set`](#command-mc.retention.set) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.retention.set.-rewind) 要求指定的 [`ALIAS`](#mc.retention.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--version-id, --vid` {#mc.retention.set.-version-id}

*mc-cmd*

*Optional*

指示 [`mc retention set`](#command-mc.retention.set) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.retention.set.-version-id) 要求指定的 [`ALIAS`](#mc.retention.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下任一标志互斥：

- [`--versions`](#mc.retention.set.-versions)
- [`--rewind`](#mc.retention.set.-rewind)
- [`--recursive`](#mc.retention.set.-recursive)

##### `--versions` {#mc.retention.set.-versions}

*mc-cmd*

*Optional*

指示 [`mc retention set`](#command-mc.retention.set) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.retention.set.-versions) 要求指定的 [`ALIAS`](#mc.retention.set.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.retention.set.-versions) 与 [`--rewind`](#mc.retention.set.-rewind) 结合使用， 可将保留设置应用到特定时间点存在的所有对象版本。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 设置存储桶默认保留设置 {#id6}

将 [`mc retention set`](#command-mc.retention.set) 与 [`--recursive`](#mc.retention.set.-recursive) 和 [`--default`](#mc.retention.set.-default) 结合使用， 以设置存储桶默认保留设置。

```shell
mc retention set  --recursive --default MODE DURATION ALIAS/PATH
```

- 将 [`MODE`](#mc.retention.set.MODE) 替换为要启用的保留模式。 MinIO 支持 AWS S3 保留模式 `governance` 和 `compliance`。
- 将 [`DURATION`](#mc.retention.set.VALIDITY) 替换为对象锁定应持续生效的时长。 例如，要将保留期设置为 30 天，请指定 `30d`。
- 将 [`ALIAS`](#mc.retention.set.ALIAS) 替换为已配置的兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.set.ALIAS) 替换为存储桶路径。

> 要使用此命令，存储桶 *必须* 启用对象锁定。 只能在创建存储桶时启用对象锁定。有关创建已启用对象锁定的存储桶的更多信息， 请参阅 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock)。

### 为已版本化对象设置对象锁定配置 {#id7}

{{< tabs group="tab1-tab2" >}}
{{< tab label="特定版本" value="tab1" >}}
将 [`mc retention set`](#command-mc.retention.set) 与 [`--version-id`](#mc.retention.set.-version-id) 结合使用， 可将保留设置应用到特定对象版本：

```shell
mc retention set --version-id VERSION MODE DURATION ALIAS/PATH
```

- 将 [`VERSION`](#mc.retention.set.-version-id) 替换为对象版本。
- 将 [`MODE`](#mc.retention.set.MODE) 替换为要启用的保留模式。 MinIO 支持 AWS S3 保留模式 `governance` 和 `compliance`。
- 将 [`DURATION`](#mc.retention.set.VALIDITY) 替换为对象锁定应持续生效的时长。 例如，要将保留期设置为 30 天，请指定 `30d`。
- 将 [`ALIAS`](#mc.retention.set.ALIAS) 替换为已配置的兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.set.ALIAS) 替换为对象路径。
{{< /tab >}}
{{< tab label="所有版本" value="tab2" >}}
将 [`mc retention set`](#command-mc.retention.set) 与 [`--versions`](#mc.retention.set.-versions) 结合使用， 可将保留设置应用到特定对象版本：

```shell
mc retention set --versions  MODE DURATION ALIAS/PATH
```

- 将 [`MODE`](#mc.retention.set.MODE) 替换为要启用的保留模式。 MinIO 支持 AWS S3 保留模式 `governance` 和 `compliance`。
- 将 [`DURATION`](#mc.retention.set.VALIDITY) 替换为对象锁定应持续生效的时长。 例如，要将保留期设置为 30 天，请指定 `30d`。
- 将 [`ALIAS`](#mc.retention.set.ALIAS) 替换为已配置的兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.retention.set.ALIAS) 替换为对象路径。
{{< /tab >}}
{{< /tabs >}}

> 要使用此命令，存储桶 *必须* 启用对象锁定。 只能在创建存储桶时启用对象锁定。有关创建已启用对象锁定的存储桶的更多信息， 请参阅 [`mc mb --with-lock`](/docs/reference/minio-mc/mc-mb/#mc.mb.-with-lock)。

## 行为 {#id8}

### 对象版本的保留 {#id9}

对于启用了 [`versioning`](/docs/reference/minio-mc/mc-version/#command-mc.version) 的存储桶，[`mc retention set`](#command-mc.retention.set) 默认对目标对象（一个或多个）的 *最新* 版本执行操作。 [`mc retention set`](#command-mc.retention.set) 包含若干特定选项，在 *显式* 指定时， 可指示命令对特定对象版本 *或* 对象的所有版本执行操作：

{{< tabs group="tab1-tab2" >}}
{{< tab label="特定对象版本" value="tab1" >}}
要让 [`mc retention set`](#command-mc.retention.set) 对对象的特定版本执行操作， 请包含 `--version-id` 参数：

- [`mc retention set --version-id`](#mc.retention.set.-version-id)
- [`mc retention set --version-id`](#mc.retention.set.-version-id)
- [`mc retention set --version-id`](#mc.retention.set.-version-id)
{{< /tab >}}
{{< tab label="所有对象版本" value="tab2" >}}
要让 [`mc retention set`](#command-mc.retention.set) 对对象的 *所有* 版本执行操作， 请包含 `--versions` 参数：

- [`mc retention set --versions`](#mc.retention.set.-versions)
- [`mc retention set --versions`](#mc.retention.set.-versions)
- [`mc retention set --versions`](#mc.retention.set.-versions)
{{< /tab >}}
{{< /tabs >}}

### 与 legal hold 的交互 {#legal-hold}

锁定对象会阻止对该对象进行任何修改或删除， 与 [`COMPLIANCE`](#mc.retention.set.MODE) 对象锁定模式类似。 对象可以同时具有基于保留的锁和 legal hold 锁。

legal hold 锁会 *覆盖* 任何保留锁定，这意味着处于 legal hold 下的对象 即使保留期到期也会保持锁定。对处于 legal hold 下对象的保留设置进行设置、 修改或清除，在 legal hold 到期或被显式禁用之前均不会生效。

有关对象 legal hold 的更多信息，请参见 [`mc legalhold`](/docs/reference/minio-mc/mc-legalhold/#command-mc.legalhold)。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。