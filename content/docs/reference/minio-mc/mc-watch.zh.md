---
title: "mc watch"

weight: 440
---

<a id="mc-watch"></a>

<a id="command-mc.watch"></a>

## 语法 {#id2}

[`mc watch`](#command-mc.watch) 命令用于监视指定 MinIO 存储桶或本地文件系统路径上的事件。 对于 S3 服务，请使用 [`mc event add`](/docs/reference/minio-mc/mc-event-add/#command-mc.event.add) 在兼容 S3 的服务上配置存储桶事件通知。

你也可以将 [`mc watch`](#command-mc.watch) 用于本地文件系统目录， 以获得与运行 `inotify -e modify,create,delete,move` 命令类似的结果。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会监视 `myminio` MinIO 部署中 `mydata` 存储桶内任意对象或前缀上的 [事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events)：

```shell
mc watch --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] watch                \
                 [--event "string"]   \
                 [--prefix "string"]  \
                 [--recursive]        \
                 [--suffix "string"]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.watch.ALIAS}

*mc-cmd*

*必需* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及要监视已配置事件的存储桶完整路径。 例如：

```shell
mc watch myminio/mybucket
```

##### `--event` {#mc.watch.-event}

*mc-cmd*

要监视的事件。使用英文逗号 `,` 分隔可指定多个事件。 支持的事件见 [支持的存储桶事件](/docs/reference/minio-mc/mc-event-add/#mc-event-supported-events)。

默认值为 `put,delete, get`。

##### `--prefix` {#mc.watch.-prefix}

*mc-cmd*

在该存储桶前缀下监视 [`--event`](#mc.watch.-event) 指定的事件。

例如，若 [`ALIAS`](#mc.watch.ALIAS) 为 `play/mybucket`，且 [`--prefix`](#mc.watch.-prefix) 为 `photos`，则仅 `play/mybucket/photos` 中的事件会触发存储桶通知。

##### `--recursive, r` {#mc.watch.-recursive}

*mc-cmd*

在指定的 [`ALIAS`](#mc.watch.ALIAS) 存储桶路径或本地目录中递归监视事件。

##### `--suffix` {#mc.watch.-suffix}

*mc-cmd*

在该存储桶后缀下监视 [`--event`](#mc.watch.-event) 指定的事件。

例如，若 [`ALIAS`](#mc.watch.ALIAS) 为 `play/mybucket`，且 [`--suffix`](#mc.watch.-suffix) 为 `.jpg`，则仅 `play/mybucket/*.jpg` 中的事件会触发存储桶通知。

### 全局标志 {#id4}

##### `--json` {#mc.watch.-json}

*mc-cmd*

*Optional*

启用 [JSON lines](http://jsonlines.org/)<a id="json-lines"></a> 格式的控制台输出。

例如：

```shell
mc --json COMMAND
```

## 示例 {#id5}

### 监视存储桶中的事件 {#id6}

```shell
mc watch --recursive ALIAS/PATH
```

- 将 [`ALIAS`](#mc.watch.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.watch.ALIAS) 替换为存储桶路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。