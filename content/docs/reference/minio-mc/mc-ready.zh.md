---
title: "mc ready"

weight: 310
---

<a id="mc-ready"></a>

<a id="command-mc.ready"></a>

## 语法 {#id2}

[`mc ready`](#command-mc.ready) 命令用于检查集群状态，以及集群是否具有 `read` 和 `write` quorum。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令向别名为 `myminio` 的集群发送 `GET` 请求，并返回其状态。

```shell
mc ready myminio
```

该命令会向 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) `myminio` 对应的部署发送 `GET` 请求。 该命令会重复发送请求，直到成功为止。

在别名 `myminio` 对应的集群就绪之前，输出类似如下：

```text
The cluster `myminio` is unreachable: Get "http://myminio.example.com:9000/minio/health/cluster": dial tcp 198.51.100.0:9000: connect: connection refused
```

当请求成功连接到 `myminio` 部署后，输出类似如下：

```text
The cluster `myminio` is ready
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] ready            \
                 TARGET           \
                 [--cluster-read] \
                 [--maintenance]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.ready.TARGET}

*mc-cmd*

*Required*

命令运行目标的完整路径，可为 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或前缀。

##### `--cluster-read` {#mc.ready.-cluster-read}

*mc-cmd*

*Optional*

检查集群是否具有足够的 [quorum](/zh/glossary/#term-read-quorum) 来处理 `READ` 请求。

##### `--maintenance` {#mc.ready.-maintenance}

*mc-cmd*

*Optional*

检查当该别名对应节点因维护下线时，集群是否仍可维持 read 和 write quorum。

对预期下线维护的具体节点使用其 alias，而不要使用指向负载均衡器的 alias。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 检查集群是否具有 read quorum {#read-quorum}

以下命令检查某个部署是否有足够可用驱动器来执行读取操作。

```shell
mc read myminio --cluster-read
```

### 检查集群是否处于维护下线场景 {#id6}

以下命令检查当别名 `myminio` 对应节点下线时，集群在维护期间是否仍可维持 read 和 write quorum。

```shell
mc ready myminio --maintenance
```