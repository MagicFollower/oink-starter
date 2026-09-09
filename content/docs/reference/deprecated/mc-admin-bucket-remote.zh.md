---
title: "mc admin bucket remote"

weight: 120
---

<a id="mc-admin-bucket-remote"></a>

<a id="command-mc.admin.bucket.remote"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> - `mc admin bucket remote add` 已替换为 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add)
> - `mc admin bucket remote update` 已替换为 [`mc replicate update`](/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update)
> - `mc admin bucket remote rm` 已替换为 [`mc replicate rm`](/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm)
> - `mc admin bucket remote ls` 已替换为 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls)

> [!NOTE]
> **变更: RELEASE.2023-02-16T19-20-11Z**
>
> - `mc admin bucket remote bandwidth` 已替换为 [`mc replicate status`](/docs/reference/minio-mc/mc-replicate-status/#command-mc.replicate.status)
>
>   与复制相关的统计信息已迁移到 `mc replicate status` 命令。

## 描述 {#id1}

[`mc admin bucket remote`](#command-mc.admin.bucket.remote) 命令用于管理 `ARN` 资源， 供 [`bucket replication`](/docs/reference/minio-mc/mc-replicate/#command-mc.replicate) 使用。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 示例 {#id2}

### 添加新的复制目标 {#id3}

使用 [`mc admin bucket remote add`](#mc.admin.bucket.remote.add) 创建一个新的复制目标 ARN，供 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add) 使用：

```shell
mc admin bucket remote add SOURCE/BUCKET DESTINATION/BUCKET
```

- 将 [`SOURCE`](#mc.admin.bucket.remote.add.SOURCE) 替换为 作为复制目标的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为存储桶完整路径，MinIO 会将来自 `DESTINATION` 的对象复制到该存储桶。
- 将 [`DESTINATION`](#mc.admin.bucket.remote.add.DESTINATION) 替换为 作为复制源的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为存储桶完整路径，MinIO 会从该存储桶复制对象到 `SOURCE`。

### 删除现有复制目标 {#id4}

使用 [`mc admin bucket remote rm`](#mc.admin.bucket.remote.rm) 从存储桶中删除复制目标：

```shell
mc admin bucket remote rm SOURCE/BUCKET --arn ARN
```

- 将 [`SOURCE`](#mc.admin.bucket.remote.rm.SOURCE) 替换为 作为复制源使用的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为 MinIO 复制对象来源存储桶的完整路径。
- 将 [`ARN`](#mc.admin.bucket.remote.rm.ARN) 替换为 远程目标的 ARN。

删除该目标会停止所有正在进行的、 发往该目标的 [`bucket replication`](/docs/reference/minio-mc/mc-replicate/#command-mc.replicate)。

<a id="id5"></a>

### 查询已配置的复制目标 {#minio-retrieve-remote-bucket-targets}

使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 列出存储桶已配置的复制目标：

```shell
mc replicate ls ALIAS/PATH
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-replicate-ls/#mc.replicate.ls.ALIAS) 替换为 作为复制源使用的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `PATH` 替换为 MinIO 复制对象来源存储桶的完整路径。

## 语法 {#id6}

#### `mc admin bucket remote add` {#mc.admin.bucket.remote.add}

*mc-cmd*

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> - `mc admin bucket remote add` 已替换为 [`mc replicate add`](/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add)

在 MinIO 部署上的存储桶中添加远程目标。该命令语法如下：

```shell
mc admin bucket remote add SOURCE DESTINATION --service "replication" [FLAGS]
```

该命令接受以下参数：

#### `SOURCE` {#mc.admin.bucket.remote.add.SOURCE}

*mc-cmd*

*Required*

要添加远程目标的存储桶完整路径。 指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 作为存储桶路径前缀。例如：

```shell
mc admin bucket remote add play/mybucket
```

#### `DESTINATION` {#mc.admin.bucket.remote.add.DESTINATION}

*mc-cmd*

*Required*

目标 MinIO 部署和存储桶。

使用以下格式指定目标 MinIO 部署和存储桶的完整 URL：

```shell
http(s)://ACCESSKEY:SECRETKEY@DESTHOSTNAME/DESTBUCKET
```

- 将 `ACCESSKEY` 替换为目标 MinIO 部署上某个用户的 access key。
- 将 `SECRETKEY` 替换为目标 MinIO 部署上某个用户的 secret key。
- **将 `DESTHOSTNAME` 替换为 MinIO 部署的主机名和端口**

  > （例如 `minio-server.example.net:9000`）。
- 将 `DESTBUCKET` 替换为目标端的存储桶。

#### `--service` {#mc.admin.bucket.remote.add.-service}

*mc-cmd*

*Required*

指定为 `"replication"`。

#### `--region` {#mc.admin.bucket.remote.add.-region}

*mc-cmd*

[`DESTINATION`](#mc.admin.bucket.remote.add.DESTINATION) 的地域。

与 [`add`](#mc.admin.bucket.remote.add) 互斥。

#### `--path` {#mc.admin.bucket.remote.add.-path}

*mc-cmd*

目标服务器支持的存储桶路径查找方式。指定以下之一：

- `on`
- `off`
- `auto`（默认）

与 [`add`](#mc.admin.bucket.remote.add) 互斥。

#### `--sync` {#mc.admin.bucket.remote.add.-sync}

*mc-cmd*

启用同步复制模式，MinIO 会在返回 PUT 对象响应 *之前* 尝试复制对象。 同步复制可能会增加等待 PUT 操作成功返回的时间。

默认情况下，[`mc admin bucket remote add`](#mc.admin.bucket.remote.add) 以异步模式运行， MinIO 会在返回 PUT 对象响应 *之后* 尝试复制对象。

#### `mc admin bucket remote ls` {#mc.admin.bucket.remote.ls}

*mc-cmd*

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> - `mc admin bucket remote ls` 已替换为 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls)

列出 MinIO 部署上与某个存储桶关联的所有远程目标。 使用 `mc admin bucket remote ls --help` 查看用法语法。

#### `mc admin bucket remote rm, remove` {#mc.admin.bucket.remote.rm}

*mc-cmd*

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> - `mc admin bucket remote rm` 已替换为 [`mc replicate rm`](/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm)

删除 MinIO 部署上某个存储桶的远程目标。该命令语法如下：

```shell
mc admin bucket remote rm SOURCE --arn ARN
```

该命令接受以下参数：

#### `SOURCE` {#mc.admin.bucket.remote.rm.SOURCE}

*mc-cmd*

*Required*

要删除远程目标的源存储桶完整路径。 指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 作为存储桶路径前缀。 例如：

```shell
mc admin bucket remote rm play/mybucket
```

#### `ARN` {#mc.admin.bucket.remote.rm.ARN}

*mc-cmd*

*Required*

要从目标存储桶中删除的远程目标 `ARN`。 使用 [`mc admin bucket remote ls`](#mc.admin.bucket.remote.ls) 列出指定存储桶的所有远程目标及其对应的 ARN。