---
title: "mc admin user svcacct enable"

weight: 40
---

<a id="mc-admin-user-svcacct-enable"></a>
<a id="minio-mc-admin-svcacct-enable"></a>

<a id="command-mc.admin.user.svcacct.enable"></a>

> [!WARNING]
> **重要**
>
> 此命令已被替代，并将在未来的 MinIO 客户端 发布版本中弃用。
>
> 从 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 起，使用 [`mc admin accesskey enable`](/docs/reference/minio-mc-admin/mc-admin-accesskey-enable/#command-mc.admin.accesskey.enable) 命令为内置 MinIO IDP 用户启用访问密钥。
>
> 如需为 AD/LDAP 用户启用访问密钥，请使用 [`mc idp ldap accesskey enable`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-enable/#command-mc.idp.ldap.accesskey.enable) 命令。

## 语法 {#id2}

[`mc admin user svcacct enable`](#command-mc.admin.user.svcacct.enable) 命令用于启用现有访问密钥。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令启用指定的访问密钥：

```shell
mc admin user svcacct enable myminio myuserserviceaccount
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin user svcacct enable          \
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

##### `ALIAS` {#mc.admin.user.svcacct.enable.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `SERVICEACCOUNT` {#mc.admin.user.svcacct.enable.SERVICEACCOUNT}

*mc-cmd*

*Required*

要启用的服务账户访问密钥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。