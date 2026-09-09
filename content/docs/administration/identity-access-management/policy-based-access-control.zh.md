---
title: "访问管理"

weight: 50
---

<a id="minio-policy"></a>
<a id="id1"></a>

## 概述 {#id3}

MinIO 使用 基于策略的访问控制 (PBAC) 来定义已认证用户可访问的授权操作和资源。 每个策略描述一条或多条 [actions](#minio-policy-actions) 与 [conditions](#minio-policy-conditions)，用于说明某个 [user](/docs/administration/identity-access-management/minio-user-management/#minio-users) 或 [group](/docs/administration/identity-access-management/minio-group-management/#minio-groups) 中用户的权限。

MinIO PBAC 在设计上兼容 AWS IAM 策略语法、结构和行为。 MinIO 文档会尽力覆盖 IAM 特定行为和功能。 若需要更完整的 AWS IAM 特定主题文档，请参考 [IAM documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/)。

[`mc admin policy`](/docs/reference/minio-mc-admin/mc-admin-policy/#command-mc.admin.policy) 命令支持在 MinIO 部署上创建和管理策略。 用法示例请参见命令参考。

## 基于标签的策略条件 {#id4}

> [!NOTE]
> **变更: RELEASE.2022-10-02T19-29-29Z**
>
> 策略可以使用条件，将用户访问限制为仅能访问带有 [特定标签](/docs/administration/object-management/#minio-object-tagging) 的对象。
>
> 对于[选定操作](#minio-selected-conditional-actions)，MinIO 支持[基于标签的条件](https://docs.aws.amazon.com/AmazonS3/latest/userguide/tagging-and-policies.html)。当 API 路径在授权前加载目标对象元数据时，`s3:ExistingObjectTag/<key>` 读取对象上已经存储的标签。`s3:RequestObjectTag/<key>` 与 `s3:RequestObjectTagKeys` 是客户端提供的请求值，不能证明对象已经具有这些标签。`PutObject`、`CreateMultipartUpload` 与 `PutObjectTagging` 会把它们显式绑定到处理器实际消费的标签输入；其他 action 路径为了兼容仍保留历史 `X-Amz-Tagging` Header 映射，因此请求标签条件只应在 API 确实消费标签时使用。
>
> 存储桶标签与对象标签不是同一类数据。`PutBucketTagging` 不会从 XML 正文填充 `s3:RequestObjectTag*` 条件键。

<a id="id5"></a>

## 内置策略 {#minio-policy-built-in}

MinIO 提供以下内置策略，可分配给 [users](/docs/administration/identity-access-management/minio-user-management/#minio-users) 或 [groups](/docs/administration/identity-access-management/minio-group-management/#minio-groups)：

#### `consoleAdmin` {#userpolicy.consoleAdmin}

*userpolicy*

授予对 MinIO 部署上所有资源执行全部 S3 和管理 API 操作的完整访问权限。 等价于以下 action 集合：

- [`s3:*`](#policy-action.s3)
- [`admin:*`](#policy-action.admin)

#### `readonly` {#userpolicy.readonly}

*userpolicy*

授予对 MinIO 部署上任意对象的只读权限。 `GET` 操作 *必须* 作用于某个具体对象，且不要求具备任何列举权限。 等价于以下 action 集合：

- [`s3:GetBucketLocation`](#policy-action.s3-GetBucketLocation)
- [`s3:GetObject`](#policy-action.s3-GetObject)

例如，该策略专门支持对特定路径下对象执行 `GET` 操作（例如 `GET play/mybucket/object.file`），例如：

- [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp)
- [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat)
- [`mc head`](/docs/reference/minio-mc/mc-head/#command-mc.head)
- [`mc cat`](/docs/reference/minio-mc/mc-cat/#command-mc.cat)

有意排除列举权限，因为典型使用场景并不希望“只读”角色对对象存储资源具有完整可发现性 （列出所有存储桶和对象）。

#### `readwrite` {#userpolicy.readwrite}

*userpolicy*

授予对 MinIO 服务器上所有存储桶和对象的读写权限。 等价于 [`s3:*`](#policy-action.s3)。

#### `diagnostics` {#userpolicy.diagnostics}

*userpolicy*

授予在 MinIO 部署上执行诊断操作的权限。 具体包括以下 action：

- [`admin:ServerTrace`](#policy-action.admin-ServerTrace)
- [`admin:Profiling`](#policy-action.admin-Profiling)
- [`admin:ConsoleLog`](#policy-action.admin-ConsoleLog)
- [`admin:ServerInfo`](#policy-action.admin-ServerInfo)
- [`admin:TopLocksInfo`](#policy-action.admin-TopLocksInfo)
- [`admin:OBDInfo`](#policy-action.admin-OBDInfo)
- [`admin:BandwidthMonitor`](#policy-action.admin-BandwidthMonitor)
- [`admin:Prometheus`](#policy-action.admin-Prometheus)

#### `writeonly` {#userpolicy.writeonly}

*userpolicy*

授予对 MinIO 部署中任意命名空间（存储桶及对象路径）的只写权限。 `PUT` 操作 *必须* 作用于某个具体对象位置，且不要求具备任何列举权限。 等价于 [`s3:PutObject`](#policy-action.s3-PutObject) action。

使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 将策略关联到 MinIO 部署上的用户或组。

例如，考虑下表中的用户。每个用户都被分配了一个 [内置策略](#minio-policy-built-in) 或某个受支持的 [action](#minio-policy-actions)。该表描述了客户端以对应用户身份完成认证后可执行的一部分操作：

<table>
  <thead>
    <tr>
      <th><p>用户</p></th>
      <th><p>策略</p></th>
      <th><p>操作</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>Operations</code></p></td>
      <td><code>finance</code> 存储桶上的 <a href="#userpolicy.readwrite"><code>readwrite</code></a><br /><code>audit</code> 存储桶上的 <a href="#userpolicy.readonly"><code>readonly</code></a><br /></td>
      <td>对 <code>finance</code> 存储桶执行 <code>PUT</code> 和 <code>GET</code>。<br />对 <code>audit</code> 存储桶执行 <code>GET</code><br /></td>
    </tr>
    <tr>
      <td><p><code>Auditing</code></p></td>
      <td><code>audit</code> 存储桶上的 <a href="#userpolicy.readonly"><code>readonly</code></a><br /></td>
      <td><p>对 <code>audit</code> 存储桶执行 <code>GET</code></p></td>
    </tr>
    <tr>
      <td><p><code>Admin</code></p></td>
      <td><p><a href="#policy-action.admin"><code>admin:*</code></a></p></td>
      <td><p>所有 <a href="/docs/reference/minio-mc-admin/#command-mc.admin"><code>mc admin</code></a> 命令。</p></td>
    </tr>
  </tbody>
</table>

每个用户只能访问内置角色 *显式* 授予的那些资源和操作。 默认情况下，MinIO 会拒绝访问任何其他资源或 action。

> [!NOTE]
> **`Deny` overrides `Allow`**
>
> MinIO 遵循 IAM 策略求值规则，即在同一操作/资源上，`Deny` 规则会覆盖 `Allow` 规则。例如，如果某个用户被显式分配的策略对某个操作/资源包含 `Allow` 规则，而其所属某个组被分配的策略对同一操作/资源包含 `Deny` 规则， 则 MinIO 只会应用 `Deny` 规则。
>
> 有关 IAM 策略求值逻辑的更多信息，请参见 IAM 文档中的 [Determining Whether a Request is Allowed or Denied Within an Account](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html#policy-eval-denyallow)。

<a id="id6"></a>

## 策略文档结构 {#minio-policy-document}

MinIO 策略文档使用与 [AWS IAM Policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access.html) 文档相同的模式。

以下示例文档为在 MinIO 部署中创建自定义策略提供了模板。 有关 IAM 策略元素的更完整文档，请参见 [IAM JSON Policy Elements Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html)。

任意单个策略文档的最大大小为 20KiB。 可附加到用户或组的策略文档数量没有限制。

```javascript
{
   "Version" : "2012-10-17",
   "Statement" : [
      {
         "Effect" : "Allow",
         "Action" : [ "s3:<ActionName>", ... ],
         "Resource" : "arn:aws:s3:::*",
         "Condition" : { ... }
      },
      {
         "Effect" : "Deny",
         "Action" : [ "s3:<ActionName>", ... ],
         "Resource" : "arn:aws:s3:::*",
         "Condition" : { ... }
      }
   ]
}
```

- 对于 `Statement.Action` 数组，指定一个或多个 [受支持的 S3 API 操作](#minio-policy-actions)。
- 对于 `Statement.Resource` 键，指定要对策略进行限制的存储桶或存储桶前缀。 可以按照 [S3 Resource Spec](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-arn-format.html) 使用 `*` 和 `?` 通配符。

  `*` 通配符可能会基于 [模式匹配](/docs/reference/minio-mc/#minio-wildcard-matching)，导致策略被意外应用到多个存储桶或前缀。 例如，`arn:aws:s3:::data*` 会匹配存储桶 `data`、`data_private` 和 `data_internal`。 如果资源键仅指定 `*`，则该策略会应用到部署上的所有存储桶和前缀。

  对象模式与存储桶 ARN **不可互换**，参见[存储桶资源与对象资源](#bucket-and-object-resources)。
- 对于 `Statement.Condition` 键，可以指定一个或多个 [受支持的 Conditions](#minio-policy-conditions)。

### 存储桶资源与对象资源 {#bucket-and-object-resources}

一个资源 ARN 要么指代存储桶本身，要么指代桶内的对象，两种形式授权的是不同的操作：

- `arn:aws:s3:::mybucket` 指代 **存储桶本身**，授权 `ListBucket`、`PutBucketPolicy` 这类桶级操作。
- `arn:aws:s3:::mybucket/*` 指代 **桶内的对象**，授权 `GetObject`、`PutObject` 这类对象操作。

当一个主体两者都需要时，就把两者都授予——这也是"既管理存储桶、又管理其内容"的策略的惯例写法：

```json
"Resource": ["arn:aws:s3:::mybucket", "arn:aws:s3:::mybucket/*"]
```

> [!WARNING]
> **十二个桶级写操作需要存储桶 ARN**
>
> `arn:aws:s3:::mybucket/*` 这样的对象级模式 **不会** 授权以下动作，即使语句授予的是 `s3:*`：
>
> `PutBucketPolicy`、`DeleteBucketPolicy`、`PutBucketObjectLockConfiguration`、`PutBucketVersioning`、`PutReplicationConfiguration`、`PutLifecycleConfiguration`、`DeleteBucket`、`ForceDeleteBucket`、`PutBucketCors`、`DeleteBucketCors`、`PutBucketQOS`、`PutInventoryConfiguration`
>
> 这些动作中的每一个，都能让调用者拿到对象级授权本来给不了的东西——把访问权发给别的主体、击穿专门针对写权限持有者的保护、在授权被吊销后仍持续生效，或者销毁存储桶实体本身。要授予它们，请在对象模式旁边补上裸的存储桶 ARN。
>
> 早期版本也会通过对象模式授权这些动作，因为桶级请求被拿去与字符串 `mybucket/` 匹配，而 `mybucket/*` 同样命中它。那是一种过度授予，参见上游 [minio/minio#20449](https://github.com/minio/minio/issues/20449)。在调整策略期间，可将 [`MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH`](/docs/reference/minio-server/settings/core/#envvar.MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH) 设为 `on` 恢复此前的行为。

其余行为一律不变。`ListBucket`、`GetBucketLocation`、各类存储桶配置 **读取** 以及 `CreateBucket` 仍然可以通过对象模式获得授权，因此按这种写法配置的列举与供应流程照常工作。`Deny` 语句与 `NotResource` 排除的匹配方式一如既往，所以任何写在 `mybucket/*` 上的限制都不会被削弱。内置的 `readwrite`、`readonly`、`writeonly`、`diagnostics` 策略使用 `arn:aws:s3:::*`，不受影响。

<a id="minio-policy-actions"></a>

## 受支持的 S3 策略 Action {#s3-action}

MinIO 策略文档支持 IAM [S3 Action keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/list_amazons3.html#amazons3-actions-as-permissions) 的一个子集。 本节还包括特定 action 在通用受支持键之外额外支持的任何 [condition keys](#minio-policy-conditions)。

以下 action 用于控制常见 S3 操作的访问。 其余小节记录更高级的 S3 操作所对应的 action：

<a id="policy-action.s3:*"></a>

#### `s3:*` {#policy-action.s3}

*policy-action*

选择器，用于匹配 *所有* MinIO S3 操作。 将该 action 应用于某个资源后，用户即可对该资源执行 *任意* S3 操作。

<a id="policy-action.s3:CreateBucket"></a>

#### `s3:CreateBucket` {#policy-action.s3-CreateBucket}

*policy-action*

控制对 [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html) S3 API 操作的访问。

<a id="policy-action.s3:DeleteBucket"></a>

#### `s3:DeleteBucket` {#policy-action.s3-DeleteBucket}

*policy-action*

控制对 [DeleteBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucket.html) S3 API 操作的访问。

<a id="policy-action.s3:ForceDeleteBucket"></a>

#### `s3:ForceDeleteBucket` {#policy-action.s3-ForceDeleteBucket}

*policy-action*

控制对带有 `x-minio-force-delete` 标志的 [DeleteBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucket.html) S3 API 操作的访问。 删除非空存储桶时需要此权限。

<a id="policy-action.s3:GetBucketLocation"></a>

#### `s3:GetBucketLocation` {#policy-action.s3-GetBucketLocation}

*policy-action*

控制对 [GetBucketLocation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLocation.html) S3 API 操作的访问。

<a id="policy-action.s3:ListAllMyBuckets"></a>

#### `s3:ListAllMyBuckets` {#policy-action.s3-ListAllMyBuckets}

*policy-action*

控制对 [ListBuckets](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBuckets.html) S3 API 操作的访问。

<a id="policy-action.s3:DeleteObject"></a>

#### `s3:DeleteObject` {#policy-action.s3-DeleteObject}

*policy-action*

控制对 [DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html) S3 API 操作的访问。

此操作授权未显式指定版本的删除请求。在启用版本控制的存储桶上，该请求会创建
delete marker。它不授权 `DELETE ?versionId=...`，也不授权 `DeleteObjects` 中
携带 `VersionId` 的条目。

支持以下额外[条件键](#minio-policy-conditions)：

```shell
s3:versionid
```

<a id="policy-action.s3:GetObject"></a>

#### `s3:GetObject` {#policy-action.s3-GetObject}

*policy-action*

控制对 [GetObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:x-amz-server-side-encryption
s3:x-amz-server-side-encryption-customer-algorithm
s3:x-amz-server-side-encryption-aws-kms-key-id
s3:ExistingObjectTag/<key>
s3:versionid
```

<a id="policy-action.s3:GetObjectAttributes"></a>

#### `s3:GetObjectAttributes` {#policy-action.s3-GetObjectAttributes}

*policy-action*

控制对 [GetObjectAttributes](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectAttributes.html) S3 API 操作的访问。

策略解析器允许此 action 使用以下条件键：

```shell
s3:ExistingObjectTag/<key>
```

但当前处理器在加载对象元数据前完成授权，因此该操作求值时此条件值缺失。

<a id="policy-action.s3:GetObjectVersionAttributes"></a>

#### `s3:GetObjectVersionAttributes` {#policy-action.s3-GetObjectVersionAttributes}

*policy-action*

控制对带版本对象执行 [GetObjectAttributes](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectAttributes.html) S3 API 操作的访问。

支持以下额外[条件键](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

版本 ID 来自请求查询参数。当前处理器在加载对象元数据前完成授权，因此策略解析器虽然允许 `s3:ExistingObjectTag/<key>`，该操作求值时此值仍然缺失。

<a id="policy-action.s3:RestoreObject"></a>

#### `s3:RestoreObject` {#policy-action.s3-RestoreObject}

*policy-action*

控制对 [RestoreObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_RestoreObject.html) S3 API 操作的访问。

<a id="policy-action.s3:ListBucket"></a>

#### `s3:ListBucket` {#policy-action.s3-ListBucket}

*policy-action*

控制对 [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:prefix
s3:delimiter
s3:max-keys
```

<a id="policy-action.s3:PutObject"></a>

#### `s3:PutObject` {#policy-action.s3-PutObject}

*policy-action*

控制对 [PutObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObject.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:x-amz-copy-source
s3:x-amz-server-side-encryption
s3:x-amz-server-side-encryption-customer-algorithm
s3:x-amz-server-side-encryption-aws-kms-key-id
s3:x-amz-metadata-directive
s3:x-amz-storage-class
s3:versionid
s3:object-lock-retain-until-date
s3:object-lock-mode
s3:object-lock-legal-hold
s3:RequestObjectTagKeys
s3:RequestObjectTag/<key>
```

<a id="policy-action.s3:PutObjectTagging"></a>

#### `s3:PutObjectTagging` {#policy-action.s3-PutObjectTagging}

*policy-action*

控制对 [PutObjectTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObjectTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
s3:RequestObjectTagKeys
s3:RequestObjectTag/<key>
```

<a id="policy-action.s3:GetObjectTagging"></a>

#### `s3:GetObjectTagging` {#policy-action.s3-GetObjectTagging}

*policy-action*

控制对 [GetObjectTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:DeleteObjectTagging"></a>

#### `s3:DeleteObjectTagging` {#policy-action.s3-DeleteObjectTagging}

*policy-action*

控制对 [DeleteObjectTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjectTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

### 存储桶配置 {#id7}

<a id="policy-action.s3:GetBucketPolicy"></a>

##### `s3:GetBucketPolicy` {#policy-action.s3-GetBucketPolicy}

*policy-action*

控制对 [GetBucketPolicy](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketPolicy.html) S3 API 操作的访问。

<a id="policy-action.s3:PutBucketPolicy"></a>

##### `s3:PutBucketPolicy` {#policy-action.s3-PutBucketPolicy}

*policy-action*

控制对 [PutBucketPolicy](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketPolicy.html) S3 API 操作的访问。

<a id="policy-action.s3:DeleteBucketPolicy"></a>

##### `s3:DeleteBucketPolicy` {#policy-action.s3-DeleteBucketPolicy}

*policy-action*

控制对 [DeleteBucketPolicy](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteBucketPolicy.html) S3 API 操作的访问。

<a id="policy-action.s3:GetBucketTagging"></a>

##### `s3:GetBucketTagging` {#policy-action.s3-GetBucketTagging}

*policy-action*

控制对 [GetBucketTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketTagging.html) S3 API 操作的访问。

<a id="policy-action.s3:PutBucketTagging"></a>

##### `s3:PutBucketTagging` {#policy-action.s3-PutBucketTagging}

*policy-action*

控制对 [PutBucketTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketTagging.html) S3 API 操作的访问。

策略解析器出于兼容性保留以下条件键：

```shell
s3:RequestObjectTagKeys
s3:RequestObjectTag/<key>
```

处理器 **不会** 从存储桶标签 XML 正文填充这些键；只有历史兼容的客户端 `X-Amz-Tagging` Header 回退可以填充它们，而这个 Header 并不能约束最终从正文写入的存储桶标签。不要用这些键强制约束 `PutBucketTagging` 请求的内容。

<a id="policy-action.s3:GetBucketPolicyStatus"></a>

##### `s3:GetBucketPolicyStatus` {#policy-action.s3-GetBucketPolicyStatus}

*policy-action*

控制对 [GetBucketPolicyStatus](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketPolicyStatus.html) S3 API 操作的访问。

### 分段上传 {#id8}

<a id="policy-action.s3:AbortMultipartUpload"></a>

##### `s3:AbortMultipartUpload` {#policy-action.s3-AbortMultipartUpload}

*policy-action*

控制对 [AbortMultipartUpload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_AbortMultipartUpload.html) S3 API 操作的访问。

<a id="policy-action.s3:ListMultipartUploadParts"></a>

##### `s3:ListMultipartUploadParts` {#policy-action.s3-ListMultipartUploadParts}

*policy-action*

控制对 [ListParts](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListParts.html) S3 API 操作的访问。

<a id="policy-action.s3:ListBucketMultipartUploads"></a>

##### `s3:ListBucketMultipartUploads` {#policy-action.s3-ListBucketMultipartUploads}

*policy-action*

控制对 [ListMultipartUploads](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListMultipartUploads.html) S3 API 操作的访问。

### 版本控制与保留 {#id9}

<a id="policy-action.s3:PutBucketVersioning"></a>

##### `s3:PutBucketVersioning` {#policy-action.s3-PutBucketVersioning}

*policy-action*

控制对 [PutBucketVersioning](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketVersioning.html) S3 API 操作的访问。

<a id="policy-action.s3:GetBucketVersioning"></a>

##### `s3:GetBucketVersioning` {#policy-action.s3-GetBucketVersioning}

*policy-action*

控制对 [GetBucketVersioning](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketVersioning.html) S3 API 操作的访问。

<a id="policy-action.s3:DeleteObjectVersion"></a>

##### `s3:DeleteObjectVersion` {#policy-action.s3-DeleteObjectVersion}

*policy-action*

控制对 [DeleteObjectVersion](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjectVersion.html) S3 API 操作的访问。

此操作授权删除明确指定的 UUID 或显式 `null` 版本。在 `DeleteObjects` 中，SILO
会对每个携带 `VersionId` 的条目独立检查该权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
```

<a id="policy-action.s3:ListBucketVersions"></a>

##### `s3:ListBucketVersions` {#policy-action.s3-ListBucketVersions}

*policy-action*

控制对 [ListBucketVersions](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListBucketVersions.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:prefix
s3:delimiter
s3:max-keys
```

<a id="policy-action.s3:PutObjectVersionTagging"></a>

##### `s3:PutObjectVersionTagging` {#policy-action.s3-PutObjectVersionTagging}

*policy-action*

控制对 [PutObjectVersionTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObjectVersionTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
s3:RequestObjectTagKeys
s3:RequestObjectTag/<key>
```

<a id="policy-action.s3:GetObjectVersionTagging"></a>

##### `s3:GetObjectVersionTagging` {#policy-action.s3-GetObjectVersionTagging}

*policy-action*

控制对 [GetObjectVersionTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectVersionTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:DeleteObjectVersionTagging"></a>

##### `s3:DeleteObjectVersionTagging` {#policy-action.s3-DeleteObjectVersionTagging}

*policy-action*

控制对 [DeleteObjectVersionTagging](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObjectVersionTagging.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:GetObjectVersion"></a>

##### `s3:GetObjectVersion` {#policy-action.s3-GetObjectVersion}

*policy-action*

控制对 [GetObjectVersion](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectVersion.html) S3 API 操作的访问。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:BypassGovernanceRetention"></a>

##### `s3:BypassGovernanceRetention` {#policy-action.s3-BypassGovernanceRetention}

*policy-action*

控制对处于 [`GOVERNANCE`](/docs/reference/minio-mc/mc-retention-set/#mc.retention.set.MODE) 保留模式下锁定对象的以下 S3 API 操作的访问：

- `s3:PutObjectRetention`
- `s3:PutObject`
- `s3:DeleteObject`

更多信息请参见 S3 文档中的 [s3:BypassGovernanceRetention](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html#object-lock-managing-bypass)。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:object-lock-remaining-retention-days
s3:object-lock-retain-until-date
s3:object-lock-mode
s3:object-lock-legal-hold
s3:RequestObjectTagKeys
s3:RequestObjectTag/<key>
```

<a id="policy-action.s3:PutObjectRetention"></a>

##### `s3:PutObjectRetention` {#policy-action.s3-PutObjectRetention}

*policy-action*

控制对 [PutObjectRetention](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObjectRetention.html) S3 API 操作的访问。

对于任何指定了 [保留元数据](/docs/administration/object-management/object-retention/#minio-object-locking) 的 `PutObject` 操作，都需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:x-amz-server-side-encryption
s3:x-amz-server-side-encryption-customer-algorithm
s3:x-amz-server-side-encryption-aws-kms-key-id
s3:object-lock-remaining-retention-days
s3:object-lock-retain-until-date
s3:object-lock-mode
s3:versionid
```

<a id="policy-action.s3:GetObjectRetention"></a>

##### `s3:GetObjectRetention` {#policy-action.s3-GetObjectRetention}

*policy-action*

控制对 [GetObjectRetention](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectRetention.html) S3 API 操作的访问。

若要在 `GetObject` 或 `HeadObject` 操作的响应中包含 [对象锁定元数据](/docs/administration/object-management/object-retention/#minio-object-locking)，则需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:x-amz-server-side-encryption
s3:x-amz-server-side-encryption-customer-algorithm
s3:x-amz-server-side-encryption-aws-kms-key-id
s3:versionid
```

<a id="policy-action.s3:GetObjectLegalHold"></a>

##### `s3:GetObjectLegalHold` {#policy-action.s3-GetObjectLegalHold}

*policy-action*

控制对 [GetObjectLegalHold](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectLegalHold.html) S3 API 操作的访问。

若要在 `GetObject` 或 `HeadObject` 操作的响应中包含 [对象锁定元数据](/docs/administration/object-management/object-retention/#minio-object-locking)，则需要此权限。

<a id="policy-action.s3:PutObjectLegalHold"></a>

##### `s3:PutObjectLegalHold` {#policy-action.s3-PutObjectLegalHold}

*policy-action*

控制对 [PutObjectLegalHold](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObjectLegalHold.html) S3 API 操作的访问。

对于任何指定了 [legal hold 元数据](/docs/administration/object-management/object-retention/#minio-object-locking) 的 `PutObject` 操作，都需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:x-amz-server-side-encryption
s3:x-amz-server-side-encryption-customer-algorithm
s3:x-amz-server-side-encryption-aws-kms-key-id
s3:object-lock-legal-hold
s3:versionid
```

<a id="policy-action.s3:GetBucketObjectLockConfiguration"></a>

##### `s3:GetBucketObjectLockConfiguration` {#policy-action.s3-GetBucketObjectLockConfiguration}

*policy-action*

控制对 [GetObjectLockConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObjectLockConfiguration.html) S3 API 操作的访问。

<a id="policy-action.s3:PutBucketObjectLockConfiguration"></a>

##### `s3:PutBucketObjectLockConfiguration` {#policy-action.s3-PutBucketObjectLockConfiguration}

*policy-action*

控制对 [PutObjectLockConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutObjectLockConfiguration.html) S3 API 操作的访问。

### 存储桶通知 {#id10}

<a id="policy-action.s3:GetBucketNotification"></a>

##### `s3:GetBucketNotification` {#policy-action.s3-GetBucketNotification}

*policy-action*

控制对 [GetBucketNotification](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketNotification.html) S3 API 操作的访问。

<a id="policy-action.s3:PutBucketNotification"></a>

##### `s3:PutBucketNotification` {#policy-action.s3-PutBucketNotification}

*policy-action*

控制对 [PutBucketNotification](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketNotification.html) S3 API 操作的访问。

<a id="policy-action.s3:ListenNotification"></a>

##### `s3:ListenNotification` {#policy-action.s3-ListenNotification}

*policy-action*

用于控制与 MinIO 存储桶通知 相关 API 操作的 MinIO 扩展。

此 action **不** 用于其他兼容 S3 的服务。

<a id="policy-action.s3:ListenBucketNotification"></a>

##### `s3:ListenBucketNotification` {#policy-action.s3-ListenBucketNotification}

*policy-action*

用于控制与 MinIO 存储桶通知 相关 API 操作的 MinIO 扩展。

此 action **不** 用于其他兼容 S3 的服务。

### 对象生命周期管理 {#id11}

<a id="policy-action.s3:PutLifecycleConfiguration"></a>

##### `s3:PutLifecycleConfiguration` {#policy-action.s3-PutLifecycleConfiguration}

*policy-action*

控制对 [PutLifecycleConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketLifecycleConfiguration.html) S3 API 操作的访问。

<a id="policy-action.s3:GetLifecycleConfiguration"></a>

##### `s3:GetLifecycleConfiguration` {#policy-action.s3-GetLifecycleConfiguration}

*policy-action*

控制对 [GetLifecycleConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketLifecycleConfiguration.html) S3 API 操作的访问。

### 对象加密 {#id12}

<a id="policy-action.s3:PutEncryptionConfiguration"></a>

##### `s3:PutEncryptionConfiguration` {#policy-action.s3-PutEncryptionConfiguration}

*policy-action*

控制对 [PutEncryptionConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_PutBucketEncryption.html) S3 API 操作的访问。

<a id="policy-action.s3:GetEncryptionConfiguration"></a>

##### `s3:GetEncryptionConfiguration` {#policy-action.s3-GetEncryptionConfiguration}

*policy-action*

控制对 [GetEncryptionConfiguration](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketEncryption.html) S3 API 操作的访问。

### 存储桶复制 {#id13}

<a id="policy-action.s3:GetReplicationConfiguration"></a>

##### `s3:GetReplicationConfiguration` {#policy-action.s3-GetReplicationConfiguration}

*policy-action*

控制对 [GetBucketReplication](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetBucketReplication.html) S3 API 操作的访问。

<a id="policy-action.s3:PutReplicationConfiguration"></a>

##### `s3:PutReplicationConfiguration` {#policy-action.s3-PutReplicationConfiguration}

*policy-action*

控制对 [PutBucketReplication](https://docs.aws.amazon.com/AmazonS3/latest/API/PutBucketReplication.html) S3 API 操作的访问。

<a id="policy-action.s3:ReplicateObject"></a>

##### `s3:ReplicateObject` {#policy-action.s3-ReplicateObject}

*policy-action*

用于控制与 [服务器端存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 相关 API 操作的 MinIO 扩展。

MinIO 服务器端复制需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:ReplicateDelete"></a>

##### `s3:ReplicateDelete` {#policy-action.s3-ReplicateDelete}

*policy-action*

用于控制与 [服务器端存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 相关 API 操作的 MinIO 扩展。

作为 MinIO 服务器端复制的一部分，在同步 [删除操作](/docs/administration/object-management/object-delete/#minio-object-delete) 时需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:ReplicateTags"></a>

##### `s3:ReplicateTags` {#policy-action.s3-ReplicateTags}

*policy-action*

用于控制与 [服务器端存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 相关 API 操作的 MinIO 扩展。

MinIO 服务器端复制需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="policy-action.s3:GetObjectVersionForReplication"></a>

##### `s3:GetObjectVersionForReplication` {#policy-action.s3-GetObjectVersionForReplication}

*policy-action*

用于控制与 [服务器端存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 相关 API 操作的 MinIO 扩展。

MinIO 服务器端复制需要此权限。

支持以下附加 [condition keys](#minio-policy-conditions)：

```shell
s3:versionid
s3:ExistingObjectTag/<key>
```

<a id="minio-selected-conditional-actions"></a>
<a id="minio-policy-conditions"></a>

## 受支持的 S3 策略条件键 {#s3}

MinIO 策略文档支持 IAM [条件语句](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html)。

每个条件元素都由 [operators](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html) 和条件键组成。MinIO 支持 IAM 条件键的一个子集。 有关任何列出条件键的完整信息，请参见 [IAM Condition Element Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html)

对于所有受支持的 [actions](#minio-policy-actions)，MinIO 支持以下条件键：

- `aws:Referer`
- `aws:SourceIp`
- `aws:UserAgent`
- `aws:SecureTransport`
- `aws:CurrentTime`
- `aws:EpochTime`
- `aws:PrincipalType`
- `aws:userid`
- `aws:username`
- `s3:x-amz-content-sha256`
- `s3:signatureAge`

> [!CAUTION]
> **警告**
>
> `aws:Referer`、`aws:SourceIp` 和 `aws:UserAgent` 键可能被伪造，因此存在潜在安全风险。`aws:SourceIp` 的可信程度取决于负责提供或覆写转发请求头的代理边界。MinIO 建议仅将这些条件键作为辅助安全措施用于 *拒绝* 访问。
>
> **绝不要** 仅凭这三个键授予访问权限。

### 条件值来源与优先级 {#condition-value-sources}

> [!WARNING]
> **尚未发布的服务端行为（截至 2026-08-03）**
>
> 下表描述配套服务端改动 `2f55347f7`（台账编号 SN-2026-003）之后的行为，该改动已随 `RELEASE.2026-08-04T00-00-00Z` 及之后的每个 Silo 版本发布。在依赖这些优先级保证之前，请核对服务端发布说明。

Silo 按请求字段的实际语义来源构造条件值映射，而不是把所有请求头与查询参数混为一谈。原始请求头或查询参数即使与内部条件键同名，也不能覆盖服务端计算出的值，或伪造服务端没有提供的值。

| 条件键类别 | 策略求值使用的来源 | 优先级与兼容性 |
| :-- | :-- | :-- |
| 身份、时间、传输、认证、`s3:versionid`、`s3:LocationConstraint`、LDAP 与 JWT 值 | 已认证的凭据与声明、服务端时钟与传输状态，或该操作解析出的 API 字段 | 同名原始请求头与查询参数不能增加或覆盖这些值。`aws:Referer` 与 `aws:UserAgent` 按定义仍由客户端控制；`aws:SourceIp` 的限制见上方警告。 |
| `s3:signatureAge` | SigV4 预签名请求校验器计算出的已过去时间 | 只有通过校验的 SigV4 预签名请求才有该值；其他请求类型中客户端提供的 `x-amz-signature-age` Header 会被忽略。 |
| `s3:prefix`、`s3:delimiter`、`s3:max-keys` | 仅查询字符串 | 同名请求头不会参与这些列表条件的求值。 |
| `s3:x-amz-content-sha256`、`s3:x-amz-copy-source`、`s3:x-amz-metadata-directive` 与服务端加密条件键 | 仅对应的 HTTP 请求头 | 查询字符串中的替代值不能满足这些条件。尤其是预签名请求校验所使用的 `X-Amz-Content-Sha256` 查询值，不会作为策略条件值暴露。 |
| `s3:x-amz-storage-class` | `X-Amz-Storage-Class` 请求头，兼容回退到查询字符串 | 只要请求头存在就优先，即使它是空值。查询形式继续保留，以兼容现有上传路径。 |
| `s3:RequestObjectTag/<key>` 与 `s3:RequestObjectTagKeys` | 默认来自 `X-Amz-Tagging` Header；标签感知处理器可显式传入实际标签集 | `PutObject` 与 `CreateMultipartUpload` 从 Header 或兼容查询形式取值，Header 存在时优先；`PutObjectTagging` 使用解析后的 XML 请求正文。无关操作会忽略 query 标签。对于策略映射允许这些键的 action，历史 Header 回退仍为兼容性保留，因此在上述三个处理器之外，请求标签条件本身不能证明该操作会消费或持久化这些标签。 |
| `s3:ExistingObjectTag/<key>` | 从目标对象存储状态加载的标签 | 请求头与查询参数永远不能提供已有对象标签。只有在授权前加载这些标签的 API 路径上才有该值，包括对象 GET/HEAD 与对象标签处理器。 |
| 对象锁条件键 | 对象锁请求头，或处理器计算出的保留值 | 查询字符串中的同名字段会被忽略。 |

如果某条 API 路径没有加载或计算上述来源，相应条件键就是缺失的，其结果由所用策略操作符的语义决定。不要因为某个动作列出了条件键，就假定服务端一定会为它合成一个值。

对于特定 S3 action 支持的其他键，请参见该 action 的参考文档。

### MinIO 扩展条件键 {#minio}

MinIO 在 S3 标准条件键基础上扩展了以下键：

`sts:DurationSeconds`

> > [!NOTE]
> > **新增: MinIO**
> >
> > SERVER RELEASE.2024-02-06T21-36-22Z
>
> 指定一个以秒为单位的时间，用于限制由 [AssumeRoleWithWebIdentity](/docs/developers/security-token-service/AssumeRoleWithWebIdentity/#minio-sts-assumerolewithwebidentity) 生成的 *所有* Security Token Service 凭证的有效期。
>
> 此值会覆盖客户端指定的 `DurationSeconds` 字段。
>
> 例如：
>
> ```json
> {
>    "Version": "2012-10-17",
>    "Statement": [
>       {
>             "Effect": "Allow",
>             "Action": [
>                "sts:AssumeRoleWithWebIdentity"
>             ],
>             "Condition": {
>                "NumericLessThanEquals": {
>                   "sts:DurationSeconds": "300"
>                }
>             }
>       }
>    ]
> }
> ```

<a id="minio-policy-mc-admin-actions"></a>

## `mc admin` 策略 Action 键 {#mc-admin-action}

MinIO 支持以下 action，用于为 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 操作定义策略。 这些 action *仅* 对 MinIO 部署有效，*不* 用于其他兼容 S3 的服务：

<a id="policy-action.admin:*"></a>

#### `admin:*` {#policy-action.admin}

*policy-action*

所有 admin action 键的选择器。

<a id="policy-action.admin:Heal"></a>

#### `admin:Heal` {#policy-action.admin-Heal}

*policy-action*

允许执行 heal 命令

<a id="policy-action.admin:StorageInfo"></a>

#### `admin:StorageInfo` {#policy-action.admin-StorageInfo}

*policy-action*

允许列出服务器信息

<a id="policy-action.admin:DataUsageInfo"></a>

#### `admin:DataUsageInfo` {#policy-action.admin-DataUsageInfo}

*policy-action*

允许列出数据使用信息

<a id="policy-action.admin:TopLocksInfo"></a>

#### `admin:TopLocksInfo` {#policy-action.admin-TopLocksInfo}

*policy-action*

允许列出 top locks

<a id="policy-action.admin:Profiling"></a>

#### `admin:Profiling` {#policy-action.admin-Profiling}

*policy-action*

允许 profiling

<a id="policy-action.admin:ServerTrace"></a>

#### `admin:ServerTrace` {#policy-action.admin-ServerTrace}

*policy-action*

允许列出 server trace

<a id="policy-action.admin:ConsoleLog"></a>

#### `admin:ConsoleLog` {#policy-action.admin-ConsoleLog}

*policy-action*

允许在终端列出 console log

<a id="policy-action.admin:KMSCreateKey"></a>

#### `admin:KMSCreateKey` {#policy-action.admin-KMSCreateKey}

*policy-action*

允许创建新的 KMS 主密钥

虽然此选项仍受支持，但更推荐使用 [`kms:CreateKey`](#policy-action.kms-CreateKey)。

<a id="policy-action.admin:KMSKeyStatus"></a>

#### `admin:KMSKeyStatus` {#policy-action.admin-KMSKeyStatus}

*policy-action*

允许获取 KMS 密钥状态

虽然此选项仍受支持，但更推荐使用 [`kms:KeyStatus`](#policy-action.kms-KeyStatus)。

<a id="policy-action.admin:ServerInfo"></a>

#### `admin:ServerInfo` {#policy-action.admin-ServerInfo}

*policy-action*

允许列出服务器信息

<a id="policy-action.admin:OBDInfo"></a>

#### `admin:OBDInfo` {#policy-action.admin-OBDInfo}

*policy-action*

允许获取集群 on-board diagnostics

<a id="policy-action.admin:ServerUpdate"></a>

#### `admin:ServerUpdate` {#policy-action.admin-ServerUpdate}

*policy-action*

允许更新 MinIO 二进制文件

<a id="policy-action.admin:ServiceRestart"></a>

#### `admin:ServiceRestart` {#policy-action.admin-ServiceRestart}

*policy-action*

允许重启 MinIO 服务。

<a id="policy-action.admin:ServiceStop"></a>

#### `admin:ServiceStop` {#policy-action.admin-ServiceStop}

*policy-action*

允许停止 MinIO 服务。

<a id="policy-action.admin:ConfigUpdate"></a>

#### `admin:ConfigUpdate` {#policy-action.admin-ConfigUpdate}

*policy-action*

允许管理 MinIO 配置

<a id="policy-action.admin:CreateUser"></a>

#### `admin:CreateUser` {#policy-action.admin-CreateUser}

*policy-action*

允许创建 MinIO 用户

<a id="policy-action.admin:DeleteUser"></a>

#### `admin:DeleteUser` {#policy-action.admin-DeleteUser}

*policy-action*

允许删除 MinIO 用户

<a id="policy-action.admin:ListUsers"></a>

#### `admin:ListUsers` {#policy-action.admin-ListUsers}

*policy-action*

允许列出用户

<a id="policy-action.admin:EnableUser"></a>

#### `admin:EnableUser` {#policy-action.admin-EnableUser}

*policy-action*

允许把用户的目标状态改为 `enabled`。该 action **不能**授权把目标状态改为 `disabled`。

<a id="policy-action.admin:DisableUser"></a>

#### `admin:DisableUser` {#policy-action.admin-DisableUser}

*policy-action*

允许把用户的目标状态改为 `disabled`。该 action **不能**授权把目标状态改为 `enabled`。

> [!IMPORTANT]
> SILO 根据请求的目标状态鉴权用户状态变更：`enabled` 必须具备 `admin:EnableUser`，`disabled` 必须具备 `admin:DisableUser`。负责两个方向的角色必须显式获得两个 action；内置 `consoleAdmin` 已通过 `admin:*` 同时具备它们。权限矩阵、最小权限策略示例、兼容性迁移和严格分离的设计决策详见[一个端点，两种权限](/blog/design/user-status-permissions/)。

<a id="policy-action.admin:GetUser"></a>

#### `admin:GetUser` {#policy-action.admin-GetUser}

*policy-action*

允许对用户信息执行 GET

<a id="policy-action.admin:AddUserToGroup"></a>

#### `admin:AddUserToGroup` {#policy-action.admin-AddUserToGroup}

*policy-action*

允许将用户添加到组

<a id="policy-action.admin:RemoveUserFromGroup"></a>

#### `admin:RemoveUserFromGroup` {#policy-action.admin-RemoveUserFromGroup}

*policy-action*

允许将用户从组中移除

<a id="policy-action.admin:GetGroup"></a>

#### `admin:GetGroup` {#policy-action.admin-GetGroup}

*policy-action*

允许获取组信息

<a id="policy-action.admin:ListGroups"></a>

#### `admin:ListGroups` {#policy-action.admin-ListGroups}

*policy-action*

允许列出组

<a id="policy-action.admin:EnableGroup"></a>

#### `admin:EnableGroup` {#policy-action.admin-EnableGroup}

*policy-action*

允许把组的目标状态改为 `enabled`，但不能据此禁用组。详见[用户与组状态权限](/blog/design/user-status-permissions/)。

<a id="policy-action.admin:DisableGroup"></a>

#### `admin:DisableGroup` {#policy-action.admin-DisableGroup}

*policy-action*

允许把组的目标状态改为 `disabled`，但不能据此启用组。负责完整组生命周期的角色需要同时授予两个 action。

<a id="policy-action.admin:CreatePolicy"></a>

#### `admin:CreatePolicy` {#policy-action.admin-CreatePolicy}

*policy-action*

允许创建策略

<a id="policy-action.admin:DeletePolicy"></a>

#### `admin:DeletePolicy` {#policy-action.admin-DeletePolicy}

*policy-action*

允许删除策略

<a id="policy-action.admin:GetPolicy"></a>

#### `admin:GetPolicy` {#policy-action.admin-GetPolicy}

*policy-action*

允许获取策略

<a id="policy-action.admin:AttachUserOrGroupPolicy"></a>

#### `admin:AttachUserOrGroupPolicy` {#policy-action.admin-AttachUserOrGroupPolicy}

*policy-action*

允许将策略附加到用户/组

<a id="policy-action.admin:ListUserPolicies"></a>

#### `admin:ListUserPolicies` {#policy-action.admin-ListUserPolicies}

*policy-action*

允许列出用户策略

<a id="policy-action.admin:CreateServiceAccount"></a>

#### `admin:CreateServiceAccount` {#policy-action.admin-CreateServiceAccount}

*policy-action*

允许创建 MinIO Access Key

<a id="policy-action.admin:UpdateServiceAccount"></a>

#### `admin:UpdateServiceAccount` {#policy-action.admin-UpdateServiceAccount}

*policy-action*

允许更新 MinIO Access Key

<a id="policy-action.admin:RemoveServiceAccount"></a>

#### `admin:RemoveServiceAccount` {#policy-action.admin-RemoveServiceAccount}

*policy-action*

允许删除 MinIO Access Key

<a id="policy-action.admin:ListServiceAccounts"></a>

#### `admin:ListServiceAccounts` {#policy-action.admin-ListServiceAccounts}

*policy-action*

允许列出 MinIO Access Key

<a id="policy-action.admin:SetBucketQuota"></a>

#### `admin:SetBucketQuota` {#policy-action.admin-SetBucketQuota}

*policy-action*

允许设置存储桶配额

<a id="policy-action.admin:GetBucketQuota"></a>

#### `admin:GetBucketQuota` {#policy-action.admin-GetBucketQuota}

*policy-action*

允许获取存储桶配额

<a id="policy-action.admin:SetBucketTarget"></a>

#### `admin:SetBucketTarget` {#policy-action.admin-SetBucketTarget}

*policy-action*

允许设置存储桶目标

<a id="policy-action.admin:GetBucketTarget"></a>

#### `admin:GetBucketTarget` {#policy-action.admin-GetBucketTarget}

*policy-action*

允许获取存储桶目标

<a id="policy-action.admin:SetTier"></a>

#### `admin:SetTier` {#policy-action.admin-SetTier}

*policy-action*

允许使用 [`mc ilm tier`](/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier) 命令创建和修改远程存储层。

<a id="policy-action.admin:ListTier"></a>

#### `admin:ListTier` {#policy-action.admin-ListTier}

*policy-action*

允许使用 [`mc ilm tier`](/docs/reference/minio-mc/mc-ilm-tier/#command-mc.ilm.tier) 命令列出已配置的远程存储层。

<a id="policy-action.admin:BandwidthMonitor"></a>

#### `admin:BandwidthMonitor` {#policy-action.admin-BandwidthMonitor}

*policy-action*

允许获取与当前带宽消耗相关的指标。

<a id="policy-action.admin:Prometheus"></a>

#### `admin:Prometheus` {#policy-action.admin-Prometheus}

*policy-action*

允许访问 MinIO [metrics](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)。 仅当 MinIO 要求采集指标时进行认证才需要此权限。

<a id="policy-action.admin:ListBatchJobs"></a>

#### `admin:ListBatchJobs` {#policy-action.admin-ListBatchJobs}

*policy-action*

允许访问并列出活动中的批处理作业。

<a id="policy-action.admin:DescribeBatchJob"></a>

#### `admin:DescribeBatchJob` {#policy-action.admin-DescribeBatchJob}

*policy-action*

允许访问并查看正在运行的批处理作业的定义详情。

<a id="policy-action.admin:StartBatchJob"></a>

#### `admin:StartBatchJob` {#policy-action.admin-StartBatchJob}

*policy-action*

允许用户启动批处理作业运行。

<a id="policy-action.admin:CancelBatchJob"></a>

#### `admin:CancelBatchJob` {#policy-action.admin-CancelBatchJob}

*policy-action*

允许用户停止当前正在执行的批处理作业。

<a id="policy-action.admin:Rebalance"></a>

#### `admin:Rebalance` {#policy-action.admin-Rebalance}

*policy-action*

允许访问并启动、查询或停止跨不同可用存储空间池的对象重平衡。

## KMS 策略 action 键 {#kms-action}

MinIO 支持通过策略限制密钥管理服务 (KMS) action。

可以在策略中使用以下任一 KMS action 来限制 KMS 活动：

<a id="policy-action.kms:Status"></a>

#### `kms:Status` {#policy-action.kms-Status}

*policy-action*

检查 KMS 状态。

<a id="policy-action.kms:Metrics"></a>

#### `kms:Metrics` {#policy-action.kms-Metrics}

*policy-action*

获取 Prometheus 格式指标。

<a id="policy-action.kms:API"></a>

#### `kms:API` {#policy-action.kms-API}

*policy-action*

列出受支持的 API 端点。

<a id="policy-action.kms:Version"></a>

#### `kms:Version` {#policy-action.kms-Version}

*policy-action*

获取 KMS 版本。

<a id="policy-action.kms:CreateKey"></a>

#### `kms:CreateKey` {#policy-action.kms-CreateKey}

*policy-action*

创建新的 KMS 密钥。

<a id="policy-action.kms:ListKeys"></a>

#### `kms:ListKeys` {#policy-action.kms-ListKeys}

*policy-action*

获取现有 KMS 密钥列表。

<a id="policy-action.kms:KeyStatus"></a>

#### `kms:KeyStatus` {#policy-action.kms-KeyStatus}

*policy-action*

获取指定 KMS 密钥的状态。

若要选择所有可用的 kms 策略 action，可使用 `kms:*`。

> [!NOTE]
> **变更: RELEASE.2024-07-16T23-46-41Z**
>
> KMS action 可以按资源或资源前缀进行限制。 可以使用通配符 `*` 将 KMS action 策略应用到所有匹配该前缀的资源。
>
> 例如，以下策略文档允许用户列出密钥、创建新密钥，并检查任何以 `keys-abc-` 或 `myuser-` 开头资源上的密钥状态。
>
> ```shell
> {
>     "Version": "2012-10-17",
>     "Statement": [
>         {
>             "Effect": "Allow",
>             "Action": [
>                 "kms:CreateKey",
>                 "kms:KeyStatus",
>                 "kms:ListKeys"
>             ],
>             "Resource": [
>                 "arn:minio:kms:::keys-abc-*",
>                 "arn:minio:kms:::myuser-*"
>             ]
>         }
>     ]
> }
> ```

## `mc admin` 策略条件键 {#mc-admin}

MinIO 支持以下条件，用于为 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) [actions](#minio-policy-mc-admin-actions) 定义策略。

- `aws:Referer`
- `aws:SourceIp`
- `aws:UserAgent`
- `aws:SecureTransport`
- `aws:CurrentTime`
- `aws:EpochTime`

有关任何列出条件键的完整信息，请参见 [IAM Condition Element Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition.html)。

## 策略变量 {#id14}

MinIO 支持使用策略变量，将来自已认证用户和/或操作的上下文自动替换到分配给该用户的一个或多个策略中。 使用 `${POLICYVARIABLE}` 格式在策略的 `Condition` 或 `Resource` 定义中指定变量。 MinIO 策略变量的工作方式类似于 [AWS IAM policy elements: Variables and tags](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html)。

每种 MinIO [identity provider](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 都支持其各自的一组策略变量：

- [MinIO 策略变量](#minio-policy-variables-internal)
- [OpenID 策略变量](#minio-policy-variables-oidc)
- [Active Directory / LDAP 策略变量](#minio-policy-variables-ad-ldap)

<a id="id15"></a>

### MinIO 策略变量 {#minio-policy-variables-internal}

下表列出了用于授权 [MinIO-managed users](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp) 的推荐策略变量：

| 变量 | 说明 |
| --- | --- |
| [aws:referrer](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-referer) | 已认证 API 调用的 HTTP 头中的 referrer。 |
| [aws:SourceIp](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-sourceip) | 已认证 API 调用的 HTTP 头中的源 IP。 |
| [aws:username](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-username) | 与已认证 API 调用关联的用户名。 |

例如，以下策略使用变量将已认证用户的用户名替换到 `Resource` 字段中，使该用户只能访问与其用户名匹配的那些前缀：

```json
{
"Version": "2012-10-17",
"Statement": [
      {
         "Action": ["s3:ListBucket"],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket"],
         "Condition": {"StringLike": {"s3:prefix": ["${aws:username}/*"]}}
      },
      {
         "Action": [
         "s3:GetObject",
         "s3:PutObject"
         ],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket/${aws:username}/*"]
      }
   ]
}
```

MinIO 会将 `Resource` 字段中的 `${aws:username}` 变量替换为用户名。 随后 MinIO 对策略进行求值，并授予或撤销对所请求 API 和资源的访问。

<a id="minio-policy-variables-oidc"></a>

### OpenID 策略变量 {#openid}

下表列出了用于授权 [OIDC 管理用户](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 的受支持策略变量。

每个变量都对应认证用户 JWT token 中返回的一项 claim：

| 变量 | 说明 |
| --- | --- |
| `jwt:sub` | 返回用户的 `sub` claim。 |
| `jwt:iss` | 返回 ID token 中的 Issuer Identifier claim。 |
| `jwt:aud` | 返回 ID token 中的 Audience claim。 |
| `jwt:jti` | 返回客户端认证信息中的 JWT ID claim。 |
| `jwt:upn` | 返回客户端认证信息中的 User Principal Name claim。 |
| `jwt:name` | 返回用户的 `name` claim。 |
| `jwt:groups` | 返回用户的 `groups` claim。 |
| `jwt:given_name` | 返回用户的 `given_name` claim。 |
| `jwt:family_name` | 返回用户的 `family_name` claim。 |
| `jwt:middle_name` | 返回用户的 `middle_name` claim。 |
| `jwt:nickname` | 返回用户的 `nickname` claim。 |
| `jwt:preferred_username` | 返回用户的 `preferred_username` claim。 |
| `jwt:profile` | 返回用户的 `profile` claim。 |
| `jwt:picture` | 返回用户的 `picture` claim。 |
| `jwt:website` | 返回用户的 `website` claim。 |
| `jwt:email` | 返回用户的 `email` claim。 |
| `jwt:gender` | 返回用户的 `gender` claim。 |
| `jwt:birthdate` | 返回用户的 `birthdate` claim。 |
| `jwt:phone_number` | 返回用户的 `phone_number` claim。 |
| `jwt:address` | 返回用户的 `address` claim。 |
| `jwt:scope` | 返回用户的 `scope` claim。 |
| `jwt:client_id` | 返回用户的 `client_id` claim。 |

关于这些 scope 的更多信息，请参阅 [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html) 文档。 你所选的 OIDC 提供方也可能有更具体的补充文档。

例如，以下策略使用变量将认证用户的 `preferred_username` 替换到 `Resource` 字段中， 使该用户只能访问与其用户名匹配的前缀：

```json
{
"Version": "2012-10-17",
"Statement": [
      {
         "Action": ["s3:ListBucket"],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket"],
         "Condition": {"StringLike": {"s3:prefix": ["${jwt:preferred_username}/*"]}}
      },
      {
         "Action": [
         "s3:GetObject",
         "s3:PutObject"
         ],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket/${jwt:preferred_username}/*"]
      }
   ]
}
```

MinIO 会将 `Resource` 字段中的 `${jwt:preferred_username}` 变量， 替换为 JWT token 中 `preferred_username` 的值。 随后，MinIO 会评估该策略，并对请求的 API 和资源授予或撤销访问权限。

<a id="minio-policy-variables-ad-ldap"></a>

### Active Directory / LDAP 策略变量 {#active-directory-ldap}

下表列出了用于授权 [AD/LDAP users](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 的受支持策略变量：

<table>
  <thead>
    <tr>
      <th><p>变量</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>ldap:username</code></p></td>
      <td>已认证用户的简单用户名（<code>name</code>）。<p>这不同于用户的 DistinguishedName 或 CommonName。</p></td>
    </tr>
    <tr>
      <td><p><code>ldap:user</code></p></td>
      <td><p>已认证用户使用的 Distinguished Name。</p></td>
    </tr>
    <tr>
      <td><p><code>ldap:groups</code></p></td>
      <td><p>已认证用户的组 Distinguished Name。</p></td>
    </tr>
  </tbody>
</table>

例如，以下策略使用变量将已认证用户的 `name` 替换到 `Resource` 字段中，使该用户只能访问与其名称匹配的那些前缀：

```json
{
"Version": "2012-10-17",
"Statement": [
      {
         "Action": ["s3:ListBucket"],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket"],
         "Condition": {"StringLike": {"s3:prefix": ["${ldap:username}/*"]}}
      },
      {
         "Action": [
         "s3:GetObject",
         "s3:PutObject"
         ],
         "Effect": "Allow",
         "Resource": ["arn:aws:s3:::mybucket/${ldap:username}/*"]
      }
   ]
}
```

MinIO 会将 `Resource` 字段中的 `${ldap:username}` 变量替换为已认证用户的 `name` 值。 随后 MinIO 对策略进行求值，并授予或撤销对所请求 API 和资源的访问。