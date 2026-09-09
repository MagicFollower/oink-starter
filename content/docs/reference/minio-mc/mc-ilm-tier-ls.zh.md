---
title: "mc ilm tier ls"

weight: 40
---

<a id="mc-ilm-tier-ls"></a>
<a id="minio-mc-ilm-tier-ls"></a>

<a id="command-mc.ilm.tier.list"></a>

<a id="command-mc.ilm.tier.ls"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc ilm tier ls`](#command-mc.ilm.tier.ls) replaces `mc admin tier ls`.

## 描述 {#id2}

[`mc ilm tier ls`](#command-mc.ilm.tier.ls) 命令显示某个部署上已配置的远程层级。

[`mc ilm tier list`](#command-mc.ilm.tier.list) 命令与 [`mc ilm tier ls`](#command-mc.ilm.tier.ls) 功能等效。

## 语法 {#id3}

该命令的语法如下：

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例输出 `myminio` 部署上现有远程层级的列表。

```shell
 mc ilm tier ls myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc ilm tier ls TARGET TIER_NAME
```
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id4}

该命令接受以下参数：

##### `TARGET` {#mc.ilm.tier.ls.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，且目标层级存在于该部署上。

### 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id6}

有关查看层级所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。