---
title: "mc encrypt clear"

weight: 10
---

<a id="mc-encrypt-clear"></a>
<a id="minio-mc-encrypt-clear"></a>

<a id="command-mc.encrypt.clear"></a>

## 语法 {#id2}

[`mc encrypt clear`](#command-mc.encrypt.clear) 命令用于移除存储桶当前的默认加密设置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会移除 `myminio` [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 关联的 MinIO 部署中 `mydata` 存储桶的默认加密设置：

```shell
mc encrypt clear myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] encrypt clear ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.encrypt.clear.ALIAS}

*mc-cmd*

要移除默认 SSE 模式的目标存储桶完整路径。 指定 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 ALIAS 路径前缀。例如：

```shell
mc encrypt clear play/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 移除存储桶的自动服务端加密设置 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
```shell
 mc encrypt clear myminio/data
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc encrypt clear ALIAS
```

- 将 `ALIAS` 替换为目标 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)， 即要移除存储桶自动服务端加密配置的部署别名。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

### 修改存储桶加密设置不会影响已加密对象 {#id8}

禁用存储桶自动加密 *不会* 解密该存储桶中的任何对象。

要永久解密存储桶中的对象，可在禁用对象解密后执行原地复制。 对于启用版本控制的存储桶，旧版本对象仍保持加密状态。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。