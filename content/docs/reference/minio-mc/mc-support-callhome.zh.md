---
title: "mc support callhome"

weight: 10
---

<a id="mc-support-callhome"></a>

<a id="command-mc.support.logs.disable"></a>

<a id="command-mc.support.logs.enable"></a>

<a id="command-mc.support.logs.status"></a>

<a id="command-mc.support.callhome"></a>

## 描述 {#id2}

[`mc support callhome`](#command-mc.support.callhome) 命令用于启用或禁用将部署诊断信息发送到 [MinIO SUBNET](https://min.io/pricing?jmp=docs)。

所有 `mc support` 命令都需要有效的 SUBNET 订阅。

启用后，MinIO 会将诊断信息发送到 SUBNET。

无论注册状态如何，MinIO 默认禁用此功能。 你必须显式启用 `callhome` 功能，信息上传才会开始。

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 语法 {#id3}

#### `mc support callhome enable` {#mc.support.callhome.enable}

*mc-cmd*

开始将部署的诊断信息、日志或两者同时发送到 SUBNET。

```shell
mc support callhome enable    \
                    ALIAS     \
                    [--logs]  \
                    [--diag]
```

> [!NOTE]
> **说明**
>
> SUBNET 不再支持 `--logs` 和 `--diag` 标志，并将在未来版本中移除。

#### `mc support callhome disable` {#mc.support.callhome.disable}

*mc-cmd*

停止将部署的诊断信息、日志或两者同时发送到 SUBNET。

```shell
mc support callhome disable  \
                    ALIAS    \
                    [--logs] \
                    [--diag]
```

> [!NOTE]
> **说明**
>
> SUBNET 不再支持 `--logs` 和 `--diag` 标志，并将在未来版本中移除。

#### `mc support callhome status` {#mc.support.callhome.status}

*mc-cmd*

输出某个部署当前是否将诊断信息、日志或两者同时发送到 SUBNET。

```shell
mc support callhome status   \
                    ALIAS    \
                    [--diag]
```

> [!NOTE]
> **说明**
>
> SUBNET 不再支持 `--diag` 标志，并将在未来版本中移除。

### 参数 {#id4}

##### `ALIAS` {#mc.support.callhome.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--diag` {#mc.support.callhome.-diag}

*mc-cmd*

*Optional*

> [!NOTE]
> **说明**
>
> SUBNET 不再支持此选项，并将在未来版本中移除。

每 24 小时向 SUBNET 发送部署诊断信息，或停止发送。

## 示例 {#id5}

### 启用 `callhome` 上报 {#callhome}

为已注册到 SUBNET 且 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 为 `minio1` 的部署启用向 SUBNET 发送诊断信息。

```shell
mc support callhome enable minio1
```

### 禁用 `callhome` 上报 {#id6}

为已注册到 SUBNET 且 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 为 `minio1` 的部署禁用向 SUBNET 发送诊断信息。

```shell
mc support callhome disable minio1
```

### 显示当前 `callhome` 设置 {#id7}

显示别名为 `minio1` 的部署是否向 SUBNET 发送信息。

```shell
mc support callhome status minio1
```

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。