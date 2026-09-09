---
title: "Metrics version 2"

weight: 30
---

<a id="metrics-version-2"></a>
<a id="minio-metrics-v2"></a>

MinIO 使用 [Prometheus 数据模型](https://prometheus.io/docs/concepts/data_model/) 发布集群和节点指标。 你可以使用任意抓取工具从 MinIO 拉取指标数据，以执行进一步分析和配置告警。

## Version 2 端点 {#version-2}

Metrics version 2 将指标划分为以下三个类别：

- [集群指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-cluster-metrics)
- [存储桶指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-bucket-metrics)
- [资源指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-resource-metrics)

每个 v2 端点都会返回其所属类别的全部指标。 例如，抓取以下端点会返回所有集群指标：

```shell
http://HOSTNAME:PORT/minio/v2/metrics/cluster
```

仅访问基础端点 `/minio/v2/metrics/` 也会返回集群指标。

如需更灵活的抓取方式和更广泛的指标集合，请使用 [metrics version 3](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)。 现有部署仍可继续使用 version 2 [指标](#minio-metrics-v2) 和 [Grafana 仪表板](/docs/operations/monitoring/grafana/#minio-grafana)。

## MinIO Grafana 仪表板 {#minio-grafana}

MinIO 提供两个 [Grafana 仪表板](/docs/operations/monitoring/grafana/#minio-grafana)，用于可视化 v2 指标。 有关为 Grafana 配置兼容 Prometheus 数据源的完整说明，请参见 [Prometheus 关于 Grafana 支持的文档](https://prometheus.io/docs/visualization/grafana/)。

## 可用的 version 2 指标 {#id2}

以下各节描述 version 2 的端点与指标。

{{< tabs group="tab1-tab2-tab3" >}}
{{< tab label="集群指标" value="tab1" >}}
你可以使用以下 URL 端点抓取[集群级指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-cluster-metrics)：

```shell
http://HOSTNAME:PORT/minio/v2/metrics/cluster
```

将 `HOSTNAME:PORT` 替换为 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr> 与端口。 对于使用负载均衡器管理 MinIO 节点间连接的部署，请指定负载均衡器地址。
{{< /tab >}}
{{< tab label="存储桶指标" value="tab2" >}}
> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2023-07-21T21-12-44Z
>
> 存储桶指标已迁移到独立端点。

> [!NOTE]
> **变更: RELEASE.2023-08-31T15-31-16Z**
>
> 你可以使用以下 URL 端点抓取[存储桶级指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-bucket-metrics)：

> [!NOTE]
> **变更: RELEASE.2025-03-12T17-29-24Z**
>
> 出于性能原因，v2 指标最多支持 100 个存储桶。 如果需要覆盖更多存储桶的指标，请改用 [v3 指标](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts-available-metrics)。

```shell
http://HOSTNAME:PORT/minio/v2/metrics/bucket
```

将 `HOSTNAME:PORT` 替换为 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr> 与端口。 对于使用负载均衡器管理 MinIO 节点间连接的部署，请指定负载均衡器地址。
{{< /tab >}}
{{< tab label="资源指标" value="tab3" >}}
> [!NOTE]
> **新增: RELEASE.2023-10-07T15-07-38Z**

你可以使用以下 URL 端点抓取[资源指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-resource-metrics)：

```shell
http://HOSTNAME:PORT/minio/v2/metrics/resource
```

将 `HOSTNAME:PORT` 替换为 MinIO 部署的 <abbr title="Fully Qualified Domain Name">FQDN</abbr> 与端口。 对于使用负载均衡器管理 MinIO 节点间连接的部署，请指定负载均衡器地址。
{{< /tab >}}
{{< /tabs >}}

- [集群指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-cluster-metrics)
- [存储桶指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-bucket-metrics)
- [资源指标（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-resource-metrics)

> > [!NOTE]
> > **变更: RELEASE.2025-03-12T17-29-24Z**
> >
> > 出于性能原因，v2 指标最多支持 100 个存储桶。 如果需要覆盖更多存储桶的指标，请改用 [v3 指标](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts-available-metrics)。

<a id="minio-available-resource-metrics"></a>