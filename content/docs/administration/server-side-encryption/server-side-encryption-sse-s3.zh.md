---
title: "部署级服务端加密密钥（SSE-S3）"

weight: 20
---

<a id="sse-s3"></a>
<a id="minio-encryption-sse-s3"></a>

MinIO 服务端加密（SSE）在写入操作期间保护对象，使客户端能够利用服务端的处理能力， 在存储层保护对象（静态加密）。SSE 还为围绕安全锁定和擦除的监管与合规要求提供关键能力。

MinIO SSE 使用 [MinIO Key Encryption Service (KES)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md) 和外部 Key Management Service (KMS) 以安全方式大规模执行加密操作。MinIO 还支持 客户端自主管理密钥，即由应用全权负责创建和管理供 MinIO SSE 使用的加密密钥。

MinIO SSE-S3 使用由 Key Management System (KMS) 管理的 <abbr title="External Key">EK</abbr> 对对象进行加/解密。 你必须在启动 MinIO 服务器时通过 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 环境变量指定 该 <abbr title="External Key">EK</abbr>。对于 *所有* SSE-S3 加密操作，MinIO 都使用同一个 EK。

你可以使用 [`mc encrypt set`](/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set) 命令启用存储桶默认 SSE-S3 加密：

```shell
mc encrypt set sse-s3 play/mybucket
```

- 将 `play/mybucket` 替换为你要启用自动 SSE-KMS 加密的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 和存储桶。

MinIO SSE-S3 在功能上兼容 AWS S3 [Server-Side Encryption with Amazon S3-Managed Keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html)， 同时将支持扩展到以下 KMS 提供商：

- [AWS Secrets Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/aws-secrets-manager.md)
- [Azure KeyVault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/azure-keyvault.md)
- [Entrust KeyControl](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/entrust-keycontrol.md)
- [Fortanix SDKMS](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/fortanix-sdkms.md)
- [Google Cloud Secret Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/google-cloud-secret-manager.md)
- [HashiCorp Vault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/hashicorp-vault-keystore.md)
- [Thales CipherTrust Manager (formerly Gemalto KeySecure)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/thales-ciphertrust.md)

<a id="id2"></a>

## 快速开始 {#minio-encryption-sse-s3-quickstart}

> [!WARNING]
> **重要**
>
> 在 MinIO 部署上启用 <abbr title="Server-Side Encryption">SSE</abbr> 后， 会自动使用默认加密密钥对该部署的后端数据进行加密。
>
> MinIO 必须能够访问 KES 和外部 KMS， 才能解密后端并正常启动。 KMS 必须维护并提供对 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 的访问。 之后你不能再禁用 KES， 也不能在后续“撤销”该 <abbr title="Server-Side Encryption">SSE</abbr> 配置。

以下流程使用 `play` MinIO <abbr title="Key Encryption Service">KES</abbr> 沙箱，在评估和早期开发环境中为 SSE-S3 提供 <abbr title="Server-Side Encryption">SSE</abbr> 支持。

对于较长期的开发环境或生产环境，请使用以下受支持的外部 Key Management Services (KMS) 之一：

- [AWS Secrets Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/aws-secrets-manager.md)
- [Azure KeyVault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/azure-keyvault.md)
- [Entrust KeyControl](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/entrust-keycontrol.md)
- [Fortanix SDKMS](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/fortanix-sdkms.md)
- [Google Cloud Secret Manager](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/google-cloud-secret-manager.md)
- [HashiCorp Vault](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/hashicorp-vault-keystore.md)
- [Thales CipherTrust Manager (formerly Gemalto KeySecure)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/integrations/thales-ciphertrust.md)

> [!WARNING]
> **重要**
>
> MinIO KES `Play` sandbox 是公开环境， 并会为所有创建的 External Keys（EK）授予 root 级访问权限。 任何存储在 `Play` sandbox 上的 <abbr title="External Key">EK</abbr> 都可能随时被访问或销毁， 从而使受保护数据暴露风险或永久不可读。
>
> - **切勿** 使用 `Play` sandbox 保护你无法承受丢失或泄露的数据。
> - **切勿** 使用会暴露组织私有、机密或内部命名约定的名称来生成 <abbr title="External Key">EK</abbr>。
> - **切勿** 在生产环境中使用 `Play` sandbox。

