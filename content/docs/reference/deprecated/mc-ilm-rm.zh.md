---
title: "mc ilm rm"

weight: 60
---

<a id="mc-ilm-rm"></a>
<a id="minio-mc-ilm-rm"></a>

<a id="command-mc.ilm.remove"></a>

<a id="command-mc.ilm.rm"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm rm` 已被 [`mc ilm rule rm`](/docs/reference/minio-mc/mc-ilm-rule-rm/#command-mc.ilm.rule.rm) 取代。

## 语法 {#id2}

[`mc ilm rm`](#command-mc.ilm.rm) 命令用于从 MinIO 存储桶中移除一条对象生命周期管理规则。

[`mc ilm remove`](#command-mc.ilm.remove) 命令与 [`mc ilm rm`](#command-mc.ilm.rm) 的功能等效。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `myminio` MinIO 部署的 `mydata` 存储桶中移除一条生命周期管理规则：

```shell
mc ilm rm --id "bgrt1ghju" myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] ilm rm                          \
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

##### `ALIAS` {#mc.ilm.rm.ALIAS}

*mc-cmd*

*Required* 要移除对象生命周期管理规则的 MinIO 部署中， [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 与存储桶完整路径。例如：

```text
mc ilm rm myminio/mydata
```

##### `all` {#mc.ilm.rm.all}

*mc-cmd*

*Required* 移除该存储桶中的所有规则。与 [`mc ilm rm id`](#mc.ilm.rm.id) 互斥。

与 [`mc ilm rm id`](#mc.ilm.rm.id) 互斥。

需要同时包含 [`force`](#mc.ilm.rm.force)。

##### `force` {#mc.ilm.rm.force}

*mc-cmd*

当指定 [`all`](#mc.ilm.rm.all) 时必需。

##### `id` {#mc.ilm.rm.id}

*mc-cmd*

*Required* 规则的唯一 ID。使用 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 列出存储桶规则， 并获取要移除规则的 `id`。

与 [`mc ilm rm all`](#mc.ilm.rm.all) 互斥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 移除存储桶生命周期管理规则 {#id6}

使用 [`mc ilm rm`](#command-mc.ilm.rm) 移除一条存储桶生命周期管理规则：

```shell
mc ilm rm --id "RULE" ALIAS/PATH
```

- 将 [`RULE`](#mc.ilm.rm.id) 替换为生命周期管理规则的唯一名称。
- 将 [`ALIAS`](#mc.ilm.rm.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ilm.rm.ALIAS) 替换为 S3 兼容主机上的存储桶路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。