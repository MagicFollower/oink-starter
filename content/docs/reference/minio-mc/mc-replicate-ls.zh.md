---
title: "mc replicate ls"

weight: 30
---

<a id="mc-replicate-ls"></a>
<a id="minio-mc-replicate-ls"></a>

<a id="command-mc.replicate.list"></a>

<a id="command-mc.replicate.ls"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc replicate ls` 替代 `mc admin bucket remote ls` 命令。

## 语法 {#id2}

[`mc replicate ls`](#command-mc.replicate.ls) 命令列出 MinIO 存储桶上的所有 [复制规则](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。

[`mc replicate list`](#command-mc.replicate.list) 命令与 [`mc replicate ls`](#command-mc.replicate.ls) 功能等价。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶的所有已启用复制规则：

```shell
mc replicate ls --status "enabled" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] replicate ls         \
                 [--status "string"]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.replicate.ls.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要列出复制规则的 存储桶或存储桶前缀的完整路径。例如：

```text
mc replicate ls myminio/mybucket
```

##### `--status` {#mc.replicate.ls.-status}

*mc-cmd*

*Optional*

按状态筛选存储桶上的复制规则。 指定以下值之一：

- `enabled` - 仅显示已启用的复制规则。
- `disabled` - 仅显示已禁用的复制规则。

如果省略，[`mc replicate ls`](#command-mc.replicate.ls) 默认显示所有复制规则。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出现有复制规则 {#id6}

使用 [`mc replicate ls`](#command-mc.replicate.ls) 列出存储桶复制规则：

```shell
mc replicate ls ALIAS/PATH
```

- 将 [`ALIAS`](#mc.replicate.ls.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.ls.ALIAS) 替换为存储桶或存储桶前缀的路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。