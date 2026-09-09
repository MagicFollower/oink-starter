---
title: "mc admin console"

weight: 130
---

<a id="mc-admin-console"></a>

<a id="command-mc.admin.console"></a>

> [!WARNING]
> **重要**
>
> 此命令已在 [mc RELEASE.2022-12-02T23-48-47Z](https://github.com/minio/mc/releases/tag/RELEASE.2022-12-02T23-48-47Z) 中被 [`mc admin logs`](/docs/reference/minio-mc-admin/mc-admin-logs/#command-mc.admin.logs) 替代。
>
> 该命令此前已在 [mc RELEASE.2022-06-26T18-51-48Z](https://github.com/minio/mc/tree/RELEASE.2022-06-26T18-51-48Z) 中被 `mc support logs show` 替代。

## 描述 {#id2}

[`mc admin console`](#command-mc.admin.console) 命令返回部署中每个 MinIO 服务器的服务端日志条目。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 语法 {#id3}

[`mc admin console`](#command-mc.admin.console) 的语法如下：

```shell
mc admin console [FLAGS] TARGET NODENAME
```

[`mc admin console`](#command-mc.admin.console) 支持以下项：

#### `TARGET` {#mc.admin.console.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将从该部署中检索服务端日志。

#### `NODENAME` {#mc.admin.console.NODENAME}

*mc-cmd*

命令从中检索服务端日志的特定 MinIO 服务器节点。

#### `--limit, l` {#mc.admin.console.-limit}

*mc-cmd*

要显示的最新日志条目数量。默认为 `10`。

#### `--type, t` {#mc.admin.console.-type}

*mc-cmd*

要返回的错误日志类型。以逗号分隔的 `,` 列表形式指定以下一个或多个选项：

- `minio`
- `application`
- `all`（默认）