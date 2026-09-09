---
title: "使用 KES 进行服务端对象加密"

description: "为 Silo 部署服务端对象加密"
weight: 10
---

<a id="kes"></a>
<a id="minio-sse-aws"></a>
<a id="minio-sse-azure"></a>
<a id="minio-sse-gcp"></a>
<a id="minio-sse-vault"></a>

> [!WARNING]
> 社区版 KES 及其文档均已弃用并归档。下方 Kubernetes 页签还引用了在 MinIO Operator 6.0.0 中移除的 Operator Console；该内容仅作为历史迁移参考保留，并不是适用于当前 `v7.1.1` 的部署流程。新部署在启用不可逆的服务端加密前，应选择仍受维护的 KMS 集成，并验证迁移或替代方案。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
本流程假定你可以访问一个已经安装并启用了 MinIO Operator 的 Kubernetes 集群。 关于如何运行 KES，请参见 [KES 文档](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/getting-started.md)。

在本流程中，你将完成：

1. 创建或修改一个通过 <abbr title="Key Encryption Service">KES</abbr> 支持 <abbr title="Server-Side Encryption">SSE</abbr> 的 MinIO 部署。 关于生产可用 MinIO 部署的指导，请参见 [部署分布式 MinIO](/docs/operations/deployments/installation/#minio-mnmd) 教程。
2. 使用 MinIO Operator Console 创建或管理一个 MinIO 租户。
3. 进入该租户的 **Encryption** 设置，并通过 [受支持的 Key Management System](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets) 配置 <abbr title="Server-Side Encryption">SSE</abbr>。
4. 创建一个新的 <abbr title="External Key">EK</abbr> 供 <abbr title="Server-Side Encryption">SSE</abbr> 使用。
5. 配置自动化的存储桶默认 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms)。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
本流程说明如何部署已配置 KES 并启用 [服务端加密](/docs/operations/server-side-encryption/#minio-sse-data-encryption) 的 MinIO。 关于如何运行 KES，请参见 [KES 文档](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/getting-started.md)。

在本流程中，你将完成：

1. 创建一个新的 <abbr title="External Key">EK</abbr> 供 <abbr title="Server-Side Encryption">SSE</abbr> 使用。
2. 创建或修改一个通过 <abbr title="Key Encryption Service">KES</abbr> 支持 <abbr title="Server-Side Encryption">SSE</abbr> 的 MinIO 部署。 关于生产可用 MinIO 部署的指导，请参见 [部署分布式 MinIO](/docs/operations/deployments/installation/#minio-mnmd) 教程。
3. 配置自动化的存储桶默认 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms)
{{< /tab >}}
{{< /tabs >}}

> [!WARNING]
> **重要**
>
> 在 MinIO 部署上启用 <abbr title="Server-Side Encryption">SSE</abbr> 后， 会自动使用默认加密密钥对该部署的后端数据进行加密。
>
> MinIO 必须能够访问 KES 和外部 KMS， 才能解密后端并正常启动。 KMS 必须维护并提供对 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 的访问。 之后你不能再禁用 KES， 也不能在后续“撤销”该 <abbr title="Server-Side Encryption">SSE</abbr> 配置。

## 前提条件 {#id2}

### 访问 MinIO 集群 {#minio}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
你必须能够访问 Kubernetes 集群，并且 `kubectl` 上下文配置的权限至少具备管理员级别。

本流程假定你的权限集足以支持在 Kubernetes 集群中部署或修改与 MinIO 相关的资源，包括但不限于 pods、statefulsets、replicasets、deployments 和 secrets。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
本流程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 对 MinIO 集群执行操作。 请在一台能够访问该集群网络的机器上安装 `mc`。 关于如何下载和安装 `mc`，请参见 `mc` [安装快速开始](/docs/reference/minio-mc/#mc-install)。

本流程假定已为 MinIO 集群配置 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
{{< /tab >}}
{{< /tabs >}}

<a id="minio-sse-vault-prereq-vault"></a>

### 确保 KES 可访问受支持的 KMS 目标 {#kes-kms}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
本流程假定已经存在一个可从 Kubernetes 集群访问的 [受支持 KMS 安装](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets)。

- 对于与 MinIO 租户位于同一 Kubernetes 集群的部署，你可以使用 Kubernetes service 名称，让 MinIO 租户连接到目标 KMS 服务。
- 对于位于 Kubernetes 集群外部的部署，你必须确保该集群支持 Kubernetes services、pods 与外部网络之间的通信路由。 这可能需要配置或部署额外的 Kubernetes 网络组件，和/或启用访问公网的能力。

关于部署和配置的指导，请以你所选 KMS 方案的文档为准。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
本流程假定已经存在一个 KES 安装，并已连接到受支持的 <abbr title="Key Management System">KMS</abbr> 安装，且二者都可从本地主机访问。 请参照你所选 [受支持 KMS 目标](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets) 的安装说明，部署 KES 并将其连接到对应 KMS 方案。
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **KES 操作要求目标处于 Unsealed 状态**
>
> 某些受支持的 <abbr title="Key Management System">KMS</abbr> 目标允许你对 Vault 实例执行 seal 或 unseal。 如果已配置的 <abbr title="Key Management System">KMS</abbr> 服务处于 sealed 状态，KES 会返回错误。
>
> 如果你重启或以其他方式 seal 了 Vault 实例，KES 将无法针对该 Vault 执行任何密码学操作。 你必须对 Vault 执行 unseal，才能确保其正常运行。
>
> 关于是否需要执行 unseal 的更多信息，请参见你所选 <abbr title="Key Management System">KMS</abbr> 方案的文档。

对于你所选的受支持 <abbr title="Key Management System">KMS</abbr>，请参照 [KES 文档](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md) 中的配置说明：

- [AWS Secrets Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/aws-secrets-manager.md)
- [Azure KeyVault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/azure-keyvault.md)
- [Entrust KeyControl](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/entrust-keycontrol.md)
- [Fortanix SDKMS](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/fortanix-sdkms.md)
- [Google Cloud Secret Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/google-cloud-secret-manager.md)
- [HashiCorp Vault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/hashicorp-vault-keystore.md)
- [Thales CipherTrust Manager (formerly Gemalto KeySecure)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/thales-ciphertrust.md)

## 流程 {#id3}

本流程说明如何在生产环境中使用你所选的 [受支持 KMS 方案](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets) 配置并启用服务端加密。 具体来说，本流程假定满足以下条件：

- 已有一个生产级 KMS 目标
- 一个或多个已连接到该 KMS 目标的 KES 服务器
- 一个或多个用于新建或现有 MinIO 部署的主机

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
1. 查看 Tenant CRD

   查看 [Tenant CRD](/docs/reference/operator-crd/#minio-operator-crd) 中的 `TenantSpec.kes` 对象、 `TenantSpec.configuration` 对象，以及 [KES Configuration 参考](https://github.com/minio/kes/wiki/Configuration)。

   在继续之前，你必须先准备好所选外部 Key Management Service 所需的全部配置。
2. 创建或修改 Tenant YAML，按需设置 `KesConfig` 的值：

   你必须修改 Tenant YAML 或 `Kustomize` 模板，以反映所需的 KES 配置。以下示例摘自固定版本的 [MinIO Operator v7.1.1 Kustomize 示例](https://github.com/minio/operator/blob/v7.1.1/examples/kustomization/tenant-kes-encryption/tenant.yaml)。

   ```yaml
   kes:
      image: "" # minio/kes:2024-06-17T15-47-05Z
      env: [ ]
      replicas: 2
      kesSecret:
         name: kes-configuration
      imagePullPolicy: "IfNotPresent"
   ```

   `kes-configuration` secret 必须引用一个 Kubernetes Opaque Secret， 其中的 `stringData` 对象需要以 `server-config.yaml` 的形式包含完整 KES 配置。 `keystore` 字段必须包含你所选 Key Management System 的完整配置。

   更多说明请参阅 [固定到 `v7.1.1` 的 Kustomize 示例](https://github.com/minio/operator/blob/v7.1.1/examples/kustomization/tenant-kes-encryption/kes-configuration-secret.yaml)。
3. 创建或修改 Tenant YAML，按需设置 `TenantSpec.configuration` 的值。

   创建一个 Opaque Secret，在 `config.env` 键中写入 Tenant 所需的环境变量，再让 Tenant 按名称引用该 Secret。不要把真实的 root 凭据提交到源码仓库。

   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: storage-configuration
     namespace: minio-tenant
   type: Opaque
   stringData:
     config.env: |-
       export MINIO_ROOT_USER="replace-with-root-user"
       export MINIO_ROOT_PASSWORD="replace-with-a-strong-secret"
   ---
   apiVersion: minio.min.io/v2
   kind: Tenant
   spec:
     configuration:
       name: storage-configuration
   ```

   Secret 与 Tenant 必须位于同一个命名空间。上游对象结构见固定到 [`v7.1.1` 的 Tenant 配置示例](https://github.com/minio/operator/blob/v7.1.1/examples/kustomization/base/tenant-config.yaml)。
4. 生成新的加密密钥

   > [!NOTE]
   > **创建密钥前先解封 Vault**
   >
   > 如果你所选的提供方有此要求， 则必须先解封底层 Vault 实例， 然后才能创建新的加密密钥。 更多信息请参考你所选 KMS 方案的文档。

   MinIO 要求某个存储桶或对象使用的 <abbr title="External Key">EK</abbr> 在执行 <abbr title="Server-Side Encryption">SSE</abbr> 操作之前， 必须已经存在于根 KMS 中。 你可以针对 MinIO Tenant 使用 [`mc admin kms key create`](/docs/reference/minio-mc-admin/mc-admin-kms-key/#mc.admin.kms.key.create) 命令。

   在使用 [`mc`](/docs/reference/minio-mc/#command-mc) 管理 Tenant 之前， 你必须确保本地主机能够访问 MinIO Tenant 的 pods 和 services。 对于 Kubernetes 集群内部主机， 你可以使用 [service DNS name](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#a-aaaa-records)。 对于 Kubernetes 集群外部主机， 请指定通过 Ingress、Load Balancer 或类似 Kubernetes 网络控制组件暴露的服务主机名。

   在单独的 Terminal 或 Shell 中运行以下命令：

   ```shell
   # Replace '-n minio' with the namespace of the MinIO deployment
   # If you deployed the Tenant without TLS you may need to change the port range

   # You can validate the ports in use by running
   #  kubectl get svc/minio -n minio

   kubectl port forward svc/minio 443:443 -n minio
   ```

   在新的 Terminal 或 Shell 窗口中执行以下操作：

   - 将本地 [`mc`](/docs/reference/minio-mc/#command-mc) 客户端连接到 Tenant。
   - 创建加密密钥。

   关于如何在本地主机上安装 `mc`， 请参见 [快速开始](/docs/reference/minio-mc/#mc-install)。

   ```shell
   # Replace USERNAME and PASSWORD with a user on the tenant with administrative permissions
   # such as the root user

   mc alias add k8s https://localhost:443 ROOTUSER ROOTPASSWORD

   # Replace my-new-key with the name of the key you want to use for SSE-KMS
   mc admin kms key create k8s encrypted-bucket-key
   ```

5. 为存储桶启用 SSE-KMS

   你可以使用 MinIO Tenant Console 或 MinIO [`mc`](/docs/reference/minio-mc/#command-mc) CLI， 通过生成的密钥启用存储桶默认 SSE-KMS：

   {{< tabs group="minio-tenant-console-minio-cli" >}}
   {{< tab label="MinIO Tenant Console" value="minio-tenant-console" >}}
   连接到 [MinIO Tenant Console service](/docs/operations/deployments/k8s-deploy-minio-tenant-on-kubernetes/#create-tenant-connect-tenant) 并登录。 对于 Kubernetes 集群内部客户端， 你可以指定 [service DNS name](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#a-aaaa-records)。 对于 Kubernetes 集群外部客户端， 请指定通过 Ingress、Load Balancer 或类似 Kubernetes 网络控制组件暴露的服务主机名。

   登录后，新建一个 Bucket，并按你的偏好命名。 选择齿轮 <svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-gear" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M7.429 1.525a6.593 6.593 0 011.142 0c.036.003.108.036.137.146l.289 1.105c.147.56.55.967.997 1.189.174.086.341.183.501.29.417.278.97.423 1.53.27l1.102-.303c.11-.03.175.016.195.046.219.31.41.641.573.989.014.031.022.11-.059.19l-.815.806c-.411.406-.562.957-.53 1.456a4.588 4.588 0 010 .582c-.032.499.119 1.05.53 1.456l.815.806c.08.08.073.159.059.19a6.494 6.494 0 01-.573.99c-.02.029-.086.074-.195.045l-1.103-.303c-.559-.153-1.112-.008-1.529.27-.16.107-.327.204-.5.29-.449.222-.851.628-.998 1.189l-.289 1.105c-.029.11-.101.143-.137.146a6.613 6.613 0 01-1.142 0c-.036-.003-.108-.037-.137-.146l-.289-1.105c-.147-.56-.55-.967-.997-1.189a4.502 4.502 0 01-.501-.29c-.417-.278-.97-.423-1.53-.27l-1.102.303c-.11.03-.175-.016-.195-.046a6.492 6.492 0 01-.573-.989c-.014-.031-.022-.11.059-.19l.815-.806c.411-.406.562-.957.53-1.456a4.587 4.587 0 010-.582c.032-.499-.119-1.05-.53-1.456l-.815-.806c-.08-.08-.073-.159-.059-.19a6.44 6.44 0 01.573-.99c.02-.029.086-.075.195-.045l1.103.303c.559.153 1.112.008 1.529-.27.16-.107.327-.204.5-.29.449-.222.851-.628.998-1.189l.289-1.105c.029-.11.101-.143.137-.146zM8 0c-.236 0-.47.01-.701.03-.743.065-1.29.615-1.458 1.261l-.29 1.106c-.017.066-.078.158-.211.224a5.994 5.994 0 00-.668.386c-.123.082-.233.09-.3.071L3.27 2.776c-.644-.177-1.392.02-1.82.63a7.977 7.977 0 00-.704 1.217c-.315.675-.111 1.422.363 1.891l.815.806c.05.048.098.147.088.294a6.084 6.084 0 000 .772c.01.147-.038.246-.088.294l-.815.806c-.474.469-.678 1.216-.363 1.891.2.428.436.835.704 1.218.428.609 1.176.806 1.82.63l1.103-.303c.066-.019.176-.011.299.071.213.143.436.272.668.386.133.066.194.158.212.224l.289 1.106c.169.646.715 1.196 1.458 1.26a8.094 8.094 0 001.402 0c.743-.064 1.29-.614 1.458-1.26l.29-1.106c.017-.066.078-.158.211-.224a5.98 5.98 0 00.668-.386c.123-.082.233-.09.3-.071l1.102.302c.644.177 1.392-.02 1.82-.63.268-.382.505-.789.704-1.217.315-.675.111-1.422-.364-1.891l-.814-.806c-.05-.048-.098-.147-.088-.294a6.1 6.1 0 000-.772c-.01-.147.039-.246.088-.294l.814-.806c.475-.469.679-1.216.364-1.891a7.992 7.992 0 00-.704-1.218c-.428-.609-1.176-.806-1.82-.63l-1.103.303c-.066.019-.176.011-.299-.071a5.991 5.991 0 00-.668-.386c-.133-.066-.194-.158-.212-.224L10.16 1.29C9.99.645 9.444.095 8.701.031A8.094 8.094 0 008 0zm1.5 8a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM11 8a3 3 0 11-6 0 3 3 0 016 0z"></path></svg> 图标打开管理视图。

   选择 **Encryption** 字段旁的铅笔 <svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-pencil" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"></path></svg> 图标， 打开配置存储桶默认 SSE 方案的弹窗。

   选择 **SSE-KMS**，然后输入上一步创建的密钥名称。

   保存更改后，尝试向该存储桶上传一个文件。 在对象浏览器中查看该文件时， 请注意侧边栏中的元数据包含了 SSE 加密方案 以及用于加密该对象的密钥信息。 这表明该对象已成功加密。
   {{< /tab >}}
   {{< tab label="MinIO CLI" value="minio-cli" >}}
   使用 [MinIO API Service](/docs/operations/deployments/k8s-deploy-minio-tenant-on-kubernetes/#create-tenant-connect-tenant) 为 MinIO 部署创建新的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。 之后即可使用 [`mc encrypt set`](/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set) 为存储桶启用 SSE-KMS 加密：

   ```shell
   mc alias set k8s https://minio.minio-tenant-1.svc.cluster-domain.example:443 ROOTUSER ROOTPASSWORD

   mc mb k8s/encryptedbucket
   mc encrypt set SSE-KMS encrypted-bucket-key k8s/encryptedbucket
   ```

   对于 Kubernetes 集群外部客户端， 请指定通过 Ingress、Load Balancer 或类似 Kubernetes 网络控制组件暴露的服务主机名。

   使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 或任何带有 `PutObject` 函数的 S3 兼容 SDK 将文件写入该存储桶。 然后你可以对该文件执行 [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat)， 以确认其关联的加密元数据。
   {{< /tab >}}
   {{< /tabs >}}
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
1. 生成供 MinIO 使用的 KES API Key

   使用 [kes identity new](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/cli/kes-identity/new.md) 命令， 为 MinIO Server 生成新的 API key：

   ```shell
   kes identity new
   ```

   输出同时包含供 MinIO 使用的 API Key， 以及供 [KES Policy 配置](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/configuration.md#policy-configuration) 使用的 Identity hash。
2. 配置 MinIO 环境文件

   为目标部署中的所有主机创建或修改 MinIO Server 环境文件， 使其包含以下环境变量：

   将以下内容添加到每台 MinIO 主机上的 MinIO 环境文件中。 关于基础 MinIO 环境文件的更详细说明， 请参见 [安装与管理](/docs/operations/deployments/installation/#minio-snsd)、[安装与管理](/docs/operations/deployments/installation/#minio-snmd) 或 [安装与管理](/docs/operations/deployments/installation/#minio-mnmd) 教程。

   ```shell
   # Add these environment variables to the existing environment file

   MINIO_KMS_KES_ENDPOINT=https://HOSTNAME:7373
   MINIO_KMS_KES_API_KEY="kes:v1:ACTpAsNoaGf2Ow9o5gU8OmcaG6Af/VcZ1Mt7ysuKoBjv"

   # Allows validation of the KES Server Certificate (Self-Signed or Third-Party CA)
   # Change this path to the location of the KES CA Path
   MINIO_KMS_KES_CAPATH=|kescertpath|/kes-server.cert

   # Sets the default KMS key for the backend and SSE-KMS/SSE-S3 Operations)
   MINIO_KMS_KES_KEY_NAME=minio-backend-default-key
   ```

   将 `HOSTNAME` 替换为 KES server 的 IP 地址或主机名。 如果 MinIO server 所在主机无法解析或访问指定的 `HOSTNAME`， 该部署可能会返回错误，或启动失败。

   - 如果只使用一台 KES server 主机，请指定该主机的 IP 或主机名。
   - 如果使用多台 KES server 主机，请指定各主机 IP 或主机名的逗号分隔列表。

   MinIO 会将 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 这个密钥 用于以下加密操作：

   - 加密 MinIO 后端（IAM、配置等）。
   - 在请求未包含特定 <abbr title="External Key">EK</abbr> 时， 使用 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms) 加密对象。
   - 使用 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 加密对象。

   MinIO 默认在 `/etc/default/minio` 查找此文件。 如果你的部署将环境文件放在其他位置，请修改对应位置的文件。
3. 启动 MinIO

   > [!NOTE]
   > **KES 操作要求 Vault 已解封**
   >
   > 根据你选择的 KMS 方案， 你可能需要先将密钥实例解封，才能执行正常的加密操作，包括密钥创建或读取。 KES 需要已解封的密钥目标才能执行这些操作。
   >
   > 关于该实例在运行时是否需要 sealed/unsealed， 请参阅你所选 [KMS 方案文档](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets)。
   >
   > 你必须先启动 KES，再启动 MinIO。 MinIO 部署在启动过程中需要访问 KES。

   你可以使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启 MinIO：

   ```shell
   mc admin service restart ALIAS
   ```

4. 生成新的加密密钥

   MinIO 要求在使用某个 <abbr title="External Key">EK</abbr> 执行 <abbr title="Server-Side Encryption">SSE</abbr> 操作之前， 该 <abbr title="External Key">EK</abbr> 必须已存在于 KMS 中。 使用 `kes key create` *或* [`mc admin kms key create`](/docs/reference/minio-mc-admin/mc-admin-kms-key/#mc.admin.kms.key.create) 为 <abbr title="Server-Side Encryption">SSE</abbr> 添加新的 <abbr title="External Key">EK</abbr>。

   以下命令使用 [`mc admin kms key create`](/docs/reference/minio-mc-admin/mc-admin-kms-key/#mc.admin.kms.key.create) 在 KMS server 上添加一个新的 External Key（EK）， 供加密 MinIO 后端时使用。

   ```shell
   mc admin kms key create ALIAS KEYNAME
   ```

5. 为存储桶启用 SSE-KMS

   使用 MinIO [`mc`](/docs/reference/minio-mc/#command-mc) CLI， 通过生成的密钥启用存储桶默认 SSE-KMS：

   以下命令会：

   - 为 MinIO 部署创建一个新的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
   - 创建一个用于存储加密数据的新存储桶。
   - 在该存储桶上启用 SSE-KMS 加密。

   ```shell
   mc alias set local http://127.0.0.1:9000 ROOTUSER ROOTPASSWORD

   mc mb local/encryptedbucket
   mc encrypt set SSE-KMS encrypted-bucket-key ALIAS/encryptedbucket
   ```

   使用 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 或任何带有 `PutObject` 函数的 S3 兼容 SDK 将文件写入该存储桶。 然后你可以对该文件执行 [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat)， 以确认其关联的加密元数据。
{{< /tab >}}
{{< /tabs >}}