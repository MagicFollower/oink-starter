---
title: "mc admin cluster bucket export"

weight: 20
---

<a id="command-mc.admin.cluster.bucket.export"></a>
<a id="mc-admin-cluster-bucket-export"></a>
<a id="minio-mc-admin-cluster-bucket-export"></a>

## 描述 {#id1}

> [!NOTE]
> **新增: RELEASE.2022-06-17T02-52-50Z**

[`mc admin cluster bucket export`](#command-mc.admin.cluster.bucket.export) 命令会导出存储桶元数据，以供 [`mc admin cluster bucket import`](/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-import/#command-mc.admin.cluster.bucket.import) 命令使用。

你可以使用此命令手动备份指定 MinIO 存储桶的元数据。 该命令始终将输出保存为 `cluster-metadata.zip`。

如果你仅将部署指定为目标，此命令会备份目标部署上所有存储桶的元数据。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会导出 `myminio` 部署的所有存储桶元数据。

```shell
mc admin cluster bucket export myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] admin cluster bucket export  \
                                      ALIAS[/BUCKET]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.admin.cluster.bucket.export.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `BUCKET` {#mc.admin.cluster.bucket.export.BUCKET}

*mc-cmd*

*Optional*

要导出元数据的存储桶。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。