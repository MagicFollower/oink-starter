---
title: "mc rb"

weight: 300
---

<a id="mc-rb"></a>

<a id="command-mc.rb"></a>

## 语法 {#id2}

[`mc rb`](#command-mc.rb) 命令用于删除 MinIO *或* 其他兼容 S3 服务上的一个或多个存储桶。

如仅需删除存储桶内容，请改用 [`mc rm`](/docs/reference/minio-mc/mc-rm/#command-mc.rm)。

> [!WARNING]
> **重要**
>
> [`mc rb`](#command-mc.rb) 会在目标部署上 *永久删除存储桶*， 包括所有 [对象版本](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 以及存储桶配置，例如 [生命周期管理](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 或 [复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。

你也可以对本地文件系统使用 [`mc rb`](#command-mc.rb)，其效果与 `rm --rf` 命令行工具类似。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令删除 `myminio` MinIO 部署上的 `mydata` 存储桶：

```shell
mc rb --force myminio/mydata
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] rb             \
                 --force        \
                 [--dangerous]  \
                 ALIAS [ALIAS...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.rb.ALIAS}

*mc-cmd*

*必需* MinIO 或其他兼容 S3 服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要删除的存储桶完整路径。例如：

```text
mc rb --force myminio/mydata
```

省略存储桶路径可对 MinIO 部署执行站点范围的存储桶删除操作。 此操作 *必须* 指定 [`--dangerous`](#mc.rb.-dangerous)，以明确确认会永久删除该部署上的 *全部* 数据。例如：

```text
mc rb --force --dangerous myminio
```

若要删除本地文件系统上的目录及其内容，请指定该目录的完整路径。 如果指定了 [`--force`](#mc.rb.-force) 标志，也会被忽略。例如：

```text
mc rb ~/data/myolddata
```

你可以指定多个 `ALIAS` 目标，目标可以是 MinIO 或本地文件系统目录。 命令会尝试删除 *所有* 指定目标。例如：

```text
mc rb --force myminio/mydata ~/data/myolddata
```

##### `--force` {#mc.rb.-force}

*mc-cmd*

*必需* 用于确认删除存储桶内容的安全标志。

##### `--dangerous` {#mc.rb.-dangerous}

*mc-cmd*

*可选* 指示 [`mc rb`](#command-mc.rb) 在每个指定的 [`ALIAS`](#mc.rb.ALIAS)（例如 `myminio/`）上执行站点范围的全部存储桶删除。

如果任一 `ALIAS` 指定的是文件系统目录，此选项会删除该目录路径下的所有子目录和文件，效果类似 `rm --rf`。

> [!CAUTION]
> **警告**
>
> 执行 [`mc rb --dangerous`](#mc.rb.-dangerous) 不可逆。 在执行前请尽可能审慎核对，确保命令仅作用于预期的 `ALIAS` 目标。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 删除存储桶 {#id6}

```shell
mc rb --force ALIAS/PATH
```

- 将 [`ALIAS`](#mc.rb.ALIAS) 替换为已配置的兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.rb.ALIAS) 替换为要删除的存储桶路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。