---
title: "ILM 设置"

weight: 90
---

<a id="ilm"></a>
<a id="minio-server-envvar-ilm"></a>

本页面介绍用于控制 MinIO 进程 ILM（信息生命周期管理）的设置。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 过期 Worker {#worker}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_ILM_EXPIRATION_WORKERS` {#envvar.MINIO_ILM_EXPIRATION_WORKERS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `ilm expiration_workers` {#mc-conf.ilm.expiration_workers}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **新增: MinIO**
>
> Server RELEASE.2024-03-03T17-50-39Z

设置用于 [对象过期](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 的 worker 数量。 有效值范围为 `1` 到 `500`。

默认值为 `100`。