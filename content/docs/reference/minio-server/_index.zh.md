---
title: "Silo 服务端（minio）"

weight: 30
aliases:
  - "/reference/minio-server/minio-server/"
icon: fa-solid fa-database
---

<a id="minio"></a>

<a id="command-minio"></a>

## Silo 服务端 {#minio-server}

[`minio server`](#command-minio.server) 命令用于启动 Silo 服务端进程。可执行文件与子命令名称 `minio server` 属于兼容契约：

```shell
minio server /mnt/disk{1...4}
```

有关在裸金属环境中部署 [`minio server`](#command-minio.server) 的示例，请参阅 [安装与管理](/docs/operations/deployments/installation/#minio-installation)。

有关在 Kubernetes 环境中部署 [`minio server`](#command-minio.server) 的示例，请参阅 [部署 Silo Tenant](/docs/operations/deployments/k8s-deploy-minio-tenant-on-kubernetes/#minio-k8s-deploy-minio-tenant)。

<a id="id2"></a>
<a id="minio-server-parameters"></a>

### 语法 {#command-minio.server}

启动 `minio` server 进程。

该命令语法如下：

```shell
minio server [FLAGS] HOSTNAME/DIRECTORIES [HOSTNAME/DIRECTORIES..]
```

该命令接受以下参数：

##### `HOSTNAME` {#minio.server.HOSTNAME}

*mc-cmd*

[`minio server`](#command-minio.server) 进程的主机名。

对于单机部署，此字段为 *可选*。 仅使用 [`DIRECTORIES`](#minio.server.DIRECTORIES) 参数即可启动一个单机 [`server`](#command-minio.server) 进程。

对于分布式部署，请指定部署中每个 [`minio server`](#command-minio.server) 的主机名。 这一组 [`minio server`](#command-minio.server) 进程共同表示一个 [服务器池](/docs/operations/concepts/#minio-intro-server-pool)。

[`HOSTNAME`](#minio.server.HOSTNAME) 支持扩展记法 `{x...y}`，用于表示按顺序排列的一组主机名。Silo *要求* 使用连续主机名，以识别该集合中的每个 [`minio server`](#command-minio.server) 进程。

例如，`https://minio{1...4}.example.net` 会扩展为：

- `https://minio1.example.net`
- `https://minio2.example.net`
- `https://minio3.example.net`
- `https://minio4.example.net`

你必须在 服务器池 中每台主机上，使用 *相同* 的 [`HOSTNAME`](#minio.server.HOSTNAME) 和 [`DIRECTORIES`](#minio.server.DIRECTORIES) 组合来运行 [`minio server`](#command-minio.server) 命令。

每增加一个 `HOSTNAME/DIRECTORIES` 对，就表示增加一个 Server Set，用于 Silo 部署的水平扩展。有关服务器池的更多信息，请参阅 [服务器池](/docs/operations/concepts/#minio-intro-server-pool)。

##### `DIRECTORIES` {#minio.server.DIRECTORIES}

*mc-cmd*

*Required*

[`minio server`](#command-minio.server) 进程用作存储后端的目录或驱动器。

[`DIRECTORIES`](#minio.server.DIRECTORIES) 支持扩展记法 `{x...y}`，用于表示按顺序排列的一组文件夹或驱动器。例如，`/mnt/disk{1...4}` 会扩展为：

- `/mnt/disk1`
- `/mnt/disk2`
- `/mnt/disk3`
- `/mnt/disk4`

首次启动 [`minio`](#command-minio.server) 进程时，[`DIRECTORIES`](#minio.server.DIRECTORIES) 路径 *必须* 为空。

[`minio server`](#command-minio.server) 进程至少需要 4 个驱动器或目录才能启用 [erasure coding](/docs/operations/concepts/erasure-coding/#minio-erasure-coding)。

> [!WARNING]
> **重要**
>
> Silo 建议使用本地直连驱动器，即 [`DIRECTORIES`](#minio.server.DIRECTORIES) 路径指向主机上的各个驱动器。除非已验证完整技术栈，应避免把网络附加存储用作主对象数据存储，因为其网络延迟和故障语义与本地直连存储不同。
>
> 在开发或评估场景中，你可以在单个物理卷上指定多个逻辑目录或分区，以便在部署中启用纠删码。
>
> 对于生产环境，**不要** 把同一物理磁盘上的多个逻辑目录或分区当作独立故障域。表面上的驱动器数量不能提供物理磁盘冗余。

##### `--address` {#minio.server.-address}

*mc-cmd*

*Optional*

将 [`minio`](#command-minio.server) server 进程绑定到特定网络地址和端口号。 将地址和端口指定为 `ADDRESS:PORT`，其中 `ADDRESS` 是 IP 地址或主机名，`PORT` 是主机系统上有效且开放的端口。 MinIO 同时支持 IPv4 和 IPv6 寻址，前提是指定地址可路由且可解析。

若要为主机上配置的所有 IP 地址或主机名修改端口号，仅指定 `:PORT` 即可，其中 `PORT` 是主机上有效且开放的端口。

> [!NOTE]
> **变更: RELEASE.2023-01-02T09-40-09Z**
>
> 你可以通过配置 hosts 文件，让 MinIO 仅监听特定 IP。 例如，如果机器的 */etc/hosts* 文件包含以下内容：
>
> ```shell
> 127.0.1.1       minioip
> 127.0.1.2       minioip
> ```
>
> 类似下面的命令会在两个已配置 IP 地址的 `9000` 端口上监听 API 调用。
>
> ```shell
> minio server --address "minioip:9000" ~/miniodirectory
> ```

若省略该参数，[`minio`](#command-minio.server) 会绑定到主机上所有已配置 IPv4 地址、IPv6 地址和主机名的 `9000` 端口。

##### `--console-address` {#minio.server.-console-address}

*mc-cmd*

*Optional*

为内置 MinIO Console 指定静态端口。

省略时，MinIO 会在 server 启动时生成动态端口。 MinIO server 会将该端口输出到系统日志。

##### `--ftp` {#minio.server.-ftp}

*mc-cmd*

*Optional*

启用并配置 File Transfer Protocol（`FTP`）或 File Transfer Protocol over SSL/TLS（`FTPS`）服务器。 多次使用该 flag 可按键值对指定地址端口、被动端口范围或 TLS 证书与密钥。

有效键如下：

- `address`，用于指定服务器使用的单个端口，通常为 `8021`
- *(Optional)* `passive-port-range`，用于限制服务器可用于传输数据的端口范围，例如防火墙规则较严格、限制 FTP 服务器可为连接请求端口时
- *(Optional)* `tls-private-key`，用于指定用户私钥路径，以便通过 TLS 访问 MinIO 部署

  与 `tls-public-cert` 配合使用。
- *(Optional)* `tls-public-cert`，用于指定证书路径，以便通过 TLS 访问 MinIO 部署

  与 `tls-private-key` 配合使用。

对于已启用 TLS 的 MinIO 部署，省略 `tls-private-key` 和 `tls-public-key`，可让 MinIO 使用部署默认 TLS 密钥。 更多信息请参阅 [网络加密（TLS）](/docs/operations/network-encryption/#minio-tls)。 仅当你要使用与 MinIO 默认值不同的一组 TLS 证书和密钥时，才需要指定证书与私钥（例如使用不同域名）。

例如：

```shell
minio server http://server{1...4}/disk{1...4} \
--ftp="address=:8021"                         \
--ftp="passive-port-range=30000-40000"        \
--ftp="tls-private-key=path/to/private.key"   \
--ftp="tls-public-cert=path/to/public.crt"    \
...
```

##### `--sftp` {#minio.server.-sftp}

*mc-cmd*

*Optional*

启用并配置 SSH File Transfer Protocol（`SFTP`）服务器。 可多次使用以指定所需的每个键值对。

下表列出有效键。

<table>
  <thead>
    <tr>
      <th><p>键</p></th>
      <th><p>说明</p></th>
      <th><p>有效值</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>address</code></p></td>
      <td><p>用于连接到 SFTP 的端口。</p></td>
      <td><p>任意有效端口号，通常为 <code>8022</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>ssh-private-key</code></p></td>
      <td><p>用户私钥文件路径。</p></td>
      <td><p>用于密钥文件的绝对路径，或相对于当前位置的相对路径。</p></td>
    </tr>
    <tr>
      <td><p><code>trusted-user-ca-key</code></p></td>
      <td><p>指定一个文件，其中包含受信任证书颁发机构的公钥，该机构可对用于身份验证的用户证书签名。
文件必须包含 <a href="https://man.openbsd.org/ssh-keygen#CERTIFICATES">user principals list</a>，且列表必须包含可使用该密钥进行身份验证的用户。</p></td>
      <td><p>用户受信任证书颁发机构公钥文件的绝对路径，或相对于当前位置的相对路径。</p></td>
    </tr>
    <tr>
      <td><p><code>pub-key-algos</code></p></td>
      <td><p>以逗号分隔的公钥算法列表。</p></td>
      <td><pre><code class="language-text">ssh-ed25519
sk-ssh-ed25519@openssh.com
sk-ecdsa-sha2-nistp256@openssh.com
ecdsa-sha2-nistp256
ecdsa-sha2-nistp384
ecdsa-sha2-nistp521
rsa-sha2-256
rsa-sha2-512
ssh-rsa
ssh-dss</code></pre></td>
    </tr>
    <tr>
      <td><p><code>kex-algos</code></p></td>
      <td><p>按优先级顺序排列的、以逗号分隔的密钥交换算法列表。</p></td>
      <td><pre><code class="language-text">curve25519-sha256
curve25519-sha256@libssh.org
ecdh-sha2-nistp256
ecdh-sha2-nistp384
ecdh-sha2-nistp521
diffie-hellman-group14-sha256
diffie-hellman-group16-sha512
diffie-hellman-group14-sha1
diffie-hellman-group1-sha1</code></pre></td>
    </tr>
    <tr>
      <td><p><code>cipher-algos</code></p></td>
      <td><p>以逗号分隔的支持的加密算法列表</p></td>
      <td><pre><code class="language-text">aes128-ctr
aes192-ctr
aes256-ctr
aes128-gcm@openssh.com
aes256-gcm@openssh.com
chacha20-poly1305@openssh.com
arcfour256
arcfour128
arcfour
aes128-cbc
3des-cbc</code></pre></td>
    </tr>
    <tr>
      <td><p><code>mac-algos</code></p></td>
      <td><p>按优先级顺序排列的、以逗号分隔的 MAC 算法列表。
基于 <a href="https://www.rfc-editor.org/rfc/rfc4253">RFC 4253 section 6.4</a>，但 <code>hmac-md5</code> 变体除外（已终止生命周期）。</p></td>
      <td><pre><code class="language-text">hmac-sha2-256-etm@openssh.com
hmac-sha2-512-etm@openssh.com
hmac-sha2-256
hmac-sha2-512
hmac-sha1
hmac-sha1-96</code></pre></td>
    </tr>
    <tr>
      <td><p><code>disable-password-auth</code></p></td>
      <td><p>禁用密码认证。</p></td>
      <td><p><code>true</code></p></td>
    </tr>
  </tbody>
</table>

例如：

```shell
minio server http://server{1...4}/disk{1...4}                                 \
--sftp="address=:8022" --sftp="ssh-private-key=/home/miniouser/.ssh/id_rsa"   \
--sftp="kex-algos=diffie-hellman-group14-sha256,curve25519-sha256@libssh.org" \
...
```

##### `--certs-dir, -S` {#minio.server.-certs-dir}

*mc-cmd*

*Optional*

指定包含证书的文件夹路径，[`minio`](#command-minio) 进程使用该路径中的证书配置 TLS/SSL 连接。

指定文件夹的内容必须符合 [default path structure](/docs/operations/network-encryption/#minio-tls-user-generated)。 例如，`--certs-dir /etc/minio` 的路径内容应类似如下：

```shell
/etc/minio
  private.key
  public.crt
  domain.tld/
    private.key
    public.crt
  CAs/
    full-chain-ca.crt
```

省略时使用默认目录路径：

- Linux/macOS: `${HOME}/.minio/certs`
- Windows: `%%USERPROFILE%%\.minio\certs`.

有关 TLS/SSL 连接的更多信息，请参阅 [网络加密（TLS）](/docs/operations/network-encryption/#minio-tls)。

> [!WARNING]
> **重要**
>
> [MinIO Server RELEASE.2023-12-09T18-17-51Z](https://github.com/minio/minio/releases/tag/RELEASE.2023-12-09T18-17-51Z) 移除了已弃用参数 `--config-dir | -C`。 使用该 flag 的部署可能会在未启用 TLS 的情况下启动。 请将这些参数替换为 `--certs-dir | -S` 并重启，以重新启用 TLS。

##### `--quiet` {#minio.server.-quiet}

*mc-cmd*

*Optional*

禁用启动信息输出。

##### `--anonymous` {#minio.server.-anonymous}

*mc-cmd*

*Optional*

在日志中隐藏敏感信息。

##### `--json` {#minio.server.-json}

*mc-cmd*

*Optional*

以 `JSON` 格式输出 server 日志和启动信息。

> [!NOTE]
> **说明**
>
> 你可以通过在 [`MINIO_OPTS`](/docs/reference/minio-server/settings/core/#envvar.MINIO_OPTS) 环境变量中设置上述任意 `minio` 参数来定义它们。 该变量的值是一个字符串，包含你希望在启动 MinIO Server 时设置的上述参数及其对应取值。

## 设置 {#id3}

你可以通过定义额外的 [Configuration Values](/docs/reference/minio-server/settings/#minio-server-configuration-options) 或 [Environment Variables](/docs/reference/minio-server/settings/#minio-server-environment-variables)，对 MinIO 服务端进程执行其他自定义配置。

许多配置值和环境变量定义的是同一个值。 如果同时设置配置值及其对应环境变量，MinIO 使用环境变量中的值。