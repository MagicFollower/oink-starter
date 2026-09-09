---
title: "mc admin kms key"

weight: 90
---

<a id="mc-admin-kms-key"></a>

<a id="command-mc.admin.kms.key"></a>

## 描述 {#id2}

[`mc admin kms key`](#command-mc.admin.kms.key) 命令通过 MinIO Key Encryption Service (KES) 执行加密密钥管理操作。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 语法 {#id3}

#### `mc admin kms key create` {#mc.admin.kms.key.create}

*mc-cmd*

在 Key Management System (KMS) 上创建一个新的主密钥。

该命令语法如下：

```shell
mc admin kms key create TARGET [KEY_NAME]
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.kms.key.create.TARGET}

*mc-cmd*

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

`TARGET` 部署 **必须** 包含已配置的 MinIO Key Encryption Service (KES) 服务器。

#### `KEY_NAME` {#mc.admin.kms.key.create.KEY_NAME}

*mc-cmd*

指定新主密钥的名称。

#### `mc admin kms key status` {#mc.admin.kms.key.status}

*mc-cmd*

请求 Key Management System (KMS) 主密钥的信息。

该命令语法如下：

```shell
mc admin kms key status TARGET [KEY_NAME]
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.kms.key.status.TARGET}

*mc-cmd*

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

`TARGET` 部署 **必须** 包含已配置的 MinIO Key Encryption Service (KES) 服务器。

#### `KEY_NAME` {#mc.admin.kms.key.status.KEY_NAME}

*mc-cmd*

指定 KMS 上主密钥的名称。

省略此参数可返回 [`TARGET`](#mc.admin.kms.key.status.TARGET) 所指部署上的默认主密钥。

#### `mc admin kms key list` {#mc.admin.kms.key.list}

*mc-cmd*

列出 MinIO 实例的所有 Key Management System (KMS) 密钥。

该命令语法如下：

```shell
mc admin kms key list TARGET
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.kms.key.list.TARGET}

*mc-cmd*

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

`TARGET` 部署 **必须** 包含已配置的 MinIO Key Encryption Service (KES) 服务器。