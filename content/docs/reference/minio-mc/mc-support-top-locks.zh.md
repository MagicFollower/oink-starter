---
title: "mc support top locks"

weight: 20
---

<a id="mc-support-top-locks"></a>

<a id="command-mc.support.top.locks"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id2}

[`mc support top locks`](#command-mc.support.top.locks) 命令列出 MinIO 部署中最旧的 10 个 [锁](/docs/administration/object-management/object-retention/#minio-object-locking)。

该命令输出锁的存在时长、锁类型、所有者和资源。 输出类似如下：

```shell
Since                 Type    Owner                 Resource
13 hours ago          WRITE   10.68.100.18:9000     .minio.sys/leader.lock
13 hours ago          WRITE   10.68.100.18:9000     .minio.sys/callhome/runCallhome.lock
13 hours ago          WRITE   10.68.100.23:9000     .minio.sys/new-drive-healing/0/0
```

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 上当前进行中的 S3 API 调用。

```shell
mc support top locks myminio/
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] support top locks  \
                 [--stale]          \
                 TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.support.top.locks.TARGET}

*mc-cmd*

*Required*

命令应在其上运行的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 或前缀的完整路径。

##### `--stale` {#mc.support.top.locks.-stale}

*mc-cmd*

*Optional*

仅返回陈旧锁。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 显示 `myminio` 部署中最旧的 10 个锁 {#myminio-10}

```shell
mc support top locks myminio/
```

### 显示 `myminio` 部署中的陈旧锁 {#myminio}

以下命令显示 `myminio` 部署中所有进行中的 `s3.PutObject` 调用：

```shell
mc support top locks --stale myminio/
```