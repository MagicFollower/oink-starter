---
title: "安装与管理"

description: "Silo 部署拓扑与安装说明"
weight: 10
icon: fa-solid fa-download
---

<a id="minio-snsd"></a>
<a id="minio-snmd"></a>
<a id="minio-installation"></a>
<a id="minio-mnmd"></a>
<a id="deploy-minio-distributed"></a>
<a id="id1"></a>

本节介绍如何在 [Kubernetes](/docs/operations/deployments/kubernetes/#minio-kubernetes) 和 [裸机或虚拟化](/docs/operations/deployments/baremetal/#minio-baremetal) 基础设施上安装与管理采用 AGPLv3 许可的 Silo 对象存储服务端。

`minio` 可执行文件、`MINIO_*` 环境变量、S3 与 Admin API、盘上格式，以及 MinIO Operator 资源名都是兼容契约。叙述使用 Silo 品牌，命令和标识符则保留兼容名称。

Silo 是兼容 S3 的软件定义分布式对象存储服务端。[下载页面](/zh/download/) 是当前已发布操作系统与架构制品的事实来源。

Silo 使用 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 保护对象数据。你可以选择以下拓扑：

**[单机单盘](#minio-snsd) （SNSD，即”单机”模式）**

> 适用于本地开发与评估，可靠性有限或无冗余

**[单机多盘](#minio-snmd) （SNMD，即”单机多盘”模式）**

> 适用于对性能、规模和容量要求较低的工作负载
>
> 提供驱动器级可靠性，可配置为最多容忍 1/2 驱动器丢失
>
> 适合评估多驱动器拓扑和故障切换行为。

**[多机多盘](#minio-mnmd) （MNMD，即”分布式”模式）**

> 企业级高性能对象存储
>
> 提供节点/驱动器级可靠性，可配置为最多容忍 1/2 节点/驱动器丢失
>
> 可作为 AI/ML、分布式查询、分析及其他数据湖组件的主存储
>
> 可扩展到 PB+ 级工作负载，同时扩展存储容量与性能

## Kubernetes {#kubernetes}

已经归档的 MinIO Kubernetes Operator `v7.1.1` 可以管理运行 Silo 服务端镜像的 Tenant 资源。Operator、Chart、CRD 与 `Tenant` Kind 保留上游名称；其上游发布周期现已冻结。

这些保留的 Operator 指南描述一份兼容快照。上游仓库已于 2026-03-20 归档，因此请根据 Kubernetes 发行版验证 `v7.1.1`，并将 Tenant 镜像覆盖为 `pgsty/silo`；Silo 项目不继承上游原厂商曾经的平台支持矩阵声明。

- [使用 Helm 部署 Silo Tenant](/docs/operations/deployments/k8s-deploy-minio-tenant-helm-on-kubernetes/)
- [部署 MinIO Operator](/docs/operations/deployments/k8s-deploy-operator-helm-on-kubernetes/)
- [查看 Kubernetes 部署说明](/docs/operations/deployments/kubernetes/)

## 裸金属 {#id3}

Silo 可以运行在物理机、虚拟化主机或容器中。请查阅当前下载矩阵和各平台页面，确认已验证的制品与范围。

- [在 Red Hat Linux 上部署 Silo](/docs/operations/deployments/baremetal-deploy-minio-on-redhat-linux/#deploy-minio-rhel)
- [在 Ubuntu Linux 上部署 Silo](/docs/operations/deployments/baremetal-deploy-minio-on-ubuntu-linux/#deploy-minio-ubuntu)
- [以容器方式部署 Silo](/docs/operations/deployments/baremetal-deploy-minio-as-a-container/#deploy-minio-container)
- [在 macOS 上部署 Silo](/docs/operations/deployments/baremetal-deploy-minio-on-macos/#deploy-minio-macos)
- [在 Windows 上部署 Silo](/docs/operations/deployments/baremetal-deploy-minio-on-windows/#deploy-minio-windows)

> [!WARNING]
> **重要**
>
> 发布制品的存在不代表所有平台都有同等的生产验证范围。长期工作负载应优先使用经过测试的 Linux 或 Kubernetes 部署，固定确切的软件包/镜像版本，并根据所选拓扑验证存储、故障域、升级与恢复行为。