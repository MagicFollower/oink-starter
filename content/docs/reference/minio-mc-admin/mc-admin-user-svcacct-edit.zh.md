---
title: "mc admin user svcacct edit"

weight: 30
---

<a id="mc-admin-user-svcacct-edit"></a>
<a id="minio-mc-admin-svcacct-edit"></a>

<a id="command-mc.admin.user.svcacct.edit"></a>

> [!WARNING]
> **重要**
>
> 此命令已被替代，并将在未来的 MinIO 客户端 发布版本中弃用。
>
> 从 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，请使用 [`mc admin accesskey edit`](/docs/reference/minio-mc-admin/mc-admin-accesskey-edit/#command-mc.admin.accesskey.edit) 命令修改内置 MinIO IDP 用户的访问密钥。
>
> 如需修改 AD/LDAP 用户的访问密钥，请使用 [`mc idp ldap accesskey edit`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-edit/#command-mc.idp.ldap.accesskey.edit) 命令。

## 语法 {#id2}

[`mc admin user svcacct edit`](#command-mc.admin.user.svcacct.edit) 命令用于修改与指定用户关联的访问密钥配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令为 `myminio` 部署上的 `myuserserviceaccount` 访问密钥应用新的策略和密钥：

```shell
mc admin user svcacct edit                                             \
                      --secret-key "myuserserviceaccountnewsecretkey"  \
                      --policy "/path/to/new/policy.json"              \
                      myminio myuserserviceaccount
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin user svcacct edit            \
                                    [--secret-key]  \
                                    [--policy]      \
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

##### `ALIAS` {#mc.admin.user.svcacct.edit.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `SERVICEACCOUNT` {#mc.admin.user.svcacct.edit.SERVICEACCOUNT}

*mc-cmd*

*Required*

要修改的服务账户。

##### `--description` {#mc.admin.user.svcacct.edit.-description}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-18T16-59-00Z**

为服务账户添加描述。 例如，可以说明该服务账户存在的原因。

##### `--expiry` {#mc.admin.user.svcacct.edit.-expiry}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-30T22-41-38Z**

为服务账户设置过期日期。 日期必须在未来，不能设置已经过去的过期日期。

允许的日期和时间格式：

- `2023-06-24`
- `2023-06-24T10:00`
- `2023-06-24T10:00:00`
- `2023-06-24T10:00:00Z`
- `2023-06-24T10:00:00-07:00`

##### `--name` {#mc.admin.user.svcacct.edit.-name}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-18T16-59-00Z**

为服务账户添加一个便于识别的名称。

##### `--policy` {#mc.admin.user.svcacct.edit.-policy}

*mc-cmd*

*Optional*

要附加到新访问密钥的 [policy document](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 路径，最大长度为 2048 个字符。 附加的策略不能授予父用户策略未明确允许的任何操作或资源访问权限。

新策略会覆盖此前已附加的任何策略。

##### `--secret-key` {#mc.admin.user.svcacct.edit.-secret-key}

*mc-cmd*

*Optional*

与新访问密钥关联的密钥。 会覆盖此前的密钥。 使用这些访问密钥的应用程序 *必须* 更新为新凭证，才能继续执行操作。

### 全局参数 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。