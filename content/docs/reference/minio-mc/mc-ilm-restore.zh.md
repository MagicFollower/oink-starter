---
title: "mc ilm restore"

weight: 10
---

<a id="mc-ilm-restore"></a>
<a id="minio-mc-ilm-restore"></a>

<a id="command-mc.ilm.restore"></a>

## 语法 {#id1}

[`mc ilm restore`](#command-mc.ilm.restore) 命令会为归档在远程层上的对象创建一个临时副本。 默认情况下，该副本会在 1 天后自动过期。

使用此命令可让应用程序通过 MinIO 部署访问分层对象（例如“热层”）。 归档对象会保留在远程层，而临时副本会成为该对象的 `HEAD`。

> [!NOTE]
> **新增: mc**
>
> RELEASE.2023-04-12T02-21-51Z
>
> 使用 [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat) 可显示已恢复对象是从本地临时副本读取还是从远程层读取。 当前正在从远程层恢复的对象会显示状态 `Ongoing : true`。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将远程层上一个已转储对象的副本恢复到 `myminio` MinIO 部署：

```shell
mc ilm restore myminio/mybucket/object.txt
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] ilm restore         \
                 [--days "int" ]     \
                 [--recursive]       \
                 [--vid "string"]    \
                 [--versions]        \
                 [--enc-c "string"]  \
                 ALIAS
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.ilm.restore.ALIAS}

*mc-cmd*

*Required*

要恢复的归档对象对应的 MinIO [alias](/docs/reference/minio-mc/mc-alias-set/#alias)、存储桶和路径。

```shell
mc ilm restore myminio/mybucket/object.txt
```

##### `--days` {#mc.ilm.restore.-days}

*mc-cmd*

*Optional*

MinIO 使已恢复归档对象副本过期前的天数。

##### `--enc-c` {#mc.ilm.restore.-enc-c}

*mc-cmd*

*Optional*

使用客户端管理的密钥，通过服务端 [SSE-C 加密](/docs/administration/server-side-encryption/#minio-sse) 对对象进行加密或解密。

该参数接受格式为 `KEY=VALUE` 的键值对。

<table>
  <tbody>
    <tr>
      <td><p><code>KEY</code></p></td>
      <td><p>对象的完整路径，格式为 <code>alias/bucket/path/object.ext</code>。</p><p>你也可以只指定顶层路径，以便对该路径下的所有操作使用同一个加密密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>VALUE</code></p></td>
      <td><p>指定用于 SSE-C 加密的密钥，可以是 32 字节 RawBase64 编码密钥，
<em>也可以是</em> 64 字节十六进制编码密钥。</p><p>Raw Base64 编码 <strong>不接受</strong> 带 <code>=</code> 填充的密钥。
请去掉填充，或使用支持 RAW 格式的 Base64 编码器。</p></td>
    </tr>
  </tbody>
</table>

- `KEY` - 对象的完整路径，格式为 `alias/bucket/path/object`。
- `VALUE` - 用于加密对象的 32 字节 RAW Base64 编码数据密钥。

例如：

```shell
# RawBase64-Encoded string "mybucket32byteencryptionkeyssec"
--enc-c "myminio/mybucket/prefix/object.obj=bXlidWNrZXQzMmJ5dGVlbmNyeXB0aW9ua2V5c3NlYwo"
```

你可以通过重复该参数来指定多个加密密钥。

也可以指定某个前缀路径，对该路径下所有匹配对象应用加密：

```shell
--enc-c "myminio/mybucket/prefix/=bXlidWNrZXQzMmJ5dGVlbmNyeXB0aW9ua2V5c3NlYwo"
```

> [!NOTE]
> **说明**
>
> MinIO 强烈不建议在生产负载中使用 SSE-C 加密。 请改用 `--enc-kms` 参数启用 SSE-KMS，或使用 `--enc-s3` 参数启用 SSE-S3。

##### `--recursive, r` {#mc.ilm.restore.-recursive}

*mc-cmd*

*Optional*

恢复指定前缀下的所有对象。

##### `--versions` {#mc.ilm.restore.-versions}

*mc-cmd*

*Optional*

恢复远程层上该对象的所有版本。

##### `--version-id, vid` {#mc.ilm.restore.-version-id}

*mc-cmd*

*Optional*

恢复远程层上该对象的指定版本。

### 全局参数 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 恢复归档对象 {#id5}

以下命令恢复一个已归档到远程层的对象：

```shell
mc ilm restore myminio/mybucket/object.txt
```

### 恢复指定版本的归档对象 {#id6}

以下命令恢复一个已归档到远程层的指定对象版本：

```shell
mc ilm restore --vid "VERSIONID" myminio/mybucket/object.txt
```

### 恢复存储桶前缀下的所有归档对象 {#id7}

以下命令恢复远程层上指定前缀下归档的所有对象：

```shell
mc ilm restore --recursive myminio/mybucket/data/
```

## 行为 {#id8}

### 已恢复对象自动过期 {#id9}

MinIO 会在指定天数后自动使已恢复对象副本过期（默认：1 天）。

### 已恢复对象会成为 HEAD {#head}

无论该对象命名空间的版本控制历史如何，已恢复的对象副本都会成为 HEAD。 在本地副本存在期间，这可能导致应用程序返回“过时”数据。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。