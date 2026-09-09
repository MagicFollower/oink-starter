---
title: "对象生命周期管理"

weight: 40
icon: fa-solid fa-clock-rotate-left
---

<a id="minio-lifecycle-management"></a>
<a id="id1"></a>

- [MinIO Object Lifecycle Management Part I](https://youtu.be/Exg2KsfzHzI?ref=docs)
- [MinIO Object Lifecycle Management Part II](https://youtu.be/5fz3rE3wjGg?ref=docs)
- [MinIO Object Lifecycle Management Lab](https://youtu.be/5fz3rE3wjGg?ref=docs)

使用 MinIO 对象生命周期管理，可以创建基于时间或日期的规则，自动迁移或过期对象。 对于对象迁移，MinIO 会自动将对象移动到已配置的远程存储层。 对于对象过期，MinIO 会自动删除该对象。

为了兼容将工作负载和生命周期规则从 S3 迁移到 MinIO 的场景，MinIO 的行为和语法遵循 [S3 lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)。 例如，您可以导出 S3 生命周期管理规则并将其导入 MinIO，反之亦然。 MinIO 使用 JSON 描述生命周期管理规则，因此在导入 S3 生命周期规则时，可能需要在 XML 与 JSON 之间进行转换。

<a id="minio-lifecycle-management-tiering"></a>

## 对象迁移（”Tiering”） {#tiering}

MinIO 支持创建对象迁移生命周期管理规则，使 MinIO 可以自动将对象移动到远程存储“层”。 MinIO 支持以下任意一种远程层目标：

- [MinIO](/docs/administration/object-management/transition-objects-to-minio/#minio-lifecycle-management-transition-to-minio)
- [Amazon S3](/docs/administration/object-management/transition-objects-to-s3/#minio-lifecycle-management-transition-to-s3)
- [Google Cloud Storage](/docs/administration/object-management/transition-objects-to-gcs/#minio-lifecycle-management-transition-to-gcs)
- [Microsoft Azure Blob Storage](/docs/administration/object-management/transition-objects-to-azure/#minio-lifecycle-management-transition-to-azure)

MinIO 对象迁移适用于这类场景：将私有云或公有云基础设施中 MinIO 集群里的陈旧数据迁移到低成本的私有云或公有云存储方案中。 目录对象，即名称以 `/` 结尾的 0 字节对象，不会被分层迁移。 MinIO 会按需管理已分层对象的取回，无需应用端添加额外逻辑。

使用 [`mc ilm tier add`](/docs/reference/minio-mc/mc-ilm-tier-add/#command-mc.ilm.tier.add) 命令为分层数据创建远程目标。 然后，您可以使用 [`mc ilm rule add --transition-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-transition-days) 命令，在指定的日历天数后将对象迁移到该层。

> [!NOTE]
> **新增: RELEASE.2022-11-10T18-20-21Z**

您可以对存储桶或存储桶前缀使用 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls)，验证对象的分层状态。 输出中会包含每个对象的存储层：

```shell
$ mc ls play/mybucket
[2022-11-08 11:30:24 PST]    52MB  STANDARD log-data.csv
[2022-11-09 12:20:18 PST]    120MB WARM event-2022-11-09.mp4
```

- `STANDARD` 表示对象存储在 MinIO 部署上。
- `WARM` 表示对象存储在同名远程层上。

> [!WARNING]
> **重要**
>
> MinIO 对象迁移支持这类成本优化策略：将较旧或陈旧的数据移动到成本优化的远程存储层，例如云存储或高密度 HDD 存储。
>
> MinIO 对象迁移 **不** 提供备份与恢复功能。 在 MinIO 发生数据丢失时，您不能将远程层用作恢复源。
>
> 如需支持备份/恢复或 <abbr title="Business Continuity / Disaster Recovery">BC/DR</abbr> 需求，请使用 [site replication](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview) 或 [bucket replication](/docs/administration/bucket-replication/#minio-bucket-replication)。

### 对远程数据的独占访问 {#id3}

MinIO 要求对远程存储层上的已转移数据拥有独占访问权限。 “hot” MinIO 源端上的对象元数据与远程 “warm/cold” 层上的对象数据紧密关联。 如果无法访问远程层，MinIO 就无法检索对象数据； 同样，远程层也不能用于恢复源端丢失的元数据。

对已转移对象的所有访问都必须仅通过 MinIO 发起的 S3 API 操作完成。 手动修改已转移对象时，无论修改的是 “hot” MinIO 层上的元数据， 还是远程 “warm/cold” 层上的对象数据，都可能导致该对象的数据丢失。

对于远程存储桶或存储桶前缀中不受该 MinIO 部署明确管理的任何对象， MinIO 都会将其忽略。 自动转移与透明对象检索依赖以下前提：

- 不会在远程存储上由外部修改、迁移或删除对象。
- 远程存储桶上不存在生命周期管理规则 （例如转移或过期）。

MinIO 会将所有已转移对象存储在远程存储桶或资源下、 每个部署唯一的前缀值之中。 该值并非用于在后端识别源部署。 在配置远程目标时，MinIO 还支持附加一个可选的人类可读前缀， 这可能有助于诊断、维护或灾难恢复相关操作。

对于包含其他数据的远程存储层， 包括来自其他 MinIO 部署的已转移对象， MinIO 建议指定此可选前缀。 本教程包含设置此前缀所需的语法。

### 远程数据的可用性 {#id4}

MinIO 分层行为依赖远程存储在收到请求后立即返回对象 （毫秒到秒级）。 因此，MinIO 不支持需要 rehydration、等待窗口 或人工干预的远程存储。

MinIO 会为每个已转移对象创建元数据，用于标识其在远程存储中的位置。 应用程序无法脱离 MinIO 直接识别和访问已转移对象。 因此，已转移数据的可用性仍依赖于 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 和分布式部署拓扑 为 MinIO 部署中所有对象提供的核心保护能力。 使用对象转移不会带来任何额外的业务连续性或灾难恢复收益。

需要 <abbr title="Business Continuity/Disaster Recovery">BC/DR</abbr> 保护的工作负载应实现 MinIO [Server-Side replication](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。 复制可确保对象保存在远程复制站点上， 从而使用户能够在发生部分或全部数据丢失时从远端重新同步。 有关如何使用复制在部分或全部数据丢失后恢复的更完整文档， 请参见 [重新同步（灾难恢复）](/docs/administration/bucket-replication/#minio-replication-behavior-resync)。

### 启用版本控制的存储桶 {#id5}

对于已启用 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的存储桶迁移规则，MinIO 采用 [S3 behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html#intro-lifecycle-rules-actions)。 具体来说，MinIO 默认将迁移操作应用于对象的 *当前* 版本。

如需迁移对象的非当前版本，请在创建迁移规则时指定 [`--noncurrent-transition-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-transition-days) 和 [`--noncurrent-transition-tier`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-transition-tier) 选项。

<a id="id6"></a>

## 对象过期 {#minio-lifecycle-management-expiration}

MinIO 生命周期管理支持对存储桶中的对象执行过期操作。 对象“过期”是指对该对象执行 `DELETE` 操作。 例如，您可以创建生命周期管理规则，使所有超过 365 天的对象过期。

使用 [`mc ilm rule add --expire-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-days) 可以让对象在指定的日历天数后过期。

对于已配置 [replication](/docs/administration/bucket-replication/#minio-bucket-replication) 的存储桶，MinIO 不会复制由生命周期管理过期规则删除的对象。 更多信息请参见 [删除操作的复制](/docs/administration/bucket-replication/#minio-replication-behavior-delete)。

### 启用版本控制的存储桶 {#id7}

对于已启用 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的存储桶过期规则，MinIO 采用 [S3 behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html#intro-lifecycle-rules-actions)。 对于启用版本控制的存储桶，MinIO 具有以下默认行为：

- MinIO 仅将过期选项应用于对象的 *当前* 版本，具体方式是像版本化删除的常规行为一样创建 `DeleteMarker`。

  如需让对象的非当前版本过期，请在创建过期规则时指定 [`--noncurrent-expire-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-expire-days) 选项。
- MinIO 不会让 `DeleteMarkers` 过期，即使该对象已不存在其他版本。

  如需在该对象已无剩余版本时让删除标记过期，请在创建过期规则时指定 [`--expire-delete-marker`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-delete-marker) 选项。
- 如需让一个没有删除标记的对象在指定天数后其所有版本都过期，请将 [`--expire-all-object-versions`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-all-object-versions) 标志与 [`--expire-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-days) 标志一同使用。 这允许该对象在指定天数过去后被永久删除。

  > [!NOTE]
  > **变更: MinIO**
  >
  > RELEASE.2024-05-01T01-11-10Z
  >
  > 此标志仅适用于没有删除标记的对象。

<a id="id8"></a>

## 生命周期管理对象扫描器 {#minio-lifecycle-management-scanner}

MinIO 使用内置的 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 主动检查对象是否符合所有已配置的生命周期管理规则。

扫描器是一个低优先级进程，在 <abbr title="Input / Output">I/O</abbr> 负载较高时会让出资源，以避免因规则触发时机导致性能尖峰。 因此，扫描器可能要到生命周期规则周期已经过去 *之后*，才会检测到某个对象已满足配置的迁移或过期生命周期规则条件。