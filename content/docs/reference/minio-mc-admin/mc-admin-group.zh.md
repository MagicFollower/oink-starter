---
title: "mc admin group"

weight: 60
---

<a id="mc-admin-group"></a>

<a id="command-mc.admin.group"></a>

## 说明 {#id2}

[`mc admin group`](#command-mc.admin.group) 命令用于管理 MinIO 部署上的组。

[组](/docs/administration/identity-access-management/minio-group-management/#minio-groups) 是 [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 的集合。每个组都可以分配一个或多个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)，用于明确列出允许或拒绝组成员访问的 操作和资源。对于具有相同访问模式和工作负载的用户，组提供了一种 简化的共享权限管理方式。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

### 组与基于策略的访问控制 {#id3}

MinIO 使用 基于策略的访问控制 (PBAC) 对已成功在部署上 *认证* 的用户执行 *授权*。每条策略都包含规则，用于规定该部署上 允许或拒绝的操作/资源。可以为一个组分配一个或多个 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。属于该组的用户会继承该组已分配的策略。用户的 总权限集合包括其显式分配的策略，*以及* 通过组成员关系继承的策略。

新创建的组默认 *不* 包含任何策略。要配置组的已分配策略，请使用 [`mc admin policy attach`](/docs/reference/minio-mc-admin/mc-admin-policy-attach/#command-mc.admin.policy.attach) 命令。

有关 MinIO 用户和组的更多信息，请参见 [用户管理](/docs/administration/identity-access-management/minio-user-management/#minio-users) 和 [组管理](/docs/administration/identity-access-management/minio-group-management/#minio-groups)。有关 MinIO 策略的更多信息， 请参见 [MinIO Policy Based Access Control](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

> [!NOTE]
> **`Deny` 会覆盖 `Allow`**
>
> MinIO 遵循 IAM 标准：在同一操作或资源上，`Deny` 规则会覆盖 `Allow` 规则。 例如，如果某个用户显式分配的策略对某个操作/资源包含 `Allow` 规则， 而该用户所属的某个组所分配策略对同一操作/资源包含 `Deny` 规则， 则 MinIO 只会应用 `Deny` 规则。
>
> 有关 IAM 策略评估逻辑的更多信息，请参见 IAM 文档中的 [Determining Whether a Request is Allowed or Denied Within an Account](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html#policy-eval-denyallow)。

## 示例 {#id4}

### 创建新组 {#id5}

使用 [`mc admin group add`](#mc.admin.group.add) 在兼容 S3 的主机上创建新组：

```shell
mc admin group add ALIAS GROUPNAME MEMBER [MEMBER...]
```

- 将 [`ALIAS`](#mc.admin.group.add.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`GROUPNAME`](#mc.admin.group.add.GROUPNAME) 替换为要创建的 组名。
- 将 [`MEMBER`](#mc.admin.group.add.MEMBERS) 替换为 S3 主机上 *至少* 一个 [`用户`](/docs/reference/minio-mc-admin/mc-admin-user/#command-mc.admin.user)。多个成员可按列表方式指定： `MEMBER1 MEMBER2 MEMBER3`

### 列出可用组 {#id6}

使用 [`mc admin group ls`](#mc.admin.group.ls) 列出兼容 S3 主机上的所有组：

```shell
mc admin group ls ALIAS
```

- 将 [`ALIAS`](#mc.admin.group.ls.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

### 查看组详情 {#id7}

使用 [`mc admin group info`](#mc.admin.group.info) 查看兼容 S3 主机上的组详细信息：

```shell
mc admin group info ALIAS GROUPNAME
```

- 将 [`ALIAS`](#mc.admin.group.info.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`GROUPNAME`](#mc.admin.group.info.GROUPNAME) 替换为 组名。

### 删除组 {#id8}

使用 [`mc admin group rm`](#mc.admin.group.rm) 从兼容 S3 主机删除组：

```shell
mc admin group rm ALIAS GROUPNAME
```

- 将 [`ALIAS`](#mc.admin.group.rm.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`GROUPNAME`](#mc.admin.group.rm.GROUPNAME) 替换为 组名。

### 禁用组 {#id9}

使用 [`mc admin group disable`](#mc.admin.group.disable) 禁用兼容 S3 主机上的组：

```shell
mc admin group disable ALIAS GROUPNAME
```

- 将 [`ALIAS`](#mc.admin.group.disable.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`GROUPNAME`](#mc.admin.group.disable.GROUPNAME) 替换为组名。

### 启用组 {#id10}

使用 [`mc admin group enable`](#mc.admin.group.enable) 启用兼容 S3 主机上的组：

```shell
mc admin group enable ALIAS GROUPNAME
```

- 将 [`ALIAS`](#mc.admin.group.enable.TARGET) 替换为兼容 S3 主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`GROUPNAME`](#mc.admin.group.enable.GROUPNAME) 替换为组名。

## 快速参考 {#id11}

**[`mc admin group add TARGET GROUPNAME MEMBERS`](#mc.admin.group.add)**

> 将用户添加到 MinIO 部署上的组。如果组不存在，则创建该组。

**[`mc admin group info TARGET GROUPNAME`](#mc.admin.group.info)**

> 返回 MinIO 部署上某个组的详细信息。

**[`mc admin group ls TARGET`](#mc.admin.group.ls)**

> 返回 MinIO 部署上所有组的列表。

**[`mc admin group rm TARGET GROUPNAME`](#mc.admin.group.rm)**

> 删除 MinIO 部署上的组。

**[`mc admin group enable TARGET GROUPNAME`](#mc.admin.group.enable)**

> 启用 MinIO 部署上的组。用户只能继承已启用组分配的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

**[`mc admin group disable TARGET GROUPNAME`](#mc.admin.group.disable)**

> 禁用 MinIO 部署上的组。用户不能继承已禁用组分配的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。

## 语法 {#id12}

#### `mc admin group add` {#mc.admin.group.add}

*mc-cmd*

将现有用户添加到组中。如果组不存在，该命令会创建组。 命令语法如下：

```shell
mc admin group add TARGET GROUPNAME MEMBERS
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.add.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令会在该部署上 向新建或现有组添加用户

#### `GROUPNAME` {#mc.admin.group.add.GROUPNAME}

*mc-cmd*

组名。如果组尚不存在，该命令会创建组。可使用 [`mc admin group ls`](#mc.admin.group.ls) 查看部署上的现有组。

组名不能包含 `=`（等号）或 `,`（逗号）字符。

#### `MEMBERS` {#mc.admin.group.add.MEMBERS}

*mc-cmd*

要添加到组中的用户名。

该用户 *必须* 存在于 [`TARGET`](#mc.admin.group.add.TARGET) MinIO 部署上。可使用 [`mc admin user ls`](/docs/reference/minio-mc-admin/mc-admin-user-list/#command-mc.admin.user.ls) 查看部署上的可用 用户。

#### `mc admin group info` {#mc.admin.group.info}

*mc-cmd*

返回目标部署上该组的详细信息，例如组内所有 [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 以及分配的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。命令语法如下：

```shell
mc admin group info TARGET GROUPNAME
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.info.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于从该部署中 获取组信息。

#### `GROUPNAME` {#mc.admin.group.info.GROUPNAME}

*mc-cmd*

组名。

#### `mc admin group ls, list` {#mc.admin.group.ls}

*mc-cmd*

列出目标 MinIO 部署上的所有组。命令语法如下：

```shell
mc admin group ls TARGET
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.ls.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于从该部署中 获取组列表。

#### `mc admin group rm, remove` {#mc.admin.group.rm}

*mc-cmd*

删除目标 MinIO 部署上的组。删除组 *不会* 删除该组中的任何成员用户。请使用 [`mc admin user rm`](/docs/reference/minio-mc-admin/mc-admin-user-remove/#command-mc.admin.user.rm) 从组中移除用户。

命令语法如下：

```shell
mc admin group rm TARGET GROUPNAME
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.rm.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令会在该部署上 删除组。

#### `GROUPNAME` {#mc.admin.group.rm.GROUPNAME}

*mc-cmd*

要删除的组名。

#### `mc admin group enable` {#mc.admin.group.enable}

*mc-cmd*

启用目标 MinIO 部署上的组。用户只能从已启用组继承 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。 组在创建时默认处于启用状态。命令语法如下：

```shell
mc admin group enable TARGET GROUPNAME
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.enable.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令会在该部署上 启用组。

#### `GROUPNAME` {#mc.admin.group.enable.GROUPNAME}

*mc-cmd*

要启用的组名。

#### `mc admin group disable` {#mc.admin.group.disable}

*mc-cmd*

禁用目标 MinIO 部署上的组。用户不能从已禁用组继承 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。命令语法如下：

```shell
mc admin group disable TARGET GROUPNAME
```

该命令接受以下参数：

#### `TARGET` {#mc.admin.group.disable.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令会在该部署上 禁用组。

#### `GROUPNAME` {#mc.admin.group.disable.GROUPNAME}

*mc-cmd*

要禁用的组名。