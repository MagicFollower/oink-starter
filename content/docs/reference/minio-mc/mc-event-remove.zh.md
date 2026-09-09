---
title: "mc event rm"

weight: 30
---

<a id="mc-event-rm"></a>
<a id="minio-mc-event-remove"></a>

<a id="command-mc.event.remove"></a>

<a id="command-mc.event.rm"></a>

## 语法 {#id2}

[`mc event rm`](#command-mc.event.rm) 命令用于从存储桶中移除事件通知触发器。

[`mc event remove`](#command-mc.event.remove) 命令与 [`mc event rm`](#command-mc.event.rm) 功能等效。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令会在 `myminio` MinIO 部署的 `mydata` 存储桶上， 移除指定 [bucket notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications) 的已配置事件通知：

```shell
mc event rm myminio/mydata arn:aws:sqs::primary:target
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] event remove        \
                 ALIAS               \
                 [ARN]               \
                 [--event "string"]  \
                 [--force]           \
                 [--prefix "string"] \
                 [--suffix "string"]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

```shell
mc [GLOBALFLAGS] event remove [FLAGS] ALIAS ARN
```

### 参数 {#id3}

##### `ALIAS` {#mc.event.rm.ALIAS}

*mc-cmd*

*Required*

用于移除事件通知的 S3 服务 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶。 例如：

```shell
mc event rm play/mybucket
```

##### `ARN` {#mc.event.rm.ARN}

*mc-cmd*

*Required*

通知目标的 [Amazon Resource Name (ARN)](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference-arns)。

MinIO 服务器在启动时会为每个已配置的通知目标输出一个 ARN。 更多信息请参见 [存储桶通知](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。

可在存储桶上运行 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 获取 ARN。

##### `--event` {#mc.event.rm.-event}

*mc-cmd*

*Optional*

添加事件时指定的事件类型。 这些条目 **必须** 与添加事件时使用的值一致。 如果没有事件与事件类型列表匹配，命令将返回 `no notification configuration matched` 错误。

使用逗号 `,` 分隔可指定多个事件。 支持的事件类型请参见 [支持的存储桶事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events)。

默认移除 [`ALIAS`](#mc.event.rm.ALIAS) 存储桶中、与 [`ARN`](#mc.event.rm.ARN) 通知目标关联且对所有事件类型触发的事件。

可通过在存储桶上运行 [`mc event ls`](/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls) 获取所使用的事件类型。 使用下表将命令输出中的事件类型转换为 [`mc event rm`](#command-mc.event.rm) 命令所需的条目：

| `mv event ls` 的输出 | 要使用的事件类型 |
| --- | --- |
| `s3:objectAccessed` | `get` |
| `s3:objectCreated` | `put` |
| `s3:objectRemoved` | `delete` |

例如，如果 `mc event ls` 返回如下内容：

```shell
arn:minio:sqs::mytest:webhook   s3:ObjectAccessed:*,s3:ObjectCreated:*   Filter:
```

使用以下命令移除该事件：

```shell
mc event rm alias/bucket arn:minio:sqs::mytest:webhook --event get,put
```

事件类型的顺序无关紧要，只需包含与该事件中已有类型相同的条目即可。

##### `--force` {#mc.event.rm.-force}

*mc-cmd*

*Optional*

移除 [`ALIAS`](#mc.event.rm.ALIAS) 存储桶中与 [`ARN`](#mc.event.rm.ARN) 通知目标关联的所有事件。

##### `--prefix` {#mc.event.rm.-prefix}

*mc-cmd*

*Optional*

命令移除存储桶通知时使用的存储桶前缀。

例如，若 [`ALIAS`](#mc.event.rm.ALIAS) 为 `play/mybucket`，且 [`--prefix`](#mc.event.rm.-prefix) 为 `photos`，则命令仅移除 `play/mybucket/photos`.

##### `--suffix` {#mc.event.rm.-suffix}

*mc-cmd*

*Optional*

命令移除存储桶通知时使用的存储桶后缀。

例如，若 [`ALIAS`](#mc.event.rm.ALIAS) 为 `play/mybucket`，且 [`--suffix`](#mc.event.rm.-suffix) 为 `.jpg`，则命令仅移除 `play/mybucket/*.jpg`.

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 从存储桶中移除事件通知 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会移除某个存储桶上的所有事件通知触发器。 该命令假设 MinIO 部署中至少配置了一个 [bucket notification target](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications):

```shell
mc event rm myminio/mydata arn:minio:sqs::primary:webhook
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc event rm ALIAS ARN
```

- 将 `ALIAS` 替换为要在其上添加存储桶通知事件的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。例如：

  `myminio/mydata`
- 将 `ARN` 替换为通知目标 [`ARN`](/docs/reference/minio-mc/mc-event-add/#mc.event.add.ARN).
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。