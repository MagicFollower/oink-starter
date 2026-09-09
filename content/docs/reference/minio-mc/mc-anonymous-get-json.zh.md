---
title: "mc anonymous get-json"

weight: 50
---

<a id="mc-anonymous-get-json"></a>
<a id="minio-mc-policy-get-json"></a>

<a id="command-mc.anonymous.get-json"></a>

## 语法 {#id2}

[`mc anonymous get-json`](#command-mc.anonymous.get-json) 命令用于获取存储桶的匿名（即未经身份验证或公开）访问 [policies](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

配置了匿名策略的存储桶允许客户端在无需 [authentication](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 的情况下访问存储桶内容，并执行与指定策略一致的操作。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令检索 `myminio` MinIO 部署上 `mydata` 存储桶的 JSON 格式匿名策略：

```shell
mc anonymous get-json myminio/mydata
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] get-json ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.anonymous.get-json.ALIAS}

*mc-cmd*

*必需* 要获取匿名存储桶策略的存储桶或存储桶前缀的完整路径。

指定 MinIO 或其他 S3 兼容服务的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，*以及* 存储桶或存储桶前缀的完整路径。例如：

```shell
mc anonymous get-json public play/mybucket
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 获取存储桶的匿名策略 {#id6}

使用 [`mc anonymous get-json`](#command-mc.anonymous.get-json) 获取存储桶的匿名策略：

```shell
mc anonymous get-json ALIAS/PATH
```

- 将 [`ALIAS`](#mc.anonymous.get-json.ALIAS) 替换为已配置 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.anonymous.get-json.ALIAS) 替换为目标存储桶。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。