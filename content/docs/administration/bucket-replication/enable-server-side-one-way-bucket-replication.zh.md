---
title: "启用服务端单向存储桶复制"

weight: 20
---

<a id="minio-bucket-replication-serverside-oneway"></a>
<a id="id1"></a>

本页面中的过程会创建一条新的存储桶复制规则，用于将对象从一个 MinIO 存储桶单向复制到另一个 MinIO 存储桶。 这些存储桶既可以位于同一个 MinIO 部署中，也可以位于不同的 MinIO 部署中。

<img src="/images/replication/active-passive-oneway-replication.svg" alt="主动-被动复制会将数据从源 MinIO 部署同步到远程 MinIO 部署。" style="max-width: 800px; height: auto;" />

- 如需在 MinIO 存储桶之间配置双向“active-active”复制，请参见 [启用双向服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway)。
- 如需在 MinIO 部署之间配置多站点“active-active”复制，请参见 [启用多站点服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-multi-site-bucket-replication/#minio-bucket-replication-serverside-multi)

> [!NOTE]
> **说明**
>
> 如需在任意兼容 S3 的服务之间配置复制（不一定是 MinIO），请使用 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror)。

## 要求 {#id3}

复制要求所有参与的集群满足 [以下要求](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements)。 本过程假定你已经审阅并验证了这些要求。

如需更多详细信息，请参见 [存储桶复制要求](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements) 页面。

## 注意事项 {#id4}

点击展开以下任一项：

> [!DETAILS]- 现有对象的复制
> MinIO 支持自动复制存储桶中的现有对象。
>
> MinIO 要求使用 [`mc replicate add --replicate`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-replicate) 或 [`mc replicate update --replicate`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-replicate) 显式启用现有对象复制，并包含 `existing-objects` 复制功能标志。 本过程包含启用现有对象复制所需的标志。

> [!DETAILS]- 删除操作的复制
> MinIO 支持将 S3 `DELETE` 操作复制到目标存储桶。 具体来说，MinIO 可以复制版本控制的 [Delete Markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/versioning-workflows.html)，以及删除特定版本对象的操作：
>
> - 对于对象的删除操作，MinIO 复制也会在目标存储桶上创建删除标记。
> - 对于对象某个版本的删除操作，MinIO 复制也会在目标存储桶上删除这些版本。
>
> MinIO 要求使用 [`mc replicate add --replicate`](/docs/reference/minio-mc/mc-replicate-add/#mc.replicate.add.-replicate) 或 [`mc replicate update --replicate`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-replicate) 显式启用删除操作复制。 本过程包含启用删除操作和删除标记复制所需的标志。
>
> MinIO *不会* 复制因应用 [生命周期管理过期规则](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 而产生的删除操作。
>
> 更完整的文档请参见 [删除操作的复制](/docs/administration/bucket-replication/#minio-replication-behavior-delete) 和 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

> [!DETAILS]- 多站点复制
> MinIO 支持为每个存储桶或存储桶前缀配置多个远程目标。 例如，你可以将一个存储桶配置为把数据复制到两个或更多远程 MinIO 部署，其中一个部署是 1:1 副本（复制包括删除在内的所有操作），另一个部署则是完整的历史记录（仅复制非破坏性的写入操作）。
>
> 本过程说明了到单个远程 MinIO 部署的单向复制。 你可以重复本教程，将单个存储桶复制到多个远程目标。

## 过程 {#id5}

- **[使用命令行配置单向存储桶复制](#minio-bucket-replication-one-way-minio-cli-procedure)**

  > - [创建复制远程目标](#minio-bucket-replication-one-way-minio-cli-create-remote-targets)
  > - [创建新的存储桶复制规则](#minio-bucket-replication-one-way-minio-cli-create-replication-rules)
  > - [验证复制配置](#minio-bucket-replication-one-way-minio-cli-verify-replication-config)

<a id="minio-bucket-replication-one-way-minio-cli-procedure"></a>

### 使用命令行 `mc` 配置单向存储桶复制 {#mc}

本过程使用 [别名](/docs/reference/minio-mc/mc-alias-set/#alias) `SOURCE` 和 `REMOTE` 来引用每个配置了复制的 MinIO 部署。 请将这些值替换为你的目标 MinIO 部署对应的别名。

本过程假定每个别名都对应一个具有 [必要复制权限](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-serverside-oneway-permissions) 的用户。

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 会自动创建所需的复制目标，因此不再需要使用已弃用的 `mc admin remote bucket add` 命令。 本过程仅说明该版本起的操作流程。

<a id="minio-bucket-replication-one-way-minio-cli-create-remote-targets"></a>
<a id="id6"></a>

#### 1) 创建新的存储桶复制规则 {#minio-bucket-replication-one-way-minio-cli-create-replication-rules}

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

<a id="id7"></a>

#### 2) 验证复制配置 {#minio-bucket-replication-one-way-minio-cli-verify-replication-config}

在其中一个部署上，使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 将新对象复制到已启用复制的存储桶中。

```shell
mc cp ~/foo.txt ALIAS/BUCKET
```

使用 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls) 验证目标存储桶中存在该对象：

```shell
mc ls ALIAS/BUCKET
```

> [!NOTE]
> **另请参阅**
>
> - 使用 [`mc replicate update`](/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update) 命令修改现有复制规则。
> - 使用 [`mc replicate update`](/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update) 命令并配合 [`--state "disable"`](/docs/reference/minio-mc/mc-replicate-update/#mc.replicate.update.-state) 标志禁用现有复制规则。
> - 使用 [`mc replicate rm`](/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm) 命令删除现有复制规则。