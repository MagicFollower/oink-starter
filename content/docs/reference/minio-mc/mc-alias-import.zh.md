---
title: "mc alias import"

weight: 40
---

<a id="mc-alias-import"></a>
<a id="minio-mc-alias-import"></a>

<a id="command-mc.alias.import"></a>

## 语法 {#id2}

[`mc alias import`](#command-mc.alias.import) 命令从 JSON 文档中导入别名配置。

你可以使用 [`mc alias export`](/docs/reference/minio-mc/mc-alias-export/#command-mc.alias.export) 生成导入所需的 JSON。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 JSON 文档中导入别名配置：

```shell
mc alias import newalias ./credentials.json
```

使用 [`mc alias list newalias`](/docs/reference/minio-mc/mc-alias-list/#command-mc.alias.list) 确认导入成功。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc alias import`](#command-mc.alias.import) 命令的语法如下：

```shell
mc [GLOBALFLAGS] alias import ALIAS PATH|STDIN
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.alias.import.ALIAS}

*mc-cmd*

*Required*

分配给导入配置的别名名称。

##### `PATH` {#mc.alias.import.PATH}

*mc-cmd*

*Required*

表示待导入别名配置的 JSON 对象的完整路径。

与 [`STDIN`](#mc.alias.import.STDIN) 参数互斥。

##### `STDIN` {#mc.alias.import.STDIN}

*mc-cmd*

*Required*

指定命令使用标准输入（STDIN）作为导入 JSON 对象的来源。

与 [`PATH`](#mc.alias.import.PATH) 参数互斥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### JSON 格式 {#json}

JSON 对象 **必须** 采用以下格式：

```json
{
   "url" : "https://hostname:port",
   "accessKey": "<STRING>",
   "secretKey": "<STRING>",
   "api": "s3v4",
   "path": "auto"
}
```

你可以使用 [`mc alias export`](/docs/reference/minio-mc/mc-alias-export/#command-mc.alias.export) 命令从本地主机配置中导出现有别名。 或者，你也可以从 [`mc`](/docs/reference/minio-mc/#command-mc) [configuration file](/docs/reference/minio-mc/#mc-configuration) 中手动提取所需的 JSON 字段。

## 示例 {#id6}

### 使用标准输入导入别名 {#id7}

以下示例为 [play.min.io](https://play.min.io) 沙箱导入一个自定义别名。 你可以修改该示例，改为使用你已创建或已验证存在于该沙箱上的用户凭据：

```shell
echo '
{
 "url": "https://play.min.io",
 "accessKey": "minioadmin",
 "secretKey": "minioadmin",
 "api": "s3v4",
 "path": "auto"
}' | mc alias import play-minioadmin
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。