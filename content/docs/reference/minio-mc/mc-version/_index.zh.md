---
title: "mc version"

weight: 430
icon: fa-solid fa-code-branch
---

<a id="mc-version"></a>

<a id="command-mc.version"></a>

## 描述 {#id2}

[`mc version`](#command-mc.version) 命令可为 MinIO 存储桶启用、禁用并获取 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 状态。

有关 MinIO 中对象版本控制的更多信息，请参见 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。

[`mc version`](#command-mc.version) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>描述</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-version-enable/#command-mc.version.enable"><code>enable</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-version-enable/#command-mc.version.enable"><code>mc version enable</code></a> 命令用于为指定存储桶启用版本控制。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-version-info/#command-mc.version.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-version-info/#command-mc.version.info"><code>mc version info</code></a> 命令返回指定存储桶的版本控制状态。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-version-suspend/#command-mc.version.suspend"><code>suspend</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-version-suspend/#command-mc.version.suspend"><code>mc version suspend</code></a> 命令用于禁用指定存储桶上的版本控制。</p></td>
    </tr>
  </tbody>
</table>

## 行为 {#id3}

### 对象锁定会启用存储桶版本控制 {#id4}

虽然默认禁用存储桶版本控制，但在存储桶上或该存储桶中的对象上配置对象锁定时，会自动为该存储桶启用版本控制。 有关配置对象锁定的更多信息，请参见 [`mc retention`](/docs/reference/minio-mc/mc-retention/#command-mc.retention)。

### 现有数据下的存储桶版本控制 {#id5}

在包含现有数据的存储桶上启用版本控制时，会立即为每个未版本化对象创建一个 null 值版本 ID。

在包含现有已版本化数据的存储桶上禁用版本控制时，*不会* 删除任何已版本化对象。 禁用存储桶版本控制后，应用程序仍可继续访问已版本化数据。 使用 [`mc rm --versions ALIAS/BUCKET/OBJECT`](/docs/reference/minio-mc/mc-rm/#mc.rm.-versions) 删除某个对象 *及其* 所有版本。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。