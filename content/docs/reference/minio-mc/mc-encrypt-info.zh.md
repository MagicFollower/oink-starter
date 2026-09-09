---
title: "mc encrypt info"

weight: 20
---

<a id="mc-encrypt-info"></a>
<a id="minio-mc-encrypt-info"></a>

<a id="command-mc.encrypt.info"></a>

## 语法 {#id2}

[`mc encrypt info`](#command-mc.encrypt.info) 命令返回存储桶当前的默认加密设置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回 `myminio` MinIO 部署上 `mydata` 存储桶的默认加密设置。

```shell
mc encrypt info myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] encrypt info ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.encrypt.info.ALIAS}

*mc-cmd*

要检索其默认 SSE 模式的存储桶完整路径。 指定 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 ALIAS 路径前缀。例如：

```shell
mc encrypt info play/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 获取存储桶的自动服务端加密设置 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
```shell
 mc encrypt info myminio/data
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc encrypt info ALIAS
```

- 将 `ALIAS` 替换为要为其配置存储桶自动服务端加密的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。