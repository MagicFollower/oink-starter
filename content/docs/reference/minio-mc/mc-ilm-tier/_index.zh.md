---
title: "mc ilm tier"

weight: 30
icon: fa-solid fa-layer-group
---

<a id="mc-ilm-tier"></a>

<a id="command-mc.ilm.tier"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> [`mc ilm tier`](#command-mc.ilm.tier) replaces `mc admin tier`.

## 说明 {#id2}

[`mc ilm tier`](#command-mc.ilm.tier) 命令及其子命令用于为 MinIO 的 [生命周期管理：对象过渡（“分层”）](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 配置受支持的远程 S3 兼容服务。

使用此命令创建一个或多个层后，可使用 [`mc ilm rule`](/docs/reference/minio-mc/mc-ilm-rule/#command-mc.ilm.rule) 及其子命令创建将对象迁移到其他存储的规则。

有关更多信息，请参阅 [生命周期管理](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 概述。

## 子命令 {#id3}

[`mc ilm tier`](#command-mc.ilm.tier) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#command-mc.ilm.tier.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#command-mc.ilm.tier.add"><code>mc ilm tier add</code></a> 命令在受支持的存储服务上创建一个新的远程存储层。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-check/#command-mc.ilm.tier.check"><code>check</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-check/#command-mc.ilm.tier.check"><code>mc ilm tier check</code></a> 命令用于显示某个部署上远程层的配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-info/#command-mc.ilm.tier.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-info/#command-mc.ilm.tier.info"><code>mc ilm tier info</code></a> 命令可输出某个层级或某个部署上所有层级的统计信息。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-ls/#command-mc.ilm.tier.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-ls/#command-mc.ilm.tier.ls"><code>mc ilm tier ls</code></a> 命令显示某个部署上已配置的远程层级。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-rm/#command-mc.ilm.tier.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-rm/#command-mc.ilm.tier.rm"><code>mc ilm tier rm</code></a> 命令用于移除尚未用于转换任何对象的远程层。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-update/#command-mc.ilm.tier.update"><code>update</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-tier-update/#command-mc.ilm.tier.update"><code>mc ilm tier update</code></a> 命令用于修改已配置的远程层。</p></td>
    </tr>
  </tbody>
</table>

<a id="id4"></a>

## 所需权限 {#minio-mc-ilm-tier-permissions}

要为对象过渡创建层，MinIO 要求在集群上具有以下管理权限：

- [`admin:SetTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-SetTier)
- [`admin:ListTier`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-ListTier)

例如，以下策略提供了足够的权限，可为集群中的任意存储桶配置对象过渡生命周期管理规则：

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

### 过渡权限 {#id5}

对象过渡生命周期管理规则要求远程存储层具备额外权限。 具体而言，MinIO 要求远程层凭证提供读取、写入、列出和删除权限。

例如，如果远程存储层使用基于 AWS IAM 策略的访问控制，则以下策略提供了对象迁入和迁出远程层所需的权限：

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

请将 `Resource` 修改为 MinIO 用于对象分层的目标存储桶。

> [!NOTE]
> **避免在远程层启用版本控制**
>
> MinIO 强烈建议不要为远程层启用存储桶版本控制。 如果远程层存储桶启用了版本控制，则每个源对象版本都会过渡为远程层中的一个 *唯一对象*。
>
> 如果你的环境要求远程层启用版本控制，则还必须允许 `s3:DeleteObjectVersion` 权限。

有关如何配置用户和权限以支持 MinIO 分层的更完整信息，请参阅受支持分层目标的相关文档：

- [Amazon S3 Permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html#amazons3-actions-as-permissions)
- [Google Cloud Storage Access Control](https://cloud.google.com/storage/docs/access-control)
- [Authorizing access to data in Azure storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth?toc=/azure/storage/blobs/toc.json)