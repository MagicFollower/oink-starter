---
title: "mc admin config"

weight: 40
---

<a id="mc-admin-config"></a>
<a id="minio-mc-admin-config"></a>

<a id="command-mc.admin.config"></a>

## 说明 {#id2}

[`mc admin config`](#command-mc.admin.config) 命令用于管理 [`minio`](/docs/reference/minio-server/#command-minio) 服务器的配置设置。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 示例 {#id3}

## 语法 {#id4}

#### `mc admin config set` {#mc.admin.config.set}

*mc-cmd*

在 MinIO 部署上设置 [配置键](/docs/reference/minio-server/settings/#minio-server-configuration-settings)。 由环境变量定义的配置会覆盖通过此命令定义的配置。

#### `mc admin config get` {#mc.admin.config.get}

*mc-cmd*

获取 MinIO 部署上通过 *mc admin config set* 创建的 [配置键](/docs/reference/minio-server/settings/#minio-server-configuration-settings)。

#### `mc admin config export` {#mc.admin.config.export}

*mc-cmd*

导出通过 *mc admin config set* 创建的所有配置设置。

#### `mc admin config history` {#mc.admin.config.history}

*mc-cmd*

列出由 *mc admin config* 对配置键所做变更的历史记录。

由环境变量定义的配置不会显示在其中。

#### `mc admin config import` {#mc.admin.config.import}

*mc-cmd*

导入通过 *mc admin config export* 导出的配置设置。

#### `mc admin config reset` {#mc.admin.config.reset}

*mc-cmd*

将配置重置为默认值。 在环境变量中定义的配置不受影响。

#### `mc admin config restore` {#mc.admin.config.restore}

*mc-cmd*

将配置键的更改回滚到历史中的先前时间点。

不影响由环境变量定义的配置。

## 配置设置 {#id5}

可用配置设置列表请参见 [设置概览](/docs/reference/minio-server/settings/#minio-server-configuration-settings)。