---
title: "mc admin heal"

weight: 70
---

<a id="mc-admin-heal"></a>

<a id="command-mc.admin.heal"></a>

## 说明 {#id2}

[`mc admin heal`](#command-mc.admin.heal) 命令会扫描受损或损坏的对象，并对这些对象执行自愈。

[`mc admin heal`](#command-mc.admin.heal) 资源开销较大，通常不需要手动执行，即使在驱动器故障或数据损坏事件之后也是如此。

作为正常运行的一部分，MinIO 会：

- 在每次 `POST` 或 `GET` 操作时，自动修复因静默位腐坏、驱动器故障或其他问题而受损的对象。
- 使用 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 周期性执行后台对象自愈。
- 在更换驱动器后积极执行对象自愈。

有关 MinIO 如何执行对象自愈的更多详细信息，请参阅 [对象自愈](/docs/operations/concepts/healing/#minio-concepts-healing)。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

## 语法 {#id3}

[`mc admin heal`](#command-mc.admin.heal) 使用以下语法：

```shell
mc admin heal [FLAGS] TARGET             \
                      [--all-drives, -a] \
                      [--force]          \
                      [--verbose, -v]
```

[`mc admin heal`](#command-mc.admin.heal) 支持以下参数：

#### `TARGET` {#mc.admin.heal.TARGET}

*mc-cmd*

*Required*

执行对象自愈的存储桶或存储桶前缀的完整路径。 指定已配置的 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 作为该路径的前缀。 例如：

```shell
mc admin heal play/mybucket/myprefix
```

如果 `TARGET` 存储桶或存储桶前缀存在活动的自愈扫描，命令将返回该扫描的状态。

#### `--all-drives, -a` {#mc.admin.heal.-all-drives}

*mc-cmd*

*Optional*

选择所有驱动器并显示详细信息。

#### `--force` {#mc.admin.heal.-force}

*mc-cmd*

*Optional*

禁用警告提示。

#### `--verbose, -v` {#mc.admin.heal.-verbose}

*mc-cmd*

*Optional*

显示离线和故障驱动器的自愈信息。

<a id="id4"></a>

## 自愈颜色 {#minio-concepts-healing-colors}

某些版本的 MinIO 使用颜色标识来区分不同自愈状态的对象。

> [!NOTE]
> **变更: mc**
>
> RELEASE.2024-11-17T19-35-25Z

颜色含义已更新。

- 绿色表示存储桶健康。
- 黄色表示存储桶在一个或多个驱动器上需要执行自愈。
- 红色表示一个或多个驱动器处于不健康状态。
- 灰色表示自愈状态不确定。