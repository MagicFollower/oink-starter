---
title: "mc support top"

weight: 70
icon: fa-solid fa-ranking-star
---

<a id="mc-support-top"></a>

<a id="command-mc.support.top"></a>

> [!NOTE]
> **说明**
>
> > [!NOTE]
> > **变更: RELEASE.2022-08-11T00-30-48Z**
>
> `mc support top` 替代 `mc admin top` 命令。

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 描述 {#id2}

[`mc support top`](#command-mc.support.top) 命令返回分布式 MinIO 部署的统计信息， 类似于 shell 中 `top` 命令的输出。

> [!NOTE]
> **说明**
>
> [`mc support top`](#command-mc.support.top) 不支持单节点单驱动 MinIO 部署。

[`mc support top`](#command-mc.support.top) 具有以下子命令：

- [`api`](/docs/reference/minio-mc/mc-support-top-api/#command-mc.support.top.api)
- [`locks`](/docs/reference/minio-mc/mc-support-top-locks/#command-mc.support.top.locks)
- [`disk`](/docs/reference/minio-mc/mc-support-top-disk/#command-mc.support.top.disk)
- [`net`](/docs/reference/minio-mc/mc-support-top-net/#command-mc.support.top.net)
- [`rpc`](/docs/reference/minio-mc/mc-support-top-rpc/#command-mc.support.top.rpc)

有关每个子命令的详细信息，请参阅上方链接的页面。

## 语法 {#id3}

该命令的语法如下：

```shell
mc support top COMMAND [COMMAND FLAGS] [ARGUMENTS ...]
```