---
title: "mc version suspend"

weight: 30
---

<a id="mc-version-suspend"></a>
<a id="minio-mc-version-suspend"></a>

<a id="command-mc.version.suspend"></a>

## 语法 {#id2}

[`mc version suspend`](#command-mc.version.suspend) 命令用于禁用指定存储桶上的版本控制。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会为 `myminio` MinIO 部署中的 `mybucket` 存储桶禁用版本控制：

```shell
mc version suspend myminio/mybucket
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] version suspend ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.version.suspend.ALIAS}

*mc-cmd*

要禁用版本控制的存储桶完整路径。 例如：

```shell
mc version suspend myminio/mybucket
```

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 禁用存储桶版本控制 {#id6}

使用 [`mc version suspend`](#command-mc.version.suspend) 为存储桶禁用版本控制：

```shell
mc version suspend ALIAS/PATH
```

- 将 [`ALIAS`](#mc.version.suspend.ALIAS) 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.version.suspend.ALIAS) 替换为要禁用版本控制的存储桶。

## 行为 {#id7}

### 现有数据下的存储桶版本控制 {#id8}

在包含现有版本化数据的存储桶上禁用版本控制时，*不会* 删除任何已版本化对象。 应用程序在禁用存储桶版本控制后仍可继续访问版本化数据。 使用 [`mc rm --versions ALIAS/BUCKET/OBJECT`](/docs/reference/minio-mc/mc-rm/#mc.rm.-versions) 删除某个对象及其所有版本。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。