---
title: "mc ilm edit"

weight: 20
---

<a id="mc-ilm-edit"></a>
<a id="minio-mc-ilm-edit"></a>

<a id="command-mc.ilm.edit"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm edit` 已被 [`mc ilm rule edit`](/docs/reference/minio-mc/mc-ilm-rule-edit/#command-mc.ilm.rule.edit) 取代。

## 语法 {#id2}

[`mc ilm edit`](#command-mc.ilm.edit) 命令用于修改 MinIO 存储桶上现有的对象生命周期管理规则。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令用于修改 `myminio` 部署上 `mydata` 存储桶的现有生命周期管理规则：

```shell
mc ilm edit --id "c79ntj94b0t6rukh6lr0" --expiry-days 90  mydata/myminio

mc ilm edit --id "c79nu2p4b0t6qko19rgg" --expired-object-delete-marker mydata/myminio

mc ilm edit --id "c79n19dn10dnab109fg1" --transition-days 30 --tier "COLDTIER"
```

该命令按如下方式修改指定规则：

- 删除对象创建时间超过 90 天的对象。
- 如果对象没有其他剩余版本，则删除 `DeleteMarker` 墓碑标记。
- 将对象创建时间超过 30 天的对象转移到 `COLDTIER` 远程层。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] ilm edit \
                 --id "string"                                                                                        \
                 [--prefix "string"]                                                                                  \
                 [--enable]                                                                                           \
                 [--disable]                                                                                          \
                 [--expiry-days "string" | --expired-object-delete-marker]                                            \
                 [--transition-days "string"] --tier "string"                                                \
                 [--noncurrentversion-expiration-days "string"]                                                       \
                 [--noncurrentversion-transition-days "string" --noncurrentversion-tier "string"] \
                 [--tags]                                                                                             \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.edit.ALIAS}

*mc-cmd*

*Required*

需要指定 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 以及要修改对象生命周期管理规则的存储桶完整路径。例如：

```text
mc ilm edit myminio/mydata
```

##### `--id` {#mc.ilm.edit.-id}

*mc-cmd*

*Required*

规则的唯一 ID。使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 列出存储桶规则，并获取要修改规则的 `id`。

##### `--disable` {#mc.ilm.edit.-disable}

*mc-cmd*

*Optional*

停止使用该规则，但保留该规则以备后续使用。 规则禁用后，对象不会发生转移或过期。

##### `--enable` {#mc.ilm.edit.-enable}

*mc-cmd*

*Optional*

启用规则以对对象执行转移或过期。

##### `--prefix` {#mc.ilm.edit.-prefix}

*mc-cmd*

*Optional*

将管理规则限制到特定的存储桶前缀。

例如：

```text
mc ilm edit --prefix "meetingnotes/" myminio/mydata/ --expiry-days "90"
```

该命令修改一条规则：对 `myminio` ALIAS 中 `mydata` 存储桶内所有带有 `meetingnotes/` 前缀的对象，在 90 天后过期。

##### `--expiry-days` {#mc.ilm.edit.-expiry-days}

*mc-cmd*

*Optional*

对象创建后保留的天数。达到指定天数后，MinIO 会将对象标记为待删除。

使用此选项时请谨慎，其行为可能导致已上传对象立即过期。任何在指定过期日期 *之后* 创建的对象都会自动满足过期条件。 同样地，如果指定的日历日期 *早于* 当前系统主机时间日期，则规则覆盖的所有对象都会被标记为删除。 一旦指定日历日期已过，建议立即移除使用此选项的 ILM 规则。

对于启用版本控制的存储桶，过期规则仅适用于 *当前* 对象版本。 使用 [`--noncurrentversion-expiration-days`](#mc.ilm.edit.-noncurrentversion-expiration-days) 选项可将过期行为应用于非当前对象版本。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的全部生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的扫描变慢，可能会延迟生命周期管理规则的生效。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner)。

与以下选项互斥：

- [`--expired-object-delete-marker`](#mc.ilm.edit.-expired-object-delete-marker)

更多信息请参见 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

##### `--expired-object-delete-marker` {#mc.ilm.edit.-expired-object-delete-marker}

*mc-cmd*

*Optional*

指定此选项可指示 MinIO 删除没有剩余对象版本的对象的删除标记。 具体而言，删除标记是给定对象唯一剩余的“版本”。

此选项与以下选项互斥：

- [`--tags`](#mc.ilm.edit.-tags)
- [`--expiry-days`](#mc.ilm.edit.-expiry-days)

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的全部生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的扫描变慢，可能会延迟生命周期管理规则的生效。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 和 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

##### `--noncurrentversion-expiration-days` {#mc.ilm.edit.-noncurrentversion-expiration-days}

*mc-cmd*

*Optional*

对象版本变为 *非当前*（即该对象的另一个版本现在是 *HEAD*）后保留的天数。 达到指定天数后，MinIO 会将非当前对象版本标记为待删除。

此选项的行为与 S3 `NoncurrentVersionExpiration` 操作一致。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的全部生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的扫描变慢，可能会延迟生命周期管理规则的生效。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner)。

##### `--noncurrentversion-transition-days` {#mc.ilm.edit.-noncurrentversion-transition-days}

*mc-cmd*

*Optional*

对象处于非当前状态（即已被同一对象的新版本替换）达到指定天数后， MinIO 会将该对象版本标记为可转移。 系统主机时间日期超过该日历日期后，MinIO 会将对象转移到 [`--tier`](#mc.ilm.edit.-tier) 指定的远程存储层。

此选项对未启用版本控制的存储桶无效。必须同时指定 [`--noncurrentversion-tier`](#mc.ilm.edit.-noncurrentversion-tier)。

此选项的行为与 S3 `NoncurrentVersionTransition` 操作一致。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的全部生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的扫描变慢，可能会延迟生命周期管理规则的生效。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner)。

##### `--noncurrentversion-tier` {#mc.ilm.edit.-noncurrentversion-tier}

*mc-cmd*

*Optional*

MinIO 将 [非当前对象版本转移](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 到的远程存储层。 指定一个由 [`mc admin tier`](/docs/reference/deprecated/mc-admin-tier/#command-mc.admin.tier) 创建的远程存储层。

MinIO *不会* 自动将对象从先前指定的远程层迁移到新的远程层。 对于存储在旧远程层上的对象，MinIO 仍会继续路由请求。

##### `--newer-noncurrentversions-expiration` {#mc.ilm.edit.-newer-noncurrentversions-expiration}

*mc-cmd*

*Optional*

应用过期规则前要保留的对象非当前版本数量。 超过指定数量的更旧非当前版本会过期。

默认情况下，当过期规则生效时，MinIO 不保留任何非当前版本。

##### `--newer-noncurrentversions-transition` {#mc.ilm.edit.-newer-noncurrentversions-transition}

*mc-cmd*

*Optional*

要保留在当前存储层上的对象非当前版本数量。 超过指定数量的更旧非当前版本会转移到指定层。

默认情况下，当转移规则生效时，MinIO 会转移所有非当前版本。

##### `--tags` {#mc.ilm.edit.-tags}

*mc-cmd*

*Optional*

一个或多个以 `&` 分隔的键值对，用于描述要应用生命周期配置规则的对象标签。

此选项与以下选项互斥：

- [`--expired-object-delete-marker`](#mc.ilm.edit.-expired-object-delete-marker)

##### `--transition-days` {#mc.ilm.edit.-transition-days}

*mc-cmd*

*Optional*

对象创建后经过的日历天数，超过该值后 MinIO 会将对象标记为可转移。 MinIO 会将对象转移到 [`--tier`](#mc.ilm.edit.-tier) 指定的远程存储层。

对于启用版本控制的存储桶，转移规则仅适用于 *当前* 对象版本。 使用 [`--noncurrentversion-transition-days`](#mc.ilm.edit.-noncurrentversion-transition-days) 选项可将转移行为应用于非当前对象版本。

必须同时指定 [`--tier`](#mc.ilm.edit.-tier)。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的全部生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的扫描变慢，可能会延迟生命周期管理规则的生效。 更多信息请参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner)。

##### `--tier` {#mc.ilm.edit.-tier}

*mc-cmd*

*Optional*

MinIO 将 [对象转移](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 到的远程存储层。 指定一个由 [`mc admin tier`](/docs/reference/deprecated/mc-admin-tier/#command-mc.admin.tier) 创建的远程存储层。

若指定 [`--transition-days`](#mc.ilm.edit.-transition-days)，则此选项为必需。

MinIO *不会* 自动将对象从先前指定的远程层迁移到新的远程层。 对于存储在旧远程层上的对象，MinIO 仍会继续路由请求。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 修改现有生命周期管理规则 {#id6}

使用 [`mc ilm edit`](#command-mc.ilm.edit) 搭配 [`--id`](#mc.ilm.edit.-id) 修改现有对象过期规则：

```shell
mc ilm edit ALIAS/PATH --id "RULEID" [FLAGS]
```

- 将 [`ALIAS`](#mc.ilm.edit.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ilm.edit.ALIAS) 替换为该 S3 兼容主机上的存储桶路径。
- 将 `RULEID` 替换为对象生命周期管理规则的唯一 ID。 使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 查找 `RULEID`。
- 指定任意附加标志以添加或修改生命周期管理规则。 例如，指定 [`--transition-days`](#mc.ilm.edit.-transition-days) 以覆盖该规则现有的转移天数值。

### 禁用生命周期管理规则 {#id7}

使用 [`mc ilm edit`](#command-mc.ilm.edit) 搭配 [`--disable`](#mc.ilm.edit.-disable) 停止使用现有管理规则。

```shell
mc ilm edit --id "RULEID" --disable myminio/mybucket
```

- 将 `RULEID` 替换为对象生命周期管理规则的唯一 ID。 使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 查找 `RULEID`。
- 将 `myminio` 替换为规则所在部署的 ALIAS。
- 将 `mybucket` 替换为该规则对应的存储桶。

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。