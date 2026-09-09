---
title: "使用 Helm 部署 Operator"

weight: 10
---

<a id="helm-operator"></a>
<a id="minio-k8s-deploy-operator-helm"></a>

## 概览 {#id2}

Helm 是一个用于将应用自动部署到 Kubernetes 集群的工具。 [Helm chart](https://helm.sh/docs/topics/charts/) 是一组定义部署细节的 YAML 文件、模板和其他文件。 以下步骤使用 Helm Chart 将 [MinIO Kubernetes Operator](/docs/operations/deployments/kubernetes/#minio-operator-installation) 安装到 Kubernetes 集群中。

> [!WARNING]
> 上游 MinIO Operator 仓库已于 2026 年 3 月 20 日归档。本流程固定到其最终版本 `v7.1.1`，仅作为冻结的兼容基线；这不代表上游仍在维护或提供支持。用于生产环境前，请针对你的 Kubernetes 平台完成验证。

## 前提条件 {#id3}

基础要求请参阅 [Operator 前提条件](/docs/operations/deployments/k8s-minio-operator/#minio-operator-prerequisites)。 使用 Helm 安装还需要满足以下额外要求：

- [Helm](https://helm.sh/docs/intro/install/) 使用与你的 Kubernetes API 版本匹配的 Helm 版本。
- [yq](https://github.com/mikefarah/yq/#install)

有关 Operator 安装要求的更多信息，包括受支持的 Kubernetes 版本和 TLS 证书，请参阅 [Operator 部署前提条件](/docs/operations/deployments/k8s-minio-operator/#minio-operator-prerequisites)。

本步骤默认你已经熟悉相关 Kubernetes 概念和工具。 虽然本文档可能会以 best-effort 方式提供 Kubernetes 相关资源的配置或部署指导，但它不能替代官方 [Kubernetes Documentation](https://kubernetes.io/docs/)。

<a id="minio-k8s-deploy-operator-helm-repo"></a>

## 使用 Helm Charts 安装 MinIO Operator {#helm-charts-minio-operator}

以下步骤使用 MinIO Operator Chart Repository 安装 Operator。 与 [本地 chart 安装](#minio-k8s-deploy-operator-helm-local) 相比，这种方式的安装路径更简单。 安装完成后，你仍可继续修改 Operator 部署。

> [!WARNING]
> **重要**
>
> 如果你使用 Helm charts 安装 Operator，就必须使用 Helm 来管理该安装。 不要使用 `kubectl krew`、Kustomize 或类似方式更新或管理 MinIO Operator 安装。

1. 将 MinIO Operator Repo 添加到 Helm

   已归档项目的仓库端点 [https://operator.min.io](https://operator.min.io) 当前仍提供 `v7.1.1` Chart。将该仓库添加到 Helm：

   ```shell
   helm repo add minio-operator https://operator.min.io
   ```

   你可以使用 `helm search` 验证仓库内容：

   ```shell
   helm search repo minio-operator
   ```

   返回结果应类似如下：

   ```shell
   NAME                            CHART VERSION   APP VERSION     DESCRIPTION
   minio-operator/minio-operator   4.3.7           v4.3.7          A Helm chart for MinIO Operator
   minio-operator/operator         7.1.1           v7.1.1          A Helm chart for MinIO Operator
   minio-operator/tenant           7.1.1           v7.1.1          A Helm chart for MinIO Operator
   ```

   `minio-operator/minio-operator` 是旧版 chart，正常情况下 **不应** 安装。
2. 安装 Operator

   运行 `helm install` 命令安装 Operator。 以下命令会指定并创建一个专用命名空间 `minio-operator` 用于安装。 MinIO 强烈建议为 Operator 使用专用命名空间。

   ```shell
   helm install \
     --namespace minio-operator \
     --create-namespace \
     --version 7.1.1 \
     operator minio-operator/operator
   ```

3. 验证 Operator 安装

   检查指定命名空间（`minio-operator`）中的内容，确保所有 pod 和 service 均已成功启动。

   ```shell
   kubectl get all -n minio-operator
   ```

   返回结果应类似如下：

   ```shell
   NAME                                  READY   STATUS    RESTARTS   AGE
   pod/minio-operator-699f797b8b-th5bk   1/1     Running   0          25h
   pod/minio-operator-699f797b8b-nkrn9   1/1     Running   0          25h

   NAME               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
   service/operator   ClusterIP   10.43.44.204    <none>        4221/TCP            25h
   service/sts        ClusterIP   10.43.70.4      <none>        4223/TCP            25h

   NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
   deployment.apps/minio-operator   2/2     2            2           25h

   NAME                                        DESIRED   CURRENT   READY   AGE
   replicaset.apps/minio-operator-79f7bfc48    2         2         2       123m
   ```

现在你可以 [使用 Helm Charts 部署租户](/docs/operations/deployments/k8s-deploy-minio-tenant-helm-on-kubernetes/#deploy-tenant-helm)。

<a id="id4"></a>

## 使用本地 Helm Charts 安装 MinIO Operator {#minio-k8s-deploy-operator-helm-local}

以下步骤使用 Helm Charts 的本地副本安装 Operator。 与 [基于仓库的安装](#minio-k8s-deploy-operator-helm-repo) 相比，这种方式可能更便于在安装前完成 Operator 预配置。

1. 下载 Helm charts

   在本地主机上，将 Operator Helm charts 下载到一个合适的目录：

   ```shell
   curl -O https://operator.min.io/helm-releases/operator-7.1.1.tgz
   ```

2. （可选）修改 `values.yaml`

   该 chart 包含一个可按需定制的 `values.yaml` 文件。 有关 MinIO Operator `values.yaml` 可用选项的详细信息，请参阅 [Operator Helm 图表](/docs/reference/operator-chart-values/#minio-operator-chart-values)。

   例如，你可以修改 `operator.replicaCount` 的副本数，以增加或减少部署中的 pod 可用性。 有关 Operator Helm Chart 和 Values 的更完整文档，请参阅 [Operator Helm 图表](/docs/reference/operator-chart-values/#minio-operator-chart-values)。

   有关定制方式的更多信息，请参阅 [Helm Charts](https://helm.sh/docs/topics/charts/)。
3. 安装 Helm Chart

   使用 `helm install` 命令安装已下载的 Chart 归档文件。

   ```shell
   helm install \
   --namespace minio-operator \
   --create-namespace \
   minio-operator ./operator-7.1.1.tgz
   ```

4. 要验证安装，请运行以下命令：

   ```shell
   kubectl get all --namespace minio-operator
   ```

   如果你使用自定义命名空间初始化了 Operator，请将 `minio-operator` 替换为该命名空间。

   使用 Chart 默认值时，该命名空间中应包含一个具有两个就绪副本的 `minio-operator` Deployment、端口为 `4221` 的 `operator` ClusterIP Service，以及端口为 `4223` 的 `sts` ClusterIP Service。Pod 哈希、Cluster IP 与运行时长会因安装而异。

现在你可以 [使用 Helm Charts 部署租户](/docs/operations/deployments/k8s-deploy-minio-tenant-helm-on-kubernetes/#deploy-tenant-helm)。