---
title: "mc support proxy"

weight: 60
---

<a id="mc-support-proxy"></a>

<a id="command-mc.support.proxy"></a>

## 说明 {#id2}

使用 [`mc support proxy`](#command-mc.support.proxy) 命令配置与 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 通信时使用的代理。

## 示例 {#id3}

### 设置代理 URL {#url}

定义部署 `minio1` 与 SUBNET 通信时使用的代理 URL。 此示例中的代理 URL 为 `http://my.proxy`。

```shell
mc support proxy set minio1 http://my.proxy
```

### 删除为部署配置的代理 URL {#id4}

以下命令会删除为别名 `minio1` 配置的代理 URL。

```shell
mc support proxy remove minio1
```

### 禁用 `callhome` 日志 {#callhome}

以下命令显示为别名 `minio1` 配置的代理 URL。

```shell
mc support proxy show minio1
```

## 语法 {#id5}

#### `mc support proxy set` {#mc.support.proxy.set}

*mc-cmd*

为 MinIO 部署创建与 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 通信时使用的代理 URL。

```shell
mc support proxy set ALIAS PROXY_URL
```

#### `mc support proxy show` {#mc.support.proxy.show}

*mc-cmd*

显示当前为与 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 通信配置的代理 URL。

```shell
mc support proxy show ALIAS
```

#### `mc support proxy remove` {#mc.support.proxy.remove}

*mc-cmd*

删除为与 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 通信配置的代理 URL。

```shell
mc support proxy remove ALIAS
```

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。