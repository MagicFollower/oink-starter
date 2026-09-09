---
title: "mc admin cluster iam import"

weight: 10
---

<a id="command-mc.admin.cluster.iam.import"></a>
<a id="mc-admin-cluster-iam-import"></a>
<a id="minio-mc-admin-cluster-iam-import"></a>

## 描述 {#id1}

> [!NOTE]
> **新增: RELEASE.2022-06-17T02-52-50Z**

[`mc admin cluster iam import`](#command-mc.admin.cluster.iam.import) 命令导入由 [`mc admin cluster iam export`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export) 命令创建的 [IAM](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 元数据。

您可以使用此命令手动恢复 MinIO 部署的 IAM 元数据设置。

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-09-09T07-53-10Z
>
> 该命令会输出导入结果，包括以下内容：
>
> - 按实体类型统计已导入的单个实体数量
> - 按策略导入目标的实体类型列出已导入策略
> - 导入失败的实体列表

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将指定文件中的 IAM 元数据导入到 `myminio` 部署。

```shell
mc admin cluster iam import myminio ~/minio-metadata-backup/myminio-cluster.zip
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin cluster iam import  \
                                   ALIAS \
                                   IAM-METADATA.ZIP
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

从 [RELEASE.2023-05-04T18-10-16Z](https://github.com/minio/mc/releases/tag/RELEASE.2023-05-04T18-10-16Z) 开始，[`mc admin cluster iam import`](#command-mc.admin.cluster.iam.import) 新增了对以尾随正斜杠结尾的别名 `ALIAS/` 的支持。 在此版本之前，如果提供尾随正斜杠，命令会执行失败。

### 参数 {#id2}

##### `ALIAS` {#mc.admin.cluster.iam.import.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `IAM-METADATA.ZIP` {#mc.admin.cluster.iam.import.IAM-METADATA.ZIP}

*mc-cmd*

*Required*

要导入的 IAM 元数据文件路径。

使用 [`mc admin cluster iam export`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export) 导出 IAM 元数据，以供此命令使用。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。