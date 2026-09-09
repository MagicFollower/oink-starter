---
title: "mc admin idp openid"

weight: 160
---

<a id="mc-admin-idp-openid"></a>
<a id="minio-mc-admin-idp-openid"></a>

<a id="command-mc.admin.idp.openid"></a>

> [!NOTE]
> **变更: RELEASE.2023-05-26T23-31-54Z**
>
> `mc admin idp openid` 及其子命令已由 [`mc idp openid`](/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid) 替代。

## 描述 {#id1}

[`mc admin idp openid`](#command-mc.admin.idp.openid) 命令允许你为第三方 [OpenID 身份与访问管理（IAM）集成](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 添加、修改、查看、列出、移除、启用和禁用服务器配置。

在 [设置 OpenID 连接](/docs/operations/external-iam/configure-openid-external-identity-management/#minio-external-identity-management-openid-configure) 时，可通过定义配置设置来替代使用环境变量。

[`mc admin idp openid`](#command-mc.admin.idp.openid) 命令包含以下子命令：

| 子命令 | 描述 |
| --- | --- |
| [`mc admin idp openid add`](#mc.admin.idp.openid.add) | 创建 OpenID IDP 服务器配置。 |
| [`mc admin idp openid update`](#mc.admin.idp.openid.update) | 修改现有的 OpenID IDP 服务器配置。 |
| [`mc admin idp openid rm`](#mc.admin.idp.openid.rm) | 从部署中移除 OpenID IDP 服务器配置。 |
| [`mc admin idp openid ls`](#mc.admin.idp.openid.ls) | 输出部署中现有 OpenID 服务器配置列表。 |
| [`mc admin idp openid info`](#mc.admin.idp.openid.info) | 显示特定 OpenID 服务器配置的详细信息。 |
| [`mc admin idp openid enable`](#mc.admin.idp.openid.enable) | 启用 OpenID 服务器配置。 |
| [`mc admin idp openid disable`](#mc.admin.idp.openid.disable) | 禁用 OpenID 服务器配置。 |

## 配置参数 {#id2}

[`mc admin idp openid`](#command-mc.admin.idp.openid) 子命令支持配置参数。 这些参数定义了服务器与 IAM 提供方的交互方式。

有关配置参数的更详细说明，请参阅 [配置设置文档](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings)。

## 语法 {#id3}

#### `add` {#mc.admin.idp.openid.add}

*mc-cmd*

为 OpenID 提供方创建一组新的配置。

你可以多次运行该命令来设置多个 OpenID 提供方。

添加多个 OpenID 提供方时，只能有一个是基于 JWT Claim 的提供方。 其余都必须是基于角色的提供方。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例为 `myminio` 部署创建配置设置，在新的 `test-config` 配置中定义 Dex 集成。

```shell
 mc admin idp openid add myminio test-config                                  \
    client_id=minio-client-app                                                \
    client_secret=minio-client-app-secret                                     \
    config_url="http://localhost:5556/dex/.well-known/openid-configuration"   \
    scopes="openid,groups"                                                    \
    redirect_uri="http://127.0.0.1:10000/oauth_callback"                      \
    role_policy="consoleAdmin"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid add        \
                           ALIAS             \
                           [CFG_NAME]        \
                           [CFG_PARAM1]      \
                           [CFG_PARAM2]...
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，命令会创建默认配置值。
- 将 `[CFG_PARAM#]` 替换为各个 [配置设置](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings) 键值对，格式为 `PARAMETER="value"`。
{{< /tab >}}
{{< /tabs >}}

#### `update` {#mc.admin.idp.openid.update}

*mc-cmd*

修改 OpenID 提供方的现有配置集合。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例修改了 `myminio` 部署中 `test-config`（用于 Dex 集成）的两个配置项。

```shell
mc admin idp openid update                      \
                    myminio                     \
                    test_config                 \
                    scopes="openid,groups"      \
                    role_policy="consoleAdmin"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid update           \
                                  ALIAS            \
                                  [CFG_NAME]       \
                                  [CFG_PARAM1]     \
                                  [CFG_PARAM2]...
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，命令会更新默认配置。
- 将 `[CFG_PARAM#]` 替换为要更新的各个 [配置设置](/docs/reference/minio-server/settings/iam/openid/#minio-open-id-config-settings) 键值对，格式为 `PARAMETER="value"`。
{{< /tab >}}
{{< /tabs >}}

#### `rm, remove` {#mc.admin.idp.openid.rm}

*mc-cmd*

删除 OpenID 提供方的现有配置集合。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例删除 `myminio` 部署中的 `test-config` 配置。

```shell
mc admin idp openid rm myminio test_config
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid rm     \
                                  ALIAS      \
                                  [CFG_NAME]
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，命令会删除默认配置。
{{< /tab >}}
{{< /tabs >}}

#### `ls, list` {#mc.admin.idp.openid.ls}

*mc-cmd*

输出 OpenID 提供方现有配置集合列表。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例输出 `myminio` 部署定义的所有 OpenID 配置集合列表。

```shell
mc admin idp openid ls myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid ls ALIAS
```

- 将 `ALIAS` 替换为要列出 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
{{< /tab >}}
{{< /tabs >}}

#### `info` {#mc.admin.idp.openid.info}

*mc-cmd*

输出 OpenID 提供方现有服务器配置集合中定义的参数值。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例输出 `myminio` 部署中 `test_config` 这组 OpenID 设置所定义的配置项。

```shell
mc admin idp openid info myminio test_config
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid info     \
                                  ALIAS      \
                                  [CFG_NAME]
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，则显示默认服务器配置的信息。
{{< /tab >}}
{{< /tabs >}}

#### `enable` {#mc.admin.idp.openid.enable}

*mc-cmd*

开始使用 OpenID 提供方的现有配置集合。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例启用 `myminio` 部署上定义为 `test_config` 的服务器配置。

```shell
mc admin idp openid enable       \
                    myminio      \
                    test_config
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid enable     \
                                  ALIAS      \
                                  [CFG_NAME]
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，命令会启用默认配置值。
{{< /tab >}}
{{< /tabs >}}

#### `disable` {#mc.admin.idp.openid.disable}

*mc-cmd*

停止使用 OpenID 提供方的一组配置。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例禁用 `myminio` 部署上定义为 `test_config` 的服务器配置。

```shell
mc admin idp openid disable      \
                    myminio      \
                    test_config
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin idp openid disable       \
                                  ALIAS         \
                                  [CFG_NAME]
```

- 将 `ALIAS` 替换为用于配置 OpenID 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `CFG_NAME` 替换为该配置的唯一字符串。 如果未指定，命令会禁用默认配置值。
{{< /tab >}}
{{< /tabs >}}

## 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。