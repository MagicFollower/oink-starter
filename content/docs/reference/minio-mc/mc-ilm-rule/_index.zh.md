---
title: "mc ilm rule"

weight: 20
icon: fa-solid fa-list-check
---

<a id="mc-ilm-rule"></a>

<a id="command-mc.ilm.rule"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> 以下命令已移至 [`mc ilm rule`](#command-mc.ilm.rule) 下的子命令：
>
> - [`mc ilm add`](/docs/reference/deprecated/mc-ilm-add/#command-mc.ilm.add)
> - [`mc ilm edit`](/docs/reference/deprecated/mc-ilm-edit/#command-mc.ilm.edit)
> - [`mc ilm export`](/docs/reference/deprecated/mc-ilm-export/#command-mc.ilm.export)
> - [`mc ilm import`](/docs/reference/deprecated/mc-ilm-import/#command-mc.ilm.import)
> - [`mc ilm ls`](/docs/reference/deprecated/mc-ilm-ls/#command-mc.ilm.ls)
> - [`mc ilm rm`](/docs/reference/deprecated/mc-ilm-rm/#command-mc.ilm.rm)

## 描述 {#id2}

[`mc ilm rule`](#command-mc.ilm.rule) 命令及其子命令用于配置 MinIO 生命周期管理中对象在各存储层之间转换所使用的规则。

在使用此命令创建规则前，请先使用 [`mc ilm tier`](/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier) 及其子命令创建对象将要迁移到的其他对象存储位置对应的一个或多个存储层。

有关更多信息，请参阅 [lifecycle management](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 概述。

## 子命令 {#id3}

[`mc ilm rule`](#command-mc.ilm.rule) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add"><code>add</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add"><code>mc ilm rule add</code></a> 命令用于向存储桶添加对象生命周期管理规则。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-edit/#command-mc.ilm.rule.edit"><code>edit</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-edit/#command-mc.ilm.rule.edit"><code>mc ilm rule edit</code></a> 命令用于修改 MinIO 存储桶上现有的对象生命周期管理规则。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-export/#command-mc.ilm.rule.export"><code>export</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-export/#command-mc.ilm.rule.export"><code>mc ilm rule export</code></a> 命令用于导出 MinIO 存储桶的对象生命周期管理配置。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-import/#command-mc.ilm.rule.import"><code>import</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-import/#command-mc.ilm.rule.import"><code>mc ilm rule import</code></a> 命令导入对象生命周期管理配置，
并将其应用到 MinIO 存储桶。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls"><code>ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls"><code>mc ilm rule ls</code></a> 命令以表格格式汇总 MinIO 存储桶上配置的所有对象生命周期管理规则。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-rm/#command-mc.ilm.rule.rm"><code>rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm-rule-rm/#command-mc.ilm.rule.rm"><code>mc ilm rule rm</code></a> 命令用于从 MinIO 存储桶中删除一条对象生命周期管理规则。</p></td>
    </tr>
  </tbody>
</table>

<a id="id4"></a>

## 权限 {#minio-mc-ilm-rule-permissions}

MinIO 要求具备以下权限，且权限范围应限定为创建生命周期管理规则的一个或多个存储桶。

- [`s3:PutLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-PutLifecycleConfiguration)
- [`s3:GetLifecycleConfiguration`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.s3-GetLifecycleConfiguration)

例如，以下策略提供了在集群任意存储桶上配置对象转换生命周期管理规则的权限：

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

### 转换权限 {#id5}

对象转换生命周期管理规则在远端存储层上需要额外权限。具体而言， MinIO 要求远端存储层凭证提供读取、写入、列举和删除权限。

例如，如果远端存储层使用基于 AWS IAM 策略的访问控制， 则以下策略提供了对象迁入和迁出远端存储层所需的必要权限：

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

请根据 MinIO 分层写入对象的目标存储桶修改 `Resource`。

有关如何配置用户和权限以支持 MinIO 分层的完整信息，请参阅受支持分层目标的文档：

- [Amazon S3 Permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html#amazons3-actions-as-permissions)
- [Google Cloud Storage Access Control](https://cloud.google.com/storage/docs/access-control)
- [Authorizing access to data in Azure storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-auth?toc=/azure/storage/blobs/toc.json)