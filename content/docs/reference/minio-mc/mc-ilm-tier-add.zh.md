---
title: "mc ilm tier add"

weight: 10
---

<a id="mc-ilm-tier-add"></a>
<a id="minio-mc-ilm-tier-add"></a>

<a id="command-mc.ilm.tier.add"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc ilm tier add`](#command-mc.ilm.tier.add) 替代了 `mc admin tier add`。

## 描述 {#id2}

[`mc ilm tier add`](#command-mc.ilm.tier.add) 命令在受支持的存储服务上创建一个新的远程存储层。

完整列表请参见 [对象转换](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering)。

### 支持的 S3 服务 {#s3}

[`mc ilm tier add`](#command-mc.ilm.tier.add) *仅* 支持以下 S3 兼容服务作为对象分层的远程目标：

- MinIO
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

### 权限 {#id5}

在为对象转换生命周期管理规则创建远程层的集群上，MinIO 需要以下管理权限：

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

## 语法 {#id6}

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例在 `myminio` 部署上创建一个名为 `WARM-MINIO-TIER` 的新远程层。 该命令为位于主机名 `https://warm-minio.com` 的远程 MinIO 部署创建一个层。

```shell
 mc ilm tier add minio myminio WARM-MINIO-TIER                     \
                               --endpoint https://warm-minio.com   \
                               --access-key ACCESSKEY              \
                               --secret-key SECRETKEY              \
                               --bucket mybucket                   \
                               --prefix myprefix/
```

`myminio` 部署上的生命周期管理规则可以使用该新层，将对象转换到远程位置 `mybucket` 存储桶中的 `myprefix/` 前缀下。
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc ilm tier add TIER_TYPE                    \
                TARGET                       \
                TIER_NAME                    \
                --bucket value               \
                [--endpoint string]          \
                [--region string]            \
                [--access-key value^]        \
                [--secret-key value^]        \
                [--use-aws-role^]            \
                [--aws-role-arn^]            \
                [--aws-web-identity-file^]   \
                [--azure-sp-tenant-id^]      \
                [--azure-sp-client-id^]      \
                [--azure-sp-client-secret^]  \
                [--account-name value^]      \
                [--account-key value^]       \
                [--credentials-file value^]  \
                [--prefix value]             \
                [--storage-class value]
