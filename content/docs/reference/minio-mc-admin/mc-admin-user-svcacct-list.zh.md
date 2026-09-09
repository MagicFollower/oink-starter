---
title: "mc admin user svcacct ls"

weight: 60
---

<a id="mc-admin-user-svcacct-ls"></a>
<a id="minio-mc-admin-svcacct-list"></a>

<a id="command-mc.admin.user.svcacct.list"></a>

<a id="command-mc.admin.user.svcacct.ls"></a>

> [!WARNING]
> **重要**
>
> 此命令已被替代，并将在未来的 MinIO 客户端版本中弃用。
>
> 从 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，请使用 [`mc admin accesskey ls`](/docs/reference/minio-mc-admin/mc-admin-accesskey-list/#command-mc.admin.accesskey.ls) 命令列出 MinIO 内置 IDP 用户的访问密钥。
>
> 对于 AD/LDAP 用户的访问密钥，请使用 [`mc idp ldap accesskey ls`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-ls/#command-mc.idp.ldap.accesskey.ls) 命令。

## 语法 {#id2}

[`mc admin user svcacct ls`](#command-mc.admin.user.svcacct.ls) 命令列出与指定用户关联的所有访问密钥。

[`mc admin user svcacct list`](#command-mc.admin.user.svcacct.list) 别名与 [`mc admin user svcacct ls`](#command-mc.admin.user.svcacct.ls) 具有等效功能。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出用户名为 `admin1` 的用户关联的所有访问密钥：

```shell
mc admin user svcacct ls myminio admin1
```

输出如下所示：

```shell
   Access Key        | Expiry
5XF3ZHNZK6FBDWH9JMLX | 2023-06-24 07:00:00 +0000 UTC
F4V2BBUZSWY7UG96ED70 | 2023-12-24 18:00:00 +0000 UTC
FZVSEZ8NM9JRBEQZ7B8Q | no-expiry
HOXGL8ON3RG0IKYCHCUD | no-expiry
```

> [!NOTE]
> **新增: RELEASE.2023-05-26T23-31-54Z**
>
> 访问密钥列表包含到期时间；对于永不过期的密钥，显示 `no-expiry`。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin user svcacct ls   \
                                    ALIAS  \
                                    USER
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.user.svcacct.ls.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USER` {#mc.admin.user.svcacct.ls.USER}

*mc-cmd*

*Required*

要列出其访问密钥的用户名。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。