此流程需要以下组件：

- 在一台能够通过网络访问源部署的机器上安装 [`mc`](/docs/reference/minio-mc/#command-mc)。 有关下载和安装 `mc` 的说明，请参阅 `mc` [Installation Quickstart](/docs/reference/minio-mc/#mc-install)。
- 在一台可访问互联网的机器上安装 [MinIO Key Encryption Service (KES)](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md)。 有关下载、安装和配置 KES 的说明，请参阅 KES [Getting Started](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/getting-started.md) 指南。

### 1) 为 SSE-S3 加密创建加密密钥 {#id3}

使用 [kes](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/cli/_index.md) 命令行工具创建一个新的 <abbr title="External Key">EK</abbr>，供 SSE-S3 加密使用。

以下命令获取已连接到 KES `play` 沙箱的 KES 服务器的 root [identity](https://github.com/minio/kes/wiki/Configuration#policy-configuration)：

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
      <td><p>KES 服务器上某个 <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/_index.md#authorization">identity</a> 的私钥。
该 identity 至少必须被授予对 <code>/v1/create</code>、<code>/v1/generate</code> 和
<code>/v1/list</code> <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/server-api.md">API endpoints</a> 的访问权限。
此步骤使用 MinIO <code>play</code> KES 沙箱的 <code>root</code> identity，它可访问
KES 服务器上的所有操作。</p></td>
    </tr>
    <tr>
      <td><p><code>KES_CLIENT_CERT</code></p></td>
      <td><p>KES 服务器上该 <a href="https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/concepts/_index.md#authorization">identity</a> 对应的证书。
此步骤使用 MinIO <code>play</code> KES 沙箱的 <code>root</code> identity，它可访问
KES 服务器上的所有操作。</p></td>
    </tr>
  </tbody>
</table>

以下命令通过 [KES CLI](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/cli/kes-key/create.md) 创建一个新的 <abbr title="External Key">EK</abbr>：

```shell
kes key create my-minio-sse-s3-key
```

本教程使用示例名称 `my-minio-sse-s3-key` 以便引用。 请指定唯一的密钥名称，以避免与现有密钥冲突。

### 2) 配置 MinIO 以启用 SSE-S3 对象加密 {#minio-sse-s3}

在部署中每个 MinIO 服务器主机的 shell 或终端中设置以下环境变量：

```shell
export MINIO_KMS_KES_ENDPOINT=https://play.min.io:7373
export MINIO_KMS_KES_API_KEY=<API-key-identity-string-from-KES> # Replace with the key string for your credentials
export MINIO_KMS_KES_KEY_NAME=my-minio-sse-s3-key
```

> [!NOTE]
> **说明**
>
> - API key 是与 KES 服务器进行身份验证的首选方式，因为它为 KES 服务器提供了 更精简且安全的认证流程。
> - 或者，使用 [`MINIO_KMS_KES_KEY_FILE`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_FILE) 和 [`MINIO_KMS_KES_CERT_FILE`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_CERT_FILE) 替代 [`MINIO_KMS_KES_API_KEY`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_API_KEY)。
>
>   API key 与基于证书的身份验证互斥。 请在 API key 变量与 Key File 和 Cert File 变量之间 *二选一*。
> - 本站文档使用 API key。

<table>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_ENDPOINT"><code>MINIO_KMS_KES_ENDPOINT</code></a></p></td>
      <td><p>MinIO <code>Play</code> KES 服务的端点。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_FILE"><code>MINIO_KMS_KES_KEY_FILE</code></a></p></td>
      <td><p>与 KES 服务上的某个
<a href="https://github.com/minio/kes/wiki/Configuration#policy-configuration">identity</a>
对应的私钥文件。该 identity 必须具备创建、生成和解密密钥的权限。
请指定与上一步中 <code>KES_KEY_FILE</code> 环境变量相同的 identity 私钥文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_CERT_FILE"><code>MINIO_KMS_KES_CERT_FILE</code></a></p></td>
      <td><p>与 KES 服务上的某个
<a href="https://github.com/minio/kes/wiki/Configuration#policy-configuration">identity</a>
对应的公钥证书文件。该 identity 必须具备创建、生成和解密密钥的权限。
请指定与上一步中 <code>KES_CERT_FILE</code> 环境变量相同的 identity 证书文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME"><code>MINIO_KMS_KES_KEY_NAME</code></a></p></td>
      <td><p>用于执行 SSE 加密操作的 EK 名称。
KES 从已配置的 Key Management System (KMS) 中获取该 EK。
请指定上一步创建的密钥名称。</p></td>
    </tr>
  </tbody>
</table>

### 3) 重启 MinIO 部署以启用 SSE-S3 {#id4}

必须重启 MinIO 部署以应用配置变更。 使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署。

```shell
mc admin service restart ALIAS
```

将 `ALIAS` 替换为要重启的部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

### 4) 配置存储桶自动加密 {#id5}

*可选*

如果你只打算使用客户端驱动的 SSE-S3，可以跳过此步骤。

使用 [`mc encrypt set`](/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set) 命令，为写入特定存储桶的所有对象启用自动 SSE-S3 保护。

```shell
mc encrypt set sse-s3 ALIAS/BUCKET
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-encrypt-set/#mc.encrypt.set.ALIAS) 替换为已启用 SSE-S3 的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`BUCKET`](/docs/reference/minio-mc/mc-encrypt-set/#mc.encrypt.set.ALIAS) 替换为你要启用自动 SSE-S3 的 存储桶或存储桶前缀的完整路径。

<a id="id6"></a>

## 安全擦除与锁定 {#minio-encryption-sse-s3-erasure-locking}

SSE-S3 使用服务器启动时通过 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 环境变量指定的 <abbr title="External Key">EK</abbr> 来保护对象。因此，MinIO *必须* 访问该 <abbr title="External Key">EK</abbr> 才能解密该对象。

- 禁用该 <abbr title="External Key">EK</abbr> 会使部署中经 SSE-S3 加密的对象暂时无法读取，从而被临时锁定。 你之后可以重新启用该 <abbr title="External Key">EK</abbr>，以恢复正常读取操作。
- 删除该 <abbr title="External Key">EK</abbr> 会使部署中所有经 SSE-S3 加密的对象 *永久* 无法读取。 如果 KMS 没有该 <abbr title="External Key">EK</abbr> 的备份或不支持其备份，此过程 *不可逆*。

该 <abbr title="External Key">EK</abbr> 的作用范围取决于：

- 哪些存储桶指定了自动 SSE-S3 加密，*以及*
- 哪些写入操作请求了 SSE-S3 加密。

<a id="id7"></a>

## 加密过程 {#minio-encryption-sse-s3-encryption-process}

> [!NOTE]
> **说明**
>
> 以下部分描述 MinIO 的内部逻辑和功能。 这些信息仅用于帮助理解，并非配置或实现任何 MinIO 功能所必需。

SSE-S3 使用由已配置的 Key Management System (KMS) 管理的 <abbr title="External Key">EK</abbr> 来执行加密操作并 保护对象。下表描述了加密过程的各个阶段：

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
      <td><p>MinIO 接收到一个请求执行 SSE-S3 加密的写入操作。
MinIO 将 <a href="/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME"><code>MINIO_KMS_KES_KEY_NAME</code></a> 中指定的密钥名称用作 EK。</p></td>
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
      <td><p>MinIO 在将对象写入磁盘 <em>之前</em> 使用 OEK 对对象进行加密。
随后，MinIO 使用 KEK 对 OEK 进行加密。</p><p>MinIO 将 OEK 和 DEK 的加密表示形式作为元数据的一部分进行存储。</p></td>
    </tr>
  </tbody>
</table>