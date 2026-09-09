---
title: "mc admin update"

weight: 180
---

<a id="mc-admin-update"></a>

<a id="command-mc.admin.update"></a>

## 描述 {#id2}

[`mc admin update`](#command-mc.admin.update) 命令会调用 MinIO 兼容的服务端原地更新 API。客户端可传入可选的发布镜像 URL，由服务端把选定的二进制分发到所有节点。

运行该命令后，会显示确认更新的提示。 输入 `y` 并按 `[ENTER]`，即可确认并继续更新。

用户 **必须** 对二进制安装目标位置具有 `write` 权限。

> [!CAUTION]
> **不要在 Silo 上使用默认更新路径**
>
> 自 `RELEASE.2026-08-06T00-00-00Z` 起，Silo 服务端禁用了原地更新器：`mc admin update ALIAS` 无法替换二进制，也不再访问上游 `dl.min.io` 发布源。仍在 `RELEASE.2026-08-04T00-00-00Z` 或更早版本的服务端在省略 `MIRROR_URL` 时会解析到该发布源并保留上游 MinIO 签名密钥，对其运行 `mc admin update` 可能把 Silo 替换成上游 MinIO 二进制。请通过软件包、镜像或编排器滚动发布新版本。
>
> 请在 Silo 服务端设置 `MINIO_UPDATE=off`，并通过[下载与安装](/zh/download/#server)、可信软件仓库或手工校验的 Silo 制品升级。本页保留命令契约是为了兼容，并不表示这是推荐的 Silo 升级流程。

> [!NOTE]
> **仅在 Silo 或兼容的 MinIO 部署上使用 `mc admin`**
>
> [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 使用 MinIO 专用管理 API。仅仅兼容通用 S3 API，并不意味着其他对象存储支持这些命令。

## 注意事项 {#id3}

### 协调重启 {#id4}

[`mc admin update`](#command-mc.admin.update) 会更新二进制并同时重启部署中的所有服务器。应用应预期短暂不可用，并重试失败或中断的请求；对象操作的原子性并不能让全量集群重启对应用不可见。

请使用协调一致的升级与重启流程。除非发布说明明确声明支持混合版本，否则不要逐节点滚动替换二进制。

### 权限 {#id5}

执行该命令的用户 **必须** 对 MinIO 服务端二进制安装目标路径具有 `write` 权限。

## 示例 {#id6}

下面的继承形式仅用于说明命令契约。**不要对 Silo 执行它**，因为省略 `MIRROR_URL` 会选择上游 MinIO 更新源：

```shell
mc admin update ALIAS
```

将 [`ALIAS`](#mc.admin.update.ALIAS) 替换为目标部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

运行该命令后，在提示中输入 yes 以确认并执行更新。

## 语法 {#id7}

[`mc admin update`](#command-mc.admin.update) 语法如下：

```shell
mc admin update ALIAS         \
                [MIRROR_URL]  \
                [--yes]
```

[`mc admin update`](#command-mc.admin.update) 支持以下参数：

#### `ALIAS` {#mc.admin.update.ALIAS}

*mc-cmd*

要更新的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

如果指定的 `ALIAS` 对应的是分布式 MinIO 部署，[`mc admin update`](#command-mc.admin.update) 会同时更新该部署中的 *所有* MinIO 服务器。

使用 [`mc alias list`](/docs/reference/minio-mc/mc-alias-list/#command-mc.alias.list) 查看已配置的别名及其对应的 MinIO 部署端点。

#### `MIRROR_URL` {#mc.admin.update.MIRROR_URL}

*mc-cmd*

目标服务端用于定位 `minio` 二进制的发布清单 URL。仅仅提供 URL 并不能使制品自动可信；使用这条兼容路径前必须核验完整的更新与签名契约。Silo 运维应优先使用文档化的软件包或手工升级流程。

#### `--yes, -y` {#mc.admin.update.-yes}

*mc-cmd*

*Optional*

传入此标志以确认更新，并跳过确认提示。

## 行为 {#id8}

### 二进制压缩 {#id9}

> [!NOTE]
> **变更: RELEASE.2024-01-28T22-35-53Z**
>
> [`mc admin update`](#command-mc.admin.update) 会先压缩二进制，再发送到部署中的所有节点。

此功能不适用于 [systemctl managed deployments](/docs/operations/deployments/baremetal/#minio-baremetal)。