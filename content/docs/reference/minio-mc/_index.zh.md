---
title: "Silo 客户端（mcli / mc）"

weight: 10
icon: fa-solid fa-terminal
---

<a id="minio"></a>
<a id="minio-client"></a>

<a id="command-mc"></a>

Pigsty 维护的客户端在独立归档与 Linux 软件包中以 **`mcli`** 发布；源码构建、容器入口点、配置目录、模块路径和命令语法则为兼容性保留 **`mc`**。它为文件系统和兼容 Amazon S3 的对象存储提供 `ls`、`cat`、`cp`、`mirror`、`diff` 等熟悉的命令。

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建。发布版本以 Silo 为正式验收对象，并尽最大努力兼容上游 MinIO 与其他 S3 兼容端点。

Silo 项目无法保证它与每一种其他 S3 兼容服务的行为，因为各家实现存在差异。在将其他服务视为兼容对象前，请先测试工作负载依赖的操作。

当前版本为 [`RELEASE.2026-09-03T07-13-05Z`](https://github.com/pgsty/mc/releases/tag/RELEASE.2026-09-03T07-13-05Z)，使用 Go 1.27.1 构建。它新增只读审计命令 [`mc checksum verify`](/docs/reference/minio-mc/mc-checksum-verify/#command-mc.checksum.verify)，并加固包含凭据的输出、策略写入、支持产物与发布溯源。20260806 以来的精确行为与依赖变化参见 [MCLI 客户端兼容性注记](/docs/compatibility/mcli/#current-release)。

[`mc`](#command-mc) 的语法如下：

```shell
mc [GLOBALFLAGS] COMMAND --help
```

支持的命令列表参见 [命令速查](#minio-mc-commands)。

<a id="id2"></a>

## 与 Silo 服务端的版本对齐 {#mc-client-versioning}

客户端与 Silo 服务端独立发布。

为获得最佳功能与兼容性，建议使用与 Silo 服务端发布时间接近的客户端版本。对上游 MinIO 的兼容属于尽最大努力；使用时请联测确切的客户端与服务端版本。

可以安装比服务端更新的客户端。但如果版本偏差过大，即使 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 等核心 S3 操作仍兼容，管理功能或 flag 也可能存在差异。

<a id="id3"></a>

<a id="quickstart"></a>

## 快速开始 {#mc-install}

### 1) 安装客户端 {#mc}

请从[下载与安装](/zh/download/#client)页面选择 Linux 软件包、适用于 Linux/macOS/Windows 的归档文件或客户端容器。版本化制品与校验和也可从 [GitHub Releases](https://github.com/pgsty/mc/releases) 获取。

独立归档与 Linux 软件包安装的命令名是 **`mcli`**，容器与源码构建则保留 **`mc`**。两者是同一个客户端的别名；本文档示例使用 `mc`，若主机上安装的是 `mcli`，请直接替换命令名。

从源码构建维护分支：

```shell
git clone https://github.com/pgsty/mc.git
cd mc
make build
./mc --version
```

> [!WARNING]
> Pigsty 分支刻意禁用了 [`mc update`](/docs/reference/minio-mc/mc-update/#command-mc.update)。请通过 [Silo 下载页](/zh/download/#client)、[Pigsty 软件仓库](https://pigsty.cc/docs/repo/infra/list/#object-storage)或 [GitHub Releases](https://github.com/pgsty/mc/releases)升级。

> [!NOTE]
> 当前 `pgsty/mc` 为脚本兼容保留 `mc license` 与 `mc support` 命令树，但所有在线 MinIO SUBNET、许可、上传、call-home 与遥测路径都已禁用。会联系这些服务的命令以稳定消息失败并返回 `1`；`support diag`、`perf`、`profile`、`inspect` 等本地诊断无需注册即可使用，并写入私有权限的本地文件。参见 [MCLI 客户端兼容性注记](/docs/compatibility/mcli/#subnet)。

### 2) 为兼容 S3 的服务创建别名 {#s3}

> [!WARNING]
> **重要**
>
> 以下示例会临时禁用 bash history，以降低身份认证凭据明文泄露的风险。 这是一项基础安全措施，无法覆盖所有可能的攻击向量。 对于在命令行输入敏感信息，请遵循你所用操作系统的安全最佳实践。

使用 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 命令将 Amazon S3 兼容服务添加到 [`mc`](#command-mc) [配置](#mc-configuration) 中。

```shell
bash +o history
mc alias set ALIAS HOSTNAME ACCESS_KEY SECRET_KEY
bash -o history
```

- 将 `ALIAS` 替换为与 S3 服务关联的名称。 [`mc`](#command-mc) 命令通常要求提供 `ALIAS` 作为参数， 以标识要执行操作的 S3 服务。
- 将 `HOSTNAME` 替换为 S3 服务的 URL endpoint 或 IP 地址。
- 将 `ACCESS_KEY` 和 `SECRET_KEY` 替换为该 S3 服务上某个用户的 access key 和 secret key。

将各参数替换为所需值。 如果省略 `ACCESS_KEY` 和 `SECRET_KEY`，命令会在 CLI 中提示输入这两个值。

以下每个标签页都包含一个特定提供商示例：

```shell {tab="Silo 服务端" group="silo-aws-s3-storage-google-cloud-storage" value="silo"}
mc alias set silo https://silo.example.net ACCESS_KEY SECRET_KEY
```

```shell {tab="AWS S3 Storage" value="aws-s3-storage"}
mc alias set myS3 https://s3.{your-region-code}.amazonaws.com/endpoint ACCESS_KEY SECRET_KEY
```

```shell {tab="Google Cloud Storage" value="google-cloud-storage"}
mc alias set myGCS https://storage.googleapis.com/endpoint ACCESS_KEY SECRET_KEY
```

### 3) 测试连接 {#id4}

使用 [`mc admin info`](/docs/reference/minio-mc-admin/mc-admin-info/#command-mc.admin.info) 命令测试与新添加 Silo 部署的连接：

```shell
mc admin info silo
```

如果命令执行成功，会返回该 S3 服务的信息。 如果失败，请检查以下各项：

- 主机可连通 S3 服务 URL（例如使用 `ping` 或 `traceroute`）。
- 指定的 `ACCESSKEY` 和 `SECRETKEY` 对应 S3 服务上的有效用户。 该用户必须有权限在该服务上执行操作。

  对于 MinIO 部署，参见 [Access Management](/docs/administration/identity-access-management/#minio-access-management) 获取更多用户访问权限信息。对于其他兼容 S3 的 服务，请参考该服务文档。

<a id="id5"></a>

## 命令速查 {#minio-mc-commands}

下表列出了 [`mc`](#command-mc) 命令：

> [!NOTE]
> **说明**
>
> 客户端还包含以 Silo 为正式验收对象的管理扩展，并尽最大努力兼容 MinIO 部署。更完整文档参见 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin)。
>
> 下表不包含这些命令。

<table>
  <thead>
    <tr>
      <th><p>命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-alias-list/#command-mc.alias.list"><code>mc alias list</code></a><br /><a href="/docs/reference/minio-mc/mc-alias-remove/#command-mc.alias.remove"><code>mc alias remove</code></a><br /><a href="/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set"><code>mc alias set</code></a><br /><a href="/docs/reference/minio-mc/mc-alias-import/#command-mc.alias.import"><code>mc alias import</code></a><br /><a href="/docs/reference/minio-mc/mc-alias-export/#command-mc.alias.export"><code>mc alias export</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-alias/#command-mc.alias"><code>mc alias</code></a> 命令提供了一个便捷接口，用于管理 <a href="#command-mc"><code>mc</code></a> 可连接并执行操作的 S3 兼容主机列表。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-anonymous-get/#command-mc.anonymous.get"><code>mc anonymous get</code></a><br /><a href="/docs/reference/minio-mc/mc-anonymous-get-json/#command-mc.anonymous.get-json"><code>mc anonymous get-json</code></a><br /><a href="/docs/reference/minio-mc/mc-anonymous-links/#command-mc.anonymous.links"><code>mc anonymous links</code></a><br /><a href="/docs/reference/minio-mc/mc-anonymous-list/#command-mc.anonymous.list"><code>mc anonymous list</code></a><br /><a href="/docs/reference/minio-mc/mc-anonymous-set/#command-mc.anonymous.set"><code>mc anonymous set</code></a><br /><a href="/docs/reference/minio-mc/mc-anonymous-set-json/#command-mc.anonymous.set-json"><code>mc anonymous set-json</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous/#command-mc.anonymous"><code>mc anonymous</code></a> 命令支持为存储桶及其内容设置或移除匿名 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policies</a>。
配置了匿名策略的存储桶允许公开访问，客户端无需进行 <a href="/docs/administration/identity-access-management/#minio-authentication-and-identity-management">authentication</a> 即可执行策略授予的任意操作。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-batch-describe/#command-mc.batch.describe"><code>mc batch describe</code></a><br /><a href="/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate"><code>mc batch generate</code></a><br /><a href="/docs/reference/minio-mc/mc-batch-list/#command-mc.batch.list"><code>mc batch list</code></a><br /><a href="/docs/reference/minio-mc/mc-batch-start/#command-mc.batch.start"><code>mc batch start</code></a><br /><a href="/docs/reference/minio-mc/mc-batch-status/#command-mc.batch.status"><code>mc batch status</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-batch/#command-mc.batch"><code>mc batch</code></a> 命令允许您在 MinIO 部署上运行一个或多个作业任务。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-cat/#command-mc.cat"><code>mc cat</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-cat/#command-mc.cat"><code>mc cat</code></a> 命令将文件或对象的内容连接到另一个文件或对象。
你也可以使用该命令将指定文件或对象的内容输出到 <code>STDOUT</code>。
<a href="/docs/reference/minio-mc/mc-cat/#command-mc.cat"><code>cat</code></a> 的功能与 <code>cat</code> 类似。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-checksum-verify/#command-mc.checksum.verify"><code>mc checksum verify</code></a></p></td>
      <td><p>Silo 客户端扩展会独立重算并比对存储的 S3 full-object 校验和。它是只读命令，支持单对象、递归前缀、版本、候选清单、dry run、JSON Lines 报告与显式失败策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-cp/#command-mc.cp"><code>mc cp</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-cp/#command-mc.cp"><code>mc cp</code></a> 命令用于在 MinIO 部署与本地文件系统之间复制对象，
其中源端可以是 MinIO <em>或</em> 本地文件系统。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-diff/#command-mc.diff"><code>mc diff</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-diff/#command-mc.diff"><code>mc diff</code></a> 命令用于计算两个文件系统目录或 MinIO 存储桶之间的差异。
<a href="/docs/reference/minio-mc/mc-diff/#command-mc.diff"><code>mc diff</code></a> 仅列出缺失的对象或大小不同的对象。<a href="/docs/reference/minio-mc/mc-diff/#command-mc.diff"><code>mc diff</code></a>
<strong>不会</strong>比较对象内容。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-du/#command-mc.du"><code>mc du</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-du/#command-mc.du"><code>mc du</code></a> 命令用于汇总存储桶和文件夹的磁盘使用量。
你也可以对本地文件系统使用 <a href="/docs/reference/minio-mc/mc-du/#command-mc.du"><code>du</code></a>，以生成与 <code>du</code> 命令类似的结果。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-encrypt-clear/#command-mc.encrypt.clear"><code>mc encrypt clear</code></a><br /><a href="/docs/reference/minio-mc/mc-encrypt-info/#command-mc.encrypt.info"><code>mc encrypt info</code></a><br /><a href="/docs/reference/minio-mc/mc-encrypt-set/#command-mc.encrypt.set"><code>mc encrypt set</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-encrypt/#command-mc.encrypt"><code>mc encrypt</code></a> 命令用于设置、更新或禁用存储桶默认的服务端加密（SSE）模式。
MinIO 会使用指定的 SSE 模式自动加密对象。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-event-add/#command-mc.event.add"><code>mc event add</code></a><br /><a href="/docs/reference/minio-mc/mc-event-list/#command-mc.event.ls"><code>mc event ls</code></a><br /><a href="/docs/reference/minio-mc/mc-event-remove/#command-mc.event.rm"><code>mc event rm</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-event/#command-mc.event"><code>mc event</code></a> 命令支持添加、删除和列出存储桶事件通知。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-find/#command-mc.find"><code>mc find</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-find/#command-mc.find"><code>mc find</code></a> 命令支持在 MinIO 部署上搜索对象。
你也可以使用该命令在文件系统上搜索文件。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-get/#command-mc.get"><code>mc get</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-get/#command-mc.get"><code>mc get</code></a> 命令将对象从目标 S3 部署下载到本地文件系统。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-head/#command-mc.head"><code>mc head</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-head/#command-mc.head"><code>mc head</code></a> 命令显示对象的前 <code>n</code> 行，
其中 <code>n</code> 是传递给该命令的参数。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey/#command-mc.idp.ldap.accesskey"><code>mc idp ldap accesskey</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-accesskey-create-with-login/#command-mc.idp.ldap.accesskey.create-with-login"><code>mc idp ldap accesskey create-with-login</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-add/#command-mc.idp.ldap.add"><code>mc idp ldap add</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-disable/#command-mc.idp.ldap.disable"><code>mc idp ldap disable</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-enable/#command-mc.idp.ldap.enable"><code>mc idp ldap enable</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-info/#command-mc.idp.ldap.info"><code>mc idp ldap info</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-ls/#command-mc.idp.ldap.ls"><code>mc idp ldap ls</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy"><code>mc idp ldap policy</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-rm/#command-mc.idp.ldap.rm"><code>mc idp ldap rm</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-update/#command-mc.idp.ldap.update"><code>mc idp ldap update</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap/#command-mc.idp.ldap"><code>mc idp ldap</code></a> 命令用于管理第三方 <a href="/docs/administration/identity-access-management/ad-ldap-access-management/#minio-external-identity-management-ad-ldap">Active Directory 或 LDAP 身份与访问管理（IAM）集成</a> 的配置。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.add"><code>mc idp openid add</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.disable"><code>mc idp openid disable</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.enable"><code>mc idp openid enable</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.info"><code>mc idp openid info</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.ls"><code>mc idp openid ls</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.rm"><code>mc idp openid rm</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-openid/#mc.idp.openid.update"><code>mc idp openid update</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-openid/#command-mc.idp.openid"><code>mc idp openid</code></a> 命令允许你管理第三方 <a href="/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid">OpenID 身份与访问管理（IAM）集成</a> 的配置。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-idp-ldap-policy-attach/#command-mc.idp.ldap.policy.attach"><code>mc idp ldap policy attach</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-policy-detach/#command-mc.idp.ldap.policy.detach"><code>mc idp ldap policy detach</code></a><br /><a href="/docs/reference/minio-mc/mc-idp-ldap-policy-entities/#command-mc.idp.ldap.policy.entities"><code>mc idp ldap policy entities</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-idp-ldap-policy/#command-mc.idp.ldap.policy"><code>mc idp ldap policy</code></a> 命令用于显示策略与关联组或用户之间的映射关系。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-ilm-restore/#command-mc.ilm.restore"><code>mc ilm restore</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add"><code>mc ilm rule add</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-edit/#command-mc.ilm.rule.edit"><code>mc ilm rule edit</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-export/#command-mc.ilm.rule.export"><code>mc ilm rule export</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-import/#command-mc.ilm.rule.import"><code>mc ilm rule import</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls"><code>mc ilm rule ls</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-rule-rm/#command-mc.ilm.rule.rm"><code>mc ilm rule rm</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-add/#command-mc.ilm.tier.add"><code>mc ilm tier add</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-check/#command-mc.ilm.tier.check"><code>mc ilm tier check</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-info/#command-mc.ilm.tier.info"><code>mc ilm tier info</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-ls/#command-mc.ilm.tier.ls"><code>mc ilm tier ls</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-rm/#command-mc.ilm.tier.rm"><code>mc ilm tier rm</code></a><br /><a href="/docs/reference/minio-mc/mc-ilm-tier-update/#command-mc.ilm.tier.update"><code>mc ilm tier update</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ilm/#command-mc.ilm"><code>mc ilm</code></a> 命令用于管理 MinIO 部署中的 <a href="/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management">对象生命周期管理规则</a> 和分层。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-legalhold-clear/#command-mc.legalhold.clear"><code>mc legalhold clear</code></a><br /><a href="/docs/reference/minio-mc/mc-legalhold-info/#command-mc.legalhold.info"><code>mc legalhold info</code></a><br /><a href="/docs/reference/minio-mc/mc-legalhold-set/#command-mc.legalhold.set"><code>mc legalhold set</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-legalhold/#command-mc.legalhold"><code>mc legalhold</code></a> 命令用于为一个或多个对象设置、移除或获取 <a href="/docs/administration/object-management/object-retention/#minio-object-locking-legalhold">object legal hold (WORM)</a> 配置。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-license-info/#command-mc.license.info"><code>mc license info</code></a><br /><a href="/docs/reference/minio-mc/mc-license-register/#command-mc.license.register"><code>mc license register</code></a><br /><a href="/docs/reference/minio-mc/mc-license-update/#command-mc.license.update"><code>mc license update</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-license/#command-mc.license"><code>mc license</code></a> 命令用于管理 <a href="https://min.io/pricing?jmp=docs">MinIO SUBNET</a> 的集群注册。
可使用这些命令注册部署、显示集群当前许可证信息，或更新集群的许可证密钥。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ls/#command-mc.ls"><code>mc ls</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ls/#command-mc.ls"><code>mc ls</code></a> 命令用于列出 MinIO 或其他 S3 兼容服务上的存储桶和对象。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-mb/#command-mc.mb"><code>mc mb</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-mb/#command-mc.mb"><code>mc mb</code></a> 命令在指定路径创建新的存储桶或目录。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-mirror/#command-mc.mirror"><code>mc mirror</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-mirror/#command-mc.mirror"><code>mc mirror</code></a> 命令用于将内容同步到 MinIO 部署，类似于 <code>rsync</code> 工具。
<a href="/docs/reference/minio-mc/mc-mirror/#command-mc.mirror"><code>mc mirror</code></a> 支持以文件系统、MinIO 部署和其他 S3 兼容主机作为同步源。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-mv/#command-mc.mv"><code>mc mv</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-mv/#command-mc.mv"><code>mc mv</code></a> 命令将对象从源移动到目标，例如在不同 MinIO 部署之间移动，<em>或</em> 在同一 MinIO 部署的不同存储桶之间移动。
<a href="/docs/reference/minio-mc/mc-mv/#command-mc.mv"><code>mc mv</code></a> 还支持在本地文件系统与 MinIO 之间移动对象。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-od/#command-mc.od"><code>mc od</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-od/#command-mc.od"><code>mc od</code></a> 命令将本地文件按指定的分片数量与分片大小复制到远程位置。
该命令会输出上传该文件所耗费的时间。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ping/#command-mc.ping"><code>mc ping</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ping/#command-mc.ping"><code>mc ping</code></a> 命令对指定目标执行存活性检查。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-pipe/#command-mc.pipe"><code>mc pipe</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-pipe/#command-mc.pipe"><code>mc pipe</code></a> 命令将内容从 <a href="https://www.gnu.org/software/libc/manual/html_node/Standard-Streams.html">STDIN</a> 流式传输到目标对象。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-put/#command-mc.put"><code>mc put</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-put/#command-mc.put"><code>mc put</code></a> 将对象从本地文件系统上传到目标 S3 部署中的存储桶。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-rb/#command-mc.rb"><code>mc rb</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-rb/#command-mc.rb"><code>mc rb</code></a> 命令用于删除 MinIO <em>或</em> 其他兼容 S3 服务上的一个或多个存储桶。</p><p>如仅需删除存储桶内容，请改用 <a href="/docs/reference/minio-mc/mc-rm/#command-mc.rm"><code>mc rm</code></a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-ready/#command-mc.ready"><code>mc ready</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-ready/#command-mc.ready"><code>mc ready</code></a> 命令用于检查集群状态，以及集群是否具有 <code>read</code> 和 <code>write</code> quorum。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add"><code>mc replicate add</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-backlog/#command-mc.replicate.backlog"><code>mc replicate backlog</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-export/#command-mc.replicate.export"><code>mc replicate export</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-import/#command-mc.replicate.import"><code>mc replicate import</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls"><code>mc replicate ls</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-resync/#command-mc.replicate.resync"><code>mc replicate resync</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-rm/#command-mc.replicate.rm"><code>mc replicate rm</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-status/#command-mc.replicate.status"><code>mc replicate status</code></a><br /><a href="/docs/reference/minio-mc/mc-replicate-update/#command-mc.replicate.update"><code>mc replicate update</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-replicate-add/#command-mc.replicate.add"><code>mc replicate</code></a> 命令用于为 MinIO 部署配置和管理 <a href="/docs/administration/bucket-replication/#minio-bucket-replication-serverside">服务端存储桶复制</a>，包括 <a href="/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway">双活复制配置</a> 和 <a href="/docs/administration/bucket-replication/#minio-replication-behavior-resync">重新同步</a>。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-retention-clear/#command-mc.retention.clear"><code>mc retention clear</code></a><br /><a href="/docs/reference/minio-mc/mc-retention-info/#command-mc.retention.info"><code>mc retention info</code></a><br /><a href="/docs/reference/minio-mc/mc-retention-set/#command-mc.retention.set"><code>mc retention set</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-retention/#command-mc.retention"><code>mc retention</code></a> 命令用于为存储桶中的一个或多个对象配置 <a href="/docs/administration/object-management/object-retention/#minio-object-locking">Write-Once Read-Many (WORM) locking</a> 设置。
你还可以为存储桶设置默认的对象锁定设置；未显式配置对象锁定设置的所有对象都会继承该存储桶默认值。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-rm/#command-mc.rm"><code>mc rm</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-rm/#command-mc.rm"><code>mc rm</code></a> 命令用于从 MinIO 部署的存储桶中 <a href="/docs/administration/object-management/object-delete/#minio-object-delete">删除对象</a>。
如需彻底删除存储桶，请改用 <a href="/docs/reference/minio-mc/mc-rb/#command-mc.rb"><code>mc rb</code></a>。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-share-download/#command-mc.share.download"><code>mc share download</code></a><br /><a href="/docs/reference/minio-mc/mc-share-list/#command-mc.share.ls"><code>mc share ls</code></a><br /><a href="/docs/reference/minio-mc/mc-share-upload/#command-mc.share.upload"><code>mc share upload</code></a><br /></td>
      <td><p>使用 <a href="/docs/reference/minio-mc/mc-share/#command-mc.share"><code>mc share</code></a> 命令管理预签名 URL，以便下载和上传 MinIO 存储桶中的对象。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-sql/#command-mc.sql"><code>mc sql</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-sql/#command-mc.sql"><code>mc sql</code></a> 命令提供 S3 Select 接口，用于对指定 MinIO 部署中的对象执行 SQL 查询。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-stat/#command-mc.stat"><code>mc stat</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-stat/#command-mc.stat"><code>mc stat</code></a> 命令用于显示 MinIO 存储桶中对象的信息，包括对象元数据。
你也可以使用它来检索存储桶元数据。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-support-callhome/#command-mc.support.callhome"><code>mc support callhome</code></a><br /><a href="/docs/reference/minio-mc/mc-support-diag/#command-mc.support.diag"><code>mc support diag</code></a><br /><a href="/docs/reference/minio-mc/mc-support-inspect/#command-mc.support.inspect"><code>mc support inspect</code></a><br /><a href="/docs/reference/minio-mc/mc-support-perf/#command-mc.support.perf"><code>mc support perf</code></a><br /><a href="/docs/reference/minio-mc/mc-support-profile/#command-mc.support.profile"><code>mc support profile</code></a><br /><a href="/docs/reference/minio-mc/mc-support-proxy/#command-mc.support.proxy"><code>mc support proxy</code></a><br /><a href="/docs/reference/minio-mc/mc-support-top-api/#command-mc.support.top.api"><code>mc support top api</code></a><br /><a href="/docs/reference/minio-mc/mc-support-top-disk/#command-mc.support.top.disk"><code>mc support top disk</code></a><br /><a href="/docs/reference/minio-mc/mc-support-top-locks/#command-mc.support.top.locks"><code>mc support top locks</code></a><br /><a href="/docs/reference/minio-mc/mc-support-upload/#command-mc.support.upload"><code>mc support upload</code></a><br /></td>
      <td><p>MinIO Client <a href="/docs/reference/minio-mc/mc-support/#command-mc.support"><code>mc support</code></a> 命令提供用于分析部署健康状况或性能、并运行诊断的工具。
你还可以上传生成的健康报告，供 MinIO 工程团队进一步分析。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-tag-list/#command-mc.tag.list"><code>mc tag list</code></a><br /><a href="/docs/reference/minio-mc/mc-tag-remove/#command-mc.tag.remove"><code>mc tag remove</code></a><br /><a href="/docs/reference/minio-mc/mc-tag-set/#command-mc.tag.set"><code>mc tag set</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-tag/#command-mc.tag"><code>mc tag</code></a> 命令用于添加、删除和列出与存储桶或对象关联的标签。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-tree/#command-mc.tree"><code>mc tree</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-tree/#command-mc.tree"><code>mc tree</code></a> 命令以树形格式列出 MinIO 存储桶中的所有前缀。
该命令还可选支持在每个前缀处列出存储桶内的所有对象，包括存储桶根。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-undo/#command-mc.undo"><code>mc undo</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-undo/#command-mc.undo"><code>mc undo</code></a> 命令用于撤销指定路径上由 <code>PUT</code> 或 <code>DELETE</code> 操作引起的更改。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-update/#command-mc.update"><code>mc update</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-update/#command-mc.update"><code>mc update</code></a> 兼容命令会报告自更新已禁用。请通过 Silo 下载页、Pigsty 软件仓库或 GitHub Releases 升级。</p></td>
    </tr>
    <tr>
      <td><a href="/docs/reference/minio-mc/mc-version-enable/#command-mc.version.enable"><code>mc version enable</code></a><br /><a href="/docs/reference/minio-mc/mc-version-info/#command-mc.version.info"><code>mc version info</code></a><br /><a href="/docs/reference/minio-mc/mc-version-suspend/#command-mc.version.suspend"><code>mc version suspend</code></a><br /></td>
      <td><p><a href="/docs/reference/minio-mc/mc-version/#command-mc.version"><code>mc version</code></a> 命令可为 MinIO 存储桶启用、禁用并获取 <a href="/docs/administration/object-management/object-versioning/#minio-bucket-versioning">版本控制</a> 状态。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-watch/#command-mc.watch"><code>mc watch</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-watch/#command-mc.watch"><code>mc watch</code></a> 命令用于监视指定 MinIO 存储桶或本地文件系统路径上的事件。
对于 S3 服务，请使用 <a href="/docs/reference/minio-mc/mc-event-add/#command-mc.event.add"><code>mc event add</code></a> 在兼容 S3 的服务上配置存储桶事件通知。</p></td>
    </tr>
  </tbody>
</table>

<a id="id8"></a>

## 配置文件 {#mc-configuration}

[`mc`](#command-mc) 使用 `JSON` 格式的配置文件来存储 某些类型的信息，例如每个已配置兼容 S3 服务的 [`aliases`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

在 Linux 和 macOS 上，默认配置文件位置为 `~/.mc/config.json`。

在 Windows 上，[`mc`](#command-mc) 会尝试通过特定环境变量 构造默认文件路径。如果某个变量未设置，[`mc`](#command-mc) 会继续 尝试下一个变量。如果所有尝试都失败，[`mc`](#command-mc) 会返回错误。 下列列表按 [`mc`](#command-mc) 检查顺序说明了可能的文件路径位置：

1. `HOME\.mc\config.json`
2. `USERPROFILE\.mc\config.json`
3. `HOMEDRIVE+HOMEPATH\.mc\config.json`

可使用 `--config-dir`

<a id="id9"></a>

## 证书 {#minio-mc-certificates}

MinIO 客户端将部署使用的证书和 CA 存储在以下路径：

Linux、macOS 和其他类 Unix 系统：

```shell
~/.mc/certs/ # certificates
~/.mc/certs/CAs/ # Certificate Authorities
```

Windows 系统：

```shell
C:\Users\[username]\mc\certs\ # certificates
C:\Users\[username]\mc\certs\CAs\ # Certificate Authorities
```

创建新的 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias) 时，MinIO Client 会拉取对端证书、计算公钥指纹，并询问用户是否接受该部署的证书。 如果你决定信任该证书，MinIO Client 会将其添加到上述证书颁发机构路径。

> [!NOTE]
> **说明**
>
> 在测试环境中，你可以通过传入 `--insecure` flag，跳过部分 MinIO Client 命令的证书检查。

<a id="id10"></a>

## 模式匹配 {#minio-wildcard-matching}

某些命令和 flag 支持模式匹配。 启用后，模式可包含以下任一通配符用于字符替换：

- `*` 表示要匹配的一串字符，可位于中间或末尾。
- `?` 表示单个字符。

例如，可参考以下通配符使用示例及其结果。

| 模式 | 文本 | 匹配结果 |
| --- | --- | --- |
| `abc*` | ab | 匹配 |
| `abc*` | abd | 不匹配 |
| `abc*c` | abcd | 匹配 |
| `ab*??d` | abxxc | 匹配 |
| `ab*??d` | abxc | 匹配 |
| `ab??d` | abxc | 匹配 |
| `ab??d` | abc | 匹配 |
| `ab??d` | abcxdd | 不匹配 |

<a id="id11"></a>

## 全局选项 {#minio-mc-global-options}

所有 [commands](#minio-mc-commands) 都支持以下全局选项。 你也可以使用 [Environment Variables](/docs/reference/minio-mc/minio-client-settings/#minio-server-envvar-mc) 来定义其中部分选项。

#### `--config-dir` {#cmdoption-mc-config-dir}

*option*

指向 `JSON` 格式配置文件的路径， **`mc`** 使用该文件存储数据。有关 **`mc`** 如何使用配置文件的更多信息，请参见 [配置文件](#mc-configuration)。

或者，设置环境变量 [`MC_CONFIG_DIR`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_CONFIG_DIR)。

#### `--debug` {#cmdoption-mc-debug}

*option*

启用控制台详细输出。

例如，以下操作会为 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls) 命令增加详细输出：

```shell
mc --debug ls play
```

或者，设置环境变量 [`MC_DEBUG`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_DEBUG)。

<a id="cmdoption-mc-dp"></a>

#### `--disable-pager --dp` {#cmdoption-mc-disable-pager}

*option*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-04-29T09-56-05Z

在 CLI 中禁用 MinIO Client 的分页功能。 使用后，输出会直接打印到原始 `STDOUT`。

#### `--insecure` {#cmdoption-mc-insecure}

*option*

禁用 TLS/SSL 证书校验。允许与证书无效的 服务器建立 TLS 连接。对不受信任的 S3 主机使用该 选项时请谨慎。

或者，设置环境变量 [`MC_INSECURE`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_INSECURE)。

#### `--json` {#cmdoption-mc-json}

*option*

启用 [JSON lines](http://jsonlines.org/)<a id="json-lines"></a> 格式输出到 控制台。

例如，以下操作会为 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls) 命令增加 JSON Lines 输出：

```shell
mc --json ls play
```

或者，设置环境变量 [`MC_JSON`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_JSON)。

#### `--no-color` {#cmdoption-mc-no-color}

*option*

禁用控制台输出的内置配色主题。适用于 dumb 终端。

或者，设置环境变量 [`MC_NO_COLOR`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_NO_COLOR)。

#### `--quiet` {#cmdoption-mc-quiet}

*option*

抑制控制台输出。

或者，设置环境变量 [`MC_QUIET`](/docs/reference/minio-mc/minio-client-settings/#envvar.MC_QUIET)。

#### `--resolve` {#cmdoption-mc-resolve}

*option*

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-08-13T05-33-17Z

创建自定义 DNS 映射，将 HOST 解析到指定 IP 地址。

使用以下语法：

```text
--resolve HOST[:PORT]=IP
```

例如：

```shell
mc alias set --resolve myminio.example.com:9000=192.168.188.118 'myminio' 'https://myminio.example.com:9000' 'miniouser' 'miniosecret'
```

可重复该 flag 多次以添加更多自定义 DNS 映射。

#### `--version` {#cmdoption-mc-version}

*option*

显示 [`mc`](#command-mc) 的当前版本。

#### `--help` {#mc.-help}

*mc-cmd*

*Optional*

在终端显示命令用法摘要。