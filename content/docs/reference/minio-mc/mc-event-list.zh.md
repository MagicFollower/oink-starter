---
title: "mc event ls"

weight: 20
---

<a id="mc-event-ls"></a>
<a id="minio-mc-event-list"></a>

<a id="command-mc.event.list"></a>

<a id="command-mc.event.ls"></a>

## 语法 {#id2}

[`mc event ls`](#command-mc.event.ls) 命令列出某个存储桶的所有事件通知触发器。

别名 [`mc event list`](#command-mc.event.list) 与 [`mc event ls`](#command-mc.event.ls) 功能等效。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶、指定 [bucket notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 的所有已配置事件通知：

```shell
mc event ls myminio myminio/mydata arn:aws:sqs::primary:target
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

```shell
mc [GLOBALFLAGS] event ls [FLAGS] ALIAS ARN
```

### 参数 {#id3}

##### `ALIAS` {#mc.event.ls.ALIAS}

*mc-cmd*

*Required*

命令要列出事件通知的 S3 服务 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶。 例如：

```shell
mc event ls play/mybucket ARN...
```

##### `ARN` {#mc.event.ls.ARN}

*mc-cmd*

*Required*

存储桶资源的 [Amazon Resource Name (ARN)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns)。

MinIO 服务器在启动时会为每个已配置的通知目标输出一个 ARN。 更多信息请参见 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出存储桶上的事件通知 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出某个存储桶上的所有事件通知触发器。

```shell
mc event ls myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc event ls ALIAS ARN
```

- 将 `ALIAS` 替换为要添加存储桶通知事件的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。例如：

  `myminio/mydata`
- 将 `ARN` 替换为通知目标 [`ARN`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.ARN)。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。