---
title: "管理对象"

weight: 20
---

<a id="minio-console-managing-objects"></a>
<a id="id1"></a>

你可以使用 MinIO Console 执行 MinIO 提供的多种存储桶和对象管理及交互操作。 根据已认证用户的权限和 IAM 策略，你可以：

- [浏览、上传、回退、管理并与对象交互](#minio-console-object-browser)。
- [浏览、创建和管理存储桶](#minio-console-buckets)。
- [创建或监控远程层](#minio-console-tiers)，以支持对象转换规则。

<a id="id3"></a>

## 对象浏览器 {#minio-console-object-browser}

对象浏览器会列出已认证用户在该部署上有权访问的存储桶和对象。

登录后或切换到该标签页时，对象浏览器会显示该用户的存储桶列表，用户可以对其进行筛选。 选择某个存储桶可显示该桶中的对象列表。

选择某个具体对象后，可显示该对象的摘要信息，例如名称、大小、标签、法律保留以及适用的保留策略。 Console 还会显示该对象的元数据。

用户可根据适用的策略和权限，对存储桶中的对象执行操作。 用户可能可以执行的操作包括：

- 回退到先前版本
- 创建前缀
- 查看已删除对象
- 上传对象
- 下载对象
- 分享
- 预览
- 管理法律保留
- 管理保留策略
- 管理标签
- 检查
- 显示版本
- [删除](/docs/administration/object-management/object-delete/#minio-object-delete)

> [!NOTE]
> **新增: Console**
>
> v0.24.0
>
> 可通过 Console 右上角的对象管理器按钮查看对象上传或下载状态。 如果你在当前会话期间未上传或下载任何对象，则不会显示该按钮。

> [!NOTE]
> **变更: Console**
>
> v0.35.0
>
> 如果你选择下载多个对象，MinIO 会将这些对象打包为一个 ZIP 归档供下载。 下载后你必须解压该归档，才能访问其中的文件。

<a id="minio-console-buckets"></a>
<a id="id4"></a>

## 存储桶 {#minio-console-admin-buckets}

Console 的 **Bucket** 部分会显示已认证用户具有 [访问权限](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 的所有存储桶。 你可以根据该用户的访问权限，在此部分中创建或管理这些存储桶。

### 创建存储桶 {#id5}

选择 **Create Bucket** 可在该部署上创建新的存储桶。 MinIO 会校验存储桶名称。 如需查看存储桶命名规则，请选择 **View Bucket Naming Rules**。

MinIO 不限制单个部署允许创建的存储桶总数。 不过，作为通用建议，MinIO 建议每个部署的存储桶数量不超过 500,000 个。

创建存储桶时，你可以启用以下功能：[版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning), [对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking), 存储桶大小（配额）限制，以及 [保留规则](/docs/administration/object-management/object-retention/#minio-object-locking-retention-modes)。 保留规则要求启用版本控制。

> [!NOTE]
> **变更: Console**
>
> v0.35.0
>
> 如果启用版本控制，你可以指定要排除在版本控制之外的前缀。

你 **必须** 在创建存储桶时配置复制、锁定和版本控制选项。 之后无法再更改该存储桶的这些设置。

### 管理存储桶 {#id6}

使用 **Search** 栏筛选特定存储桶。 选择某个存储桶所在行可显示该存储桶的摘要信息。

在摘要页面中，选择任一可用标签页以进一步管理该存储桶。

> [!NOTE]
> **说明**
>
> 如果已认证用户没有 [所需的管理权限](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-mc-admin-actions)，某些管理功能可能不可用。

管理存储桶时，你的访问设置可能允许你查看或更改以下内容：

- **Summary** 部分显示存储桶配置的摘要。

  你可以在此部分查看和修改存储桶的访问策略、加密、配额和标签。
- 在 **Events** 部分配置告警，以便在用户上传、访问或删除匹配对象时触发 [通知事件](/docs/administration/monitoring/bucket-notifications/#minio-bucket-notifications)。
- 在 **Replication** 部分使用 [服务端存储桶复制规则](/docs/administration/bucket-replication/#minio-bucket-replication-serverside) 将对象复制到远程位置。
- 在 **Lifecycle** 部分设置 [对象生命周期管理规则](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management)，以过期或转换存储桶中的对象。
- 在 **Access** 部分通过列出对该存储桶有访问权限的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 和 [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 来审查安全设置。
- 在 **Anonymous** 部分管理未认证用户可用于读取或写入对象的前缀规则，以妥善保护匿名访问。

<a id="id7"></a>

## 层 {#minio-console-tiers}

**Tiering** 部分提供了用于添加和管理 [远程层](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 的界面，以支持生命周期管理转换规则。 MinIO 分层支持将对象从该部署迁移到远程存储，但不支持自动将其恢复到该部署。

分层标签页允许具有相应权限的用户执行以下操作：

- 查看所有已配置远程层的状态和摘要信息。
- 为新的远程目标存储创建层，目标可以是另一个 MinIO 部署、Google Cloud Storage、Amazon 的 AWS S3 或 Azure。
- 使用层上的 <svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-pencil" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"></path></svg> 图标轮换任意已配置层的访问凭证。