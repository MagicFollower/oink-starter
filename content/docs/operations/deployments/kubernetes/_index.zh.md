---
title: "在 Kubernetes 上部署 Silo"

weight: 10
icon: fa-solid fa-dharmachakra
---

<a id="kubernetes-minio"></a>
<a id="minio-operator-installation"></a>
<a id="deploy-operator-aks"></a>
<a id="deploy-operator-gke"></a>
<a id="deploy-operator-eks"></a>
<a id="deploy-operator-rancher"></a>
<a id="deploy-operator-openshift"></a>
<a id="deploy-operator-kubernetes"></a>
<a id="minio-kubernetes"></a>

Silo 是可在 Kubernetes 中运行的 S3 兼容对象存储服务端。MinIO Kubernetes Operator 的最后一个上游版本 `v7.1.1` 可以部署使用 Silo 镜像的 `Tenant`：将 `tenant.image.repository` 覆盖为 `pgsty/silo`，并固定经过测试的标签或摘要。

这些指南默认你熟悉所引用的 Kubernetes 概念、工具和操作流程。它们不能替代官方 [Kubernetes Documentation](https://kubernetes.io/docs/)；Silo 项目也不继承原 MinIO 厂商针对各 Kubernetes 发行版的支持矩阵。

MinIO Operator、Helm Chart、CRD 与 `Tenant` Kind 都是独立于 Silo 发布的上游契约。上游 `minio/operator` 仓库已于 2026-03-20 归档并设为只读，因此其发布周期已经冻结，这些指南只是一份兼容快照。

归档的 Operator 代码提供 MinIO 兼容的 Tenant 管理与配置功能。在部署或升级前，请针对实际集群验证固定的 Operator 与 Chart；上游不再提供持续的兼容性或支持承诺。

你可以通过 Operator 的 [Custom Resource Definition (CRD)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) 与其交互。

CRD 为 Kustomize、Helm 和 `kubectl` 等工具部署与管理使用 Silo 镜像的 Tenant 提供可定制入口。

> [!WARNING]
> **重要**
>
> MinIO Operator Console UI 已被弃用，并在 MinIO Operator 6.0.0 中移除。
>
> 你仍可继续使用标准 Kubernetes 方式管理 MinIO 租户，例如 Kustomize 模板、Helm Charts，以及用于查看租户命名空间和资源的 `kubectl` 命令。