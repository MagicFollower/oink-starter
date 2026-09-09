---
title: "mc mb"

weight: 230
---

<a id="mc-mb"></a>

<a id="command-mc.mb"></a>

## 语法 {#id2}

[`mc mb`](#command-mc.mb) 命令在指定路径创建新的存储桶或目录。

你也可将 [`mc mb`](#command-mc.mb) 用于本地文件系统，实现与 `mkdir -p` 命令行工具类似的效果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` MinIO 部署上创建一个新的存储桶 `mydata`。 该命令创建的存储桶将 [启用对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking)。

```shell
mc mb --with-locks myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] mb                   \
                 [--ignore-existing]  \
                 [--region "string"]  \
                 [--with-lock]        \
                 [--with-versioning]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.mb.ALIAS}

*mc-cmd*

*Required*

要在其上创建新存储桶的 MinIO 或其他 S3 兼容服务。

如果要在 MinIO 上创建存储桶，请指定 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶名称。例如：

```text
mc mb play/mybucket
```

如果要在本地文件系统上创建目录，请指定该目录的完整 路径。例如：

```text
mc mb ~/mydata/mydir
```

##### `--ignore-existing, p` {#mc.mb.-ignore-existing}

*mc-cmd*

*Optional*

指示 [`mc mb`](#command-mc.mb) 在存储桶或目录已存在时不执行任何操作。

##### `--region` {#mc.mb.-region}

*mc-cmd*

*Optional*

指定创建存储桶的区域。 如果指定的 [`ALIAS`](#mc.mb.ALIAS) 是文件系统目录，则该选项无效。

如果未指定，默认值为 `us-east-1`。

##### `--with-lock, l` {#mc.mb.-with-lock}

*mc-cmd*

*Optional*

在指定存储桶上启用 [对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking)。 对象锁定要求并因此隐含启用对象版本控制。

> [!WARNING]
> **重要**
>
> 你 *只能* 在创建存储桶时启用对象锁定。 未启用对象锁定创建的存储桶无法使用 [存储桶生命周期管理](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 或 [存储桶对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking) 功能。

##### `--with-versioning` {#mc.mb.-with-versioning}

*mc-cmd*

*Optional*

在新存储桶上启用 [对象版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 启用版本控制后，默认情况下 MinIO 允许每个对象的版本数最多达到 Int64 最大值，即超过 9.2 quintillion。 可定义 [对象过期](/docs/administration/object-management/create-lifecycle-management-expiration-rule/#minio-lifecycle-management-create-expiry-rule) 规则，清理不再需要的对象版本，例如按版本数量或版本日期删除。

[存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication) 或 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview) 需要版本控制。 版本控制不隐含也不要求对象锁定。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 创建启用对象锁定的存储桶 {#id6}

使用 [`mc mb`](#command-mc.mb) 在 S3 兼容主机上创建存储桶。 [`--with-lock`](#mc.mb.-with-lock) 选项创建启用锁定的存储桶：

```shell
mc mb --with-lock ALIAS/BUCKET
```

- 将 [`ALIAS`](#mc.mb.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`BUCKET`](#mc.mb.ALIAS) 替换为要创建的存储桶。

### 在指定区域创建新存储桶 {#id7}

使用 [`mc mb`](#command-mc.mb) 在 S3 兼容主机上创建存储桶。 [`--region`](#mc.mb.-region) 选项在目标区域创建该存储桶。

```shell
mc mb --region --region=us-west-2 myminio/mynewbucket
```

上述命令会在 `us-west-2` 区域中的 `myminio` 上创建新存储桶 `mynewbucket`。

### 创建启用版本控制的新存储桶 {#id8}

```shell
mc mb --with-versioning myminio/myversionedbucket
```

上述命令会在 `myminio` alias 上创建新的存储桶 `myversionedbucket`。 新存储桶为桶内所有对象启用 [对象版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。

## 行为 {#id9}

### 每个部署的存储桶限制 {#id10}

MinIO 不限制你在单个部署上可创建的存储桶数量。 但作为通用指导，MinIO 建议每个部署的存储桶数量不超过 500,000。

### 非 MinIO S3 服务的存储桶限制 {#minio-s3}

某些 S3 服务可能限制单个用户或账户可创建的存储桶数量。 例如，Amazon S3 将每个账户限制为 [100 buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketRestrictions.html)。如果用户在目标 S3 服务上达到存储桶上限，[`mc mb`](#command-mc.mb) 可能返回错误。

MinIO 对象存储部署不限制每个用户可创建的 存储桶数量。

### 在创建存储桶时启用对象锁定 {#id11}

MinIO 遵循 [AWS S3 behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html#object-lock-bucket-config)， 要求你 *必须* 在创建存储桶时启用 [对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking)。 未启用对象锁定创建的存储桶 *永远* 无法启用对象保留或锁定。

启用存储桶锁定并 *不会* 设置任何对象锁定或保留配置。 建议将启用存储桶锁定作为标准实践。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。