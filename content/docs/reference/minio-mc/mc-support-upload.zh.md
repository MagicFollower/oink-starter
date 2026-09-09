---
title: "mc support upload"

weight: 80
---

<a id="mc-support-upload"></a>

<a id="command-mc.support.upload"></a>

## Description {#description}

[`mc support upload`](#command-mc.support.upload) 将文件从本地文件系统复制到 SUBNET 工单。

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## Syntax {#syntax}

[`mc support profile`](/docs/reference/minio-mc/mc-support-profile/#command-mc.support.profile) 命令具有以下语法：

```shell
mc [GLOBALFLAGS] support profile              \
                         ALIAS                \
                         FILE                 \
                         [--comment "string"] \
                         [--enc]              \
                         [--issue integer]
```

### Parameters {#parameters}

##### `ALIAS` {#mc.support.upload.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `FILE` {#mc.support.upload.FILE}

*mc-cmd*

*Required*

要上传到 SUBNET 的文件路径。

##### `--comment` {#mc.support.upload.-comment}

*mc-cmd*

*Optional*

上传文件时，向 issue 附加一条消息。

##### `--enc` {#mc.support.upload.-enc}

*mc-cmd*

*Optional*

对上传内容进行加密。 用于加密的密钥仅 MinIO 可访问。

##### `--issue` {#mc.support.upload.-issue}

*mc-cmd*

*Optional*

指定要添加该文件的 issue 编号。 如果未指定，则文件会上传到通用 issue 编号 `0`。

### Global Flags {#global-flags}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## Examples {#examples}

### Upload a file to an issue {#upload-a-file-to-an-issue}

此命令将本地文件系统中的文件 `./trace.log` 上传到别名为 `minio1` 的部署对应的 SUBNET issue `10001`。

```shell
mc support upload --issue 10001 minio1 ./trace.log
```

### Upload a file to an issue with a comment for MinIO Engineers {#upload-a-file-to-an-issue-with-a-comment-for-minio-engineers}

此命令将本地文件系统中的文件 `./trace.log` 上传到别名为 `minio1` 的部署对应的 SUBNET issue `10001`。 该命令还会附加一条关于该文件的注释，供 MinIO Engineers 查看。

```shell
mc support upload --issue 10001 --comment "here is the requested trace log" minio1 ./trace.log
```