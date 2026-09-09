---
title: "mc admin policy create"

weight: 20
---

<a id="mc-admin-policy-create"></a>

<a id="command-mc.admin.policy.create"></a>

## Syntax {#syntax}

在目标 MinIO 部署上创建一个新策略。

MinIO 部署默认包含以下 [内置策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-built-in)：

- [`readonly`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readonly)
- [`readwrite`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readwrite)
- [`diagnostics`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.diagnostics)
- [`writeonly`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.writeonly)

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
假设以下 JSON 策略文档保存在名为 `/tmp/listmybuckets.json` 的文件中：

```javascript
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
            "s3:ListAllMyBuckets"
         ],
         "Resource": [
            "arn:aws:s3:::*"
         ]
      }
   ]
}
```

以下命令使用文件 `/tmp/listmybuckets.json` 中的策略，在 [alias](/zh/glossary/#term-alias) `myminio` 上创建一个名为 `listmybuckets` 的新策略。

```shell
mc admin policy create myminio listmybuckets /tmp/listmybuckets.json
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc admin policy create     \
                TARGET     \
                POLICYNAME \
                POLICYPATH
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### Parameters {#parameters}

[`mc admin policy create`](#command-mc.admin.policy.create) 命令接受以下参数：

##### `TARGET` {#mc.admin.policy.create.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于向该部署添加新策略。

##### `POLICYNAME` {#mc.admin.policy.create.POLICYNAME}

*mc-cmd*

要添加的策略名称。

指定已有策略的名称会覆盖 [`TARGET`](#mc.admin.policy.create.TARGET) MinIO 部署上的该策略。

##### `POLICYPATH` {#mc.admin.policy.create.POLICYPATH}

*mc-cmd*

要添加的策略文件路径。 该文件 *必须* 为 JSON 格式，使用 [IAM 兼容语法](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)，且长度不超过 2048 个字符。

### Global Flags {#global-flags}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## Examples {#examples}

在别名为 `myminio` 的部署上，使用 `/tmp/writeonly.json` 的 JSON 文件创建一个名为 `writeonly` 的新策略。

```shell
mc admin policy create myminio writeonly /tmp/writeonly.json
```