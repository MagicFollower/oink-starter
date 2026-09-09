---
title: "mc alias remove"

weight: 20
---

<a id="mc-alias-remove"></a>
<a id="minio-mc-alias-remove"></a>

<a id="command-mc.alias.remove"></a>

## 语法 {#id2}

[`mc alias remove`](#command-mc.alias.remove) 从本地 **`mc`** 配置中移除一个已存在的别名。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会从主机上移除 MinIO 部署的 `myminio` [alias](/docs/reference/minio-mc/mc-alias-set/#alias)：

```shell
mc alias remove myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc alias remove`](#command-mc.alias.remove) 命令的语法如下：

```shell
mc [GLOBALFLAGS] alias remove ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.alias.remove.ALIAS}

*mc-cmd*

*必填* 要从本地 **`mc`** 配置中移除的别名。

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 从 `mc` 配置中移除别名 {#mc}

使用 [`mc alias remove`](#command-mc.alias.remove) 从 **`mc`** 配置中移除一个已存在的别名：

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会移除 `myminio` 别名。

```shell
mc alias remove myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc alias remove ALIAS
```

将 `ALIAS` 替换为要移除的别名名称。
{{< /tab >}}
{{< /tabs >}}

### 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。