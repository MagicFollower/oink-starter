---
title: "mc replicate export"

weight: 80
---

<a id="mc-replicate-export"></a>
<a id="minio-mc-replicate-export"></a>

<a id="command-mc.replicate.export"></a>

## 语法 {#id2}

[`mc replicate export`](#command-mc.replicate.export) 命令将 MinIO 存储桶的 JSON 格式 [复制规则](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 导出到 `STDOUT`。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令导出 `myminio` MinIO 部署中 `mydata` 存储桶的复制配置：

```shell
mc replicate export myminio/mydata > mydata-replication.json
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] export ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.replicate.export.ALIAS}

*mc-cmd*

*必填* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要导出复制规则的存储桶或 存储桶前缀的完整路径。例如：

```text
mc replicate export myminio/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 导出现有复制规则 {#id6}

使用 [`mc replicate export`](#command-mc.replicate.export) 导出存储桶复制规则：

```shell
mc replicate export ALIAS/PATH > bucket-replication-rules.json
```

- 将 [`ALIAS`](#mc.replicate.export.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.replicate.export.ALIAS) 替换为存储桶或存储桶前缀的 路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。