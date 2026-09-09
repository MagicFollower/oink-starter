---
title: "mc share ls"

weight: 30
---

<a id="mc-share-ls"></a>

<a id="command-mc.share.list"></a>

<a id="command-mc.share.ls"></a>

## 语法 {#id2}

[`mc share ls`](#command-mc.share.ls) 命令会显示由 [`mc share upload`](/docs/reference/minio-mc/mc-share-upload/#command-mc.share.upload) 或 [`mc share download`](/docs/reference/minio-mc/mc-share-download/#command-mc.share.download) 生成的所有未过期预签名 URL。

[`mc share list`](#command-mc.share.list) 命令与 [`mc share ls`](#command-mc.share.ls) 的功能等效。

应用程序可以执行 `PUT` 以从该 URL 获取对象。

有关可共享对象 URL 的更多信息，请参阅 Amazon S3 文档中的 [Pre-Signed URLs](https://docs.aws.amazon.com/AmazonS3/latest/dev/ShareObjectPreSignedURL.html).

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令分别列出 `myminio` MinIO 部署中 `mydata` 存储桶的 所有上传和下载预签名 URL：

```shell
mc share ls upload myminio/mydata
mc share ls download myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] share list           \
                 [download | upload]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `download` {#mc.share.ls.download}

*mc-cmd*

*必需* 列出所有未过期的预签名下载（`GET`）URL。

与 [`mc share ls upload`](#mc.share.ls.upload) 互斥。

##### `upload` {#mc.share.ls.upload}

*mc-cmd*

*必需* 列出所有未过期的预签名上传（`PUT`）URL。

与 [`mc share ls download`](#mc.share.ls.download) 互斥。

##### `ALIAS` {#mc.share.ls.ALIAS}

*mc-cmd*

*必需* MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及对象的完整路径， 用于列出该对象的未过期预签名 URL。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出已生成的下载和上传 URL {#url}

{{< tabs group="url-url-2" >}}
{{< tab label="列出活动下载预签名 URL" value="url" >}}
使用 [`mc share ls download`](#mc.share.ls.download) 生成一个 URL， 该 URL 支持 `POST` 请求，用于将文件上传到 S3 兼容主机上的 特定对象位置：

```shell
mc share ls download ALIAS
```

- 将 [`ALIAS`](#mc.share.ls.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< tab label="列出活动上传预签名 URL" value="url-2" >}}
使用 [`mc share ls upload`](#mc.share.ls.upload) 生成一个 URL， 该 URL 支持 `POST` 请求，用于将文件上传到 S3 兼容主机上的 特定对象位置：

```shell
mc share ls upload ALIAS
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-share-upload/#mc.share.upload.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。