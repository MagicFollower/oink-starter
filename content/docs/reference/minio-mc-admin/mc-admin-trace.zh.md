---
title: "mc admin trace"

weight: 170
---

<a id="mc-admin-trace"></a>

<a id="command-mc.admin.trace"></a>

## 说明 {#id2}

[`mc admin trace`](#command-mc.admin.trace) 命令显示目标 MinIO 部署上发生的 API 操作。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 示例 {#id3}

### 监控所有 API 操作 {#api}

使用 [`mc admin trace`](#command-mc.admin.trace) 监控 MinIO 部署上的 API 操作：

```shell
mc admin trace -a ALIAS
```

- 将 [`ALIAS`](#mc.admin.trace.TARGET) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

### 查看返回 503 错误的调用 {#id4}

使用 [`mc admin trace`](#command-mc.admin.trace) 监控返回 503 Service Unavailable 错误的 API 操作：

```shell
mc admin trace -v --status-code 503 ALIAS
```

- 将 [`ALIAS`](#mc.admin.trace.TARGET) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

### 查看指定路径的控制台跟踪 {#id5}

使用 [`mc admin trace`](#command-mc.admin.trace) 监控指定路径的活动：

```shell
mc admin trace --path my-bucket/my-prefix/* ALIAS
```

- 将 [`ALIAS`](#mc.admin.trace.TARGET) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `my-bucket/my-prefix/*` 替换为你要跟踪的存储桶、前缀和对象名称或通配符。

### 查看响应大小大于 1Mb 的控制台跟踪 {#mb}

使用 [`mc admin trace`](#command-mc.admin.trace) 监控超过指定大小的响应：

```shell
mc admin trace --filter-response --filter-size 1Mb ALIAS
```

- 将 [`ALIAS`](#mc.admin.trace.TARGET) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `1Mb` 替换为所需的响应大小。

### 查看请求操作时长大于 5ms 的控制台跟踪 {#ms}

使用 [`mc admin trace`](#command-mc.admin.trace) 监控耗时较长的操作：

```shell
mc admin trace --filter-duration --filter-size 5ms ALIAS
```

- 将 [`ALIAS`](#mc.admin.trace.TARGET) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

## 语法 {#id6}

[`mc admin trace`](#command-mc.admin.trace) 的语法如下：

```shell
mc admin trace [FLAGS] TARGET
```

[`mc admin trace`](#command-mc.admin.trace) 支持以下参数：

#### `TARGET` {#mc.admin.trace.TARGET}

*mc-cmd*

指定已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于监控其 API 操作。

#### `--all, a` {#mc.admin.trace.-all}

*mc-cmd*

返回 MinIO 部署上的所有流量，包括 MinIO 服务器之间的节点间流量。

#### `--call` {#mc.admin.trace.-call}

*mc-cmd*

仅跟踪匹配的客户端操作或调用类型。 例如，以下命令仅跟踪 `scanner` 类型的操作。

```shell
mc admin trace --call scanner TARGET
```

有效的调用类型包括：

- `batch-keyrotation`
- `batch-replication`
- `bootstrap`
- `decommission`
- `ftp`
- `healing`
- `ilm`
- `internal`
- `os`
- `rebalance`
- `replication-resync`
- `s3`
- `scanner`
- `storage`

如果未指定，MinIO 返回 `s3` 类型的调用。

#### `--errors, e` {#mc.admin.trace.-errors}

*mc-cmd*

仅返回失败的 API 操作。

#### `--filter-request` {#mc.admin.trace.-filter-request}

*mc-cmd*

跟踪请求大小大于指定 [`--filter-size`](#mc.admin.trace.-filter-size) 值的客户端操作或调用。

必须与 [`--filter-size`](#mc.admin.trace.-filter-size) 标志一起使用。

#### `--filter-response` {#mc.admin.trace.-filter-response}

*mc-cmd*

跟踪响应大小大于指定 [`--filter-size`](#mc.admin.trace.-filter-size) 值的客户端操作或调用。

必须与 [`--filter-size`](#mc.admin.trace.-filter-size) 标志一起使用。

#### `--filter-size` {#mc.admin.trace.-filter-size}

*mc-cmd*

过滤后的客户端操作或调用的大小限制。

必须与 [`--filter-request`](#mc.admin.trace.-filter-request) 或 [`--filter-response`](#mc.admin.trace.-filter-response) 标志之一一起使用。

有效单位包括：

| 后缀 | 单位大小 |
| --- | --- |
| `k` | KB（Kilobyte，1000 Bytes） |
| `m` | MB（Megabyte，1000 Kilobytes） |
| `g` | GB（Gigabyte，1000 Megabytes） |
| `t` | TB（Terrabyte，1000 Gigabytes） |
| `ki` | KiB（Kibibyte，1024 Bites） |
| `mi` | MiB（Mebibyte，1024 Kibibytes） |
| `gi` | GiB（Gibibyte，1024 Mebibytes） |
| `ti` | TiB（Tebibyte，1024 Gibibytes） |

#### `--funcname` {#mc.admin.trace.-funcname}

*mc-cmd*

返回输入函数名对应的调用。

#### `--method` {#mc.admin.trace.-method}

*mc-cmd*

返回指定 HTTP 方法的调用。

#### `--node` {#mc.admin.trace.-node}

*mc-cmd*

返回指定服务器的调用。

#### `--path` {#mc.admin.trace.-path}

*mc-cmd*

返回指定路径的调用。

#### `--request-header` {#mc.admin.trace.-request-header}

*mc-cmd*

返回与提供的请求头匹配的调用。

#### `--request-query` {#mc.admin.trace.-request-query}

*mc-cmd*

返回与提供的请求查询参数匹配的调用。 此调试选项只能在 MinIO Support 指导下使用。

#### `--response-duration` {#mc.admin.trace.-response-duration}

*mc-cmd*

跟踪响应时长大于指定值的调用。

#### `--response-threshold` {#mc.admin.trace.-response-threshold}

*mc-cmd*

接受时间字符串作为值，例如 `5ms`。 仅返回响应时间大于所提供阈值的调用。

如果未指定，MinIO 返回响应时间大于 5ms 的调用。

#### `--status-code` {#mc.admin.trace.-status-code}

*mc-cmd*

返回指定 HTTP 状态码的调用。

#### `--stats` {#mc.admin.trace.-stats}

*mc-cmd*

在当前跟踪会话期间，为每个被跟踪的函数调用累积聚合统计信息。

输出表包含以下列。

<table>
  <tbody>
    <tr>
      <td><p>Call</p></td>
      <td><p>捕获到的客户端操作或函数名称。</p></td>
    </tr>
    <tr>
      <td><p>Count</p></td>
      <td><p>客户端操作或调用发生的次数。</p></td>
    </tr>
    <tr>
      <td><p>RPM</p></td>
      <td><p>客户端操作或调用的每分钟速率（Rate Per Minute，RPM）。</p></td>
    </tr>
    <tr>
      <td><p>Avg Time</p></td>
      <td><p>客户端操作或调用完成所需的平均时间。</p></td>
    </tr>
    <tr>
      <td><p>Min Time</p></td>
      <td><p>客户端操作或调用完成所用的最短时间。</p></td>
    </tr>
    <tr>
      <td><p>Max Time</p></td>
      <td><p>客户端操作或调用完成所用的最长时间。</p></td>
    </tr>
    <tr>
      <td><p>Avg TTFB</p></td>
      <td><aside class="alert alert-info"><p><strong>新增: RELEASE.2023-11-15T22-45-58Z</strong></p></aside><p>客户端操作或调用响应的平均首字节时间（Time To First Byte，TTFB）。</p></td>
    </tr>
    <tr>
      <td><p>Max TTFB</p></td>
      <td><aside class="alert alert-info"><p><strong>新增: RELEASE.2023-11-15T22-45-58Z</strong></p></aside><p>客户端操作或调用响应的最大首字节时间。</p></td>
    </tr>
    <tr>
      <td><p>Avg Size</p></td>
      <td><p>客户端操作或调用响应的平均大小。</p></td>
    </tr>
    <tr>
      <td><p>Errors</p></td>
      <td><p>因错误失败的客户端操作或调用数量。</p></td>
    </tr>
    <tr>
      <td><p>RX Avg</p></td>
      <td><p>客户端操作或调用的平均接收字节数（Bytes Received，RX）。
此统计仅在值不为零（0）时显示。</p></td>
    </tr>
    <tr>
      <td><p>TX AVG</p></td>
      <td><p>客户端操作或调用的平均发送字节数（Bytes Sent，TX）。
此统计仅在值不为零（0）时显示。</p></td>
    </tr>
  </tbody>
</table>

累积统计信息，例如名称、计数、持续时间、最短时间、最长时间、首字节时间或错误。 最多累积 15 条统计条目。

#### `--verbose` {#mc.admin.trace.-verbose}

*mc-cmd*

返回详细输出。

### 全局标志 {#id7}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。