---
title: "密钥加密服务设置"

weight: 100
---

<a id="minio-server-envvar-kes"></a>
<a id="id1"></a>

MinIO Server 提供三组环境变量，用于管理 MinIO Server 与 Key Encryption Service (KES)、Key Management Service (KMS) 或静态密钥文件的交互方式。 这三组中只能定义一组。 如果定义了多种类型的环境变量组，MinIO 会返回错误。

> [!NOTE]
> **说明**
>
> 这些设置不支持通过 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 进行配置。

在启动或重启 MinIO 进程之前，请在宿主系统中定义其中任意一组环境变量。 有关如何定义环境变量，请参考操作系统文档。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## Key Encryption Service {#key-encryption-service}

定义以下变量以使用 Key Encryption Service (KES) 连接到 [受支持的第三方 Key Management Service 提供商](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets)。

#### `MINIO_KMS_KES_ENDPOINT` {#envvar.MINIO_KMS_KES_ENDPOINT}

*envvar*

MinIO Key Encryption Service (KES) 进程用于支持 SSE-S3 和 MinIO 后端加密操作的 endpoint。 多个 KES endpoint 使用 `,` 分隔。

#### `MINIO_KMS_KES_KEY_NAME` {#envvar.MINIO_KMS_KES_KEY_NAME}

*envvar*

KES 服务器上配置的 Key Management system (KMS) 中外部密钥名称，用于执行加密和解密操作。 MinIO 将此密钥用于以下用途：

- 加密后端数据（[IAM](/docs/administration/identity-access-management/#minio-authentication-and-identity-management)、服务器配置）。
- [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms) 的默认服务端加密密钥。
- [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 的服务端加密密钥。

> [!WARNING]
> **重要**
>
> 在 MinIO 部署上启用 <abbr title="服务端加密">SSE</abbr> 后， 会自动使用默认加密密钥对该部署的后端数据进行加密。
>
> MinIO 必须能够访问 KES 和外部 KMS， 才能解密后端并正常启动。 KMS 必须维护并提供对 [`MINIO_KMS_KES_KEY_NAME`](#envvar.MINIO_KMS_KES_KEY_NAME) 的访问。 之后你不能再禁用 KES， 也不能在后续“撤销”该 <abbr title="服务端加密">SSE</abbr> 配置。

#### `MINIO_KMS_KES_API_KEY` {#envvar.MINIO_KMS_KES_API_KEY}

*envvar*

使用通过 [kes identity new](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/cli/kes-identity/new.md) 命令获取的 KES API key 与加密服务进行身份认证的首选方式。

此环境变量与 [`MINIO_KMS_KES_KEY_FILE`](#envvar.MINIO_KMS_KES_KEY_FILE) 和 [`MINIO_KMS_KES_CERT_FILE`](#envvar.MINIO_KMS_KES_CERT_FILE) 环境变量互斥。

#### `MINIO_KMS_KES_KEY_FILE` {#envvar.MINIO_KMS_KES_KEY_FILE}

*envvar*

与 [`MINIO_KMS_KES_CERT_FILE`](#envvar.MINIO_KMS_KES_CERT_FILE) x.509 证书关联的私钥，用于向 KES 服务器进行身份认证。 KES 服务器要求客户端提供证书以执行 mutual TLS (mTLS)。

有关 KES 访问控制的完整文档，请参见 [KES wiki](https://github.com/minio/kes/wiki/Configuration#policy-configuration)。

还必须设置 [`MINIO_KMS_KES_CERT_FILE`](#envvar.MINIO_KMS_KES_CERT_FILE)。 此变量与 [`MINIO_KMS_KES_API_KEY`](#envvar.MINIO_KMS_KES_API_KEY) 互斥。

#### `MINIO_KMS_KES_CERT_FILE` {#envvar.MINIO_KMS_KES_CERT_FILE}

*envvar*

提供给 KES 服务器的 x.509 证书。 KES 服务器要求客户端提供证书以执行 mutual TLS (mTLS)。

KES 服务器会根据证书计算 [identity](https://github.com/minio/kes/wiki/Configuration#policy-configuration)，并将其与已配置策略进行比对。 KES 服务器仅向 [`minio`](/docs/reference/minio-server/#command-minio) 服务器授予策略中明确允许的操作访问权限。

有关 KES 访问控制的完整文档，请参见 [KES wiki](https://github.com/minio/kes/wiki/Configuration#policy-configuration)。

还必须设置 [`MINIO_KMS_KES_KEY_FILE`](#envvar.MINIO_KMS_KES_KEY_FILE)。 此变量与 [`MINIO_KMS_KES_API_KEY`](#envvar.MINIO_KMS_KES_API_KEY) 互斥。

#### `MINIO_KMS_KES_CAPATH` {#envvar.MINIO_KMS_KES_CAPATH}

*envvar*

*Optional*

允许使用自签名或第三方 <abbr title="Certificate Authority">CA</abbr> 验证 KES 服务器证书。 指定 KES 部署所使用的 <abbr title="Certificate Authority">CA</abbr> 证书路径。

如果使用公共证书颁发机构，则不需要此变量。

#### `MINIO_KMS_KES_KEY_PASSWORD` {#envvar.MINIO_KMS_KES_KEY_PASSWORD}

*envvar*

*Optional*

用于加密和解密 TLS 私钥的密码（如果使用）。

## MinIO Key Management Server (KMS) {#minio-key-management-server-kms}

定义以下变量以使用 [MinIO KMS](https://min.io/product/enterprise/key-management-server?ref=docs) 管理密钥。

#### `MINIO_KMS_SERVER` {#envvar.MINIO_KMS_SERVER}

*envvar*

MinIO Key Management Service (KMS) 进程用于支持 SSE-S3 和 MinIO 后端加密操作的 endpoint。 多个 KMS endpoint 使用 `,` 分隔。

#### `MINIO_KMS_ENCLAVE` {#envvar.MINIO_KMS_ENCLAVE}

*envvar*

密钥和身份所在的 MinIO KMS Enclave。

#### `MINIO_KMS_SSE_KEY` {#envvar.MINIO_KMS_SSE_KEY}

*envvar*

当调用未指定密钥身份时，用于 SSE-S3 加密的默认密钥。

#### `MINIO_KMS_API_KEY` {#envvar.MINIO_KMS_API_KEY}

*envvar*

用于向 MinIO KMS 服务进行身份认证的凭据。

## 静态密钥文件 {#id3}

> [!CAUTION]
> **警告**
>
> 这些设置用于在不依赖外部 KMS 的情况下，对对象服务端加密进行早期开发和评估。 不要在长期开发、QA 或生产环境中使用这些设置。 关于如何使用 MinIO Key Encryption Service (KES) 和外部 KMS 部署 SSE，请参见 [使用 KES 进行服务端对象加密](/docs/operations/server-side-encryption/configure-minio-kes/#minio-sse-vault)。

提供静态 KMS 密钥或密钥文件用于加密。

#### `MINIO_KMS_SECRET_KEY` {#envvar.MINIO_KMS_SECRET_KEY}

*envvar*

静态 KMS 密钥的 base64 形式，格式为 `<key-name>:<base64-32byte-key>`。 实现了部分 KMS API。

#### `MINIO_KMS_SECRET_KEY_FILE` {#envvar.MINIO_KMS_SECRET_KEY_FILE}

*envvar*

读取静态 KMS 密钥的文件路径。