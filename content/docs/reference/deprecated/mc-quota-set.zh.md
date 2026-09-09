---
title: "mc quota set"

weight: 30
---

<a id="mc-quota-set"></a>

<a id="command-mc.quota.set"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-13T00-23-28Z**
>
> `mc quota set` 替代了 `mc admin bucket quota --hard`。

> [!NOTE]
> **变更: RELEASE.2024-07-31T15-58-33Z**
>
> `mc quota set` 已弃用。

## 说明 {#id2}

[`mc quota set`](#command-mc.quota.set) 为存储桶分配硬配额限制，超过该限制后 MinIO 不再允许写入。

### 计量单位 {#id3}

[`mc quota set --size`](#mc.quota.set.-size) 标志接受以下 **不区分大小写** 的后缀，用于表示指定大小值的单位：

| 后缀 | 单位大小 |
| --- | --- |
| `k` | KB（Kilobyte，1000 Bytes） |
| `m` | MB（Megabyte，1000 Kilobytes） |
| `g` | GB（Gigabyte，1000 Megabytes） |
| `t` | TB（Terabyte，1000 Gigabytes） |
| `ki` or `kib` | KiB（Kibibyte，1024 Bites） |
| `mi` or `mib` | MiB（Mebibyte，1024 Kibibytes） |
| `gi` or `gib` | GiB（Gibibyte，1024 Mebibytes） |
| `ti` or `tib` | TiB（Tebibyte，1024 Gibibytes） |

如果省略后缀，则默认使用 `bytes`。

## 示例 {#id4}

### 为存储桶配置硬配额 {#id5}

将 [`mc quota set`](#command-mc.quota.set) 与 [`--size`](#mc.quota.set.-size) 标志配合使用，可为存储桶指定硬配额。 硬配额可防止存储桶大小增长到超出指定限制。

```shell
mc quota set TARGET/BUCKET --size LIMIT
```

- 将 `TARGET` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为要设置硬配额的存储桶名称。
- 将 `LIMIT` 替换为存储桶可增长到的最大大小（整数），并可按需附加后缀。 例如，要设置 10 Terabytes 的硬限制，请指定 `10t`。

## 语法 {#id6}

[`mc quota set`](#command-mc.quota.set) 的语法如下：

```shell
mc quota set TARGET --size LIMIT
```

[`mc quota set`](#command-mc.quota.set) 支持以下参数：

#### `TARGET` {#mc.quota.set.TARGET}

*mc-cmd*

*Required*

要为其创建配额的存储桶完整路径。 在路径前缀中指定 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 例如：

```shell
mc quota set play/mybucket --size 10Gi
```

#### `--size` {#mc.quota.set.-size}

*mc-cmd*

*Required*

设置存储桶存储大小的最大限制。 MinIO 服务器会拒绝任何内容将超出存储桶已配置配额的传入 `PUT` 请求。

例如，若硬限制为 `10G`，当存储桶达到 10 gigabytes 时，将无法再添加任何对象。

### 全局标志 {#id7}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。