---
title: "mc ilm export"

weight: 30
---

<a id="mc-ilm-export"></a>
<a id="minio-mc-ilm-export"></a>

<a id="command-mc.ilm.export"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm export` 已被 [`mc ilm rule export`](/docs/reference/minio-mc/mc-ilm-rule-export/#command-mc.ilm.rule.export) 替代。

## 语法 {#id2}

[`mc ilm export`](#command-mc.ilm.export) 命令用于导出 MinIO 存储桶的对象生命周期管理配置。

[`mc ilm export`](#command-mc.ilm.export) 命令默认输出到 `STDOUT`。你可以将内容输出到 `.json` 文件中，以便归档或通过 [`mc ilm import`](/docs/reference/deprecated/mc-ilm-import/#command-mc.ilm.import) 导入使用。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将 `myminio` 部署上 `mydata` 存储桶的生命周期管理配置 导出到 `mydata-lifecycle-config.json` 文件：

```shell
mc ilm export myminio/mydata > mydata-lifecycle-config.json
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] ilm export ALIAS > STDOUT
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.export.ALIAS}

*mc-cmd*

*必需* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶完整路径，用于导出该 存储桶的对象生命周期管理规则。例如：

```text
mc ilm export myminio/mydata > bucket-lifecycle.json
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 导出存储桶生命周期管理配置 {#id6}

{{< tabs group="example-syntax" >}}
{{< tab label="Example" value="example" >}}
以下命令将存储桶生命周期管理配置导出到 `bucket-lifecycle.json` 文件：

```shell
mc ilm export myminio/mybucket > bucket-lifecycle.json
```
{{< /tab >}}
{{< tab label="Syntax" value="syntax" >}}
```shell
mc ilm export ALIAS > file.json
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和需要导出 对象生命周期管理规则的存储桶：

  `myminio/mydata`
- 将 `file.json` 替换为用于导出生命周期管理规则的文件名。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。