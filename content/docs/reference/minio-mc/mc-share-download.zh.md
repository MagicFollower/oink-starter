---
title: "mc share download"

weight: 10
---

<a id="mc-share-download"></a>

<a id="command-mc.share.download"></a>

## 语法 {#id2}

[`mc share download`](#command-mc.share.download) 命令会生成一个临时的预签名 URL，并集成访问凭证， 用于从 MinIO 存储桶下载对象。该临时 URL 会在可配置的时间限制后过期。

- 应用程序可以通过执行 `GET` 从该 URL 获取对象。
- 用户可以在浏览器中打开该 URL 下载对象。

有关可共享对象 URL 的更多信息，请参阅 Amazon S3 关于 [Pre-Signed URLs](https://docs.aws.amazon.com/AmazonS3/latest/dev/ShareObjectPreSignedURL.html).

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会为 `myminio` MinIO 部署中的 `mydata` 存储桶生成一个新的预签名下载 URL：

```shell
mc share download --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] share download           \
                 [--expire "string"]      \
                 [--recursive]            \
                 [--version-id "string"]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.share.download.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要为其生成下载 URL 的对象完整路径。例如：

```shell
mc share download play/mybucket/object.txt
```

你可以在同一个或不同的 MinIO 部署上指定多个对象。例如：

```shell
mc share download play/mybucket/object.txt play/mybucket/otherobject.txt
```

如果指定的是存储桶路径或存储桶前缀路径，则 **必须** 同时指定 [`--recursive`](#mc.share.download.-recursive) 参数。例如：

```shell
mc share download --recursive play/mybucket/

mc share download --recursive play/mybucket/myprefix/
```

##### `--expire, E` {#mc.share.download.-expire}

*mc-cmd*

*Optional*

为所有生成的 URL 设置过期时间限制。

指定一个格式为 `##h##m##s` 的字符串。例如：`12h34m56s` 表示 URL 生成后 12 小时 34 分 56 秒过期。

默认为 `168h`，即 168 小时（7 天）。

##### `--recursive, r` {#mc.share.download.-recursive}

*mc-cmd*

*Optional*

递归地为 [`mc share download ALIAS`](#mc.share.download.ALIAS) 存储桶或存储桶前缀中的所有对象生成 URL。

如果任一 `ALIAS` 指向存储桶路径或存储桶前缀路径，则此参数为必需。

##### `--version-id, vid` {#mc.share.download.-version-id}

*mc-cmd*

*Optional*

指示 [`mc share download`](#command-mc.share.download) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.share.download.-version-id) 要求指定的 [`ALIAS`](#mc.share.download.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 生成用于下载对象的 URL {#url}

{{< tabs group="tab1-tab2" >}}
{{< tab label="获取特定对象" value="tab1" >}}
使用 [`mc share download`](#command-mc.share.download) 为对象生成支持 `GET` 请求的 URL：

```shell
mc share download --expire DURATION ALIAS/PATH
```

- 将 [`ALIAS`](#mc.share.download.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.share.download.ALIAS) 替换为 MinIO 部署上对象的路径。
- 将 [`DURATION`](#mc.share.download.-expire) 替换为 URL 的过期时长。 例如，要设置为 30 天过期，请指定 `30d`。
{{< /tab >}}
{{< tab label="获取存储桶中的对象" value="tab2" >}}
使用 [`mc share download`](#command-mc.share.download) 并结合 [`--recursive`](#mc.share.download.-recursive) 选项，可为存储桶中的每个对象生成一个 URL。 每个 URL 都支持对其关联对象执行 `GET` 请求：

```shell
mc share download --recursive --expire DURATION ALIAS/PATH
```

- 将 [`ALIAS`](#mc.share.download.ALIAS) 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 [`PATH`](#mc.share.download.ALIAS) 替换为 MinIO 部署上的存储桶路径或存储桶前缀路径。
- 将 [`DURATION`](#mc.share.download.-expire) 替换为 URL 的过期时长。 例如，要设置为 30 天过期，请指定 `30d`。
{{< /tab >}}
{{< /tabs >}}

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。