---
title: "术语表"

weight: 999
type: docs
icon: fa-solid fa-book-open
---

<a id="id1"></a>

<a id="term-access-keys"></a>

**access keys**

<a id="term-0"></a>

**访问密钥**

> MinIO 部署或租户中的一种受限用户账户，通常用于 API 调用。 访问密钥过去称为 “Service Account（服务账户）”。

<a id="term-active-active"></a>

**active-active**

<a id="term-1"></a>

**双活**

> 一种 [replication](#term-replication) 方式，提供数据的双向镜像。 在 active-active 配置中，修改任一存储位置中的数据，也会同步修改其他存储位置中的数据。
>
> 另请参见：[active-passive](#term-active-passive)。

<a id="term-active-passive"></a>

**active-passive**

<a id="term-2"></a>

**主备**

> 一种 [replication](#term-replication) 方式，提供数据的单向镜像。 在 active-passive 配置中，修改源位置的数据也会同步修改目标位置的数据。 但对目标位置数据的更改不会影响源位置的数据。
>
> 另请参见：[active-active](#term-active-active)。

<a id="term-alias"></a>

**alias**

<a id="term-3"></a>

**别名**

> 本地定义的 MinIO 部署引用，用于大多数命令行接口操作。 参见 [`mc alias set`](/zh/reference/minio-mc/mc-alias-set/#command-mc.alias.set)。

<a id="term-audit-logs"></a>

**audit logs**

<a id="term-4"></a>

**审计日志**

> 对 MinIO 部署中每项操作的细粒度记录。 [Audit logs](/zh/operations/monitoring/minio-logging/#minio-logging) 有助于满足要求对操作进行详细跟踪的安全标准和法规。
>
> 另请参见：[server logs](#term-server-logs)。

<a id="term-bit-rot"></a>

**bit rot**

<a id="term-5"></a>

**位腐坏**

> 在用户不知情的情况下发生的数据损坏。
>
> MinIO 通过 [hashing](#term-hashing) 和 [erasure coding](#term-erasure-coding) 来应对 bit rot。

<a id="term-bit-rot-healing"></a>

**bit rot healing**

<a id="term-6"></a>

**位腐坏自愈**

> 因 bit rot 而损坏的对象会在任何 `GET` 或 `HEAD` 操作期间自动 [healed](#term-healing)。 MinIO 借助其 [hashing](#term-hashing) 实现，在访问过程中实时检测并修复损坏对象。

<a id="term-bucket"></a>

**bucket**

<a id="term-buckets"></a>

**buckets**

<a id="term-7"></a>

**存储桶**

> [objects](#term-objects) 及相关配置的逻辑分组。

<a id="term-cluster"></a>

**cluster**

<a id="term-8"></a>

**集群**

> 由一组磁盘以及一个或多个 `minio server` 进程组成，并汇聚为单一存储资源的集合。
>
> 另请参见：[tenant](#term-tenant)。

<a id="term-cluster-registration"></a>

**cluster registration**

<a id="term-9"></a>

**集群注册**

> 集群注册会将 MinIO 部署关联到 [SUBNET](#term-SUBNET) [subscription](https://min.io/pricing?jmp=docs)。 一个组织可以将多个 MinIO 集群注册到同一个 SUBNET 订阅。

<a id="term-Console"></a>

**Console**

<a id="term-MinIO-Console"></a>

**MinIO Console**

<a id="term-MinIO"></a>

**MinIO 控制台**

> 用于与 MinIO 部署或 [tenant](#term-tenant) 交互的图形用户界面 (GUI)。

<a id="term-data"></a>

**data**

<a id="term-10"></a>

**数据块**

> MinIO 在执行 [erasure coding](#term-erasure-coding) 时写入的两类块之一。 数据块包含对象内容。
>
> 当数据块损坏或丢失时，[parity](#term-parity) 块可用于重建数据。

<a id="term-decommission"></a>

**decommission**

<a id="term-11"></a>

**下线**

> 从 [distributed](#term-distributed) 部署中移除一个磁盘池的过程。 启动后，待下线池中的对象会迁移到该部署中的其他池，从而完成排空。
>
> 该过程不可逆。

<a id="term-deployment"></a>

**deployment**

<a id="term-12"></a>

**部署**

> 一个具体的 MinIO 实例，包含一组 [buckets](#term-buckets) 和 [objects](#term-objects)。

<a id="term-disk-encryption"></a>

**disk encryption**

<a id="term-13"></a>

**磁盘加密**

> 将写入磁盘的全部内容转换为未经授权实体难以解读的值。 磁盘加密可与其他加密技术结合使用，以构建稳健的数据安全体系。

<a id="term-enclave"></a>

**enclave**

<a id="term-14"></a>

**隔离域**

> 对有状态 Key Encryption Service (KES) 服务器中隔离区域的称谓。 一个 KES 服务器可以包含一个或多个隔离域。 KES 服务器中的每个隔离域都持有独立的密钥、策略和管理身份。 任一隔离域都无法查看或使用服务器上的其他隔离域。
>
> 例如，你可以使用多个隔离域，在单个有状态 KES 服务器中为多个 MinIO 租户保存彼此完全隔离的密钥库。

<a id="term-encryption-at-rest"></a>

**encryption at rest**

<a id="term-15"></a>

**静态加密**

> 一种以加密状态存储对象的加密方式。 对象在未从一个位置移动到另一个位置时始终保持加密状态。
>
> 服务器可使用以下密钥管理方式之一对对象进行加密： [SSE-KMS](#term-SSE-KMS)、[SSE-S3](#term-SSE-S3) 或 [SSE-C](#term-SSE-C)。

<a id="term-encryption-in-transit"></a>

**encryption in transit**

<a id="term-16"></a>

**传输加密**

> 一种在对象从一个位置传输到另一个位置时保护对象的加密方式，例如在 GET 请求期间。 对象在源端或目标存储设备上可以是加密状态，也可以不是。

<a id="term-erasure-coding"></a>

**erasure coding**

<a id="term-17"></a>

**纠删码**

> 一种将 [objects](#term-objects) 拆分为多个分片，并将这些分片写入多个独立磁盘的技术。
>
> 根据所使用的 [topology](#term-topology)，纠删码允许 MinIO 部署在丢失部分磁盘或节点的情况下仍保留读写能力。

<a id="term-erasure-set"></a>

**erasure set**

<a id="term-18"></a>

**纠删码集合**

> MinIO 中支持 [erasure coding](#term-erasure-coding) 的一组磁盘。 MinIO 会将部署中服务器池的磁盘划分为若干组，每组包含 4 到 16 个磁盘，每组构成一个纠删码集合。 写入对象时，[data](#term-data) 和 [parity](#term-parity) 块会随机写入该纠删码集合中的各个磁盘。

<a id="term-hashing"></a>

**hashing**

<a id="term-19"></a>

**哈希**

> 使用算法生成唯一且定长的字符串值来标识一段数据。

<a id="term-healing"></a>

**healing**

<a id="term-20"></a>

**自愈**

> 从 bit rot、磁盘故障或站点故障导致的部分数据丢失中恢复数据的过程。

<a id="term-health-diagnostics"></a>

**health diagnostics**

<a id="term-21"></a>

**健康诊断**

> 一组 MinIO [API endpoints](/zh/operations/monitoring/healthcheck-probe/#minio-healthcheck-api)，用于检查服务器是否：
>
> - 在线
> - 可用于写入数据
> - 可用于读取数据
> - 可在不影响集群读写操作的情况下进入维护状态

<a id="term-host-bus-adapter"></a>

**host bus adapter**

<a id="term-HBA"></a>

**HBA**

<a id="term-22"></a>

**主机总线适配器**

> 连接主机系统与存储设备的电路板或集成电路适配器。 <abbr title="host bus adapter">HBA</abbr> 负责执行相关处理，以减轻主机系统处理器的负载。

<a id="term-IAM-integration"></a>

**IAM integration**

<a id="term-IAM"></a>

**IAM 集成**

> MinIO 仅允许经过身份验证的用户访问数据。 MinIO 提供内置的身份管理方案来创建授权凭据。 此外，MinIO 用户还可以选择使用来自第三方身份提供者 (IDP) 的凭据进行身份验证，包括 OpenID 或 LDAP 提供者。

<a id="term-JBOD"></a>

**JBOD**

<a id="term-23"></a>

**直通磁盘组**

> “Just A Bunch of Drives”的首字母缩写。 JBOD 是一种可容纳多个硬盘的存储设备机箱。 这些磁盘可以组合成一个逻辑存储单元。
>
> 另请参见：[RAID](#term-RAID)

<a id="term-lifecycle-management"></a>

**lifecycle management**

<a id="term-ILM"></a>

**ILM**

<a id="term-24"></a>

**生命周期管理**

> 用于确定 [objects](#term-objects) 何时迁移或过期的一组规则。

<a id="term-locking"></a>

**locking**

<a id="term-25"></a>

**锁定**

> 一种规则，用于防止对象在授权代理移除该规则或规则到期之前被移除或删除。

<a id="term-monitoring"></a>

**monitoring**

<a id="term-26"></a>

**监控**

> 对 MinIO 集群、部署、租户或服务器的状态、活动和可用性进行审查的行为。 MinIO 提供以下工具：
>
> - 与 [Prometheus](https://prometheus.io/) 兼容的指标与告警
> - [Audit logs](#term-audit-logs)
> - [server logs](#term-server-logs)
> - [Healthcheck API endpoints](/zh/operations/monitoring/healthcheck-probe/#minio-healthcheck-api)
> - [Bucket notifications](/zh/administration/monitoring/bucket-notifications/#minio-bucket-notifications)

<a id="term-multi-node-multi-drive"></a>

**multi-node multi-drive**

<a id="term-MNMD"></a>

**MNMD**

<a id="term-27"></a>

**多机多盘**

<a id="term-distributed"></a>

**distributed**

<a id="term-28"></a>

**分布式**

> 一种系统 [topology](#term-topology)，使用多台服务器且每台服务器配备多个磁盘来承载 MinIO 实例。 对于分布式部署，MinIO 建议使用 Kubernetes。

<a id="term-multipart-upload"></a>

**multipart upload**

<a id="term-29"></a>

**分段上传**

> 分段上传是一种由客户端发起的 [S3 功能](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)，它会将单个对象拆分为多个分片，以便从一个位置传输到另一个位置。 客户端将每个分片独立上传到 MinIO，而 MinIO 负责将这些已接收的分片重建为原始对象。
>
> 分段上传的优势包括更高的吞吐量以及更强的网络错误恢复能力。 对于实际或预估大小超过 100MB 的对象，通常使用分段上传能获得最佳效果。
>
> 更多细节参见 [AWS 文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)。

<a id="term-network-encryption"></a>

**network encryption**

<a id="term-30"></a>

**网络加密**

> 一种在数据从一个位置传输到另一个位置时保护数据的方式，例如服务端到服务端或客户端到服务端之间的传输。 MinIO 对入站和出站流量均支持 [Transport Layer Security (TLS)](/zh/operations/network-encryption/#minio-tls) 1.2 及更高版本。

<a id="term-object"></a>

**object**

<a id="term-objects"></a>

**objects**

<a id="term-31"></a>

**对象**

> MinIO 通过兼容 S3 的 API 交互的数据项。 对象可以分组到 [buckets](#term-buckets) 中。

<a id="term-Operator"></a>

**Operator**

<a id="term-Operator-Console"></a>

**Operator Console**

<a id="term-32"></a>

**Operator 控制台**

> 用于在分布式部署环境中部署和管理 MinIO [tenants](#term-tenants) 的图形用户界面 (GUI)。

<a id="term-parity"></a>

**parity**

<a id="term-33"></a>

**校验块**

> MinIO 为对象写入的块中，用于在数据块缺失或损坏时支持数据重建的部分。 校验块的数量决定了部署在仍保持读写能力的前提下，可丢失的 [erasure set](#term-erasure-set) 磁盘数量。

<a id="term-prefix"></a>

**prefix**

<a id="term-34"></a>

**前缀**

> 前缀通过为应共享相似层级或结构的对象分配相同字符串，来组织 [bucket](#term-bucket) 中的 [objects](#term-objects)。 使用定界字符（通常为 */*）可以增加层级。 虽然带有前缀的对象在某些文件系统中可能看起来像目录结构，但前缀并不是目录。
>
> MinIO 本身不会限制某个特定前缀可包含的对象数量。 但对于较大的前缀，硬件和网络条件可能会带来性能影响。
>
> - 对于硬件配置一般或预算导向的部署，应将每个前缀约 10,000 个对象作为工作负载设计的基线。 然后根据真实工作负载的基准测试和监控结果，在硬件可有效承载的范围内逐步提高这一目标。
> - 对于高性能或企业级 [hardware](/zh/operations/checklists/hardware/#deploy-minio-distributed-recommendations)，通常可以处理包含数百万个甚至更多对象的前缀。
>
> [MinIO SUBNET](https://min.io/pricing?jmp=docs) 企业版账户可将年度架构评审纳入部署和维护策略，以确保依赖 MinIO 的项目获得长期性能与成功。

<a id="term-RAID"></a>

**RAID**

<a id="term-35"></a>

**磁盘阵列**

> “Redundant Array of Independent Disks”的首字母缩写。 该技术将多个独立物理磁盘合并为一个存储单元或阵列。 某些 RAID 级别通过在物理磁盘之间复制、条带化或镜像数据来提供数据冗余或容错能力。
>
> 另请参见：[JBOD](#term-JBOD)。

<a id="term-read-quorum"></a>

**read quorum**

<a id="term-36"></a>

**读仲裁**

> 执行读操作时，重建完整对象所需的最少对象分片数量。 更多信息参见 [纠删码基础](/zh/operations/concepts/erasure-coding/#minio-ec-basics)。

<a id="term-replication"></a>

**replication**

<a id="term-mirror"></a>

**mirror**

<a id="term-37"></a>

**复制**

<a id="term-38"></a>

**镜像复制**

> 将 [bucket](/zh/administration/bucket-replication/#minio-bucket-replication) 或整个 [site](/zh/operations/replication/multi-site-replication/#minio-site-replication-overview) 复制到另一位置的行为。

<a id="term-scanner"></a>

**scanner**

<a id="term-MinIO-Scanner"></a>

**MinIO Scanner**

<a id="term-39"></a>

**扫描器**

> MinIO 运行的若干低优先级进程之一，用于检查：
>
> - 需要执行对象迁移的生命周期管理规则
> - 存储桶或站点复制状态
> - 对象 [bit rot](#term-bit-rot) 和 [healing](#term-healing)
> - 使用量数据
>
> 更多信息参见 [对象扫描器](/zh/operations/concepts/scanner/#minio-concepts-scanner)。

<a id="term-self-signed-certificates"></a>

**self signed certificates**

<a id="term-40"></a>

**自签名证书**

> 自签名证书是由负责证书所保护内容的公司或开发者自行创建、签发并签名的证书。 自签名证书并非由公开受信任的第三方证书颁发机构 (CA) 签发或签名。 这类证书不会过期，无需定期审查，也无法被吊销。

<a id="term-server-logs"></a>

**server logs**

<a id="term-41"></a>

**服务器日志**

> 记录到系统控制台的 `minio server` 操作日志。 [Server logs](/zh/operations/monitoring/minio-logging/#minio-logging) 支持常规监控和故障排查。
>
> 更详细的日志信息参见 [audit logs](#term-audit-logs)。

<a id="term-service-account"></a>

**service account**

<a id="term-44"></a>

**服务账户**

> 该术语已更名为 [access keys](#term-access-keys)。 MinIO 部署或租户中的一种受限用户账户，通常用于 API 调用。

<a id="term-shard"></a>

**shard**

<a id="term-shards"></a>

**shards**

<a id="term-45"></a>

**分片**

> 对象经过 MinIO [erasure coded](#term-erasure-coding) 后形成的一部分。 每个分片都表示数据块或校验块，供 MinIO 在读请求时用于重建对象。
>
> > [!NOTE]
> > **磁盘独占访问**
> >
> > MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
> >
> > 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。
>
> 更详细的信息参见 [纠删码](/zh/operations/concepts/erasure-coding/#minio-erasure-coding)。

<a id="term-single-node-multi-drive"></a>

**single-node multi-drive**

<a id="term-SNMD"></a>

**SNMD**

<a id="term-46"></a>

**单机多盘**

> 一种系统 [topology](#term-topology)，在单个计算资源上使用多个挂载磁盘部署 MinIO。

<a id="term-single-node-single-drive"></a>

**single-node single-drive**

<a id="term-SNSD"></a>

**SNSD**

<a id="term-47"></a>

**单机单盘**

<a id="term-filesystem"></a>

**filesystem**

<a id="term-48"></a>

**文件系统模式**

> 一种系统 [topology](#term-topology)，在单个计算资源上使用单个磁盘部署 MinIO。 这为原本标准的文件系统增加了 S3 类型的功能。

<a id="term-SSE-C"></a>

**SSE-C**

> 一种 [encryption at rest](#term-encryption-at-rest) 方式，在写入对象时使用随写请求提供的加密密钥对对象进行加密。 读取对象时，必须提供与最初写入该对象时相同的加密密钥。 此外，还必须自行管理所使用的加密密钥。
>
> 另请参见：[SSE-KMS](#term-SSE-KMS)、[SSE-S3](#term-SSE-S3)、[encryption at rest](#term-encryption-at-rest)、[network encryption](#term-network-encryption)。

<a id="term-SSE-KMS"></a>

**SSE-KMS**

> 一种 [encryption at rest](#term-encryption-at-rest) 方式，在写入时使用由服务提供方管理的独立密钥对每个对象进行加密。 可以使用存储桶级（默认）或对象级密钥。 对于加密密钥管理，MinIO 推荐使用 SSE-KMS。
>
> 另请参见：[SSE-S3](#term-SSE-S3)、[SSE-C](#term-SSE-C)、[encryption at rest](#term-encryption-at-rest)、[network encryption](#term-network-encryption)。

<a id="term-SSE-S3"></a>

**SSE-S3**

> 一种 [encryption at rest](#term-encryption-at-rest) 方式，在写入时使用一个单一密钥为部署中的所有对象进行加密。 一个部署使用同一个外部密钥来解密该部署中的任意对象。
>
> 另请参见：[SSE-KMS](#term-SSE-KMS)、[SSE-C](#term-SSE-C)、[encryption at rest](#term-encryption-at-rest)、[network encryption](#term-network-encryption)。

<a id="term-standalone-deployment"></a>

**standalone deployment**

<a id="term-49"></a>

**独立部署**

> 一个 [single-node single-drive](#term-single-node-single-drive) (SNSD) MinIO 部署。 该术语此前用于指代已弃用的 [Gateway or Filesystem Mode](/zh/operations/deployments/baremetal-migrate-fs-gateway/#minio-gateway-migration) 部署类型。

<a id="term-SUBNET"></a>

**SUBNET**

> [MinIO Subscription Network](https://min.io/pricing?jmp=docs) 用于跟踪支持工单，并为订阅账户提供 24 小时直连工程师支持。

<a id="term-tenant"></a>

**tenant**

<a id="term-tenants"></a>

**tenants**

<a id="term-50"></a>

**租户**

> 在 [distributed](#term-distributed) 模式下，指某个具体的 MinIO 部署。 一个 MinIO Operator 实例可以拥有多个租户。

<a id="term-topology"></a>

**topology**

<a id="term-51"></a>

**拓扑**

> 部署使用的硬件配置。 MinIO 支持三种拓扑：
>
> - [multi-node multi-drive](#term-multi-node-multi-drive)
> - [single-node multi-drive](#term-single-node-multi-drive)
> - [single-node single-drive](#term-single-node-single-drive)

<a id="term-versioning"></a>

**versioning**

<a id="term-52"></a>

**版本控制**

> 在 [object](#term-object) 随时间变化的过程中保留其多个迭代版本。

<a id="term-webhook"></a>

**webhook**

<a id="term-Webhook"></a>

**Webhook 回调**

> [webhook](/zh/administration/monitoring/publish-events-to-webhook/#minio-bucket-notifications-publish-webhook) 是一种通过自定义回调改变网页或 Web 应用行为的方法。 其格式通常为通过 HTTP POST 请求发送的 <abbr title="JavaScript Object Notation">JSON</abbr>。

<a id="term-WORM"></a>

**WORM**

<a id="term-54"></a>

**一次写入多次读取**

> Write Once Read Many (WORM) 是一种数据保留方法，也是对象锁定机制的一部分。 许多请求都可以检索并查看启用 WORM 锁定的对象（`read many`），但任何写请求都不能更改该对象（`write once`）。

<a id="term-write-quorum"></a>

**write quorum**

<a id="term-53"></a>

**写仲裁**

> 执行写操作时，MinIO 必须成功写入到 [erasure set](/zh/operations/concepts/erasure-coding/#minio-ec-erasure-set) 的最少对象分片数量。 更多信息参见 [纠删码基础](/zh/operations/concepts/erasure-coding/#minio-ec-basics)。

<a id="term-42"></a>

**服务器池**

<a id="term-pool"></a>

**pool**

<a id="term-43"></a>

**服务器池**

> 一组 `minio server` 节点，它们组合各自的磁盘和资源，以支持对象存储与检索请求。
>
> 更多信息参见 [MinIO 如何管理多个虚拟或物理服务器？](/zh/operations/concepts/#minio-intro-server-pool)。