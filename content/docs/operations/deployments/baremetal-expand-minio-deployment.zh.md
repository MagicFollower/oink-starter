---
title: "扩展分布式 Silo 部署"

weight: 30
math: true
---

<a id="minio"></a>
<a id="expand-minio-distributed"></a>

Silo 支持通过添加新的[服务器池](/docs/operations/concepts/#minio-intro-server-pool)扩展现有分布式部署。每个 pool 都会增加集群的总可用存储容量。

扩容并不能提供 Business Continuity/Disaster Recovery (BC/DR) 级别的保护。 虽然每个 pool 都是一组相互独立的服务器，并通过各自的 [纠删码集合](/docs/operations/concepts/erasure-coding/#minio-ec-erasure-set) 提供可用性，但只要其中一个 pool 完全丢失，MinIO 就会停止该部署中所有 pool 的 I/O。 同样地，只要某个 pool 中的某个纠删码集合失去 quorum，该集合中存储的对象就会发生数据丢失，而不受其他纠删码集合或 pool 数量的影响。

新的 服务器池 **不必** 与现有任一 服务器池 使用相同类型或规格的硬件和软件配置，不过保持一致通常有助于简化集群管理，并让各 pool 间的性能表现更可预测。 新 pool 内的所有驱动器 **应当** 保持相同类型和容量。 有关如何选择合适配置的完整建议，请参阅 MinIO 的 [硬件建议](/docs/operations/checklists/hardware/#minio-hardware-checklist)。

若要为单 pool 或多 pool 的 MinIO 部署提供 BC/DR 级别的故障切换与恢复支持，请使用 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview)。

本页步骤用于为现有 [分布式](/docs/operations/deployments/installation/#deploy-minio-distributed) MinIO 部署增加一个额外的 服务器池。

> [!WARNING]
> **重要**
>
> MinIO 不支持扩展 单机单盘 拓扑。

<a id="id2"></a>

## 前提条件 {#expand-minio-distributed-prereqs}

### 网络与防火墙 {#id3}

部署中的每个节点都应当与其他所有节点具备完整的双向网络访问能力。 对于容器化或编排式基础设施，这可能需要针对 Ingress、负载均衡器等网络和路由组件进行专门配置。 某些操作系统还可能需要设置防火墙规则。 例如，以下命令会在使用 `firewalld` 的服务器上显式开放 MinIO server 默认 API 端口 `9000`：

```shell
firewall-cmd --permanent --zone=public --add-port=9000/tcp
firewall-cmd --reload
```

部署中的所有 MinIO server *必须* 使用相同的监听端口。

如果你为 [MinIO Console](/docs/administration/minio-console/#minio-console) 设置了静态端口（例如 `:9001`）， 则还必须允许外部客户端访问该端口，以确保连接可用。

MinIO **强烈建议** 使用负载均衡器管理到集群的连接。 由于部署中的任意 MinIO 节点都可以接收、转发或处理客户端请求，因此负载均衡器应采用 “Least Connections” 算法将请求路由到 MinIO 部署。

以下负载均衡器已知可与 MinIO 良好配合：

- [NGINX](https://www.nginx.com/products/nginx/load-balancing/)
- [HAProxy](https://cbonte.github.io/haproxy-dconv/2.3/intro.html#3.3.5)

如何配置防火墙或负载均衡器以支持 MinIO 不在本步骤范围内。 [为 MinIO Server 配置 NGINX 代理](/docs/integrations/setup-nginx-proxy-with-minio/#integrations-nginx-proxy) 参考页提供了一个将 NGINX 作为反向代理并启用基础负载均衡的基线配置。

### 连续主机名 {#id4}

MinIO 在创建 服务器池 时，*要求* 使用扩展表示法 `{x...y}` 来表示一组连续的 MinIO 主机。 因此，MinIO *要求* 使用连续编号的主机名来表示 pool 中的每个 [`minio server`](/docs/reference/minio-server/#command-minio.server) 进程。

在开始本步骤之前，请先创建所需的 DNS 主机名映射。 例如，以下主机名可用于一个 4 节点分布式 服务器池：

- `minio5.example.com`
- `minio6.example.com`
- `minio7.example.com`
- `minio8.example.com`

你可以使用扩展表示法 `minio{5...8}.example.com` 来指定完整的主机名范围。

如何配置 DNS 以支持 MinIO 不在本步骤范围内。

### 存储要求 {#id5}

以下要求概括了 MinIO 硬件建议中的 [存储](/docs/operations/checklists/hardware/#minio-hardware-checklist-storage) 一节：

**使用本地存储**

> 直连存储（DAS）相比网络存储 （<abbr title="Network Attached Storage">NAS</abbr>、<abbr title="Storage Area Network">SAN</abbr>、 <abbr title="Network File Storage">NFS</abbr>）在性能和一致性方面具有显著优势。 对于主数据或“热”数据，MinIO 强烈建议使用闪存存储（NVMe、SSD）。

**磁盘使用 XFS 格式**

> MinIO 强烈建议为存储配置使用 XFS 格式化的磁盘。 MinIO 在内部测试和验证套件中使用 XFS，因此对其在各种规模下的性能和行为更有信心。
>
> 对于 EXT4、BTRFS 或 ZFS 等其他文件系统，MinIO **既不** 测试，也不推荐。

**使用一致的磁盘类型**

> MinIO 不区分磁盘类型，也无法从混合存储类型中获益。 每个 [pool](/zh/glossary/#term-pool) 都必须使用相同类型的磁盘（NVMe、SSD）
>
> 例如，部署一个仅由 NVMe 磁盘组成的 pool。 如果你在其中混用 SSD 或 HDD，MinIO 会将这些磁盘与 NVMe 磁盘一视同仁。 这可能导致性能问题，因为某些磁盘的读写特性不同或更差，无法以与 NVMe 磁盘相同 的速率响应。

**使用一致的磁盘容量**

> MinIO 会将每块磁盘的可用容量限制为 pool 中最小磁盘的容量。
>
> 例如，部署一个由相同数量、容量均为 `7.68TiB` 的 NVMe 磁盘组成的 pool。 如果其中有一块磁盘容量为 `3.84TiB`，MinIO 会将 pool 中所有磁盘都视为只有 该较小容量。

**配置顺序编号的磁盘挂载**

> MinIO 在创建新的 服务器池 时使用 Go 扩展表示法 `{x...y}` 表示顺序连续的 磁盘序列，其中 服务器池 中所有节点都挂载了完全相同的一组磁盘。 最好将磁盘挂载路径也配置成顺序序列，以便支持这种表示法。 例如，可按 `/mnt/drive-n` 的模式挂载磁盘，其中 `n` 从 `1` 开始，并随每块 磁盘按 `1` 递增。

**在重启后保持磁盘挂载与映射一致**

> 使用 `/etc/fstab` 确保节点重启前后磁盘到挂载点的映射保持一致。
>
> 非 Linux 操作系统应使用等效的磁盘挂载管理工具。

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

### 满足纠删码校验的最小驱动器数量 {#id6}

MinIO 要求每个 pool 都满足部署的 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 设置。 具体来说，新 pool 的拓扑必须为每个 [纠删码集合](/docs/operations/concepts/erasure-coding/#minio-ec-erasure-set) 提供至少 `2 x EC:N` 个驱动器，其中 `EC:N` 是该部署的 [Standard](/docs/reference/minio-server/settings/storage-class/#minio-ec-storage-class) 校验存储类。 这一要求可确保新的 服务器池 满足该部署预期的 <abbr title="Service Level Agreement">SLA</abbr>。

你可以使用 [MinIO Erasure Code Calculator](https://min.io/product/erasure-code-calculator?ref=docs) 检查新 pool 的 **Erasure Code Stripe Size (K+M)**。 如果列出的最大值至少为 `2 x EC:N`，则该 pool 支持部署当前的纠删码校验设置。

### 时间同步 {#id7}

多节点系统必须保持时间和日期同步，才能维持稳定的节点间操作与交互。 请确保所有节点都定期同步到同一时间服务器。 不同操作系统可采用不同方式同步时间和日期，例如 `ntp`、`timedatectl` 或 `timesyncd`。

请查阅所用操作系统的文档，了解如何在各节点之间建立并维护准确且一致的系统时钟。

### 先备份集群设置 {#id8}

在开始扩容前，使用 [`mc admin cluster bucket export`](/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export) 和 [`mc admin cluster iam export`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export) 命令分别为存储桶元数据和 IAM 配置创建快照。 必要时，你可以使用这些快照恢复 [存储桶](/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-import/#minio-mc-admin-cluster-bucket-import) 和 [IAM](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-import/#minio-mc-admin-cluster-iam-import) 设置，以从用户错误或流程错误中恢复。

## 注意事项 {#id9}

<a id="id10"></a>

### 写入文件 {#minio-writing-files}

MinIO 不会自动在新的 服务器池 之间重新平衡对象。 相反，MinIO 会根据某个 pool 的空闲空间占所有可用 pool 总空闲空间的比例，将新的写入操作分配到空闲空间最多的 pool。

用于计算某个 pool 被选中执行写操作概率的公式如下：

\(FreeSpaceOnPoolA / FreeSpaceOnAllPools\)

假设有一个由三个 pool 组成的部署，总空闲空间为 10 TiB，分布如下：

- Pool A 有 3 TiB 空闲空间
- Pool B 有 2 TiB 空闲空间
- Pool C 有 5 TiB 空闲空间

MinIO 计算各 pool 被用于写入操作的概率如下：

- Pool A：30% (\(3TiB / 10TiB\))
- Pool B：20% (\(2TiB / 10TiB\))
- Pool C：50% (\(5TiB / 10TiB\))

除空闲空间计算外，如果某次写入（含校验）会导致驱动器使用率超过 99%，或已知剩余 inode 数量低于 1000，MinIO 也不会写入该 pool。

如有需要，你可以使用 [`mc admin rebalance`](/docs/reference/minio-mc-admin/mc-admin-rebalance/#command-mc.admin.rebalance) 手动启动重平衡过程。 有关重平衡工作方式的更多信息，请参阅 [跨部署管理对象](/docs/operations/concepts/#minio-rebalance)。

同样地，MinIO 不会向正在退役中的 pool 执行写入。

### 扩容是无中断的 {#id11}

新增 服务器池 需要在大致同一时间重启部署中的 *所有* MinIO server 进程。

MinIO 强烈建议同时重启一个部署中的所有 MinIO 服务端进程。 MinIO 操作具有原子性并保持严格一致。 因此，该重启过程不会中断应用或正在进行的操作。

**不要** 执行“滚动”重启（例如一次只重启一个节点）。

### 基于容量的规划 {#id12}

MinIO 建议预先规划足以存放 **至少** 2 年数据的存储容量，并在使用率达到 70% 之前完成准备。 如果过于频繁地执行 [服务器池 扩容](#expand-minio-distributed)，或按“just-in-time”方式扩容，通常意味着架构或规划存在问题。

例如，假设某套应用每年预计至少产生 100 TiB 数据，并计划在 3 年后再扩容。 初始 服务器池 为该部署提供了约 500 TiB 的可用存储，使集群能够在安全满足 70% 阈值的同时，为数据增长保留一定缓冲。 理想情况下，新 服务器池 **至少** 也应提供 500 TiB 的额外存储，以便在下次扩容前维持类似的生命周期。

由于 MinIO [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 需要预留部分存储用于校验，因此总 **原始** 存储容量必须高于计划中的 **可用** 容量。 建议使用 MinIO [纠删码计算器](https://min.io/product/erasure-code-calculator)，围绕具体纠删码设置进行容量规划。

### 推荐的操作系统 {#id13}

本教程默认所有运行 MinIO 的主机都使用 [推荐的 Linux 操作系统](/docs/operations/deployments/baremetal/#minio-installation-platform-support)。

部署中的所有主机都应采用一致的 [软件配置](/docs/operations/checklists/software/#minio-software-checklists)。

<a id="id14"></a>

## 扩展分布式 MinIO 部署 {#expand-minio-distributed-baremetal}

以下步骤将向现有 MinIO 部署中添加一个 [服务器池](/docs/operations/concepts/#minio-intro-server-pool)。 每个 Pool 都会在保持集群整体 [可用性](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 的同时，扩展集群的总可用存储容量。

以下所有命令都使用示例值。 请将这些值替换为适用于你部署的实际值。

开始本步骤前，请先阅读 [前提条件](#expand-minio-distributed-prereqs)。

在 [退役旧硬件 pool](/docs/operations/deployments/baremetal-decommission-server-pool/#minio-decommissioning) 之前，请先完成所有计划中的硬件扩容。

### 1) 在新服务器池的每个节点上安装 Silo 二进制 {#id15}

安装与现有 pool **完全相同的公开 Silo 版本**。从[下载与安装](/zh/download/#server)获取 x86-64 或 ARM64 的 RPM、DEB 或独立归档，并在安装前校验摘要。当前 Silo 发布只提供这两种 Linux 架构，因此已删除继承文档中指向未发布 `ppc64le` 与 `s390x` 制品的说明。

{{< tabs group="rpmrhel-debdebianubuntu-tab3" >}}
{{< tab label="RPM（RHEL 系）" value="rpmrhel" >}}
```shell
sudo dnf install ./minio-*.rpm
```
{{< /tab >}}
{{< tab label="DEB（Debian/Ubuntu）" value="debdebianubuntu" >}}
```shell
sudo dpkg -i ./minio_*_amd64.deb
```

ARM64 主机请使用名称中带 `arm64` 的软件包。
{{< /tab >}}
{{< tab label="独立归档" value="tab3" >}}
```shell
tar -xzf minio_*_linux_*.tar.gz
sudo install -m 0755 ./minio /usr/local/bin/minio
minio --version
```
{{< /tab >}}
{{< /tabs >}}

在每个新节点运行 `minio --version` 并与现有 pool 比对；不要把版本不同的节点加入集群。需要升级时，请遵循[`systemctl` 管理的 Silo 升级流程](/docs/operations/deployments/baremetal-upgrade-minio-deployment/#minio-upgrade-systemctl)。

### 2) 添加 TLS/SSL 证书 {#tls-ssl}

当 MinIO 检测到 `${HOME}/.minio/certs` 目录中存在有效的 x.509 证书 （`.crt`）和私钥（`.key`）时，会自动启用 [传输层安全（TLS）](/docs/operations/network-encryption/#minio-tls) 1.2+。

对于由 `systemd` 管理的部署，请使用运行 MinIO server 进程的用户对应的 `$HOME` 目录。提供的 `minio.service` 文件会以 `minio-user` 身份运行 该进程。前一步已经包含了如何创建该用户及其主目录 `/home/minio-user` 的说明。

- 在每个主机上将 TLS 证书放置到 `/home/minio-user/.minio/certs` 中。
- 如果 *任何* MinIO server 或客户端使用了由未知证书颁发机构签名的证书 （自签或内部 CA），你 *必须* 将 CA 证书放到该部署中所有 MinIO 主机的 `/home/minio-user/.minio/certs/CAs` 下。MinIO 会拒绝无效证书 （不受信任、已过期或格式错误）。

如果 `minio.service` 文件指定了其他用户账户，请改用该账户对应的 `$HOME` 目录。或者，也可以通过 [`minio server --certs-dir`](/docs/reference/minio-server/#minio.server.-certs-dir) 命令行参数指定 自定义证书目录。修改 `/etc/default/minio` 中的 `MINIO_OPTS` 变量即可设置 此选项。运行 MinIO server 进程的 `systemd` 用户 *必须* 对指定目录具有读取和 列目录权限。

有关为 MinIO 配置 TLS 的更具体指导，包括通过 Server Name Indication (SNI) 支持多域名，请参见 [网络加密（TLS）](/docs/operations/network-encryption/#minio-tls)。你也可以跳过这一步，以不启用 TLS 的方式 部署。除了早期开发阶段以外，MinIO 强烈 *不建议* 使用非 TLS 部署。

### 3) 创建 `systemd` 服务文件 {#systemd}

`.deb` 或 `.rpm` 软件包会将以下 [systemd](https://www.freedesktop.org/wiki/Software/systemd/) 服务文件 安装到 `/usr/lib/systemd/system/minio.service`。 对于二进制安装方式，请在所有 MinIO 主机上手动创建该文件。

> [!NOTE]
> **说明**
>
> `systemd` 会先检查 `/etc/systemd/...` 路径，再检查 `/usr/lib/systemd/...` 路径， 并使用它找到的第一个文件。 为避免配置冲突或意外选项，请确认该文件仅存在于 `/usr/lib/systemd/system/minio.service` 路径下。
>
> 关于文件路径搜索顺序的详细信息，请参阅 [systemd.unit 的 man page](https://www.man7.org/linux/man-pages/man5/systemd.unit.5.html)。

```shell
[Unit]
Description=MinIO
Documentation=https://silo.pgsty.com/docs/
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
Type=notify

WorkingDirectory=/usr/local

User=minio-user
Group=minio-user
ProtectProc=invisible

EnvironmentFile=-/etc/default/minio
ExecStart=/usr/local/bin/minio server $MINIO_OPTS $MINIO_VOLUMES

# Let systemd restart this service always
Restart=always

# Specifies the maximum file descriptor number that can be opened by this process
LimitNOFILE=1048576

# Turn-off memory accounting by systemd, which is buggy.
MemoryAccounting=no

# Specifies the maximum number of threads this process can create
TasksMax=infinity

# Disable timeout logic and wait until process is stopped
TimeoutSec=infinity

# Disable killing of MinIO by the kernel's OOM killer
OOMScoreAdjust=-1000

SendSIGKILL=no

[Install]
WantedBy=multi-user.target

# Built for ${project.name}-${project.version} (${project.name})
```

The `minio.service` file runs as the `minio-user` User and Group by default. You can create the user and group using the `groupadd` and `useradd` commands. The following example creates the user, group, and sets permissions to access the folder paths intended for use by MinIO. These commands typically require root (`sudo`) permissions.

```shell
groupadd -r minio-user
useradd -M -r -g minio-user minio-user
chown minio-user:minio-user /mnt/disk1 /mnt/disk2 /mnt/disk3 /mnt/disk4
```

The specified drive paths are provided as an example. Change them to match the path to those drives intended for use by MinIO.

Alternatively, change the `User` and `Group` values to another user and group on the system host with the necessary access and permissions.

MinIO publishes additional startup script examples on [github.com/minio/minio-service](https://github.com/minio/minio-service).

To update deployments managed using `systemctl`, see [升级由 systemctl 管理的 MinIO 部署](/docs/operations/deployments/baremetal-upgrade-minio-deployment/#minio-upgrade-systemctl).

### 4) 创建服务环境文件 {#id16}

在 `/etc/default/minio` 创建环境文件。 MinIO 服务会将该文件作为 MinIO *以及* `minio.service` 文件所用全部 [环境变量](/docs/reference/minio-server/settings/#minio-server-environment-variables) 的来源。

以下示例假设：

- 该部署当前只有一个 服务器池，由四台使用连续主机名的 MinIO server 主机构成。

  ```shell
  minio1.example.com   minio3.example.com
  minio2.example.com   minio4.example.com
  ```

  每台主机都有 4 块本地直连驱动器，挂载点连续：

  ```shell
  /mnt/disk1/minio   /mnt/disk3/minio
  /mnt/disk2/minio   /mnt/disk4/minio
  ```

- 新的 服务器池 由八台使用连续主机名的新 MinIO 主机构成：

  ```shell
  minio5.example.com   minio9.example.com
  minio6.example.com   minio10.example.com
  minio7.example.com   minio11.example.com
  minio8.example.com   minio12.example.com
  ```

- 所有主机都具有八块本地直连驱动器，挂载点连续：

  ```shell
  /mnt/disk1/minio  /mnt/disk5/minio
  /mnt/disk2/minio  /mnt/disk6/minio
  /mnt/disk3/minio  /mnt/disk7/minio
  /mnt/disk4/minio  /mnt/disk8/minio
  ```

- 该部署有一个运行在 `https://minio.example.net` 的负载均衡器，用于管理到所有 MinIO 主机的连接。 在此步骤中，负载均衡器不应将请求路由到新主机，但应已准备好所需的配置更新计划。

请根据你的部署拓扑修改示例：

```shell
# Set the hosts and volumes MinIO uses at startup
# The command uses MinIO expansion notation {x...y} to denote a
# sequential series.
#
# The following example starts the MinIO server with two 服务器池s.
#
# The space delimiter indicates a seperate 服务器池
#
# The second set of hostnames and volumes is the newly added pool.
# The pool has sufficient stripe size to meet the existing erasure code
# parity of the deployment (2 x EC:4)
#
# The command includes the port on which the MinIO servers listen for each
# 服务器池.

MINIO_VOLUMES="https://minio{1...4}.example.net:9000/mnt/disk{1...4}/minio https://minio{5...12}.example.net:9000/mnt/disk{1...8}/minio"

# Set all MinIO server options
#
# The following explicitly sets the MinIO Console listen address to
# port 9001 on all network interfaces. The default behavior is dynamic
# port selection.

MINIO_OPTS="--console-address :9001"

# Set the root username. This user has unrestricted permissions to
# perform S3 and administrative API operations on any resource in the
# deployment.
#
# Defer to your organizations requirements for superadmin user name.

MINIO_ROOT_USER=minioadmin

# Set the root password
#
# Use a long, random, unique string that meets your organizations
# requirements for passwords.

MINIO_ROOT_PASSWORD=minio-secret-key-CHANGE-ME
```

你可以根据部署需要指定其他 [环境变量](/docs/reference/minio-server/settings/#minio-server-environment-variables) 或 server 命令行选项。 部署中的所有 MinIO 节点都应包含相同且取值一致的环境变量。

### 5) 使用扩展后的配置重启 MinIO 部署 {#id17}

在部署中的每个节点上 **同时** 执行以下命令，以重启 MinIO 服务：

```shell
sudo systemctl restart minio.service
```

Use the following commands to confirm the service is online and functional:

```shell
sudo systemctl status minio.service
journalctl -f -u minio.service
```

MinIO may log an increased number of non-critical warnings while the server processes connect and synchronize. These warnings are typically transient and should resolve as the deployment comes online.

MinIO 强烈建议同时重启一个部署中的所有 MinIO 服务端进程。 MinIO 操作具有原子性并保持严格一致。 因此，该重启过程不会中断应用或正在进行的操作。

**不要** 执行“滚动”重启（例如一次只重启一个节点）。

### 6) 后续步骤 {#id18}

- 更新所有负载均衡器、反向代理或其他网络控制平面，使客户端请求能够路由到 MinIO 分布式部署中的新主机。 虽然 MinIO 会在内部自动管理路由，但由控制平面处理初始连接通常可以减少网络跳数并提升效率。
- 查看 [MinIO Console](/docs/administration/minio-console/#minio-console)，确认更新后的集群拓扑并监控性能。