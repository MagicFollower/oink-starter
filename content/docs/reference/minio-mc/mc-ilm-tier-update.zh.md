---
title: "mc ilm tier update"

weight: 60
---

<a id="mc-ilm-tier-update"></a>
<a id="minio-mc-ilm-tier-update"></a>

<a id="command-mc.ilm.tier.update"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc ilm tier update`](#command-mc.ilm.tier.update) 替代 `mc admin tier edit`。

## 描述 {#id2}

[`mc ilm tier update`](#command-mc.ilm.tier.update) 命令用于修改已配置的远程层。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

### 支持的 S3 服务 {#s3}

[`mc ilm tier`](/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier) *仅* 支持以下兼容 S3 的服务作为对象分层的远程目标：

- MinIO
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

### 所需权限 {#id3}

MinIO 要求在你创建生命周期管理规则的存储桶范围内，具备以下权限。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

MinIO 还要求在集群上具备以下管理权限，以便为对象过渡生命周期管理规则创建远程层：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略授予在集群中任意存储桶上配置对象过渡生命周期管理规则的权限：

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

#### 过渡权限 {#id4}

对象过渡生命周期管理规则在远程存储层上需要额外权限。具体而言，MinIO 要求远程层凭证提供读取、写入、列出和删除权限。

例如，如果远程存储层实现基于 AWS IAM 策略的访问控制，则以下策略提供对象在远程层之间迁入和迁出所需的权限：

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
            "Action": [
               "s3:ListBucket"
            ],
            "Effect": "Allow",
            "Resource": [
               "arn:aws:s3:::MyDestinationBucket"
            ],
            "Sid": ""
      },
      {
            "Action": [
               "s3:GetObject",
               "s3:PutObject",
               "s3:DeleteObject"
            ],
            "Effect": "Allow",
            "Resource": [
               "arn:aws:s3:::MyDestinationBucket/*"
            ],
            "Sid": ""
      }
   ]
}

```

请修改 `Resource` 为 MinIO 执行对象分层所使用的存储桶。

关于配置用户和权限以支持 MinIO 分层的更完整信息，请参阅受支持分层目标的文档：

- [Amazon S3 Permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html#amazons3-actions-as-permissions)
- [Google Cloud Storage Access Control](https://cloud.google.com/storage/docs/access-control)
- [Authorizing access to data in Azure storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth?toc=/azure/storage/blobs/toc.json)

## 语法 {#id5}

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例会更新 `myminio` 部署上名为 `S3TIER` 的现有远程层凭证。

```shell
 mc ilm tier update myminio S3TIER --access-key ACCESS_KEY --secret-key SECRET_KEY
```

运行此命令后，`myminio` 部署上的生命周期管理规则会使用该层的新凭证将对象过渡到远程位置。 命令中未修改的选项会保留其现有配置。
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc ilm tier update TARGET                         \
                   TIER_NAME                      \
                   [--account-key value]          \
                   [--access-key value]           \
                   [--az-sp-tenant-id value]      \
                   [--az-sp-client-id value]      \
                   [--az-sp-client-secret value]  \
                   [--secret-key value]           \
                   [--use-aws-role]               \
                   [--credentials-file value]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id6}

该命令接受以下参数：

##### `TARGET` {#mc.ilm.tier.update.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `TIER_NAME` {#mc.ilm.tier.update.TIER_NAME}

*mc-cmd*

*Required*

命令要修改的远程层名称。 该值对应于创建远程层时指定的 [`mc ilm tier add TIER_NAME`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_NAME)。

##### `--access-key` {#mc.ilm.tier.update.-access-key}

*mc-cmd*

*Optional*

远程 S3 或 MinIO 层上某个用户的 access key。 该用户必须具备在远程存储桶或存储桶前缀上执行 read/write/list/delete 操作的权限。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

##### `--secret-key` {#mc.ilm.tier.update.-secret-key}

*mc-cmd*

*Optional*

远程 `s3` 或 `minio` 层上某个用户的 secret key。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

##### `--use-aws-role` {#mc.ilm.tier.update.-use-aws-role}

*mc-cmd*

*Optional*

使用本地已配置的 [AWS Role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) 的访问权限。

此选项仅在 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 时适用。 对其他 `TIER_TYPE` 值，此选项无效。

##### `--account-key` {#mc.ilm.tier.update.-account-key}

*mc-cmd*

*Optional*

远程 Azure 层上某个用户的 account key。

**Azure 层类型必填**。

使用此选项轮换与远程层关联的 [`--account-name`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-account-name) 的凭证。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 的远程存储层。 对其他登录类型，此选项无效。

##### `--az-sp-tenant-id` {#mc.ilm.tier.update.-az-sp-tenant-id}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-07-03T20-17-25Z

Azure service principal account 的 Directory ID。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 的远程存储层。 对其他登录类型，此选项无效。

##### `--az-sp-client-id` {#mc.ilm.tier.update.-az-sp-client-id}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-07-03T20-17-25Z

Azure service principal account 的 Client ID。

需要 [`--az-sp-client-secret`](#mc.ilm.tier.update.-az-sp-client-secret)。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 的远程存储层。 对其他登录类型，此选项无效。

##### `--az-sp-client-secret` {#mc.ilm.tier.update.-az-sp-client-secret}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-07-03T20-17-25Z

Azure service principal account 的 secret。

需要 [`--az-sp-client-id`](#mc.ilm.tier.update.-az-sp-client-id)。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 的远程存储层。 对其他登录类型，此选项无效。

##### `--credentials-file` {#mc.ilm.tier.update.-credentials-file}

*mc-cmd*

*Optional*

**Google Cloud Storage 层类型必填**。

远程 GCS 层上某个用户的凭证文件。 该用户必须具备在远程存储桶或存储桶前缀上执行 read/write/list/delete 操作的权限。

此选项仅适用于 [`TIER_TYPE`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_TYPE) 为 `gcs` 的远程存储层。 对其他登录类型，此选项无效。

### 全局标志 {#id7}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id8}

### 轮换 S3 远程层凭证 {#id9}

以下示例更新 `myminio` 部署上名为 `S3TIER` 的 S3 远程层凭证。

```shell
mc ilm tier update myminio S3TIER --access-key ACCESS_KEY --secret-key SECRET_KEY
```

- 将 `S3TIER` 替换为你的 Amazon Simple Storage Solution 层名称。
- 将 `ACCESS_KEY` 替换为你的 S3 存储更新后的 access key。
- 将 `SECRET_KEY` 替换为上面提供的 access key 对应的更新后 secret key。

### 轮换 Azure Blob Storage 远程层凭证 {#azure-blob-storage}

以下示例更新 `myminio` 部署上名为 `AXTIER` 的 Azure 远程层凭证。

```shell
mc ilm tier update myminio AZTIER --account-key ACCOUNT-KEY
```

- 将 `AZTIER` 替换为你的 Azure 层名称。
- 将 `ACCOUNT-KEY` 替换为你的 Azure 存储更新后的密钥。

### 轮换 Google Cloud Storage 远程层凭证 {#google-cloud-storage}

以下示例更新 `myminio` 部署上名为 `GCSTIER` 的 Google Cloud Storage 远程层凭证。

```shell
 mc ilm tier update myminio GCSTIER --credentials-file /path/to/credentials.json
```

- 将 `GCSTIER` 替换为你的 Google Cloud Storage 层名称。
- 将 `/path/to/credentials.json` 替换为用于访问远程存储的更新后凭证文件路径。

### S3 兼容性 {#id10}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id11}

有关修改层所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。