---
title: "mc idp ldap accesskey rm"

weight: 60
---

<a id="mc-idp-ldap-accesskey-rm"></a>
<a id="minio-mc-idp-ldap-accesskey-rm"></a>

<a id="command-mc.idp.ldap.accesskey.rm"></a>

<a id="command-mc.idp.ldap.accesskey.remove"></a>

## 描述 {#id2}

[`mc idp ldap accesskey rm`](#command-mc.idp.ldap.accesskey.rm) 从本地服务器中删除指定的访问密钥。

[`mc idp ldap accesskey rm`](#command-mc.idp.ldap.accesskey.rm) 也称为 [`mc idp ldap accesskey remove`](#command-mc.idp.ldap.accesskey.remove)。

此命令适用于 AD/LDAP 用户在通过 MinIO 完成身份验证后创建的 [访问密钥](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys)。

使用 [`mc idp ldap accesskey create`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-create/#command-mc.idp.ldap.accesskey.create) 命令创建 AD/LDAP 服务账户。

MinIO 支持使用 [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) 通过 [Security Token Service](/docs/developers/security-token-service/#minio-security-token-service) 生成临时访问密钥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
> 以下示例从 `minio` 部署中删除访问密钥 `mykey`：

```shell
mc idp ldap accesskey rm minio/ mykey
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令使用以下语法：

```shell
mc [GLOBALFLAGS] idp ldap accesskey rm              \
                                 ALIAS              \
                                 KEY
```

- 将 `ALIAS` 替换为已配置 AD/LDAP 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `KEY` 替换为要删除的访问密钥。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.accesskey.remove.ALIAS}

*mc-cmd*

*Required*

已配置 AD/LDAP 的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap accesskey ls minio
```

##### `KEY` {#mc.idp.ldap.accesskey.remove.KEY}

*mc-cmd*

*Required*

要删除的已配置访问密钥。

### 示例 {#id4}

从 `minio` 部署中删除访问密钥 `mykey`。

```shell
mc idp ldap accesskey rm minio/ mykey
```

### 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。