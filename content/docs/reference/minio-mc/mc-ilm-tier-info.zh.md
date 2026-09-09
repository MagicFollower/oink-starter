---
title: "mc ilm tier info"

weight: 30
---

<a id="mc-ilm-tier-info"></a>
<a id="minio-mc-ilm-tier-info"></a>

<a id="command-mc.ilm.tier.info"></a>

## 描述 {#id2}

[`mc ilm tier info`](#command-mc.ilm.tier.info) 命令可输出某个层级或某个部署上所有层级的统计信息。

### 所需权限 {#id3}

MinIO 要求具备以下权限，且权限范围限定为你要创建生命周期管理规则的一个或多个存储桶。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

此外，在为对象转换生命周期管理规则创建远程层级时，MinIO 还要求在对应集群上具备以下管理权限：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略授予在集群中任意存储桶上配置对象转换生命周期管理规则的权限：

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
            "Action": [
               "admin:SetTier",
               "admin:ListTier"
            ],
            "Effect": "Allow",
            "Sid": "EnableRemoteTierManagement"
      },
      {
            "Action": [
               "s3:PutLifecycleConfiguration",
               "s3:GetLifecycleConfiguration"
            ],
            "Resource": [
                        "arn:aws:s3:::*"
            ],
            "Effect": "Allow",
            "Sid": "EnableLifecycleManagementRules"
      }
   ]
}
```

## 语法 {#id4}

该命令的语法如下：

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例输出 `myminio` 部署上名为 `WARM-TIER` 的现有远程层级的配置信息。

```shell
 mc ilm tier info myminio WARM-TIER
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc ilm tier info TARGET TIER_NAME
```
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id5}

该命令接受以下参数：

##### `TARGET` {#mc.ilm.tier.info.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，且目标层级存在于该部署上。

##### `TIER_NAME` {#mc.ilm.tier.info.TIER_NAME}

*mc-cmd*

*Optional*

要显示的现有远程层级名称。

你 **必须** 使用全大写指定层级，例如 `WARM_TIER`。

如果未指定，MinIO 会列出该部署上所有现有层级的统计信息。

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id7}

### 显示现有层级的统计信息 {#id8}

以下示例显示 `myminio` 部署上 `WARM-TIER` 层级的统计信息。

```shell
mc ilm tier info myminio WARM-TIER
```

### 显示部署上所有现有层级的统计信息 {#id9}

以下示例显示 `myminio` 部署上所有现有层级的统计信息。

```shell
mc ilm tier info myminio
```

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id10}

有关查看层级所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。