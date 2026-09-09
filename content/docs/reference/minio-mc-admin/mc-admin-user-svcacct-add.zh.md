---
title: "mc admin user svcacct add"

weight: 10
---

<a id="mc-admin-user-svcacct-add"></a>
<a id="minio-mc-admin-svcacct-add"></a>

<a id="command-mc.admin.user.svcacct.add"></a>

> [!WARNING]
> **重要**
>
> 此命令已被替代，并将在未来的 MinIO 客户端版本中弃用。
>
> 从 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，请使用 [`mc admin accesskey create`](/docs/reference/minio-mc-admin/mc-admin-accesskey-create/#command-mc.admin.accesskey.create) 命令为内置 MinIO IDP 用户添加访问密钥。
>
> 如需为 AD/LDAP 用户添加访问密钥，请使用 [`mc idp ldap accesskey create`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create) 命令。

## 语法 {#id2}

[`mc admin user svcacct add`](#command-mc.admin.user.svcacct.add) 命令为现有 MinIO 或 AD/LDAP 用户添加新的访问密钥。

> [!NOTE]
> **OpenID Connect 用户的访问密钥**
>
> 要为 [OpenID Connect 用户](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 生成服务账户访问密钥，请使用 [MinIO Console](/docs/administration/minio-console/#minio-console)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会创建一个与现有 MinIO 用户关联的新访问密钥：

```shell
mc admin user svcacct add                       \
   --access-key "myuserserviceaccount"          \
   --secret-key "myuserserviceaccountpassword"  \
   --policy "/path/to/policy.json"              \
   myminio myuser
```

命令会返回该新账号的访问密钥和秘密密钥。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin user svcacct add             \
                                    [--access-key]  \
                                    [--secret-key]  \
                                    [--policy]      \
                                    [--comment]     \
                                    ALIAS           \
                                    USER
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.user.svcacct.add.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USER` {#mc.admin.user.svcacct.add.USER}

*mc-cmd*

*Required*

MinIO 要为其添加新访问密钥的用户名。

- 对于 [MinIO 管理的用户](/docs/administration/identity-access-management/minio-user-management/#minio-users)，指定该用户的访问密钥。
- 对于 [Active Directory/LDAP 用户](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap)，指定用户的 Distinguished Name。
- 对于 [OpenID Connect 用户](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid)，请使用 [MinIO Console](/docs/administration/minio-console/#minio-console) 生成访问密钥。

##### `--access-key` {#mc.admin.user.svcacct.add.-access-key}

*mc-cmd*

*Optional*

用作此账号访问密钥的字符串。 省略时，MinIO 会自动生成一个 20 个字符的随机值。

Access Key 名称在所有用户之间 *必须* 唯一。

##### `--comment` {#mc.admin.user.svcacct.add.-comment}

*mc-cmd*

*Optional*

> [!NOTE]
> **变更: RELEASE.2023-05-18T16-59-00Z**
>
> 已由 [`--description`](#mc.admin.user.svcacct.add.-description) 和 [`--name`](#mc.admin.user.svcacct.add.-name) 替代。
>
> 最初在 RELEASE.2023-01-28T20-29-38Z 版本中引入。

此选项已移除。 请改用 `--description` 或 `--name`。

##### `--description` {#mc.admin.user.svcacct.add.-description}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-18T16-59-00Z**

为服务账户添加描述。 例如，可以说明该服务账户存在的原因。

##### `--expiry` {#mc.admin.user.svcacct.add.-expiry}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-30T22-41-38Z**

为服务账户设置过期日期。 该日期必须是未来时间，不能设置已经过去的过期日期。

允许的日期和时间格式：

- `2023-06-24`
- `2023-06-24T10:00`
- `2023-06-24T10:00:00`
- `2023-06-24T10:00:00Z`
- `2023-06-24T10:00:00-07:00`

##### `--name` {#mc.admin.user.svcacct.add.-name}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2023-05-18T16-59-00Z**

为服务账户添加一个人类可读的名称。

##### `--policy` {#mc.admin.user.svcacct.add.-policy}

*mc-cmd*

*Optional*

要附加到新访问密钥的 [策略文档](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 路径，最大大小为 2048 个字符。 附加的策略不能授予父用户策略未明确允许的任何操作或资源访问权限。

##### `--secret-key` {#mc.admin.user.svcacct.add.-secret-key}

*mc-cmd*

*Optional*

与新账号关联的秘密密钥。 省略时，MinIO 会自动生成一个 40 字符的随机值。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。