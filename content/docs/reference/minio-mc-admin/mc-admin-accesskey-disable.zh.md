---
title: "mc admin accesskey disable"

weight: 20
---

<a id="mc-admin-accesskey-disable"></a>
<a id="minio-mc-admin-accesskey-disable"></a>

<a id="command-mc.admin.accesskey.disable"></a>

## 语法 {#id2}

[`mc admin accesskey disable`](#command-mc.admin.accesskey.disable) 命令用于禁用 MinIO IDP 用户的现有访问密钥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会禁用指定的访问密钥：

```shell
mc admin accesskey disable myminio myuserserviceaccount
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin accesskey disable         \
                                 ALIAS           \
                                 SERVICEACCOUNT
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.accesskey.disable.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `SERVICEACCOUNT` {#mc.admin.accesskey.disable.SERVICEACCOUNT}

*mc-cmd*

*Required*

要禁用的访问密钥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。