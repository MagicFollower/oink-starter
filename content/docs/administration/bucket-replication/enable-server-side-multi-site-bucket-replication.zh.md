---
title: "启用多站点服务端存储桶复制"

weight: 40
---

<a id="minio-bucket-replication-serverside-multi"></a>
<a id="id1"></a>

本页中的过程用于在多个 MinIO 部署之间配置自动化的服务端存储桶复制。多站点 Active-Active 复制基于 [启用双向服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway) 过程，并增加了额外注意事项，以确保所有站点上的复制行为可预测。

<img src="/images/replication/active-active-multi-replication.svg" alt="Active-Active 复制可在多个远程部署之间同步数据。" style="max-width: 600px; height: auto;" />

- 如需在任意 S3 兼容服务之间配置复制，请使用 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror)。
- 如需在两个 MinIO 部署之间配置单向 “active-active” 复制，请参阅 [启用双向服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway)。
- 如需在 MinIO 部署之间配置单向 “active-passive” 复制，请参阅 [启用服务端单向存储桶复制](/docs/administration/bucket-replication/enable-server-side-one-way-bucket-replication/#minio-bucket-replication-serverside-oneway)。

多站点 Active-Active 复制配置可以跨越多个机架、数据中心或地理位置。多站点配置的部署与维护复杂度通常会随着站点数量和每个站点规模的增加而提高。计划实施多站点复制的企业应考虑借助 [MinIO SUBNET](https://min.io/pricing?ref=docs) 支持，以获取应对此类用例所需的专业知识、规划能力和工程资源。

> [!NOTE]
> **另请参阅**
>
> - 使用 [`mc replicate update`](/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update) 命令修改现有复制规则。
> - 使用带有 [`--state "disable"`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-state) 标志的 [`mc replicate update`](/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update) 命令禁用现有复制规则。
> - 使用 [`mc replicate rm`](/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm) 命令删除现有复制规则。

<a id="id3"></a>

## 要求 {#minio-bucket-replication-serverside-multi-requirements}

你必须满足 [Bucket Replication Requirements](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements) 中描述的所有存储桶复制基础要求。

此外，要创建多站点存储桶复制配置，你还必须满足以下额外要求：

### 访问所有集群 {#id4}

要设置多站点 Active-Active 存储桶复制，你必须具备访问所有部署的网络连通性，以及具有正确权限的登录凭证。

你可以通过安装 [`mc`](/docs/reference/minio-mc/#command-mc) 并使用命令行访问这些部署。 使用 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 命令为每个 MinIO 部署创建别名。

创建别名时，需要指定该部署上某个用户的 access key。 该用户 **必须** 具有在该部署上创建和管理用户及策略的权限。

具体来说，请确保该用户 *至少* 具有以下权限：

- [`admin:CreateUser`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-CreateUser)
- [`admin:ListUsers`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListUsers)
- [`admin:GetUser`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-GetUser)
- [`admin:CreatePolicy`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-CreatePolicy)
- [`admin:GetPolicy`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-GetPolicy)
- [`admin:AttachUserOrGroupPolicy`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-AttachUserOrGroupPolicy)

## 注意事项 {#id5}

点击展开以下任意条目：

> [!DETAILS]- 使用一致的复制设置
> MinIO 支持自定义复制配置，以启用或禁用以下复制行为：
>
> - 复制 [delete operations](/docs/administration/object-management/object-delete/#minio-object-delete)
> - 复制删除标记
> - 复制现有对象
> - 复制仅元数据变更
>
> 为存储桶配置复制规则时，请确保参与多站点复制的所有 MinIO 部署使用 *相同* 的复制行为，以保证对象同步的一致性和可预测性。

> [!DETAILS]- 现有对象复制
> MinIO 支持自动复制存储桶中的现有对象。
>
> MinIO 要求使用 [`mc replicate add --replicate`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-replicate) 或 [`mc replicate update --replicate`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-replicate) 显式启用现有对象复制，并包含 `existing-objects` 复制功能标志。 本过程包含用于启用现有对象复制的必需标志。

> [!DETAILS]- 删除操作复制
> MinIO 支持将 [delete operations](/docs/administration/object-management/object-delete/#minio-object-delete) 复制到目标存储桶。 具体来说，MinIO 可以复制版本控制中的 [Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html)，以及删除指定版本对象的操作：
>
> - 对对象执行删除操作时，MinIO 复制也会在目标存储桶上创建删除标记。
> - 对对象的某个版本执行删除操作时，MinIO 复制也会在目标存储桶上删除这些版本。
>
> MinIO 要求使用 [`mc replicate add --replicate`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-replicate) 或 [`mc replicate update --replicate`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-replicate) 显式启用删除操作复制。 本过程包含用于启用删除操作和删除标记复制的必需标志。
>
> MinIO *不会* 复制因应用 [lifecycle management expiration rules](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 而产生的删除操作。 请在所有复制站点上为该存储桶配置一致的过期规则，以确保对象过期策略得到一致应用。

## 过程 {#id6}

对于参与多站点复制配置的每个 MinIO 部署，都需要重复执行本过程中的步骤。根据部署数量的不同，该过程在实施时可能需要投入大量时间并格外谨慎。MinIO 建议在尝试执行文档中的步骤之前，先完整阅读本过程。

- 使用命令行配置多站点存储桶复制

  > - [创建新的存储桶复制规则](#minio-bucket-replication-multi-site-minio-cli-create-replication-rules)
  > - [验证复制配置](#minio-bucket-replication-multi-site-minio-cli-verify-replication-config)

### 使用命令行 `mc` 配置多站点存储桶复制 {#mc}

本过程使用占位符 `ALIAS` 来引用每个被配置为复制端点的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。 请将这些值替换为各个 MinIO 部署对应的实际别名。

本过程假设每个别名都对应一个具备 [necessary replication permissions](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements) 的用户。

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 会自动创建所需的复制目标，因此不再需要使用已弃用的 `mc admin remote bucket add` 命令。 本过程仅记录该版本及之后的操作方式。

<a id="id7"></a>

#### 1) 创建新的存储桶复制规则 {#minio-bucket-replication-multi-site-minio-cli-create-replication-rules}

使用 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 命令，为每个 MinIO 部署添加新的复制规则。

```shell
mc replicate add ALIAS/BUCKET \
   --remote-bucket 'https://USER:PASSWORD@HOSTNAME:PORT/BUCKET' \
   --replicate "delete,delete-marker,existing-objects"
```

- 将 `ALIAS` 替换为源 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。 该名称 *必须* 与上一步创建远端目标时指定的存储桶名称一致。
- 将 `BUCKET` 替换为源部署上要作为复制源的存储桶名称。
- 使用 `--remote-bucket` 指定 `ALIAS/BUCKET` 要复制到的远端 MinIO 部署和存储桶。

  `USER:PASSWORD` 必须对应远端部署上具有 [所需复制权限](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway-permissions) 的用户。

  `HOSTNAME:PORT` 必须能解析到远端部署上可访问的 MinIO 实例。 `BUCKET` 必须已存在，并满足其他所有 [复制要求](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements)。
- `--replicate "delete,delete-marker,existing-objects"` 标志会启用以下复制功能：

  - [删除复制](/docs/administration/bucket-replication/#minio-replication-behavior-delete)
  - [现有对象复制](/docs/administration/bucket-replication/#minio-replication-behavior-existing-objects)

  有关更完整的文档，请参阅 [`mc replicate add --replicate`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-replicate)。 省略任意字段即可禁用对应组件的复制。

可按需为 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 指定其他受支持的可选参数。

对于参与多站点复制配置的每个远程 MinIO 部署，都要重复执行这些命令。 例如，一个由 MinIO 部署 `minio1`、`minio2` 和 `minio3` 组成的多站点复制配置，需要在每个部署上针对每个远程端重复执行此步骤。

具体来说，在这种场景下，需要在每个部署上执行两次此步骤：

- 在 `minio1` 部署上，为 `minio2` 创建一条规则，再为 `minio3` 单独创建另一条规则。
- 在 `minio2` 部署上，为 `minio1` 创建一条规则，再为 `minio3` 单独创建另一条规则。
- 在 `minio3` 部署上，为 `minio1` 创建一条规则，再为 `minio2` 单独创建另一条规则。

<a id="id8"></a>

#### 2) 验证复制配置 {#minio-bucket-replication-multi-site-minio-cli-verify-replication-config}

在其中一个部署上，使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 将新对象复制到已启用复制的存储桶中。

```shell
mc cp ~/foo.txt ALIAS/BUCKET
```

使用 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls) 验证目标存储桶中存在该对象：

```shell
mc ls ALIAS/BUCKET
```

在每个部署上重复执行此测试：复制一个新的唯一文件，并检查该文件是否已复制到其他每个部署。

你也可以使用 [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat) 检查该文件，以查看对象当前的 [replication stage](/docs/administration/bucket-replication/#minio-replication-process)。