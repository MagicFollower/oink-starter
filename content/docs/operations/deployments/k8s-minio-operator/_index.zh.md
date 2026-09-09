---
title: "MinIO Kubernetes Operator"

weight: 10
icon: fa-solid fa-dharmachakra
---

<a id="minio-kubernetes-operator"></a>
<a id="deploy-minio-operator"></a>

Silo 是兼容 S3 的对象存储。MinIO Operator 是上游 Kubernetes 组件，其仓库已于 2026-03-20 归档并设为只读。最后一个版本 `v7.1.1` 可以通过 Tenant CRD 管理 Silo 服务端镜像。Operator 名称、API 组、CRD kind、资源名、镜像名和环境变量都属于上游契约，因此不在此改名。

MinIO Operator 会安装 [Custom Resource Definition (CRD)](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions)，其中包括用于把托管对象存储工作负载描述为 Kubernetes [object](https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/) 的 `Tenant` kind。

固定的 v7.1.1 Kustomize 清单会在 `minio-operator` 命名空间部署一个 `minio-operator` Deployment，其中包含两个控制器副本；它不会部署独立的 Operator Console pod。

本站验证的是部署示例中的 Silo 镜像覆盖。归档后的 Operator 不再有持续的上游平台支持或商业支持承诺，本站也不会建立此类承诺。

上游 CRD 契约请参阅固定版本的 MinIO Operator v7.1.1 [CRD Reference](https://github.com/minio/operator/blob/v7.1.1/docs/tenant_crd.adoc)。

<a id="minio-operator-prerequisites"></a>

## Operator 前提条件 {#operator}

### Kubernetes 版本 {#kubernetes}

归档的 v7.1.1 README 要求 Kubernetes 1.30.0 或更高版本。请选择仍在维护且 API 兼容的 Kubernetes 版本，并在自己的集群中验证精确组合。可参阅 [受维护的 Kubernetes 版本](https://kubernetes.io/releases/) 与 [Operator v7.1.1 发布页](https://github.com/minio/operator/releases/tag/v7.1.1)；Silo 不另行声明更宽的平台支持矩阵。

如果 Kubernetes 基础设施运行的是生命周期已结束的 API 版本，在部署 Operator 时可能出现意料之外或不期望的行为。

### Kustomize 和 `kubectl` {#kustomize-kubectl}

[Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization) 是一个基于 YAML 的模板工具，可让你以声明式、可重复的方式定义 Kubernetes 资源。 Kustomize 已内置在 [kubectl](https://kubernetes.io/docs/reference/kubectl) 命令行工具中。

本步骤默认你的本地主机既安装了与 Kubernetes 集群版本匹配的 `kubectl`，也具备在该集群中创建新资源所需的访问权限。

固定版本的 [MinIO Operator v7.1.1 Kustomize 模板](https://github.com/minio/operator/blob/v7.1.1/kustomization.yaml) 提供了可复现的起点。你可以修改该 Kustomization 文件，或应用自己的 [patches](https://datatracker.ietf.org/doc/html/rfc6902) 适配集群。不要推断还存在受支持的上游新版；任何分支或替代实现都必须独立审查。

<a id="minio-k8s-deploy-operator-tls"></a>

### Kubernetes TLS Certificate API {#kubernetes-tls-certificate-api}

MinIO Operator 使用 Kubernetes `certificates.k8s.io` [TLS certificate management API](https://kubernetes.io/docs/tasks/tls/managing-tls-in-a-cluster/) 管理 TLS Certificate Signing Requests (CSR)，并在以下场景中创建已签名的 TLS 证书：

- 当启用 `autoCert` 时。
- 当 [`MINIO_CONSOLE_TLS_ENABLE`](/docs/reference/operator-environment-variables/#envvar.MINIO_CONSOLE_TLS_ENABLE) 环境变量设置为 `on` 时，用于 Tenant Console。
- 当 [`OPERATOR_STS_ENABLED`](/docs/reference/operator-environment-variables/#envvar.OPERATOR_STS_ENABLED) 环境变量设置为 `on` 时，用于 [STS service](/docs/developers/security-token-service/#minio-security-token-service)。
- 用于获取集群健康状态。

MinIO Operator 会读取 `operator-ca-tls` secret 中的证书，并在 tenant 命名空间内同步该 secret，以信任私有证书颁发机构，例如使用 cert-manager 时的场景。

在上述任一场景下，MinIO Operator 都 *要求* Kubernetes `kube-controller-manager` 的配置中包含以下 [配置项](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/#options)：

- `--cluster-signing-key-file` - 指定用于签发集群级证书的 PEM 编码 RSA 或 ECDSA 私钥。
- `--cluster-signing-cert-file` - 指定用于签发集群级证书的 PEM 编码 x.509 Certificate Authority 证书。

Kubernetes TLS API 会使用 CA 的签名算法生成新证书。与 RSA 相比，ECDSA（例如 [NIST P-256 curve](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)）或 EdDSA（例如 <a id="index-0"></a>[**Curve25519**](https://datatracker.ietf.org/doc/html/rfc7748.html)）通常需要更少的计算资源。Silo 服务端支持的套件请参阅 [支持的 TLS Cipher Suite](/docs/operations/network-encryption/#minio-tls-supported-cipher-suites)。

如果 Kubernetes 集群未配置为对生成的 <abbr title="Certificate Signing Request">CSR</abbr> 作出响应，Operator 将无法完成初始化。 某些 Kubernetes 提供方默认不会指定这些配置值。

若要检查 `kube-controller-manager` 是否指定了集群签名密钥和证书文件，请使用以下命令：

```shell
kubectl get pod kube-controller-manager-$CLUSTERNAME-control-plane \
  -n kube-system -o yaml
```

- 将 `$CLUSTERNAME` 替换为 Kubernetes 集群名称。

确认输出中包含高亮标出的行。 上例命令的输出可能与你终端中的实际输出不同：

```shell
 spec:
 containers:
 - command:
     - kube-controller-manager
     - --allocate-node-cidrs=true
     - --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf
     - --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf
     - --bind-address=127.0.0.1
     - --client-ca-file=/etc/kubernetes/pki/ca.crt
     - --cluster-cidr=10.244.0.0/16
     - --cluster-name=my-cluster-name
     - --cluster-signing-cert-file=/etc/kubernetes/pki/ca.crt
     - --cluster-signing-key-file=/etc/kubernetes/pki/ca.key
 ...
```

> [!WARNING]
> **重要**
>
> MinIO Operator 可以使用指定的 Certificate Authority (CA) 为 Tenant pod 生成 TLS 证书。Kubernetes 集群外部的客户端必须信任该 CA，才能连接到 Silo Tenant 端点。
>
> 禁用 TLS 校验仅适用于受控测试。生产客户端应信任签发 CA，或使用其本来就信任的 CA 所签发的证书。
>
> 另一种方式是生成由已知且受信任 CA 签发的 x.509 TLS 证书，并通过 Tenant CRD 提供这些证书。更完整的文档请参阅 [网络加密（TLS）](/docs/operations/network-encryption/#minio-tls)。