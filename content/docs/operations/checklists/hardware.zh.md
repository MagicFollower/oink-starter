---
title: "硬件检查清单"

weight: 10
math: true
---

<a id="minio-hardware-checklist"></a>
<a id="id1"></a>

在为生产级分布式 MinIO 部署规划硬件配置时，请使用以下检查清单。

## 考虑因素 {#id3}

在为 MinIO 选型硬件时，请考虑以下因素：

- 上线时预计需要存储的数据量（tebibyte）
- 至少未来两年内数据规模的预期增长
- 对象数量以及平均对象大小
- 数据的平均保留时长（年）
- 计划部署的站点数量
- 预期的存储桶数量

<a id="id4"></a>

## 生产硬件建议 {#deploy-minio-distributed-recommendations}

以下检查清单遵循 MinIO 面向生产部署的 [Recommended Configuration](https://min.io/product/reference-hardware?ref-docs)。 这里提供的指导仅作为基线，不能替代 [MinIO SUBNET](https://min.io/pricing?jmp=docs) Performance Diagnostics、Architecture Reviews 以及 direct-to-engineering 支持。

与其他分布式系统一样，MinIO 在同一 [服务器池](/zh/glossary/#term-43) 内的所有节点都使用相同配置时，通常能获得更好的效果。 请确保 pool 内各节点的硬件（CPU、内存、主板、存储适配器）和软件（操作系统、内核设置、系统服务）选择保持一致。

如果节点的硬件或软件配置不一致，部署可能表现出不可预测的性能。 对于适合将陈旧数据放在低成本硬件上的工作负载，应改为部署专用的“温”或“冷”MinIO 部署，并将数据 [转移](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 到该层级。

> [!NOTE]
> **MinIO 不提供托管服务或硬件销售**
>
> 如需查看硬件合作伙伴提供的服务器与存储组件精选清单，请参见我们的 [Reference Hardware](https://min.io/product/reference-hardware#hardware?ref-docs) 页面。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
<table>
  <thead>
    <tr>
      <th></th>
      <th><p>说明</p></th>
      <th><p>最低</p></th>
      <th><p>推荐</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>专用于承载 MinIO Tenant 的 Kubernetes worker 节点。</p></td>
      <td><p>每个 Tenant 4 个 worker</p></td>
      <td><p>每个 Tenant 8 个以上 worker</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-storage">为 MinIO Tenant 配置专用 Persistent Volume</a>。</p></td>
      <td><p>每个 MinIO Server pod 4 个 PV</p></td>
      <td><p>每个 MinIO Server pod 8 个以上 PV</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-network">高速网络基础设施</a>。</p></td>
      <td><p>25GbE</p></td>
      <td><p>100GbE</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>支持现代 SIMD 指令（AVX-512）的服务器级 CPU，例如 Intel® Xeon® Scalable 或更高规格。</p></td>
      <td><p>每个 MinIO Pod 4 个 vCPU</p></td>
      <td><p>每个 MinIO Pod 8 个以上 vCPU</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-memory">可用内存</a> 应在每台服务器使用量的基础上保留合理余量，并满足或超过该值。</p></td>
      <td><p>每个 worker 节点 32GB 可用内存</p></td>
      <td><p>每个 worker 节点 128GB 以上可用内存</p></td>
    </tr>
  </tbody>
</table>
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
<table>
  <thead>
    <tr>
      <th></th>
      <th><p>说明</p></th>
      <th><p>最低</p></th>
      <th><p>推荐</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>专用裸机或虚拟主机（“主机”）。</p></td>
      <td><p>4 台专用主机</p></td>
      <td><p>8 台以上专用主机</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-storage">为每台主机配置专用本地直连驱动器</a>。</p></td>
      <td><p>每个 MinIO Server 4 块驱动器</p></td>
      <td><p>每个 MinIO Server 8 块以上驱动器</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-network">高速网络基础设施</a>。</p></td>
      <td><p>25GbE</p></td>
      <td><p>100GbE</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>支持现代 SIMD 指令（AVX-512）的服务器级 CPU，例如 Intel® Xeon® Scalable 或更高规格。</p></td>
      <td><p>每台主机 8 个 CPU/socket 或 vCPU</p></td>
      <td><p>每台主机 16 个以上 CPU/socket 或 vCPU</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="#minio-hardware-checklist-memory">可用内存</a> 应在每台服务器使用量的基础上保留合理余量，并满足或超过该值。</p></td>
      <td><p>每台主机 32GB 可用内存</p></td>
      <td><p>每台主机 128GB 以上可用内存</p></td>
    </tr>
  </tbody>
</table>
{{< /tab >}}
{{< /tabs >}}

> [!WARNING]
> **重要**
>
> 以下领域对 MinIO 性能影响最大，重要性从高到低依次如下：
>
> <table>
>   <tbody>
>     <tr>
>       <td><p>网络基础设施</p></td>
>       <td><p>吞吐量不足或受限会约束性能</p></td>
>     </tr>
>     <tr>
>       <td><p>存储控制器</p></td>
>       <td><p>固件过旧、吞吐量有限或硬件故障会约束性能并影响可靠性</p></td>
>     </tr>
>     <tr>
>       <td><p>存储（驱动器）</p></td>
>       <td><p>固件过旧，或硬件过慢、老化、故障，会约束性能并影响可靠性</p></td>
>     </tr>
>   </tbody>
> </table>
>
> 在关注计算类约束等其他硬件资源之前，请优先确保这些领域的关键组件到位。

上述最低建议体现了 MinIO 在协助企业客户部署到多种 IT 基础设施、同时保持目标 SLA/SLO 方面的实践经验。 虽然 MinIO 可能在低于最低建议的拓扑上运行，但任何潜在的成本节省都要以可靠性、性能或整体功能下降为代价。

<a id="id5"></a>

### 网络 {#minio-hardware-checklist-network}

MinIO 建议使用高速网络，以支撑所连接存储（聚合驱动器、存储控制器和 PCIe 总线）的最大可能吞吐量。 下表给出了不同物理或虚拟网络接口可支撑的最大存储吞吐量的一般参考值。 该表假设所有网络基础设施组件（例如路由器、交换机和物理线缆）同样支持对应的 NIC 带宽。

<table>
  <tbody>
    <tr>
      <td><p>NIC 带宽（Gbps）</p></td>
      <td><p>估算聚合存储吞吐量（GBps）</p></td>
    </tr>
    <tr>
      <td><p>10Gbps</p></td>
      <td><p>1.25GBps</p></td>
    </tr>
    <tr>
      <td><p>25Gbps</p></td>
      <td><p>3.125GBps</p></td>
    </tr>
    <tr>
      <td><p>50Gbps</p></td>
      <td><p>6.25GBps</p></td>
    </tr>
    <tr>
      <td><p>100Gbps</p></td>
      <td><p>12.5GBps</p></td>
    </tr>
  </tbody>
</table>

网络对 MinIO 性能影响最大，较低的单主机带宽会人为限制存储的潜在性能。 以下网络吞吐受限示例假设机械盘可提供约 100MB/S 的持续 I/O：

- 1GbE 网络链路最多可支撑 125MB/s，大约相当于一块机械盘
- 10GbE 网络大约可支撑 1.25GB/s，理论上可支撑 10 到 12 块机械盘
- 25GbE 网络大约可支撑 3.125GB/s，理论上可支撑约 30 块机械盘

<a id="id6"></a>

### 内存 {#minio-hardware-checklist-memory}

内存主要限制每个节点可同时处理的并发连接数。

你可以使用以下公式计算每个节点的最大并发请求数：

> \(totalRam / ramPerRequest\)

若要计算每个请求使用的 RAM，请使用以下公式：

> \(((2MiB + 128KiB) \times driveCount) + (2 \times 10MiB) + (2 \times 1MiB)\)
>
> 10MiB 是默认的 erasure block size v1。 1 MiB 是默认的 erasure block size v2。

下表根据主机驱动器数量和系统 *可用* RAM，列出节点上的最大并发请求数：

| 驱动器数量 | 32 GiB RAM | 64 GiB RAM | 128 GiB RAM | 256 GiB RAM | 512 GiB RAM |
| --- | --- | --- | --- | --- | --- |
| 4 Drives | 1,074 | 2,149 | 4,297 | 8,595 | 17,190 |
| 8 Drives | 840 | 1,680 | 3,361 | 6,722 | 13,443 |
| 16 Drives | 585 | 1,170 | 2.341 | 4,681 | 9,362 |

下表根据节点本地存储总量，给出为 MinIO 分配内存的一般建议：

| 主机总存储量 | 建议的主机内存 |
| --- | --- |
| 不超过 1 Tebibyte (Ti) | 8GiB |
| 不超过 10 Tebibyte (Ti) | 16GiB |
| 不超过 100 Tebibyte (Ti) | 32GiB |
| 不超过 1 Pebibyte (Pi) | 64GiB |
| 超过 1 Pebibyte (Pi) | 128GiB |

> [!WARNING]
> **重要**
>
> 从 [RELEASE.2024-01-28T22-35-53Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-01-28T22-35-53Z) 开始，MinIO 在分布式部署中会为每个节点预分配 2GiB 内存，在单节点部署中会预分配 1GiB 内存。

<a id="id7"></a>

### 存储 {#minio-hardware-checklist-storage}

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

#### 推荐的存储介质 {#id8}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
MinIO 建议为每个 MinIO Tenant 配置满足其性能目标的 storage class。

在可能的情况下，请将 PV 底层的 Storage Class、CSI 或其他 provisioner 配置为将卷格式化为 XFS，以获得最佳性能。

请确保 Tenant 中所有已配置 PV 的底层存储类型（NVMe、SSD、HDD）保持一致。

请确保每个 Tenant [服务器池](/docs/operations/concepts/#minio-intro-server-pool) 内所有节点呈现给各 PV 的容量一致。 MinIO 会将每个 PV 的最大可用容量限制为该 pool 中最小的 PV。 例如，如果某个 pool 具有 15 个 10TB PV 和 1 个 1TB PV，MinIO 会将每个 PV 的可用容量限制为 1TB。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
MinIO 建议在所有工作负载类型和规模下都使用闪存介质（NVMe 或 SSD）。 对性能要求较高的工作负载应优先选择 NVMe 而不是 SSD。

MinIO 不建议在生产环境中使用 HDD 存储。 HDD 存储通常无法提供现代工作负载所需的性能，而其规模化成本优势也会被介质本身的性能约束所抵消。
{{< /tab >}}
{{< /tabs >}}

#### 优先使用直连“本地”存储（DAS） {#das}

<abbr title="Direct-Attached Storage">DAS</abbr>，例如本地直连的 <abbr title="Just a Bunch of Disks">JBOD</abbr> 阵列，相比网络存储（NAS、SAN、NFS）在性能和一致性方面具有显著优势。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
虽然 MinIO Tenant 可以使用远程 Persistent Volume (PV) 资源，但通过网络执行 I/O 的成本通常会限制整体性能。

MinIO 强烈建议使用能够将存储配置到 Kubernetes 调度 MinIO pods 所在 worker 节点上的 CSI，例如 [MinIO DirectPV](https://github.com/minio/directpv)。

在其他场景中，也应尽可能选择能让 MinIO 像访问本地挂载文件系统一样访问存储的 CSI。 在 MinIO 与操作系统级存储访问 API 之间增加软件层或转换层的 CSI，必然会增加系统复杂度，并可能带来意料之外或不期望的行为。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
请将 JBOD 阵列配置为无 RAID、无 pooling 或其他类似的软件层，使存储可以直接呈现给 MinIO。

对于虚拟机或需要以虚拟卷形式提供存储的系统，MinIO 只建议使用 thick LUN。
{{< /tab >}}
{{< /tabs >}}

> [!DETAILS]- 网络文件系统卷会破坏一致性保证
> MinIO 严格的 **read-after-write** 和 **list-after-write** 一致性模型要求使用本地驱动器文件系统。 如果底层存储卷是 NFS 或类似的网络挂载存储卷，MinIO 无法提供一致性保证。

#### 使用 XFS 格式化驱动器并保持一致挂载 {#xfs}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
MinIO 建议将 MinIO Persistent Volumes 底层驱动器格式化为 `xfs`。

如果使用 CSI，请查阅对应 CSI 的文档，并确保其支持指定 `xfs` 文件系统。 MinIO 强烈建议避免使用会将驱动器格式化为 `ext4`、`btrfs` 或其他文件系统的 CSI。

MinIO 预期所有已配置的 Persistent Volumes (PV) 都专供自身使用，且底层存储介质能够在指定挂载路径上保证对已存储数据的访问。 对底层存储介质的修改，包括但不限于外部或第三方应用干预，或对本地直连存储进行任意重新挂载，都可能导致异常行为或数据丢失。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
请将驱动器格式化为 XFS，并以无 RAID 或其他 pooling 配置的 <abbr title="Just a Bunch of Disks">JBOD</abbr> 阵列形式提供给 MinIO。 使用其他类型的后端存储（SAN/NAS、ext4、RAID、LVM）通常会降低性能、可靠性、可预测性和一致性。

格式化 XFS 驱动器时，请为每块驱动器设置唯一标签。 例如，以下命令会将四块驱动器格式化为 XFS，并为其设置对应标签。

```shell
mkfs.xfs /dev/sdb -L MINIODRIVE1
mkfs.xfs /dev/sdc -L MINIODRIVE2
mkfs.xfs /dev/sdd -L MINIODRIVE3
mkfs.xfs /dev/sde -L MINIODRIVE4
```

MinIO **要求** 驱动器在重启后仍保持其挂载位置上的顺序不变。 MinIO **不支持** 将已有 MinIO 数据的驱动器任意迁移到新的挂载位置，无论这是人工操作还是操作系统行为导致。

你 **必须** 使用 `/etc/fstab` 或类似的挂载控制系统，将驱动器挂载到固定路径。 例如：

```shell
$ nano /etc/fstab

# <file system>        <mount point>    <type>  <options>         <dump>  <pass>
LABEL=MINIODRIVE1      /mnt/drive-1     xfs     defaults,noatime  0       2
LABEL=MINIODRIVE2      /mnt/drive-2     xfs     defaults,noatime  0       2
LABEL=MINIODRIVE3      /mnt/drive-3     xfs     defaults,noatime  0       2
LABEL=MINIODRIVE4      /mnt/drive-4     xfs     defaults,noatime  0       2
```

在初始设置期间，你可以使用 `mount -a` 将这些驱动器挂载到这些路径。 否则，操作系统应在节点启动过程中自动完成这些驱动器的挂载。

MinIO **强烈建议** 使用基于标签的挂载规则，而不是基于 UUID 的规则。 基于标签的规则允许你用格式和标签相同的替换盘，替换不健康或损坏的驱动器。 基于 UUID 的规则则要求编辑 `/etc/fstab` 文件，用新驱动器的 UUID 替换原有映射。

> [!NOTE]
> **说明**
>
> 依赖挂载外部存储的云环境实例，如果一个或多个远程文件挂载返回错误或失败，可能在启动时直接失败。 例如，挂载持久化 EBS 卷的 AWS ECS 实例，如果一个或多个 EBS 卷挂载失败，可能无法按照标准 `/etc/fstab` 配置正常启动。
>
> 你可以设置 `nofail` 选项，在启动时静默这些错误并允许实例在存在一个或多个挂载问题时继续启动。
>
> 但对于使用本地直连磁盘的系统，不应使用该选项，因为静默驱动器错误会阻止 MinIO 和操作系统以正常方式响应这些错误。
{{< /tab >}}
{{< /tabs >}}

#### 禁用 XFS 的出错重试 {#id9}

MinIO **强烈建议** 通过 `max_retries` 配置禁用 [retry-on-error](https://docs.kernel.org/admin-guide/xfs.html?highlight=xfs#error-handling) 行为，至少针对以下错误类别：

- `EIO` 读或写时发生错误
- `ENOSPC` 设备空间不足错误
- `default` 其他所有错误

默认的 `max_retries` 设置通常会让文件系统在出错后无限重试，而不是将错误向上传递。 MinIO 可以正确处理 XFS 错误，因此 retry-on-error 行为最多只会引入不必要的延迟或性能下降。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
关于如何配置文件系统级设置，请以所选 CSI 或 StorageClass 的文档为准。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
以下脚本会遍历指定挂载路径下的所有驱动器，并将推荐错误类别对应的 XFS `max_retries` 设置为 `0`，即“出错立即失败”。 该脚本会忽略所有未挂载的驱动器，无论它们是手动未挂载，还是未通过 `/etc/fstab` 挂载。 请将 `/mnt/drive` 这一行修改为符合你 MinIO 驱动器路径模式的值。

```bash
#!/bin/bash

for i in $(df -h | grep /mnt/drive | awk '{ print $1 }'); do
      mountPath="$(df -h | grep $i | awk '{ print $6 }')"
      deviceName="$(basename $i)"
      echo "Modifying xfs max_retries and retry_timeout_seconds for drive $i mounted at $mountPath"
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/EIO/max_retries
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/ENOSPC/max_retries
      echo 0 > /sys/fs/xfs/$deviceName/error/metadata/default/max_retries
done
exit 0
```

你必须在所有 MinIO 节点上运行此脚本，并将其配置为在重启后重新执行，因为 Linux 操作系统通常不会持久保存这些修改。 你可以使用 `@reboot` 时机的 `cron` 任务，在节点每次重启时运行上述脚本，以确保所有驱动器都禁用了 retry-on-error。 使用 `crontab -e` 创建以下任务，并将脚本路径修改为各节点上的实际路径：

```shell
@reboot /opt/minio/xfs-retry-settings.sh
```
{{< /tab >}}
{{< /tabs >}}

#### 统一驱动器类型与容量 {#id10}

请确保 MinIO 部署底层存储的驱动器类型（NVMe、SSD、HDD）一致。 MinIO 不区分存储类型，也不支持在单一部署内部配置“热”或“温”驱动器。 混用不同驱动器类型通常会导致性能下降，因为无论更快驱动器能力如何，部署中最慢的驱动器都会成为瓶颈。

请在每个 MinIO [服务器池](/docs/operations/concepts/#minio-intro-server-pool) 的所有节点上使用相同容量和类型的驱动器。 MinIO 会将每块驱动器的最大可用容量限制为部署中最小的那块驱动器容量。 例如，如果某个部署中有 15 块 10TB 驱动器和 1 块 1TB 驱动器，MinIO 会将每块驱动器的可用容量限制为 1TB。

## 推荐的硬件测试 {#id11}

### 操作系统诊断工具 {#id12}

如果你无法运行 [`mc support diag`](/docs/reference/minio-mc/mc-support-diag/#command-mc.support.diag)，或者其结果出现异常，可以改用操作系统默认提供的工具。

请在所有服务器上分别测试每块驱动器，以确认它们的性能一致。 使用这些操作系统级工具的结果来验证你的存储硬件能力。 请记录这些结果，以备后续参考。

1. 测试驱动器写入性能

   此测试通过按指定块数、每次最多写入指定字节数的方式向驱动器写入新数据（非缓存），以模拟驱动器在写入非缓存数据时的实际工作方式。 这可以让你在保持文件 I/O 一致的前提下，观察驱动器的真实写入性能。

   ```text
   dd if=/dev/zero of=/mnt/driveN/testfile bs=128k count=80000 oflag=direct conv=fdatasync > dd-write-drive1.txt
   ```

   请将 `driveN` 替换为你要测试的驱动器路径。

   <table>
     <tbody>
       <tr>
         <td><p><code>dd</code></p></td>
         <td><p>用于复制和粘贴数据的命令</p></td>
       </tr>
       <tr>
         <td><p><code>if=/dev/zero</code></p></td>
         <td><p>从 <code>/dev/zero</code> 读取，这是一种系统生成的、无限输出 0 字节的数据流，可用于创建指定大小的文件</p></td>
       </tr>
       <tr>
         <td><p><code>of=/mnt/driveN/testfile</code></p></td>
         <td><p>写入到 <code>/mnt/driveN/testfile</code></p></td>
       </tr>
       <tr>
         <td><p><code>bs=128k</code></p></td>
         <td><p>每次最多写入 128,000 字节</p></td>
       </tr>
       <tr>
         <td><p><code>count=80000</code></p></td>
         <td><p>最多写入 80000 个数据块</p></td>
       </tr>
       <tr>
         <td><p><code>oflag=direct</code></p></td>
         <td><p>使用 direct I/O 写入，避免数据被缓存</p></td>
       </tr>
       <tr>
         <td><p><code>conv=fdatasync</code></p></td>
         <td><p>在结束前将输出文件数据物理写入磁盘</p></td>
       </tr>
       <tr>
         <td><p><code>&gt; dd-write-drive1.txt</code></p></td>
         <td><p>将操作输出内容写入当前工作目录下的 <code>dd-write-drive1.txt</code></p></td>
       </tr>
     </tbody>
   </table>

   该操作会返回已写入文件数量、总写入字节数、操作总耗时（秒）以及某种字节每秒表示的写入速度。
2. 测试驱动器读取性能

   ```text
   dd if=/mnt/driveN/testfile of=/dev/null bs=128k iflag=direct > dd-read-drive1.txt
   ```

   请将 `driveN` 替换为你要测试的驱动器路径。

   <table>
     <tbody>
       <tr>
         <td><p><code>dd</code></p></td>
         <td><p>用于复制和粘贴数据的命令</p></td>
       </tr>
       <tr>
         <td><p><code>if=/mnt/driveN/testfile</code></p></td>
         <td><p>从 <code>/mnt/driveN/testfile</code> 读取；请替换为用于测试驱动器读取性能的文件路径</p></td>
       </tr>
       <tr>
         <td><p><code>of=/dev/null</code></p></td>
         <td><p>写入 <code>/dev/null</code>，这是一个在操作完成后不会保留内容的虚拟文件</p></td>
       </tr>
       <tr>
         <td><p><code>bs=128k</code></p></td>
         <td><p>每次最多写入 128,000 字节</p></td>
       </tr>
       <tr>
         <td><p><code>count=80000</code></p></td>
         <td><p>最多写入 80000 个数据块</p></td>
       </tr>
       <tr>
         <td><p><code>iflag=direct</code></p></td>
         <td><p>使用 direct I/O 读取，避免数据被缓存</p></td>
       </tr>
       <tr>
         <td><p><code>&gt; dd-read-drive1.txt</code></p></td>
         <td><p>将操作输出内容写入当前工作目录下的 <code>dd-read-drive1.txt</code></p></td>
       </tr>
     </tbody>
   </table>

   请使用足够大的文件，以模拟部署的主要使用场景，从而获得准确的读取测试结果。

   以下建议可在性能测试时提供帮助：

   - 小文件：&lt; 128KB
   - 普通文件：128KB – 1GB
   - 大文件：&gt; 1GB

   你可以使用 `head` 命令创建测试文件。 以下命令示例会创建一个名为 `testfile` 的 10 Gigabyte 文件。

   ```shell
   head -c 10G </dev/urandom > testfile
   ```

   该操作会返回已读取文件数量、总读取字节数、操作总耗时（秒）以及某种字节每秒表示的读取速度。

### 第三方诊断工具 {#id13}

I/O 控制器测试

使用 [IOzone](http://iozone.org/) 对输入/输出控制器及所有驱动器组合进行测试。 请记录部署中每台服务器的性能数据。

```shell
iozone -s 1g -r 4m -i 0 -i 1 -i 2 -I -t 160 -F /mnt/sdb1/tmpfile.{1..16} /mnt/sdc1/tmpfile.{1..16} /mnt/sdd1/tmpfile.{1..16} /mnt/sde1/tmpfile.{1..16} /mnt/sdf1/tmpfile.{1..16} /mnt/sdg1/tmpfile.{1..16} /mnt/sdh1/tmpfile.{1..16} /mnt/sdi1/tmpfile.{1..16} /mnt/sdj1/tmpfile.{1..16} /mnt/sdk1/tmpfile.{1..16} > iozone.txt
```

<table>
  <tbody>
    <tr>
      <td><p><code>-s 1g</code></p></td>
      <td><p>每个文件大小为 1G</p></td>
    </tr>
    <tr>
      <td><p><code>-r</code></p></td>
      <td><p>4m，即 4MB 块大小</p></td>
    </tr>
    <tr>
      <td><p><code>-i #</code></p></td>
      <td><p>0=write/rewrite，1=read/re-read，2=random-read/write</p></td>
    </tr>
    <tr>
      <td><p><code>-I</code></p></td>
      <td><p>使用 Direct-IO 模式</p></td>
    </tr>
    <tr>
      <td><p><code>-t N</code></p></td>
      <td><p>线程数（numberOfDrives * 16）</p></td>
    </tr>
    <tr>
      <td><p><code>-F &lt;&gt;</code></p></td>
      <td><p>文件列表（上述命令按每块驱动器 16 个文件进行测试）</p></td>
    </tr>
  </tbody>
</table>

## 适用于 MinIO 订阅的推荐工具 {#minio}

> [!WARNING]
> **重要**
>
> 本节提到的工具 **需要** MinIO 订阅。MinIO 强烈建议所有生产部署结合其 SUBNET 许可证使用 [AIStor Object Store](https://www.min.io/product/aistor/object-data-store)。更多信息请参见 [MinIO AIStor pricing page](https://min.io/pricing?jmp=docs)。

1. 健康诊断工具

   生成部署健康状态摘要。 如果你可以访问 SUBNET，可以将结果上传到那里。

   ```shell
   mc support diag ALIAS --airgap
   ```

   请将 ALIAS 替换为该部署中定义的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
2. 网络测试

   对 alias 为 `minio1` 的集群运行网络吞吐测试。

   ```shell
   mc support perf net minio1
   ```

3. 驱动器测试

   对 alias 为 `minio1` 的集群，在所有节点上的所有驱动器执行读写性能测量。 该命令使用默认的 4MiB blocksize。

   ```shell
   mc support perf drive minio1
   ```

4. 对象测试

   对 alias 为 `minio1` 的对象执行 S3 读写性能测量。 MinIO 会自动调优并发度，以获得最大吞吐量和 IOPS（Input/Output Per Second）。

   ```shell
   mc support perf object minio1
   ```