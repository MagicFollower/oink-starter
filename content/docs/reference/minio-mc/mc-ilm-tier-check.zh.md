---
title: "mc ilm tier check"

weight: 20
---

<a id="mc-ilm-tier-check"></a>
<a id="minio-mc-ilm-tier-check"></a>

<a id="command-mc.ilm.tier.check"></a>

## 描述 {#id2}

[`mc ilm tier check`](#command-mc.ilm.tier.check) 命令用于显示某个部署上远程层的配置。

## 语法 {#id3}

该命令具有以下语法：

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例显示 `myminio` 部署上名为 `WARM-TIER` 的现有远程层配置。

```shell
 mc ilm tier check myminio WARM-TIER
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令具有以下语法：

```shell
mc ilm tier add TARGET TIER_NAME
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id4}

该命令接受以下参数：

##### `TARGET` {#mc.ilm.tier.check.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，且目标层存在于该部署上。

##### `TIER_NAME` {#mc.ilm.tier.check.TIER_NAME}

*mc-cmd*

*Required*

要显示的现有远程层名称。

**必须** 使用全大写指定该层，例如 `WARM_TIER`。

### 全局标志 {#id7}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id8}

### 显示现有层的配置 {#id9}

以下示例显示 `myminio` 部署上 `WARM-TIER` 层的配置。

```shell
mc ilm tier check myminio WARM-TIER
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id10}

有关查看层所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。