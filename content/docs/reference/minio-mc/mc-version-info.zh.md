---
title: "mc version info"

weight: 20
---

<a id="mc-version-info"></a>
<a id="minio-mc-version-info"></a>

<a id="command-mc.version.info"></a>

## 语法 {#id2}

[`mc version info`](#command-mc.version.info) 命令返回指定存储桶的版本控制状态。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回 `myminio` MinIO 部署中 `mybucket` 存储桶的版本控制状态：

```shell
mc version info myminio/mybucket
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] version info ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.version.info.ALIAS}

*mc-cmd*

要获取其版本控制状态的存储桶的完整路径。 例如：

```shell
mc version info myminio/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 获取存储桶版本控制状态 {#id6}

使用 [`mc version info`](#command-mc.version.info) 获取存储桶的版本控制状态：

```shell
mc version info ALIAS/PATH
```

- 将 [`ALIAS`](#mc.version.info.ALIAS) 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.version.info.ALIAS) 替换为要获取版本控制状态的存储桶。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。