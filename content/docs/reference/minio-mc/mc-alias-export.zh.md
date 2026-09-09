---
title: "mc alias export"

weight: 50
---

<a id="mc-alias-export"></a>
<a id="minio-mc-alias-export"></a>

<a id="command-mc.alias.export"></a>

> [!NOTE]
> **新增: mc.RELEASE.2023-11-15T22-45-58Z**

## 语法 {#id1}

[`mc alias export`](#command-mc.alias.export) 命令从现有的 [configuration](/docs/reference/minio-mc/#mc-configuration) 中导出别名配置。

该命令将结果输出到 `STDOUT`，你可以将输出保存为文件，*或* 按需进一步修改输出内容。

使用 [`mc alias import`](/docs/reference/minio-mc/mc-alias-import/#command-mc.alias.import) 命令导入生成的 JSON 配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从现有主机导出别名配置并输出到文件：

```shell
mc alias export play > play.json
```

该命令会将内容输出到标准输出（`STDOUT`）。 你也可以将输出通过管道传递给所选工具执行后续操作。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc alias export`](#command-mc.alias.export) 命令的语法如下：

```shell
mc [GLOBALFLAGS] alias export ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.alias.export.ALIAS}

*mc-cmd*

*Required*

要导出的别名名称。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id4}

### JSON 格式 {#json}

该命令输出一个符合以下结构的 JSON 对象：

```json
{
   "url" : "https://hostname:port",
   "accessKey": "<STRING>",
   "secretKey": "<STRING>",
   "api": "s3v4",
   "path": "auto"
}
```

你可以使用 [`mc alias import`](/docs/reference/minio-mc/mc-alias-import/#command-mc.alias.import) 导入该 JSON 文档。

## 示例 {#id5}

### 导出并转换别名 {#id6}

以下示例导出 [play.min.io](https://play.min.io) 沙箱的别名。 随后使用 [jq](https://jqlang.github.io/jq/) 工具转换该配置，并基于修改后的配置创建新别名：

```shell
mc alias export play | jq '.accessKey = "minioadmin" | .secretKey = "minioadmin"' | mc alias import play-custom
```

### 备份别名配置 {#id7}

以下命令将别名配置导出为 JSON 文件。 然后你可以按你偏好的流程备份该文件。

```shell
mc alias export play > play-backup.json
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。