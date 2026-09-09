---
title: "mc admin replicate"

weight: 140
---

<a id="mc-admin-replicate"></a>
<a id="minio-mc-admin-replicate"></a>

<a id="command-mc.admin.replicate"></a>

> [!NOTE]
> **变更: RELEASE.2023-01-11T03-14-16Z**
>
> - `mc admin replicate edit` renamed to [`mc admin replicate update`](#mc.admin.replicate.update)
> - `mc admin replicate remove` renamed to [`mc admin replicate rm`](#mc.admin.replicate.rm)

## 描述 {#id2}

[`mc admin replicate`](#command-mc.admin.replicate) 命令用于为一组 MinIO 对等站点创建并管理 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview)。

站点复制类似于 active-active 存储桶复制，但适用于多个 MinIO 部署。 在这组站点中，无论 IAM 设置、存储桶或对象发生何种变更，该变更都会在站点复制组中的所有站点间复制。

[存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication) 用于在单个部署内或跨部署将特定存储桶或对象从一个位置镜像到另一个位置，而站点复制会持续将整个 MinIO 站点镜像到其他站点。

在配置站点复制时，[`mc admin replicate`](#command-mc.admin.replicate) 仅支持 [分布式部署](/docs/operations/deployments/installation/#deploy-minio-distributed) 的站点复制。

在初始化新的站点复制配置时，只允许一个部署包含数据。

站点复制会对所有存储桶强制启用 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)，包括现有存储桶以及启动站点复制后新增的任何存储桶。 与仅处理对象最新版本的 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror) 相比，站点复制会完整同步版本化对象。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

[`mc admin replicate`](#command-mc.admin.replicate) 命令包含以下子命令：

| 子命令 | 描述 |
| --- | --- |
| [`mc admin replicate add`](#mc.admin.replicate.add) | 创建新的站点复制配置，或扩展现有配置。 |
| [`mc admin replicate info`](#mc.admin.replicate.info) | 返回站点复制配置信息。 |
| [`mc admin replicate resync`](#mc.admin.replicate.resync) | 当第二个站点丢失数据时，将一个站点中的内容重新同步到第二个站点。 |
| [`mc admin replicate rm`](#mc.admin.replicate.rm) | 删除整个站点复制配置，或将一个或多个对等站点从站点复制中移除。 |
| [`mc admin replicate status`](#mc.admin.replicate.status) | 显示参与站点之间 [可复制数据](/docs/operations/replication/multi-site-replication/#minio-site-replication-what-replicates) 的状态。 |
| [`mc admin replicate update`](#mc.admin.replicate.update) | 修改站点复制配置中指定对等站点的 endpoint。 |

## 语法 {#id3}

#### `mc admin replicate add` {#mc.admin.replicate.add}

*mc-cmd*

创建或扩展站点复制配置。 按 MinIO 的建议，该配置默认使用异步站点复制。

若要启用同步站点复制，请先使用此命令创建复制配置。 然后使用 [`mc admin replicate update --mode sync`](#mc.admin.replicate.update.-mode) 更新配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
假设一个多站点 MinIO 拓扑包含三个独立的 MinIO 部署，使用以下 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)：`minio1`、`minio2` 和 `minio3`。 三个站点之间都具备完整的双向网络访问，并且站点间延迟较低。

```shell
mc admin replicate add minio1 minio2 minio3
```

以下命令将一个现有站点复制配置（包含对等站点 `minio1`、`minio2`、`minio3` 和 `minio4`）扩展到新的对等站点 `minio5`。 `minio5` 不包含任何数据。 请先列出 *所有* 现有对等站点。 最后列出要扩展到的站点。

如果任一现有站点不可达，请先使用 [`mc admin replicate rm`](#mc.admin.replicate.rm) 删除不可达站点，再继续扩展站点复制。

```shell
mc admin replicate add minio1 minio2 minio3 minio4 minio5
```

以下命令创建新的站点复制配置，并在对等站点 `minio1`、`minio2` 和 `minio3` 之间同步 ILM 过期规则。

```shell
mc admin replicate add minio1 minio2 minio3 --replicate-ilm-expiry
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin replicate add      \
                            ALIAS1        \
                            ALIAS2        \
                            [ALIAS3 ...]  \
                            [--replicate-ilm-expiry]
```
{{< /tab >}}
{{< /tabs >}}

#### `ALIAS` {#mc.admin.replicate.add.ALIAS}

*mc-cmd*

*Required*

要纳入站点复制的 MinIO 部署 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

创建站点复制至少需要两个 MinIO 部署别名。 只有第一个别名可以包含存储桶或对象。 第一个站点也可以为空。

要将现有站点复制扩展到一个或多个新站点，请先列出待扩展的站点复制集合中所有现有对等站点的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。 然后再附加一个或多个 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)，将其加入现有站点复制。 新增对等站点必须为空。

#### `--replicate-ilm-expiry` {#mc.admin.replicate.add.-replicate-ilm-expiry}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-02T02-03-28Z

在对等站点间复制 [ILM expiration](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 规则。

#### `mc admin replicate update` {#mc.admin.replicate.update}

*mc-cmd*

修改参与站点复制的现有对等站点所使用的 endpoint。

> [!NOTE]
> **变更: RELEASE.2023-01-11T03-14-16Z**
>
> `mc admin replicate edit` renamed to `mc admin replicate update`.

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
```shell
mc admin replicate update                                                   \
                   minio2                                                 \
                   --deployment-id c1758167-4426-454f-9aae-5c3dfdf6df64   \
                   --endpoint https://minio2:9000
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin replicate update                     \
                            ALIAS                           \
                            --deployment-id [deploymentID]  \
                            --endpoint [newEndpoint]        \
                            --mode ["sync" | "async"]       \
                            --enable-ilm-expiry-replication \
                            --disable-ilm-expiry-replication
```
{{< /tab >}}
{{< /tabs >}}

#### `ALIAS` {#mc.admin.replicate.update.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

#### `--bucket-bandwidth` {#mc.admin.replicate.update.-bucket-bandwidth}

*mc-cmd*

以每秒比特为单位设置存储桶的默认带宽限制。

有效单位包括：

- `B` 表示字节
- `K` 表示千字节
- `M` 表示兆字节
- `G` 表示吉字节
- `T` 表示太字节
- `Ki` 表示 kibibyte
- `Mi` 表示 mibibyte
- `Gi` 表示 gibibyte
- `Ti` 表示 tebibyte

例如，以下命令将 `myminio` 部署上的复制带宽限制为不超过每秒 2 Gigabytes。

```shell
mc admin replicate update myminio --deployment-id c1758167-4426-454f-9aae-5c3dfdf6df64 --bucket-bandwidth "2G"
```

#### `--deployment-id` {#mc.admin.replicate.update.-deployment-id}

*mc-cmd*

*Required*

要修改的部署唯一 ID。

可通过运行 [`mc admin replicate info ALIAS`](#mc.admin.replicate.info.ALIAS) 获取部署 ID

#### `--disable-ilm-expiry-replication` {#mc.admin.replicate.update.-disable-ilm-expiry-replication}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-02T02-03-28Z

停止在对等站点之间复制 ILM 过期规则。 对等站点之间已经同步的现有规则不会从任何对等站点移除。

#### `--enable-ilm-expiry-replication` {#mc.admin.replicate.update.-enable-ilm-expiry-replication}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-02T02-03-28Z

开始在对等站点之间复制 ILM 过期规则。

#### `--endpoint` {#mc.admin.replicate.update.-endpoint}

*mc-cmd*

*Required*

与该对等站点关联的新 endpoint 或 URL。

#### `--mode` {#mc.admin.replicate.update.-mode}

*mc-cmd*

*Optional*

指定 MinIO 对该对等站点执行同步或异步复制操作。 可用值为 `sync` 和 `async`。

默认值为 `async`。

#### `--sync` {#mc.admin.replicate.update.-sync}

*mc-cmd*

*Optional*

> [!WARNING]
> **重要**
>
> `--sync` 标志自 `RELEASE.2023-07-07T05-25-51Z` 起已弃用。 请改用 [`--mode`](#mc.admin.replicate.update.-mode)。

启用或禁用同步站点复制。 可用值为 `enable` 和 `disable`。 若未定义，MinIO 使用异步站点复制。

#### `mc admin replicate rm, remove` {#mc.admin.replicate.rm}

*mc-cmd*

> [!NOTE]
> **变更: RELEASE.2023-01-11T03-14-16Z**
>
> `mc admin replicate remove` 子命令重命名为 `mc admin replicate rm`。

从站点复制配置中移除一个或多个站点。

请注意，如果你打算未来将该站点重新加入站点复制配置，则其必须不包含任何 [可复制数据](/docs/operations/replication/multi-site-replication/#minio-site-replication-what-replicates)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
从包含 *minio2* 的现有站点复制配置中，移除所有已连接站点的站点复制。 这会删除所有参与站点的站点复制配置。

```shell
mc admin replicate rm      \
                   minio2  \
                   --all   \
                   --force
```

从包含 *minio2* 的现有站点复制配置中移除别名为 `minio5` 和 `minio6` 的站点

```shell
mc admin replicate rm      \
                   minio2  \
                   minio5  \
                   minio6  \
                   --force
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin rm          \
                       TARGET      \
                       ALIAS1      \
                       [ALIAS2...] \
                       --all       \
                       --force
```
{{< /tab >}}
{{< /tabs >}}

#### `TARGET` {#mc.admin.replicate.rm.TARGET}

*mc-cmd*

*Required*

要操作的站点复制中，处于活动状态的 MinIO 部署 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。 除非要从站点复制中移除所有站点，否则不要使用待移除部署的别名。

#### `ALIAS` {#mc.admin.replicate.rm.ALIAS}

*mc-cmd*

*Optional*

要从站点复制配置中移除的活动 MinIO 部署 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。 可重复指定以移除更多站点。

#### `--all` {#mc.admin.replicate.rm.-all}

*mc-cmd*

*Optional*

包含此标志可移除为站点复制配置的所有站点，并结束该站点复制配置。

#### `--force` {#mc.admin.replicate.rm.-force}

*mc-cmd*

*Required*

此标志会强制从站点复制配置中移除指定的对等站点。

#### `mc admin replicate info` {#mc.admin.replicate.info}

*mc-cmd*

返回站点复制配置中各站点的信息。

```shell {tab="示例" group="tab1-tab2" value="tab1"}
mc admin replicate info minio1
```

```shell {tab="语法" value="tab2"}
mc [GLOBALFLAGS] admin replicate info ALIAS
```

#### `ALIAS` {#mc.admin.replicate.info.ALIAS}

*mc-cmd*

*Required*

站点复制配置中活动 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

#### `mc admin replicate status` {#mc.admin.replicate.status}

*mc-cmd*

显示站点复制配置中站点、存储桶、用户、组或策略的状态。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
显示包含站点 `minio1` 的站点复制配置的整体复制状态。

```shell
mc admin replicate status minio1
```

显示包含站点 `minio1` 的站点复制配置中，跨站点的存储桶复制状态。

```shell
mc admin replicate status     \
                   minio1     \
                   --buckets
```

显示包含站点 `minio1` 的站点复制配置中，名为 `images` 的存储桶在跨站点间的站点复制状态。

```shell
mc admin replicate status           \
                    minio1          \
                    --bucket images
```

显示包含站点 `minio1` 的站点复制配置中，用户 `janedoe` 设置在跨站点间的站点复制状态。

```shell
mc admin replicate status         \
                   minio1         \
                   --user janedoe
```

上述示例的输出类似如下：

```shell
Bucket replication status:
●  30/30 Buckets in sync

Policy replication status:
●  5/5 Policies in sync

User replication status:
●  3/3 Users in sync

Group replication status:
No Groups present

ILM Expiry Rules replication status:
●  5/5 ILM Expiry Rules in sync

Object replication status:
Replication status since 1 day
Summary:
Replicated:    0 objects (0 B)
Queued:        - 0 objects, (0 B) (avg: 0 objects, 0 B; max: 0 objects, 0 B)
Received:      0 objects (0 B)
```

显示包含站点 `minio1` 的站点复制配置中，规则 ID 为 `ckok9v5b4dtgofkbi6tg` 的 ILM 过期规则在跨站点间的站点复制状态。

```shell
mc admin replicate status minio1 --ilm-expiry-rule ckok9v5b4dtgofkbi6tg
```

输出类似如下：

```shell
●  ILM Expiry Rule replication summary for: ckok9v5b4dtgofkbi6tg

ILMExpiryRule   | MINIO1          | MINIO2
ILM Expiry Rule | ✔               | ✔
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc [GLOBALFLAGS] admin replicate status          \
                   TARGET                        \
                   [--all]                       \
                   [--buckets]                   \
                   [--bucket nameOfBucket]       \
                   [--groups]                    \
                   [--group nameOfGroup]         \
                   [--ilm-expiry-rules]          \
                   [--ilm-expiry-rule <rule ID>] \
                   [--policies]                  \
                   [--policy nameOfPolicy]       \
                   [--users]                     \
                   [--user accessKey]
```
{{< /tab >}}
{{< /tabs >}}

#### `TARGET` {#mc.admin.replicate.status.TARGET}

*mc-cmd*

*Required*

站点复制配置中活动 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。

#### `--all` {#mc.admin.replicate.status.-all}

*mc-cmd*

*Optional*

显示所有可用的站点复制状态信息。

#### `--buckets` {#mc.admin.replicate.status.-buckets}

*mc-cmd*

*Optional*

显示所有存储桶的复制状态。

#### `--bucket` {#mc.admin.replicate.status.-bucket}

*mc-cmd*

*Optional*

在该标志后指定存储桶名称，以显示特定存储桶的复制状态。

#### `--groups` {#mc.admin.replicate.status.-groups}

*mc-cmd*

*Optional*

显示所有组的复制状态。

#### `--group` {#mc.admin.replicate.status.-group}

*mc-cmd*

*Optional*

在该标志后指定组名称，以显示特定组的复制状态。

#### `--ilm-expiry-rules` {#mc.admin.replicate.status.-ilm-expiry-rules}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-02T02-03-28Z

显示 ILM 过期规则的同步信息。

与 [`--ilm-expiry-rule`](#mc.admin.replicate.status.-ilm-expiry-rule) 互斥

#### `--ilm-expiry-rule` {#mc.admin.replicate.status.-ilm-expiry-rule}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-12-02T02-03-28Z

显示指定 ILM 过期规则的复制状态信息。

与 [`--ilm-expiry-rules`](#mc.admin.replicate.status.-ilm-expiry-rules) 互斥

#### `--policies` {#mc.admin.replicate.status.-policies}

*mc-cmd*

*Optional*

显示所有策略的复制状态。

#### `--policy` {#mc.admin.replicate.status.-policy}

*mc-cmd*

*Optional*

在该标志后指定策略名称，以显示特定策略的复制状态。

#### `--users` {#mc.admin.replicate.status.-users}

*mc-cmd*

*Optional*

显示所有用户的复制状态。

#### `--user` {#mc.admin.replicate.status.-user}

*mc-cmd*

*Optional*

在该标志后指定用户名，以显示特定用户的复制状态。

#### `mc admin replicate resync` {#mc.admin.replicate.resync}

*mc-cmd*

在数据丢失场景下，将复制配置中一个站点的数据重新同步到复制配置中的第二个站点。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令启动重新同步过程，将 `minio1` 的数据恢复到 `minio2`

```shell
mc admin replicate resync start minio1 minio2
```

以下命令显示当前进行中的重新同步状态。

```shell
mc admin replicate resync status minio1 minio2
```

以下命令停止进行中的重新同步。

```shell
mc admin replicate resync cancel minio1 minio2
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
```shell
mc [GLOBALFLAGS] admin replicate resync start|status|cancel ALIAS1 ALIAS2
```

- 将 `ALIAS1` 替换为拥有待恢复数据的站点别名。
- 将 `ALIAS2` 替换为需要重新同步数据的站点别名。
{{< /tab >}}
{{< /tabs >}}

#### `start` {#mc.admin.replicate.resync.start}

*mc-cmd*

从拥有数据的一个站点到需要同步的第二个站点，发起新的重新同步流程。

#### `status` {#mc.admin.replicate.resync.status}

*mc-cmd*

显示已配置站点复制的两个站点之间，现有重新同步流程的状态。

#### `cancel` {#mc.admin.replicate.resync.cancel}

*mc-cmd*

结束已配置站点复制的两个站点之间当前进行中的重新同步流程。

#### `alias1` {#mc.admin.replicate.resync.alias1}

*mc-cmd*

站点复制配置中活动 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)，其包含你希望重新同步到另一个站点的数据。

#### `alias2` {#mc.admin.replicate.resync.alias2}

*mc-cmd*

站点复制配置中活动 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)，其需要从另一个站点重新同步数据。

## 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。