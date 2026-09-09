---
title: "mc admin bucket quota"

weight: 110
---

<a id="mc-admin-bucket-quota"></a>

<a id="command-mc.admin.bucket.quota"></a>

> [!NOTE]
> **变更: RELEASE.2022-12-13T00-23-28Z**
>
> `mc admin bucket quota` 已被以下命令替代：
>
> - [`mc quota set`](/docs/reference/deprecated/mc-quota-set/#command-mc.quota.set)
> - [`mc quota info`](/docs/reference/deprecated/mc-quota-info/#command-mc.quota.info)
> - [`mc quota clear`](/docs/reference/deprecated/mc-quota-clear/#command-mc.quota.clear)

## 说明 {#id2}

[`mc admin bucket quota`](#command-mc.admin.bucket.quota) 命令用于管理按存储桶设置的存储配额。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

<a id="id3"></a>

### 计量单位 {#mc-admin-bucket-quota-units}

[`mc admin bucket quota --hard`](#mc.admin.bucket.quota.-hard) 标志 接受以下不区分大小写的后缀，用于表示所指定大小值的单位：

| 后缀 | 单位大小 |
| --- | --- |
| `k` | KB（千字节，1000 字节） |
| `m` | MB（兆字节，1000 千字节） |
| `g` | GB（吉字节，1000 兆字节） |
| `t` | TB（太字节，1000 吉字节） |
| `ki` | KiB（二进制千字节，1024 字节） |
| `mi` | MiB（二进制兆字节，1024 KiB） |
| `gi` | GiB（二进制吉字节，1024 MiB） |
| `ti` | TiB（二进制太字节，1024 GiB） |

省略后缀时，默认单位为 `bytes`。

## 示例 {#id4}

### 为存储桶配置硬配额 {#id5}

使用 [`mc admin bucket quota`](#command-mc.admin.bucket.quota) 搭配 [`--hard`](#mc.admin.bucket.quota.-hard) 标志，为存储桶指定硬配额。 硬配额可防止存储桶大小增长超过指定限制。

```shell
mc admin bucket quota TARGET/BUCKET --hard LIMIT
```

- 将 `TARGET` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为要设置硬配额的存储桶名称。
- 将 `LIMIT` 替换为存储桶可增长到的最大大小。 例如，要将硬限制设置为 10 TB，请指定 `10t`。 支持的单位请参见 [计量单位](#mc-admin-bucket-quota-units)。

### 获取存储桶配额配置 {#id6}

使用 [`mc admin bucket quota`](#command-mc.admin.bucket.quota) 获取存储桶当前的配额配置：

```shell
mc admin bucket quota TARGET/BUCKET
```

将 `TARGET` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为要获取配额的存储桶名称。

### 清除已配置的存储桶配额 {#id7}

使用 [`mc admin bucket quota`](#command-mc.admin.bucket.quota) 搭配 [`--clear`](#mc.admin.bucket.quota.-clear) 标志，清除存储桶上的所有配额。

```shell
mc admin bucket quota TARGET/BUCKET --clear
```

- 将 `TARGET` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。 将 `BUCKET` 替换为要清除配额的存储桶名称。

## 语法 {#id8}

[`mc admin bucket quota`](#command-mc.admin.bucket.quota) 使用以下语法：

```shell
mc admin bucket quota TARGET [ARGUMENTS]
```

[`mc admin bucket quota`](#command-mc.admin.bucket.quota) 支持以下参数：

#### `TARGET` {#mc.admin.bucket.quota.TARGET}

*mc-cmd*

命令为其创建配额的存储桶的完整路径。 指定 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias) 作为路径前缀。 例如：

```shell
mc admin bucket quota play/mybucket
```

省略其他所有参数可返回指定存储桶的当前配额设置。

#### `--hard` {#mc.admin.bucket.quota.-hard}

*mc-cmd*

设置存储桶存储大小的最大限制。对于内容会超过存储桶已配置配额的传入 `PUT` 请求，MinIO 服务器会予以拒绝。

例如，若硬限制为 `10GB`，当存储桶大小达到 `10GB` 时，将无法再添加 任何对象。

支持的单位大小请参见 [计量单位](#mc-admin-bucket-quota-units)。

#### `--clear` {#mc.admin.bucket.quota.-clear}

*mc-cmd*

清除为该存储桶配置的所有配额。