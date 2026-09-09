---
title: "mc admin scanner trace"

weight: 20
---

<a id="mc-admin-scanner-trace"></a>

<a id="command-mc.admin.scanner.trace"></a>

## 说明 {#id2}

[`mc admin scanner trace`](#command-mc.admin.scanner.trace) 命令会显示目标 MinIO 部署上发生的 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 相关 API 操作。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例返回 `myminio` 部署上与 scanner 相关的 API 操作列表。

```shell
mc admin scanner trace myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc admin scanner trace ALIAS
                       [--filter-request]            \
                       [--filter-response]           \
                       [--filter-size <value>]       \
                       [--funcname <value>]          \
                       [--node <value>]              \
                       [--path <value>]              \
                       [--response-duration <value>] \
                       [--verbose, -v]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.scanner.trace.ALIAS}

*mc-cmd*

*Required*

要显示其 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) API 操作的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--filter-request` {#mc.admin.scanner.trace.-filter-request}

*mc-cmd*

*Optional*

跟踪请求大小大于指定 [`--filter-size`](#mc.admin.scanner.trace.-filter-size) 值的 scanner 操作或调用。

**必须** 与 [`--filter-size`](#mc.admin.scanner.trace.-filter-size) 标志配合使用。

##### `--filter-response` {#mc.admin.scanner.trace.-filter-response}

*mc-cmd*

*Optional*

跟踪响应大小大于指定 [`--filter-size`](#mc.admin.scanner.trace.-filter-size) 值的 scanner 操作或调用。

**必须** 与 [`--filter-size`](#mc.admin.scanner.trace.-filter-size) 标志配合使用。

##### `--filter-size` {#mc.admin.scanner.trace.-filter-size}

*mc-cmd*

*Optional*

将输出过滤为请求大小或响应大小大于指定大小的条目。

必须与 [`--filter-request`](#mc.admin.scanner.trace.-filter-request) 或 [`--filter-response`](#mc.admin.scanner.trace.-filter-response) 标志之一配合使用。

有效单位包括：

| 后缀 | 单位大小 |
| --- | --- |
| `k` | KB（Kilobyte，1000 Bytes） |
| `m` | MB（Megabyte，1000 Kilobytes） |
| `g` | GB（Gigabyte，1000 Megabytes） |
| `t` | TB（Terabyte，1000 Gigabytes） |
| `ki` | KiB（Kibibyte，1024 Bytes） |
| `mi` | MiB（Mebibyte，1024 Kibibytes） |
| `gi` | GiB（Gibibyte，1024 Mebibytes） |
| `ti` | TiB（Tebibyte，1024 Gibibytes） |

##### `--funcname` {#mc.admin.scanner.trace.-funcname}

*mc-cmd*

*Optional*

返回与输入函数名对应的调用。

##### `--node` {#mc.admin.scanner.trace.-node}

*mc-cmd*

*Optional*

返回指定服务器的调用。

##### `--path` {#mc.admin.scanner.trace.-path}

*mc-cmd*

*Optional*

返回指定路径的调用。

##### `--response-duration` {#mc.admin.scanner.trace.-response-duration}

*mc-cmd*

*Optional*

跟踪响应持续时间大于指定值的调用。

##### `--verbose, -v` {#mc.admin.scanner.trace.-verbose}

*mc-cmd*

*Optional*

返回详细输出。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 监控所有 scanner API 操作 {#scanner-api}

使用 [`mc admin scanner trace`](#command-mc.admin.scanner.trace) 监控别名为 `myminio` 的 MinIO 部署上的 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) API 操作：

```shell
mc admin scanner trace myminio
```

### 显示特定路径的 scanner 跟踪 {#scanner}

使用 [`mc admin scanner trace`](#command-mc.admin.scanner.trace) 监控别名为 `myminio` 的部署上路径 `my-bucket/my-prefix/*` 的 API 操作：

```shell
mc admin scanner trace --path my-bucket/my-prefix/* myminio
```

### 显示 `scanObject` 函数的 scanner API 操作 {#scanobject-scanner-api}

监控 `myminio` 部署上 `scanObject` 函数的 scanner 活动：

```shell
mc admin scanner trace --funcname=scanner.ScanObject myminio
```

### 显示大于 `1MB` 的 scanner 操作请求 {#mb-scanner}

使用 [`mc admin scanner trace`](#command-mc.admin.scanner.trace) 监控 `myminio` 部署上大于 `1MB` 的请求：

```shell
mc admin scanner trace --filter-request --filter-size 1MB myminio
```

### 显示大于 `1MB` 的 scanner 操作响应 {#id6}

使用 [`mc admin scanner trace`](#command-mc.admin.scanner.trace) 监控较大的响应大小：

```shell
mc admin scanner trace --filter-response --filter-size 1MB myminio
```

### 显示持续超过五毫秒的 scanner 操作 {#id7}

使用 [`mc admin scanner trace`](#command-mc.admin.scanner.trace) 监控耗时较长的操作：

```shell
mc admin scanner trace --response-duration 5ms myminio
```