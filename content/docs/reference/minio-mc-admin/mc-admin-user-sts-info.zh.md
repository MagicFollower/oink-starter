---
title: "mc admin user sts info"

weight: 70
---

<a id="mc-admin-user-sts-info"></a>
<a id="minio-mc-admin-sts-info"></a>

<a id="command-mc.admin.user.sts.info"></a>

## 语法 {#id2}

[`mc admin user sts info`](#command-mc.admin.user.sts.info) 命令用于检索指定 STS 凭证的信息，例如生成该凭证的父 [MinIO user](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp)、关联策略和过期时间。

<abbr title="Security Token Service">STS</abbr> 凭证为 MinIO 部署提供临时访问权限。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令检索具有指定访问密钥的 STS 凭证信息：

```shell
mc admin user sts info myminio/ "J123C4ZXEQN8RK6ND35I"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin user sts info          \
                                [--policy]    \
                                ALIAS         \
                                STSACCESSKEY
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.user.sts.info.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `STSACCESSKEY` {#mc.admin.user.sts.info.STSACCESSKEY}

*mc-cmd*

*Required*

STS 凭证的访问密钥。

##### `--policy` {#mc.admin.user.sts.info.-policy}

*mc-cmd*

*Optional*

以 JSON 格式打印附加到指定 STS 凭证的策略。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。