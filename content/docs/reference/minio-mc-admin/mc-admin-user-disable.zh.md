---
title: "mc admin user disable"

weight: 20
---

<a id="mc-admin-user-disable"></a>
<a id="minio-mc-admin-user-disable"></a>

<a id="command-mc.admin.user.disable"></a>

## 语法 {#id2}

[`mc admin user disable`](#command-mc.admin.user.disable) 命令用于在目标 MinIO 部署上禁用 [MinIO 用户](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp)。

客户端不能使用该用户凭证向 MinIO 部署进行身份验证。 禁用用户 *不会* 将该用户从部署中移除。 使用 [`mc admin user enable`](/docs/reference/minio-mc-admin/mc-admin-user-enable/#command-mc.admin.user.enable) 可在 MinIO 部署上启用已禁用的用户。

如需管理外部身份提供商用户，请参阅 [`OIDC`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 或 [`AD/LDAP`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` MinIO 部署上禁用用户 `myuser`：

```shell
mc admin user disable myminio myuser
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] admin user disable   \
                            ALIAS     \
                            USERNAME
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.user.disable.ALIAS}

*mc-cmd*

*Required*

要禁用用户所在 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USERNAME` {#mc.admin.user.disable.USERNAME}

*mc-cmd*

*Required*

要禁用的用户名。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 禁用用户 {#id6}

使用 [`mc admin user disable`](#command-mc.admin.user.disable) 在 MinIO 部署上禁用用户。

```shell
mc admin user disable ALIAS USERNAME
```

- 将 [`ALIAS`](#mc.admin.user.disable.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`USERNAME`](#mc.admin.user.disable.USERNAME) 替换为要禁用的用户名。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。