---
title: "mc admin prometheus"

weight: 120
icon: fa-solid fa-chart-line
---

<a id="mc-admin-prometheus"></a>

<a id="command-mc.admin.prometheus"></a>

## 说明 {#id2}

[`mc admin prometheus`](#command-mc.admin.prometheus) 命令及其子命令用于访问 MinIO Prometheus 指标。

## 子命令 {#id3}

[`mc admin prometheus`](#command-mc.admin.prometheus) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-prometheus-generate/#command-mc.admin.prometheus.generate"><code>generate</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-prometheus-generate/#command-mc.admin.prometheus.generate"><code>mc admin prometheus generate</code></a> 命令会生成一个用于 <a href="https://prometheus.io/">Prometheus</a> 的指标抓取配置文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-prometheus-metrics/#command-mc.admin.prometheus.metrics"><code>metrics</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc-admin/mc-admin-prometheus-metrics/#command-mc.admin.prometheus.metrics"><code>mc admin prometheus metrics</code></a> 命令用于输出集群的 Prometheus 指标。</p></td>
    </tr>
  </tbody>
</table>