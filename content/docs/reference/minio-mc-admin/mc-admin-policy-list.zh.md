---
title: "mc admin policy ls"

weight: 60
---

<a id="mc-admin-policy-ls"></a>

<a id="command-mc.admin.policy.ls"></a>

<a id="command-mc.admin.policy.list"></a>

## 语法 {#id2}

列出目标 MinIO 部署上的所有策略。

[`mc admin policy list`](#command-mc.admin.policy.list) 命令与 [`mc admin policy ls`](#command-mc.admin.policy.ls) 具有等效功能。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `play` 上当前存在的策略列表。

```shell
mc admin policy ls play
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc admin policy ls TARGET
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

[`mc admin policy ls`](#command-mc.admin.policy.ls) 命令接受以下参数：

##### `TARGET` {#mc.admin.policy.list.TARGET}

*mc-cmd*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，命令将从该部署列出可用策略。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

列出别名为 `myminio` 的部署上存在的策略。

```shell
mc admin policy ls myminio
```

### 输出 {#id6}

该命令返回的输出类似如下：

```shell
readwrite
writeonly
```