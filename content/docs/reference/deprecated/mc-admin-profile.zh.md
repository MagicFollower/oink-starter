---
title: "mc admin profile"

weight: 170
---

<a id="mc-admin-profile"></a>

<a id="command-mc.admin.profile"></a>

> [!NOTE]
> **说明**
>
> 自 *mc* RELEASE.2023-04-06T16-51-10Z 起，该命令已由 [`mc support profile`](/docs/reference/minio-mc/mc-support-profile/#command-mc.support.profile) 取代。

## 描述 {#id2}

[`mc admin profile`](#command-mc.admin.profile) 命令会生成用于调试的性能分析数据。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

### 性能分析数据格式 {#id3}

[`mc admin profile`](#command-mc.admin.profile) 会生成一个 `ZIP` 归档文件 `profile.zip`， 其中包含一个或多个 `.pprof` 文件。使用 [pprof](https://github.com/google/pprof) `go` 工具读取这些性能分析数据。

## 示例 {#id4}

### 单个资源的性能分析数据 {#id5}

使用 [`mc admin profile start`](#mc.admin.profile.start) 并结合 [`type`](#mc.admin.profile.start.type) 标志开始对该资源进行性能分析：

```shell
mc admin profile start --type "TYPE" ALIAS
```

- 将 [`ALIAS`](#mc.admin.profile.start.TARGET) 替换为 MinIO 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TYPE`](#mc.admin.profile.start.type) 替换为要分析的资源类型。

使用 [`mc admin profile stop`](#mc.admin.profile.stop) 停止对指定资源的性能分析并输出结果：

```shell
mc admin profile stop
```

该命令会将性能分析数据输出为 `profile.zip`。

### 多个资源的性能分析数据 {#id6}

使用 [`mc admin profile start`](#mc.admin.profile.start) 并结合 [`type`](#mc.admin.profile.start.type) 标志开始对这些资源进行性能分析：

```shell
mc admin profile start --type "TYPE,[TYPE...]" ALIAS
```

- 将 [`ALIAS`](#mc.admin.profile.start.TARGET) 替换为 MinIO 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`TYPE`](#mc.admin.profile.start.type) 替换为要分析的资源类型。 多个资源类型请使用逗号分隔列表指定。

使用 [`mc admin profile stop`](#mc.admin.profile.stop) 停止对指定资源的性能分析并输出结果：

```shell
mc admin profile stop
```

该命令会将性能分析数据输出为 `profile.zip`。

## 语法 {#id7}

[`mc admin profile`](#command-mc.admin.profile) 的语法如下：

```shell
mc admin profile SUBCOMMAND
```

[`mc admin profile`](#command-mc.admin.profile) 支持以下子命令：

#### `mc admin profile start` {#mc.admin.profile.start}

*mc-cmd*

在目标 MinIO 部署上开始收集性能分析数据。该命令语法如下：

```shell
mc admin profile start [FLAGS] TARGET
```

[`mc admin profile start`](#mc.admin.profile.start) 支持以下参数：

#### `TARGET` {#mc.admin.profile.start.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将从该部署收集性能分析数据。

#### `type` {#mc.admin.profile.start.type}

*mc-cmd*

从 [`TARGET`](#mc.admin.profile.start.TARGET) MinIO 部署收集的性能分析数据类型。

将以下一个或多个支持的类型以逗号分隔列表形式指定：

- `cpu`
- `mem`
- `block`
- `mutex`
- `trace`
- `threads`
- `goroutines`

省略时默认为 `cpu,mem,block`。

#### `mc admin profile stop` {#mc.admin.profile.stop}

*mc-cmd*

停止性能分析过程，并将收集的数据作为 `profile.zip` 返回。该 `zip` 文件包含一个或多个 `.pprof` 文件，可由 `go` [pprof](https://github.com/google/pprof) 等工具读取。

该命令语法如下：

```shell
mc admin profile stop TARGET
```

该命令支持以下参数：

#### `TARGET` {#mc.admin.profile.stop.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将从该部署返回可用的性能分析数据。