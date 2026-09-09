---
title: "已弃用设置"

weight: 120
---

<a id="minio-server-envvar-deprecated"></a>
<a id="id1"></a>

本页介绍用于控制 MinIO 进程核心行为的已弃用设置。

本页中的设置可能随时被移除。 用户应尽早迁移到推荐的替代项。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 环境变量 {#id3}

以下 *环境变量* 已弃用。 此处仅为历史参考而列出。

#### `MINIO_SECRET_KEY` {#envvar.MINIO_SECRET_KEY}

*envvar*

> [!CAUTION]
> **已弃用: RELEASE.2021-04-22T15-44-28Z**

[root](/docs/administration/identity-access-management/minio-user-management/#minio-users-root) 用户的 secret key。

该环境变量已 *弃用*，请改用 [`MINIO_ROOT_PASSWORD`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_PASSWORD) 环境变量。

> [!CAUTION]
> **警告**
>
> 如果未设置 [`MINIO_SECRET_KEY`](#envvar.MINIO_SECRET_KEY)，[`minio`](/docs/reference/minio-server/#command-minio) 默认使用 `minioadmin`。
>
> 在生产环境中 **绝不要** 使用默认凭证。 MinIO 强烈建议在所有环境中为 [`MINIO_ACCESS_KEY`](#envvar.MINIO_ACCESS_KEY) 指定唯一、足够长且随机的值。

#### `MINIO_ACCESS_KEY` {#envvar.MINIO_ACCESS_KEY}

*envvar*

> [!CAUTION]
> **已弃用: RELEASE.2021-04-22T15-44-28Z**

[root](/docs/administration/identity-access-management/minio-user-management/#minio-users-root) 用户的 access key。

> 该环境变量已 *弃用*，请改用 [`MINIO_ROOT_USER`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_USER) 环境变量。

> [!CAUTION]
> **警告**
>
> 如果未设置 [`MINIO_ACCESS_KEY`](#envvar.MINIO_ACCESS_KEY)，[`minio`](/docs/reference/minio-server/#command-minio) 默认使用 `minioadmin`。
>
> 在生产环境中 **绝不要** 使用默认凭证。 MinIO 强烈建议在所有环境中为 [`MINIO_ACCESS_KEY`](#envvar.MINIO_ACCESS_KEY) 指定唯一、足够长且随机的值。

#### `MINIO_ACCESS_KEY_OLD` {#envvar.MINIO_ACCESS_KEY_OLD}

*envvar*

> [!CAUTION]
> **已弃用: RELEASE.2021-04-22T15-44-28Z**

要轮换 root 凭证，请修改 [`MINIO_ROOT_USER`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_USER) 和 [`MINIO_ROOT_PASSWORD`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_PASSWORD) 环境变量。

#### `MINIO_OPERATOR_DEPLOYMENT_NAME` {#envvar.MINIO_OPERATOR_DEPLOYMENT_NAME}

*envvar*

> [!CAUTION]
> **已弃用: Operator**
>
> 6.0.4

指定为 Operator 创建并使用的命名空间。

未指定时，默认值为 `minio-operator`。

#### `MINIO_SECRET_KEY_OLD` {#envvar.MINIO_SECRET_KEY_OLD}

*envvar*

> [!CAUTION]
> **已弃用: RELEASE.2021-04-22T15-44-28Z**

要轮换 root 凭证，请修改 [`MINIO_ROOT_USER`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_USER) 和 [`MINIO_ROOT_PASSWORD`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_PASSWORD) 环境变量。

#### `MINIO_SERVER_URL` {#envvar.MINIO_SERVER_URL}

*envvar*

> [!CAUTION]
> **已弃用: RELEASE.2024-05-10T01-41-38Z**

MinIO Console 用于连接 MinIO Server 的 [fully qualified domain name](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) (FQDN)。

为确保 Console 正常工作，MinIO server URL *必须* 是主机的 FQDN，且可解析并可达。

如果指定值无法解析到 MinIO server，通过 MinIO Console 登录将失败，并在等待一段时间后返回网络错误。 较旧版本的 Console 可能会返回通用的“Invalid Login”错误。 可通过取消设置该值 *或* 解决 FQDN 解析问题来恢复 Console 登录。 在以下情况下可能需要该设置：

- MinIO Server 使用的 TLS 证书在 Subject Alternative Name (SAN) 中未包含主机本地 IP。

或

- 由于反向代理或类似配置，Console 必须使用特定主机名来连接或引用 MinIO Server。