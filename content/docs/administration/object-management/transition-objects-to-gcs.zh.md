---
title: "将对象从 MinIO 迁移到 GCS"

weight: 30
---

<a id="minio-gcs"></a>
<a id="minio-lifecycle-management-transition-to-gcs"></a>

本页中的过程会创建一条新的对象生命周期管理规则，将对象从 MinIO 存储桶迁移到 Google Cloud Storage 后端上的远程存储层。该过程适用于这类场景：在达到特定时间周期或日历日期后， 将陈旧数据迁移到低成本的公有云存储方案。

## 要求 {#id2}

### 安装并配置 `mc` {#mc}

该过程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 在 MinIO 集群上执行操作。 请在一台可同时通过网络访问源集群和目标集群的机器上安装 [`mc`](/docs/reference/minio-mc/#command-mc)。 有关下载和安装 `mc` 的说明，请参见 `mc` [Installation Quickstart](/docs/reference/minio-mc/#mc-install)。

使用 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 命令为源 MinIO 集群创建别名。 创建别名时，需要为源集群和目标集群上的用户指定访问密钥。 指定的用户必须具备用于配置和应用迁移操作的 [权限](#minio-lifecycle-management-transition-to-gcs-permissions)。

<a id="minio-lifecycle-management-transition-to-gcs-permissions"></a>

### 所需的 MinIO 权限 {#minio}

MinIO 要求在您为其创建生命周期管理规则的一个或多个存储桶范围内，具备以下权限。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

此外，在为对象迁移生命周期管理规则创建远程层的集群上，MinIO 还要求具备以下管理权限：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略授予在集群中任意存储桶上配置对象迁移生命周期管理规则的权限：

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

<a id="minio-lifecycle-management-transition-to-gcs-permissions-remote"></a>

### 所需的 GCS 权限 {#gcs}

对象迁移生命周期管理规则要求在远程存储层上具备额外权限。 具体来说，MinIO 要求 <abbr title="Google Cloud Storage">GCS</abbr> 凭证对远程存储桶具备读取、写入、列出和删除权限。

有关配置所需权限的更完整说明，请参见 [GCS IAM permissions](https://cloud.google.com/storage/docs/access-control/iam-permissions) 文档。

### 远程存储桶必须已存在 {#id3}

在配置以该存储桶为目标的生命周期管理层或规则之前，请先创建远程 GCS 存储桶。

如果您设置了默认的 GCS [storage class](https://cloud.google.com/storage/docs/storage-classes)，那么在定义远程层时，如果未指定 [`storage class`](/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-storage-class)，MinIO 就会使用该默认值。 请确保记录您的 GCS 存储桶设置以及 MinIO 分层配置，以避免潜在的混淆、错误配置或其他意外结果。

## 注意事项 {#id4}

### 生命周期管理对象扫描器 {#id5}

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置的生命周期管理规则检查对象。 高 IO 工作负载或有限的系统资源导致的扫描缓慢，可能会延迟生命周期管理规则的应用。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner)。

### 对远程数据的独占访问 {#id6}

MinIO 要求对远程存储层上的已转移数据拥有独占访问权限。 “hot” MinIO 源端上的对象元数据与远程 “warm/cold” 层上的对象数据紧密关联。 如果无法访问远程层，MinIO 就无法检索对象数据； 同样，远程层也不能用于恢复源端丢失的元数据。

对已转移对象的所有访问都必须仅通过 MinIO 发起的 S3 API 操作完成。 手动修改已转移对象时，无论修改的是 “hot” MinIO 层上的元数据， 还是远程 “warm/cold” 层上的对象数据，都可能导致该对象的数据丢失。

对于远程存储桶或存储桶前缀中不受该 MinIO 部署明确管理的任何对象， MinIO 都会将其忽略。 自动转移与透明对象检索依赖以下前提：

- 不会在远程存储上由外部修改、迁移或删除对象。
- 远程存储桶上不存在生命周期管理规则 （例如转移或过期）。

MinIO 会将所有已转移对象存储在远程存储桶或资源下、 每个部署唯一的前缀值之中。 该值并非用于在后端识别源部署。 在配置远程目标时，MinIO 还支持附加一个可选的人类可读前缀， 这可能有助于诊断、维护或灾难恢复相关操作。

对于包含其他数据的远程存储层， 包括来自其他 MinIO 部署的已转移对象， MinIO 建议指定此可选前缀。 本教程包含设置此前缀所需的语法。

### 远程数据的可用性 {#id7}

MinIO 分层行为依赖远程存储在收到请求后立即返回对象 （毫秒到秒级）。 因此，MinIO 不支持需要 rehydration、等待窗口 或人工干预的远程存储。

MinIO 会为每个已转移对象创建元数据，用于标识其在远程存储中的位置。 应用程序无法脱离 MinIO 直接识别和访问已转移对象。 因此，已转移数据的可用性仍依赖于 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 和分布式部署拓扑 为 MinIO 部署中所有对象提供的核心保护能力。 使用对象转移不会带来任何额外的业务连续性或灾难恢复收益。

需要 <abbr title="Business Continuity/Disaster Recovery">BC/DR</abbr> 保护的工作负载应实现 MinIO [Server-Side replication](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)。 复制可确保对象保存在远程复制站点上， 从而使用户能够在发生部分或全部数据丢失时从远端重新同步。 有关如何使用复制在部分或全部数据丢失后恢复的更完整文档， 请参见 [重新同步（灾难恢复）](/docs/administration/bucket-replication/#minio-replication-behavior-resync)。

## 过程 {#id8}

### 1) 配置生命周期管理的用户账户和策略 {#id9}

此步骤会在 MinIO 部署上创建用于支持生命周期管理操作的用户和策略。 如果该部署已经存在具备所需 [permissions](#minio-lifecycle-management-transition-to-gcs-permissions) 的用户，则可以跳过此步骤。

以下示例使用 `Alpha` 作为 MinIO 部署 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 的占位符。 请将其替换为配置生命周期管理规则时所使用的 MinIO 部署别名。 同时，请按照所在组织的密码生成最佳实践， 将密码 `LongRandomSecretKey` 替换为足够长、随机且安全的密钥。

```shell
wget -O - https://silo.pgsty.com/extra/examples/LifecycleManagementAdmin.json | \
mc admin policy create Alpha LifecycleAdminPolicy /dev/stdin
mc admin user add Alpha alphaLifecycleAdmin LongRandomSecretKey
mc admin policy attach Alpha LifecycleAdminPolicy --user=alphaLifecycleAdmin
```

此示例假定所指定的 alias 具有在该部署上创建策略和用户所需的权限。 有关 MinIO 用户和策略的更完整文档， 请分别参见 [用户管理](/docs/administration/identity-access-management/minio-user-management/#minio-users) 和 [MinIO Policy Based Access Control](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

### 2) 配置远程存储层 {#id10}

使用 [`mc ilm tier add`](/docs/reference/minio-mc/mc-ilm-tier-add/#command-mc.ilm.tier.add) 命令将新的 Google Cloud Storage 服务添加为远程存储层：

```shell
mc ilm tier add gcs TARGET TIER_NAME \
   --bucket BUCKET \
   --prefix PREFIX \
   --credentials-file CREDENTIALS \
   --storage-class STORAGE_CLASS
```

上述示例使用了以下参数：

<table>
  <thead>
    <tr>
      <th><p>参数</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TARGET"><code>TARGET</code></a></p></td>
      <td><p>要在其上配置 GCS 远程层的 MinIO 部署的
<a href="/docs/reference/minio-mc/mc-alias/#command-mc.alias"><code>alias</code></a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.TIER_NAME"><code>TIER_NAME</code></a></p></td>
      <td><p>与新 GCS 远程存储层关联的名称。
请使用全大写指定该名称，例如 <code>GCS_TIER</code>。
下一步需要使用该值。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-bucket"><code>BUCKET</code></a></p></td>
      <td><p>MinIO 迁移对象所使用的 GCS 存储后端上的存储桶名称。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-prefix"><code>PREFIX</code></a></p></td>
      <td><p>MinIO 迁移对象时使用的可选存储桶前缀。</p><p>MinIO 会将所有已迁移对象存储到指定的 <code>BUCKET</code> 中，并使用每个部署唯一的前缀值。
省略此参数时，MinIO 仅使用该值在远程存储中隔离和组织数据。</p><p>对于包含其他数据（包括来自其他 MinIO 部署的已迁移对象）的远程存储层，
MinIO 建议指定此可选前缀。该前缀应能清晰映射到源 MinIO 部署，
以便简化与诊断、维护或灾难恢复相关的运维工作。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-credentials-file"><code>CREDENTIALS</code></a></p></td>
      <td><p>远程 GCS 层上用户的 <a href="https://cloud.google.com/docs/authentication/getting-started">credential file</a>。
指定的用户凭证必须对应一个具备所需
<a href="#minio-lifecycle-management-transition-to-gcs-permissions-remote">权限</a> 的 GCS 用户。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#mc.ilm.tier.add.-storage-class"><code>STORAGE_CLASS</code></a></p></td>
      <td><p>MinIO 应用于迁移到 GCS 存储桶中的对象的 GCS 存储类别。</p><p>MinIO 的分层行为依赖于远程存储在收到请求后立即返回对象（毫秒到秒级）。
因此，MinIO 无法支持需要回温、等待周期或人工干预的远程存储。</p><p>以下 GCS 存储类别满足 MinIO 作为远程层的要求：</p><ul><li><p><code>STANDARD</code></p></li><li><p><code>NEARLINE</code></p></li><li><p><code>COLDLINE</code></p></li></ul><p>更多信息请参见 <a href="https://cloud.google.com/storage/docs/storage-classes">GCS storage class</a>。</p></td>
    </tr>
  </tbody>
</table>

### 3) 创建并应用迁移规则 {#id11}

使用 [`mc ilm rule add`](/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add) 命令为存储桶创建新的转移规则。 以下示例将对象配置为在指定的日历天数后执行转移：

```shell
mc ilm rule add ALIAS/BUCKET \
--transition-tier TIERNAME \
--transition-days DAYS \
--noncurrent-transition-days NONCURRENT_DAYS
--noncurrent-transition-tier TIERNAME
```

上述示例指定了以下参数：

<table>
  <thead>
    <tr>
      <th><p>参数</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS"><code>ALIAS</code></a></p></td>
      <td><p>指定要为其创建生命周期管理规则的 MinIO 部署
<a href="/docs/reference/minio-mc/mc-alias/#command-mc.alias"><code>alias</code></a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS"><code>BUCKET</code></a></p></td>
      <td><p>指定要为其创建生命周期管理规则的存储桶完整路径。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-transition-tier"><code>TIERNAME</code></a></p></td>
      <td><p>MinIO 将对象转移到的远程存储层。
指定在上一步中创建的远程存储层名称。</p><p>如果要将非当前对象版本转移到不同的远程层，
请为 <a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-transition-tier"><code>--noncurrent-transition-tier</code></a>
指定另一个层名称。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-transition-days"><code>DAYS</code></a></p></td>
      <td><p>MinIO 在经过多少个日历天后将对象标记为可转移。
该值必须为整数，例如 <code>30</code> 表示 30 天。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-transition-days"><code>NONCURRENT_DAYS</code></a></p></td>
      <td><p>MinIO 在经过多少个日历天后将非当前对象版本标记为可转移。
MinIO 具体计算的是对象变为非当前版本后的时间，
而不是对象创建时间。该值必须为整数，
例如 <code>90</code> 表示 90 天。</p><p>省略此值可忽略非当前对象版本。</p><p>此选项对未启用版本控制的存储桶无效。</p></td>
    </tr>
  </tbody>
</table>

### 4) 验证迁移规则 {#id12}

使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 命令查看已配置的迁移规则：

```shell
mc ilm rule ls ALIAS/PATH --transition
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-ilm-rule-ls/#mc.ilm.rule.ls.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](/docs/reference/minio-mc/mc-ilm-rule-ls/#mc.ilm.rule.ls.ALIAS) 替换为要获取其已配置生命周期管理规则的存储桶名称。