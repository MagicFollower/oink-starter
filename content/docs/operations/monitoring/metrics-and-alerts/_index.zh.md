---
title: "指标与告警"

weight: 10
icon: fa-solid fa-gauge-high
---

<a id="minio-metrics-and-alerts"></a>
<a id="minio-metrics-and-alerts-alerting"></a>
<a id="minio-metrics-and-alerts-endpoints"></a>
<a id="id1"></a>

MinIO 使用 [Prometheus 数据模型](https://prometheus.io/docs/concepts/data_model/) 发布指标。 你可以使用任意抓取工具从 MinIO 拉取指标数据，以执行进一步分析和配置告警。

从 MinIO 服务端 [RELEASE.2024-07-15T19-02-30Z](https://github.com/minio/minio/releases/tag/RELEASE.2024-07-15T19-02-30Z) 与 MinIO 客户端 [RELEASE.2024-07-11T18-01-28Z](https://github.com/minio/mc/releases/tag/RELEASE.2024-07-11T18-01-28Z) 开始，metrics version 3 提供了更多端点。 对于新部署，MinIO 建议使用 version 3。

> [!NOTE]
> **Metrics version 2**
>
> 现有部署可以继续使用 version 2 [指标](/docs/operations/monitoring/metrics-v2/#minio-metrics-v2) 和 [Grafana 仪表板](/docs/operations/monitoring/grafana/#minio-grafana)。

## Version 3 端点 {#version-3}

对于 metrics version 3，所有指标都位于基础端点 `/minio/metrics/v3` 之下。 你可以抓取该基础端点以一次性收集全部指标，也可以追加可选路径，仅返回特定类别的指标。

> [!WARNING]
> **重要**
>
> 本页中的 V3 指标说明可能存在缺漏、不准确或错误信息。 如需最准确的指标定义，请参考 [minio/minio](https://github.com/minio/minio)<a id="minio-minio"></a> 仓库并审阅源代码。

例如，以下端点会返回 audit 指标：

```shell
http://HOSTNAME:PORT/minio/metrics/v3/audit
```

将 `HOSTNAME:PORT` 替换为 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr> 与端口。 对于使用负载均衡器管理 MinIO 节点间连接的部署，请指定负载均衡器地址。

默认情况下，MinIO 要求在抓取指标端点时进行身份验证。 如需生成所需的 bearer token，请使用 [`mc admin prometheus generate`](/docs/reference/minio-mc-admin/mc-admin-prometheus-generate/#command-mc.admin.prometheus.generate)。 你也可以将 [`MINIO_PROMETHEUS_AUTH_TYPE`](/docs/reference/minio-server/settings/metrics-and-logging/#envvar.MINIO_PROMETHEUS_AUTH_TYPE) 设置为 `public`，以禁用指标端点认证。

相对于基础 URL，MinIO 提供以下抓取端点：

<table>
  <thead>
    <tr>
      <th><p>类别</p></th>
      <th><p>路径</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>API</p></td>
      <td><p><code>/api/requests</code></p><p><code>/bucket/api</code></p></td>
    </tr>
    <tr>
      <td><p>审计</p></td>
      <td><p><code>/audit</code></p></td>
    </tr>
    <tr>
      <td><p>集群</p></td>
      <td><p><code>/cluster/config</code></p><p><code>/cluster/erasure-set</code></p><p><code>/cluster/health</code></p><p><code>/cluster/iam</code></p><p><code>/cluster/usage/buckets</code></p><p><code>/cluster/usage/objects</code></p></td>
    </tr>
    <tr>
      <td><p>调试</p></td>
      <td><p><code>/debug/go</code></p></td>
    </tr>
    <tr>
      <td><p>ILM</p></td>
      <td><p><code>/ilm</code></p></td>
    </tr>
    <tr>
      <td><p>日志 Webhook</p></td>
      <td><p><code>/logger/webhook</code></p></td>
    </tr>
    <tr>
      <td><p>通知</p></td>
      <td><p><code>/notification</code></p></td>
    </tr>
    <tr>
      <td><p>复制</p></td>
      <td><p><code>/replication</code></p><p><code>/bucket/replication</code></p></td>
    </tr>
    <tr>
      <td><p>扫描器</p></td>
      <td><p><code>/scanner</code></p></td>
    </tr>
    <tr>
      <td><p>系统</p></td>
      <td><p><code>/system/drive</code></p><p><code>/system/memory</code></p><p><code>/system/cpu</code></p><p><code>/system/network/internode</code></p><p><code>/system/process</code></p></td>
    </tr>
  </tbody>
</table>

各端点对应的完整指标列表，请参见 [Available version 3 metrics](#minio-metrics-and-alerts-available-metrics)。

如需在 MinIO Console 中启用历史数据可视化，请在 MinIO 部署的每个节点上设置以下环境变量：

- 将 [`MINIO_PROMETHEUS_URL`](/docs/reference/minio-server/settings/console/#envvar.MINIO_PROMETHEUS_URL) 设置为 Prometheus 服务的 URL
- 将 [`MINIO_PROMETHEUS_JOB_ID`](/docs/reference/minio-server/settings/console/#envvar.MINIO_PROMETHEUS_JOB_ID) 设置为分配给已采集指标的唯一 job ID

<a id="id3"></a>

## 可用的 version 3 指标 {#minio-metrics-and-alerts-available-metrics}

MinIO 为集群、API 请求、存储桶以及 MinIO 服务的其他方面发布多类指标：

- [API 指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-api-metrics)
- [审计指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-audit-metrics)
- [集群指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-cluster-metrics)
- [调试指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-debug-metrics)
- [ILM 指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-ilm-metrics)
- [日志 Webhook 指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-logger-webhook-metrics)
- [通知指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-notification-metrics)
- [复制指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-replication-metrics)
- [扫描器指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-scanner-metrics)
- [系统指标（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-system-metrics)

许多指标都包含标签，用于标识生成该指标的资源及其他相关信息。