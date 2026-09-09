---
title: "mc version enable"

weight: 10
---

<a id="mc-version-enable"></a>
<a id="minio-mc-version-enable"></a>

<a id="command-mc.version.enable"></a>

## 语法 {#id2}

[`mc version enable`](#command-mc.version.enable) 命令用于为指定存储桶启用版本控制。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` MinIO 部署中的 `mybucket` 存储桶启用版本控制：

```shell
 mc version enable myminio/mybucket
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] version enable ALIAS                \
                                --exclude-folders    \
                                --excluded-prefixes
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.version.enable.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 与要启用版本控制的存储桶完整路径。例如：

```shell
mc version enable myminio/mybucket
```

##### `--exclude-folders` {#mc.version.enable.-exclude-folders}

*mc-cmd*

*Optional*

在指定存储桶中，对所有文件夹（名称以 `/` 结尾的对象）禁用版本控制。

##### `--excluded-prefixes` {#mc.version.enable.-excluded-prefixes}

*mc-cmd*

*Optional*

对匹配前缀列表的对象禁用版本控制，最多支持 10 个前缀。 前缀列表会匹配前缀或名称中包含指定字符串的所有对象，类似 `prefix*` 形式的正则表达式。 如果仅按前缀匹配对象，请使用 `prefix/*`。

例如，以下命令将前缀或名称中包含 `_test` 或 `_temp` 的对象排除在版本控制之外：

```shell
mc version enable --excluded-prefixes "_test, _temp" myminio/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 启用存储桶版本控制 {#id6}

使用 [`mc version enable`](#command-mc.version.enable) 为存储桶启用版本控制：

```shell
mc version enable ALIAS/PATH
```

- 将 [`ALIAS`](#mc.version.enable.ALIAS) 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.version.enable.ALIAS) 替换为要启用版本控制的存储桶。

## 行为 {#id7}

### 现有数据的存储桶版本控制 {#id8}

在包含现有数据的存储桶上启用版本控制后，会立即为每个未版本化对象创建值为 `NULL` 的版本 ID。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。