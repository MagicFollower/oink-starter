---
title: "使用 InfluxDB 进行监控与告警"

weight: 20
---

<a id="influxdb"></a>
<a id="minio-metrics-influxdb"></a>

MinIO 使用 [Prometheus 数据模型](https://prometheus.io/docs/concepts/data_model/) 发布集群和节点指标。 [InfluxDB](https://www.influxdata.com/?ref=minio) 支持抓取 MinIO 指标数据，用于监控和告警。

本页介绍以下内容：

- 配置 InfluxDB 服务，抓取并展示 MinIO 部署的指标
- 基于 MinIO 指标配置告警

> [!NOTE]
> **前提条件**
>
> 此过程要求满足以下条件：
>
> - 已有 InfluxDB 部署，并配置一个或多个[通知端点](https://docs.influxdata.com/influxdb/v2/monitor-alert/notification-endpoints/)
> - 已有可通过网络访问 InfluxDB 部署的 MinIO 部署
> - 本地主机已安装 [`mc`](/docs/reference/minio-mc/#command-mc)，并已配置为可 [访问](/docs/reference/minio-mc/mc-alias-set/#alias) MinIO 部署
>
> 本文说明使用 [version 2 指标](/docs/operations/monitoring/metrics-v2/#minio-metrics-v2)。 关于指标 API 版本的更多信息，请参见 [指标与告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)。

对于 Kubernetes 上的 MinIO 部署，本文默认已具备 Ingress、负载均衡器等必要的网络控制组件，以便 MinIO 租户与 InfluxDB 服务之间能够互相访问。

## 配置 InfluxDB 收集 MinIO 指标并触发告警 {#influxdb-minio}

> [!WARNING]
> **重要**
>
> 本过程专门使用 InfluxDB UI 来创建抓取端点。
>
> InfluxDB UI 提供的配置能力不如 [Telegraf](https://docs.influxdata.com/telegraf/v1.24/) 及其对应的 [Prometheus plugin](https://github.com/influxdata/telegraf/blob/release-1.24/plugins/inputs/prometheus/README.md) 完整。 具体来说：
>
> - 无法通过 InfluxDB UI 为 MinIO 指标端点启用认证访问
> - 无法为已采集指标设置标签（例如 `url_tag`），以唯一标识特定 MinIO 部署的指标
>
> Telegraf Prometheus plugin 还支持 Kubernetes 特有能力，例如抓取特定 MinIO 租户的 `minio` service。
>
> 配置 Telegraf 不在本文范围内。 可将本文作为配置 Telegraf 抓取 MinIO 指标的一般指导。

1. 配置对 MinIO 指标的公开访问

   在 MinIO 部署的所有节点上，将 [`MINIO_PROMETHEUS_AUTH_TYPE`](/docs/reference/minio-server/settings/metrics-and-logging/#envvar.MINIO_PROMETHEUS_AUTH_TYPE) 环境变量设置为 `"public"`。 随后可重启部署，以允许公开访问 MinIO 指标。

   可通过对指标端点执行 `curl` 来验证变更是否生效：

   ```shell
   curl https://HOSTNAME/minio/v2/metrics/cluster
   ```

   将 `HOSTNAME` 替换为访问 MinIO 部署所使用的负载均衡器或反向代理 URL。 也可以将任意单个节点写成 `HOSTNAME:PORT`，即在节点主机名之外再指定 MinIO server API 端口。

   响应正文中应包含已采集的 MinIO 指标列表。
2. 登录 InfluxDB UI 并创建 Bucket

   选择用于存储 MinIO 指标的 [Organization](https://docs.influxdata.com/influxdb/v2.4/organizations/view-orgs/)。

   创建一个 [New Bucket](https://docs.influxdata.com/influxdb/v2.4/organizations/buckets/create-bucket/)，用于存储该 MinIO 部署的指标。
3. 创建新的抓取源

   创建一个 [新的 InfluxDB Scraper](https://docs.influxdata.com/influxdb/v2.4/write-data/no-code/scrape-data/manage-scrapers/create-a-scraper/)。

   指定 MinIO 部署的完整 URL，其中包含指标端点：

   ```shell
   https://HOSTNAME/minio/v2/metrics/cluster
   ```

   将 `HOSTNAME` 替换为访问 MinIO 部署所使用的负载均衡器或反向代理 URL。 也可以将任意单个节点写成 `HOSTNAME:PORT`，即在节点主机名之外再指定 MinIO server API 端口。
4. 验证数据

   使用 [DataExplorer](https://docs.influxdata.com/influxdb/v2.4/query-data/execute-queries/data-explorer/) 可视化已采集的 MinIO 数据。

   例如，可针对 `minio_cluster_capacity_usable_total_bytes` 和 `minio_cluster_capacity_usable_free_bytes` 设置过滤条件，以比较 MinIO 部署中的总可用空间和剩余可用空间。
5. 配置 Check

   基于某个 MinIO 指标创建一个[新的 Check](https://docs.influxdata.com/influxdb/v2/monitor-alert/checks/create/)。

   以下示例 Check 规则为 MinIO 部署提供了一组基础告警。 可按需修改这些示例，或将其作为构建自定义 Check 的参考。

   - 创建一个名为 `MINIO_NODE_DOWN` 的 **Threshold Check**。

     将过滤条件设置为 `minio_cluster_nodes_offline_total` 键。

     在值大于 **1** 时，将 **Thresholds** 设置为 **WARN**。
   - 创建一个名为 `MINIO_QUORUM_WARNING` 的 **Threshold Check**。

     将过滤条件设置为 `minio_cluster_drive_offline_total` 键。

     当该值比已配置的 [纠删码校验值](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 少 1 时，将 **Thresholds** 设置为 **CRITICAL**。

     例如，使用 `EC:4` 的部署应将该值设置为 `3`。

   配置 [Notification endpoints](https://docs.influxdata.com/influxdb/v2.4/monitor-alert/notification-endpoints/) 和 [Notification rules](https://docs.influxdata.com/influxdb/v2.4/monitor-alert/notification-rules/)，使各类 Check 都能触发适当响应。