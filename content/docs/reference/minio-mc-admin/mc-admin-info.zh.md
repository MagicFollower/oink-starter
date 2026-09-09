---
title: "mc admin info"

weight: 80
---

<a id="mc-admin-info"></a>

<a id="command-mc.admin.info"></a>

## 描述 {#id2}

[`mc admin info`](#command-mc.admin.info) 命令显示 MinIO 服务器的信息。 对于分布式 MinIO 部署，[`mc admin info`](#command-mc.admin.info) 会显示部署中每个 MinIO 服务器的信息。

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-05-03T11-21-07Z
>
> 命令输出包含集群的 [erasure code](/docs/operations/concepts/erasure-coding/#minio-ec-erasure-set) 设置信息。 该信息在输出中以 `EC:#` 格式显示。

命令输出如下所示：

```text
●  play.min.io
   Uptime: 2 hours
   Version: 2024-05-10T08:24:14Z
   Network: 1/1 OK
   Drives: 4/4 OK
   Pool: 1

Pools:
   1st, Erasure sets: 1, Drives per erasure set: 4

0 B Used, 3 Buckets, 0 Objects
4 drives online, 0 drives offline, EC:1
```

## 示例 {#id3}

以下示例假定 `play` 别名已存在于 [`mc`](/docs/reference/minio-mc/#command-mc) [配置文件](/docs/reference/minio-mc/#mc-configuration) 中。你可以将 `play` 替换为 你首选 S3 兼容部署的别名。

有关别名的更多信息，请参阅 [`mc alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

```shell
mc admin info play
```

## 语法 {#id4}

[`mc admin info`](#command-mc.admin.info) 语法如下：

```shell
mc admin info TARGET      \
              [--offline]
```

将已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 指定为 `TARGET`。

### 参数 {#id5}

##### `TARGET` {#mc.admin.info.TARGET}

*mc-cmd*

*Required*

要显示信息的部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--offline` {#mc.admin.info.-offline}

*mc-cmd*

*Optional*

仅显示离线驱动器或节点。