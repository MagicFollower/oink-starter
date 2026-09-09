---
title: "mc admin user svcacct info"

weight: 50
---

<a id="mc-admin-user-svcacct-info"></a>
<a id="minio-mc-admin-svcacct-info"></a>

<a id="command-mc.admin.user.svcacct.info"></a>

> [!WARNING]
> **重要**
>
> 此命令已被替代，并将在未来的 MinIO 客户端版本中弃用。
>
> 从 MinIO客户端版本RELEASE.2024-10-08T09-37-26Z 开始，请使用 [`mc admin accesskey info`](/docs/reference/minio-mc-admin/mc-admin-accesskey-info/#command-mc.admin.accesskey.info) 命令显示内置 MinIO IDP 用户的 access key 信息。
>
> 对于 AD/LDAP 用户的 access key，请使用 [`mc idp ldap accesskey info`](/docs/reference/minio-mc/mc-idp-ldap-accesskey-info/#command-mc.idp.ldap.accesskey.info) 命令。

## 语法 {#id2}

[`mc admin user svcacct info`](#command-mc.admin.user.svcacct.info) 命令返回指定 [access key](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys) 的描述信息。

在 MinIO 中，“Access Keys” 与 “Service Accounts” 功能等效，并取代了后者这一概念。

描述输出在可用时包含以下详细信息：

- Access Key
- 指定 access key 的父用户
- access key 状态（`on` 或 `off`）
- 策略（单个或多个）
- 注释
- 过期时间

使用 [`--policy`](#mc.admin.user.svcacct.info.-policy) 查看附加的策略。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令返回指定 access key 的信息：

```shell
mc admin user svcacct info myminio myuseraccesskey
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] admin user svcacct info           \
                                    [--policy]     \
                                    ALIAS          \
                                    ACCESSKEY
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.user.svcacct.info.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `ACCESSKEY` {#mc.admin.user.svcacct.info.ACCESSKEY}

*mc-cmd*

*Required*

要显示的 service account access key。

##### `--policy` {#mc.admin.user.svcacct.info.-policy}

*mc-cmd*

*Optional*

显示附加到指定 service account 的策略。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 显示 Service Account 详情 {#service-account}

使用 [`mc admin user svcacct info`](#command-mc.admin.user.svcacct.info) 显示 MinIO 部署上某个 service account 的详细信息：

```shell
   mc admin user svcacct info ALIAS ACCESSKEY
```

- 将 [`ALIAS`](/docs/reference/minio-mc-admin/mc-admin-user-add/#mc.admin.user.add.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`ACCESSKEY`](#mc.admin.user.svcacct.info.ACCESSKEY) 替换为 service account access key。

输出类似如下：

```shell
AccessKey: myuserserviceaccount
ParentUser: myuser
Status: on
Comment:
Policy: implied
Expiration: no-expiry
```

### 显示 Service Account 策略详情 {#id6}

使用 [`mc admin user svcacct info`](#command-mc.admin.user.svcacct.info) 显示附加到 service account 的策略：

```shell
   mc admin user svcacct info --policy ALIAS ACCESSKEY
```

- 将 [`ALIAS`](/docs/reference/minio-mc-admin/mc-admin-user-add/#mc.admin.user.add.ALIAS) 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`ACCESSKEY`](#mc.admin.user.svcacct.info.ACCESSKEY) 替换为 service account access key。

输出类似如下：

```shell
{
 "Version": "2012-10-17",
 "Statement": [
  {
   "Effect": "Allow",
   "Action": [
    "s3:*"
   ],
   "Resource": [
    "arn:aws:s3:::*"
   ]
  }
 ]
}
```

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。