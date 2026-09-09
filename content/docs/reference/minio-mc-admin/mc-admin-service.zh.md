---
title: "mc admin service"

weight: 160
---

<a id="mc-admin-service"></a>

<a id="command-mc.admin.service"></a>

## 说明 {#id2}

[`mc admin service`](#command-mc.admin.service) 命令可用于重启或解除冻结 MinIO 服务器。

[`mc admin service`](#command-mc.admin.service) 会同时影响目标部署中的 *所有* MinIO 服务器。 该命令会中断 MinIO 部署上正在进行的 API 操作。对某个部署执行此命令时请谨慎。

> [!NOTE]
> **`mc admin` 仅用于 MinIO 部署**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 示例 {#id3}

### 重启目标部署中的 MinIO 服务器 {#minio}

以下示例使用默认的 `myminio` 别名。`myminio` 别名指向运行在 `9000` 端口上的本地 `minio` 服务器。有关安装并运行本地 `minio` 服务器实例的更多信息，请参阅 &lt;installation instructions&gt;。

有关别名的更多信息，请参阅 [`mc alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

```shell
mc admin service restart myminio
```

### 恢复目标部署上的 S3 调用 {#s3}

以下示例使用默认的 `myminio` 别名。`myminio` 别名指向运行在 `9000` 端口上的本地 `minio` 服务器。有关安装并运行本地 `minio` 服务器实例的更多信息，请参阅 &lt;installation instructions&gt;。

有关别名的更多信息，请参阅 [`mc alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

```shell
mc admin service unfreeze myminio
```

## 语法 {#id4}

[`mc admin service`](#command-mc.admin.service) 的语法如下：

```shell
mc admin service COMMAND [ARGUMENTS]
```

[`mc admin service`](#command-mc.admin.service) 支持以下命令：

#### `restart` {#mc.admin.service.restart}

*mc-cmd*

重启 MinIO 服务器。 如有需要，命令可能会根据状态建议重启节点。

[`mc admin service restart`](#mc.admin.service.restart) 的语法如下：

```shell
mc admin service restart ALIAS
```

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 [`restart`](#mc.admin.service.restart) 会重启该部署中的 *所有* MinIO 服务器。

#### `unfreeze` {#mc.admin.service.unfreeze}

*mc-cmd*

恢复 MinIO 集群上的 S3 API 调用。

[`mc admin service unfreeze`](#mc.admin.service.unfreeze) 的语法如下：

```shell
mc admin service unfreeze ALIAS
```

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。