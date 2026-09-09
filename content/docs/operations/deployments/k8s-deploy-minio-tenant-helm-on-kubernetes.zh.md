---
title: "使用 Helm Charts 部署 Silo Tenant"

weight: 20
---

<a id="helm-charts-minio-tenant"></a>
<a id="deploy-tenant-helm"></a>

## 概览 {#id2}

Helm 是一个用于将应用自动部署到 Kubernetes 集群的工具。 [Helm chart](https://helm.sh/docs/topics/charts/) 是一组定义部署细节的 YAML 文件、模板和其他文件。 以下步骤使用 Helm Chart 部署由 MinIO Operator 管理的 Tenant。

本步骤要求 Kubernetes 集群中已存在一个有效的 [Operator](/docs/operations/deployments/kubernetes/#deploy-operator-kubernetes) 部署。 你不能使用 MinIO Operator Tenant chart 在脱离 Operator 的情况下独立部署 Tenant。

> [!WARNING]
> **重要**
>
> MinIO Operator Tenant Chart 与服务端仓库中的旧社区 [MinIO Chart](https://github.com/minio/minio/tree/master/helm/minio) *不同*。本指南使用 Operator Tenant Chart，因为它提供明确的 Tenant 镜像覆盖。上游 Operator 仓库已于 2026 年 3 月 20 日归档，因此本文固定其最终 `v7.1.1` Chart，仅作为冻结的兼容基线；Silo 不继承上游厂商的支持承诺。

## 前提条件 {#id3}

要使用 Helm 安装 MinIO Tenant，你必须满足以下要求：

- 一个现有的 Kubernetes 集群
- 本地主机上安装了与集群版本匹配的 `kubectl` CLI 工具
- [Helm](https://helm.sh/docs/intro/install/) 3.8 或更高版本
- [yq](https://github.com/mikefarah/yq/#install) 4.18.1 或更高版本
- 一个现有的 [MinIO Operator 安装](/docs/operations/deployments/kubernetes/#deploy-operator-kubernetes)

本步骤默认你对 Kubernetes 集群的访问权限具备较广泛的管理能力。

有关 Tenant 安装要求的更多信息，包括受支持的 Kubernetes 版本和 TLS 证书，请参阅 [Tenant 部署前提条件](/docs/operations/checklists/hardware/#minio-hardware-checklist-storage)。

本步骤默认你已经熟悉相关 Kubernetes 概念和工具。 虽然本文档可能会以 best-effort 方式提供 Kubernetes 相关资源的配置或部署指导，但它不能替代官方 [Kubernetes Documentation](https://kubernetes.io/docs/)。

### 命名空间 {#id4}

租户必须使用自己的命名空间，不能与其他租户共享命名空间。 此外，MinIO 强烈建议为租户使用专用命名空间，且该命名空间内不要运行其他应用。

<a id="id5"></a>

## 使用 Helm Charts 部署 Silo Tenant {#deploy-tenant-helm-repo}

以下步骤使用 MinIO Operator Chart Repository 部署 MinIO Tenant。 与 [本地 chart 安装](#deploy-tenant-helm-local) 相比，这种方式的安装路径更简单。

以下步骤使用 Helm 通过已归档上游项目的 `v7.1.1` Tenant Chart 部署 MinIO Tenant。

> [!WARNING]
> **重要**
>
> 如果你使用 Helm 部署 MinIO Tenant，就必须使用 Helm 来管理或升级该部署。 不要使用 `kubectl krew`、Kustomize 或类似方式来管理或升级 MinIO Tenant。

本步骤并未穷尽 [Tenant Chart](/docs/reference/tenant-chart-values/#minio-tenant-chart-values) 中所有可能的配置项。 它只提供一个基线，你可以在此基础上按需修改和定制 Tenant。

1. 验证 MinIO Operator Repo 配置

   已归档项目的端点 [https://operator.min.io](https://operator.min.io) 当前仍提供 `v7.1.1` Chart。 如果该仓库尚未存在于本地 Helm 配置中，请先添加后再继续：

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

2. 创建 Helm `values.yaml` 的本地副本以供修改

   ```shell
   curl -sLo values.yaml https://raw.githubusercontent.com/minio/operator/v7.1.1/helm/tenant/values.yaml
   ```

   请使用文本编辑器打开 `values.yaml`。继续之前，替换上游服务端镜像默认值，并禁用继承的原地更新器：

   ```yaml
   tenant:
     image:
       repository: pgsty/silo
       tag: RELEASE.2026-09-03T13-18-01Z
       pullPolicy: IfNotPresent
     env:
       - name: MINIO_UPDATE
         value: "off"
   ```

   仅当更新标签已在 [Silo 下载页](/zh/download/#server) 发布，并通过你的部署验证后才应使用。Silo 生产环境的 values 文件不应保留 `quay.io/minio/minio` 或 `latest`。
3. 配置 Tenant 拓扑

   以下字段都带有 `tenant.pools[0]` 前缀，用于控制 Tenant 中所有 pod 的 server 数量、每个 server 的卷数量以及存储类：

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>servers</code></p></td>
         <td><p>要在 服务器池 中部署的 MinIO pod 数量。</p></td>
       </tr>
       <tr>
         <td><p><code>volumesPerServer</code></p></td>
         <td><p>每个 MinIO pod（<code>servers</code>）要挂载的持久卷数量。
   Operator 会为该 Tenant 生成 <code>volumesPerServer x servers</code> 个 Persistent Volume Claim。</p></td>
       </tr>
       <tr>
         <td><p><code>storageClassName</code></p></td>
         <td><p>与生成的 Persistent Volume Claim 关联的 Kubernetes 存储类。</p><p>如果不存在与指定值匹配的存储类，<em>或者</em> 指定的存储类无法满足所请求的 PVC 数量或存储容量，Tenant 可能无法启动。</p></td>
       </tr>
       <tr>
         <td><p><code>size</code></p></td>
         <td><p>为每个生成的 PVC 请求的存储容量。</p></td>
       </tr>
     </tbody>
   </table>
4. 配置 Tenant Affinity 或 Anti-Affinity

   Tenant Chart 支持以下 Kubernetes Selector、Affinity 和 Anti-Affinity 配置：

   - Node Selector (`tenant.nodeSelector`)
   - Node/Pod Affinity or Anti-Affinity (`spec.pools[n].affinity`)

   MinIO 建议为 Tenant 配置 Pod Anti-Affinity，以确保 Kubernetes 调度器不会将多个 pod 调度到同一个 worker node 上。

   如果你希望将租户部署到特定 worker node 上，请将对应的 node label 或过滤条件传入 `nodeSelector` 或 `affinity` 字段，以约束调度器仅在这些节点上放置 pod。
5. 配置网络加密

   MinIO Tenant CRD 提供了以下字段，你可以通过它们配置租户的 TLS 网络加密：

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>tenant.certificate.requestAutoCert</code></p></td>
         <td><p>启用或禁用 MinIO <a href="/docs/operations/network-encryption/#minio-tls">自动 TLS 证书生成</a>。</p><p>若省略该字段，默认值为 <code>true</code>，即启用。</p></td>
       </tr>
       <tr>
         <td><p><code>tenant.certificate.certConfig</code></p></td>
         <td><p>在启用的情况下，自定义 <a href="/docs/operations/network-encryption/#minio-tls">自动 TLS</a> 的行为。</p></td>
       </tr>
       <tr>
         <td><p><code>tenant.certificate.externalCertSecret</code></p></td>
         <td><p>通过 Server Name Indication (SNI) 为多个主机名启用 TLS。</p><p>指定一个或多个类型为 <code>kubernetes.io/tls</code> 或 <code>cert-manager</code> 的 Kubernetes secret。</p></td>
       </tr>
       <tr>
         <td><p><code>tenant.certificate.externalCACertSecret</code></p></td>
         <td><p>启用对由未知、第三方或内部 Certificate Authorities (CA) 签发的客户端 TLS 证书的校验。</p><p>指定一个或多个类型为 <code>kubernetes.io/tls</code> 的 Kubernetes secret，其中包含某个 CA 的完整证书链。</p></td>
       </tr>
     </tbody>
   </table>
6. 配置 Silo 环境变量

   你可以使用 `tenant.configuration` 字段设置服务端 `MINIO_*` 环境变量。这些名称属于 MinIO 兼容契约，不得改名。

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>tenant.configuration</code></p></td>
         <td><p>指定一个 Kubernetes opaque secret，其数据负载 <code>config.env</code> 包含你希望设置的每一个 MinIO 环境变量。</p><p><code>config.env</code> 数据负载 <strong>必须</strong> 是一个 base64 编码字符串。
   你可以先创建一个本地文件，在其中设置环境变量，再通过 <code>cat LOCALFILE | base64</code> 生成该负载。</p></td>
       </tr>
     </tbody>
   </table>

   该 YAML 中包含一个 `kind: Secret` 且 `metadata.name: storage-configuration` 的对象，用于设置 root 用户名、密码、纠删码校验设置，以及启用 Tenant Console。

   请根据 Tenant 的实际需求修改这些值。
7. 部署 Tenant

   使用 `helm` 安装 Tenant Chart，并将 `values.yaml` 作为覆盖配置：

   ```shell
   helm install \
   --namespace TENANT-NAMESPACE \
   --create-namespace \
   --version 7.1.1 \
   --values values.yaml \
   TENANT-NAME minio-operator/tenant
   ```

   你可以使用以下命令监控进度：

   ```shell
   watch kubectl get all -n TENANT-NAMESPACE
   ```

8. 暴露 Tenant 的 MinIO S3 API 端口

   若要在本地机器上测试 MinIO Client [`mc`](/docs/reference/minio-mc/#command-mc)，请转发 MinIO 端口并创建别名。

   - 转发 Tenant 的 MinIO 端口：

   ```shell
   kubectl port-forward svc/TENANT-NAME-hl 9000 -n TENANT-NAMESPACE
   ```

   - 为 Tenant 服务创建别名：

   ```shell
   mc alias set myminio https://localhost:9000 minio minio123 --insecure
   ```

   你可以使用 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 在 Tenant 上创建存储桶：

   ```shell
   mc mb myminio/mybucket --insecure
   ```

   如果你为 MinIO Tenant 部署的是由受信任 Certificate Authority (CA) 签发的 TLS 证书，则可以省略 `--insecure` 参数。

   有关连接 Tenant 的更多文档，请参阅 [连接到 Tenant](/docs/operations/deployments/k8s-deploy-minio-tenant-on-kubernetes/#create-tenant-connect-tenant)。

<a id="deploy-tenant-helm-local"></a>

## 使用本地 Helm Chart 部署 Tenant {#helm-chart-tenant}

以下步骤使用 Helm Charts 的本地副本部署 Tenant。 与 [基于仓库的安装](#deploy-tenant-helm-repo) 相比，这种方式可能更便于在安装前完成 Tenant 预配置。

1. 下载 Helm charts

   在本地主机上拉取已固定的 Tenant Chart，并将默认 values 提取为单独覆盖文件：

   ```shell
   helm pull minio-operator/tenant --version 7.1.1
   helm show values tenant-7.1.1.tgz > values.yaml
   ```

   每个 chart 都包含一个可按需定制的 `values.yaml` 文件。 有关 MinIO Tenant `values.yaml` 可用选项的详细信息，请参阅 [租户 Helm Charts](/docs/reference/tenant-chart-values/#minio-tenant-chart-values)。

   请使用文本编辑器打开 `values.yaml`：将 `tenant.image.repository` 设为 `pgsty/silo`，将 `tenant.image.tag` 固定为已发布 Silo 版本，并在 `tenant.env` 中加入 `MINIO_UPDATE=off`，与 [基于仓库的流程](#deploy-tenant-helm-repo) 中的示例一致。
2. 配置 Tenant 拓扑

   以下字段都带有 `tenant.pools[0]` 前缀，用于控制 Tenant 中所有 pod 的 server 数量、每个 server 的卷数量以及存储类：

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>servers</code></p></td>
         <td><p>要在 服务器池 中部署的 MinIO pod 数量。</p></td>
       </tr>
       <tr>
         <td><p><code>volumesPerServer</code></p></td>
         <td><p>每个 MinIO pod（<code>servers</code>）要挂载的持久卷数量。
   Operator 会为该 Tenant 生成 <code>volumesPerServer x servers</code> 个 Persistent Volume Claim。</p></td>
       </tr>
       <tr>
         <td><p><code>storageClassName</code></p></td>
         <td><p>与生成的 Persistent Volume Claim 关联的 Kubernetes 存储类。</p><p>如果不存在与指定值匹配的存储类，<em>或者</em> 指定的存储类无法满足所请求的 PVC 数量或存储容量，Tenant 可能无法启动。</p></td>
       </tr>
       <tr>
         <td><p><code>size</code></p></td>
         <td><p>为每个生成的 PVC 请求的存储容量。</p></td>
       </tr>
     </tbody>
   </table>
3. 配置 Tenant Affinity 或 Anti-Affinity

   Tenant Chart 支持以下 Kubernetes Selector、Affinity 和 Anti-Affinity 配置：

   - Node Selector (`tenant.nodeSelector`)
   - Node/Pod Affinity or Anti-Affinity (`spec.pools[n].affinity`)

   MinIO 建议为 Tenant 配置 Pod Anti-Affinity，以确保 Kubernetes 调度器不会将多个 pod 调度到同一个 worker node 上。

   如果你希望将租户部署到特定 worker node 上，请将对应的 node label 或过滤条件传入 `nodeSelector` 或 `affinity` 字段，以约束调度器仅在这些节点上放置 pod。
4. 配置网络加密

   MinIO Tenant CRD 提供了以下字段，你可以通过它们配置租户的 TLS 网络加密：

   | 字段 | 描述 |
   | --- | --- |
   | `tenant.certificate.requestAutoCert` | 启用或禁用 MinIO [自动 TLS 证书生成](/docs/operations/network-encryption/#minio-tls) |
   | `tenant.certificate.certConfig` | 控制 [自动 TLS](/docs/operations/network-encryption/#minio-tls) 的设置。 需要 `spec.requestAutoCert: true` |
   | `tenant.certificate.externalCertSecret` | 指定一个或多个类型为 `kubernetes.io/tls` 或 `cert-manager` 的 Kubernetes secret。 MinIO 会基于主机名（Server Name Indication）使用这些证书执行 TLS 握手。 |
   | `tenant.certificate.externalCACertSecret` | 指定一个或多个类型为 `kubernetes.io/tls` 的 Kubernetes secret，其中包含 Tenant 为允许客户端 TLS 连接而必须信任的 Certificate Authority (CA) 证书链。 |

5. 配置 Silo 环境变量

   你可以使用 `tenant.configuration` 字段设置服务端 `MINIO_*` 环境变量。这些名称仍属兼容契约。

   该字段必须指定一个 Kubernetes opaque secret，其数据负载 `config.env` 包含你希望设置的每一个 MinIO 环境变量。

   该 YAML 中包含一个 `kind: Secret` 且 `metadata.name: storage-configuration` 的对象，用于设置 root 用户名、密码、纠删码校验设置，以及启用 Tenant Console。

   请根据 Tenant 的实际需求修改这些值。
6. 以下 Helm 命令使用已固定的本地 Chart 与经审查 values 创建 Silo Tenant：

   ```shell
   helm install \
   --namespace TENANT-NAMESPACE \
   --create-namespace \
   --values values.yaml \
   TENANT-NAME tenant-7.1.1.tgz
   ```

   若要部署多个 Tenant，请创建一个包含新 Tenant 详细配置的 Helm chart，并重复上述部署步骤。 重新部署同一个 chart 会更新此前已部署的 Tenant。
7. 暴露 Tenant 的 MinIO 端口

   若要在本地机器上测试 MinIO Client [`mc`](/docs/reference/minio-mc/#command-mc)，请转发 MinIO 端口并创建别名。

   - 转发 Tenant 的 MinIO 端口：

     ```shell
     kubectl port-forward svc/TENANT-NAME-hl 9000 -n TENANT-NAMESPACE
     ```

   - 为 Tenant 服务创建别名：

     ```shell
     mc alias set myminio https://localhost:9000 minio minio123 --insecure
     ```

     该示例使用 HTTPS，但本地客户端可能不信任 Tenant 提供的证书，因此包含 `--insecure`。如果 Tenant 提供客户端信任的证书，请省略该参数。应确认当前 Tenant 实际生成的服务名，而不要假定固定为 `svc/minio`。

   你可以使用 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 在 Tenant 上创建存储桶：

   > ```shell
   > mc mb myminio/mybucket --insecure
   > ```

有关连接 Tenant 的更多文档，请参阅 [连接到 Tenant](/docs/operations/deployments/k8s-deploy-minio-tenant-on-kubernetes/#create-tenant-connect-tenant)。