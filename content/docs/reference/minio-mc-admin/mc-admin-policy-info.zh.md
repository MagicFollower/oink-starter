---
title: "mc admin policy info"

weight: 50
---

<a id="mc-admin-policy-info"></a>

<a id="command-mc.admin.policy.info"></a>

## 语法 {#id2}

如果目标 MinIO 部署上存在指定策略，则以 JSON 格式返回该策略。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令显示 [alias](/zh/glossary/#term-alias) `myminio` 上 `writeonly` 策略的内容。

```shell
 mc admin policy info myminio writeonly
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc admin policy info TARGET POLICYNAME
                     [--policy-file, -f <path>]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

[`mc admin policy info`](#command-mc.admin.policy.info) 命令接受以下参数：

##### `TARGET` {#mc.admin.policy.info.TARGET}

*mc-cmd*

*Required*

已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)，用于显示指定策略。

##### `POLICYNAME` {#mc.admin.policy.info.POLICYNAME}

*mc-cmd*

*Required*

要显示其详细信息的策略名称。

##### `--policy-file` {#mc.admin.policy.info.-policy-file}

*mc-cmd*

*Optional*

指定一个文件路径，用于写入指定策略的 JSON 内容。 如果该路径已存在，命令会用指定策略的内容覆盖已有文件。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

显示 [alias](/zh/glossary/#term-alias) `myminio` 上 `writeonly` 策略的内容。

```shell
mc admin policy info myminio writeonly
```

显示指定策略的信息，并将策略 JSON 内容写入 /tmp/policy.json。

```shell
mc admin policy info myminio writeonly --policy-file /tmp/policy.json
```

### 输出 {#id6}

该命令返回的输出类似如下：

```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
            "s3:PutObject"
         ],
         "Resource": [
            "arn:aws:s3:::*"
         ]
      }
   ]
}
```