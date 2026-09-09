---
title: "mc support perf"

weight: 40
---

<a id="mc-support-perf"></a>

<a id="command-mc.support.perf"></a>

> [!NOTE]
> **变更: RELEASE.2022-07-24T02-25-13Z**
>
> `mc support perf` 替代 `mc admin speedtest` 命令。

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 描述 {#id2}

使用 [`mc support perf`](#command-mc.support.perf) 命令可检查 S3 API（读/写）、网络 IO 和存储（磁盘读/写）的性能。

测试结果可为部署在 S3 `GET` 和 `PUT` 请求下的性能提供总体参考，并识别潜在瓶颈。 如需更完整的性能测试，建议结合预发应用环境中的负载测试与 MinIO [WARP](https://github.com/minio/warp)<a id="warp"></a> S3 基准测试工具。

[`mc support perf`](#command-mc.support.perf) 包含以下子命令

1. [`drive`](#mc.support.perf.drive)

   测量 MinIO 部署中磁盘的速度。

   [`mc support perf drive`](#mc.support.perf.drive) 在测试期间会临时暂停 S3 API 调用。 命令运行期间，传入请求会保存在队列中。 命令完成或结束后，MinIO 会处理排队请求并恢复正常运行。
2. [`object`](#mc.support.perf.object)

   测量集群中对象读写速度。
3. [`net`](#mc.support.perf.net)

   测量所有节点的网络吞吐量。

   [`mc support perf net`](#mc.support.perf.net) 在测试期间会临时暂停 S3 API 调用。 命令运行期间，传入请求会保存在队列中。 命令完成或结束后，MinIO 会处理排队请求并恢复正常运行。
4. [`client`](#mc.support.perf.client)

   测量到客户端的网络吞吐量。
5. [`site-replication`](#mc.support.perf.site-replication)

   测量站点复制操作的速度。

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 示例 {#id3}

### 测量对象速度 {#id4}

在别名 `minio1` 上，测量某个对象的 S3 读写性能。 MinIO 会自动调优并发度，以获得最大吞吐量和 IOPS（Input/Output Per Second）。

```shell
mc support perf object minio1
```

### 在指定时长内测量指定大小对象的速度 {#id5}

在别名 `minio1` 上，对大小为 128MiB 的对象运行 20 秒的 S3 读写性能测试。 MinIO 会自动调优并发度以获得最大吞吐量。

```shell
mc support perf object minio1 --duration 20s --size 128MiB
```

### 使用默认规格测试所有节点上的全部磁盘速度 {#id6}

在别名为 `minio1` 的集群上，对所有节点上的所有磁盘执行读写性能测量。 该命令未指定 blocksize，因此使用默认值 4MiB。

```shell
mc support perf drive minio1
```

### 使用自定义规格测试磁盘速度 {#id7}

在别名为 `minio1` 的集群上执行磁盘读写性能测量，指定 blocksize 为 64KiB，且每个磁盘读写数据量为 2GiB。

```shell
mc support perf drive minio1 --blocksize 64KiB --filesize 2GiB
```

### 测试网络吞吐量 {#id8}

在别名为 `minio1` 的集群上运行网络吞吐量测试。

```shell
mc support perf net minio1
```

### 测试站点复制速度 {#id9}

测试站点 `minio1` 到其他已配置对等站点的站点复制操作速度。

```shell
mc support perf site-replication minio1
```

## 语法 {#id10}

#### `mc support perf drive` {#mc.support.perf.drive}

*mc-cmd*

测量集群中磁盘的读写速度。

```shell
mc [GLOBAL FLAGS] support perf drive   \
                [--concurrent]         \
                [--verbose, -v]        \
                [--filesize]           \
                [--blocksize]          \
                [--serial]             \
                [--airgap]             \
                ALIAS
```

#### `mc support perf object` {#mc.support.perf.object}

*mc-cmd*

测量集群中对象读写的 S3 性能。

```shell
mc [GLOBAL FLAGS] support perf object  \
                [--size]               \
                [--concurrent]         \
                [--verbose, -v]        \
                [--airgap]             \
                ALIAS
```

#### `mc support perf net` {#mc.support.perf.net}

*mc-cmd*

测量集群中所有节点的网络吞吐量。

```shell
mc [GLOBAL FLAGS] support perf net  \
                [--concurrent]      \
                [--verbose, -v]     \
                [--serial]          \
                [--airgap]          \
                ALIAS
```

#### `mc support perf client` {#mc.support.perf.client}

*mc-cmd*

测量运行 MinIO Client 的本地设备到服务器的网络吞吐量。

```shell
mc [GLOBAL FLAGS] support perf client  \
                --duration             \
                [--verbose, -v]        \
                [--airgap]             \
                ALIAS
```

#### `mc support perf site-replication` {#mc.support.perf.site-replication}

*mc-cmd*

测量从指定 `ALIAS` 到其他已配置对等站点的站点复制操作速度。

```shell
mc [GLOBAL FLAGS] support perf site-replication \
                  --duration                    \
                  [--verbose, -v]               \
                  ALIAS
```

### 参数 {#id11}

##### `--airgap` {#mc.support.perf.-airgap}

*mc-cmd*

*Optional*

用于无法通过网络访问 SUBNET 的环境（例如 airgapped、受防火墙限制或类似配置）。

如果部署本身是 airgapped，但你使用 [minio client](/docs/reference/minio-mc/#minio-client) 的本地设备可以访问网络，则无需使用 `--airgap` 标志。

##### `--size` {#mc.support.perf.-size}

*mc-cmd*

*Optional*

适用于 [`object`](#mc.support.perf.object) 命令。

指定上传和下载性能测试所使用的对象大小。

未指定时，默认值为 `64MiB`。

使用 `--size <value>`，其中 `<value>` 为数字加存储单位 `KiB`、`MiB` 或 `GiB`。

##### `--concurrent` {#mc.support.perf.-concurrent}

*mc-cmd*

*Optional*

适用于 [`drive`](#mc.support.perf.drive)、[`object`](#mc.support.perf.object) 和 [`net`](#mc.support.perf.net) 命令。

指定每台服务器用于测试的并发请求数。

未指定时，默认值为 `32`。

使用 `--concurrent <value>`，其中 `<value>` 为数字。

##### `--verbose, -v` {#mc.support.perf.-verbose}

*mc-cmd*

*Optional*

适用于 [`drive`](#mc.support.perf.drive)、[`object`](#mc.support.perf.object) 和 [`net`](#mc.support.perf.net) 命令。

在输出中显示每台服务器的统计信息。

##### `--filesize` {#mc.support.perf.-filesize}

*mc-cmd*

*Optional*

适用于 [`drive`](#mc.support.perf.drive) 命令。

指定每个磁盘读取或写入的数据总量。

未指定时，默认值为 `1GiB`。

使用 `--filesize <value>`，其中 `<value>` 为数字和存储单位 `KiB`、`MiB` 或 `GiB`。

##### `--blocksize` {#mc.support.perf.-blocksize}

*mc-cmd*

*Optional*

适用于 [`drive`](#mc.support.perf.drive) 命令。

指定读写块大小。

未指定时，默认值为 `4MiB`。

使用 `--filesize <value>`，其中 `<value>` 为数字和存储单位，使用标准存储单位缩写。

##### `--serial` {#mc.support.perf.-serial}

*mc-cmd*

*Optional*

适用于 [`drive`](#mc.support.perf.drive) 和 [`net`](#mc.support.perf.net) 命令。

逐个对磁盘执行性能测试。

##### `ALIAS` {#mc.support.perf.ALIAS}

*mc-cmd*

*Required*

适用于 [`drive`](#mc.support.perf.drive)、[`object`](#mc.support.perf.object)、[`net`](#mc.support.perf.net) 和 [`client`](#mc.support.perf.client) 命令。

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--duration` {#mc.support.perf.-duration}

*mc-cmd*

*Required*

适用于 [`client`](#mc.support.perf.client) 命令。

执行测试的时长（秒）。 时间不能为 *0* 或负数。

### 全局标志 {#id12}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。