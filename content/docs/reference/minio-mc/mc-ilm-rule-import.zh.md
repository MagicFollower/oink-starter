---
title: "mc ilm rule import"

weight: 40
---

<a id="mc-ilm-rule-import"></a>
<a id="minio-mc-ilm-rule-import"></a>

<a id="command-mc.ilm.rule.import"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm rule import` 替代 `mc ilm import`。

## 语法 {#id2}

[`mc ilm rule import`](#command-mc.ilm.rule.import) 命令导入对象生命周期管理配置， 并将其应用到 MinIO 存储桶。

[`mc ilm rule import`](#command-mc.ilm.rule.import) 命令默认从 `STDIN` 导入。 你可以从 `.json` 文件输入内容，例如由 [`mc ilm rule export`](/docs/reference/minio-mc/mc-ilm-rule-export/#command-mc.ilm.rule.export) 生成的文件。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `mydata-lifecycle-config.json` 导入生命周期管理配置， 并将其应用到 `myminio` 部署中的 `mydata` 存储桶：

```shell
mc ilm rule import myminio/mydata < mydata-lifecycle-config.json
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] ilm rule import ALIAS < STDIN
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.rule.import.ALIAS}

*mc-cmd*

*Required*

MinIO 部署上用于导入对象生命周期管理规则的存储桶的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整路径。 例如：

```text
mc ilm rule import myminio/mydata < bucket-lifecycle.json
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 导入存储桶生命周期管理配置 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `bucket-lifecycle.json` 文件导入 存储桶生命周期管理配置：

```shell
mc ilm rule import myminio/mybucket < bucket-lifecycle.json
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc ilm rule import ALIAS < file.json
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及要导入对象生命周期管理规则的存储桶：

  `myminio/mydata`
- 将 `file.json` 替换为用于导入生命周期管理规则的文件名。
{{< /tab >}}
{{< /tabs >}}

## 所需权限 {#id7}

有关导入规则所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-rule/#minio-mc-ilm-rule-permissions)。

## 行为 {#id8}

### 导入配置会覆盖现有规则 {#id9}

[`mc ilm rule import`](#command-mc.ilm.rule.import) 会使用导入的 JSON 配置中定义的规则 替换当前的存储桶生命周期管理规则。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。