---
title: "mc admin cluster iam export"

weight: 20
---

<a id="command-mc.admin.cluster.iam.export"></a>
<a id="mc-admin-cluster-iam-export"></a>
<a id="minio-mc-admin-cluster-iam-export"></a>

## 描述 {#id1}

> [!NOTE]
> **新增: RELEASE.2022-06-26T18-51-48Z**

[`mc admin cluster iam export`](#command-mc.admin.cluster.iam.export) 命令导出 [IAM](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 元数据，以供 [`mc admin cluster iam import`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-import/#command-mc.admin.cluster.iam.import) 命令使用。

该命令将输出保存为 `ALIAS-iam-metadata.zip`，其中 `ALIAS` 是 MinIO 部署的 [`alias`](#mc.admin.cluster.iam.export.ALIAS)。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令导出 `myminio` 部署的全部 IAM 元数据。

```shell
mc admin cluster iam export myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin cluster iam export ALIAS  \
                 [--output, -o <string>]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

从 [RELEASE.2023-05-04T18-10-16Z](https://github.com/minio/mc/releases/tag/RELEASE.2023-05-04T18-10-16Z) 开始，[`mc admin cluster iam export`](#command-mc.admin.cluster.iam.export) 支持以尾随正斜杠结尾的别名 `ALIAS/`。 在此版本之前，提供尾随正斜杠会导致命令执行失败。

### 参数 {#id2}

##### `ALIAS` {#mc.admin.cluster.iam.export.ALIAS}

*mc-cmd*

*Required*

要导出 IAM 元数据的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--output, --o` {#mc.admin.cluster.iam.export.-output}

*mc-cmd*

*Optional*

指定导出 IAM 数据时使用的自定义文件名和路径。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 将集群的全部 IAM 元数据下载到 ZIP 文件 {#iam-zip}

以下命令下载别名为 `myminio` 的集群全部 IAM 元数据，并将其保存到 ZIP 文件中。

```shell
mc admin cluster iam export myminio
```

ZIP 文件命名为 `<alias>-iam-info.zip`，其中 `<alias>` 是集群别名。 在上述示例中，文件名为 `myminio-iam-info.zip`。

该文件位于当前活动目录中。

### 下载集群的全部 IAM 元数据并指定 ZIP 文件名称和路径 {#id5}

以下命令下载别名为 `myminio` 的集群全部 IAM 元数据，并将其保存为 `/tmp/myminio-iam.zip` ZIP 文件。

```shell
mc admin cluster iam export myminio --output /tmp/myminio-iam.zip
```