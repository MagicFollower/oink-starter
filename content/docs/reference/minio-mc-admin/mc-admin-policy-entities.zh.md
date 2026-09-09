---
title: "mc admin policy entities"

weight: 40
---

<a id="mc-admin-policy-entities"></a>

<a id="command-mc.admin.policy.entities"></a>

## 语法 {#id2}

列出目标 MinIO 部署中与策略、用户或组关联的实体。

> [!NOTE]
> **变更: RELEASE.2023-05-27T05-56-19Z**
>
> 此命令仅返回 [MinIO 管理的用户和组](/docs/administration/identity-access-management/minio-user-management/#minio-users)。

如需列出与 Active Directory 或 LDAP（AD/LDAP）配置关联的实体，请使用 [`mc idp ldap policy entities`](/docs/reference/minio-mc/mc-idp-ldap-policy-entities/#command-mc.idp.ldap.policy.entities)。

例如，你可以列出附加到某个策略的所有用户和组，或者列出附加到特定用户或组的所有策略。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回别名为 `myminio` 的部署中与用户 `bob` 关联的策略列表。

```shell
mc admin policy entities myminio/ --user bob
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc admin policy entities         \
                TARGET           \
                [--user value]   \
                [--group value]  \
                [--policy value]
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
> 此命令仅用于管理 [MinIO 管理的](/docs/administration/identity-access-management/minio-user-management/#minio-users) 用户的策略关联。
>
> 如需管理 OpenID 管理用户的策略，请参阅 [OpenID Connect 访问管理](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid)。
>
> 如需查看 Active Directory/LDAP 用户或组的策略，请使用 [`mc idp ldap policy entities`](/docs/reference/minio-mc/mc-idp-ldap-policy-entities/#command-mc.idp.ldap.policy.entities)。

### 参数 {#id3}

[`mc admin policy entities`](#command-mc.admin.policy.entities) 命令接受以下参数：

##### `TARGET` {#mc.admin.policy.entities.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，将在该部署上添加新策略。

##### `--group` {#mc.admin.policy.entities.-group}

*mc-cmd*

*Optional*

要列出其附加策略的组身份名称。

你可以通过多次重复该标志来包含多个组。 命令会返回每个组及其关联实体列表。

##### `--policy` {#mc.admin.policy.entities.-policy}

*mc-cmd*

*Optional*

要列出其关联实体的策略名称。

你可以通过多次重复该标志来包含多个策略。 命令会返回每个策略及其所有关联实体列表。

##### `--user` {#mc.admin.policy.entities.-user}

*mc-cmd*

*Optional*

要列出其附加策略的身份用户名。

你可以通过多次重复该标志来包含多个用户。 命令会返回每个用户及其关联策略列表。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出某个部署的所有实体及策略关联 {#id6}

以下命令列出别名为 `myminio` 的部署上所有策略及其关联的实体映射。

```shell
mc admin policy entities myminio/
```

### 列出与两个不同策略关联的实体 {#id7}

以下命令列出别名为 `myminio` 的部署上与策略 `inteam-policy` 和 `mlteam-policy` 关联的所有实体。

```shell
mc admin policy entities myminio/ --policy finteam-policy --policy mlteam-policy
```

### 列出与两个不同用户关联的策略 {#id8}

以下命令列出别名为 `myminio` 的部署上与用户 `bob` 和 `james` 关联的所有策略。

该命令先输出与 `bob` 关联的策略列表，再输出别名为 `myminio` 的部署中与 `james` 关联的策略列表。

```shell
mc admin policy entities myminio/ --user bob --user james
```

### 列出与两个不同组关联的策略 {#id9}

以下命令列出别名为 `myminio` 的部署上与组 `auditors` 和 `accounting` 关联的所有策略。

该命令先输出与组 `auditors` 关联的策略列表，再输出别名为 `myminio` 的部署中与组 `accounting` 关联的策略列表。

```shell
mc admin policy entities play/ --group auditors --group accounting
```

### 列出与一个策略、一个组和一个用户关联的策略 {#id10}

以下命令列出别名为 `myminio` 的部署上与策略 `finteam-policy`、用户 `bobfisher` 和组 `consulting` 关联的所有策略。

该命令先输出与策略 `finteam-policy` 关联的组和用户列表，然后列出与用户 `bobfisher` 关联的策略，最后列出别名为 `myminio` 的部署中与组 `consulting` 关联的策略。

```shell
mc admin policy entities play/ \
           --policy finteam-policy --user bobfisher --group consulting
```

## 输出 {#id11}

命令输出类似如下：

```shell
Query time: 2023-04-04T20:39:27Z
  Policy -> Entity Mappings:
    Policy: finteam-policy
      User Mappings:
        bobfisher
    Policy: diagnostics
      User Mappings:
        james
        bobfisher
        marcia
      Group Mappings:
        consulting
        auditors
  User -> Policy Mappings:
    User: bobfisher
      ALLOW_PUBLIC_READ
      finteam-policy
      diagnostics
      readonly
      readwrite
      writeonly
```