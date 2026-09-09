---
title: "mc admin logs"

weight: 100
---

<a id="mc-admin-logs"></a>

<a id="command-mc.support.logs.show"></a>

<a id="command-mc.admin.logs"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

> [!NOTE]
> **变更: RELEASE.2022-12-02T23-48-47Z**
>
> `mc support logs` 已迁移至 `mc admin logs`，并提供了更简化的命令接口，用于显示 MinIO 部署的服务器日志。
>
> 对于由 systemd 管理的部署，其输出与 `journalctl -uf minio` 提供的内容类似。

## 描述 {#id2}

使用 [`mc admin logs`](#command-mc.admin.logs) 命令显示 MinIO 服务器日志。

上传功能默认保持禁用，只有在某个部署上明确选择加入后才会启用。 如果已经启用，你可以随时使用 [`mc support callhome disable`](/docs/reference/minio-mc/mc-support-callhome/#mc.support.callhome.disable) 关闭该功能。

## 示例 {#id3}

### 显示某个部署的日志 {#id4}

以下命令显示别名为 `minio1` 的部署中任意类型的最近 10 条服务器日志。

```shell
mc admin logs minio1
```

### 显示某个节点最近 5 条日志条目 {#id5}

以下命令显示别名为 `minio1` 的部署中 `node1` 节点最近的 5 条日志条目。

```shell
mc admin logs --last 5 myminio node1
```

### 显示某个部署的 application 类型日志条目 {#application}

以下命令显示别名为 `minio1` 的部署中所有节点的 `application` 类型日志条目。

```shell
mc admin logs --type application minio1
```

## 语法 {#id6}

命令语法如下：

```shell
mc admin logs [GLOBAL FLAGS]     \
              [--last, -l value] \
              [--type, -t value] \
              ALIAS              \
              [NODE]
```

### 参数 {#id7}

##### `ALIAS` {#mc.admin.logs.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--last, -l` {#mc.admin.logs.-last}

*mc-cmd*

*Optional*

仅显示最近指定数量的日志条目。

如果不包含此标志，则最多显示最近 10 条日志条目。

##### `--type, --type` {#mc.admin.logs.-type}

*mc-cmd*

*Optional*

列出指定类型的日志条目。 有效类型为 `minio`、`application` 或 `all`。

如果未指定，则显示所有类型的日志条目。

##### `NODE` {#mc.admin.logs.NODE}

*mc-cmd*

*Optional*

在分布式部署中，输入节点名称以指定要显示其日志的节点。

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。