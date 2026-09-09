---
title: "配置 Silo 使用 Active Directory / LDAP 进行认证"

weight: 10
---

<a id="minio-active-directory-ldap"></a>
<a id="minio-authenticate-using-ad-ldap-generic"></a>

## 概览 {#id2}

MinIO 支持配置单个 Active Directory / LDAP 连接，用于对用户身份进行外部管理。

本页流程提供以下内容的操作说明：

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
对于使用 [MinIO Kubernetes Operator](/docs/operations/deployments/kubernetes/#minio-kubernetes) 部署的 MinIO Tenant，本流程包括：

- 配置 MinIO Tenant 使用外部 AD/LDAP 提供方
- 使用 AD/LDAP 凭证访问 Tenant Console
- 使用 MinIO `AssumeRoleWithLDAPIdentity` Security Token Service (STS) API 生成供应用程序使用的临时凭证
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
对于部署在裸金属基础设施上的 MinIO，本流程包括：

- 为 MinIO 集群配置外部 AD/LDAP 提供方
- 使用 AD/LDAP 凭证访问 MinIO Console
- 使用 MinIO `AssumeRoleWithLDAPIdentity` Security Token Service (STS) API 生成供应用程序使用的临时凭证
{{< /tab >}}
{{< /tabs >}}

本流程是面向 AD/LDAP 服务的通用配置流程。 有关用户身份配置的具体步骤，请参阅你所选 AD/LDAP 提供方的文档。

## 前提条件 {#id3}

### 访问 MinIO 集群 {#minio}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
你必须能够访问 MinIO Operator Console Web UI。 你可以使用自己偏好的 Kubernetes 路由组件暴露 MinIO Operator Console service，也可以通过临时端口转发，在本地机器上暴露 Console service 端口。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
本流程使用 [`mc`](/docs/reference/minio-mc/#command-mc) 对 MinIO 集群执行操作。 请在一台能够访问该集群网络的机器上安装 `mc`。 关于如何下载和安装 `mc`，请参见 `mc` [安装快速开始](/docs/reference/minio-mc/#mc-install)。

本流程假定已为 MinIO 集群配置 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
{{< /tab >}}
{{< /tabs >}}

### 兼容 Active Directory / LDAP 的身份提供方 {#active-directory-ldap}

本流程假定你已经拥有一个现成的 Active Directory 或 LDAP 服务。 AD/LDAP 本身的配置不在本流程范围内。

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
- 如果 AD/LDAP 部署与 MinIO Tenant 位于同一 Kubernetes 集群内，你可以使用 Kubernetes service 名称，让 MinIO Tenant 能够连接到 AD/LDAP 服务。
- 如果 AD/LDAP 部署位于 Kubernetes 集群外部，则必须确保该集群支持 Kubernetes services、pods 与外部网络之间的通信路由。 这可能需要配置或部署额外的 Kubernetes 网络组件，和/或启用访问公网的能力。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
MinIO 部署必须与目标 AD / LDAP 服务保持双向网络连通。
{{< /tab >}}
{{< /tabs >}}

MinIO 需要一组只读访问凭证，以便通过 [bind](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-lookup-bind) 执行认证用户和组查询。 请确保每个打算与 MinIO 配合使用的 AD/LDAP 用户和组，都在 MinIO 部署上拥有对应的 [策略](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-access-control)。 如果某个 AD/LDAP 用户没有分配任何策略，*并且* 所属组也都没有分配任何策略，那么该用户无权访问 MinIO 集群中的任何操作或资源。

<a id="id4"></a>

## 为 MinIO 配置 Active Directory 或 LDAP 外部身份管理 {#minio-external-identity-management-ad-ldap-configure}

1. 设置 Active Directory / LDAP 配置项

   你可以使用以下任一方式配置 AD/LDAP 提供方：

   - MinIO Client
   - 环境变量

   所有方式都需要启动或重启 MinIO 部署后才能生效。

   以下选项卡给出了可用配置方式的速查：

   {{< tabs group="minio-client-tab2" >}}
   {{< tab label="MinIO Client" value="minio-client" >}}
   MinIO 支持使用 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 命令配置 AD/LDAP 提供方设置。

   对于分布式部署，[`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 命令会将配置应用到部署中的所有节点。

   以下示例代码设置了外部身份管理所需的全部 AD/LDAP 相关配置项。 至少需要以下设置：

   - [`server_addr`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.server_addr)
   - [`lookup_bind_dn`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.lookup_bind_dn)
   - [`lookup_bind_password`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.lookup_bind_password)
   - [`user_dn_search_base_dn`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.user_dn_search_base_dn)
   - [`user_dn_search_filter`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap.user_dn_search_filter)

   ```shell
   mc idp ldap add ALIAS                                                  \
     server_addr="ldaps.example.net:636"                                  \
     lookup_bind_dn="CN=xxxxx,OU=xxxxx,OU=xxxxx,DC=example,DC=net"        \
     lookup_bind_password="xxxxxxxx"                                      \
     user_dn_search_base_dn="DC=example,DC=net"                           \
     user_dn_search_filter="(&(objectCategory=user)(sAMAccountName=%s))"  \
     group_search_filter= "(&(objectClass=group)(member=%d))"             \
     group_search_base_dn="ou=MinIO Users,dc=example,dc=net"              \
     tls_skip_verify="off"                                                \
     server_insecure=off                                                  \
     server_starttls="off"                                                \
     srv_record_name=""                                                   \
     comment="Test LDAP server"
   ```

   对于 Kubernetes 部署，请确保 *ALIAS* 对应 MinIO Tenant 的外部可访问主机名。

   这些设置的完整文档请参阅 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)。

   > [!NOTE]
   > **建议使用 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap)**
   >
   > 相比 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 运行时配置， [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 提供了更多功能和更完善的校验能力。 [`mc idp ldap`](/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap) 支持与 [`mc admin config`](/docs/reference/minio-mc-admin/mc-admin-config/#command-mc.admin.config) 以及 [`identity_ldap`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap) 配置键相同的设置项。
   >
   > [`identity_ldap`](/docs/reference/minio-server/settings/iam/ldap/#mc-conf.identity_ldap) 配置键仍可用于现有脚本和工具。
   {{< /tab >}}
   {{< tab label="环境变量" value="tab2" >}}
   MinIO 支持使用 [环境变量](/docs/reference/minio-server/settings/iam/ldap/#minio-server-envvar-external-identity-management-ad-ldap) 指定 AD/LDAP 提供方设置。[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会在下一次启动时应用这些设置。 对于分布式部署，请在部署中的所有节点上使用 *相同* 的值设置这些变量。 节点之间的配置不一致会导致启动或配置失败。

   以下示例代码设置了外部身份管理所需的全部 AD/LDAP 相关环境变量。 至少需要以下变量：

   - [`MINIO_IDENTITY_LDAP_SERVER_ADDR`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_SERVER_ADDR)
   - [`MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN)
   - [`MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD)
   - [`MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN)
   - [`MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER`](/docs/reference/minio-server/settings/iam/ldap/#envvar.MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER)

   ```shell
   export MINIO_IDENTITY_LDAP_SERVER_ADDR="ldaps.example.net:636"
   export MINIO_IDENTITY_LDAP_LOOKUP_BIND_DN="CN=xxxxx,OU=xxxxx,OU=xxxxx,DC=example,DC=net"
   export MINIO_IDENTITY_LDAP_USER_DN_SEARCH_BASE_DN="dc=example,dc=net"
   export MINIO_IDENTITY_LDAP_USER_DN_SEARCH_FILTER="(&(objectCategory=user)(sAMAccountName=%s))"
   export MINIO_IDENTITY_LDAP_LOOKUP_BIND_PASSWORD="xxxxxxxxx"
   export MINIO_IDENTITY_LDAP_GROUP_SEARCH_FILTER="(&(objectClass=group)(member=%d))"
   export MINIO_IDENTITY_LDAP_GROUP_SEARCH_BASE_DN="ou=MinIO Users,dc=example,dc=net"
   export MINIO_IDENTITY_LDAP_TLS_SKIP_VERIFY="off"
   export MINIO_IDENTITY_LDAP_SERVER_INSECURE="off"
   export MINIO_IDENTITY_LDAP_SERVER_STARTTLS="off"
   export MINIO_IDENTITY_LDAP_SRV_RECORD_NAME=""
   export MINIO_IDENTITY_LDAP_COMMENT="LDAP test server"
   ```

   这些变量的完整文档请参阅 [Active Directory / LDAP 设置](/docs/reference/minio-server/settings/iam/ldap/#minio-server-envvar-external-identity-management-ad-ldap)。
   {{< /tab >}}
   {{< /tabs >}}
2. 重启 MinIO 部署

   你必须重启 MinIO 部署，才能应用这些配置更改。

   如果你是在 MinIO Console 中配置 AD/LDAP，则无需额外操作。 MinIO Console 会在保存新的 AD/LDAP 配置后自动重启部署。

   对于 MinIO Client 和环境变量方式，请使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 命令重启部署：

   ```shell
   mc admin service restart ALIAS
   ```

   将 `ALIAS` 替换为要重启部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
3. 使用 AD/LDAP 凭证登录 MinIO Console

   MinIO Console 支持完整工作流，包括向 AD/LDAP 提供方认证、 使用 MinIO [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) Security Token Service (STS) 端点生成临时凭证， 以及将用户登录到 MinIO 部署。

   你可以通过访问 MinIO 集群的根 URL 打开 Console， 例如 `https://minio.example.net:9000`。

   登录后，你可以执行该认证用户 [被授权](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-access-control) 的任何操作。

   你还可以为必须在 MinIO 上执行操作的支持型应用程序创建 [access key](/docs/administration/identity-access-management/minio-user-management/#minio-idp-service-account)。 Access Key 是长期有效的凭证，会继承父用户的权限。 父用户还可以在创建服务账户时进一步限制这些权限。
4. 使用 AD/LDAP 凭证生成 S3 兼容临时凭证

   MinIO 要求客户端使用 [AWS Signature Version 4 协议](https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html) 进行认证，同时兼容已弃用的 Signature Version 2 协议。 具体来说，客户端必须提供有效的 access key 和 secret key， 才能访问任意 S3 或 MinIO 管理 API，例如 `PUT`、`GET` 和 `DELETE`。

   应用程序可以按需使用 [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity) Security Token Service (STS) API 端点 和 AD/LDAP 用户凭证生成临时访问凭证。 MinIO 提供了示例 Go 应用程序 [ldap.go](https://github.com/minio/minio/blob/master/docs/sts/ldap.go)， 用于演示该工作流。

   ```shell
   POST https://minio.example.net?Action=AssumeRoleWithLDAPIdentity
   &LDAPUsername=USERNAME
   &LDAPPassword=PASSWORD
   &Version=2011-06-15
   &Policy={}
   ```

   - 将 `LDAPUsername` 替换为 AD/LDAP 用户名。
   - 将 `LDAPPassword` 替换为 AD/LDAP 用户密码。
   - 将 `Policy` 替换为内联、经过 URL 编码的 JSON [policy](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)， 以进一步限制这些临时凭证关联的权限。

     如果省略，则会使用名称与 AD/LDAP 用户 Distinguished Name (DN) [匹配的 policy](/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-access-control)。

   API 响应为 XML 文档，其中包含 access key、secret key、session token 和过期时间。 应用程序可使用 access key 和 secret key 访问 MinIO 并执行操作。

   参考文档请参阅 [AssumeRoleWithLDAPIdentity](/docs/developers/security-token-service/AssumeRoleWithLDAPIdentity/#minio-sts-assumerolewithldapidentity)。

## 禁用已配置的 Active Directory / LDAP 连接 {#id5}

> [!NOTE]
> **新增: RELEASE.2023-03-20T20-16-18Z**

你可以按需启用或禁用已配置的 AD/LDAP 连接。

使用 [`mc idp ldap disable`](/docs/reference/minio-mc/mc-idp-ldap-disable/#command-mc.idp.ldap.disable) 停用已配置连接。 使用 [`mc idp ldap enable`](/docs/reference/minio-mc/mc-idp-ldap-enable/#command-mc.idp.ldap.enable) 激活此前已配置的连接。