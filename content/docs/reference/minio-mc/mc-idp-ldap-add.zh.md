---
title: "mc idp ldap add"

weight: 10
---

<a id="mc-idp-ldap-add"></a>
<a id="minio-mc-idp-ldap-add"></a>

<a id="command-mc.idp.ldap.add"></a>

## 描述 {#id2}

[`mc idp ldap add`](#command-mc.idp.ldap.add) 命令用于创建 AD/LDAP IDP 服务器配置。

每个 MinIO 部署最多仅支持 *一个* (1) AD/LDAP 提供商。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例为 `myminio` 部署设置 AD/LDAP 配置项。

```shell
mc idp ldap add                                                            \
            myminio                                                        \
            server_addr=myldapserver:636                                   \
            lookup_bind_dn=cn=admin,dc=min,dc=io                           \
            lookup_bind_password=somesecret                                \
            user_dn_search_base_dn=dc=min,dc=io                            \
            user_dn_search_filter="(uid=%s)"                               \
            group_search_base_dn=ou=swengg,dc=min,dc=io                    \
            group_search_filter="(&(objectclass=groupofnames)(member=%d))"
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] idp ldap add               \
                          ALIAS             \
                          [CFG_PARAM1]      \
                          [CFG_PARAM2]...
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于创建 AD/LDAP 集成。
- 将 `[CFG_PARAM#]` 替换为各个 [configuration setting](/docs/reference/minio-server/settings/iam/ldap/#minio-ldap-config-settings) 键值对，格式为 `PARAMETER="value"`。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.add.ALIAS}

*mc-cmd*

*Required*

要添加 AD/LDAP 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap add myminio                               \
                server_addr=myldapserver:636          \
                lookup_bind_dn=cn=admin,dc=min,dc=io  \
                lookup_bind_password=somesecret       \
                user_dn_search_base_dn=dc=min,dc=io   \
                user_dn_search_filter="(uid=%s)"      \
```

##### `server_addr` {#mc.idp.ldap.add.server_addr}

*mc-cmd*

*Required*

指定 Active Directory / LDAP server 的主机名。例如：

```shell
ldapserver.com:636
```

> [!NOTE]
> **[`srv_record_name`](#mc.idp.ldap.add.srv_record_name) 会自动识别端口**
>
> 如果你的 AD/LDAP server 使用 [`DNS SRV Records`](#mc.idp.ldap.add.srv_record_name)，则 *不要* 在 [`server_addr`](#mc.idp.ldap.add.server_addr) 的值后追加端口号。 SRV 请求在返回可用服务器列表时会自动包含端口号。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_SERVER_ADDR`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SERVER_ADDR)。

##### `lookup_bind_dn` {#mc.idp.ldap.add.lookup_bind_dn}

*mc-cmd*

*Required*

指定 MinIO 在查询 AD/LDAP server 时所使用的 AD/LDAP 账户 Distinguished Name (DN)。 这会启用对 AD/LDAP server 的 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 认证。

该 DN 账户应为只读访问账号，并具备足够权限以支持执行用户和组查询。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN)。

##### `lookup_bind_password` {#mc.idp.ldap.add.lookup_bind_password}

*mc-cmd*

*Required*

指定 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 用户账户的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当通过 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回此值时，MinIO 会将其脱敏。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD)。

##### `user_dn_attributes` {#mc.idp.ldap.add.user_dn_attributes}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2024-06-06T09-36-42Z**

用户 DN 属性的逗号分隔列表。

一些有效值包括 `uid,cn,mail,sshPublicKey`。

如果要为 LDAP 用户启用公钥认证，请将 `sshPublicKey` 作为 DN 属性传入。 随后，用户即可使用传入的 SSH Public Key 登录 SFTP server。

```text
mc idp ldap update ALIAS user_dn_attributes=sshPublicKey
```

##### `user_dn_search_base_dn` {#mc.idp.ldap.add.user_dn_search_base_dn}

*mc-cmd*

*Required*

指定 MinIO 在查询与认证客户端所提供凭证相匹配的用户凭证时所使用的基础 Distinguished Name (DN)。

多个 DN 之间请使用分号（`;`）分隔。

例如：

```shell
cn=miniousers,dc=myldapserver,dc=net;ou=swengg,dc=min,dc=io
```

支持 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 模式。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN)。

##### `user_dn_search_filter` {#mc.idp.ldap.add.user_dn_search_filter}

*mc-cmd*

*Required*

指定 MinIO 在查询与认证客户端所提供凭证相匹配的用户凭证时所使用的 AD/LDAP 搜索过滤器。

使用 `%s` 替换字符将客户端指定的用户名插入搜索字符串。例如：

```shell
(userPrincipalName=%s)
```

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER)。

##### `comment` {#mc.idp.ldap.add.comment}

*mc-cmd*

*Optional*

