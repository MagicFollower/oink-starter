---
title: "使用按存储桶划分密钥的服务端加密（SSE-KMS）"

weight: 10
---

<a id="sse-kms"></a>
<a id="minio-encryption-sse-kms"></a>

MinIO 服务端加密（SSE）在写入操作过程中保护对象，使客户端能够利用服务端的处理能力在存储层保护对象（静态加密）。 SSE 还为围绕安全锁定和擦除的监管与合规要求提供关键能力。

MinIO SSE 使用 [MinIO Key Encryption Service (KES)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md) 和受支持的 [外部密钥管理服务（KMS）](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets)，以安全地大规模执行加密操作。 MinIO 还支持由客户端管理密钥的模式，此时应用程序对为 MinIO SSE 创建和管理加密密钥承担全部责任。

MinIO SSE-KMS 使用由密钥管理系统（KMS）管理的外部密钥（EK）对对象进行加密或解密。 每个存储桶和对象都可以拥有单独的 <abbr title="外部密钥">EK</abbr>，从而在部署中支持更细粒度的加密操作。 只有在 MinIO 同时能够访问 KMS *以及* 用于加密该对象的 <abbr title="外部密钥">EK</abbr> 时，才能解密该对象。

你可以使用 [`mc encrypt set`](/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set) 命令启用存储桶默认的 SSE-KMS 加密：

```shell
mc encrypt set sse-kms EXTERNALKEY play/mybucket
```

- 将 `EXTERNALKEY` 替换为用于加密该存储桶中对象的 <abbr title="外部密钥">EK</abbr> 名称。
- 将 `play/mybucket` 替换为你要启用自动 SSE-KMS 加密的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 和存储桶。

MinIO SSE-KMS 在功能上与 AWS S3 [使用存储在 AWS 中的 KMS 密钥进行服务端加密](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html) 兼容，同时将支持扩展到以下 KMS 提供商：

- [AWS Secrets Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/aws-secrets-manager.md)
- [Azure Key Vault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/azure-keyvault.md)
- [Entrust KeyControl](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/entrust-keycontrol.md)
- [Fortanix SDKMS](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/fortanix-sdkms.md)
- [Google Cloud Secret Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/google-cloud-secret-manager.md)
- [HashiCorp Vault Keystore](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/hashicorp-vault-keystore.md)
- [Thales CipherTrust Manager (formerly Gemalto KeySecure)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/thales-ciphertrust.md)

<a id="id2"></a>

## 快速开始 {#minio-encryption-sse-kms-quickstart}

> [!WARNING]
> **重要**
>
> 在 MinIO 部署上启用 <abbr title="服务端加密">SSE</abbr> 后， 会自动使用默认加密密钥对该部署的后端数据进行加密。
>
> MinIO 必须能够访问 KES 和外部 KMS， 才能解密后端并正常启动。 KMS 必须维护并提供对 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 的访问。 之后你不能再禁用 KES， 也不能在后续“撤销”该 <abbr title="服务端加密">SSE</abbr> 配置。

以下过程使用 `play` MinIO <abbr title="Key Encryption Service">KES</abbr> 沙箱，在评估和早期开发环境中为 <abbr title="服务端加密">SSE</abbr> 提供 SSE-KMS 支持。

对于扩展开发环境或生产环境，请使用以下受支持的外部密钥管理服务（KMS）之一：

- [AWS Secrets Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/aws-secrets-manager.md)
- [Azure Key Vault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/azure-keyvault.md)
- [Entrust KeyControl](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/entrust-keycontrol.md)
- [Fortanix SDKMS](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/fortanix-sdkms.md)
- [Google Cloud Secret Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/google-cloud-secret-manager.md)
- [HashiCorp Vault Keystore](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/hashicorp-vault-keystore.md)
- [Thales CipherTrust Manager (formerly Gemalto KeySecure)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/thales-ciphertrust.md)

