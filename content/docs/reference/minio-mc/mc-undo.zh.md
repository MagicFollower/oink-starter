---
title: "mc undo"

weight: 410
---

<a id="mc-undo"></a>
<a id="minio-mc-undo"></a>

<a id="command-mc.undo"></a>

## 语法 {#id2}

[`mc undo`](#command-mc.undo) 命令用于撤销指定路径上由 `PUT` 或 `DELETE` 操作引起的更改。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会回滚 `myminio` 部署中 `data` 存储桶内 `file.zip` 对象最近三次上传和/或删除操作：

```shell
mc undo myminio/data/file.zip --last 3
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] undo                \
                 TARGET              \
                 [--action "type"]   \
                 [--force]           \
                 [--last "integer"]  \
                 [--recursive, r]    \
                 [--dry-run]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `TARGET` {#mc.undo.TARGET}

*mc-cmd*

*Required*

命令应执行的对象或前缀的完整路径。 路径必须包含 [ALIAS](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias)、存储桶以及前缀或对象名称。

##### `--action` {#mc.undo.-action}

*mc-cmd*

*Optional*

撤销指定类型的最近一次更改。 可接受的值为 `DELETE` 或 `PUT`。

默认情况下，[`mc undo`](#command-mc.undo) 会同时回滚 `DELETE` 和 `PUT` 操作。 使用 [`--action`](#mc.undo.-action) 可在两者中选择其一，但仅针对该类型最近的一次操作。

以下命令会回滚 `data` 存储桶中对象 `today.zip` 最近一次 `PUT`，恢复到该对象的上一版本：

```shell
mc undo myminio/data/today.zip --action "PUT"
```

以下示例会回滚前缀 `archive` 最近一次 `DELETE`，并递归恢复该前缀及其所有子对象：

```shell
mc undo myminio/data/archive --recursive --action "DELETE"
```

与 [`--last`](#mc.undo.-last) 互斥。

##### `--dry-run` {#mc.undo.-dry-run}

*mc-cmd*

*Optional*

输出命令结果，但不实际执行操作。 使用此标志可测试按特定方式运行命令时的结果。

##### `--force` {#mc.undo.-force}

*mc-cmd*

*Optional*

强制执行递归操作。

##### `--last` {#mc.undo.-last}

*mc-cmd*

*Optional*

接受一个整数值，用于指定要撤销的 `PUT` 和/或 `DELETE` 更改次数。

若未指定，命令默认回滚一次（`1`）操作。 与 [`--action`](#mc.undo.-action) 互斥。

##### `--recursive, r` {#mc.undo.-recursive}

*mc-cmd*

*Optional*

以递归方式执行命令。 例如，可使用此标志撤销某个前缀上的更改。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 撤销对象最近三次上传或删除 {#id6}

以下命令会回滚 `myminio` 部署中 `data` 存储桶内 `file.zip` 对象最近三次上传和/或删除操作：

```shell
mc undo myminio/data/file.zip --last 3
```

### 撤销某个前缀下任意对象最近一次上传或删除 {#id7}

使用 [`mc undo`](#command-mc.undo) 回滚在 `myminio` 别名下、`data` 存储桶中 `presentations/recordings/` [prefix](/zh/glossary/#term-prefix) 内最近一次 `PUT` 或 `DELETE` 操作：

```shell
mc undo myminio/data/presentations/recordings/ --recursive --force
```

## 行为 {#id8}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。