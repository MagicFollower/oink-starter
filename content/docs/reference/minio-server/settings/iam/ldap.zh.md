---
title: "Active Directory / LDAP 设置"

weight: 10
---

<a id="active-directory-ldap"></a>
<a id="minio-ldap-config-settings"></a>
<a id="minio-server-envvar-external-identity-management-ad-ldap"></a>

本页面说明通过 Active Directory 或 LDAP 服务启用外部身份管理所需的设置。 有关使用这些设置的教程，请参见 [配置 MinIO 使用 Active Directory / LDAP 进行认证](/docs/operations/external-iam/configure-ad-ldap-external-identity-management/#minio-authenticate-using-ad-ldap-generic)。

> [!WARNING]
> **重要**
>
> 在 `RELEASE.2023-05-26T23-31-54Z` 版本中新增：
>
> 相比使用配置设置，优先使用 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 命令将 MinIO 配置为使用 Active Directory 或 LDAP 进行身份管理。
>
> MinIO 建议使用 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 命令执行 LDAP 管理操作。 这些命令提供了更好的校验能力和附加功能，同时提供与 `identity_ldap` 配置键相同的设置。 有关 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 的使用教程，请参见 [配置 MinIO 使用 Active Directory / LDAP 进行认证](/docs/operations/external-iam/configure-ad-ldap-external-identity-management/#minio-authenticate-using-ad-ldap-generic)。

`identity_ldap` 配置设置仍可用于现有脚本和其他工具。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## 示例 {#id2}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
```shell
MINIO_IDENTITY_LDAP_SERVER_ADDR="ldapserver.com:636"
```

> [!NOTE]
> **说明**
>
> `srv_record_name` 会自动识别端口。
>
> 如果你的 AD/LDAP 服务器使用 `DNS SRV Records`，请 *不要* 在 `server_addr` 值后附加端口号。 SRV 请求在返回可用服务器列表时会自动包含端口号。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
#### `identity_ldap` {#mc-conf.identity_ldap}

*mc-conf*

使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 LDAP 时，以下设置为必需项：

- `enabled`
- `server_addr`
- `lookup_bind_dn`
- `lookup_bind_dn_password`
- `user_dn_search_base_dn`
- `user_dn_search_filter`

```shell
mc admin config set identity_ldap                        \
   enabled="true"                                        \
   server_addr="ad-ldap.example.net/"                    \
   lookup_bind_dn="cn=miniolookupuser,dc=example,dc=net" \
   lookup_bind_dn_password="userpassword"                \
   user_dn_search_base_dn="dc=example,dc=net"            \
   user_dn_search_filter="(&(objectCategory=user)(sAMAccountName=%s))"
```
{{< /tab >}}
{{< /tabs >}}

## 设置 {#id3}

### 服务器地址 {#id4}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_SERVER_ADDR` {#envvar.MINIO_IDENTITY_LDAP_SERVER_ADDR}

*envvar*

指定 Active Directory / LDAP server 的主机名。例如：

```shell
ldapserver.com:636
```

> [!NOTE]
> **[`srv_record_name`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.srv_record_name) 会自动识别端口**
>
> 如果你的 AD/LDAP server 使用 [`DNS SRV Records`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.srv_record_name)，则 *不要* 在 [`server_addr`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.server_addr) 的值后追加端口号。 SRV 请求在返回可用服务器列表时会自动包含端口号。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap server_addr` {#mc-conf.identity_ldap.server_addr}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 Active Directory / LDAP server 的主机名。例如：

```shell
ldapserver.com:636
```

> [!NOTE]
> **[`srv_record_name`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.srv_record_name) 会自动识别端口**
>
> 如果你的 AD/LDAP server 使用 [`DNS SRV Records`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.srv_record_name)，则 *不要* 在 [`server_addr`](/docs/reference/minio-mc/mc-idp-ldap-add/#mc.idp.ldap.add.server_addr) 的值后追加端口号。 SRV 请求在返回可用服务器列表时会自动包含端口号。

### Lookup Bind DN {#lookup-bind-dn}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN` {#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap lookup_bind_dn` {#mc-conf.identity_ldap.lookup_bind_dn}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在查询 AD/LDAP server 时所使用的 AD/LDAP 账户 Distinguished Name (DN)。 这会启用对 AD/LDAP server 的 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 认证。

该 DN 账户应为只读访问账号，并具备足够权限以支持执行用户和组查询。

### Lookup Bind 密码 {#lookup-bind}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD` {#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap lookup_bind_password` {#mc-conf.identity_ldap.lookup_bind_password}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 用户账户的密码。

> [!NOTE]
> **变更: RELEASE.2023-06-23T20-26-00Z**
>
> 当通过 [`mc admin config get`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.get) 返回此值时，MinIO 会将其脱敏。

### 用户 DN 搜索基准 DN {#dn-dn}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN` {#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap user_dn_search_base_dn` {#mc-conf.identity_ldap.user_dn_search_base_dn}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在查询与认证客户端所提供凭证相匹配的用户凭证时所使用的基础 Distinguished Name (DN)。

多个 DN 之间请使用分号（`;`）分隔。

例如：

```shell
cn=miniousers,dc=myldapserver,dc=net;ou=swengg,dc=min,dc=io
```

支持 [Lookup-Bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 模式。

### 用户 DN 搜索过滤器 {#dn}

*必需*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER` {#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap user_dn_search_filter` {#mc-conf.identity_ldap.user_dn_search_filter}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在查询与认证客户端所提供凭证相匹配的用户凭证时所使用的 AD/LDAP 搜索过滤器。

使用 `%s` 替换字符将客户端指定的用户名插入搜索字符串。例如：

```shell
(userPrincipalName=%s)
```

### 用户 DN 属性 {#id5}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_USER_DN_ATTRIBUTES` {#envvar.MINIO_IDENTITY_LDAP_USER_DN_ATTRIBUTES}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap user_dn_attributes` {#mc-conf.identity_ldap.user_dn_attributes}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

> [!NOTE]
> **新增: RELEASE.2024-06-06T09-36-42Z**

用户 DN 属性的逗号分隔列表。

一些有效值包括 `uid,cn,mail,sshPublicKey`。

如果要为 LDAP 用户启用公钥认证，请将 `sshPublicKey` 作为 DN 属性传入。 随后，用户即可使用传入的 SSH Public Key 登录 SFTP server。

```text
mc idp ldap update ALIAS user_dn_attributes=sshPublicKey
```

### 启用 {#id6}

*可选*

{{< tabs group="tab1-tab2" default="tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
此设置没有环境变量选项。 请改用配置设置。
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap enabled` {#mc-conf.identity_ldap.enabled}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

将其设置为 `false` 可禁用 AD/LDAP 配置。

若为 `false`，应用程序将无法生成 STS 凭证，也无法通过已配置的提供者向 MinIO 进行身份验证。

默认为 `true`（即 “enabled”）。

### 组搜索过滤器 {#id9}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_GROUP_SEARCH_FILTER` {#envvar.MINIO_IDENTITY_LDAP_GROUP_SEARCH_FILTER}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap group_search_filter` {#mc-conf.identity_ldap.group_search_filter}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定用于为已认证用户执行组查询的 AD/LDAP 搜索过滤器。

使用 `%s` 替换字符将客户端指定的用户名插入搜索字符串。 使用 `%d` 替换字符将客户端指定用户名对应的 Distinguished Name 插入搜索字符串。

例如：

```shell
(&(objectclass=groupOfNames)(memberUid=%s))
```

在提供 AD/LDAP 组搜索过滤器时，应将其配置为仅返回支持认证所需的最少相关组。 返回大量组成员关系的过滤器会增加相关调用和资源的体量。 对大请求体或大响应体敏感的功能可能因此出现意外行为。

在提供 AD/LDAP 组搜索过滤器时，应配置一个仅返回满足身份验证需求的最小相关组集合的过滤器。 返回大量组分配信息的过滤器会增加相关调用和资源消耗。 对大体积请求或响应体敏感的功能可能因此出现非预期行为。

### 组搜索基准 DN {#id10}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_GROUP_SEARCH_BASE_DN` {#envvar.MINIO_IDENTITY_LDAP_GROUP_SEARCH_BASE_DN}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap group_search_base_dn` {#mc-conf.identity_ldap.group_search_base_dn}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 MinIO 在执行组查询时所使用的组搜索基础 [Distinguished Names](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names) 列表，多个值之间使用分号（`;`）分隔。

例如：

```shell
cn=miniogroups,dc=myldapserver,dc=net;ou=swengg,dc=min,dc=io
```

### TLS 跳过校验 {#tls}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_TLS_SKIP_VERIFY` {#envvar.MINIO_IDENTITY_LDAP_TLS_SKIP_VERIFY}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap tls_skip_verify` {#mc-conf.identity_ldap.tls_skip_verify}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 可在不验证的情况下信任 AD/LDAP server 的 TLS 证书。 如果 AD/LDAP server 的 TLS 证书由不受信任的证书颁发机构签名 （例如自签名），则可能需要此选项。

默认值为 `off`

### 服务器不安全模式 {#id11}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_SERVER_INSECURE` {#envvar.MINIO_IDENTITY_LDAP_SERVER_INSECURE}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap server_insecure` {#mc-conf.identity_ldap.server_insecure}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 可允许与 AD/LDAP server 建立未加密的连接（非 TLS）。

MinIO 会以明文形式将 AD/LDAP 用户凭证发送到 AD/LDAP server，因此 *必须* 启用 TLS，才能防止凭证在传输过程中被读取。 启用此选项会带来安全风险，因为任何能够访问网络流量的用户都可能看到未加密的明文 凭证。

默认值为 `off`。

### 服务器 Start TLS {#start-tls}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_SERVER_STARTTLS` {#envvar.MINIO_IDENTITY_LDAP_SERVER_STARTTLS}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap server_starttls` {#mc-conf.identity_ldap.server_starttls}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定 `on` 可启用到 AD/LDAP server 的 `StartTLS` 连接。

默认值为 `off`

有关 `StartTLS` 的更多信息，请参见 [LDAP RFC 4511 specification](https://docs.ldap.com/specs/rfc4511.txt) 第 4.14 节。

### SRV 记录名称 {#srv}

*可选*

> [!NOTE]
> **新增: RELEASE.2022-12-12T19-27-27Z**

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_SRV_RECORD_NAME` {#envvar.MINIO_IDENTITY_LDAP_SRV_RECORD_NAME}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap srv_record_name` {#mc-conf.identity_ldap.srv_record_name}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

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
> 关于如何配置 AD/LDAP server 地址，请参见 [`server_addr`](#mc-conf.identity_ldap.server_addr) 或 [`MINIO_IDENTITY_LDAP_SERVER_ADDR`](#envvar.MINIO_IDENTITY_LDAP_SERVER_ADDR)。

### 备注 {#id12}

*可选*

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_IDENTITY_LDAP_COMMENT` {#envvar.MINIO_IDENTITY_LDAP_COMMENT}

*envvar*
{{< /tab >}}
{{< tab label="配置设置" value="tab2" >}}
##### `identity_ldap identity_ldap comment` {#mc-conf.identity_ldap.identity_ldap.comment}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

指定要附加到 AD/LDAP 配置上的注释。