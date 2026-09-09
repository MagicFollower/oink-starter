---
title: "mc admin user info"

weight: 40
---

<a id="mc-admin-user-info"></a>
<a id="minio-mc-admin-user-info"></a>

<a id="command-mc.admin.user.info"></a>

## 语法 {#id2}

[`mc admin user info`](#command-mc.admin.user.info) 命令返回目标 MinIO 部署中某个 [MinIO 用户](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp) 的详细信息。

如需管理外部身份提供商用户，请参见 [`OIDC`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 或 [`AD/LDAP`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令返回 `myminio` MinIO 部署中用户 `myuser` 的详细信息：

```shell
mc admin user info myminio myuser
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin user info      \
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

##### `ALIAS` {#mc.admin.user.info.ALIAS}

*mc-cmd*

*Required*

用于获取用户信息的已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `USERNAME` {#mc.admin.user.info.USERNAME}

*mc-cmd*

要查询信息的用户名。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

> [!NOTE]
> **变更: RELEASE.2023-05-26T23-31-54Z**
>
> `mc admin user info --json` 输出包含用户通过组成员关系继承的策略，位于 `memberOf` 中。

## 示例 {#id5}

### 查看用户详细信息 {#id6}

使用 [`mc admin user info`](#command-mc.admin.user.info) 查看 MinIO 部署中某个用户的详细信息：

```shell
mc admin user info ALIAS USERNAME
```

- 将 [`ALIAS`](#mc.admin.user.info.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`USERNAME`](#mc.admin.user.info.USERNAME) 替换为要显示信息的用户名。

对于 [MinIO 内部身份提供商 (IDP)](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp)，输出类似如下：

```shell
AccessKey: miniouser
Status: enabled
PolicyName:
MemberOf: []
Authentication: builtin (miniouser)
```

对于 LDAP 等 [第三方](/docs/operations/external-iam/#minio-external-identity-management) 身份服务，输出类似如下：

```shell
AccessKey: uid=dillon,ou=people,ou=swengg,dc=min,dc=io
Status:
PolicyName: consoleAdmin
MemberOf: []
Authentication: ldap/localhost:1389 (uid=dillon,ou=people,ou=swengg,dc=min,dc=io)
```

### 查看来自组成员关系的策略 {#id7}

将 [`mc admin user info`](#command-mc.admin.user.info) 与 `--json` 配合使用，可查看用户从其 [组成员关系](/docs/administration/identity-access-management/minio-group-management/#minio-groups) 继承的策略：

```shell
mc admin user info ALIAS USERNAME --json
```

- 将 [`ALIAS`](#mc.admin.user.info.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`USERNAME`](#mc.admin.user.info.USERNAME) 替换为要显示信息的用户名。

输出中的 `memberOf` 属性包含该用户所属组的列表，以及附加到各组的策略。 输出类似如下：

```shell
{
 "status": "success",
 "accessKey": "myuser",
 "userStatus": "enabled",
 "memberOf": [
  {
   "name": "testingGroup",
   "policies": [
    "testingGroupPolicy"
   ]
 "authentication": builtin (myuser)
  }
 ]
}
```

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。