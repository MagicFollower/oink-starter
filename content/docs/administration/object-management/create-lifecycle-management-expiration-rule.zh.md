---
title: "对象自动过期"

weight: 50
---

<a id="minio-lifecycle-management-create-expiry-rule"></a>
<a id="id1"></a>

本页中的每个过程都会创建一条新的对象生命周期管理规则，用于让 MinIO 存储桶中的对象过期。该过程适用于在特定时间段或日历日期之后删除“旧”对象 等场景。

## 要求 {#id3}

### 安装并配置 `mc` {#mc}

该过程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 对 MinIO 集群执行操作。请在一台可同时通过网络访问源集群 和目标集群的机器上安装 [`mc`](/docs/reference/minio-mc/#command-mc)。有关下载和安装 `mc` 的说明，请参阅 `mc` [快速安装](/docs/reference/minio-mc/#mc-install)。

使用 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 命令为源 MinIO 集群和目标 S3 兼容服务创建别名。 创建别名时，需要为源集群和目标集群上的用户指定访问密钥。指定的用户必须具备 配置和应用过期操作所需的 [权限](#minio-lifecycle-management-create-expiry-rule-permissions)。

<a id="id4"></a>

### 所需权限 {#minio-lifecycle-management-create-expiry-rule-permissions}

MinIO 要求对创建生命周期管理规则的存储桶或多个存储桶授予以下权限。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

如果要在某个集群上为对象转换生命周期管理规则创建远程层，MinIO 还要求在该 集群上具备以下管理权限：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略授予了在该集群任意存储桶上配置对象转换生命周期管理规则的 权限：

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

## 按天数使对象过期 {#id5}

使用带有 [`--expire-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-days) 的 [`mc ilm rule add`](/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add)， 可在对象创建若干天后使存储桶内容过期：

```shell
mc ilm rule add ALIAS/PATH --expire-days "DAYS"
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS) 替换为 S3 兼容主机上该存储桶的 路径。
- 将 [`DAYS`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-days) 替换为对象过期前的天数。 例如，指定 `30` 表示对象会在创建 30 天后过期。

## 使已版本控制的对象过期 {#id6}

使用 [`mc ilm rule add`](/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add) 使非当前对象版本和对象删除标记过期：

- 若要让非当前对象版本在指定天数后过期，请包含 [`--noncurrent-expire-days`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-expire-days)。
- 若要让没有剩余版本的对象的删除标记过期，请包含 [`--expire-delete-marker`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-delete-marker)。

```shell
mc ilm rule add ALIAS/PATH \
   --noncurrent-expire-days NONCURRENT_DAYS \
   --expire-delete-marker
```

- 若要让对象的所有版本过期，请包含 [`--expire-all-object-versions`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-expire-all-object-versions)。此过期规则仅适用于 最新版本或当前版本不是 `DeleteMarker` 的对象。

  ```shell
  mc ilm rule add ALIAS/PATH \
     --expire-all-object-versions
  ```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.ALIAS) 替换为 S3 兼容主机上该存储桶的 路径。
- 将 [`NONCURRENT_DAYS`](/docs/reference/minio-mc/mc-ilm-rule-add/#mc.ilm.rule.add.-noncurrent-expire-days) 替换为非当前对象版本过期前的 天数。例如，指定 `30d` 表示某个版本在成为非当前版本至少 30 天后过期。