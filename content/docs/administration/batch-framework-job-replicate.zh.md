---
title: "批量复制"

weight: 10
---

<a id="minio-batch-framework-replicate-job"></a>
<a id="id1"></a>

> [!NOTE]
> **新增: MinIO**
>
> RELEASE.2022-10-09T21-10-59Z
>
> 批处理框架在 [`mc`](/docs/reference/minio-mc/#command-mc) [RELEASE.2022-10-09T21-10-59Z](https://github.com/minio/mc/releases/tag/RELEASE.2022-10-09T21-10-59Z) 中随 `replicate` 作业类型一同引入。

MinIO 批处理框架允许您使用 YAML 格式的作业定义文件（“批处理文件”）来创建、管理、监控和执行作业。 批处理作业直接在 MinIO 部署上运行，可利用服务端处理能力，而不受运行 [MinIO Client](/docs/reference/minio-mc/#minio-client) 的本地机器限制。

`replicate` 批处理作业会将对象从一个 MinIO 部署（`source` 部署）复制到另一个 MinIO 部署（`target` 部署）。 `source` 或 `target` 中 **必须** 有一方是 [local](/docs/administration/batch-framework/#minio-batch-local) 部署。

与使用 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror) 相比，MinIO 部署之间的批量复制具有以下优势：

- 消除了客户端到集群网络成为潜在瓶颈的可能
- 用户只需要具备启动批处理作业的访问权限，而无需其他权限，因为作业完全在集群服务端运行
- 如果对象未能复制，作业可提供重试机制
- 批处理作业是一次性的、可编排的过程，可对复制进行精细控制
- （仅限 MinIO 到 MinIO）复制过程会将对象版本从源端复制到目标端

从 MinIO Server `RELEASE.2023-05-04T21-44-30Z` 开始，另一端部署既可以是另一个 MinIO 部署，也可以是使用实时存储类的任意 S3 兼容位置。 使用复制 `YAML` 文件中的筛选选项，可排除存储在需要先重新水化或通过其他恢复方式处理后才能提供请求对象的位置中的对象。 复制到此类远端时，批量复制采用 `mc mirror` 的行为。

## 行为 {#id3}

### 访问控制与要求 {#id4}

批量复制与 [bucket replication](/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements) 具有类似的访问和权限要求。

“source” 部署所使用的凭据必须具有类似以下的策略：

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

“remote” 部署所使用的凭据必须具有类似以下的策略：

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

有关向 MinIO 部署添加用户、访问密钥和策略的更完整文档，请参见 [`mc admin user`](/docs/reference/minio-mc-admin/mc-admin-user/#command-mc.admin.user)、[`mc admin user svcacct`](/docs/reference/minio-mc-admin/mc-admin-user-svcacct/#command-mc.admin.user.svcacct) 和 [`mc admin policy`](/docs/reference/minio-mc-admin/mc-admin-policy/#command-mc.admin.policy)。

已配置 [Active Directory/LDAP](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 或 [OpenID Connect](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 用户管理的 MinIO 部署，也可以创建专用的 [access keys](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account) 来支持批量复制。

### 筛选复制目标 {#id5}

批处理作业定义文件可按存储桶、前缀和/或筛选条件限制复制范围，从而只复制特定对象。 复制过程对对象和存储桶的访问，可能会受到您在 YAML 中为源端或目标端提供的凭据限制。

> [!NOTE]
> **变更: MinIO**
>
> Server RELEASE.2023-04-07T05-28-58Z
>
> 您可以从远程 MinIO 部署复制到运行该批处理作业的本地部署。

例如，您可以使用批处理作业执行一次性复制同步，将对象从本地部署 `minio-local/invoices/` 上的某个存储桶推送到远程部署 `minio-remote/invoices` 上的某个存储桶。 您也可以将对象从远程部署 `minio-remote/invoices` 拉取到本地部署 `minio-local/invoices`。

### 小文件优化 {#id6}

从 [RELEASE.2023-12-09T18-17-51Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-12-09T18-17-51Z) 开始，批量复制默认会自动对小于 5MiB 的对象进行批量打包和压缩，以高效地在源端与远端之间传输数据。 远程 MinIO 部署可以检查这些打包后的对象，并立即应用生命周期管理分层规则。 该功能类似于 S3 Snowball Edge 提供的小文件批处理能力。

您可以在 [replicate](/docs/reference/minio-mc/mc-batch-generate/#minio-batch-job-types) 作业配置中修改压缩设置。

<a id="id7"></a>

## 复制批处理作业参考 {#minio-batch-framework-replicate-job-ref}

YAML **必须** 定义源部署和目标部署。 如果 *source* 部署是远程部署，则 *target* 部署 **必须** 为 `local`。 此外，YAML 还可以定义标志，用于筛选要复制的对象、为作业发送通知或定义作业的重试次数。

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2023-04-07T05-28-58Z
>
> 您可以从远程 MinIO 部署复制到运行该批处理作业的本地部署。

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2024-08-03T04-33-23Z
>
> 此版本引入了 Batch Job Replicate API 的新版本 `v2`。 更新后的 API 允许您在源端列出多个要复制的前缀。 若要从一个源端复制多个前缀，请将 `replicate.apiVersion` 指定为 `v2`。
>
> ```text
> replicate:
>   apiVersion: v1
>   source:
>     type: minio
>     bucket: mybucket
>     prefix:
>       - prefix1
>       - prefix2
> ...
> ```

对于 **源部署**

- 必需信息

  <table>
    <tbody>
      <tr>
        <td><p><code>type:</code></p></td>
        <td><p>必须为 <code>minio</code>。</p></td>
      </tr>
      <tr>
        <td><p><code>bucket:</code></p></td>
        <td><p>部署上的存储桶。</p></td>
      </tr>
    </tbody>
  </table>
- 可选信息

  <table>
    <tbody>
      <tr>
        <td><p><code>prefix:</code></p></td>
        <td>应复制对象的前缀。<br />从 MinIO Server <code>RELEASE.2024-08-03T04-33-23Z</code> 开始，Batch Job Replicate API 的 v2 允许您列出多个前缀。<br />将 <code>replicate.apiVersion</code> 指定为 <code>v2</code>，即可从多个前缀执行复制。<br /></td>
      </tr>
      <tr>
        <td><p><code>endpoint:</code></p></td>
        <td>用于复制批处理作业源端或目标端的部署位置。<br />例如，<code>https://minio.example.net</code>。<br /><br />如果该部署就是命令中指定的 <a href="/docs/reference/minio-mc/mc-alias-set/#alias">mc alias set</a>，可省略此字段，让 MinIO 使用该别名对应的 endpoint 和 credentials 值。<br />源部署或远程部署中<em>必须</em>有一方是 <a href="/docs/administration/batch-framework/#minio-batch-local">“local”</a> 别名。<br />非 “local” 部署必须指定 <code>endpoint</code> 和 <code>credentials</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>path:</code></p></td>
        <td>指示 MinIO 使用存储桶的 Path 或 Virtual Style（DNS）查找方式。<br /><br />- 指定 <code>on</code> 使用 Path 风格<br />- 指定 <code>off</code> 使用 Virtual 风格<br />- 指定 <code>auto</code> 让 MinIO 自动判断正确的查找方式。<br /><br />默认为 <code>auto</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>credentials:</code></p></td>
        <td>授予对象访问权限的 <code>accesskey:</code> 和 <code>secretKey:</code>，或 <code>sessionToken:</code>。<br />仅对非 <a href="/docs/administration/batch-framework/#minio-batch-local">local</a> 部署指定此项。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball</code></p></td>
        <td><em>版本新增</em>：RELEASE.2023-12-09T18-17-51Z<br /><br />用于控制批量打包与压缩功能的配置选项。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.disable</code></p></td>
        <td>指定 <code>true</code> 可在复制期间禁用批量打包与压缩功能。<br />默认为 <code>false</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.batch</code></p></td>
        <td>指定用于压缩打包的对象最大整数数量。<br />默认为 <code>100</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.inmemory</code></p></td>
        <td>指定 <code>false</code> 表示使用本地存储暂存归档，或指定 <code>true</code> 表示暂存到内存（RAM）。<br />默认为 <code>true</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.compress</code></p></td>
        <td>指定 <code>true</code> 可在线路传输中使用 <a href="https://en.wikipedia.org/wiki/Snappy_(compression)">S2/Snappy compression algorithm</a> 生成压缩后的打包对象。<br />默认为 <code>false</code>，即不压缩。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.smallerThan</code></p></td>
        <td>指定对象大小阈值，小于该值时 MinIO 应对对象执行批量打包。<br />默认为 <code>5MiB</code>。<br /></td>
      </tr>
      <tr>
        <td><p><code>snowball.skipErrs</code></p></td>
        <td>指定 <code>false</code> 可让 MinIO 在读取任意产生错误的对象时停止处理。<br />默认为 <code>true</code>。<br /></td>
      </tr>
    </tbody>
  </table>

对于 **目标部署**

- 必需信息

  <table>
    <tbody>
      <tr>
        <td><p><code>type:</code></p></td>
        <td><p>必须为 <code>minio</code>。</p></td>
      </tr>
      <tr>
        <td><p><code>bucket:</code></p></td>
        <td><p>部署上的存储桶。</p></td>
      </tr>
    </tbody>
  </table>
- 可选信息

  <table>
    <tbody>
      <tr>
        <td><p><code>prefix:</code></p></td>
        <td><p>要复制对象的前缀。</p></td>
      </tr>
      <tr>
        <td><p><code>endpoint:</code></p></td>
        <td>目标部署的位置。<br /><br />如果目标是命令中指定的 <a href="/docs/reference/minio-mc/mc-alias-set/#alias">alias</a>，则可以省略此项以及 <code>credentials</code> 字段。<br />如果目标是 “local”，则源端<em>必须</em>通过 <code>endpoint</code> 和 <code>credentials</code> 指定远程部署。<br /></td>
      </tr>
      <tr>
        <td><p><code>credentials:</code></p></td>
        <td><p>授予对象访问权限的 <code>accesskey</code> 和 <code>secretKey</code>，或 <code>sessionToken</code>。</p></td>
      </tr>
    </tbody>
  </table>

对于 **筛选条件**

<table>
  <tbody>
    <tr>
      <td><p><code>newerThan:</code></p></td>
      <td><p>表示时长的字符串，格式为 <code>#d#h#s</code>。</p><p>仅复制比指定时长更新的对象。
例如，<code>7d</code>、<code>24h</code>、<code>5d12h30s</code> 都是有效字符串。</p></td>
    </tr>
    <tr>
      <td><p><code>olderThan:</code></p></td>
      <td><p>表示时长的字符串，格式为 <code>#d#h#s</code>。</p><p>仅复制比指定时长更旧的对象。</p></td>
    </tr>
    <tr>
      <td><p><code>createdAfter:</code></p></td>
      <td><p>采用 <code>YYYY-MM-DDTHH:MM:SSZ</code> <a href="https://datatracker.ietf.org/doc/html/rfc3339.html"><strong>RFC3339</strong></a> 日期时间格式的日期。</p><p>仅复制在该日期之后创建的对象。</p></td>
    </tr>
    <tr>
      <td><p><code>createdBefore:</code></p></td>
      <td><p>采用 <code>YYYY-MM-DDTHH:MM:SSZ</code> <a href="https://datatracker.ietf.org/doc/html/rfc3339.html"><strong>RFC3339</strong></a> 日期时间格式的日期。</p><p>仅复制在该日期之前创建的对象。</p></td>
    </tr>
  </tbody>
</table>

对于 **通知**

<table>
  <tbody>
    <tr>
      <td><p><code>endpoint:</code></p></td>
      <td><p>用于发送通知事件的预定义 endpoint。</p></td>
    </tr>
    <tr>
      <td><p><code>token:</code></p></td>
      <td><p>用于访问 <code>endpoint</code> 的可选 JWT &lt;JSON Web Token&gt;。</p></td>
    </tr>
  </tbody>
</table>

对于 **重试次数**

如果有任何因素中断作业，您可以定义该批处理作业的重试次数。 对于每次重试，您还可以定义两次尝试之间的等待时长。

<table>
  <tbody>
    <tr>
      <td><p><code>attempts:</code></p></td>
      <td><p>在放弃之前完成该批处理作业的尝试次数。</p></td>
    </tr>
    <tr>
      <td><p><code>delay:</code></p></td>
      <td><p>每次尝试之间至少等待的时间。</p></td>
    </tr>
  </tbody>
</table>

## `replicate` 作业类型的 YAML 描述文件示例 {#replicate-yaml}

使用 [`mc batch generate`](/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate) 创建基础的 `replicate` 批处理作业，以便进一步自定义。

对于 [local](/docs/administration/batch-framework/#minio-batch-local) 部署，请勿指定 endpoint 或 credentials。 根据哪一方是 `local`，删除或注释掉源端或目标端部分中的这些行。

```yaml
replicate:
  apiVersion: v1
  # source of the objects to be replicated
  source:
    type: TYPE # valid values are "s3" or "minio"
    bucket: BUCKET
    prefix: PREFIX # 'PREFIX' is optional
    # If your source is the 'local' alias specified to 'mc batch start', then the 'endpoint' and 'credentials' fields are optional and can be omitted
    # Either the 'source' or 'remote' *must* be the "local" deployment
    endpoint: "http[s]://HOSTNAME:PORT" 
    # path: "on|off|auto" # "on" enables path-style bucket lookup. "off" enables virtual host (DNS)-style bucket lookup. Defaults to "auto"
    credentials:
      accessKey: ACCESS-KEY # Required
      secretKey: SECRET-KEY # Required
    # sessionToken: SESSION-TOKEN # Optional only available when rotating credentials are used
    snowball: # automatically activated if the source is local
      disable: false # optionally turn-off snowball archive transfer
      batch: 100 # upto this many objects per archive
      inmemory: true # indicates if the archive must be staged locally or in-memory
      compress: false # S2/Snappy compressed archive
      smallerThan: 5MiB # create archive for all objects smaller than 5MiB
      skipErrs: false # skips any source side read() errors

  # target where the objects must be replicated
  target:
    type: TYPE # valid values are "s3" or "minio"
    bucket: BUCKET
    prefix: PREFIX # 'PREFIX' is optional
    # If your source is the 'local' alias specified to 'mc batch start', then the 'endpoint' and 'credentials' fields are optional and can be omitted

    # Either the 'source' or 'remote' *must* be the "local" deployment
    endpoint: "http[s]://HOSTNAME:PORT"
    # path: "on|off|auto" # "on" enables path-style bucket lookup. "off" enables virtual host (DNS)-style bucket lookup. Defaults to "auto"
    credentials:
      accessKey: ACCESS-KEY
      secretKey: SECRET-KEY
    # sessionToken: SESSION-TOKEN # Optional only available when rotating credentials are used

  # NOTE: All flags are optional
  # - filtering criteria only applies for all source objects match the criteria
  # - configurable notification endpoints
  # - configurable retries for the job (each retry skips successfully previously replaced objects)
  flags:
    filter:
      newerThan: "7d" # match objects newer than this value (e.g. 7d10h31s)
      olderThan: "7d" # match objects older than this value (e.g. 7d10h31s)
      createdAfter: "datetime" # match objects created after this date and time in RFC3339 format
      createdBefore: "datetime" # match objects created before this date and time in RFC3339 format

      ## NOTE: tags are not supported when "source" is remote.
      # tags:
      #   - key: "name"
      #     value: "pick*" # match objects with tag 'name', with all values starting with 'pick'

      # metadata:
      #   - key: "content-type"
      #     value: "image/*" # match objects with 'content-type', with all values starting with 'image/'

    notify:
      endpoint: "https://notify.endpoint" # notification endpoint to receive job status events
      token: "Bearer xxxxx" # optional authentication token for the notification endpoint

    retry:
      attempts: 10 # number of retries for the job before giving up
      delay: "500ms" # least amount of delay between each retry

```