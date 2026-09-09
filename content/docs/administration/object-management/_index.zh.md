---
title: "对象管理"

weight: 120
icon: fa-solid fa-box-archive
---

<a id="id1"></a>

- [Versioning overview](https://youtu.be/XGOiwV6Cbuk?ref=docs)
- [Object locking and retention overview](https://youtu.be/Hk9Z-sltUu8?ref=docs)
- [MinIO Object Lifecycle Management Part I](https://youtu.be/Exg2KsfzHzI?ref=docs)
- [MinIO Object Lifecycle Management Part II](https://youtu.be/5fz3rE3wjGg?ref=docs)

<a id="objects"></a>

[对象](#objects) 是二进制数据，例如图像、音频文件、电子表格，甚至二进制可执行代码。 “Binary Large Object” 或 “blob” 这一术语有时会与对象存储关联使用，不过 blob 的大小可以从几个字节到数 TB 不等。 像 MinIO 这样的对象存储平台提供专用工具和能力，用于通过标准的 S3 兼容 API 存储、列出和获取对象。

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

<a id="buckets"></a>

MinIO 对象存储使用 [存储桶](#buckets) 组织对象。 存储桶类似于文件系统中的顶层驱动器、文件夹或目录（`/mnt/data` 或 `C:\`），每个存储桶都可以容纳任意数量的对象。

MinIO 服务器上的对象结构可能类似如下：

```text
/ #root
/images/
   2020-01-02-MinIO-Diagram.png
   2020-01-03-MinIO-Advanced-Deployment.png
   MinIO-Logo.png
/videos/
   2020-01-04-MinIO-Interview.mp4
/articles/
   /john.doe/
      2020-01-02-MinIO-Object-Storage.md
      2020-01-02-MinIO-Object-Storage-comments.json
   /jane.doe/
      2020-01-03-MinIO-Advanced-Deployment.png
      2020-01-02-MinIO-Advanced-Deployment-comments.json
      2020-01-04-MinIO-Interview.md
```

按照上述示例结构，管理员会创建 `/images`、`/videos` 和 `/articles` 这些存储桶。 客户端应用使用对象的完整“路径”将对象写入这些存储桶，其中包括所有中间 [前缀](/zh/glossary/#term-prefix)。

MinIO 使用前缀支持多级嵌套目录和对象，以支撑最动态的对象存储工作负载。 MinIO 使用 `/` 作为分隔符，从完整对象路径中自动推断中间前缀，例如 `/articles/john.doe`。 客户端和管理员都不应手动创建这些前缀。

客户端和管理员都不需要手动创建中间前缀，因为 MinIO 会根据对象名称自动推断它们。

<a id="minio-object-management-path-virtual-access"></a>

## Path 与 Virtual Host 存储桶访问 {#path-virtual-host}

MinIO 同时支持 [path-style](https://docs.aws.amazon.com/AmazonS3/latest/userguide/VirtualHosting.html#path-style-access) （默认）和 [virtual-host bucket lookups](https://docs.aws.amazon.com/AmazonS3/latest/userguide/VirtualHosting.html) 。

例如，假设某个 MinIO 部署分配的完全限定域名（FQDN）为 `minio.example.net`：

- 使用 path-style 查找时，应用将存储桶的完整路径指定为 `minio.example.net/mybucket` 这类形式。
- 使用 virtual-host 查找时，应用将存储桶指定为子域名，例如 `mybucket.minio.example.net/`。

某些应用在针对 MinIO 执行 S3 操作时，可能要求或预期支持 virtual-host 查找。 要启用 virtual-host 存储桶查找，必须将 [`MINIO_DOMAIN`](/docs/reference/minio-server/settings/core/#envvar.MINIO_DOMAIN) 环境变量设置为可解析到 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr>。

如果配置了 `MINIO_DOMAIN`，则 **必须** 视指定 FQDN 的所有子域名为专门保留给存储桶名称使用。 任何与这些域名冲突的 MinIO 服务（例如复制目标）都可能因为冲突而表现出意外或不符合预期的行为。

例如，如果设置 `MINIO_DOMAIN=minio.example.net`，则 **不能** 将 `minio.example.net` 的任何子域名（即 `*.minio.example.net` 形式）分配给任何 MinIO 服务或目标。 这包括用于 [bucket](/docs/administration/bucket-replication/#minio-bucket-replication)、[batch](/docs/administration/batch-framework-job-replicate/#minio-batch-framework-replicate-job) 或 [site replication](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview) 的主机名。

> [!WARNING]
> **重要**
>
> 对于 [启用 TLS](/docs/operations/network-encryption/#minio-tls) 的部署，**必须** 确保 TLS 证书的 SAN 覆盖 [`MINIO_DOMAIN`](/docs/reference/minio-server/settings/core/#envvar.MINIO_DOMAIN) 中最左侧域名下的所有子域名。
>
> 例如，`MINIO_DOMAIN=minio.example.net` 的情况要求 TLS SAN 覆盖 `minio.example.net` 的所有子域名。 可以额外设置一个 `*.minio.example.net` 的 TLS SAN，以正确覆盖该子域命名空间。
>
> TLS 通配符规则不允许继续匹配更深层级的子域名，因此，带有 `*.example.net` 通配符 SAN 的 TLS 证书 **不能** 覆盖 `*.minio.example.net` 这样的 virtual host 查找。

## 对象组织与规划 {#id3}

管理员通常负责控制存储桶的创建和配置。 之后，客户端应用可以使用 [S3 兼容 SDK](/docs/developers/minio-drivers/#minio-drivers) 在 MinIO 部署上创建、列出、获取并 [删除](/docs/administration/object-management/object-delete/#minio-object-delete) 对象。 因此，客户端决定给定存储桶或前缀中的整体数据层次结构，而管理员则可以通过 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 控制对某个操作或资源的授权或拒绝。

MinIO 对于给定部署中的存储桶、对象或前缀数量没有硬性的 [阈值](/docs/operations/concepts/thresholds/#minio-server-limits)。 不过，MinIO 部署底层硬件和网络的相对性能，可能会对单个前缀或存储桶中可承载的对象数量形成实际限制。 具体而言，使用较慢驱动器或网络基础设施的硬件，在对象层次结构较为扁平的存储桶或前缀中通常会表现出较差的性能。 有关其他需要注意的考量、阈值或限制，请参见 [阈值与限制](/docs/operations/concepts/thresholds/#minio-server-limits)。

对于客户端应用的工作负载模式，可将以下几点作为一般性指导：

- 使用普通或预算导向硬件的部署，应将每个前缀 10,000 个对象作为工作负载架构设计的基线目标。 然后基于真实工作负载的基准测试和监控结果，提高这一目标，直到硬件能够有意义地承载的上限。
- 使用高性能或企业级 [硬件](/docs/operations/checklists/hardware/#deploy-minio-distributed-recommendations) 的部署，通常可以处理每个前缀数百万甚至更多对象。

[MinIO SUBNET](https://min.io/pricing?jmp=docs) 企业账户可将年度架构评审纳入部署和维护策略，以确保依赖 MinIO 的项目在长期内保持性能与成功运行。

若要更深入了解限制前缀内容数量的收益，请参阅 [优化 S3 性能](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html) 一文。

> [!NOTE]
> **说明**
>
> 无论 Windows 文件系统是否支持，MinIO 都不支持在对象名称中使用 `\` 或 `:` 字符。 请在对象名称中使用 `/` 作为分隔符，以便 MinIO 使用 [前缀](/zh/glossary/#term-prefix) 自动创建文件夹结构。

## 对象版本控制 {#id4}

<img src="/images/retention/minio-versioning-multiple-versions.svg" alt="Object with Multiple Versions" style="max-width: 100%; height: auto;" />

在存储桶上执行写入、列出、获取或 [删除](/docs/administration/object-management/object-delete/#minio-object-delete) 操作时，具体的客户端行为取决于该存储桶的版本控制状态：

<table>
  <thead>
    <tr>
      <th><p>操作</p></th>
      <th><p>已启用版本控制</p></th>
      <th><p>已禁用版本控制 | 已挂起</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>PUT</code> (写入)</p></td>
      <td><p>为对象创建一个新的完整版本作为“最新”版本，并分配唯一的版本 ID</p></td>
      <td><p>创建对象；如果命名空间匹配则覆盖已有对象。</p></td>
    </tr>
    <tr>
      <td><p><code>GET</code> (读取)</p></td>
      <td><p>默认获取对象的最新版本</p><p>支持通过版本 ID 获取任意对象版本。</p></td>
      <td><p>获取对象</p></td>
    </tr>
    <tr>
      <td><p><code>LIST</code> (读取)</p></td>
      <td><p>获取指定存储桶或前缀下对象的最新版本</p><p>支持获取所有对象及其关联的版本 ID。</p></td>
      <td><p>获取指定存储桶或前缀下的所有对象</p></td>
    </tr>
    <tr>
      <td><p><code>DELETE</code> (写入)</p></td>
      <td><p>为对象创建一个 0 字节的“Delete Marker”作为“最新”版本（软删除）</p><p>支持通过版本 ID 删除任意对象版本（硬删除）。
硬删除操作无法撤销。</p><p>更多信息请参见 <a href="/docs/administration/object-management/object-delete/#minio-object-delete">对象删除</a>。</p></td>
      <td><p>删除对象</p></td>
    </tr>
  </tbody>
</table>

有关更完整的文档，请参见 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。

<a id="id5"></a>

## 对象标签 {#minio-object-tagging}

MinIO 支持向对象添加自定义标签。 标签是包含在对象元数据中的键值对。 标签可用于配合策略控制访问，或者通过 [`mc find --tags`](/docs/reference/minio-mc/mc-find/#mc.find.-tags) 定位对象。

MinIO 支持为单个对象最多添加 10 个自定义标签。

有关设置标签的更多信息，请参见 [`mc tag set`](/docs/reference/minio-mc/mc-tag-set/#command-mc.tag.set)。

## 对象保留 {#id6}

MinIO 对象锁定（“对象保留”）通过强制执行一次写入、多次读取（WORM）不可变性，防止 [已启用版本控制的对象](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 被删除。 MinIO 同时支持 [基于时长的对象保留](/docs/administration/object-management/object-retention/#minio-object-locking-retention-modes) 和 [无限期 legal hold 保留](/docs/administration/object-management/object-retention/#minio-object-locking-legalhold)。

<img src="/images/retention/minio-object-locking.svg" alt="30 Day Locked Objects" style="max-width: 600px; height: auto;" />

针对受 WORM 锁定对象的删除操作，结果取决于具体操作类型：

- 未指定版本 ID 的删除操作会创建一个 “Delete Marker”
- 指定受锁定对象版本 ID 的删除操作会返回 WORM locking error

只有在首次创建存储桶时才能启用对象锁定。 启用存储桶锁定也会同时启用 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。

根据 [Cohasset Associates](https://min.io/cohasset?ref=docs) 的说明，MinIO 对象锁定 提供关键的数据保留合规能力，并满足 SEC17a-4(f)、FINRA 4511(C) 和 CFTC 1.31(c)-(d) 的要求。

有关更完整的文档，请参见 [MinIO 对象锁定](/docs/administration/object-management/object-retention/#minio-object-locking) 和 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

## 对象生命周期管理 {#id7}

MinIO 对象生命周期管理允许为对象创建基于时间或日期的自动过渡或过期规则。 对于对象过渡，MinIO 会自动将对象移动到已配置的远程存储层。 对于对象过期，MinIO 会自动删除对象。

MinIO 在 [启用和未启用版本控制的存储桶](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 上应用生命周期管理规则时，其行为与常规客户端操作一致。 可以指定处理最新对象版本、非当前对象版本或同时处理两者的过渡或生命周期规则。

MinIO 生命周期管理在行为和语法上与 [AWS S3 Lifecycle Management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html) 保持兼容。 MinIO 使用 JSON 描述生命周期管理规则。 导入在 S3 或类似兼容平台上创建的规则时，可能需要在 XML 和 JSON 之间进行转换。

有关更完整的文档，请参见 [对象生命周期管理](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management)。

## 目标存储桶注意事项 {#id8}

MinIO *不* 要求目标存储桶在对象管理或版本控制配置上与源存储桶保持一致。 目标存储桶 *可以* 拥有自己的一组对象管理规则，但前提是经过谨慎定义。

目标存储桶 *不应* 拥有自己的过期规则或额外分层规则。 过期规则可能导致仍被源存储桶使用的分层数据被移除。 分层到额外远端会在热层与其数据之间增加额外的网络跳数，同时也会提升运维复杂度。

远程存储桶 *可以* 配置对象锁定或版本控制。

在目标存储桶上启用版本控制或对象锁定可能带来如下影响：

- 目标存储桶上设置的对象锁定，可能导致源存储桶期望执行的 `delete` 操作无法完成。
- MinIO 对对象进行分层时会为其分配自己的 `UUID`，因此目标存储桶上的版本控制至多只是冗余配置。
- 目标端的存储效率降低，因为 `delete` 操作会创建 `DeleteMarker`，而不是释放空间。
- 源存储桶和目标存储桶中可能出现重复的删除标记。

## 对远程数据的独占访问 {#id9}

MinIO **必须** 对目标存储桶拥有 *独占* 访问权。 任何其他用户、进程、应用或资源都不应访问目标存储桶，也不应对其执行任何操作。

对已过渡对象的所有访问都 *必须* 仅通过 MinIO 的 S3 API 操作进行。 手动修改已过渡对象，无论是热 MinIO 层上的元数据，还是远程温/冷层上的对象数据，都可能导致该对象数据丢失。

MinIO 会忽略远程存储桶或存储桶前缀中任何不由该 MinIO 部署显式管理的对象。 自动过渡和透明对象读取依赖以下假设：

- 远程存储上的对象不会被外部修改、迁移或删除。
- 远程存储桶上不存在生命周期管理规则（例如过渡或过期）。

为实现这种独占访问，应在其 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 中向生命周期管理用户授予目标存储桶的 `read`、`write` 和 `delete` 访问权限。 所有其他策略都应对目标存储桶 `deny` 访问。

## 冲突对象 {#id10}

应用必须为所有对象分配不冲突的唯一键。 这包括避免创建名称与其父对象或同级对象发生冲突的对象。 在发生冲突的位置，MinIO 对 LIST 操作返回空结果集。

例如，以下操作会创建命名空间冲突

```text
PUT data/invoices/2024/january/vendors.csv
PUT data/invoices/2024/january <- collides with existing object prefix
```

```text
PUT data/invoices/2024/january
PUT data/invoices/2024/january/vendors.csv <- collides with existing object
```

虽然仍然可以对这些对象执行 GET 或 HEAD 操作，但名称冲突会导致在 `/invoices/2024/january` 路径上的 LIST 操作返回空结果集。