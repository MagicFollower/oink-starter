---
title: "Root 访问设置"

weight: 30
---

<a id="root"></a>
<a id="minio-server-envvar-root"></a>

本页介绍用于控制 MinIO 进程 root（超级用户）访问权限的设置。 root 用户具有完整访问权限，可在 MinIO 部署上执行操作。

即使使用 [MinIO Key Encryption Service](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md) 或其他密钥管理工具，也必须配置 Root User 和 Root Password。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## Root User {#root-user}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_ROOT_USER` {#envvar.MINIO_ROOT_USER}

*envvar*

[root](/docs/administration/identity-access-management/minio-user-management/#minio-users-root) 用户的访问密钥。

> [!CAUTION]
> **警告**
>
> 如果未设置 [`MINIO_ROOT_USER`](#envvar.MINIO_ROOT_USER)，[`minio`](/docs/reference/minio-server/#command-minio) 默认使用 `minioadmin`。
>
> 在生产环境中 **绝不要** 使用默认凭证。 MinIO 强烈建议在所有环境中为 [`MINIO_ROOT_USER`](#envvar.MINIO_ROOT_USER) 指定唯一、足够长且随机的值。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置变量。 请改用环境变量。
{{< /tab >}}
{{< /tabs >}}

## Root Password {#root-password}

{{< tabs group="tab1-tab2" default="tab1" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_ROOT_PASSWORD` {#envvar.MINIO_ROOT_PASSWORD}

*envvar*

[root](/docs/administration/identity-access-management/minio-user-management/#minio-users-root) 用户的密钥。

> [!CAUTION]
> **警告**
>
> 如果未设置 [`MINIO_ROOT_PASSWORD`](#envvar.MINIO_ROOT_PASSWORD)，[`minio`](/docs/reference/minio-server/#command-minio) 默认使用 `minioadmin`。
>
> 在生产环境中 **绝不要** 使用默认凭证。 MinIO 强烈建议在所有环境中为 [`MINIO_ROOT_PASSWORD`](#envvar.MINIO_ROOT_PASSWORD) 指定唯一、足够长且随机的值。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置变量。 请改用环境变量。
{{< /tab >}}
{{< /tabs >}}

<a id="id2"></a>

## Root 访问 {#minio-disable-root-access}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_API_ROOT_ACCESS` {#envvar.MINIO_API_ROOT_ACCESS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `api root-access` {#mc-conf.api.root-access}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2023-05-04T21-44-30Z

设置为 `on` 可启用 [root](/docs/administration/identity-access-management/minio-user-management/#minio-users-root) 用户账号，设置为 `off` 可禁用该账号。 禁用 root 服务账户时，也会禁用所有与 root 关联的服务账户，但用于站点复制的账号除外。 默认值为 `on`。

> [!WARNING]
> **重要**
>
> 如果通过此设置禁用 root API 访问，你 **仍然必须** 为内部使用设置 root user 和 root password。

在禁用 root 账号之前，请确保至少存在一个其他管理员用户，例如具备 [`consoleAdmin`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.consoleAdmin) 策略的用户。 如果没有其他管理员用户，禁用 root 账号会导致该部署的管理访问被锁定。

你可以使用此变量临时覆盖配置项，重新启用对部署的 root 访问。

如果发生意外锁定，要进行重置，请将 [`MINIO_API_ROOT_ACCESS`](#envvar.MINIO_API_ROOT_ACCESS) 设为 `on` 以覆盖此设置，并临时重新启用 root 账号。 随后你可以将此设置改为 `on`，*或* 完成必要的用户/策略调整，以确保可通过其他非 root 账号进行正常管理访问。

## 唯一 Root 凭证 {#id3}

> [!NOTE]
> **新增: Server**
>
> RELEASE.2024-03-03T17-50-39Z
>
> 如果同时满足以下所有条件，MinIO 会自动生成唯一的 root 凭证：
>
> - [KES](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/tutorials/getting-started.md) Release 2024-03-01T18-06-46Z or later running
> - **未** 定义：
>
>   - `MINIO_ROOT_USER` 变量
>   - `MINIO_ROOT_PASSWORD` 变量
> - **已**：
>
>   - 使用 [受支持的 KMS 目标](https://github.com/minio/kes-docs/blob/67cc5e56909035aad851f2d031a295a8ad9efe57/content/_index.md#supported-kms-targets) 完成 KES 配置
>   - 通过 [MinIO 环境变量](#minio-disable-root-access) 禁用 root 访问
>
> 当这些条件在启动时满足后， MinIO 会使用 KMS 和 [hash-based message authentication code (HMAC)](https://en.wikipedia.org/wiki/HMAC) 为该部署生成唯一的 root 凭证。
>
> 如果 MinIO 生成了此类凭证， 则用于生成这些凭证的密钥 **必须** 保持不变，并且必须持续存在。 该部署中的所有数据都使用此密钥加密！
>
> 如果要轮换已生成的 root 凭证， 请先在 KMS 中生成新密钥，然后将 [`MINIO_KMS_KES_KEY_NAME`](/docs/reference/minio-server/settings/kes/#envvar.MINIO_KMS_KES_KEY_NAME) 的值更新为该新密钥。