---
title: "硬件故障恢复"

weight: 90
icon: fa-solid fa-life-ring
---

<a id="minio-restore-hardware-failure"></a>
<a id="id1"></a>

分布式 MinIO 部署依赖 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding)，对多块驱动器或多个节点故障提供内建容错能力。 根据部署拓扑和所选纠删码校验位，MinIO 在保持对象读取访问能力（“read quorum”）的前提下，最多可容忍部署中一半驱动器或节点丢失。

下表列出了 MinIO 部署中的典型故障类型，以及对应的恢复流程链接：

| 故障类型 | 说明 |
| --- | --- |
| [驱动器故障](/docs/operations/data-recovery/recover-after-drive-failure/#minio-restore-hardware-failure-drive) | MinIO 支持将故障驱动器热替换为新的健康驱动器。 |
| [节点故障](/docs/operations/data-recovery/recover-after-node-failure/#minio-restore-hardware-failure-node) | MinIO 会检测节点何时重新加入部署，并在其重新并入集群后不久主动开始对该节点执行 [自愈](/docs/operations/concepts/healing/#minio-concepts-healing)，恢复此前存储在该节点上的数据。 |
| [站点故障](/docs/operations/data-recovery/recover-after-site-failure/#minio-restore-hardware-failure-site) | MinIO Site Replication 支持在站点完全丢失后，对存储桶、对象以及可复制的配置项执行完整重同步。 |

由于 MinIO 即使处于降级状态也通常不会出现显著性能损失，管理员可以根据硬件故障速率来安排替换窗口。 “正常”故障率（单个驱动器或节点故障）通常允许采用更从容的替换节奏，而“关键”故障率（多个驱动器或节点故障）则可能需要更快响应。

对于包含一个或多个部分故障或已处于降级状态的驱动器的节点（例如驱动器错误增加、SMART 告警、MinIO 日志中出现超时等），如果集群剩余健康驱动器足以维持 [读写仲裁](/docs/operations/concepts/erasure-coding/#minio-ec-parity)，您可以安全地卸载该驱动器。 相较于持续产生读写错误的驱动器，缺失驱动器对部署的破坏性反而更小。

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

> [!NOTE]
> **MinIO 专业支持**
>
> [MinIO SUBNET](https://min.io/pricing?jmp=docs) 用户可以 [登录](https://subnet.min.io/) 并创建与驱动器、节点或站点故障相关的新 issue。 通过 SUBNET 与 MinIO Engineering 协作，可提升生产 MinIO 部署恢复操作成功率，并获得根因分析与健康诊断支持。
>
> 社区用户可以在 [MinIO Community Slack](https://slack.min.io) 寻求支持。 社区支持仅为尽力而为，不提供响应时间相关 SLA。