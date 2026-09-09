---
title: "mc admin prometheus metrics"

weight: 20
---

<a id="mc-admin-prometheus-metrics"></a>

<a id="command-mc.admin.prometheus.metrics"></a>

## 说明 {#id2}

[`mc admin prometheus metrics`](#command-mc.admin.prometheus.metrics) 命令用于输出集群的 Prometheus 指标。

输出还包含每个指标的附加信息，例如其值类型是 `counter` 还是 `gauge`。

有关将 MinIO 与 Prometheus 配合使用的完整文档，请参阅 [How to monitor MinIO server with Prometheus](/docs/operations/monitoring/collect-minio-metrics-using-prometheus/#minio-metrics-collect-using-prometheus)

从 MinIO 服务端 [RELEASE.2024-07-15T19-02-30Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-07-15T19-02-30Z) 和 MinIO 客户端 [RELEASE.2024-07-11T18-01-28Z](https://github.com/minio/mc/releases/tag/RELEASE.2024-07-11T18-01-28Z) 开始，[metrics version 3 (v3)](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts) 提供了额外的端点和指标。 要输出 v3 指标，请使用 `--api_version v3` 选项。

MinIO 建议新部署使用 [version 3 (v3)](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)。 现有部署可以继续使用 [metrics version 2](/docs/operations/monitoring/metrics-v2/#minio-metrics-v2)。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令输出 [alias](/zh/glossary/#term-alias) `myminio` 对应部署的集群指标：

```shell
mc admin prometheus metrics myminio cluster
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin prometheus metrics  \
                                  ALIAS                                           \
                                  [TYPE]                                          \
                                  [--api_version v3]                              \
                                  [--bucket <bucket name>]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.prometheus.metrics.ALIAS}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将输出该部署的指标。

##### `--api-version` {#mc.admin.prometheus.metrics.-api-version}

*mc-cmd*

*Optional*

要输出 [version 3 (v3)](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts) 指标，请添加 `--api-version v3` 参数。 `v3` 是唯一接受的值。

省略 `--api-version` 则输出 [version 2 (v2)](/docs/operations/monitoring/metrics-v2/#minio-metrics-v2) 指标。

##### `--bucket` {#mc.admin.prometheus.metrics.-bucket}

*mc-cmd*

*Optional*

需要 [`--api-version`](#mc.admin.prometheus.metrics.-api-version)。 对于返回存储桶级指标的 v3 指标类型，需指定存储桶名称。

`--bucket` 适用于以下 v3 指标类型：

- `api`
- `replication`

以下示例输出存储桶 `mybucket` 的 API 指标：

```shell
mc admin prometheus metrics ALIAS api --bucket mybucket --api-version v3
```

##### `TYPE` {#mc.admin.prometheus.metrics.TYPE}

*mc-cmd*

*Optional*

要输出的指标类型。

> metrics version 3 的有效值为：
>
> - `api`
> - `audit`
> - `cluster`
> - `debug`
> - `ilm`
> - `logger`
> - `notification`
> - `replication`
> - `scanner`
> - `system`
>
> 未指定时，`v3` 命令返回所有指标。
>
> metrics version 2 的有效值为：
>
> - `bucket`
> - `cluster`
> - `node`
> - `resource`
>
> 未指定时，`v2` 命令返回集群指标。 集群指标包含部分节点指标的汇总值。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 输出 v3 指标 {#v3}

使用 [`mc admin prometheus metrics --api-version v3`](#mc.admin.prometheus.metrics.-api-version) 输出某个 MinIO 部署中所有可用的 v3 指标及其当前值：

```shell
mc admin prometheus metrics ALIAS --api-version v3
```

- 将 `ALIAS` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

要输出特定类型的指标，请添加 [`TYPE`](#mc.admin.prometheus.metrics.TYPE)。 以下命令输出某个部署的全部 scanner 指标：

```shell
mc admin prometheus metrics ALIAS scanner --api-version v3
```

### 输出 v3 API 或存储桶复制指标 {#v3-api}

某些 v3 指标类型接受 [`--bucket`](#mc.admin.prometheus.metrics.-bucket) 参数，用于指定要输出指标的存储桶。 以下示例输出存储桶 `mybucket` 的 v3 replication 指标：

```shell
mc admin prometheus metrics ALIAS replication --bucket mybucket --api-version v3
```

- 将 `ALIAS` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

要输出该存储桶的 API 指标，请将 `replication` 替换为 `api`。

### 输出 v2 集群指标 {#v2}

默认情况下，[`mc admin prometheus metrics`](#command-mc.admin.prometheus.metrics) 输出 v2 集群指标：

```shell
mc admin prometheus metrics ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

### 输出其他类型的 v2 指标 {#id6}

要输出另一种 v2 指标类型，请指定所需的 [`TYPE`](#mc.admin.prometheus.metrics.TYPE)。 以下示例输出 v2 bucket 指标：

```shell
mc admin prometheus metrics ALIAS bucket
```

可接受的值为 `bucket`、`cluster`、`node` 和 `resource`。