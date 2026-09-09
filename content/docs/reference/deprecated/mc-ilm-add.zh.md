---
title: "mc ilm add"

weight: 10
---

<a id="mc-ilm-add"></a>
<a id="minio-mc-ilm-add"></a>

<a id="command-mc.ilm.add"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm add` 已由 [`mc ilm rule add`](/docs/reference/minio-mc/mc-ilm-rule-add/#command-mc.ilm.rule.add) 取代。

## 语法 {#id2}

[`mc ilm add`](#command-mc.ilm.add) 命令用于向存储桶添加对象生命周期管理规则。

该命令支持同时添加 [Transition (Tiering)](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 和 [Expiration](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 生命周期管理规则。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会向 `myminio` 部署上的 `mydata` 存储桶添加新的生命周期管理规则：

```shell
mc ilm add --expire-days 90 --noncurrent-expire-days 30 myminio/mydata

mc ilm add --expire-delete-marker myminio/mydata

mc ilm add --transition-days 30 --transition-tier "COLDTIER" myminio/mydata

mc ilm add --noncurrent-transition-days 7 --noncurrent-transition-tier "COLDTIER"
```

已配置规则的效果如下：

- 删除超过 90 天的对象
- 在对象变为非当前版本 30 天后删除该对象
- 如果对象没有其他剩余版本，则删除其 `DeleteMarker` 墓碑。
- 将超过 30 天的对象过渡到 `COLDTIER` 远程层。
- 在对象变为非当前版本 7 天后，将其过渡到 `COLDTIER` 远程层。
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] ilm add                                    \
                 [--prefix string]                          \
                 [--tags string]                            \
                 --expire-days "integer"                    \
                 [--expire-delete-marker]                   \
                 [--transition-days "string"]               \
                 [--transition-tier "string"]               \
                 [--noncurrent-expire-days "integer"]       \
                 [--noncurrent-expire-newer "integer"]      \
                 [--noncurrent-transition-days "integer"]   \
                 [--noncurrent-transition-tier "string"]    \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.add.ALIAS}

*mc-cmd*

*Required*

要添加对象生命周期管理规则的 MinIO 部署中的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶。

例如：

```text
mc ilm add myminio/mydata
```

##### `--prefix` {#mc.ilm.add.-prefix}

*mc-cmd*

*Optional*

将管理规则限制到特定对象前缀。

例如：

```text
mc ilm add --prefix "meetingnotes/" myminio/mydata/ --expire-days "90"
```

该命令会创建一条规则：对 `myminio` ALIAS 下 `mydata` 存储桶中带有 `meetingnotes/` 前缀的对象，在 90 天后过期。

##### `--tags` {#mc.ilm.add.-tags}

*mc-cmd*

*Optional*

一个或多个以与号 `&` 分隔的键值对，用于描述对象标签，并据此筛选生命周期配置规则适用的对象。

此选项与以下选项互斥：

- [`--expire-delete-marker`](#mc.ilm.add.-expire-delete-marker)

##### `--expire-days` {#mc.ilm.add.-expire-days}

*mc-cmd*

*Required*

对象创建后保留的天数。 MinIO 在达到指定天数后将对象标记为待删除。 天数需指定为整数，例如 `30` 表示 30 天。

对于启用版本控制的存储桶，过期规则仅适用于 *当前* 对象版本。 使用 [`--noncurrent-expire-days`](#mc.ilm.add.-noncurrent-expire-days) 选项可将过期行为应用到非当前对象版本。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

与以下选项互斥：

- [`--expire-delete-marker`](#mc.ilm.add.-expire-delete-marker)

有关对象过期的更完整文档，请参见 [对象过期](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 和 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

##### `--expire-delete-marker` {#mc.ilm.add.-expire-delete-marker}

*mc-cmd*

*Optional*

指定此选项可让 MinIO 删除没有剩余对象版本的对象的删除标记。 具体来说，删除标记是给定对象仅剩的 *唯一*“版本”。

此选项与以下选项互斥：

- [`--tags`](#mc.ilm.add.-tags)
- [`--expire-days`](#mc.ilm.add.-expire-days)

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

有关对象过期的更完整文档，请参见 [对象过期](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-expiration) 和 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

##### `--transition-days` {#mc.ilm.add.-transition-days}

*mc-cmd*

*Optional*

从对象创建开始计算，经过多少个日历日后，MinIO 将对象标记为可过渡。 MinIO 会将对象过渡到 [`--transition-tier`](#mc.ilm.add.-transition-tier) 指定的远程层。 天数需指定为整数，例如 `30` 表示 30 天。

对于启用版本控制的存储桶，过渡规则仅适用于 *当前* 对象版本。 使用 [`--noncurrent-transition-days`](#mc.ilm.add.-noncurrent-transition-days) 选项可将过渡行为应用到非当前对象版本。

需要同时指定 [`--transition-tier`](#mc.ilm.add.-transition-tier)。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

有关对象过渡的更完整文档，请参见 [对象迁移（”Tiering”）](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering)。

##### `--transition-tier` {#mc.ilm.add.-transition-tier}

*mc-cmd*

*Optional*

MinIO 将对象 [过渡](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 到的远程层。 指定一个通过 [`mc admin tier`](/docs/reference/deprecated/mc-admin-tier/#command-mc.admin.tier) 创建的现有远程层。

如果指定了 [`--transition-days`](#mc.ilm.add.-transition-days)，则此选项为必需。

##### `--noncurrent-expire-days` {#mc.ilm.add.-noncurrent-expire-days}

*mc-cmd*

*Optional*

对象版本变为 *非当前* 后（即该对象的另一个版本现为 *HEAD*）保留的天数。 MinIO 在达到指定天数后将非当前对象版本标记为待删除。

此选项行为与 S3 `NoncurrentVersionExpiration` 动作一致。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

##### `--noncurrent-transition-days` {#mc.ilm.add.-noncurrent-transition-days}

*mc-cmd*

*Optional*

对象处于非当前状态（即被同一对象更新版本替换）多少天后，MinIO 将该对象版本标记为可过渡。 当系统主机日期时间超过该日历日期后，MinIO 会将对象过渡到 [`--transition-tier`](#mc.ilm.add.-transition-tier) 指定的远程层。

此选项对未启用版本控制的存储桶无效。 需要同时指定 [`--noncurrent-transition-tier`](#mc.ilm.add.-noncurrent-transition-tier)。

此选项行为与 S3 `NoncurrentVersionTransition` 动作一致。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

##### `--noncurrent-transition-tier` {#mc.ilm.add.-noncurrent-transition-tier}

*mc-cmd*

*Optional*

MinIO 将 [非当前对象版本过渡](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering) 到的远程层。 指定一个通过 [`mc admin tier`](/docs/reference/deprecated/mc-admin-tier/#command-mc.admin.tier) 创建的远程层。

##### `--noncurrent-expire-newer` {#mc.ilm.add.-noncurrent-expire-newer}

*mc-cmd*

*Optional*

要保留的非当前对象版本最大数量，按从新到旧排序。

使用此标志可按先进先出方式保留文件的一定数量历史版本。 在保留达到非当前版本最大数量后，MinIO 会将其余更旧的非当前对象版本标记为可过期。

下表列出了在 `--noncurrent-expire-newer 3` 下若干对象版本及其过期资格：

<table>
  <tbody>
    <tr>
      <td><p>v5 (current version)</p></td>
      <td><p>当前版本不受 ILM 规则影响。</p></td>
    </tr>
    <tr>
      <td><p>v4</p></td>
      <td><p>保留</p></td>
    </tr>
    <tr>
      <td><p>v3</p></td>
      <td><p>保留</p></td>
    </tr>
    <tr>
      <td><p>v2</p></td>
      <td><p>保留</p></td>
    </tr>
    <tr>
      <td><p>v1</p></td>
      <td><p>标记为过期</p></td>
    </tr>
  </tbody>
</table>

MinIO 保留当前版本 v5。 MinIO 还会从最新开始保留下一个 `3` 个非当前版本。 这意味着 MinIO 将 `v4`、`v3` 和 `v2` 作为要保留的三个非当前版本。

`v1` 将成为第 4 个非当前版本，超出非当前版本保留上限，因此 MinIO 会将 `v1` 标记为过期。

更新此标志的数值只会影响尚未标记的对象版本。 如果提高保留数量，已标记为过期的版本不会改变。

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据所有已配置生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 在指定天数后过期存储桶中的所有内容 {#id6}

使用 [`mc ilm add`](#command-mc.ilm.add) 和 [`--expire-days`](#mc.ilm.add.-expire-days)，可将存储桶内容标记为在对象创建后经过指定天数过期：

```shell
mc ilm add ALIAS/PATH --expire-days "DAYS"
```

- 将 [`ALIAS`](#mc.ilm.add.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ilm.add.ALIAS) 替换为该 S3 兼容主机上的存储桶路径。
- 将 [`DATE`](#mc.ilm.add.-expire-days) 替换为对象过期前的天数。 例如，指定 `30` 表示对象在创建 30 天后过期。

### 将前缀下的非当前对象版本过渡到其他层 {#id7}

将 [`mc ilm add`](#command-mc.ilm.add) 与 [`--prefix`](#mc.ilm.add.-prefix) 和 [`--transition-tier`](#mc.ilm.add.-transition-tier) 配合使用，可将对象较旧的非当前版本过渡到不同的存储层。

```shell
mc ilm add --prefix "doc/" --transition-days "90" --trasition-tier "MINIOTIER-1"                  \
       --noncurrent-transition-days "45" --noncurrent-transition-tier "MINIOTIER-2"  \
       myminio/mybucket/