```

**注意：** 每个受支持的存储供应商使用不同的认证方式。 用于认证的标志因存储供应商而异。 详见下方 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE)。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id11}

该命令接受以下参数：

##### `TIER_TYPE` {#mc.ilm.tier.add.TIER_TYPE}

*mc-cmd*

*Required*

MinIO 将对象转换到的云服务提供商存储后端（”Tier”）。 指定以下受支持值之一：

<table>
  <tbody>
    <tr>
      <td><p><code>minio</code></p></td>
      <td><p>使用远程 MinIO 部署作为新 Tier 的存储后端。</p><p>还需要指定以下参数：</p><ul><li><p><a href="#mc.ilm.tier.add.-access-key"><code>--access-key</code></a></p></li><li><p><a href="#mc.ilm.tier.add.-secret-key"><code>--secret-key</code></a></p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>s3</code></p></td>
      <td><p>使用 AWS S3 作为新 Tier 的存储后端。</p><p>还需要指定以下参数：</p><ul><li><p><a href="#mc.ilm.tier.add.-access-key"><code>--access-key</code></a></p></li><li><p><a href="#mc.ilm.tier.add.-secret-key"><code>--secret-key</code></a></p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>azure</code></p></td>
      <td><p>使用 Azure Blob Storage 作为新 Tier 的存储后端。</p><p>还需要指定以下参数：</p><ul><li><p><a href="#mc.ilm.tier.add.-account-name"><code>--account-name</code></a></p></li><li><p><a href="#mc.ilm.tier.add.-account-key"><code>--account-key</code></a></p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>gcs</code></p></td>
      <td><p>使用 GCP Cloud Storage 作为新 Tier 的存储后端。</p><p>还需要指定以下参数：</p><ul><li><p><a href="#mc.ilm.tier.add.-credentials-file"><code>--credentials-file</code></a></p></li></ul></td>
    </tr>
  </tbody>
</table>

##### `TARGET` {#mc.ilm.tier.add.TARGET}

*mc-cmd*

*Required*

命令在该已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 上创建新的远程层。 随后你可以使用 [`mc ilm rule add`](/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add) 并指定该新远程层来创建新规则。

##### `TIER_NAME` {#mc.ilm.tier.add.TIER_NAME}

*mc-cmd*

*Required*

与新远程层关联的名称。 该名称 **必须** 在 MinIO 集群所有已配置层中唯一。

你 **必须** 使用全大写指定 tier，例如 `WARM_TIER`。

##### `--endpoint` {#mc.ilm.tier.add.-endpoint}

*mc-cmd*

*Optional*

S3 或 MinIO 存储的 URL endpoint。 URL endpoint **必须** 解析到 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 指定的提供方。

对 `s3` 或 `minio` tier 类型为必需，对 `azure` 为可选。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--access-key` {#mc.ilm.tier.add.-access-key}

*mc-cmd*

*Optional*

远程 `S3` 或 `minio` tier 类型中某个用户的 access key。 该用户必须具有对远程存储桶或存储桶前缀执行 read/write/list/delete 操作的权限。

当 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 时必需。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--secret-key` {#mc.ilm.tier.add.-secret-key}

*mc-cmd*

*Optional*

远程 `s3` 或 `minio` tier 类型中某个用户的 secret key。

当 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 时必需。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--account-name` {#mc.ilm.tier.add.-account-name}

*mc-cmd*

*Optional*

用作远程存储资源的 [Storage Account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)。

当 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 时必需。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

MinIO *不* 支持更改与 Azure 远程 tier 关联的存储账户名。 Azure 存储后端绑定到存储账户，因此更改该值会更换存储后端，并导致无法访问已转换到原账户/后端的任何对象。

##### `--account-key` {#mc.ilm.tier.add.-account-key}

*mc-cmd*

*Optional*

与远程 Azure tier 关联的 [`--account-name`](#mc.ilm.tier.add.-account-name) 对应的共享 account key。

该 account key 必须绑定具备所需 [权限](/docs/administration/object-management/transition-objects-to-azure/#minio-lifecycle-management-transition-to-azure-permissions-remote) 的 Azure 策略。

当 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 时必需。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--credentials-file` {#mc.ilm.tier.add.-credentials-file}

*mc-cmd*

*Optional*

远程 Google Cloud Storage tier 中用户使用的 [credential file](https://cloud.google.com/docs/authentication/getting-started)。 该用户必须具有对远程存储桶或存储桶前缀执行 read/write/list/delete 操作的权限。

当 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `gcs` 时必需。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--bucket` {#mc.ilm.tier.add.-bucket}

*mc-cmd*

*Required*

MinIO 将对象转换到的远程 tier 存储桶。

对于 `azure` 远程 tier，该值对应 [Container name](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction#containers)

##### `--prefix` {#mc.ilm.tier.add.-prefix}

*mc-cmd*

*Optional*

MinIO 将对象转换到指定 [`--bucket`](#mc.ilm.tier.add.-bucket) 的前缀路径。

省略此字段可将对象转换到存储桶根路径。

##### `--storage-class` {#mc.ilm.tier.add.-storage-class}

*mc-cmd*

*Optional*

MinIO 应用于转换到远程存储桶对象的 storage class（在 Microsoft Azure 中称为 “access tier”）。

应用于 MinIO 转换到远程存储桶对象的 storage class。 MinIO 分层行为依赖远程存储在请求后立即返回对象（毫秒到秒级）。 因此 MinIO *无法* 支持需要 rehydration、等待周期或手动干预的远程存储。

选择与 `TIER_TYPE` 对应的选项卡，查看各层支持的值：

{{< tabs group="minio-s3-gcs-azure" >}}
{{< tab label="minio" value="minio" >}}
- `STANDARD` *推荐*
- `REDUCED`

更多信息请参见 [纠删码存储类](/docs/reference/minio-server/settings/storage-class/#minio-ec-storage-class)。
{{< /tab >}}
{{< tab label="s3" value="s3" >}}
- `STANDARD`
- `STANDARD-IA`
- `ONEZONE-IA`

更多信息请参见 [使用 Amazon S3 存储类](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)。
{{< /tab >}}
{{< tab label="gcs" value="gcs" >}}
- `STANDARD`
- `NEARLINE`
- `COLDLINE`

更多信息请参见 [GCS 存储类](https://cloud.google.com/storage/docs/storage-classes)。
{{< /tab >}}
{{< tab label="azure" value="azure" >}}
- `Hot`
- `Cool`

更多信息请参见 [Blob 数据的 Hot、Cool 和 Archive 访问层](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview)。
{{< /tab >}}
{{< /tabs >}}

若省略，对象将使用远程存储桶定义的默认存储类。

##### `--region` {#mc.ilm.tier.add.-region}

*mc-cmd*

*Optional*

指定 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 的 S3 后端区域，例如 `us-west-1`。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 时生效。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--use-aws-role` {#mc.ilm.tier.add.-use-aws-role}

*mc-cmd*

*Optional*

使用本地配置的 [AWS Role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) 的访问权限。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` 或 `minio` 时生效。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--aws-role-arn` {#mc.ilm.tier.add.-aws-role-arn}

*mc-cmd*

*Optional*

转换对象时要使用的 AWS S3 角色名称。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` **且** 源端是 Amazon EKS 上的 MinIO pod 时生效。

##### `--aws-web-identity-file` {#mc.ilm.tier.add.-aws-web-identity-file}

*mc-cmd*

*Optional*

指定转换对象时使用的 web identity token 文件。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `s3` **且** 源端是 Amazon EKS 上的 MinIO pod 时生效。

##### `--azure-sp-tenant-id` {#mc.ilm.tier.add.-azure-sp-tenant-id}

*mc-cmd*

*Optional*

用于登录 Azure 存储的 [service principal account](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1) 的 Tenant ID。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 且使用 service principal 身份登录时生效。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--azure-sp-client-id` {#mc.ilm.tier.add.-azure-sp-client-id}

*mc-cmd*

*Optional*

用于登录 Azure 存储的 [service principal account](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1) 的 Client ID。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 且使用 service principal 身份登录时生效。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

##### `--azure-sp-client-secret` {#mc.ilm.tier.add.-azure-sp-client-secret}

*mc-cmd*

*Optional*

用于登录 Azure 存储的 [service principal account](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1) 的 client secret。

该选项仅在 [`TIER_TYPE`](#mc.ilm.tier.add.TIER_TYPE) 为 `azure` 且使用 service principal 身份登录时生效。 对 `TIER_TYPE` 的任何其他取值，该选项均无效。

### 全局标志 {#id22}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id23}

### 配置一个 Tier 以将对象转换到 MinIO 部署 {#tier-minio}

以下示例在本地部署上创建一个新层，已配置规则可使用该层将对象转换到独立的远程 MinIO 部署。

```shell
mc ilm tier add minio myminio WARM-MINIO-TIER --endpoint https://warm-minio.com \
     --access-key ACCESSKEY --secret-key SECRETKEY --bucket mybucket --prefix myprefix/
```

该命令在 `myminio` 部署上为 `minio` 类型远程存储创建一个名为 `WARM-MINIO-TIER` 的新层。

- 远程 MinIO 存储位于 `https://warm-minio.com`。
- 命令中包含了一个对该存储桶及前缀具备 read、write、list 和 delete 权限用户的凭据。
- 该层会将对象转换到远程 MinIO 存储上的 `mybucket` 存储桶与 `myprefix` 前缀。

### 配置一个 Tier 以将对象转换到 Azure Blob Storage 位置 {#tier-azure-blob-storage}

以下示例在本地部署上创建一个新层，已配置规则可使用该层将对象转换到 Azure Blob Storage。

```shell
mc ilm tier add azure myminio AZTIER --account-name ACCOUNT-NAME --account-key ACCOUNT-KEY \
     --bucket myazurebucket --prefix myazureprefix/
```

该命令在 `myminio` 部署上为 `azure` 类型远程存储创建一个名为 `AZTIER` 的新层。

- 使用提供的 account name 和 key 访问远程 Azure 存储。
- 该层会将对象转换到 Azure 存储上的 `myazurebucket` 存储桶与 `myazureprefix` 前缀。

### 配置一个 Tier 以将对象转换到 Google Cloud Storage {#tier-google-cloud-storage}

以下示例在本地部署上创建一个新层，已配置规则可使用该层将对象转换到 Google Cloud Storage。

```shell
 mc ilm tier add gcs myminio GCSTIER --credentials-file /path/to/credentials.json \
     --bucket mygcsbucket  --prefix mygcsprefix/
```

该命令在 `myminio` 部署上为 `gcs` 类型远程存储创建一个名为 `GCSTIER` 的新层。

- 使用提供的 credentials file 访问远程 GCS 存储。
- 该层会将对象转换到 GCS 存储上的 `mygcsbucket` 存储桶与 `mygcsprefix` 前缀。

### 配置一个 Tier 以将对象转换到 Amazon Simple Storage Service (S3) {#tier-amazon-simple-storage-service-s3}

以下示例在本地部署上创建一个新层，已配置规则可使用该层将对象转换到 S3 上的 STANDARD 存储。

```shell
 mc ilm tier add s3 myminio S3TIER --endpoint https://s3.amazonaws.com \
     --access-key ACCESSKEY --secret-key SECRETKEY --bucket mys3bucket --prefix mys3prefix/ \
     --storage-class "STANDARD" --region us-west-2
```

该命令在 `myminio` 部署上为 `s3` 类型远程存储创建一个名为 `S3TIER` 的新层。

- S3 存储位于提供的 endpoint。
- 使用提供的 access key 和 secret key 访问远程 S3 存储。
- 该层会将对象转换到 GCS 存储上的 `mys3bucket` 存储桶与 `mys3prefix` 前缀。
- 该层使用位于 `us-west-2` S3 区域的 S3 `STANDARD` 存储类。

### S3 兼容性 {#id24}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

## 所需权限 {#id25}

有关添加 tier 所需的权限，请参见父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-tier/#minio-mc-ilm-tier-permissions)。