---
title: "mc support top api"

weight: 10
---

<a id="mc-support-top-api"></a>

<a id="command-mc.support.top.api"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id2}

[`mc support top api`](#command-mc.support.top.api) 命令用于汇总 MinIO 部署服务器上的实时 API 事件。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 上当前正在进行的 S3 API 调用。

```shell
mc support top api myminio/
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] support top api    \
                 TARGET             \
                 [--name "string"]  \
                 [--path "string"]  \
                 [--node "string"]  \
                 [--errors, -e]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.support.top.api.TARGET}

*mc-cmd*

*Required*

命令应在其上运行的 alias、前缀或对象完整路径。 该路径至少必须包含一个 [ALIAS](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias)。

##### `--name` {#mc.support.top.api.-name}

*mc-cmd*

*Optional*

输出与输入字符串匹配的当前 API 调用摘要。

##### `--path` {#mc.support.top.api.-path}

*mc-cmd*

*Optional*

输出指定路径的当前 API 调用摘要。

##### `--node` {#mc.support.top.api.-node}

*mc-cmd*

*Optional*

输出匹配服务器上的当前 API 调用摘要。

##### `--errors, -e` {#mc.support.top.api.-errors}

*mc-cmd*

*Optional*

输出返回错误的当前 API 调用摘要。

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 显示当前所有正在进行的 S3 API 调用 {#s3-api}

以下命令显示 `myminio` 部署中所有正在进行的 S3 API 调用：

```shell
mc support top api myminio/
```

### 显示当前正在进行的 `s3.PutObject` 调用 {#s3-putobject}

以下命令显示 `myminio` 部署中所有正在进行的 `s3.PutObject` 调用：

```shell
mc support top api --name s3.PutObject myminio/
```