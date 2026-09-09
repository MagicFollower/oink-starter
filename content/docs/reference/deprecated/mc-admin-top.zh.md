---
title: "mc admin top"

weight: 200
---

<a id="mc-admin-top"></a>

<a id="command-mc.admin.top"></a>

> [!NOTE]
> **变更: RELEASE.2022-08-11T00-30-48Z**
>
> `mc admin top` 已由 [`mc support top`](/docs/reference/minio-mc/mc-support-top/#command-mc.support.top) 替代。

## 描述 {#id2}

[`mc admin top`](#command-mc.admin.top) 命令返回分布式 MinIO 部署的统计信息， 类似于 `top` 命令的输出。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 语法 {#id3}

#### `mc admin top locks` {#mc.admin.top.locks}

*mc-cmd*

返回 MinIO 部署中最早的 10 个锁。

该命令的语法如下：

```shell
mc admin top locks TARGET
```

该命令支持以下参数：

#### `TARGET` {#mc.admin.top.locks.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将从该部署 获取统计信息。

该 alias *必须* 对应分布式（多节点）MinIO 部署。 对于 [single-node single-drive](/zh/glossary/#term-single-node-single-drive) 部署，该命令会返回错误。