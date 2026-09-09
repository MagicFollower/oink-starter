---
title: "健康检查 API"

weight: 30
---

<a id="api"></a>
<a id="minio-healthcheck-api"></a>

MinIO 提供无需身份验证的端点，用于探测节点在线状态以及集群 [高可用性](/docs/operations/concepts/erasure-coding/#minio-ec-parity)，从而执行简单健康检查。这些 端点返回一个 HTTP 状态码，用于表示底层资源是否健康，或是否满足读写仲裁。 MinIO 不会通过这些端点暴露任何其他数据。

## 节点存活 {#id2}

使用以下端点测试某个 MinIO server 是否在线：

```shell
curl -I https://minio.example.net:9000/minio/health/live
```

将 `https://minio.example.net:9000` 替换为待检查 MinIO server 的 DNS 主机名。

返回 `200 OK` 表示该 MinIO server 在线且工作正常。 任何其他 HTTP 状态码都表示访问该 server 存在问题，例如临时网络故障或潜在停机。

单靠 healthcheck probe 无法判断某个 MinIO server 是否离线。 它只能判断当前主机是否能够访问该 server。 建议配置 Prometheus [告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)，使用 [metrics v3（英文详细表）](/operations/monitoring/metrics-and-alerts/#minio-available-v3-cluster-metrics) 的 `minio_cluster_health_nodes_offline_count` 或 [metrics v2（英文详细表）](/operations/monitoring/metrics-v2/#minio-available-cluster-metrics) 的 `minio_cluster_nodes_offline_total`，以检测一个或多个 MinIO 节点是否离线。

<a id="id3"></a>

## 集群写仲裁 {#minio-cluster-write-quorum}

使用以下端点测试 MinIO 集群是否具备 [写仲裁](/docs/operations/concepts/erasure-coding/#minio-ec-parity)：

```shell
curl -I https://minio.example.net:9000/minio/health/cluster
```

将 `https://minio.example.net:9000` 替换为待检查 MinIO 集群中某个节点的 DNS 主机名。 对于使用负载均衡器管理传入连接的集群，请指定负载均衡器的主机名。

返回 `200 OK` 表示 MinIO 集群当前有足够的 MinIO server 在线，可满足写仲裁。 返回 `503 Service Unavailable` 表示集群当前不具备写仲裁。

单靠 healthcheck probe 无法判断某个 MinIO server 是否离线，也无法判断其是否正在正常处理写操作。 它只能根据配置的 [纠删码校验值](/docs/operations/concepts/erasure-coding/#minio-ec-parity) 判断当前是否有足够的 MinIO server 在线，以满足写仲裁要求。 建议配置 Prometheus [告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)，使用以下指标检测 MinIO 集群中的潜在问题或错误：

- `minio_cluster_nodes_offline_total`：在一个或多个 MinIO 节点离线时触发告警。
- `minio_node_drive_free_bytes`：在集群可用磁盘空间不足时触发告警。

## 集群读仲裁 {#id4}

使用以下端点测试 MinIO 集群是否具备 [读仲裁](/docs/operations/concepts/erasure-coding/#minio-ec-parity)：

```shell
curl -I https://minio.example.net:9000/minio/health/cluster/read
```

将 `https://minio.example.net:9000` 替换为待检查 MinIO 集群中某个节点的 DNS 主机名。 对于使用负载均衡器管理传入连接的集群，请指定负载均衡器的主机名。

返回 `200 OK` 表示 MinIO 集群当前有足够的 MinIO server 在线，可满足读仲裁。 返回 `503 Service Unavailable` 表示集群当前不具备读仲裁。

单靠 healthcheck probe 无法判断某个 MinIO server 是否离线，也无法判断其是否正在正常处理读操作。 它只能根据配置的 [纠删码校验值](/docs/operations/concepts/erasure-coding/#minio-ec-parity) 判断当前是否有足够的 MinIO server 在线，以满足读仲裁要求。 建议配置 Prometheus [告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)，使用 `minio_cluster_nodes_offline_total` 指标检测一个或多个 MinIO 节点是否离线。

## 集群维护检查 {#id5}

使用以下端点测试在将指定 MinIO server 下线维护时， MinIO 集群是否仍能同时维持 [读](/docs/operations/concepts/erasure-coding/#minio-ec-parity) 和 [写](/docs/operations/concepts/erasure-coding/#minio-ec-parity)：

```shell
curl -I https://minio.example.net:9000/minio/health/cluster?maintenance=true
```

将 `https://minio.example.net:9000` 替换为待检查 MinIO 集群中某个节点的 DNS 主机名。 对于使用负载均衡器管理传入连接的集群，请指定负载均衡器的主机名。

返回 `200 OK` 表示 MinIO 集群当前有足够的 MinIO server 在线，可满足写仲裁。 返回 `412 Precondition Failed` 表示如果该 MinIO server 离线，集群将失去仲裁。

单靠 healthcheck probe 无法判断某个 MinIO server 是否离线。 它只能判断在该节点因维护而下线后，是否仍有足够的 MinIO server 在线，以根据配置的 [纠删码校验值](/docs/operations/concepts/erasure-coding/#minio-ec-parity) 满足读写仲裁要求。 建议配置 Prometheus [告警](/docs/operations/monitoring/metrics-and-alerts/#minio-metrics-and-alerts)，使用 `minio_cluster_nodes_offline_total` 指标检测一个或多个 MinIO 节点是否离线。

## 重启后的就绪窗口 {#startup-readiness-window}

上述任何一个端点都不能证明收到请求的节点在重启后已经能够服务数据面。每个节点通过一个监控循环把自己的纠删码磁盘连接到各个对端：启动时没能连上的远端磁盘会在该节点上保持"未安装"状态直到之后的某一轮重连，而监控循环在每轮完成后等待 15 秒，因此这个间隔只是两次尝试之间的下限，不是恢复时间的上限。在磁盘未安装期间，该节点的存活端点返回 `200 OK`，两个集群端点、`mc admin info` 以及 `mcli ready` 也可能报告健康，因为集群端点汇总的是每个对端对自身本地磁盘的报告，而不是本节点实际已安装的磁盘。然而，经由该节点的 PUT 可能因缺少写入仲裁而返回 `503 SlowDownWrite`，经由该节点读取其他节点刚写入的对象可能返回 `404 NoSuchKey`。在确认这一现象的评审运行中，四节点回环集群上，抽样 I/O 大约在管理视图变健康后 13 到 15 秒开始成功，与重连间隔相符；窗口期间由其他节点确认写入的对象事后都能读到。这些都是观察结果而非保证，因为重连可能持续失败。

重启集群后立即写入的自动化流程（例如升级或故障切换的运行手册）应当以一个有界的数据面检查作为门槛，而不是依赖这些端点：经由每个节点各写入一个小对象，再经由每个节点读取每个对象，在一个固定的截止时间内重复，直到每个请求都返回正确的字节和已确认的版本；每个请求的超时按剩余时间预算、并禁用 SDK 重试，之后再重新读取那些已确认写入的对象。把"首次可用 I/O 所需时间"与端点结果分开记录。这样的检查证明的是那一刻、这些对象键所落到的纠删集上的抽样 I/O；它既不证明每个纠删集都已完整，也不证明还有承受再失去一个节点的余量，因为一个纠删集在并非全部磁盘就绪时就可以接受写入。这些端点对于其既定用途（进程存活与仲裁成员资格）仍然是正确的信号。