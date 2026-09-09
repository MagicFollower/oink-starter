---
title: "mc idp ldap accesskey ls"

weight: 50
---

<a id="mc-idp-ldap-accesskey-ls"></a>
<a id="minio-mc-idp-ldap-accesskey-ls"></a>

<a id="command-mc.idp.ldap.accesskey.list"></a>

<a id="command-mc.idp.ldap.accesskey.ls"></a>

## 描述 {#id2}

[`mc idp ldap accesskey ls`](#command-mc.idp.ldap.accesskey.ls) 用于显示 LDAP 访问密钥对列表。

[`mc idp ldap accesskey ls`](#command-mc.idp.ldap.accesskey.ls) 也称为 [`mc idp ldap accesskey list`](#command-mc.idp.ldap.accesskey.list)。

此命令适用于 AD/LDAP 用户在通过 MinIO 完成身份验证后创建的 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)。

使用 [`mc idp ldap accesskey create`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create) 命令创建 AD/LDAP 服务账户。

MinIO 支持使用 [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) 通过 [Security Token Service](/docs/developers/security-token-service/#minio-security-token-service) 生成临时访问密钥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
> 以下示例返回 `minio` [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 上与已认证用户关联的访问密钥列表：

```shell
mc idp ldap accesskey ls minio/
```

如果已认证用户具有 `admin:ListUsers` 权限，则该示例命令会返回所有用户及其关联访问密钥的列表。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] idp ldap accesskey ls           \
                                 ALIAS           \
                                 [--all]         \
                                 [--self]        \
                                 [--svcacc-only] \
                                 [--temp-only]   \
                                 [--users-only]  \
                                 [DN] ...
```

- 将 `ALIAS` 替换为已配置 AD/LDAP 集成的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `DN` 替换为用户的 [distinguished name](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names) 字符串。 你可以用空格分隔多个 distinguished name。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.accesskey.ls.ALIAS}

*mc-cmd*

*Required*

已配置 AD/LDAP 的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap accesskey ls minio
```

##### `--all` {#mc.idp.ldap.accesskey.ls.-all}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-07-31T15-58-33Z

列出所有 LDAP 用户的全部访问密钥。

##### `--self` {#mc.idp.ldap.accesskey.ls.-self}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-07-31T15-58-33Z

列出当前已认证用户的访问密钥。

##### `--svcacc-only` {#mc.idp.ldap.accesskey.ls.-svcacc-only}

*mc-cmd*

*Optional*

仅输出服务账户访问密钥。

与 [`--temp-only`](#mc.idp.ldap.accesskey.ls.-temp-only) 互斥。

##### `--temp-only` {#mc.idp.ldap.accesskey.ls.-temp-only}

*mc-cmd*

*Optional*

仅输出临时访问密钥。

与 [`--svcacc-only`](#mc.idp.ldap.accesskey.ls.-svcacc-only) 互斥。

##### `--users-only` {#mc.idp.ldap.accesskey.ls.-users-only}

*mc-cmd*

*Optional*

仅输出用户 distinguished name。

### 示例 {#id4}

#### 列出所有访问密钥 {#id5}

要返回所有访问密钥列表，你必须先以 `admin` 用户完成认证。 认证完成后，以下命令会返回 `minio` 部署上的全部 AD/LDAP 访问密钥。

```shell
mc idp ldap accesskey ls minio
```

> [!NOTE]
> **说明**
>
> 如果用户没有 `admin:ListUsers` 权限，该命令仅返回已认证用户的访问密钥列表。

#### 列出用户 Distinguished Name {#distinguished-name}

要返回某个部署的 DN 列表，你必须先以具有 `admin:ListUsers` 权限的用户完成认证。 认证完成后，以下命令会输出 `minio` 部署上的 AD/LDAP distinguished name。

```shell
mc idp ldap accesskey ls minio --users-only
```

#### 列出临时访问密钥 {#id6}

要返回某个部署的全部临时访问密钥列表，你必须先以具有 `admin:ListUsers` 权限的用户完成认证。 认证完成后，以下命令会输出 distinguished name 及其关联临时访问密钥的列表。

```shell
mc idp ldap accesskey ls minio --temp-only
```

#### 列出某个用户的访问密钥 {#id7}

以下命令返回 `minio` 部署上用户 `bobfisher` 的 AD/LDAP 访问密钥。

```shell
mc idp ldap accesskey list minio/ uid=bobfisher,dc=min,dc=io
```

#### 列出多个用户的访问密钥 {#id8}

以下命令返回 `minio` 部署上用户 `bobfisher` 和 `cody3` 的 AD/LDAP 访问密钥。

```shell
mc idp ldap accesskey list minio/ uid=bobfisher,dc=min,dc=io uid=cody3,dc=min,dc=io
```

#### 列出已认证用户的访问密钥 {#id9}

以下命令返回 `minio` 部署上当前已认证用户的 AD/LDAP 访问密钥。

```shell
mc idp ldap accesskey list minio/
```

> [!NOTE]
> **说明**
>
> 如果已认证用户具有 `admin:ListUsers` 权限，则该命令会返回部署上所有用户及其访问密钥列表。

### 全局参数 {#id10}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id11}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。