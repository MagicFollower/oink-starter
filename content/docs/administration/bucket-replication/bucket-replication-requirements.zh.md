---
title: "设置存储桶复制的要求"

weight: 10
---

<a id="minio-bucket-replication-requirements"></a>
<a id="id1"></a>

存储桶复制使用规则将一个 MinIO 部署中的存储桶内容同步到远端 MinIO 部署中的存储桶。

复制可以通过以下任一方式完成：

- [Active-Passive](/docs/administration/bucket-replication/enable-server-side-one-way-bucket-replication/#minio-bucket-replication-serverside-oneway) 符合条件的对象会从源存储桶复制到远端存储桶。 远端存储桶上的任何更改都不会反向复制回来。
- [Active-Active](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway) 任一存储桶中符合条件对象的更改都会以双向方式复制到另一个存储桶。
- [Multi-Site Active-Active](/docs/administration/bucket-replication/enable-server-side-multi-site-bucket-replication/#minio-bucket-replication-serverside-multi) 任何已设置存储桶复制的存储桶中符合条件对象的更改，都会复制到所有其他存储桶。

在设置这些复制配置之前，请确保满足以下前提条件。

<a id="minio-bucket-replication-serverside-oneway-permissions"></a>

## 设置存储桶复制所需的权限 {#id3}

要配置和启用复制规则，存储桶复制要求源端和目标端部署具备特定权限。

{{< tabs group="tab1-tab2" >}}
{{< tab label="复制管理员" value="tab1" >}}
下列策略提供了在部署上配置和启用复制所需的权限。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "admin:SetBucketTarget",
                "admin:GetBucketTarget",
                "admin:ListBatchJobs",
                "admin:DescribeBatchJob",
                "admin:StartBatchJob",
                "admin:CancelBatchJob"
            ],
            "Effect": "Allow",
            "Sid": "EnableRemoteBucketConfiguration"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:GetBucketLocation",
                "s3:GetBucketVersioning",
                "s3:GetObjectRetention",
                "s3:GetObjectLegalHold",
                "s3:PutReplicationConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicationRuleConfiguration"
        }
    ]
}

```

- `"EnableRemoteBucketConfiguration"` 语句授予创建远端目标以支持复制的权限。
- `"EnableReplicationRuleConfiguration"` 语句授予在存储桶上创建复制规则的权限。 `"arn:aws:s3:::*` 资源会将复制权限应用到源部署上的 *任意* 存储桶。 你可以按需将该用户策略限制到特定存储桶。