```

该命令会检查 `myminio` 部署中 `mybucket` 存储桶内带 `doc/` 前缀的内容。

- 前缀中超过 90 天的当前对象会移动到 `MINIOTIER-1` 存储层。
- 前缀中超过 45 天的非当前对象会移动到 `MINIOTIER-2` 存储层。
- `MINIOTIER-1` 和 `MINIOTIER-2` 均已通过 [`mc admin tier add`](/docs/reference/deprecated/mc-admin-tier/#mc.admin.tier.add) 创建。

### 在前缀下过期所有对象，并让当前对象版本比非当前对象版本保留更久 {#id8}

将 [`mc ilm add`](#command-mc.ilm.add) 命令与 [`--prefix`](#mc.ilm.add.-prefix)、[`--expire-days`](#mc.ilm.add.-expire-days) 和 [`--noncurrent-expire-days`](#mc.ilm.add.-noncurrent-expire-days) 配合使用，可让对象的当前版本与非当前版本在不同时间过期。

```shell
mc ilm add --prefix "doc/" --expire-days "300" --noncurrent-expire-days "100" myminio/mybucket/
```

该命令会检查 `myminio` 部署中 `mybucket` 存储桶内带 `doc/` 前缀的内容。

- 当前对象在 300 天后过期。
- 非当前对象在 100 天后过期。

## 行为 {#id9}

### 生命周期管理对象扫描器 {#id10}

MinIO 使用 [scanner process](/docs/operations/concepts/scanner/#minio-concepts-scanner) 根据已配置的生命周期管理规则检查对象。 高 IO 负载或系统资源受限导致的慢速扫描可能会延迟生命周期管理规则的生效。 参见 [生命周期管理对象扫描器](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 了解更多信息。

### 过期与过渡 {#id11}

MinIO 支持在同一个存储桶或存储桶前缀中同时指定过期和过渡规则。 无论对象的过渡状态如何，MinIO 都可以对其执行过期规则。 使用 [`mc ilm ls`](/docs/reference/deprecated/mc-ilm-ls/#command-mc.ilm.ls) 查看当前配置的对象生命周期管理规则， 以评估过期规则与过渡规则之间可能存在的相互影响。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。