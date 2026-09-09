---
title: "mc admin policy detach"

weight: 30
---

<a id="mc-admin-policy-detach"></a>

<a id="command-mc.admin.policy.detach"></a>

## 语法 {#id2}

从 [MinIO 管理的用户或组](/docs/administration/identity-access-management/minio-user-management/#minio-users) 中移除一个或多个 IAM 策略。

必须且只能指定 [`--user`](#mc.admin.policy.detach.-user) 或 [`--group`](#mc.admin.policy.detach.-group) 其中之一。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从别名为 `myminio` 的部署中为用户 `james` 解绑 `readonly` 策略。

```shell
mc admin policy detach myminio readonly --user james
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc admin policy detach TARGET                         \
                       POLICY                         \
                       [POLICY...]                    \
                       [--user USER | --group GROUP]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

> [!WARNING]
> **重要**
>
> 此命令仅用于管理 [MinIO 管理](/docs/administration/identity-access-management/minio-user-management/#minio-users) 用户的策略关联。
>
> 如需管理 OpenID 管理的用户策略，请参见 [OpenID Connect 访问管理](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid)。
>
> 如需从 Active Directory/LDAP 用户或组解绑策略，请使用 [`mc idp ldap policy detach`](/docs/reference/minio-mc/mc-idp-ldap-policy-detach/#command-mc.idp.ldap.policy.detach)。

### 参数 {#id3}

[`mc admin policy detach`](#command-mc.admin.policy.detach) 命令接受以下参数：

##### `TARGET` {#mc.admin.policy.detach.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，其中包含你要解绑一个或多个策略的用户或组。

##### `POLICY` {#mc.admin.policy.detach.POLICY}

*mc-cmd*

*Required*

要从用户或组解绑的策略名称。 你可以通过空格分隔多个策略名称，一次解绑多个策略。

MinIO 部署默认包含以下 [内置策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-built-in)：

- [`readonly`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readonly)
- [`readwrite`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.readwrite)
- [`diagnostics`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.diagnostics)
- [`writeonly`](/docs/administration/identity-access-management/policy-based-access-control/#userpolicy.writeonly)

##### `--user` {#mc.admin.policy.detach.-user}

*mc-cmd*

*Optional*

要解绑策略的身份用户名。 只能指定一个用户。

必须包含 `--user` 或 `--group` 标志之一。 不能将 `--user` 与 `--group` 标志同时使用。

##### `--group` {#mc.admin.policy.detach.-group}

*mc-cmd*

*Optional*

要解绑策略的组名称。 只能指定一个组。

组内所有成员都会失去该组关联策略所授予的权限，除非这些权限也由用户所属的其他策略或组授予。

必须包含 `--group` 或 `--user` 标志之一。 不能将 `--group` 与 `--user` 标志同时使用。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

从别名为 `myminio` 的部署中为用户 `james` 解绑 `readonly` 策略。

```shell
mc admin policy detach myminio readonly --user james
```

从别名为 `myminio` 的部署中为组 `legal` 解绑 `audit-policy` 和 `acct-policy` 策略。

```shell
mc admin policy detach myminio audit-policy acct-policy --group legal
```