---
title: "mc admin rebalance"

weight: 130
---

<a id="mc-admin-rebalance"></a>
<a id="minio-mc-admin-rebalance"></a>

<a id="command-mc.admin.rebalance"></a>

## 权限 {#id2}

执行此命令的用户必须拥有该部署的 [`admin:Rebalance`](/docs/administration/identity-access-management/policy-based-access-control/#policy-action.admin-Rebalance) [策略操作](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

## 描述 {#id3}

[`mc admin rebalance`](#command-mc.admin.rebalance) 命令可用于在 MinIO 部署上启动、监控或停止再平衡操作。 再平衡会在部署中的所有池之间重新分配对象。

当新增 服务器池 时，MinIO 不会自动对对象执行再平衡。 相反，MinIO 会将 [新对象写入](/docs/operations/deployments/baremetal-expand-minio-deployment/#minio-writing-files) 相较于部署中其他可用池可用空间更多的池。 触发手动再平衡流程会促使 MinIO 扫描整个部署，并按需移动对象，以使所有池的可用空间大致相当。

这是一项开销大且耗时的操作。 建议仅在部署负载较轻或空闲时运行再平衡流程。 如果在再平衡期间发生写操作，这些写操作会并行处理，并写入当前未参与再平衡的池。

你可以停止再平衡，并在之后按需重新启动。

使用以下命令跟踪正在进行的再平衡操作进度：

```shell
mc admin trace --call rebalance ALIAS
```

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

[`mc admin rebalance`](#command-mc.admin.rebalance) 命令具有以下子命令：

| 子命令 | 说明 |
| --- | --- |
| [`mc admin rebalance start`](#mc.admin.rebalance.start) | 在 MinIO 部署上启动再平衡操作。 |
| [`mc admin rebalance status`](#mc.admin.rebalance.status) | 输出正在进行的再平衡操作的当前状态。 |
| [`mc admin rebalance stop`](#mc.admin.rebalance.stop) | 停止正在进行中的再平衡操作。 |

## 语法 {#id4}

#### `mc admin rebalance start` {#mc.admin.rebalance.start}

*mc-cmd*

为 MinIO 部署启动再平衡操作。

{{< tabs group="examples-syntax" >}}
{{< tab label="EXAMPLES" value="examples" >}}
假设一个 MinIO 部署有两个池，并分配了别名 `minio1`。 其中一个池有 250 GB 可用空间，另一个池有 3 TB 可用空间。

[`mc admin rebalance`](#command-mc.admin.rebalance) 命令会将对象从可用空间较少的池迁移到可用空间较多的池，使两个池的可用空间大致相等。

```shell
mc admin rebalance start minio1
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin rebalance start ALIAS
```

- 将 ALIAS 替换为要执行再平衡的 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

#### `mc admin rebalance status` {#mc.admin.rebalance.status}

*mc-cmd*

查询具有活动再平衡进程的部署，并返回该再平衡进程的状态信息。

状态输出包括再平衡操作 ID、操作时间，以及部署中每个池的详细信息。 对每个池，状态会显示池 ID、该池的再平衡状态、已用空间百分比以及该池的再平衡进度。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
```shell
mc admin rebalance status minio1
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin rebalance ALIAS
```

- 将 ALIAS 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

#### `mc admin rebalance stop` {#mc.admin.rebalance.stop}

*mc-cmd*

结束指定部署上正在进行中的再平衡任务。

{{< tabs group="examples-syntax" >}}
{{< tab label="EXAMPLES" value="examples" >}}
```shell
mc admin rebalance stop minio1
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin rebalance stop ALIAS
```

- 将 ALIAS 替换为 MinIO 部署的 [别名](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

## 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id6}

### 先备份集群设置 {#id7}

在开始下线操作前，使用 [`mc admin cluster bucket export`](/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export) 和 [`mc admin cluster iam export`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export) 命令分别对存储桶元数据和 IAM 配置进行快照。 必要时可使用这些快照恢复存储桶/IAM 设置，以便从用户或进程错误中恢复。

### 再平衡会忽略已过期对象和尾部 `DeleteMarker` {#deletemarker}

从 [RELEASE.2023-06-23T20-26-00Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-06-23T20-26-00Z) 开始，再平衡会忽略那些基于父存储桶已配置的 [生命周期规则](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 而过期的对象版本。

再平衡还会忽略仅剩余版本为 [删除标记](/docs/administration/object-management/object-versioning/#minio-bucket-versioning-delete) 的对象。 这可避免对已被视为完全删除的对象执行跨池 <abbr title="Input/Output">I/O</abbr>。

MinIO 依赖 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 来识别并清理这些过期对象或尾部 `DeleteMarker` 对象。