---
title: "mc ilm rule rm"

weight: 60
---

<a id="mc-ilm-rule-rm"></a>
<a id="minio-mc-ilm-rule-rm"></a>

<a id="command-mc.ilm.rule.rm"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm rule rm` 替代 `mc ilm rm`。

## 语法 {#id2}

[`mc ilm rule rm`](#command-mc.ilm.rule.rm) 命令用于从 MinIO 存储桶中删除一条对象生命周期管理规则。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `myminio` MinIO 部署的 `mydata` 存储桶中删除一条生命周期管理规则：

```shell
mc ilm rule rm --id "bgrt1ghju" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] ilm rule rm                         \
                     --id "string" | (--all --force) \
                     ALIAS                           \
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.rule.rm.ALIAS}

*mc-cmd*

*Required*

要删除对象生命周期管理规则的 MinIO 部署上存储桶的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整路径。 例如：

```text
mc ilm rule rm myminio/mydata
```

##### `--all` {#mc.ilm.rule.rm.-all}

*mc-cmd*

*Optional*

删除存储桶中的所有规则。 需要同时包含 [`--force`](#mc.ilm.rule.rm.-force)。

与 [`--id`](#mc.ilm.rule.rm.-id) 互斥。

##### `--force` {#mc.ilm.rule.rm.-force}

*mc-cmd*

*Optional*

指定 [`--all`](#mc.ilm.rule.rm.-all) 时必需。

##### `--id` {#mc.ilm.rule.rm.-id}

*mc-cmd*

*Optional*

规则的唯一 ID。 使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 列出存储桶规则，并获取要删除规则的 `id`。

与 [`mc ilm rule rm --all`](#mc.ilm.rule.rm.-all) 互斥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 删除存储桶生命周期管理规则 {#id6}

使用 [`mc ilm rule rm`](#command-mc.ilm.rule.rm) 删除存储桶生命周期管理规则：

```shell
mc ilm rule rm --id "RULE" ALIAS/PATH
```

- 将 `RULE` 替换为生命周期管理规则的唯一标识符。 使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 查找要使用的 ID。
- 将 [`ALIAS`](#mc.ilm.rule.rm.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上存储桶的路径。

## 所需权限 {#id7}

有关删除规则所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-rule/#minio-mc-ilm-rule-permissions)。

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。