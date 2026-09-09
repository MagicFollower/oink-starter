---
title: "mc ilm rule ls"

weight: 50
---

<a id="mc-ilm-rule-ls"></a>
<a id="minio-mc-ilm-rule-ls"></a>

<a id="command-mc.ilm.rule.list"></a>

<a id="command-mc.ilm.rule.ls"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-24T15-21-38Z**
>
> `mc ilm rule ls` 替代了 `mc ilm ls`。

> [!NOTE]
> **变更: RELEASE.2023-05-26T23-31-54Z**
>
> `mc ilm rule ls --json` 的输出在 `updateAt` 中包含策略修改时间。

## 语法 {#id2}

[`mc ilm rule ls`](#command-mc.ilm.rule.ls) 命令以表格格式汇总 MinIO 存储桶上配置的所有对象生命周期管理规则。

[`mc ilm rule list`](#command-mc.ilm.rule.list) 命令与 [`mc ilm rule ls`](#command-mc.ilm.rule.ls) 的功能等效。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令列出 `myminio` MinIO 部署中 `mydata` 存储桶的所有生命周期管理规则：

```shell
mc ilm rule ls myminio/mydata
```

命令输出可能类似如下：

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
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
[`mc ilm rule ls`](#command-mc.ilm.rule.ls) 命令语法如下：

```shell
mc [GLOBALFLAGS] ilm rule ls     \
                 [--expiry]      \
                 [--transition]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.ilm.rule.ls.ALIAS}

*mc-cmd*

*Required*

要列出对象生命周期管理规则的 MinIO 部署中，存储桶对应的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 和完整路径。 例如：

```text
mc ilm rule ls myminio/mydata
```

##### `--expiry` {#mc.ilm.rule.ls.-expiry}

*mc-cmd*

*Optional*

[`mc ilm rule ls`](#command-mc.ilm.rule.ls) 仅返回与生命周期规则过期相关的字段。

与 [`--transition`](#mc.ilm.rule.ls.-transition) 互斥。

##### `--transition` {#mc.ilm.rule.ls.-transition}

*mc-cmd*

*Optional*

[`mc ilm rule ls`](#command-mc.ilm.rule.ls) 仅返回与生命周期规则转移相关的字段。

与 [`--expiry`](#mc.ilm.rule.ls.-expiry) 互斥。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 列出存储桶生命周期管理规则 {#id6}

使用 [`mc ilm rule ls`](#command-mc.ilm.rule.ls) 列出存储桶的生命周期管理规则：

```shell
mc ilm rule ls ALIAS/PATH
```

- 将 [`ALIAS`](#mc.ilm.rule.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上该存储桶的路径。

### 显示策略修改时间 {#id7}

使用带有 `--json` 的 [`mc ilm rule ls`](#command-mc.ilm.rule.ls) 显示存储桶策略上次更新时间。

```shell
mc ilm rule ls ALIAS/PATH --json
```

- 将 [`ALIAS`](#mc.ilm.rule.ls.ALIAS) 替换为 S3 兼容主机的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `PATH` 替换为 S3 兼容主机上该存储桶的路径。

JSON 输出中的 `updateAt` 属性包含该策略更新的日期和时间。

输出类似如下：

```shell
{
 "status": "success",
 "target": "myminio/mybucket",
 "config": {
  "Rules": [
   {
    "Expiration": {
     "Days": 30
    },
    "ID": "ci1o2mg0sko6f1r3krv0",
    "Status": "Enabled"
   }
  ]
 },
 "updatedAt": "2023-06-09T19:45:30Z"
}
```

## 所需权限 {#id8}

有关列出规则所需的权限，请参阅父命令中的 [required permissions](/docs/reference/minio-mc/mc-ilm-rule/#minio-mc-ilm-rule-permissions)。

## 行为 {#id9}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。