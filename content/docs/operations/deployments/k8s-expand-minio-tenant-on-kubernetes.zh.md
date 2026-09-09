---
title: "扩展 Silo Tenant"

weight: 50
---

<a id="minio-tenant"></a>
<a id="minio-k8s-expand-minio-tenant"></a>

本步骤说明如何通过在 Kubernetes 基础设施中部署额外的一组 MinIO pod，来扩展现有 MinIO tenant 的可用存储容量。

> [!WARNING]
> **重要**
>
> MinIO Operator Console 已被弃用，并在 Operator 6.0.0 中移除。
>
> 有关将通过 Operator Console 安装的 Tenant 迁移到 Kustomization 的说明，请参阅 [修改 MinIO Tenant](/docs/operations/deployments/k8s-modify-minio-tenant-on-kubernetes/#minio-k8s-modify-minio-tenant)。

## 前提条件 {#id2}

### MinIO Kubernetes Operator {#minio-kubernetes-operator}

本页步骤 *要求* 已有一个有效的 MinIO Kubernetes Operator 安装，并假定本地主机也安装了与之匹配的 Operator。本页使用仓库归档前的最终上游版本 `v7.1.1`，仅作为冻结的兼容基线。

有关部署 MinIO Operator 的完整文档，请参阅 [在 Kubernetes 上部署 MinIO](/docs/operations/deployments/kubernetes/#deploy-operator-kubernetes)。

### 可用 Worker Nodes {#worker-nodes}

MinIO 会为新的 Tenant pool 部署额外的 [`minio server`](/docs/reference/minio-server/#command-minio.server) pod。 Kubernetes 集群 *必须* 具备足够的可用 worker node 来调度这些新 pod。

MinIO Operator 提供了用于控制 pod affinity 和 anti-affinity 的配置，以便将调度定向到特定 worker。

### 持久卷 {#id3}

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

MinIO 可以使用任何支持 [ReadWriteOnce](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) 访问模式的 Kubernetes [Persistent Volume (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes)。 MinIO 的一致性保证依赖于 `ReadWriteOnce` 提供的独占存储访问。

对于节点具有 Direct Attached Storage 的 Kubernetes 集群，MinIO 强烈建议使用 [DirectPV CSI driver](https://min.io/directpv?ref=docs)。 DirectPV 提供了一个分布式持久卷管理器，可在 Kubernetes 节点之间发现、格式化、挂载、调度和监控驱动器。 DirectPV 解决了手动配置和监控 [local persistent volumes](https://kubernetes.io/docs/concepts/storage/volumes/#local) 的局限性。

> [!NOTE]
> **说明**
>
> EKS 上的 MinIO Tenant 必须使用 [EBS CSI Driver](https://github.com/kubernetes-sigs/aws-ebs-csi-driver) 来预配所需的底层持久卷。 MinIO 强烈建议使用基于 SSD 的 EBS 卷以获得最佳性能。 有关 EBS 资源的更多信息，请参阅 [EBS Volume Types](https://aws.amazon.com/ebs/volume-types/)。

## 步骤 {#id4}

MinIO Operator 支持通过添加额外 pool 来扩展 MinIO Tenant。

{{< tabs group="kustomization-helm" >}}
{{< tab label="Kustomization" value="kustomization" >}}
1. 检查描述 Tenant 对象（`tenant.yaml`）的 Kustomization 对象。

   `spec.pools` 数组描述当前的 pool 拓扑。
2. 在 `spec.pools` 数组中新增一个条目。

   新 pool 必须反映你期望的 Worker node、每个 server 的卷数量、存储类以及 affinity/scheduler 设置组合。 有关与 Pool 相关配置项的更完整文档，请参阅 [MinIO 自定义资源定义](/docs/reference/operator-crd/#minio-operator-crd)。
3. 应用更新后的 Tenant 配置

   使用 `kubectl apply` 命令更新 Tenant：

   ```shell
   kubectl apply -k ~/kustomization/TENANT-NAME
   ```

   请根据本地配置修改 Kustomization 目录路径。
{{< /tab >}}
{{< tab label="Helm" value="helm" >}}
1. 检查 Helm `values.yaml` 文件。

   `tenant.pools` 数组描述当前的 pool 拓扑。
2. 在 `tenant.pools` 数组中新增一个条目。

   新 pool 必须反映你期望的 Worker node、每个 server 的卷数量、存储类以及 affinity/scheduler 设置组合。 有关与 Pool 相关配置项的更完整文档，请参阅 [租户 Helm Charts](/docs/reference/tenant-chart-values/#minio-tenant-chart-values)。
3. 应用更新后的 Tenant 配置

   使用 `helm upgrade` 命令更新 Tenant：

   ```shell
   helm upgrade TENANT-NAME minio-operator/tenant -f values.yaml -n TENANT-NAMESPACE
   ```

   上述命令默认使用的是 MinIO Operator Chart 仓库。 如果你是手动安装 Chart，或使用了不同的仓库名称，请在命令中指定相应的 chart 或名称。

   分别将 `TENANT-NAME` 和 `TENANT-NAMESPACE` 替换为 Tenant 的名称和命名空间。 你可以使用 `helm list -n TENANT-NAMESPACE` 验证 Tenant 名称。
{{< /tab >}}
{{< /tabs >}}

你可以使用 `kubectl get events -n TENANT-NAMESPACE --watch` 监控扩容进度。 MinIO Operator 会更新 service，以便在新节点之间正确路由连接。 如果你使用了自定义 service、route、ingress 或类似 Kubernetes 网络组件，可能还需要针对新的 pod 主机名范围更新这些组件。