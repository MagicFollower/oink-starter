---
title: "部署 Silo Tenant"

weight: 10
---

<a id="minio-tenant"></a>
<a id="deploy-minio-tenant-redhat-openshift"></a>
<a id="minio-k8s-deploy-minio-tenant"></a>

本步骤说明如何使用 MinIO Operator v7.1.1 管理运行 Silo 服务端镜像的 Tenant。上游 Operator 仓库已于 2026-03-20 归档并设为只读，因此这是一份冻结的兼容基线，而不是仍在维护的 Operator 路径。`MinIO Operator`、`Tenant`、`minio.min.io` API 组以及 CRD 字段名属于上游 Kubernetes 契约，因此保留原名。

下文验证过的基线会创建一个四服务端 Tenant。单节点拓扑适合本地测试，但其生产故障模型与存储布局不在本文档覆盖范围内。

本文档默认你已经熟悉所有被引用的 Kubernetes 概念、工具和操作流程。 虽然本文档 *可能* 会以 best-effort 方式提供 Kubernetes 相关资源的配置或部署指导，但它不能替代官方 [Kubernetes Documentation](https://kubernetes.io/docs/)。

<a id="minio-k8s-deploy-minio-tenant-security"></a>

## 使用 Kustomize 部署 Silo Tenant {#kustomize-minio-tenant}

以下步骤使用 [MinIO Operator v7.1.1 仓库](https://github.com/minio/operator/tree/v7.1.1/examples/kustomization/base) 中的 `base` Kustomization 模板，然后将其中默认的上游 MinIO 镜像替换为固定版本的 Silo 镜像。

你也可以从 v7.1.1 的其他 [示例](https://github.com/minio/operator/tree/v7.1.1/examples/kustomization/) 中选择起点，或者依据 [MinIO Custom Resource Documentation](/docs/reference/operator-crd/#minio-operator-crd) 自行构建资源。上游没有更晚的受支持版本；离开此固定快照前，应独立审查任何分支、替代实现或 CRD 变化。

> [!WARNING]
> **重要**
>
> 如果你使用 Kustomize 部署 MinIO Tenant，就必须使用 Kustomize 来管理或升级该部署。 不要使用 `kubectl krew`、Helm Chart 或类似方式来管理或升级该 MinIO Tenant。

本步骤并未穷尽 [Tenant CRD](/docs/reference/operator-crd/#minio-operator-crd) 中的所有可配置项。 它只提供一个基线，你可以在此基础上按需修改和定制 Tenant。

1. 为 Tenant 创建 YAML 对象

   克隆固定版本的 Operator，并使用 `kubectl kustomize` 生成一个 YAML 文件，其中包含部署 `base` Tenant 所需的全部 Kubernetes 资源：

   ```shell
   git clone --branch v7.1.1 --depth 1 https://github.com/minio/operator.git
   kubectl kustomize operator/examples/kustomization/base > tenant-base.yaml
   ```

   该命令会创建一个单独的 YAML 文件，多个对象之间使用 `---` 分隔。 请使用你偏好的编辑器打开此文件。

   上游模板默认使用 `quay.io/minio/minio`。应用前，请在 `kind: Tenant` 对象中把 `spec.image` 改为已验证的 Silo 版本，并关闭继承而来的原地更新器：

   ```yaml
   spec:
     image: pgsty/silo:RELEASE.2026-09-03T13-18-01Z
     env:
       - name: MINIO_UPDATE
         value: "off"
   ```

   请按标签或摘要固定镜像。若选择更新的 Silo 镜像，应单独审查并测试该版本，而不是沿用 Operator 模板中的上游镜像。

   下文各步骤将根据对象的 `kind` 和 `metadata.name` 字段来引用这些对象：
2. 配置 Tenant 拓扑

   `kind: Tenant` 对象用于描述由 MinIO Operator 管理的 Silo 工作负载。

   以下字段都带有 `spec.pools[0]` 前缀，用于控制 Tenant 中所有 pod 的 server 数量、每个 server 的卷数量以及存储类：

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
         <td><p>要在服务器池中部署的 Silo pod 数量。</p></td>
       </tr>
       <tr>
         <td><p><code>volumesPerServer</code></p></td>
         <td><p>每个 Silo pod（<code>servers</code>）要挂载的持久卷数量。
   Operator 会为该 Tenant 生成 <code>volumesPerServer x servers</code> 个 Persistent Volume Claim。</p></td>
       </tr>
       <tr>
         <td><p><code>volumeClaimTemplate.spec.storageClassName</code></p></td>
         <td><p>与生成的 Persistent Volume Claim 关联的 Kubernetes 存储类。</p><p>如果不存在与指定值匹配的存储类，<em>或者</em> 指定的存储类无法满足所请求的 PVC 数量或存储容量，Tenant 可能无法启动。</p></td>
       </tr>
       <tr>
         <td><p><code>volumeClaimTemplate.spec.resources.requests.storage</code></p></td>
         <td><p>为每个生成的 PVC 请求的存储容量。</p></td>
       </tr>
     </tbody>
   </table>
3. 配置 Tenant Affinity 或 Anti-Affinity

   MinIO Operator 支持以下 Kubernetes Affinity 和 Anti-Affinity 配置：

   - Node Affinity (`spec.pools[n].nodeAffinity`)
   - Pod Affinity (`spec.pools[n].podAffinity`)
   - Pod Anti-Affinity (`spec.pools[n].podAntiAffinity`)

   生产环境应为 Tenant 配置 Pod Anti-Affinity，避免 Kubernetes 调度器将多个 Tenant pod 放到同一个 worker node 上。

   如果你希望将 Tenant 部署到特定 worker node 上，请将对应的 node label 或过滤条件传入 `nodeAffinity` 字段，以约束调度器仅在这些节点上放置 pod。
4. 配置网络加密

   MinIO Tenant CRD 提供以下字段，用于配置 Tenant 的 TLS 网络加密：

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>spec.requestAutoCert</code></p></td>
         <td><p>启用或禁用 Silo <a href="/docs/operations/network-encryption/#minio-tls">自动 TLS 证书生成</a>。</p><p>若省略该字段，默认值为 <code>true</code>。</p></td>
       </tr>
       <tr>
         <td><p><code>spec.certConfig</code></p></td>
         <td><p>在启用的情况下，自定义 <a href="/docs/operations/network-encryption/#minio-tls">自动 TLS</a> 的行为。</p></td>
       </tr>
       <tr>
         <td><p><code>spec.externalCertSecret</code></p></td>
         <td><p>通过 Server Name Indication (SNI) 为多个主机名启用 TLS</p><p>指定一个或多个类型为 <code>kubernetes.io/tls</code> 或 <code>cert-manager</code> 的 Kubernetes secret。</p></td>
       </tr>
       <tr>
         <td><p><code>spec.externalCaCertSecret</code></p></td>
         <td><p>启用对由未知、第三方或内部 Certificate Authorities (CA) 签发的客户端 TLS 证书的校验。</p><p>指定一个或多个类型为 <code>kubernetes.io/tls</code> 的 Kubernetes secret，其中包含某个 CA 的完整证书链。</p></td>
       </tr>
     </tbody>
   </table>
5. 配置 Silo 环境变量

   Silo 保留上游 `MINIO_*` 环境变量契约。你可以通过 Tenant CRD 的 `spec.configuration` 字段所引用的 Secret 提供这些变量，也可以使用 `spec.env` 设置 `MINIO_UPDATE` 等单项变量。

   <table>
     <thead>
       <tr>
         <th><p>字段</p></th>
         <th><p>描述</p></th>
       </tr>
     </thead>
     <tbody>
       <tr>
         <td><p><code>spec.configuration.name</code></p></td>
         <td><p>指定一个 Kubernetes opaque Secret，其 <code>config.env</code> 键包含要设置的上游兼容环境变量。</p><p>按 v7.1.1 基础模板使用 <code>stringData.config.env</code> 时填写明文；若改用 <code>data.config.env</code>，其值必须经过 base64 编码。</p></td>
       </tr>
     </tbody>
   </table>

   该 YAML 中包含一个 `kind: Secret` 且 `metadata.name: storage-configuration` 的对象，用于设置 root 用户名、密码、纠删码校验设置，以及启用 Tenant Console。

   请根据 Tenant 的实际需求修改这些值。
6. 检查命名空间

   YAML 对象 `kind: Namespace` 将 Tenant 的默认命名空间设置为 `minio-tenant`。

   你可以修改该值，为 Tenant 创建不同的命名空间。 你必须同时修改 YAML 文件中 **所有** `metadata.namespace` 的值，使其与该命名空间保持一致。
7. 部署 Tenant

   使用 `kubectl apply -f` 命令部署 Tenant。

   ```shell
   kubectl apply -f tenant-base.yaml
   ```

   该命令会在配置好的命名空间中创建 YAML 对象里定义的每一项资源。

   你可以使用以下命令监控进度：

   ```shell
   watch kubectl get all -n minio-tenant
   ```

8. 暴露 Tenant 的 S3 API 端口

   若要在本地机器上测试 Silo 客户端 [`mc`](/docs/reference/minio-mc/#command-mc)，请转发 S3 API 端口并创建别名。

   - 转发 Tenant 的 S3 API 端口：

   ```shell
   kubectl port-forward svc/MINIO_TENANT_NAME-hl 9000 -n MINIO_TENANT_NAMESPACE
   ```

   - 为 Tenant 服务创建别名：

   ```shell
   mc alias set myminio https://localhost:9000 minio minio123 --insecure
   ```

   你可以使用 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 在 Tenant 上创建存储桶：

   ```shell
   mc mb myminio/mybucket --insecure
   ```

   如果你为 Tenant 部署的是由受信任 Certificate Authority (CA) 签发的 TLS 证书，则可以省略 `--insecure` 参数。

   具体说明请参阅 [连接到 Tenant](#create-tenant-connect-tenant)。

<a id="create-tenant-connect-tenant"></a>

## 连接到 Tenant {#tenant}

MinIO Operator 会为 Silo Tenant 创建 Kubernetes Service；这些生成名称仍属于 Operator 契约。

使用 `kubectl get svc -n NAMESPACE` 命令查看已部署的服务。 如果你的 Kubernetes 环境使用自定义的 `kubectl` 替代程序，也可以替换为对应程序名。

```shell
kubectl get svc -n minio-tenant-1
```

```shell
NAME                               TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
minio                              LoadBalancer   10.97.114.60     <pending>     443:30979/TCP    2d3h
TENANT-NAMESPACE-console           LoadBalancer   10.106.103.247   <pending>     9443:32095/TCP   2d3h
TENANT-NAMESPACE-hl                ClusterIP      None             <none>        9000/TCP         2d3h
```

- `minio` 服务暴露 Tenant S3 API。应用程序应通过该服务对 Silo 执行 S3 操作。
- `*-console` 服务暴露 [Silo Console](/docs/administration/minio-console/)。管理员可以通过该服务进行浏览器管理。

其余服务用于支撑 Tenant 内部操作，并不面向用户或管理员直接使用。

默认情况下，每个服务仅在 Kubernetes 集群内部可见。 部署在集群内部的应用可以通过 `CLUSTER-IP` 访问这些服务。

位于 Kubernetes 集群外部的应用可以通过 `EXTERNAL-IP` 访问这些服务。 该值只有在 Kubernetes 集群配置了 Ingress 或类似网络访问服务时才会被填充。 Kubernetes 提供了多种对 service 开放外部访问的方式。

有关如何配置 service 的外部访问，请参阅 Kubernetes 文档中的 [Publishing Services (ServiceTypes)](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) 和 [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)。

对于 OpenShift、Rancher 等特定 Kubernetes 发行版，请以其服务文档中关于对内或对外暴露 Service 的首选或可用方式为准。