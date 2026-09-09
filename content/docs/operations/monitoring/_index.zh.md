---
title: "监控与告警"

weight: 40
icon: fa-solid fa-chart-line
---

<a id="id1"></a>

- [使用 MinIO 和 Prometheus 进行监控：概览](https://youtu.be/A3vCDaFWNNs?ref=docs)
- [使用 MinIO 和 Prometheus 进行监控：实验](https://youtu.be/Oix9iXndSUY?ref=docs)

## 指标与告警 {#id3}

MinIO 使用 [Prometheus 数据模型](https://prometheus.io/docs/concepts/data_model/) 发布时点指标。 你可以使用任何支持该数据模型的抓取工具，将这些指标拉取到数据库中，以生成历史视图、执行指标查询与分析，或基于关注的数据点创建告警。

下表列出了将 MinIO 指标接入部分第三方监控软件的教程。

<table>
  <tbody>
    <tr>
      <td><p><a href="/docs/operations/monitoring/collect-minio-metrics-using-prometheus/#minio-metrics-collect-using-prometheus">使用 Prometheus 进行监控与告警</a></p></td>
      <td><p>配置 Prometheus，对 MinIO 部署进行监控与告警</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/operations/monitoring/monitor-and-alert-using-influxdb/#minio-metrics-influxdb">使用 InfluxDB 进行监控与告警</a></p></td>
      <td><p>配置 InfluxDB，对 MinIO 部署进行监控与告警。</p></td>
    </tr>
  </tbody>
</table>

其他支持 Prometheus 数据模型的指标与分析软件套件，即使未出现在上表中，也可能同样可用。

## 日志 {#id4}

MinIO 会将所有 [`minio server`](/docs/reference/minio-server/#command-minio.server) 操作输出到系统控制台。 MinIO 还支持将服务日志和审计日志发布到 HTTP Webhook。

- [服务日志](/docs/operations/monitoring/minio-logging/#minio-logging-publish-server-logs) 包含与系统控制台中相同的 [`minio server`](/docs/reference/minio-server/#command-minio.server) 操作日志。 服务日志适用于常规监控与运维排障。
- [审计日志](/docs/operations/monitoring/minio-logging/#minio-logging-publish-audit-logs) 会以更细粒度描述 MinIO 部署上的每一次操作。 审计日志适用于需要对操作进行详细追踪的安全标准与合规要求。

MinIO 会将日志作为 JSON 文档，通过 `PUT` 请求发送到每个已配置的端点。 端点服务器负责处理这些 JSON 文档。 MinIO 要求显式配置每个 Webhook 端点，默认情况下 *不会* 向 Webhook 发布日志。

更完整的文档请参见 [将服务日志或审计日志发布到外部服务](/docs/operations/monitoring/minio-logging/#minio-logging)。

## 健康检查 {#id5}

MinIO 提供无需身份验证的端点，用于探测节点在线状态以及集群 [高可用性](/docs/operations/concepts/erasure-coding/#minio-ec-parity)，从而执行简单健康检查。 这些端点只返回 HTTP 状态码。 更多信息请参见 [健康检查 API](/docs/operations/monitoring/healthcheck-probe/#minio-healthcheck-api)。