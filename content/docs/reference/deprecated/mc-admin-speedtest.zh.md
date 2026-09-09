---
title: "mc admin speedtest"

weight: 180
---

<a id="mc-admin-speedtest"></a>

<a id="command-mc.admin.speedtest"></a>

> [!NOTE]
> **变更: RELEASE.2022-07-24T02-25-13Z**
>
> `mc admin speedtest` 已由 [`mc support perf`](/docs/reference/minio-mc/mc-support-perf/#command-mc.support.perf) 替代。

## 描述 {#id1}

[`mc admin speedtest`](#command-mc.admin.speedtest) 命令通过 `PUT` 和 `GET` 操作测试每个主机的吞吐量。

[`speedtest`](#command-mc.admin.speedtest) 从 `mc` [RELEASE.2021-09-02T09-21-27Z](https://github.com/minio/mc/releases/tag/RELEASE.2021-09-02T09-21-27Z) 开始可用，并支持运行 [RELEASE.2021-07-30T00-02-00Z](https://github.com/minio/minio/releases/tag/RELEASE.2021-07-30T00-02-00Z) 或更高版本的分布式 MinIO 部署。

[`speedtest`](#command-mc.admin.speedtest) 不支持独立部署或 MinIO Gateway 部署。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 语法 {#id2}

[`mc admin speedtest`](#command-mc.admin.speedtest) 使用以下语法：

```shell
mc admin speedtest [FLAGS] TARGET
```

[`mc admin speedtest`](#command-mc.admin.speedtest) 支持以下参数：

#### `TARGET` {#mc.admin.speedtest.TARGET}

*mc-cmd*

*必需*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于执行 speedtest。

#### `--duration` {#mc.admin.speedtest.-duration}

*mc-cmd*

整个 speedtest 的运行时长。默认为 `10s`。

#### `--size` {#mc.admin.speedtest.-size}

*mc-cmd*

用于上传/下载的对象大小。默认为 `64MiB`。

#### `--concurrent` {#mc.admin.speedtest.-concurrent}

*mc-cmd*

每个服务器的并发请求数。默认为 `32`。