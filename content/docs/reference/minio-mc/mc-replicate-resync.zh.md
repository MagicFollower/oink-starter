---
title: "mc replicate resync"

weight: 50
---

<a id="mc-replicate-resync"></a>
<a id="minio-mc-replicate-resync"></a>

<a id="command-mc.replicate.reset"></a>

<a id="command-mc.replicate.resync"></a>

## 语法 {#id2}

[`mc replicate resync`](#command-mc.replicate.resync) 命令会将指定 MinIO 存储桶中的所有对象， 重新同步到远端 [replication](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 目标。

此命令 *要求* 先使用 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 命令配置远端存储桶目标。 执行 [`mc replicate resync`](#command-mc.replicate.resync) 时，必须指定由此生成的远端 ARN。

此命令支持使用 active-active 复制的远端作为“备份”来源来重建 MinIO 部署。 有关 active-active 复制的更多信息，请参阅以下教程：

- [启用双向服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway)
- [启用多站点服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-multi-site-bucket-replication/#minio-bucket-replication-serverside-multi)

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将 `myminio` MinIO 部署中 `mydata` 存储桶的内容， 重新同步到与指定 `--remote-bucket` 关联的远端 MinIO 部署：

```shell
mc replicate resync start \
   --remote-bucket "arn:minio:replication::d3c086c7-1d64-40c2-954b-fe8222907033:mydata" \
   myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] replicate resync start|status  \
                 --remote-bucket "string"       \
                 [--older-than "string"]        \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.replicate.resync.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及 MinIO 用作复制源的存储桶或存储桶前缀的完整路径。 例如，以下命令使用与 `primary` 别名关联的 MinIO 部署上的 `data` 存储桶启动复制。

```text
mc replicate resync start primary/data --remote-bucket "ARN"
```

##### `start` {#mc.replicate.resync.start}

*mc-cmd*

*Required*

使用指定的 [`bucket`](#mc.replicate.resync.ALIAS) 作为源， 并使用 [`--remote-bucket`](#mc.replicate.resync.-remote-bucket) 作为远端目标， 启动重新同步过程。

与 [`mc replicate resync status`](#mc.replicate.resync.status) 互斥。

##### `status` {#mc.replicate.resync.status}

*mc-cmd*

*Required*

返回指定 [`bucket`](#mc.replicate.resync.ALIAS) 到所有远端目标的重新同步状态。

包含 [`--remote-bucket`](#mc.replicate.resync.-remote-bucket) 参数可将状态输出过滤为仅显示指定远端目标。

##### `--remote-bucket` {#mc.replicate.resync.-remote-bucket}

*mc-cmd*

*Required*

指定目标部署和存储桶的 ARN。

可通过 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 配合 `--json` 选项获取 ARN。 `rule.Destination.Bucket` 字段包含任意给定复制规则的 ARN。

##### `older-than` {#mc.replicate.resync.older-than}

*mc-cmd*

*Optional*

指定一个以天为单位的时长，MinIO 仅会重新同步早于该时长的对象。

仅可与 [`mc replicate resync start`](#mc.replicate.resync.start) 一起使用。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 从源存储桶重新同步远端复制目标 {#id6}

以下 [`mc replicate resync`](#command-mc.replicate.resync) 命令会将指定源存储桶中的所有对象重新同步到远端目标， 不考虑其复制状态：

```shell
mc replicate resync start --remote-bucket "arn:minio:replication::UUID:data" primary/data
```

- 将 `primary/data` 替换为 [`ALIAS`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.ALIAS) 对应的完整存储桶路径，用于创建复制配置。
- 将 [`--remote-bucket`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-remote-bucket) 的值替换为远端目标的 ARN。 使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 列出所有已配置的远端复制目标。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。