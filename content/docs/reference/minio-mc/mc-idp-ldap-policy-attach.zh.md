---
title: "mc idp ldap policy attach"

weight: 10
---

<a id="mc-idp-ldap-policy-attach"></a>
<a id="minio-mc-idp-ldap-policy-attach"></a>

<a id="command-mc.idp.ldap.policy.attach"></a>

## 描述 {#id2}

[`mc idp ldap policy attach`](#command-mc.idp.ldap.policy.attach) 命令将一个或多个策略附加到实体。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
> 以下示例将策略 `userpolicy` 附加到 `myminio` 部署中的用户 `bobfisher`：

```shell
mc idp ldap policy attach myminio                                                  \
                          userpolicy                                               \
                          --user='uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] idp ldap policy attach             \
                                 POLICYNAME         \
                                 [POLICY2] ...      \
                                 ALIAS              \
                                 [--user=`USER`]    \
                                 [--group=`GROUP`]
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于配置 AD/LDAP 集成。
- 将 `POLICYNAME` 替换为要附加到实体的策略。 你可以列出多个要附加到实体的策略。
- 必须使用 `--user` 或 `--group` 标志之一。 在命令中每个标志只能使用一次。 不能在同一命令中同时使用这两个标志。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.policy.attach.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，其中包含要附加策略的实体。

例如：

```text
mc idp ldap policy attach myminio                                                  \
                          userpolicy                                               \
                          --user='uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'
```

### 示例 {#id4}

以下示例将两个策略 `policy1` 和 `policy2` 附加到 `myminio` 部署中的 `projectb` 组：

```shell
mc idp ldap policy attach myminio                                                 \
                          policy1                                                 \
                          policy2                                                 \
                          --group='cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```

### 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。