---
title: "mc support"

weight: 380
icon: fa-solid fa-life-ring
---

<a id="mc-support"></a>

<a id="command-mc.support"></a>

## 描述 {#id2}

MinIO Client [`mc support`](#command-mc.support) 命令提供用于分析部署健康状况或性能、并运行诊断的工具。 你还可以上传生成的健康报告，供 MinIO 工程团队进一步分析。

> [!WARNING]
> **重要**
>
> `mc support` 命令需要有效的 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册。
>
> [`mc support proxy set`](/docs/reference/minio-mc/mc-support-proxy/#mc.support.proxy.set) 和 [`mc support proxy remove`](/docs/reference/minio-mc/mc-support-proxy/#mc.support.proxy.remove) 是例外，因为你可能需要先配置代理才能完成部署注册。

## 子命令 {#id3}

[`mc support`](#command-mc.support) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-callhome/#command-mc.support.callhome"><code>callhome</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-support-callhome/#command-mc.support.callhome"><code>mc support callhome</code></a> 命令用于启用或禁用将部署诊断信息发送到 <a href="https://min.io/pricing?jmp=docs">MinIO SUBNET</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-diag/#command-mc.support.diag"><code>diag</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-support-diag/#command-mc.support.diag"><code>mc support diag</code></a> 命令用于为 MinIO 部署生成健康报告。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-inspect/#command-mc.support.inspect"><code>inspect</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-support-inspect/#command-mc.support.inspect"><code>mc support inspect</code></a> 命令会收集指定路径下与对象相关的数据和元数据。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-perf/#command-mc.support.perf"><code>perf</code></a></p></td>
      <td><p>使用 <a href="/docs/reference/minio-mc/mc-support-perf/#command-mc.support.perf"><code>mc support perf</code></a> 命令可检查 S3 API（读/写）、网络 IO 和存储（磁盘读/写）的性能。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-profile/#command-mc.support.profile"><code>profile</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-support-profile/#command-mc.support.profile"><code>mc support profile</code></a> 为你的部署运行系统性能剖析。
剖析结果可帮助了解给定节点上运行的 MinIO 服务端进程状态。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-proxy/#command-mc.support.proxy"><code>proxy</code></a></p></td>
      <td><p>使用 <a href="/docs/reference/minio-mc/mc-support-proxy/#command-mc.support.proxy"><code>mc support proxy</code></a> 命令配置与 <a href="https://min.io/pricing?jmp=docs">MinIO SUBNET</a> 通信时使用的代理。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-support-top/#command-mc.support.top"><code>top</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-support-top/#command-mc.support.top"><code>mc support top</code></a> 命令返回分布式 MinIO 部署的统计信息，
类似于 shell 中 <code>top</code> 命令的输出。</p></td>
    </tr>
  </tbody>
</table>