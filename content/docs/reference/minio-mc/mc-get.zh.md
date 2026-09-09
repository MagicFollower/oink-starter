---
title: "mc get"

weight: 120
---

<a id="mc-get"></a>

<a id="command-mc.get"></a>

> [!NOTE]
> **新增: mc**
>
> RELEASE.2024-02-24T01-33-20Z

## 语法 {#id2}

[`mc get`](#command-mc.get) 命令将对象从目标 S3 部署下载到本地文件系统。

与 [`mc cp`](/docs/reference/minio-mc/mc-cp/#command-mc.cp) 或 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror) 相比，`mc get` 为下载文件提供了更简化的接口。 `mc get` 使用单向下载功能，以牺牲效率为代价，换取相较其他命令更低的功能复杂度。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令将文件 `logo.png` 从 s3 源下载到本地文件系统路径 `~/images/collateral/`。

```shell
mc get minio/marketing/logo.png ~/images/collateral
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] get                      \
                 SOURCE                   \
                 TARGET                   \
                 [--enc-c string]         \
                 [--version-id, --vid value]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `SOURCE` {#mc.get.SOURCE}

*mc-cmd*

*Required*

要下载对象的完整路径，包含 [alias](/docs/reference/minio-mc/mc-alias-set/#minio-mc-alias)、存储桶、prefix（如使用）和对象名。

##### `TARGET` {#mc.get.TARGET}

*mc-cmd*

*Required*

本地文件系统上的目标路径，命令会将下载的文件放置到该路径。

##### `--enc-c` {#mc.get.-enc-c}

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

##### `--version-id, --vid` {#mc.get.-version-id}

*mc-cmd*

*Optional*

检索对象的特定版本。 传入要检索对象的版本 ID。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id5}

### 从 MinIO 检索对象到本地文件系统 {#minio}

以下命令从别名 `myminio` 下的存储桶 `mybucket` 检索文件 `myobject.csv`，并将其放置到本地文件系统路径 `/my/local/folder`。

```shell
mc get myminio/mybucket/myobject.csv /my/local/folder
```

### 从 MinIO 检索加密对象 {#id6}

以下命令检索一个加密文件，并将其放置到本地文件夹路径。

```shell
mc get --enc-c "play/mybucket/object=MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDA" play/mybucket/object path-to/object
```