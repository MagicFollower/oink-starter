---
title: "mc anonymous set"

weight: 10
---

<a id="mc-anonymous-set"></a>
<a id="minio-mc-anonymous-set"></a>
<a id="minio-mc-policy-set"></a>

<a id="command-mc.anonymous.set"></a>

## 语法 {#id2}

[`mc anonymous set`](#command-mc.anonymous.set) 命令为存储桶设置匿名（即未认证或公开）访问 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

配置了匿名策略的存储桶允许客户端在无需 [身份验证](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 的情况下， 访问存储桶内容并执行与指定策略一致的操作。

要使用 IAM [JSON 策略](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html)设置存储桶匿名策略，请使用 [`mc anonymous set-json`](/docs/reference/minio-mc/mc-anonymous-set-json/#command-mc.anonymous.set-json) 命令。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` MinIO 部署上的多个存储桶设置匿名访问策略：

```shell
mc anonymous set upload myminio/uploads
mc anonymous set download myminio/downloads
mc anonymous set public myminio/public
```

应用程序可在无需认证的情况下执行以下操作：

- 向 `myminio/uploads` 和 `myminio/public` 执行 `PUT` 对象操作。
- 从 `myminio/downloads` 和 `myminio/public` 执行 `GET` 对象操作。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] policy set PERMISSION ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `PERMISSION` {#mc.anonymous.set.PERMISSION}

*mc-cmd*

*必需* 要分配给指定 `ALIAS` 的策略名称。 指定以下值之一：

- `none` - 禁用对 `ALIAS` 的匿名访问。
- `download` - 启用对 `ALIAS` 的仅下载访问。
- `upload` - 启用对 `ALIAS` 的仅上传访问。
- `public` - 启用对 `ALIAS` 的下载和上传访问。

##### `ALIAS` {#mc.anonymous.set.ALIAS}

*mc-cmd*

*必需* 要应用指定 [`PERMISSION`](#mc.anonymous.set.PERMISSION) 的存储桶或存储桶前缀的完整路径。

指定 MinIO 或其他 S3 兼容服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，*以及* 存储桶或存储桶前缀的完整路径。例如：

```shell
mc anonymous set public play/mybucket
```

指定存储桶前缀可仅对该前缀设置策略。例如，以下命令分别为 `mybucket/downloads` 和 `mybucket/uploads` 前缀设置不同的匿名存储桶策略：

```shell
mc anonymous set download play/mybucket/downloads
mc anonymous set upload play/mybucket/uploads
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 为存储桶设置匿名策略 {#id6}

使用 [`mc anonymous set`](#command-mc.anonymous.set) 为存储桶设置匿名策略：

```shell
mc anonymous set POLICY ALIAS/PATH
```

- 将 [`POLICY`](#mc.anonymous.set.PERMISSION) 替换为受支持的 [`permission`](#mc.anonymous.set.PERMISSION)。
- 将 [`ALIAS`](#mc.anonymous.set.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.anonymous.set.ALIAS) 替换为目标存储桶。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。