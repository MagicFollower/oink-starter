---
title: "mc support top rpc"

weight: 50
---

<a id="mc-support-top-rpc"></a>

<a id="command-mc.support.top.rpc"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id2}

[`mc support top rpc`](#command-mc.support.top.rpc) 命令显示远程过程调用（RPC）的指标。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 部署当前的远程过程调用指标。

```shell
mc support top rpc myminio/
```

输出会返回如下信息：server、连接数、ping 时延、距离上次 ping（`pong`）的时间、重连次数、string in、string out、messages in 和 messages out。

输出类似如下：

```bash
λ mc support top rpc myminio
      SERVER            CONCTD  PING     PONG   OUT.Q   RECONNS STR.IN  STR.OUT MSG.IN  MSG.OUT
 To  127.0.0.1:9002       5     0.7ms   1s ago    0        0     ->0      0->    3269    3212
From 127.0.0.1:9002       5     1.1ms   1s ago    0        0     ->0      0->    3213    3269
 To  127.0.0.1:9003       5     0.6ms   1s ago    0        0     ->0      0->    6001    6076
From 127.0.0.1:9003       5     0.6ms   1s ago    0        0     ->0      0->    6077    6001
 To  127.0.0.1:9004       5     0.6ms   1s ago    0        0     ->0      0->    3243    3160
From 127.0.0.1:9004       5     0.4ms   1s ago    0        0     ->0      0->    3161    3243
 To  127.0.0.1:9005       5     0.6ms   1s ago    0        0     ->0      0->    3150    3094
From 127.0.0.1:9005       5     0.3ms   1s ago    0        0     ->0      0->    3095    3150
 To  127.0.0.1:9006       5     0.3ms   1s ago    0        0     ->0      0->    3185    3221
From 127.0.0.1:9006       5     0.6ms   1s ago    0        0     ->0      0->    3222    3185
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] support top rpc                 \
                             [--airgap]          \
                             [--in value]        \
                             [--interval value]  \
                             [-n value]          \
                             [--nodes value]     \
                             TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.support.top.rpc.TARGET}

*mc-cmd*

*Required*

命令应运行的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或 [prefix](/zh/glossary/#term-prefix) 的完整路径。

##### `--airgap` {#mc.support.top.rpc.-airgap}

*mc-cmd*

*Optional*

用于无法通过网络访问 SUBNET 的环境。

##### `--in` {#mc.support.top.rpc.-in}

*mc-cmd*

*Optional*

回放先前保存的 JSON 文件。 指定要回放的 JSON 文件路径，例如由此前运行该命令生成的文件。

##### `--interval` {#mc.support.top.rpc.-interval}

*mc-cmd*

*Optional*

指标请求之间的间隔时间（秒）。

默认情况下，命令每秒请求一次指标。

##### `-n` {#mc.support.top.rpc.-n}

*mc-cmd*

*Optional*

在退出前要运行的请求次数。 使用 `0` 表示无限运行。

如果未指定，命令不会自动退出。

##### `--nodes` {#mc.support.top.rpc.-nodes}

*mc-cmd*

*Optional*

以逗号分隔的节点列表，用于指定从哪些节点收集指标。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。