---
title: "mc admin idp ldap policy"

weight: 150
---

<a id="mc-admin-idp-ldap-policy"></a>
<a id="minio-mc-admin-idp-ldap-policy"></a>

<a id="command-mc.admin.idp.ldap.policy"></a>

> [!NOTE]
> **变更: RELEASE.2023-05-26T23-31-54Z**
>
> `mc admin idp ldap policy` 及其子命令已由 [`mc idp ldap policy`](/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy) 替代。

## 说明 {#id2}

[`mc admin idp ldap policy`](#command-mc.admin.idp.ldap.policy) 命令用于查看策略与关联组或用户之间的映射关系。

[`mc admin idp ldap policy`](#command-mc.admin.idp.ldap.policy) 命令包含以下子命令：

| 子命令 | 说明 |
| --- | --- |
| [`mc admin idp ldap policy attach`](#mc.admin.idp.ldap.policy.attach) | 将策略附加到实体 |
| [`mc admin idp ldap policy detach`](#mc.admin.idp.ldap.policy.detach) | 从实体分离策略 |
| [`mc admin idp ldap policy entities`](#mc.admin.idp.ldap.policy.entities) | 列出策略与实体的映射 |

## 语法 {#id3}

#### `attach` {#mc.admin.idp.ldap.policy.attach}

*mc-cmd*

将一个或多个策略附加到实体。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例将两个策略 `policy1` 和 `policy2` 附加到 `myminio` 部署上的 `projectb` 组。

```shell
 mc admin idp ldap policy attach myminio/                                               \
                                 policy1                                                \
                                 policy2                                                \
                                 --group='cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```

以下示例将策略 `userpolicy` 附加到 `myminio` 部署上的用户 `bobfisher`。

```shell
 mc admin idp ldap policy attach myminio/                                               \
                                 mypolicy                                               \
                                 policy2                                                \
                                 --user='uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap policy attach     \
                                POLICYNAME        \
                                [POLICY2] ...     \
                                ALIAS             \
                                [--user=`USER`]   \
                                [--group=`GROUP`]
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于配置 AD/LDAP 集成。
- 将 `POLICYNAME` 替换为要附加到实体的策略。 你可以列出多个策略并附加到该实体。
- 必须使用 `--user` 或 `--group` 其中之一。 每个命令中只能使用一次该标志。 不能在同一命令中同时使用这两个标志。
{{< /tab >}}
{{< /tabs >}}

#### `detach` {#mc.admin.idp.ldap.policy.detach}

*mc-cmd*

从实体分离一个或多个策略。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例从 `myminio` 部署上的 `projectb` 组分离两个策略 `policy1` 和 `policy2`。

```shell
 mc admin idp ldap policy detach myminio/                                               \
                                 policy1                                                \
                                 policy2                                                \
                                 --group='cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```

以下示例从 `myminio` 部署上的用户 `bobfisher` 分离策略 `userpolicy`。

```shell
 mc admin idp ldap policy detach myminio/                                               \
                                 mypolicy                                               \
                                 policy2                                                \
                                 --user='uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap policy detach     \
                                POLICYNAME        \
                                [POLICY2] ...     \
                                ALIAS             \
                                [--user=`USER`]   \
                                [--group=`GROUP`]
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于配置 AD/LDAP 集成。
- 将 `POLICYNAME` 替换为要从实体分离的策略。 你可以列出多个策略并从该实体分离。
- 必须使用 `--user` 或 `--group` 其中之一。 每个命令中只能使用一次该标志。 不能在同一命令中同时使用这两个标志。
{{< /tab >}}
{{< /tabs >}}

#### `entities` {#mc.admin.idp.ldap.policy.entities}

*mc-cmd*

显示用户、组和/或策略的映射列表。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例列出 `myminio` 部署中某个特定策略、一组组以及部分用户的全部映射关系。

具体包括： - 映射到 `finteam-policy` 策略的用户。 - 分配给用户 `uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io` 的策略 - 分配给组 `cn=projectb,ou=groups,ou=swengg,dc=min,dc=io` 的策略

```shell
 mc admin idp ldap policy entities myminio/                                            \
                              --policy finteam-policy                                  \
                              --user 'uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'  \
                              --group 'cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap policy entities                \
                                ALIAS                          \
                                [--user `value`, -u `value`]   \
                                [--group `value`, -g `value`]  \
                                [--policy value]
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于配置 AD/LDAP 集成。
- 在命令中可按需多次使用 `--user`、`--group` 和/或 `--policy` 标志。
- 对于每个标志，输出会列出映射到指定策略、用户或组的实体。
- 省略所有标志可返回所有策略的映射列表。
{{< /tab >}}
{{< /tabs >}}

## 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。