> [!WARNING]
> **重要**
>
> MinIO KES `Play` sandbox 是公开环境， 并会为所有创建的 External Keys（EK）授予 root 级访问权限。 任何存储在 `Play` sandbox 上的 <abbr title="外部密钥">EK</abbr> 都可能随时被访问或销毁， 从而使受保护数据暴露风险或永久不可读。
>
> - **切勿** 使用 `Play` sandbox 保护你无法承受丢失或泄露的数据。
> - **切勿** 使用会暴露组织私有、机密或内部命名约定的名称来生成 <abbr title="外部密钥">EK</abbr>。
> - **切勿** 在生产环境中使用 `Play` sandbox。

此过程需要以下组件：

- 在一台能够通过网络访问源部署的机器上安装 [`mc`](/docs/reference/minio-mc/#command-mc)。 有关下载和安装 `mc` 的说明，请参阅 `mc` [安装快速开始](/docs/reference/minio-mc/#mc-install)。
- 在一台可以访问互联网的机器上安装 [MinIO Key Encryption Service (KES)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md)。 有关下载、安装和配置 KES 的说明，请参阅 `kes` [快速开始](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/getting-started.md) 指南。

### 1) 为 SSE-KMS 加密创建加密密钥 {#id3}

使用 [kes](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/cli/_index.md) 命令行工具创建一个新的外部密钥（EK），供 SSE-KMS 加密使用。

以下命令获取 `play` KES 服务器的 root [身份](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/_index.md#authorization)：

```shell
curl -sSL --tlsv1.2 \
  -O 'https://raw.githubusercontent.com/minio/kes/master/root.key' \
  -O 'https://raw.githubusercontent.com/minio/kes/master/root.cert'
```

在终端或 shell 中设置以下环境变量：

```shell
export KES_CLIENT_KEY=root.key
export KES_CLIENT_CERT=root.cert
```

<table>
  <tbody>
    <tr>
      <td><p><code>KES_CLIENT_KEY</code></p></td>
      <td><p>KES 服务器上某个 <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/_index.md#authorization">身份</a> 的私钥。
该身份至少必须被授予对 <code>/v1/create</code>、<code>/v1/generate</code> 和 <code>/v1/list</code> <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/server-api.md">API 端点</a> 的访问权限。
本步骤使用 MinIO <code>play</code> KES 沙箱中的 <code>root</code> 身份，该身份可访问 KES 服务器上的所有操作。</p></td>
    </tr>
    <tr>
      <td><p><code>KES_CLIENT_CERT</code></p></td>
      <td><p>KES 服务器上该 <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/_index.md#authorization">身份</a> 对应的证书。
本步骤使用 MinIO <code>play</code> KES 沙箱中的 <code>root</code> 身份，该身份可访问 KES 服务器上的所有操作。</p></td>
    </tr>
  </tbody>
</table>

以下命令通过 KES 创建一个新的 <abbr title="外部密钥">EK</abbr>。

```shell
kes key create my-minio-sse-kms-key
```

本教程使用示例名称 `my-minio-sse-kms-key` 以便引用。 请指定唯一的密钥名称，以避免与现有密钥冲突。

### 2) 配置 MinIO 以进行 SSE-KMS 对象加密 {#minio-sse-kms}

在部署中的每台 MinIO 服务器主机上，于 shell 或终端中指定以下环境变量：

```shell
export MINIO_KMS_KES_ENDPOINT=https://play.min.io:7373
export MINIO_KMS_KES_API_KEY=<API-key-identity-string-from-KES> # Replace with the key string for your credentials
export MINIO_KMS_KES_KEY_NAME=my-minio-sse-s3-key
```

> [!NOTE]
> **说明**
>
> - API 密钥是与 KES 服务器进行身份验证的首选方式，因为它提供了更简洁且更安全的认证流程。
> - 或者，也可以指定 [`MINIO_KMS_KES_KEY_FILE`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_FILE) 和 [`MINIO_KMS_KES_CERT_FILE`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_CERT_FILE)，而不是 [`MINIO_KMS_KES_API_KEY`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_API_KEY)。
>
>   API 密钥与基于证书的身份验证互斥。 请指定 API 密钥变量，*或* 指定密钥文件和证书文件变量。
> - 本站文档使用 API 密钥。

<table>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_ENDPOINT"><code>MINIO_KMS_KES_ENDPOINT</code></a></p></td>
      <td><p>MinIO <code>Play</code> KES 服务的端点。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_API_KEY"><code>MINIO_KMS_KES_API_KEY</code></a></p></td>
      <td><p>KES 为 MinIO 部署 <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/kes-for-minio.md#kes-server-setup">生成的</a> API 密钥。
该 API 密钥对应的身份必须具有创建、生成和解密密钥的权限。</p><p>API 密钥是与 KES 服务器进行身份验证的首选方式。
如果情况需要，请改为指定 <a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_FILE"><code>MINIO_KMS_KES_KEY_FILE</code></a> 和 <a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_CERT_FILE"><code>MINIO_KMS_KES_CERT_FILE</code></a>。
请指定 API 密钥，<em>或</em> 指定密钥文件和证书文件。
<em>不要</em> 同时填充这三个环境变量。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME"><code>MINIO_KMS_KES_KEY_NAME</code></a></p></td>
      <td><p>用于执行 SSE 加密操作的外部密钥（EK）名称。
KES 会从已配置的密钥管理服务（KMS）中检索该 EK。
指定上一步创建的密钥名称。</p></td>
    </tr>
  </tbody>
</table>

### 3) 重启 MinIO 部署以启用 SSE-KMS {#id4}

你必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启该部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

### 4) 配置自动存储桶加密 {#id5}

使用 [`mc encrypt set`](/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set) 命令，为写入特定存储桶的所有对象启用自动 SSE-KMS 保护。

```shell
mc encrypt set sse-kms my-minio-sse-kms-key ALIAS/BUCKET
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-encrypt-set/#mc.encrypt.set.ALIAS) 替换为已启用 SSE-KMS 的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`BUCKET`](/docs/reference/minio-mc/mc-encrypt-set/#mc.encrypt.set.ALIAS) 替换为你要启用自动 SSE-KMS 的 存储桶或存储桶前缀的完整路径。

写入指定存储桶的对象会自动使用指定的 <abbr title="外部密钥">EK</abbr> 加密。

对于每个要启用自动 SSE-KMS 加密的存储桶，请重复此步骤。 你可以按存储桶或存储桶前缀生成额外的密钥，从而将每个 <abbr title="外部密钥">EK</abbr> 的作用范围限制为对象子集。

<a id="id6"></a>

## 安全擦除与锁定 {#minio-encryption-sse-kms-erasure-locking}

SSE-KMS 使用在存储桶自动加密设置中指定的 <abbr title="外部密钥">EK</abbr>，或在写入操作中指定的 <abbr title="外部密钥">EK</abbr> 来保护对象。 因此，MinIO 在解密该对象时 *必须* 能够访问该 <abbr title="外部密钥">EK</abbr>。

- 禁用 <abbr title="外部密钥">EK</abbr> 会暂时锁定使用该 <abbr title="外部密钥">EK</abbr> 加密的对象，使其变得不可读。 之后你可以重新启用该 <abbr title="外部密钥">EK</abbr>，以恢复这些对象的正常读取操作。
- 删除 <abbr title="外部密钥">EK</abbr> 会使所有由该 <abbr title="外部密钥">EK</abbr> 加密的对象 *永久* 不可读。 如果 KMS 没有该 <abbr title="外部密钥">EK</abbr> 的备份或不支持其备份，则此过程 *不可逆*。

单个 <abbr title="外部密钥">EK</abbr> 的作用范围取决于：

- 哪些存储桶将该 <abbr title="外部密钥">EK</abbr> 指定为自动 SSE-KMS 加密所用密钥， *以及*
- 哪些写入操作在请求 SSE-KMS 加密时指定了该 <abbr title="外部密钥">EK</abbr>。

例如，假设一个 MinIO 部署为每个存储桶使用一个 <abbr title="外部密钥">EK</abbr>。 禁用其中一个 <abbr title="外部密钥">EK</abbr> 会使关联存储桶中的所有对象不可读，而不会影响其他存储桶。 如果该部署改为对所有对象和存储桶使用同一个 <abbr title="外部密钥">EK</abbr>，则禁用该 <abbr title="外部密钥">EK</abbr> 会使部署中的所有对象都不可读。

<a id="id7"></a>

## 加密过程 {#minio-encryption-sse-kms-encryption-process}

> [!NOTE]
> **说明**
>
> 本节介绍 MinIO 的内部逻辑和功能。 这些信息仅用于帮助理解，并不是配置或实现任何 MinIO 功能的前提条件。

SSE-KMS 使用由已配置密钥管理系统（KMS）管理的外部密钥（EK） 来执行加密操作并保护对象。下表描述了加密过程的各个阶段：

<table>
  <thead>
    <tr>
      <th><p>阶段</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>启用 SSE 的写入操作</p></td>
      <td><p>MinIO 接收到一个请求使用 SSE-KMS 加密的写入操作。
该写入操作 <em>必须</em> 关联一个用于加密对象的外部密钥（EK）。</p><ul><li><p>对于位于已启用自动 SSE-KMS 的存储桶中的写入操作，
MinIO 使用该存储桶的 EK。如果写入操作包含显式指定的 EK，
MinIO 会使用它来 <em>替代</em> 存储桶 EK。</p></li><li><p>对于位于 <em>未</em> 启用自动 SSE-KMS 的存储桶中的写入操作，
MinIO 使用该写入操作指定的 EK。</p></li></ul></td>
    </tr>
    <tr>
      <td><p>生成数据加密密钥（DEK）</p></td>
      <td><p>MinIO 使用 EK 生成数据加密密钥（DEK）。
具体来说，<a href="https://github.com/minio/kes">MinIO Key Encryption Service (KES)</a> 会以 EK
作为“根”密钥，向 KMS 请求新的加密密钥。</p><p>KES 会返回 DEK 的明文形式 <em>以及</em> 其经过 EK 加密后的表示。
MinIO 将加密后的表示作为对象元数据的一部分进行存储。</p></td>
    </tr>
    <tr>
      <td><p>生成密钥加密密钥（KEK）</p></td>
      <td><p>MinIO 使用确定性算法生成唯一的 256 位密钥加密密钥（KEK）。
该密钥派生算法使用伪随机函数，并以明文 DEK、随机生成的初始化向量以及由
存储桶名称、对象名称等值构成的上下文作为输入。</p><p>MinIO 会在每次加密或解密操作时生成 KEK，并且 <em>绝不会</em> 将 KEK 存储到磁盘上。</p></td>
    </tr>
    <tr>
      <td><p>生成对象加密密钥（OEK）</p></td>
      <td><p>MinIO 会生成随机且唯一的 256 位对象加密密钥（OEK），并使用该密钥加密对象。
MinIO 不会将 OEK 的明文形式存储到磁盘上。
在加密或解密操作期间，OEK 的明文仅驻留在 RAM 中。</p></td>
    </tr>
    <tr>
      <td><p>加密对象</p></td>
      <td><p>MinIO 在将对象写入驱动器 <em>之前</em> 使用 OEK 对对象进行加密。
然后，MinIO 再使用 KEK 对 OEK 进行加密。</p><p>MinIO 将 OEK 和 DEK 的加密表示作为元数据的一部分存储。</p></td>
    </tr>
  </tbody>
</table>

对于读取操作，MinIO 会先获取 <abbr title="外部密钥">EK</abbr> 以解密 <abbr title="数据加密密钥">DEK</abbr>。 随后 MinIO 会重新生成 <abbr title="密钥加密密钥">KEK</abbr>、解密 <abbr title="对象加密密钥">OEK</abbr>，并解密该对象。