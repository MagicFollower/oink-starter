---
title: "升级 Silo Tenant"

weight: 40
---

<a id="minio-tenant"></a>
<a id="minio-k8s-upgrade-minio-tenant"></a>

以下步骤用于使用 Kustomize 或 Helm 升级单个 Silo Tenant。请先在非生产 Tenant 中测试确切的服务端镜像、Operator/Chart 版本与回滚流程。

> [!CAUTION]
> 服务端镜像必须保持为 `pgsty/silo`，并仅使用 [Silo 下载页](/zh/download/#server) 已发布的标签或摘要。上游 Tenant 默认值使用 MinIO 镜像。同时保留 `MINIO_UPDATE=off`；继承的原地更新器仍指向上游 MinIO 发布源，不是 Silo 升级路径。

> [!WARNING]
> **重要**
>
> 对于使用早于 [RELEASE.2024-03-30T09-41-56Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-03-30T09-41-56Z) 的 MinIO Image 且启用了 [AD/LDAP](/docs/reference/minio-server/settings/iam/ldap/#minio-ldap-config-settings) 的 Tenant，在开始本步骤前，你 **必须** 先完整阅读 [RELEASE.2024-04-18T19-09-19Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-04-18T19-09-19Z) 的发布说明。 你必须将该发布说明中记录的额外步骤纳入升级过程。

<a id="minio-upgrade-tenant-kustomize"></a>
<a id="minio-upgrade-tenant-plugin"></a>

## 使用 Kustomize 升级 Tenant {#kustomize-tenant}

以下步骤使用 Kustomize 和 `kubectl` CLI 升级 MinIO Tenant。 如果你是使用 [Helm](/docs/operations/deployments/k8s-deploy-minio-tenant-helm-on-kubernetes/#deploy-tenant-helm) 部署 Tenant，请改用 [使用 MinIO Helm Chart 升级 Tenant](#minio-upgrade-tenant-helm) 步骤。

若要使用 Kustomize 升级 Tenant：

如果 Tenant 是通过 Operator Console 部署的，则在升级前还需要额外步骤来创建基础配置文件。

如果 Tenant 是通过 Kustomize 部署的，则基础配置就是原始 Tenant 部署中已有的 `kustomization` 文件。

请根据 Tenant 的部署方式选择下方标签页：

{{< tabs group="tabs-ff01f39e" default="operator-console-deployed-tenant" >}}
{{< tab label="Operator Console-Deployed Tenant" value="operator-console-deployed-tenant" >}}
1. 创建基础配置文件：

   1. 在一个合适的目录中，使用 `kubectl get` 将当前 Tenant 配置保存到文件：

      > ```shell
      > kubectl get tenant/my-tenant -n my-tenant-ns -o yaml > my-tenant-base.yaml
      > ```
      >
      > 将 `my-tenant` 和 `my-tenant-ns` 替换为待升级 Tenant 的名称和命名空间。
      >
      > 编辑该文件，删除以下几行：
      >
      > - `creationTimestamp:`
      > - `resourceVersion:`
      > - `uid:`
      > - `selfLink:`（如果存在）
      >
      > 例如，删除高亮显示的这些行：
      >
      > ```shell
      > metadata:
      >   creationTimestamp: "2024-05-29T21:22:20Z"
      >   generation: 1
      >   name: my-tenant
      >   namespace: my-tenant-ns
      >   resourceVersion: "4699"
      >   uid: d5b8e468-3bed-4aa3-8ddb-dfe1ee0362da
      > ```

   2. 在同一目录中，创建一个 `kustomization.yaml` 文件，其内容类似如下：

      ```shell
      apiVersion: kustomize.config.k8s.io/v1beta1
      kind: Kustomization

      resources:
      - my-tenant-base.yaml

      patches:
      - path: upgrade-minio-tenant.yaml
      ```

      如果你在上一步为 `kubectl get` 输出使用了不同的文件名，请将 `my-tenant-base.yaml` 替换为对应文件名。
{{< /tab >}}
{{< tab label="现有 Kustomize 部署 Tenant" value="kustomize-tenant" >}}
1. 你可以使用原始部署中的 `kustomization` 文件作为基础配置来升级 Tenant。 如果你已经没有这些文件，请按照 Operator Console-Deployed Tenant 标签页中的说明操作。
{{< /tab >}}
{{< /tabs >}}

2. 创建一个 `upgrade-minio-tenant.yaml` 文件，其内容类似如下：

```shell
apiVersion: minio.min.io/v2
kind: Tenant

metadata:
  name: my-tenant
  namespace: my-tenant-ns

spec:
  image: pgsty/silo:RELEASE.2026-09-03T13-18-01Z
  env:
    - name: MINIO_UPDATE
      value: "off"
```

该文件会指示 Kustomize 使用指定镜像升级 Tenant。 该文件名 `upgrade-minio-tenant.yaml` 必须与上一步创建的 `kustomization.yaml` 中 `patches.path` 指定的文件名一致。

将 `my-tenant` 和 `my-tenant-ns` 替换为待升级 Tenant 的名称和命名空间。仅当更新的 Silo 发布已公开发布且经过验证时，才替换示例镜像标签。

或者，你也可以按照本地流程直接更新基础配置。 更多信息请参阅 [Kustomize Documentation](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization)。

3. 在与上述文件相同的目录中，使用 `kubectl apply` 将更新后的配置应用到 Tenant：

> ```shell
> kubectl apply -k ./
> ```
>
> 输出类似如下：
>
> ```shell
> tenant.minio.min.io/my-tenant configured
> ```

<a id="minio-upgrade-tenant-helm"></a>

## 使用 MinIO Helm Chart 升级 Tenant {#minio-helm-chart-tenant}

本步骤使用 Helm Charts 升级现有 MinIO Tenant。

如果你是通过 Kustomize 部署 Tenant，请改用 [使用 Kustomize 升级 Tenant](#minio-upgrade-tenant-kustomize) 步骤。

1. 验证现有 Silo Tenant 安装。

   使用 `kubectl get all -n TENANT_NAMESPACE` 验证所有 Tenant pod 和 service 的健康状态。

   使用 `helm list` 命令查看该命名空间中已安装的 chart：

   ```shell
   helm list -n TENANT_NAMESPACE
   ```

   结果应类似如下：

   ```shell
   NAME            NAMESPACE         REVISION        UPDATED                                 STATUS          CHART           APP VERSION
   CHART_NAME      TENANT_NAMESPACE  1               2023-11-01 15:49:58.810412732 -0400 EDT deployed        tenant-5.0.x   v5.0.x
   ```

2. 更新 Operator 仓库

   使用 `helm repo update minio-operator` 更新 MinIO Operator 仓库。 如果你为 MinIO Operator 仓库设置了不同的别名，请在命令中指定该别名。 你可以使用 `helm repo list` 查看已安装的仓库列表。

   在更新 Operator 仓库后，使用 `helm search` 检查最新可用的 chart 版本：

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
3. 保留并审查 Tenant values

   导出当前发布由用户提供的 values，然后确认该文件保留了所有拓扑、存储、TLS、凭据与调度设置：

   ```shell
   helm get values CHART_NAME -n TENANT_NAMESPACE -o yaml > values.yaml
   ```

   将 `tenant.image.repository` 设为 `pgsty/silo`，将 `tenant.image.tag` 固定为经测试的已发布 Silo 版本，并确保 `tenant.env` 包含 `MINIO_UPDATE=off`。不得让 Chart 升级默默恢复上游镜像默认值。

4. 运行已固定的 `helm upgrade`

   Chart 版本与 Silo 服务端镜像应分别固定，并传入经过审查的 values 文件：

   ```shell
   helm upgrade -n TENANT_NAMESPACE \
     --version 7.1.1 \
     --values values.yaml \
     CHART_NAME minio-operator/tenant
   ```

   命令结果应返回成功，并且 `REVISION` 值会递增。
5. 验证 Tenant 升级

   检查所有 service 和 pod 是否都已在线，确认实际运行的镜像摘要，并执行经过认证的 S3 读写冒烟测试后再完成发布。