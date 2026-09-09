---
title: "mc admin idp ldap"

weight: 140
---

<a id="mc-admin-idp-ldap"></a>
<a id="minio-mc-admin-idp-ldap"></a>

<a id="command-mc.admin.idp.ldap"></a>

> [!NOTE]
> **变更: RELEASE.2023-05-26T23-31-54Z**
>
> `mc admin idp ldap` 及其子命令已由 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 替代。

## 说明 {#id2}

[`mc admin idp ldap`](#command-mc.admin.idp.ldap) 命令允许你为第三方 [Active Directory 或 LDAP 身份与访问管理（IAM）集成](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 添加、修改、查看、列出、移除、启用和禁用服务器配置。

在 [配置 AD/LDAP 连接](/docs/operations/external-iam/configure-ad-ldap-external-identity-management/#minio-authenticate-using-ad-ldap-generic) 时，可将配置设置作为使用环境变量的替代方案。

> [!NOTE]
> **说明**
>
> 配置设置 **不会** 覆盖通过环境变量配置的设置。

[`mc admin idp ldap`](#command-mc.admin.idp.ldap) 命令包含以下子命令：

| 子命令 | 说明 |
| --- | --- |
| [`mc admin idp ldap add`](#mc.admin.idp.ldap.add) | 创建 AD/LDAP IDP 服务器配置。 |
| [`mc admin idp ldap update`](#mc.admin.idp.ldap.update) | 修改现有的 AD/LDAP IDP 服务器配置。 |
| [`mc admin idp ldap ls`](#mc.admin.idp.ldap.ls) | 列出 AD/LDAP 服务器配置。 |
| [`mc admin idp ldap rm`](#mc.admin.idp.ldap.rm) | 从部署中移除 AD/LDAP IDP 服务器配置。 |
| [`mc admin idp ldap info`](#mc.admin.idp.ldap.info) | 显示指定 AD/LDAP 服务器配置的详细信息。 |
| [`mc admin idp ldap enable`](#mc.admin.idp.ldap.enable) | 启用 AD/LDAP 服务器配置。 |
| [`mc admin idp ldap disable`](#mc.admin.idp.ldap.disable) | 禁用 AD/LDAP 服务器配置。 |
| [`mc admin idp ldap policy entities`](/docs/reference/deprecated/mc-admin-idp-ldap-policy/#mc.admin.idp.ldap.policy.entities) | 列出策略关联实体。 |

## 配置参数 {#id3}

[`mc admin idp ldap`](#command-mc.admin.idp.ldap) 子命令支持配置参数。 这些参数定义了服务器与 Active Directory 或 LDAP IAM 提供方的交互方式。

有关配置参数的更详细说明，请参阅 [配置设置文档](/docs/reference/minio-server/settings/iam/ldap/#minio-ldap-config-settings)。

## 语法 {#id4}

#### `add` {#mc.admin.idp.ldap.add}

*mc-cmd*

为 AD/LDAP 提供方创建新配置。 每个部署中，MinIO 最多仅支持 *一个* (1) AD/LDAP 提供方。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例为 `myminio` 部署设置 AD/LDAP 配置参数。

```shell
 mc admin idp ldap add                                               \
      myminio                                                        \
      server_addr=myldapserver:636                                   \
      lookup_bind_dn=cn=admin,dc=min,dc=io                           \
      lookup_bind_password=somesecret                                \
      user_dn_search_base_dn=dc=min,dc=io                            \
      user_dn_search_filter="(uid=%s)"                               \
      group_search_base_dn=ou=swengg,dc=min,dc=io                    \
      group_search_filter="(&(objectclass=groupofnames)(member=%d))"
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap add          \
                           ALIAS             \
                           [CFG_PARAM1]      \
                           [CFG_PARAM2]...
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于创建 AD/LDAP 集成配置。
- 将 `[CFG_PARAM#]` 替换为各个 [配置设置](/docs/reference/minio-server/settings/iam/ldap/#minio-ldap-config-settings) 键值对，格式为 `PARAMETER="value"`。
{{< /tab >}}
{{< /tabs >}}

#### `update` {#mc.admin.idp.ldap.update}

*mc-cmd*

修改 AD/LDAP 提供方现有的一组配置。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例修改 `myminio` 部署中的两个 AD/LDAP 配置参数。

```shell
mc admin idp ldap update                                \
                  myminio                               \
                  lookup_bind_dn=cn=admin,dc=min,dc=io  \
                  lookup_bind_password=somesecret
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap update           \
                                ALIAS            \
                                [CFG_PARAM1]     \
                                [CFG_PARAM2]...
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于更新 AD/LDAP 集成配置。
- 将 `[CFG_PARAM#]` 替换为要更新的各个 [配置设置](/docs/reference/minio-server/settings/iam/ldap/#minio-ldap-config-settings) 键值对，格式为 `PARAMETER="value"`。
{{< /tab >}}
{{< /tabs >}}

#### `ls, list` {#mc.admin.idp.ldap.ls}

*mc-cmd*

列出 AD/LDAP 提供方现有的一组配置。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例列出 `myminio` 部署中的 AD/LDAP 配置参数。

```shell
mc admin idp ldap ls myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap ls ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于列出 AD/LDAP 集成配置。
{{< /tab >}}
{{< /tabs >}}

#### `rm, remove` {#mc.admin.idp.ldap.rm}

*mc-cmd*

移除 AD/LDAP 提供方现有配置。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例移除 `myminio` 部署中的 AD/LDAP 提供方设置。

```shell
mc admin idp ldap rm myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap rm     \
                                ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于移除 AD/LDAP 集成配置。
{{< /tab >}}
{{< /tabs >}}

#### `info` {#mc.admin.idp.ldap.info}

*mc-cmd*

输出指定 MinIO 部署上 AD/LDAP 提供方的当前配置。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例输出 `myminio` 部署上的 AD/LDAP 配置参数。

```shell
mc admin idp ldap info myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap info     \
                                ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于获取 AD/LDAP 集成信息。
{{< /tab >}}
{{< /tabs >}}

#### `enable` {#mc.admin.idp.ldap.enable}

*mc-cmd*

启用当前已配置的 AD/LDAP 提供方。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例在 `myminio` 部署上启用 AD/LDAP 配置。

```shell
mc admin idp ldap enable       \
                  myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap enable     \
                                ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于启用 AD/LDAP 集成配置。
{{< /tab >}}
{{< /tabs >}}

#### `disable` {#mc.admin.idp.ldap.disable}

*mc-cmd*

禁用当前已配置的 AD/LDAP 提供方。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下示例在 `myminio` 部署上禁用 AD/LDAP 配置。

```shell
mc admin idp ldap disable      \
                  myminio
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp ldap disable       \
                                ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于禁用 AD/LDAP 集成配置。
{{< /tab >}}
{{< /tabs >}}

## 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。