下列代码使用所需策略创建一个 [MinIO 管理用户](/docs/administration/identity-access-management/minio-user-management/#minio-users)。 将 `TARGET` 替换为你要配置复制的 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)：

```shell
wget -O - https://silo.pgsty.com/extra/examples/ReplicationAdminPolicy.json | \
mc admin policy create TARGET ReplicationAdminPolicy /dev/stdin
mc admin user add TARGET ReplicationAdmin LongRandomSecretKey
mc admin policy attach TARGET ReplicationAdminPolicy --user=ReplicationAdmin
```

对于配置了 [Active Directory/LDAP](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 或 [OpenID Connect](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 用户管理的 MinIO 部署，则应改为为存储桶复制创建专用 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account)。
{{< /tab >}}
{{< tab label="复制远端用户" value="tab2" >}}
下列策略提供了将复制数据同步 *到* 该部署所需的权限。

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:GetBucketLocation",
                "s3:GetBucketVersioning",
                "s3:GetBucketObjectLockConfiguration",
                "s3:GetEncryptionConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicationOnBucket"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetReplicationConfiguration",
                "s3:ReplicateTags",
                "s3:AbortMultipartUpload",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetObjectVersionTagging",
                "s3:PutObject",
                "s3:PutObjectRetention",
                "s3:PutBucketObjectLockConfiguration",
                "s3:PutObjectLegalHold",
                "s3:DeleteObject",
                "s3:ReplicateObject",
                "s3:ReplicateDelete"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ],
            "Sid": "EnableReplicatingDataIntoBucket"
        }
    ]
}
```

- `"EnableReplicationOnBucket"` 语句授予远端目标获取存储桶级配置的权限， 从而支持在 MinIO 部署中 *所有* 存储桶上执行复制操作。 如果要将策略限制到特定存储桶，请像 `"arn:aws:s3:::bucketName"` 一样， 在 `Resource` 数组中指定这些存储桶。
- `"EnableReplicatingDataIntoBucket"` 语句授予远端目标将数据同步到 MinIO 部署中 *任意* 存储桶的权限。 如果要将策略限制到特定存储桶，请像 `"arn:aws:s3:::bucketName/*"` 一样， 在 `Resource` 数组中指定这些存储桶。

SILO 目标端的复制删除沿用 `s3:DeleteObject` 加 `s3:ReplicateDelete` 的 receiver
契约。复制凭据不需要额外获得 `s3:DeleteObjectVersion` 的 Allow；但显式 Deny
`s3:DeleteObjectVersion` 仍会阻止对应的版本清理。这个内部契约不改变普通 S3
客户端的要求：只要请求明确指定版本，就必须具备 `s3:DeleteObjectVersion`。

下列代码使用所需策略创建一个 [MinIO 管理用户](/docs/administration/identity-access-management/minio-user-management/#minio-users)。 将 `TARGET` 替换为你要配置复制的 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)：

```shell
wget -O - https://silo.pgsty.com/extra/examples/ReplicationRemoteUserPolicy.json | \
mc admin policy create TARGET ReplicationRemoteUserPolicy /dev/stdin
mc admin user add TARGET ReplicationRemoteUser LongRandomSecretKey
mc admin policy attach TARGET ReplicationRemoteUserPolicy --user=ReplicationRemoteUser
```

对于配置了 [Active Directory/LDAP](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 或 [OpenID Connect](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 用户管理的 MinIO 部署，则应改为为存储桶复制创建专用 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account)。
{{< /tab >}}
{{< /tabs >}}

关于在 MinIO 部署中添加用户、访问密钥和策略的更完整文档，请参见 [`mc admin user`](/docs/reference/minio-mc-admin/mc-admin-user/#command-mc.admin.user)、[`mc admin user svcacct`](/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct) 和 [`mc admin policy`](/docs/reference/minio-mc-admin/mc-admin-policy/#command-mc.admin.policy)。

## 存储桶复制的对象加密设置需保持一致 {#id4}

MinIO 支持复制使用 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms) 和 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 加密的对象：

- 对于使用 SSE-KMS 加密的对象，MinIO *要求* 目标存储桶支持使用与源存储桶对象 加密时 *相同的密钥名称* 对对象执行 SSE-KMS 加密。
- 对于使用 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 加密的对象，MinIO *要求* 目标存储桶同样支持 SSE-S3 对象加密，而不考虑密钥名称。

在复制过程中，MinIO 会先在源存储桶上对对象进行 *解密*，再通过网络传输未加密的 对象。目标 MinIO 部署随后会使用目标端的加密设置重新对该对象进行加密。 因此，MinIO *强烈建议* 在源端和目标端部署上都 [启用 TLS](/docs/operations/network-encryption/#minio-tls)，以确保对象在传输过程中的安全。

MinIO *不* 支持复制客户端加密对象（SSE-C）。

## 存储桶复制要求使用 MinIO 部署 {#minio}

MinIO 服务端复制仅适用于 MinIO 部署之间。 源端和目标端部署 *都必须* 运行版本匹配的 MinIO Server。

如需在任意 S3 兼容服务之间配置复制，请使用 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror)。

## 复制要求启用版本控制 {#id5}

MinIO 依赖 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 提供的不可变性保护来支持 复制和重新同步。

使用 [`mc version info`](/docs/reference/minio-mc/mc-version-info/#command-mc.version.info) 验证源存储桶和远端存储桶的版本控制状态。 必要时使用 [`mc version enable`](/docs/reference/minio-mc/mc-version-enable/#command-mc.version.enable) 命令启用版本控制。

如果你在源存储桶中将某个前缀或文件夹排除在版本控制之外，MinIO 就无法复制该文件夹 或前缀中的对象。

## 对象锁定状态需与存储桶复制保持一致 {#id6}

MinIO 支持复制受 [WORM 锁定](/docs/administration/object-management/object-retention/#minio-object-locking) 保护的对象。 两个复制存储桶 *都必须* 启用对象锁定，MinIO 才能复制被锁定的对象。 对于主动-主动配置，MinIO 建议在两个存储桶上使用 *相同的* 保留规则，以确保跨站点 行为一致。

根据 S3 的行为要求，你必须在创建存储桶时启用对象锁定。 随后，你可以在任何时候配置对象保留规则。 在开始此过程 *之前*，请先在状态异常的目标存储桶上配置所需规则。