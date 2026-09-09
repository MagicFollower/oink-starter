---
title: "mc anonymous set-json"

weight: 60
---

<a id="mc-anonymous-set-json"></a>
<a id="minio-mc-policy-set-json"></a>

<a id="command-mc.anonymous.set-json"></a>

## 语法 {#id2}

[`mc anonymous set-json`](#command-mc.anonymous.set-json) 命令使用 IAM [JSON 策略文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html)，为存储桶设置匿名（即未认证或公开）访问[策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

配置了匿名策略的存储桶允许客户端在无需 [authentication](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 的情况下访问存储桶内容， 并执行与指定策略一致的操作。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将 JSON 格式的匿名策略应用到 `myminio` MinIO 部署上的 `mydata` 存储桶：

```shell
mc anonymous set-json ~/mydata-anonymous.json myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] set-json POLICY ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `POLICY` {#mc.anonymous.set-json.POLICY}

*mc-cmd*

*必需* 要分配给指定 `ALIAS` 的 JSON 格式策略文件路径。

##### `ALIAS` {#mc.anonymous.set-json.ALIAS}

*mc-cmd*

*必需* 存储桶或存储桶前缀的完整路径，命令会将指定的 [`POLICY`](#mc.anonymous.set-json.POLICY) 应用到该路径。

指定 MinIO 或其他 S3 兼容服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，*以及* 存储桶或存储桶前缀的完整路径。例如：

```shell
mc anonymous set-json public play/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 为存储桶设置匿名策略 {#id6}

使用 [`mc anonymous set-json`](#command-mc.anonymous.set-json) 为存储桶设置匿名策略：

```shell
mc anonymous set-json POLICY ALIAS/PATH
```

- 将 [`POLICY`](#mc.anonymous.set-json.POLICY) 替换为受支持的 [`POLICY`](#mc.anonymous.set-json.POLICY)。
- 将 [`ALIAS`](#mc.anonymous.set-json.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.anonymous.set-json.ALIAS) 替换为目标存储桶。

### 移除存储桶的匿名策略 {#id7}

使用 [`mc anonymous set`](/docs/reference/minio-mc/mc-anonymous-set/#command-mc.anonymous.set) 清除存储桶的匿名策略：

```shell
mc anonymous set none ALIAS/PATH
```

- 将 [`ALIAS`](/docs/reference/minio-mc/mc-anonymous-set/#mc.anonymous.set.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](/docs/reference/minio-mc/mc-anonymous-set/#mc.anonymous.set.ALIAS) 替换为目标存储桶。

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。