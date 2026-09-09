---
title: "mc quota info"

weight: 20
---

<a id="mc-quota-info"></a>

<a id="command-mc.quota.info"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-13T00-23-28Z**
>
> `mc quota info` 替代了 `mc admin bucket quota`。

> [!NOTE]
> **变更: RELEASE.2024-07-31T15-58-33Z**
>
> `mc quota info` 已弃用。

## 说明 {#id2}

[`mc quota info`](#command-mc.quota.info) 命令显示存储桶当前配置的配额。

## 示例 {#id3}

### 获取存储桶配额配置 {#id4}

使用 [`mc quota info`](#command-mc.quota.info) 获取存储桶当前的配额配置：

```shell
mc quota info TARGET/BUCKET
```

将 `TARGET` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为要查询配额的存储桶名称。

## 语法 {#id5}

[`mc quota info`](#command-mc.quota.info) 的语法如下：

```shell
mc quota info TARGET
```

[`mc quota info`](#command-mc.quota.info) 支持以下参数：

#### `TARGET` {#mc.quota.info.TARGET}

*mc-cmd*

*Required*

要为其创建配额的存储桶完整路径。 指定 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 作为路径前缀。 例如：

```shell
mc quota play/mybucket
```

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。