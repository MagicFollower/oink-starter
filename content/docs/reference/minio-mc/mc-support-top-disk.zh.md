---
title: "mc support top disk"

weight: 30
---

<a id="mc-support-top-disk"></a>

<a id="command-mc.support.top.disk"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id2}

[`mc support top disk`](#command-mc.support.top.disk) 命令显示当前驱动器统计信息。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 上当前正在进行的 S3 API 调用。

```shell
mc support top disk myminio/
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] support top disk                     \
                             [--count, -c "integer"]  \
                             TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.support.top.disk.TARGET}

*mc-cmd*

*Required*

要运行该命令的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或 [prefix](/zh/glossary/#term-prefix) 的完整路径。

##### `--count, -c` {#mc.support.top.disk.-count}

*mc-cmd*

*Optional*

显示统计信息，最多显示到指定数量的驱动器。

如果未提供值，该命令最多返回 10 个驱动器的统计信息。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。