---
title: "mc support top net"

weight: 40
---

<a id="mc-support-top-net"></a>

<a id="command-mc.support.top.net"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id2}

[`mc support top net`](#command-mc.support.top.net) 命令用于显示实时网络指标。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 部署当前的实时网络指标。

```shell
mc support top net myminio/
```

输出将返回服务器 URL、网络接口、接收速率、发送速率和系统消息等信息。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] support top disk                \
                             [--interval value]  \
                             TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.support.top.net.TARGET}

*mc-cmd*

*Required*

命令应运行的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或 [prefix](/zh/glossary/#term-prefix) 的完整路径。

##### `--interval` {#mc.support.top.net.-interval}

*mc-cmd*

*Optional*

两次指标请求之间的间隔（秒）。

默认情况下，命令每秒请求一次指标。

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。