---
title: "mc encrypt set"

weight: 30
---

<a id="mc-encrypt-set"></a>
<a id="minio-mc-encrypt-set"></a>

<a id="command-mc.encrypt.set"></a>

## 语法 {#id2}

[`mc encrypt set`](#command-mc.encrypt.set) 加密命令用于设置或更新存储桶默认的 [服务端加密（SSE）模式](/docs/administration/server-side-encryption/#minio-sse)。MinIO 会使用指定的 SSE 模式 自动加密写入该存储桶的对象。

[`mc encrypt set`](#command-mc.encrypt.set) 仅支持 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms) 和 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` MinIO 部署上的 `mydata` 存储桶设置默认的 [SSE-KMS 加密密钥](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms)：

```shell
mc encrypt set sse-kms "minio-encryption-key" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] encrypt set  ENCRYPTION [KMSKEY] ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ENCRYPTION` {#mc.encrypt.set.ENCRYPTION}

*mc-cmd*

指定作为默认 SSE 模式的服务端加密类型。 支持以下取值：

- `sse-kms` - 使用 [`KMSKEY`](#mc.encrypt.set.KMSKEY) 中指定的密钥 对对象加密。MinIO 必须能够访问外部 KMS 上指定的密钥，才能成功加密 或解密受 SSE-KMS 保护的对象。
- `sse-s3` - 使用 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 指定的密钥 对对象加密。MinIO 必须能够访问外部 KMS 上指定的密钥，才能成功加密 或解密受 SSE-S3 保护的对象。

##### `KMSKEY` {#mc.encrypt.set.KMSKEY}

*mc-cmd*

指定用于执行 SSE 对象加密的 KMS Master Key。该选项仅在 [`ENCRYPTION`](#mc.encrypt.set.ENCRYPTION) 为 `sse-kms` 时生效。

省略该选项可让 MinIO 使用 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME).

##### `ALIAS` {#mc.encrypt.set.ALIAS}

*mc-cmd*

要设置默认 SSE 模式的存储桶完整路径。将 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 作为 TARGET 路径前缀。例如：

```shell
mc encrypt set ENCRYPTION [KMSKEY] play/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 启用自动服务端存储桶加密 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令假设：

- MinIO 服务端配置支持 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms)
- root KMS 上存在加密密钥 `minio-encryption-key`。

```shell
 mc encrypt set sse-kms minio-encryption-key myminio/data
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc encrypt set ENCRYPTION KMSKEY TARGET
```

- 将 `ENCRYPTION` 替换为 `sse-kms` 或 `sse-s3`，具体取决于 所需的加密模式。
- 将 `KMSKEY` 替换为已配置 root KMS 中的加密密钥名称。 该参数对 `sse-s3` 无效。
- 将 `TARGET` 替换为要配置自动服务端存储桶加密的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id7}

[`mc encrypt set`](#command-mc.encrypt.set) 不会对 MinIO 服务端当前的加密状态作任何假设。 如果指定了服务端无法支持的默认加密设置，可能导致非预期行为。

设置或修改默认服务端加密设置时，*不会* 自动加密或解密存储桶中已有内容。 如果存储桶内容 *必须* 保持一致的加密状态，请使用 [`mc mv`](/docs/reference/minio-mc/mc-mv/#command-mc.mv) 命令并结合 [`--enc-kms`](/docs/reference/minio-mc/mc-mv/#mc.mv.-enc-kms)、[`--enc-s3`](/docs/reference/minio-mc/mc-mv/#mc.mv.-enc-s3) 或 [`--enc-c`](/docs/reference/minio-mc/mc-mv/#mc.mv.-enc-c) 指定迁移内容使用的加密类型。 这会在更改存储桶默认设置 *之前*，手动修改存储桶内容的加密设置或加密状态。