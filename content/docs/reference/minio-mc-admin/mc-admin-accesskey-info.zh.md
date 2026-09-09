---
title: "mc admin accesskey info"

weight: 50
---

<a id="mc-admin-accesskey-info"></a>
<a id="minio-mc-admin-accesskey-info"></a>

<a id="command-mc.admin.accesskey.info"></a>

## 语法 {#id1}

[`mc admin accesskey info`](#command-mc.admin.accesskey.info) 命令返回指定 [access key(s)](/docs/administration/identity-access-management/minio-user-management/#minio-id-access-keys) 的描述信息。

描述输出会在可用时包含以下详细信息：

- Access Key
- 指定访问密钥的父用户
- 访问密钥状态（`on` 或 `off`）
- 策略（单个或多个）
- 注释
- 过期时间

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令返回指定访问密钥的信息：

```shell
mc admin accesskey info myminio myuseraccesskey
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] admin accesskey info      \
                                 ALIAS     \
                                 ACCESSKEY
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.admin.accesskey.info.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

##### `ACCESSKEY` {#mc.admin.accesskey.info.ACCESSKEY}

*mc-cmd*

*Required*

要显示的访问密钥。

通过空格分隔多个访问密钥，可返回多个访问密钥的信息。

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 显示访问密钥详细信息 {#id5}

使用 [`mc admin accesskey info`](#command-mc.admin.accesskey.info) 显示 MinIO 部署中某个访问密钥的详细信息：

```shell
   mc admin accesskey info myminio myaccesskey
```

- 将 `myminio` 替换为 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`myaccesskey`](/docs/reference/minio-mc-admin/mc-admin-user-svcacct-info/#mc.admin.user.svcacct.info.ACCESSKEY) 替换为要显示信息的访问密钥。 如需列出多个密钥，请使用空格分隔。

输出类似如下：

```shell
AccessKey: myuserserviceaccount
ParentUser: myuser
Status: on
Comment:
Policy: implied
Expiration: no-expiry
```

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。