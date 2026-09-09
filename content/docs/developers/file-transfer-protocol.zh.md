---
title: "文件传输协议 (FTP/SFTP)"

weight: 220
icon: fa-solid fa-file-arrow-up
---

<a id="ftp-sftp"></a>
<a id="minio-ftp"></a>

- [使用 FTP 和 SFTP 与 MinIO 进行文件传输](https://www.youtube.com/watch?v=lNZyL8wD-lI)

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
从 MinIO Operator 5.0.7 和 [MinIO Server RELEASE.2023-04-20T17-56-55Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-04-20T17-56-55Z) 起，你可以使用 SSH 文件传输协议 (SFTP) 与 MinIO Operator 租户部署中的对象交互。

互联网工程任务组 (IETF) 将 SFTP 定义为 SSH 2.0 的扩展。 它允许通过 SSH 进行文件传输，可用于 [传输层安全 (TLS)](/docs/operations/network-encryption/#minio-tls) 和虚拟专用网络 (VPN) 场景。

启用 SFTP 不会影响其他 MinIO 功能。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
从 [MinIO Server RELEASE.2023-04-20T17-56-55Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-04-20T17-56-55Z) 起，你可以使用文件传输协议 (FTP) 与 MinIO 部署中的对象交互。

启动服务器时，你必须显式启用 FTP 或 SFTP。 启用任一服务器类型都不会影响其他 MinIO 功能。

本页下文统一使用缩写 FTP，但你可以使用下文描述的任意受支持 FTP 协议。
{{< /tab >}}
{{< /tabs >}}

## 支持的协议 {#id2}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
MinIO Operator 仅支持配置 SSH 文件传输协议 (SFTP)。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
启用后，MinIO 支持通过以下协议进行 FTP 访问：

- SSH 文件传输协议 (SFTP)

  互联网工程任务组 (IETF) 将 SFTP 定义为 SSH 2.0 的扩展。 SFTP 允许通过 SSH 进行文件传输，可用于 [传输层安全 (TLS)](/docs/operations/network-encryption/#minio-tls) 和虚拟专用网络 (VPN) 场景。

  你的 FTP 客户端必须支持 SFTP。
- 通过 SSL/TLS 的文件传输协议 (FTPS)

  FTPS 允许在标准 FTP 通信通道上使用 TLS 证书进行加密传输。 不应将 FTPS 与 SFTP 混淆，因为 FTPS 并不通过 Secure Shell (SSH) 通信。

  你的 FTP 客户端必须支持 FTPS。
- 文件传输协议 (FTP)

  不加密的文件传输。

  MinIO **不** 建议使用未加密的 FTP 进行文件传输。
{{< /tab >}}
{{< /tabs >}}

## 支持的命令 {#id5}

启用后，MinIO 支持以下 SFTP 操作：

- `get`
- `put`
- `ls`
- `mkdir`
- `rmdir`
- `delete`

MinIO 不支持 `append` 或 `rename` 操作。

## 注意事项 {#id6}

### 版本控制 {#id7}

SFTP 客户端只能操作对象的 [当前版本](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 具体来说：

- 对于读取操作，MinIO 只会向 SFTP 客户端返回所请求对象的最新版本。
- 对于写入操作，MinIO 会应用正常的版本控制行为，并在指定命名空间中创建新的对象版本。 `rm` 和 `rmdir` 操作会创建 `DeleteMarker` 对象。

### 身份验证与访问控制 {#id8}

SFTP 访问与其他 S3 客户端一样，使用相同的身份验证机制。 MinIO 支持以下身份验证提供方：

- [MinIO IDP](/docs/administration/identity-access-management/minio-identity-management/#minio-internal-idp) 用户及其服务账户
- [Active Directory/LDAP](/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap) 用户及其服务账户
- [OpenID/OIDC](/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid) 服务账户

[STS](/docs/developers/security-token-service/#minio-security-token-service) 凭证 **不能** 通过 SFTP 访问存储桶或对象。

已通过身份验证的用户可依据分配给该用户或其父用户账号的 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 访问存储桶和对象。

SFTP 协议不需要任何 `admin:*` [权限](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-mc-admin-actions)。 你不能通过 SFTP 执行其他 MinIO 管理操作。

## 前提条件 {#id9}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
- MinIO Operator v5.0.7 或更高版本。
- 为服务器启用一个 SFTP 端口 (8022)。
- 一个用于 SFTP 命令的端口，以及一个端口范围，用于允许 SFTP 服务器在数据传输期间按需请求使用。
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
- MinIO RELEASE.2023-04-20T17-56-55Z 或更高版本。
- 为服务器启用一个 FTP 或 SFTP 端口。
- 一个用于 FTP 命令的端口，以及一个端口范围，用于允许 FTP 服务器在数据传输期间按需请求使用。
{{< /tab >}}
{{< /tabs >}}

## 操作步骤 {#id10}

{{< tabs group="kubernetes-tab2" >}}
{{< tab label="Kubernetes" value="kubernetes" >}}
1. 为目标 Tenant 启用 SFTP：

   使用以下 Kubectl 命令编辑 Tenant YAML 配置：

   ```yaml
   kubectl edit tenants/my-tenant -n my-tenant-ns
   ```

   将 `my-tenant` 和 `my-tenant-ns` 替换为目标 Tenant 和命名空间。

   > 在 `features:` 部分，将 `enableSFTP` 的值设置为 `true`：
   >
   > ```yaml
   > spec:
   >    configuration:
   >       name: my-tenant-env-configuration
   >    credsSecret:
   >       name: my-tenant-secret
   >    exposeServices:
   >       console: true
   >       minio: true
   >    features:
   >       enableSFTP: true
   > ```
   >
   > Kubectl 会重启 MinIO 以应用更改。
   >
   > 你也可以在 [Helm chart](https://github.com/minio/operator/blob/8385948929bc95648d1be82d96f829c810519674/helm/tenant/values.yaml) 或 [Kustomize 配置](https://github.com/minio/operator/blob/8385948929bc95648d1be82d96f829c810519674/examples/kustomization/base/tenant.yaml) 中设置 `enableSFTP`，为新创建的 Tenant 启用 SFTP。
2. 如有需要，请根据本地策略为 SFTP 端口配置 ingress。
3. 验证配置

   以下 `kubectl get` 命令使用 [yq](https://github.com/mikefarah/yq/#install) 显示 `enableSFTP` 的值，以确认是否已启用 SFTP：

   ```console
   kubectl get tenants/my-tenant -n my-tenant-ns -o yaml | yq '.spec.features'
   ```

   将 `my-tenant` 和 `my-tenant-ns` 替换为目标 Tenant 和命名空间。

   如果已启用 SFTP，输出类似如下：

   ```console
   enableSFTP: true
   ```

4. 使用你偏好的 SFTP 客户端连接到 MinIO 部署。 你必须以其 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 允许访问目标存储桶和对象的用户身份进行连接。

   连接到 MinIO 部署的具体方式取决于所使用的 SFTP 客户端。 请参阅该客户端的文档。

   以下示例连接到转发到本地主机系统的 MinIO Tenant SFTP 服务器，并列出名为 `runner` 的存储桶内容。

   > ```console
   > > sftp -P 8022 minio@localhost
   > minio@localhost's password:
   > Connected to localhost.
   > sftp> ls runner/
   > chunkdocs  testdir
   > ```

以下 `kubectl get` 命令使用 [yq](https://github.com/mikefarah/yq/#install) 显示 `enableSFTP` 的值，以确认是否已启用 SFTP：

```console
kubectl get tenants/my-tenant -n my-tenant-ns -o yaml | yq '.spec.features'
```

将 `my-tenant` 和 `my-tenant-ns` 替换为目标 Tenant 和命名空间。

如果已启用 SFTP，输出类似如下：

```console
enableSFTP: true
```
{{< /tab >}}
{{< tab label="裸金属" value="tab2" >}}
1. 启动 MinIO 并启用 FTP 和/或 SFTP 端口。

   {{< tabs group="ftps-sftpftp" >}}
   {{< tab label="FTPS" value="ftps" >}}
   以下示例以启用 FTPS 的方式启动 MinIO。

   ```shell
   minio server http://server{1...4}/disk{1...4} \
   --ftp="address=:8021"                         \
   --ftp="passive-port-range=30000-40000"        \
   --ftp="tls-private-key=path/to/private.key"   \
   --ftp="tls-public-cert=path/to/public.crt"    \
   ...
   ```

   > [!NOTE]
   > **说明**
   >
   > 省略 `tls-private-key` 和 `tls-public-cert` 可使用 MinIO 默认 TLS 密钥进行 FTPS 连接。 更多信息请参阅 [MinIO TLS 文档](/docs/operations/network-encryption/#minio-tls)。
   {{< /tab >}}
   {{< tab label="SFTP/FTP" value="sftpftp" >}}
   ```shell
   minio server http://server{1...4}/disk{1...4}        \
   --ftp="address=:8021"                                \
   --ftp="passive-port-range=30000-40000"               \
   --sftp="address=:8022"                               \
   --sftp="ssh-private-key=/home/miniouser/.ssh/id_rsa" \
   ...
   ```

   有关使用这些标志启动 MinIO 服务的详细信息，请参阅 [`minio server --ftp`](/docs/reference/minio-server/#minio.server.-ftp) 和 [`minio server --sftp`](/docs/reference/minio-server/#minio.server.-sftp)。 若要通过 TLS (FTPS) 连接到 FTP 端口，除非使用 MinIO 默认 TLS 密钥，否则还需要传入 `tls-private-key` 和 `tls-public-cert` 键值。

   命令输出应类似如下：

   ```shell
   MinIO FTP Server listening on :8021
   MinIO SFTP Server listening on :8022
   ```
   {{< /tab >}}
   {{< /tabs >}}
2. 使用你偏好的 FTP 客户端连接到 MinIO 部署。 你必须使用其 [策略](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy) 允许访问目标存储桶和对象的用户身份进行连接。

   连接到 MinIO 部署的具体方式取决于所使用的 FTP 客户端。 请参阅该客户端的文档。

   若要通过 TLS 或 SSH 连接，必须使用支持相应协议的客户端。
3. 连接到 MinIO

   {{< tabs group="sftpftp-ftps" >}}
   {{< tab label="SFTP/FTP" value="sftpftp" >}}
   以下示例连接到 SFTP 服务器，并列出名为 `runner` 的存储桶内容。

   ```console
   > sftp -P 8022 minio@localhost
   minio@localhost's password:
   Connected to localhost.
   sftp> ls runner/
   chunkdocs  testdir
   ```
   {{< /tab >}}
   {{< tab label="FTPS" value="ftps" >}}
   以下示例使用 Linux 的 [FTP CLI client](https://linux.die.net/man/1/ftp)，通过 `minio` 凭证连接到 MinIO 服务器，并列出名为 `runner` 的存储桶内容。

   ```shell
   > ftp localhost -P 8021
   Connected to localhost.
   220 Welcome to MinIO FTP Server
   Name (localhost:user): minio
   331 User name ok, password required
   Password:
   230 Password ok, continue
   Remote system type is UNIX.
   Using binary mode to transfer files.
   ftp> ls runner/
   229 Entering Extended Passive Mode (|||39155|)
   150 Opening ASCII mode data connection for file list
   drwxrwxrwx 1 nobody nobody            0 Jan  1 00:00 chunkdocs/
   drwxrwxrwx 1 nobody nobody            0 Jan  1 00:00 testdir/
   ...
   ```
   {{< /tab >}}
   {{< /tabs >}}
4. 下载对象

   {{< tabs group="sftpftp-ftps" >}}
   {{< tab label="SFTP/FTP" value="sftpftp" >}}
   本示例先列出存储桶中的条目，然后下载该存储桶中的内容。

   ```console
   > sftp -P 8022 minio@localhost
   minio@localhost's password:
   Connected to localhost.
   sftp> ls runner/
   chunkdocs  testdir
   sftp> get runner/chunkdocs/metadata metadata
   Fetching /runner/chunkdocs/metadata to metadata
   metadata                               100%  226    16.6KB/s   00:00
   sftp>
   ```
   {{< /tab >}}
   {{< tab label="FTPS" value="ftps" >}}
   本示例先列出存储桶中的条目，然后下载该存储桶中的内容。

   ```console
   > ftp localhost -P 8021
   Connected to localhost.
   220 Welcome to MinIO FTP Server
   Name (localhost:user): minio
   331 User name ok, password required
   Password:
   230 Password ok, continue
   Remote system type is UNIX.
   Using binary mode to transfer files.ftp> ls runner/chunkdocs/metadata
   229 Entering Extended Passive Mode (|||44269|)
   150 Opening ASCII mode data connection for file list
   -rwxrwxrwx 1 nobody nobody           45 Apr  1 06:13 chunkdocs/metadata
   226 Closing data connection, sent 75 bytes
   ftp> get
   (remote-file) runner/chunkdocs/metadata
   (local-file) test
   local: test remote: runner/chunkdocs/metadata
   229 Entering Extended Passive Mode (|||37785|)
   150 Data transfer starting 45 bytes
      45        3.58 KiB/s
   226 Closing data connection, sent 45 bytes
   45 bytes received in 00:00 (3.55 KiB/s)
   ...
   ```
   {{< /tab >}}
   {{< /tabs >}}
{{< /tab >}}
{{< /tabs >}}

<a id="minio-certificate-key-file-sftp-k8s"></a>

## 使用证书密钥文件通过 SFTP 连接到 MinIO {#sftp-minio}

> [!NOTE]
> **新增: RELEASE.2024-05-07T06-41-25Z**

MinIO 支持在 SFTP 上使用基于证书的双向 TLS (mTLS) 身份验证，服务器与客户端会相互验证对方的真实性。

这种身份验证方式需要以下材料：

1. 受信任证书颁发机构的公钥文件
2. 由受信任证书颁发机构签发并签名的 MinIO Server 公钥文件
3. 供通过 SFTP 连接的客户端使用的用户公钥文件。该文件由受信任证书颁发机构签发并签名，并位于用户的 `.ssh` 文件夹中（或操作系统中的等效位置）

这些密钥必须包含可使用该密钥进行身份验证的用户的 [principals 列表](https://man.openbsd.org/ssh-keygen#CERTIFICATES)：

```shell
ssh-keygen -s ~/.ssh/ca_user_key -I miniouser -n miniouser -V +1h -z 1 miniouser1.pub
```

- **`-s` 指定用于生成此密钥的证书颁发机构公钥路径。**

  > 指定的公钥必须具有包含该用户的 `principals` 列表。
- `-I` 指定该公钥的密钥标识。
- `-n` 创建此密钥有效的 `user principals` 列表。 你必须包含该密钥有效的用户，且该用户必须与 MinIO 中的用户名匹配。
- `-V` 限制生成密钥的有效时长。 在此示例中，该密钥的有效期为一小时。 请根据需求调整时长。
- `-z` 为密钥添加序列号，以便将此生成的公钥与由同一证书颁发机构公钥签名的其他密钥区分开。

MinIO 要求指定用于签发 SFTP 访问证书的证书颁发机构 (Certificate Authority)。 启动或重启 MinIO Server，并通过 `--sftp="trusted-user-ca-key=PATH"` 参数指定受信任证书颁发机构公钥的路径：

```shell
minio server {path-to-server} --sftp="trusted-user-ca-key=/path/to/.ssh/ca_user_key.pub" {...other flags}
```

通过 SFTP 连接到 MinIO 服务端 时，客户端会先验证 MinIO Server 的证书。 随后，客户端会将自己的证书发送给 MinIO Server。 MinIO Server 会将上面创建的密钥与服务器启动时提供的证书颁发机构公钥进行比对，以验证该密钥。

一旦 MinIO Server 验证了客户端证书，用户就可以通过 SFTP 连接到 MinIO 服务端：

```bash
sftp -P <SFTP port> <server IP>
```

### 要求使用服务账户或 LDAP 进行身份验证 {#ldap}

若要强制使用 LDAP 或服务账户凭证进行 SFTP 身份验证，请在用户名后附加后缀。 有效后缀为 `=ldap` 或 `=svc`。

```console
> sftp -P 8022 my-ldap-user=ldap@[minio@localhost]:/bucket
```

```console
> sftp -P 8022 my-ldap-user=svc@[minio@localhost]:/bucket
```

- 将 `my-ldap-user` 替换为要使用的用户名。
- 将 `[minio@localhost]` 替换为 MinIO 服务器地址。