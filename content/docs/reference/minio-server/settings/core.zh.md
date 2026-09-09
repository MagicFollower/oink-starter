---
title: "核心设置"

weight: 20
---

<a id="minio-server-envvar-core"></a>
<a id="id1"></a>

本页介绍用于控制 MinIO 进程核心行为的设置。

你可以通过以下方式建立或修改设置：

- 在启动或重启 MinIO Server 之前，在宿主机系统上定义 *环境变量*。 如何定义环境变量，请参考所用操作系统的文档。
- 使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 定义 *配置项*。

如果同时定义了环境变量和对应的配置项，MinIO 使用环境变量的值。

有些设置只有环境变量或配置项中的一种，而不是两者同时存在。

> [!WARNING]
> **重要**
>
> 每个配置项都会控制 MinIO 的基础行为和功能。 MinIO **强烈建议** 先在 DEV 或 QA 等较低级别环境中测试配置变更，再应用到生产环境。

## MinIO Server CLI 选项 {#minio-server-cli}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_OPTS` {#envvar.MINIO_OPTS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此变量没有对应的配置项，因为这些设置在服务器启动时生效。
{{< /tab >}}
{{< /tabs >}}

*可选*

设置一个 [参数](/docs/reference/minio-server/#minio-server-parameters) 字符串，在启动 MinIO Server 时使用。

对于采用推荐 MinIO `systemd` 服务的类 Unix 系统，请使用 `/etc/default/minio` 文件并创建环境变量 `MINIO_OPTS`，用于指定要附加到 `minio` systemd 进程的参数：

```shell
# Editing /etc/default/minio

MINIO_OPTS=' --console-address=":9001" --ftp="address=:8021" --ftp="passive-port-range=30000-40000" '
```

对于在命令行运行 `minio` 的系统，`MINIO_OPTS` 是可选项。 如需使用，请按标准 shell 语义声明该环境变量，然后在启动 MinIO Server 时引用该环境变量：

```shell
export MINIO_OPTS=' --console-address=":9001" --ftp="address=:8021" --ftp="passive-port-range=30000-40000" '

minio server $MINIO_OPTS ...

# The above is equivalent to running the following:
# minio server --console-address=":9001" \
#              --ftp="address=:8021"     \
#              --ftp="passive-port-range=30000-40000"
```

> [!WARNING]
> **重要**
>
> `minio server` 命令不会直接读取 `$MINIO_OPTS`。 该变量仅在按上述方式使用时才会生效。

## 存储卷 {#id3}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_VOLUMES` {#envvar.MINIO_VOLUMES}

*envvar*

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程用作存储后端的目录或磁盘。

在功能上等价于设置 [`minio server DIRECTORIES`](/docs/reference/minio-server/#minio.server.DIRECTORIES)。 在通过环境文件配置 MinIO 运行时使用此值。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

## 环境变量文件路径 {#id4}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_CONFIG_ENV_FILE` {#envvar.MINIO_CONFIG_ENV_FILE}

*envvar*

指定 MinIO server 进程用于加载环境变量的文件完整路径。

对于由 `systemd` 管理的文件，将该值设置为环境文件路径（`/etc/default/minio`），以便在使用 [`mc admin service restart`](/docs/reference/minio-mc-admin/mc-admin-service/#mc.admin.service.restart) 重启部署时，指示 MinIO 重新加载该文件中的变更。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

## 过期处理工作线程 {#id5}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_ILM_EXPIRY_WORKERS` {#envvar.MINIO_ILM_EXPIRY_WORKERS}

*envvar*

指定用于处理按 ILM 过期规则配置对象过期任务的工作线程数。 未设置时，MinIO 默认最多使用可用处理器核心数的一半。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

## 域名 {#id6}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_DOMAIN` {#envvar.MINIO_DOMAIN}

*envvar*

为 MinIO 部署启用 Virtual Host 风格请求。 将该值设置为完全限定域名（FQDN），使 MinIO 能够接受传入的虚拟主机请求。

省略此设置时，MinIO 仅接受默认的 path-style 请求。

例如，某个 MinIO 部署分配的 FQDN 为 `minio.example.net`。

- 使用 path-style 访问时，应用可通过完整路径 `minio.example.net/mybucket` 访问存储桶。
- 使用 virtual-host 访问时，应用可通过虚拟主机 `mybucket.minio.example.net/` 访问存储桶。

> [!WARNING]
> **重要**
>
> 如果配置了 `MINIO_DOMAIN`，你 **必须** 将指定 FQDN 的所有子域名视为专用于存储桶名称。 任何与这些域名冲突的 MinIO 服务（例如复制目标）都可能因为冲突而表现出意外或非预期行为。
>
> 例如，若设置 `MINIO_DOMAIN=minio.example.net`，则 **不能** 将 `minio.example.net` 的任何子域名（即 `*.minio.example.net` 形式）分配给任何 MinIO 服务或目标。 这包括用于 [bucket](/docs/administration/bucket-replication/#minio-bucket-replication)、[batch](/docs/administration/batch-framework-job-replicate/#minio-batch-framework-replicate-job) 或 [site replication](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview) 的主机名。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

<a id="id7"></a>

## 扫描器速度 {#minio-scanner-speed-options}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_SCANNER_SPEED` {#envvar.MINIO_SCANNER_SPEED}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `scanner speed` {#mc-conf.scanner.speed}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

用于在平衡 MinIO 读写性能与扫描进程时，管理 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 的最大等待周期。

MinIO 使用 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 执行 [存储桶复制](/docs/administration/bucket-replication/#minio-bucket-replication)、 [站点复制](/docs/operations/replication/multi-site-replication/#minio-site-replication-overview)、 [生命周期管理](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management) 和 [自愈](/docs/operations/concepts/healing/#minio-concepts-healing) 任务。

有效值包括：

<table>
  <tbody>
    <tr>
      <td><p><code>fastest</code></p></td>
      <td><p>移除扫描器在读/写延迟上的等待时间，使扫描器以最高速度和 IOPS 消耗运行。
此设置可能导致读取和写入性能下降。</p></td>
    </tr>
    <tr>
      <td><p><code>fast</code></p></td>
      <td><p>将扫描器在读/写延迟上的等待时间设置为较短，
使扫描器以更高速度和 IOPS 消耗运行。
此设置可能导致读取和写入性能下降。</p></td>
    </tr>
    <tr>
      <td><p><code>default</code></p></td>
      <td><p>将扫描器在读/写延迟上的等待时间设置为中等，
使扫描器以平衡的速度和 IOPS 消耗运行。
此设置旨在在保持读写性能的同时允许扫描器持续工作。</p></td>
    </tr>
    <tr>
      <td><p><code>slow</code></p></td>
      <td><p>将扫描器在读/写延迟上的等待时间设置为中等，
此时扫描器以较低速度和 IOPS 消耗运行。
该设置在降低扫描器性能的同时，可提供更好的读写性能。</p><p>可能影响依赖扫描器的功能，例如生命周期管理和复制。</p></td>
    </tr>
    <tr>
      <td><p><code>slowest</code></p></td>
      <td><p>将扫描器在读/写延迟上的等待时间设置为较长，
此时扫描器以显著更低的速度和 IOPS 消耗运行。
该设置优先保障读写操作，但可能以牺牲扫描器操作为代价。</p><p>可能影响依赖扫描器的功能，例如生命周期管理和复制。</p></td>
    </tr>
  </tbody>
</table>

## 批量复制 {#id8}

{{< tabs group="tab1" >}}
{{< tab label="配置项" value="tab1" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

## 数据压缩 {#id9}

以下部分记录用于为对象启用数据压缩的设置。 有关如何使用这些配置设置的教程，请参见 [数据压缩](/docs/administration/object-management/data-compression/#minio-data-compression)。

本节中的所有设置都归属于以下顶层键：

#### `compression` {#mc-conf.compression}

*mc-conf*

### 启用压缩 {#id10}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_COMPRESSION_ENABLE` {#envvar.MINIO_COMPRESSION_ENABLE}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `compression enable` {#mc-conf.compression.enable}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

*可选*

设置为 `on` 以对新对象启用数据压缩。 默认为 `off`。

启用或禁用数据压缩不会更改现有对象。

### 允许加密 {#id11}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_COMPRESSION_ALLOW_ENCRYPTION` {#envvar.MINIO_COMPRESSION_ALLOW_ENCRYPTION}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `compression allow_encryption` {#mc-conf.compression.allow_encryption}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

*可选*

设置为 `on` 以在压缩后对对象进行加密。 默认为 `off`。

> [!NOTE]
> **对压缩对象加密可能会削弱安全性**
>
> MinIO 强烈不建议对压缩对象进行加密。 如果你需要加密，请仔细评估可能泄露加密对象内容信息的风险。

### 压缩扩展名 {#id12}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_COMPRESSION_EXTENSIONS` {#envvar.MINIO_COMPRESSION_EXTENSIONS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `compression extensions` {#mc-conf.compression.extensions}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

*可选*

要压缩的文件扩展名列表，以逗号分隔。 设置新的扩展名列表会替换先前已配置的列表。 默认为 `".txt, .log, .csv, .json, .tar, .xml, .bin"`。

> [!NOTE]
> **变更: RELEASE.2024-03-15T01-07-19Z**
>
> 可指定 `"*"` 以指示 MinIO 压缩所有受支持的文件类型。

即使在此参数中显式指定，MinIO 也不支持压缩 [Excluded File Types](/docs/administration/object-management/data-compression/#minio-data-compression-excluded-types) 列表中的文件类型。

### 压缩 MIME 类型 {#mime}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
##### `MINIO_COMPRESSION_MIME_TYPES` {#envvar.MINIO_COMPRESSION_MIME_TYPES}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `compression mime_types` {#mc-conf.compression.mime_types}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

*可选*

要压缩的 MIME 类型列表，以逗号分隔。 设置新的类型列表会替换先前已配置的列表。 默认为 `"text/*, application/json, application/xml, binary/octet-stream"`。

> [!NOTE]
> **默认排除文件**
>
> 某些类型的文件无法显著减小体积。 MinIO *不会* 压缩这些文件，即使它们在 [`mime_types`](#mc-conf.compression.mime_types) 参数中被指定。 详见 [Excluded types](/docs/administration/object-management/data-compression/#minio-data-compression-excluded-types)。

### 注释 {#id13}

{{< tabs group="tab1-tab2" default="tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
此设置没有环境变量选项。 请改用配置项。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
##### `compression comment` {#envvar.compression.comment}

*envvar*
{{< /tab >}}
{{< /tabs >}}

*可选*

指定一个与数据压缩配置关联的注释。

## 纠删码条带大小 {#id14}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_ERASURE_SET_DRIVE_COUNT` {#envvar.MINIO_ERASURE_SET_DRIVE_COUNT}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

*可选*

应用于指定 [服务器池](/zh/glossary/#term-43) 中所有驱动器的 [erasure set size](/docs/operations/concepts/erasure-coding/#minio-ec-basics)。

如果设置此值，你 **必须** 在初始化集群 *之前* 完成设置。 集群初始化后，所选条带大小为 **不可变**，并会影响后续添加到集群中的所有 服务器池。

[MinIO SUBNET](https://min.io/pricing?jmp=docs) 用户应先登录并提交 issue，讨论条带大小设置后再在任何环境中实施。

> [!CAUTION]
> **警告**
>
> 除非 MinIO 工程团队明确指导，否则 **不要** 更改条带大小设置。
>
> 条带大小变更会对部署功能、可用性、性能和行为产生重大影响。 MinIO 的条带选择算法已为大多数工作负载设置了适当默认值。 偏离该默认值来调整条带大小并不常见，通常也没有必要或不被建议。

## 最大对象版本数 {#id15}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_API_OBJECT_MAX_VERSIONS` {#envvar.MINIO_API_OBJECT_MAX_VERSIONS}

*envvar*
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
#### `api object_max_versions` {#mc-conf.api.object_max_versions}

*mc-conf*
{{< /tab >}}
{{< /tabs >}}

*可选*

定义每个对象允许的默认最大版本数。

默认情况下，MinIO 允许每个对象的版本数最高达到 Int64 的最大值，即超过 9.2 quintillion。

> [!NOTE]
> **说明**
>
> `RELEASE.2023-08-04T17-40-21Z` 到 `RELEASE.2024-03-26T22-10-45Z` 之间的 MinIO 版本，默认上限为 10,000 个对象版本。 可使用此设置将该上限覆盖为其他值。

为对象设置任意高的版本数可能导致某些操作（如 `LIST`）性能下降。 在使用低成本硬件或机械硬盘（HDD）的系统上，这一点尤为明显。 对于每个对象会生成数千个或更多版本的应用或工作负载，可能需要进行设计或架构评审，以缓解潜在的性能下降。

将上限设置为不超过 `100`，通常可满足大多数常见使用场景。

## 客户端源地址信任 {#client-source-address-trust}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_API_TRUSTED_PROXIES` {#envvar.MINIO_API_TRUSTED_PROXIES}

*envvar*

指定哪些对端有资格告诉服务器"请求来自哪里"。

默认情况下，MinIO 会采信来自任何对端的 `X-Forwarded-For`、`X-Real-IP` 与 RFC 7239 `Forwarded` 头，因此一个能直接连到 API 端口的客户端可以自行设定它表面上的源地址。该地址会流入 `aws:SourceIp` 策略条件、审计日志的 `remotehost` 字段，以及事件通知的 `Host` 字段。

将其设为以逗号分隔的地址或 CIDR 列表，则 **只** 采信名单内对端送来的转发头。此时转发链会从右向左、跳过名单内的跳数来解析，这也会丢弃"追加型代理"在链首留下的、由客户端自己提供的那一项——nginx 默认的 `$proxy_add_x_forwarded_for` 写法与 HAProxy 追加的第二行头都会产生这一项。

将其设为 `none`，则完全不采信任何转发头，始终使用对端地址。

> [!NOTE]
> **说明**
>
> 不设置是默认值，保持历史行为，因此在你主动配置之前该设置完全惰性。
>
> 要列出 **代理本身，而不是它们所在的网段**。名单内的条目在遍历转发链时会被跳过，因此一个同时覆盖了客户端的网段，等于让那些客户端可以伪造。多节点部署必须把自己各节点的地址也列进去，因为 MinIO 会在节点之间转发部分请求。回环地址始终被视为可信对端，以便 FTP 与 SFTP 能正确归属其会话。取值格式错误、或没有指向任何代理，都会阻止启动。

如果你使用 `IpAddress` 或 `NotIpAddress` 策略条件，那么在此设置指明你的代理之前（或部署本身除代理外不可达之前），这些条件是无法强制执行的。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}

## 旧版存储桶资源匹配 {#legacy-bucket-resource-matching}

{{< tabs group="tab1-tab2" >}}
{{< tab label="环境变量" value="tab1" >}}
#### `MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH` {#envvar.MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH}

*envvar*

设为 `on` 可恢复桶级请求在 IAM 策略资源匹配上的历史行为。

默认情况下，有十二个桶级写操作不再能通过 `arn:aws:s3:::mybucket/*` 这样的对象级资源模式获得授权。动作清单以及正确授予它们的策略改法，见[存储桶资源与对象资源](/docs/administration/identity-access-management/policy-based-access-control/#bucket-and-object-resources)。

设为 `on` 会回到"把桶级请求与字符串 `mybucket/` 相匹配"的做法，而对象模式同样命中该字符串。该值在启动时读取一次，仅用作更新存量策略期间的临时手段。

> [!WARNING]
> **这会恢复一处过度授予**
>
> 正是这种历史匹配方式，让一个只持有 `arn:aws:s3:::mybucket/*` 上 `s3:*` 的主体能够改写桶策略（包括把桶变为公开），或者直接删除该桶。这个开关是全有全无的：为了一个动作打开它，会把十二个动作一并放开。
{{< /tab >}}
{{< tab label="配置项" value="tab2" >}}
此设置没有对应的配置项。
{{< /tab >}}
{{< /tabs >}}