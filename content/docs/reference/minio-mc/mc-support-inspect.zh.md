---
title: "mc support inspect"

weight: 30
---

<a id="mc-support-inspect"></a>

<a id="command-mc.support.inspect"></a>

> [!NOTE]
> **需要完成 SUBNET 注册**
>
> `mc support` 命令面向已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的 MinIO 部署设计，以确保诊断和 性能测试获得最佳结果。 未注册 SUBNET 的部署无法使用 `mc support` 命令。

## 描述 {#id2}

[`mc support inspect`](#command-mc.support.inspect) 命令会收集指定路径下与对象相关的数据和元数据。

对于每个指定对象，MinIO 会从存储其 [纠删码分片](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 的各个后端驱动器汇总这些数据。 该命令会生成一个加密 zip 文件，其中包含所有匹配文件及其对应的 *host+drive+path*。

如果诊断 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 问题需要这些信息，MinIO Engineering 会提供相应命令。 生成的报告用于 MinIO Engineering 通过 SUBNET 进行分析，且可能包含与对象相关的内部或私有数据点。 将报告发送给第三方或发布到公共论坛前请谨慎评估。

> [!NOTE]
> **变更: RELEASE.2023-01-11T03-14-16Z**
>
> 该文件会上传到 MinIO，供工程团队用于支持工作。 如果文件上传失败（例如在 airgapped 环境中），则会保存到当前工作目录。

> [!NOTE]
> **变更: RELEASE.2022-12-12T19-27-27Z**
>
> 在写入 zip 归档时，MinIO 还会对归档内文件名的 zip 索引进行加密。

> [!NOTE]
> **变更: RELEASE.2024-10-29T15-34-59Z**
>
> Inspect 现在会生成唯一文件名，以区分不同的 inspect 文件。 文件名会体现被检查的路径。

> [!WARNING]
> **重要**
>
> [`mc support inspect`](#command-mc.support.inspect) 要求 MinIO 部署端服务版本为 2021 年 10 月或之后。

## 通配符 {#id3}

使用 Bash shell 时，该命令支持对前缀或对象进行通配符 `*` 模式匹配。 对于非 Bash shell，会显示提示消息，说明通配符模式仅在 Bash 中受支持。

```shell
mc support inspect ALIAS/bucket/path/**/xl.meta
```

该命令会收集 `ALIAS/bucket/path/` 下与对象相关的所有 `xl.meta`。

## 示例 {#id4}

### 下载对象元数据 {#id5}

可下载某个对象的元数据。 元数据存储在 `xl.meta` 二进制文件中。

以下命令从 `minio1` 部署中的 `mybucket/myobject` 下载 `xl.meta`。

该文件会从所有驱动器下载，并打包为 zip 归档文件。

```shell
mc support inspect minio1/mybucket/myobject/xl.meta
```

`xl.meta` 文件内容不可直接人工阅读。 可将 `xl.meta` 文件内容转换为 JSON 格式。

### 递归下载某个前缀下的所有对象 {#id6}

以下命令会递归下载某个前缀下找到的所有对象。

> [!CAUTION]
> **注意**
>
> 该操作的开销可能较高。 请谨慎执行。

```shell
mc support inspect minio1/mybucket/myobject/**
```

## 语法 {#id7}

该命令语法如下：

```shell
mc [GLOBALFLAGS] support inspect       \
                         [--legacy]   \
                         TARGET
```

### 参数 {#id8}

##### `--legacy` {#mc.support.inspect.-legacy}

*mc-cmd*

*Optional*

使用旧版检查数据导出方式，该方式默认不加密数据。

##### `TARGET` {#mc.support.inspect.TARGET}

*mc-cmd*

*Required*

要检查的位置或对象路径。 该路径应包含 MinIO 部署的 *alias &lt;alias&gt;*，并在需要时包含前缀和/或对象名称。

### 全局标志 {#id9}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。