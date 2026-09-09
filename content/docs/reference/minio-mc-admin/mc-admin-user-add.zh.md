---
title: "mc admin user add"

weight: 10
---

<a id="mc-admin-user-add"></a>
<a id="minio-mc-admin-user-add"></a>

<a id="command-mc.admin.user.add"></a>

## 语法 {#id2}

[`mc admin user add`](#command-mc.admin.user.add) 命令会在目标 MinIO 部署中添加一个新的 [MinIO 用户](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp)。

要管理外部身份提供商用户，请参见 [`OIDC`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 或 [`AD/LDAP`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会在 `myminio` MinIO 部署上创建一个新用户 `newuser`：

```shell
mc admin user add myminio newuser newusersecret
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin user add        \
                            ALIAS      \
                            ACCESSKEY  \
                            SECRETKEY
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ACCESSKEY` {#mc.admin.user.add.ACCESSKEY}

*mc-cmd*

*Required*

用于唯一标识新用户的访问密钥，类似于用户名。

##### `ALIAS` {#mc.admin.user.add.ALIAS}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于在该部署上创建新用户。

##### `SECRETKEY` {#mc.admin.user.add.SECRETKEY}

*mc-cmd*

*Required*

新用户的 secret key。创建 secret key 时请参考以下建议：

- 密钥应为 *唯一* 值
- 密钥应足够 *长*（超过 12 个字符）
- 密钥应具备 *复杂性*（混合使用字符、数字和符号）

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 创建新用户 {#id6}

使用 [`mc admin user add`](#command-mc.admin.user.add) 在 MinIO 部署上创建用户：

```shell
   mc admin user add ALIAS ACCESSKEY SECRETKEY
```

- 将 [`ALIAS`](#mc.admin.user.add.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`ACCESSKEY`](#mc.admin.user.add.ACCESSKEY) 替换为该用户的 access key。
- 将 [`SECRETKEY`](#mc.admin.user.add.SECRETKEY) 替换为该用户的 secret key。 MinIO *不* 提供任何在设置后检索 secret key 的方法。

请为 `ACCESSKEY` 和 `SECRETKEY` 都指定唯一、随机且足够长的字符串。 组织在生成用于 access key 或 secret key 的值时，可能存在特定的内部或监管要求。

## 行为 {#id9}

### 新用户默认没有策略 {#id10}

新创建的用户默认 *没有* 任何策略，因此无法在 MinIO 部署上执行任何操作。 要配置用户的已分配策略，你可以执行以下一项或两项操作：

- 使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 将一个或多个策略关联到用户。
- 使用 [`mc admin group add`](/docs/reference/minio-mc-admin/mc-admin-group/#mc.admin.group.add) 将用户关联到组。 用户会继承分配给该组的所有策略。

有关 MinIO 用户和组的更多信息，请参见 [用户管理](/docs/administration/identity-access-management/minio-user-management/#minio-users) 和 [组管理](/docs/administration/identity-access-management/minio-group-management/#minio-groups)。 有关 MinIO 策略的更多信息，请参见 [MinIO Policy Based Access Control](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。