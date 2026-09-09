---
title: "mc ilm ls"

weight: 50
---

<a id="mc-ilm-ls"></a>
<a id="minio-mc-ilm-ls"></a>

<a id="command-mc.ilm.ls"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm ls` 已由 [`mc ilm rule ls`](/docs/reference/minio-mc/mc-ilm-rule-ls/#command-mc.ilm.rule.ls) 替代。

## 语法 {#id2}

[`mc ilm ls`](#command-mc.ilm.ls) 命令以表格形式汇总 MinIO 存储桶上已配置的所有对象生命周期管理规则。

该命令的输出可能如下所示：

```shell
┌───────────────────────────────────────────────────────────────────────────────┐
│ Transition for latest version (Transition)                                    │
├────────┬─────────┬────────┬─────────────────────┬──────────────┬──────────────┤
│ ID     │ STATUS  │ PREFIX │ TAGS                │ DAYS TO TIER │ TIER         │
├────────┼─────────┼────────┼─────────────────────┼──────────────┼──────────────┤
│ rule-1 │ Enabled │ doc/   │ key1=val1&key2=val2 │            0 │ WARM-MINIO-1 │
└────────┴─────────┴────────┴─────────────────────┴──────────────┴──────────────┘
┌────────────────────────────────────────────────────────────────┐
│ Transition for older versions (NoncurrentVersionTransition)    │
├────────┬─────────┬────────┬──────┬──────────────┬──────────────┤
│ ID     │ STATUS  │ PREFIX │ TAGS │ DAYS TO TIER │ TIER         │
├────────┼─────────┼────────┼──────┼──────────────┼──────────────┤
│ rule-2 │ Enabled │ logs/  │ -    │           10 │ WARM-MINIO-1 │
└────────┴─────────┴────────┴──────┴──────────────┴──────────────┘
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Expiration for latest version (Expiration)                                             │
├────────┬─────────┬────────┬─────────────────────┬────────────────┬─────────────────────┤
│ ID     │ STATUS  │ PREFIX │ TAGS                │ DAYS TO EXPIRE │ EXPIRE DELETEMARKER │
├────────┼─────────┼────────┼─────────────────────┼────────────────┼─────────────────────┤
│ rule-1 │ Enabled │ doc/   │ key1=val1&key2=val2 │             30 │ false               │
└────────┴─────────┴────────┴─────────────────────┴────────────────┴─────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Expiration for older versions (NoncurrentVersionExpiration)                      │
├────────┬─────────┬────────┬─────────────────────┬────────────────┬───────────────┤
│ ID     │ STATUS  │ PREFIX │ TAGS                │ DAYS TO EXPIRE │ KEEP VERSIONS │
├────────┼─────────┼────────┼─────────────────────┼────────────────┼───────────────┤
│ rule-1 │ Enabled │ doc/   │ key1=val1&key2=val2 │             15 │             0 │
│ rule-2 │ Enabled │ logs/  │ -                   │              1 │             3 │
└────────┴─────────┴────────┴─────────────────────┴────────────────┴───────────────┘
```

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶的所有生命周期管理规则：

```shell
mc ilm ls myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
[`mc ilm ls`](#command-mc.ilm.ls) 命令的语法如下：

```shell
mc [GLOBALFLAGS] ilm ls                        \
                 [--expiry | --transition]     \
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.ls.ALIAS}

*mc-cmd*

*Required*

用于指定要列出对象生命周期管理规则的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和存储桶完整路径。例如：

```text
mc ilm ls myminio/mydata
```

##### `--expiry` {#mc.ilm.ls.-expiry}

*mc-cmd*

*Optional*

[`mc ilm ls`](#command-mc.ilm.ls) 仅返回与生命周期规则过期相关的字段。

与 [`--transition`](#mc.ilm.ls.-transition) 互斥。

##### `--transition` {#mc.ilm.ls.-transition}

*mc-cmd*

*Optional*

[`mc ilm ls`](#command-mc.ilm.ls) 仅返回与生命周期规则转换相关的字段。

与 [`--expiry`](#mc.ilm.ls.-expiry) 互斥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出存储桶生命周期管理规则 {#id6}

使用 [`mc ilm ls`](#command-mc.ilm.ls) 列出存储桶的生命周期管理规则：

```shell
mc ilm ls ALIAS/PATH
```

- 将 [`ALIAS`](#mc.ilm.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.ilm.ls.ALIAS) 替换为 S3 兼容主机上存储桶的路径。

## 行为 {#id7}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。