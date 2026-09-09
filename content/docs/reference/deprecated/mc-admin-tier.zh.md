---
title: "mc admin tier"

weight: 190
---

<a id="mc-admin-tier"></a>

<a id="command-mc.admin.tier"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc admin tier` 已由 [`mc ilm tier`](/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier) 替代。

## 描述 {#id2}

[`mc admin tier`](#command-mc.admin.tier) 命令用于配置受支持的远程 S3 兼容服务，以支持 MinIO [Lifecycle Management: Object Transition (“Tiering”)](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration)。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

### 支持的 S3 服务 {#s3}

[`mc admin tier`](#command-mc.admin.tier) *仅* 支持将以下 S3 兼容服务用作对象分层的远程目标：

- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

### 所需权限 {#id3}

MinIO 需要以下权限，作用范围应限定为你要为其创建生命周期管理规则的一个或多个存储桶。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

MinIO 还需要在集群上具备以下管理权限，用于为对象过渡生命周期管理规则创建远程层：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略授予在集群任意存储桶上配置对象过渡生命周期管理规则的权限：

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

对象过渡生命周期管理规则需要远程存储层的额外权限。具体来说，MinIO 要求远程层凭证具备读取、写入、列举和删除权限。

例如，如果远程存储层使用基于 AWS IAM 策略的访问控制，以下策略提供了对象迁入和迁出远程层所需的权限：

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

修改 `Resource` 使其指向 MinIO 要分层写入对象的存储桶。

有关配置用户与权限以支持 MinIO 分层的更完整信息，请参考受支持分层目标的文档：

- [Amazon S3 Permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html#amazons3-actions-as-permissions)
- [Google Cloud Storage Access Control](https://cloud.google.com/storage/docs/access-control)
- [Authorizing access to data in Azure storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth?toc=/azure/storage/blobs/toc.json)

## 语法 {#id5}

#### `mc admin tier add` {#mc.admin.tier.add}

*mc-cmd*

创建一个新的远程存储层，用于通过 MinIO 生命周期管理规则过渡对象。

> [!WARNING]
> **重要**
>
> MinIO 不支持移除远程存储层。在将其添加为远程层目标 *之前*，请先确保该存储后端能够满足预期工作负载。

命令语法如下：

```shell
mc admin tier add TIER_TYPE TARGET TIER_NAME [FLAGS]
```

此命令接受以下参数：

#### `TIER_TYPE` {#mc.admin.tier.add.TIER_TYPE}

*mc-cmd*

*Required*

MinIO 用于过渡对象的云服务提供商存储后端（“Tier”）。请在以下受支持值中指定 *一个*：

<table>
  <tbody>
    <tr>
      <td><p><code>s3</code></p></td>
      <td><p>使用 AWS S3 <em>或</em> 远程 MinIO 部署作为新 Tier 的存储后端。</p><p>需要额外指定以下选项：</p><ul><li><p><a href="#mc.admin.tier.add.-access-key"><code>--access-key</code></a></p></li><li><p><a href="#mc.admin.tier.add.-secret-key"><code>--secret-key</code></a></p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>azure</code></p></td>
      <td><p>使用 Azure Blob Storage 作为新 Tier 的存储后端。</p><p>需要额外指定以下选项：</p><ul><li><p><a href="#mc.admin.tier.add.-account-name"><code>--account-name</code></a></p></li><li><p><a href="#mc.admin.tier.add.-account-key"><code>--account-key</code></a></p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>gcs</code></p></td>
      <td><p>使用 GCP Cloud Storage 作为新 Tier 的存储后端。</p><p>需要额外指定以下选项：</p><ul><li><p><a href="#mc.admin.tier.add.-credentials-file"><code>--credentials-file</code></a></p></li></ul></td>
    </tr>
  </tbody>
</table>

#### `TARGET` {#mc.admin.tier.add.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令会在该部署上创建新的远程层。

#### `TIER_NAME` {#mc.admin.tier.add.TIER_NAME}

*mc-cmd*

*Required*

与新远程层关联的名称。该名称在 MinIO 集群所有已配置层中 *必须* 唯一。

你 **必须** 使用全大写指定 tier，例如 `WARM_TIER`。

#### `--endpoint` {#mc.admin.tier.add.-endpoint}

*mc-cmd*

*Required*

云服务提供商的 URL endpoint。该 URL endpoint *必须* 能解析到 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 指定的提供商。

#### `--access-key` {#mc.admin.tier.add.-access-key}

*mc-cmd*

*Required*

远程 S3 层用户的 access key。该用户必须对远程存储桶或存储桶前缀具备读/写/列举/删除操作权限。

当 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 时必填。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `--secret-key` {#mc.admin.tier.add.-secret-key}

*mc-cmd*

*Required*

远程 S3 层用户的 secret key。

当 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 时必填。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `--account-name` {#mc.admin.tier.add.-account-name}

*mc-cmd*

*Required*

远程 Azure 层用户的 account name。该用户必须对远程存储桶或存储桶前缀具备读/写/列举/删除操作权限。

当 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `azure` 时必填。 对 `TIER_TYPE` 的其他取值，此选项无效。

MinIO *不* 支持修改与 Azure 远程层关联的 account name。Azure 存储后端与账号绑定，修改账号会改变存储后端，并导致无法访问已过渡到原账号/后端的任何对象。

#### `--account-key` {#mc.admin.tier.add.-account-key}

*mc-cmd*

*Required*

与远程 Azure 层关联的 [`--account-name`](#mc.admin.tier.add.-account-name) 对应的 account key。

当 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `azure` 时必填。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `--credentials-file` {#mc.admin.tier.add.-credentials-file}

*mc-cmd*

*Required*

远程 GCS 层用户的 [credential file](https://cloud.google.com/docs/authentication/getting-started)。该用户必须对远程存储桶或存储桶前缀具备读/写/列举/删除操作权限。

当 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `gcs` 时必填。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `--bucket` {#mc.admin.tier.add.-bucket}

*mc-cmd*

*Required*

MinIO 过渡对象所使用的远程层存储桶。

#### `--prefix` {#mc.admin.tier.add.-prefix}

*mc-cmd*

*Optional*

指定 [`--bucket`](#mc.admin.tier.add.-bucket) 下 MinIO 过渡对象使用的前缀路径。

省略此字段则将对象过渡到存储桶根路径。

#### `--storage-class` {#mc.admin.tier.add.-storage-class}

*mc-cmd*

*Optional*

MinIO 过渡对象时使用的 AWS 存储类。MinIO 仅支持以下存储类：

- `STANDARD`
- `REDUCED_REDUNDANCY`

省略时默认为 `S3_STANDARD`。

此选项仅在 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 时生效。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `--region` {#mc.admin.tier.add.-region}

*mc-cmd*

*Optional*

指定 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 的 S3 后端区域，例如 `us-west-1`。

此选项仅在 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 时生效。 对 `TIER_TYPE` 的其他取值，此选项无效。

#### `mc admin tier edit` {#mc.admin.tier.edit}

*mc-cmd*

修改或移除 MinIO 集群中的远程存储层。远程存储层支持通过 MinIO 生命周期管理规则进行对象过渡。

命令语法如下：

```shell
mc admin tier edit TARGET TIER_NAME [FLAGS]
```

此命令接受以下参数：

#### `TARGET` {#mc.admin.tier.edit.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

#### `TIER_NAME` {#mc.admin.tier.edit.TIER_NAME}

*mc-cmd*

*Required*

命令要修改的远程层名称。该值对应于创建远程层时指定的 [`mc admin tier add TIER_NAME`](#mc.admin.tier.add.TIER_NAME)。

#### `--access-key` {#mc.admin.tier.edit.-access-key}

*mc-cmd*

*Optional*

远程 S3 层用户的 access key。该用户必须对远程存储桶或存储桶前缀具备读/写/列举/删除操作权限。

此选项仅适用于 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

#### `--secret-key` {#mc.admin.tier.edit.-secret-key}

*mc-cmd*

*Optional*

远程 S3 层用户的 secret key。

此选项仅适用于 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `s3` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

#### `--account-key` {#mc.admin.tier.edit.-account-key}

*mc-cmd*

*Required*

远程 Azure 层用户的 account key。 使用此选项可轮换与远程层关联的 [`--account-name`](#mc.admin.tier.add.-account-name) 凭证。

此选项仅适用于 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `azure` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

#### `--credentials-file` {#mc.admin.tier.edit.-credentials-file}

*mc-cmd*

*Required*

远程 GCS 层用户的 credential file。该用户必须对远程存储桶或存储桶前缀具备读/写/列举/删除操作权限。

此选项仅适用于 [`TIER_TYPE`](#mc.admin.tier.add.TIER_TYPE) 为 `gcs` 的远程存储层。 对其他 `TIER_TYPE`，此选项无效。

#### `mc admin tier ls` {#mc.admin.tier.ls}

*mc-cmd*

列出 MinIO 集群上的所有远程存储层。远程存储层支持通过 MinIO 生命周期管理规则进行对象过渡。

命令语法如下：

```shell
mc admin tier ls TARGET [FLAGS]
```

此命令接受以下参数：

#### `TARGET` {#mc.admin.tier.ls.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。