---
title: "mc ilm tier rm"

weight: 50
---

<a id="mc-ilm-tier-rm"></a>
<a id="minio-mc-ilm-tier-rm"></a>

<a id="command-mc.ilm.tier.remove"></a>

<a id="command-mc.ilm.tier.rm"></a>

## 描述 {#id2}

[`mc ilm tier rm`](#command-mc.ilm.tier.rm) 命令用于移除尚未用于转换任何对象的远程层。

[`mc ilm tier remove`](#command-mc.ilm.tier.remove) 命令与 [`mc ilm tier rm`](#command-mc.ilm.tier.rm) 具有等效功能。

> [!NOTE]
> **说明**
>
> 一旦某个层已经转换过对象，则无法将其移除。

### 所需权限 {#id3}

MinIO 要求具备以下权限，且权限范围限定为你要创建生命周期管理规则的一个或多个存储桶。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

MinIO 还要求在集群上具备以下管理权限，该集群用于为对象转换生命周期管理规则创建远程层：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略提供了在集群中任意存储桶上配置对象转换生命周期管理规则的权限：

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

该命令具有以下语法：

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例在 `myminio` 部署上移除名为 `WARM-TIER` 的现有远程层。 没有对象被转换到 `WARM-TIER` 层。

```shell
 mc ilm tier rm myminio WARM-TIER
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc ilm tier info TARGET TIER_NAME
```
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id5}

该命令接受以下参数：

##### `TARGET` {#mc.ilm.tier.rm.TARGET}

*mc-cmd*

*Required*

目标层所在的已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `TIER_NAME` {#mc.ilm.tier.rm.TIER_NAME}

*mc-cmd*

*Required*

要移除的现有远程层名称。

你 **必须** 使用全大写指定该层，例如 `WARM_TIER`。

不能有任何对象已转换到该层。

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id7}

有关移除层所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。