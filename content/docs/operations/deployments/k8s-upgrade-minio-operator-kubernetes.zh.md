---
title: "升级 MinIO Operator"

weight: 20
---

<a id="minio-operator"></a>
<a id="minio-k8s-upgrade-minio-operator"></a>

你可以随时升级 MinIO Operator，而不会影响其管理的 MinIO Tenant。

在升级过程中，Operator 可能会更新并重启 Tenant，以支持 MinIO 自定义资源定义（CRD）的变更。 这些变更不需要操作员或管理员采取额外操作，也不会影响 Tenant 的运行。

本页说明如何将 Operator 从 5.0.15 升级到 7.1.1。 如果在开始本流程前需要先升级到 Operator 5.0.15，请参阅 [将 MinIO Operator 4.5.8 及更高版本升级到 5.0.15](/docs/operations/deployments/k8s-upgrade-minio-operator-4.5.7-earlier/#minio-k8s-upgrade-minio-operator-to-5-0-15)。

> [!NOTE]
> **Operator 6.0.0 弃用 Operator Console**
>
> 从 Operator 6.0.0 开始，MinIO Operator Console 已被弃用并移除。
>
> 你可以继续使用 Kustomize 或 Helm 等标准 Kubernetes 方式来管理和部署 MinIO Tenant。

<a id="minio-k8s-upgrade-minio-operator-procedure"></a>

## 将 MinIO Operator 从 5.0.15 升级到 7.1.1 {#minio-operator-5-0-15-operator-version-stable}

> [!WARNING]
> **重要**
>
> Operator 6.0.0 弃用 MinIO Operator Console，并从 MinIO Operator CRD 中移除相关资源。 其中包括 Operator Console 的 service、pod 等资源。
>
> 后续请改用 Kustomize 或 Helm 来管理 Tenant。

{{< tabs group="kustomize-helm" >}}
{{< tab label="使用 Kustomize 升级" value="kustomize" >}}
以下步骤使用 Kustomize 升级 MinIO Operator。 对于使用 Operator 5.0.0 到 5.0.14 的部署，请先按照 [将 MinIO Operator 4.5.8 及更高版本升级到 5.0.15](/docs/operations/deployments/k8s-upgrade-minio-operator-4.5.7-earlier/#minio-k8s-upgrade-minio-operator-to-5-0-15) 完成升级，再执行本流程。

如果你是通过 [Helm](/docs/operations/deployments/k8s-deploy-operator-helm-on-kubernetes/#minio-k8s-deploy-operator-helm) 安装 Operator，请改用 **使用 Helm 升级** 步骤。

1. *(可选)* 将每个 MinIO Tenant 升级到最新稳定版 MinIO。

   定期升级 MinIO 可确保 Tenant 获得最新特性和性能改进。 在将升级应用到生产 Tenant 之前，请先在 Dev 或 QA Tenant 等较低环境中验证。 升级 MinIO Tenant 的具体流程请参阅 [升级 MinIO Tenant](/docs/operations/deployments/k8s-upgrade-minio-tenant-on-kubernetes/#minio-k8s-upgrade-minio-tenant)。
2. 验证现有 Operator 安装。 使用 `kubectl get all -n minio-operator` 验证所有 Operator pod 和 service 的健康状态与运行状态。

   如果你将 Operator 安装到了自定义命名空间，请在命令中指定 `-n <NAMESPACE>`。

   你可以通过获取该命名空间中某个 operator pod 的对象规范，确认当前安装的 Operator 版本。 以下示例使用 `jq` 工具从 `kubectl` 输出中过滤出所需信息：

   ```shell
   kubectl get pod -l 'name=minio-operator' -n minio-operator -o json | jq '.items[0].spec.containers'
   ```

   输出类似如下：

   ```json
   {
      "env": [
         {
            "name": "CLUSTER_DOMAIN",
            "value": "cluster.local"
         }
      ],
      "image": "minio/operator:v5.0.15",
      "imagePullPolicy": "IfNotPresent",
      "name": "minio-operator"
   }
   ```

   如果本地主机未安装 `jq`，你也可以只执行命令的前半部分，然后在输出中查找 `spec.containers` 段落。
3. 使用 Kustomize 升级 Operator

   以下命令会将 Operator 升级到 7.1.1：

   ```shell
   kubectl apply -k github.com/minio/operator
   ```

   在下面的示例输出中，`configured` 表示更新后的 CRD 已应用对应变更：

   ```shell
   namespace/minio-operator unchanged
   customresourcedefinition.apiextensions.k8s.io/miniojobs.job.min.io configured
   customresourcedefinition.apiextensions.k8s.io/policybindings.sts.min.io configured
   customresourcedefinition.apiextensions.k8s.io/tenants.minio.min.io configured
   serviceaccount/minio-operator unchanged
   clusterrole.rbac.authorization.k8s.io/minio-operator-role configured
   clusterrolebinding.rbac.authorization.k8s.io/minio-operator-binding unchanged
   service/operator unchanged
   service/sts unchanged
   deployment.apps/minio-operator configured
   ```

4. 验证 Operator 升级结果

   你可以使用前面相同的 `kubectl` 命令检查新的 Operator 版本：

   ```shell
   kubectl get pod -l 'name=minio-operator' -n minio-operator -o json | jq '.items[0].spec.containers'
   ```
{{< /tab >}}
{{< tab label="使用 Helm 升级" value="helm" >}}
以下步骤使用 Helm 升级现有的 MinIO Operator 安装。

如果你是使用 Kustomize 安装 Operator，请改用 **使用 Kustomize 升级** 步骤。

1. *(可选)* 将每个 MinIO Tenant 升级到最新稳定版 MinIO。

   定期升级 MinIO 可确保 Tenant 获得最新特性和性能改进。 在将升级应用到生产 Tenant 之前，请先在 Dev 或 QA Tenant 等较低环境中验证。 升级 MinIO Tenant 的具体流程请参阅 [升级 MinIO Tenant](/docs/operations/deployments/k8s-upgrade-minio-tenant-on-kubernetes/#minio-k8s-upgrade-minio-tenant)。
2. 验证现有 Operator 安装。

   使用 `kubectl get all -n minio-operator` 验证所有 Operator pod 和 service 的健康状态与运行状态。

   如果你将 Operator 安装到了自定义命名空间，请在命令中指定 `-n <NAMESPACE>`。

   使用 `helm list` 查看该命名空间中已安装的 chart：

   ```shell
   helm list -n minio-operator
   ```

   结果应类似如下：

   ```shell
   NAME            NAMESPACE       REVISION        UPDATED                                 STATUS          CHART           APP VERSION
   operator        minio-operator  1               2023-11-01 15:49:54.539724775 -0400 EDT deployed        operator-5.0.x v5.0.x
   ```

3. 更新 Operator 仓库

   使用 `helm repo update minio-operator` 更新 MinIO Operator 仓库。 如果你为 MinIO Operator 仓库设置了不同别名，请在命令中使用该别名替代 `minio-operator`。 你可以使用 `helm repo list` 查看当前已安装的仓库。

   更新 Operator 仓库后，使用 `helm search` 检查最新可用的 chart 版本：

   ```shell
   helm search repo minio-operator
   ```

   返回结果应类似如下：

   ```shell
   NAME                            CHART VERSION   APP VERSION     DESCRIPTION
   minio-operator/minio-operator   4.3.7           v4.3.7          A Helm chart for MinIO Operator
   minio-operator/operator         7.1.1          v7.1.1         A Helm chart for MinIO Operator
   minio-operator/tenant           7.1.1          v7.1.1         A Helm chart for MinIO Operator
   ```

   `minio-operator/minio-operator` 是旧版 chart，正常情况下 **不应** 安装。
4. 运行 `helm upgrade`

   Helm 会使用最新 chart 升级 MinIO Operator：

   ```shell
   helm upgrade -n minio-operator \
   operator minio-operator/operator
   ```

   如果你将 MinIO Operator 安装到了其他命名空间，请在 `-n` 参数中指定该命名空间。

   如果你使用的安装名不是 `operator`，请将上面的值替换为实际安装名。

   命令应返回成功，并且 `REVISION` 值会递增。
5. 验证 Operator 升级结果

   你可以使用前面相同的 `kubectl` 命令检查新的 Operator 版本：

   ```shell
   kubectl get pod -l 'name=minio-operator' -n minio-operator -o json | jq '.items[0].spec.containers'
   ```
{{< /tab >}}
{{< /tabs >}}