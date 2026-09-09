---
title: "故障排查"

weight: 100
icon: fa-solid fa-screwdriver-wrench
---

<a id="id1"></a>

## 概述 {#id3}

MinIO 用户有两种支持渠道可选。

1. 通过 [公开 Slack 频道](https://slack.min.io)<a id="slack"></a> 获取社区支持。

   社区支持仅为尽力而为，不提供 <abbr title="Service Level Agreement">SLA</abbr> 或 <abbr title="Service Level Objective">SLO</abbr>。
2. 付费订阅用户可访问 MinIO Subscription Network，即 [SUBNET](https://min.io/pricing?jmp=docs)，可获得健康检查、直接面向工程团队的支持以及许可证管理。

   当前许可级别和定价请参见 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 页面。

## 工具 {#id4}

[MinIO Client](/docs/reference/minio-mc/#minio-client) 提供了多项功能，用于显示 MinIO 部署信息或监控其活动。

- 如需查看 MinIO 部署的基础信息，请使用 [`mc admin info`](/docs/reference/minio-mc-admin/mc-admin-info/#command-mc.admin.info)。
- 如需进一步排查 S3 调用与响应，请使用 [`mc admin trace`](/docs/reference/minio-mc-admin/mc-admin-trace/#command-mc.admin.trace)。
- 使用 [`mc admin logs`](/docs/reference/minio-mc-admin/mc-admin-logs/#command-mc.admin.logs) 从命令行显示日志。 该命令支持类型和数量过滤器，可进一步限制日志输出。

## 升级与版本支持 {#id5}

MinIO 会定期发布更新，以引入新功能、提升性能、解决安全问题或修复缺陷。 这些发布可能非常频繁，并且会因产品不同而有所差异。

在生产部署升级之前，务必先在开发环境中测试软件版本。

### 建议的升级周期 {#id6}

MinIO 建议始终安装最新版本，以获得安全增强和其他改进。 我们理解，如此频繁的发布节奏对某些组织而言可能并不现实。 在这种情况下，我们建议使用发布不超过六个月的 MinIO 及相关产品版本。

### 版本对齐 {#id7}

由于 MinIO 各产品会按照各自的节奏分别发布，我们建议采用以下版本对齐实践：

**MinIO**

> 更新到最新版本，或更新到不超过六个月的版本。

**MinIO 客户端**

> 更新到在 MinIO 发布后紧接着发布的 *mc* 版本，时间间隔控制在一到两周内。

**MinIO Operator**

> 使用不早于 Operator 发布时最新版本的 MinIO 版本。 该发布时间点的最新 MinIO 版本，可在对应 Operator 版本示例租户 kustomization YAML 文件中的 quay.io 链接中找到。
>
> - 4.5.5: MinIO RELEASE.2022-12-07T00-56-37Z or later
> - 4.5.6: MinIO RELEASE.2023-01-02T09-40-09Z or later
> - 4.5.7: MinIO RELEASE.2023-01-12T02-06-16Z or later
> - 4.5.8: MinIO RELEASE.2023-01-12T02-06-16Z or later
>
> 创建新租户时，Operator 会使用最新可用的 MinIO 发布镜像，或使用你在创建租户时指定的镜像。
>
> [Upgrading the Operator](/docs/operations/deployments/k8s-upgrade-minio-operator-kubernetes/#minio-k8s-upgrade-minio-operator) 不会自动升级现有租户。 需要单独执行 [Upgrade existing tenant](/docs/operations/deployments/k8s-upgrade-minio-tenant-on-kubernetes/#minio-k8s-upgrade-minio-tenant) 以升级 MinIO 版本。