---
title: "mc replicate rm"

weight: 60
---

<a id="mc-replicate-rm"></a>
<a id="minio-mc-replicate-rm"></a>

<a id="command-mc.replicate.remove"></a>

<a id="command-mc.replicate.rm"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc replicate rm` 替代 `mc admin bucket remote rm` 命令。 删除复制配置时会自动删除其底层远程目标。

## 语法 {#id2}

[`mc replicate rm`](#command-mc.replicate.rm) 命令用于从 MinIO 存储桶中删除 [replication rule](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。

[`mc replicate remove`](#command-mc.replicate.remove) 命令与 [`mc replicate rm`](#command-mc.replicate.rm) 功能等价。

```shell
mc [GLOBALFLAGS] replicate rm FLAGS [FLAGS] ALIAS
```

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `myminio` MinIO 部署中的 `mydata` 存储桶删除指定 id 的复制规则：

```shell
mc replicate rm --id "c76um9h4b0t1ijr36mug" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] replicate rm     \
                 --id "string"    \
                 [--all --force]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.replicate.rm.ALIAS}

*mc-cmd*

*必需* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要删除复制规则的 存储桶或存储桶前缀的完整路径。例如：

```text
mc replicate rm --id "ID" myminio/mybucket
```

##### `--id` {#mc.replicate.rm.-id}

*mc-cmd*

*必需* 指定已配置复制规则的唯一 ID。

如果指定 [`--all`](#mc.replicate.rm.-all)，则可省略此选项

##### `--all` {#mc.replicate.rm.-all}

*mc-cmd*

*可选* 删除指定存储桶上的所有复制规则。要求同时指定 [`--force`](#mc.replicate.rm.-force) 标志。

##### `--force` {#mc.replicate.rm.-force}

*mc-cmd*

*可选* 当指定 [`--all`](#mc.replicate.rm.-all) 时必需。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 从存储桶中删除一条复制规则 {#id6}

使用 [`mc replicate rm`](#command-mc.replicate.rm) 删除存储桶复制规则：

```shell
mc replicate rm --id "ID" ALIAS/PATH
```

- 将 [`ID`](#mc.replicate.rm.-id) 替换为要删除的复制规则唯一 ID。 使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 列出该存储桶的所有复制规则。
- 将 [`ALIAS`](#mc.replicate.rm.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.rm.ALIAS) 替换为存储桶或存储桶前缀的路径。

### 从存储桶中删除所有复制规则 {#id7}

使用 [`mc replicate rm`](#command-mc.replicate.rm) 删除存储桶复制规则：

```shell
mc replicate rm --all --force ALIAS/PATH
```

- 将 [`ALIAS`](#mc.replicate.rm.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.rm.ALIAS) 替换为存储桶或存储桶前缀的路径。

## 行为 {#id8}

### 删除复制规则不会影响已复制对象 {#id9}

删除存储桶的一条或全部复制规则，*不会* 删除已按这些规则复制的任何对象。

使用此命令或 [`mc rb`](/docs/reference/minio-mc/mc-rb/#command-mc.rb) 命令可删除远程目标上的已复制对象。 你可以通过 `X-Amz-Replication-Status` 元数据字段识别已复制对象，其值为 `REPLICA`。包含来自多个复制源对象的存储桶在删除前可能需要额外的 处理与过滤，以确定对象来源。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。