指定要附加到 AD/LDAP 配置上的注释。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_COMMENT`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_COMMENT)。

##### `enabled` {#mc.idp.ldap.add.enabled}

*mc-cmd*

*Optional*

设为 `false` 可禁用 AD/LDAP 配置。

如果设为 `false`，应用程序将无法生成 STS 凭证， 也无法再使用已配置的提供者向 MinIO 进行身份验证。

默认为 `true`，即 “enabled”。

##### `group_search_base_dn` {#mc.idp.ldap.add.group_search_base_dn}

*mc-cmd*

*Optional*

指定 MinIO 在执行组查询时所使用的组搜索基础 [Distinguished Names](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names) 列表，多个值之间使用分号（`;`）分隔。

例如：

```shell
cn=miniogroups,dc=myldapserver,dc=net;ou=swengg,dc=min,dc=io
```

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_GROUP_SEARCH_BASE_DN`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_GROUP_SEARCH_BASE_DN)。

##### `group_search_filter` {#mc.idp.ldap.add.group_search_filter}

*mc-cmd*

*Optional*

指定用于为已认证用户执行组查询的 AD/LDAP 搜索过滤器。

使用 `%s` 替换字符将客户端指定的用户名插入搜索字符串。 使用 `%d` 替换字符将客户端指定用户名对应的 Distinguished Name 插入搜索字符串。

例如：

```shell
(&(objectclass=groupOfNames)(memberUid=%s))
```

在提供 AD/LDAP 组搜索过滤器时，应将其配置为仅返回支持认证所需的最少相关组。 返回大量组成员关系的过滤器会增加相关调用和资源的体量。 对大请求体或大响应体敏感的功能可能因此出现意外行为。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_GROUP_SEARCH_FILTER`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_GROUP_SEARCH_FILTER)。

##### `server_insecure` {#mc.idp.ldap.add.server_insecure}

*mc-cmd*

*Optional*

指定 `on` 可允许与 AD/LDAP server 建立未加密的连接（非 TLS）。

MinIO 会以明文形式将 AD/LDAP 用户凭证发送到 AD/LDAP server，因此 *必须* 启用 TLS，才能防止凭证在传输过程中被读取。 启用此选项会带来安全风险，因为任何能够访问网络流量的用户都可能看到未加密的明文 凭证。

默认值为 `off`。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_SERVER_INSECURE`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SERVER_INSECURE)。

##### `server_starttls` {#mc.idp.ldap.add.server_starttls}

*mc-cmd*

*Optional*

指定 `on` 可启用到 AD/LDAP server 的 `StartTLS` 连接。

默认值为 `off`

有关 `StartTLS` 的更多信息，请参见 [LDAP RFC 4511 specification](https://docs.ldap.com/specs/rfc4511.txt) 第 4.14 节。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_SERVER_STARTTLS`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SERVER_STARTTLS)。

##### `srv_record_name` {#mc.idp.ldap.add.srv_record_name}

*mc-cmd*

*Optional*

> [!NOTE]
> **新增: RELEASE.2022-12-12T19-27-27Z**

指定适当的值，以允许 MinIO 通过 [DNS SRV record](https://ldap.com/dns-srv-records-for-ldap) 请求选择 AD/LDAP server。

启用后，MinIO 会通过以下方式选择 AD/LDAP server：

- 按标准命名约定构造目标 SRV 记录名称。
- 请求可用的 AD/LDAP server 列表。
- 根据优先级和权重选择合适的目标。

下面的配置示例假定 AD/LDAP server 地址设为 `example.com`，SRV 记录协议为 `_tcp`。

对于以 `_ldap` 开头的 SRV 记录名称，指定 `ldap`。 构造出的 DNS SRV 记录名称类似如下：

```shell
_ldap._tcp.example.com
```

对于以 `_ldaps` 开头的 SRV 记录名称，指定 `ldaps`。 构造出的 DNS SRV 记录名称类似如下：

```shell
_ldaps._tcp.example.com
```

如果你的 DNS SRV 记录名称使用了其他 service 或 protocol 名称，请指定 `on`， 并将完整记录名称作为 LDAP server 地址提供。 例如：`_ldapserver._specialtcp.example.com`

有关 DNS SRV 记录的更多信息，请参见 [DNS SRV Records for LDAP](https://ldap.com/dns-srv-records-for-ldap)。

> [!NOTE]
> **DNS SRV 记录配置中的 server 地址**
>
> 指定的 server 名称 **不得** 包含端口号。 这与标准 AD/LDAP 配置不同，后者要求提供端口号。
>
> 关于如何配置 AD/LDAP server 地址，请参见 [`server_addr`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.server_addr) 或 [`MINIO_IDENTITY_LDAP_SERVER_ADDR`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SERVER_ADDR)。

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_SRV_RECORD_NAME`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SRV_RECORD_NAME)。

##### `tls_skip_verify` {#mc.idp.ldap.add.tls_skip_verify}

*mc-cmd*

*Optional*

指定 `on` 可在不验证的情况下信任 AD/LDAP server 的 TLS 证书。 如果 AD/LDAP server 的 TLS 证书由不受信任的证书颁发机构签名 （例如自签名），则可能需要此选项。

默认值为 `off`

该参数对应环境变量 [`MINIO_IDENTITY_LDAP_TLS_SKIP_VERIFY`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_TLS_SKIP_VERIFY)。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。