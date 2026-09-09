---
title: "数据压缩"

weight: 50
---

<a id="minio-data-compression"></a>
<a id="id1"></a>

## 概述 {#id3}

MinIO Server 支持对对象进行压缩，以减少磁盘使用量。 对象在 PUT 时会先压缩再写入磁盘，在 GET 时会先解压再发送给客户端。这样一来，压缩过程对客户端应用程序和服务是透明的。

根据数据类型的不同，压缩还可能提高整体吞吐量。 在生产部署中，写入吞吐量通常为系统中每个可用 CPU 核心每秒 500MB 或更高。 解压吞吐量大约为每个 CPU 核心每秒 1 GB 或更高。

为获得最佳效果，请参阅 MinIO 的 [推荐硬件配置](/docs/operations/checklists/hardware/#deploy-minio-distributed-recommendations)，或使用 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 与工程师直接协作分析压缩性能。

<a id="id4"></a>

### 默认文件类型 {#minio-data-compression-default-types}

数据压缩是全局选项，所配置的设置会应用于部署中的所有存储桶。 启用数据压缩后，默认会压缩以下类型的数据：

<table>
  <thead>
    <tr>
      <th><p>文件扩展名</p></th>
      <th><p>媒体（MIME）类型</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>.txt</code></p><p><code>.log</code></p><p><code>.csv</code></p><p><code>.json</code></p><p><code>.tar</code></p><p><code>.xml</code></p><p><code>.bin</code></p></td>
      <td><p><code>text/*</code></p><p><code>application/json</code></p><p><code>application/xml</code></p><p><code>binary/octet-stream</code></p></td>
    </tr>
  </tbody>
</table>

你可以通过指定所需的文件扩展名和 [media (MIME) types](https://en.wikipedia.org/wiki/Media_type) 来控制哪些对象会被压缩。

> [!NOTE]
> **现有对象不会被修改**
>
> 启用、禁用或更新某个部署的压缩设置时，不会修改现有对象。 新对象会根据其创建时生效的设置进行压缩。

<a id="id5"></a>

### 排除的文件类型 {#minio-data-compression-excluded-types}

某些数据无法被有效压缩。 例如：视频、已经压缩过的数据，或小于 4KiB 的文件。 MinIO 不会压缩常见的不可压缩文件类型，即使它们已在压缩配置中指定。

这些类型的对象永远不会被压缩：

<table>
  <thead>
    <tr>
      <th><p>对象类型</p></th>
      <th><p>文件扩展名</p></th>
      <th><p>媒体（MIME）类型</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>音频</p></td>
      <td></td>
      <td><p><code>audio/*</code></p></td>
    </tr>
    <tr>
      <td><p>视频</p></td>
      <td><code>*.mp4</code><br /><code>*.mkv</code><br /><code>*.mov</code><br /></td>
      <td><p><code>video/*</code></p></td>
    </tr>
    <tr>
      <td><p>图像</p></td>
      <td><code>*.jpg</code><br /><code>*.png</code><br /><code>*.gif</code><br /></td>
      <td><p><code>application/x-compress</code> (LZW)</p></td>
    </tr>
    <tr>
      <td><p>7ZIP 压缩文件</p></td>
      <td><p><code>*.7z</code></p></td>
      <td></td>
    </tr>
    <tr>
      <td><p>BZIP2 压缩文件</p></td>
      <td><p><code>*.bz2</code></p></td>
      <td><p><code>application/x-bz2</code></p></td>
    </tr>
    <tr>
      <td><p>GZIP 压缩文件</p></td>
      <td><p><code>*.gz</code></p></td>
      <td><p><code>application/x-gzip</code></p></td>
    </tr>
    <tr>
      <td><p>RAR 压缩文件</p></td>
      <td><p><code>*.rar</code></p></td>
      <td></td>
    </tr>
    <tr>
      <td><p>LZMA 压缩文件</p></td>
      <td><p><code>*.xz</code></p></td>
      <td><p><code>application/x-xz</code></p></td>
    </tr>
    <tr>
      <td><p>ZIP 压缩文件</p></td>
      <td><p><code>*.zip</code></p></td>
      <td><code>application/zip</code><br /><code>application-x-zip-compressed</code><br /></td>
    </tr>
    <tr>
      <td><p>小于 4 KiB</p></td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>

### 数据压缩与加密 {#id6}

MinIO 支持对压缩后的对象进行加密，但不建议在未事先进行风险评估的情况下同时启用压缩和加密。 在为压缩对象启用加密之前，请仔细评估你的环境中的安全需求。

有关如何同时使用压缩和加密的更多信息，请参阅 [Transparent Data Compression on MinIO](https://blog.min.io/transparent-data-compression/)。 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 用户可以 [log in](https://subnet.min.io/?ref=docs) 并与我们的工程和安全团队沟通，以评估加密选项。

## 教程 {#id7}

### 启用数据压缩 {#id8}

要启用数据压缩，请使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 将 [`compression`](/docs/reference/minio-server/settings/core/#mc-conf.compression) 键的 [`enable`](/docs/reference/minio-server/settings/core/#mc-conf.compression.enable) 选项设置为 `on`。

以下命令会为 [默认类型](#minio-data-compression-default-types) 的新对象启用压缩：

```shell
mc admin config set ALIAS compression enable=on
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

现有的未压缩对象不会被修改。 要配置需要压缩的扩展名和类型，请参阅 [配置要压缩哪些对象](#minio-data-compression-configure-objects)。

要查看当前的压缩设置：

```shell
mc admin config get ALIAS compression
```

### 禁用数据压缩 {#id9}

要禁用数据压缩，请使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 将 [`compression`](/docs/reference/minio-server/settings/core/#mc-conf.compression) 键的 [`enable`](/docs/reference/minio-server/settings/core/#mc-conf.compression.enable) 选项设置为 `off`：

以下命令会禁用新对象的数据压缩：

```shell
mc admin config set ALIAS compression enable=off
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

现有的已压缩对象不会被修改。

<a id="id10"></a>

### 配置要压缩哪些对象 {#minio-data-compression-configure-objects}

通过在 [`extensions`](/docs/reference/minio-server/settings/core/#mc-conf.compression.extensions) 或 [`mime_types`](/docs/reference/minio-server/settings/core/#mc-conf.compression.mime_types) 参数中指定所需的文件扩展名和媒体类型，来配置需要压缩的对象。

默认的数据压缩配置会压缩以下类型的数据：

<table>
  <thead>
    <tr>
      <th><p>文件扩展名</p></th>
      <th><p>媒体（MIME）类型</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>.txt</code></p><p><code>.log</code></p><p><code>.csv</code></p><p><code>.json</code></p><p><code>.tar</code></p><p><code>.xml</code></p><p><code>.bin</code></p></td>
      <td><p><code>text/*</code></p><p><code>application/json</code></p><p><code>application/xml</code></p><p><code>binary/octet-stream</code></p></td>
    </tr>
  </tbody>
</table>

> [!NOTE]
> **默认排除的扩展名和类型永远不会被压缩**
>
> 某些对象无法被高效压缩。 即使这些对象已在 [`extensions`](/docs/reference/minio-server/settings/core/#mc-conf.compression.extensions) 或 [`mime_types`](/docs/reference/minio-server/settings/core/#mc-conf.compression.mime_types) 参数中指定，MinIO 也不会尝试压缩它们。 排除类型列表请参阅 [排除的文件类型](#minio-data-compression-excluded-types)。

以下各节介绍如何为所需的文件扩展名和媒体类型配置压缩。

#### 压缩所有可压缩对象 {#id11}

要压缩除 [默认排除类型](#minio-data-compression-excluded-types) 之外的所有对象，请使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 将 [`compression`](/docs/reference/minio-server/settings/core/#mc-conf.compression) 键的 [`extensions`](/docs/reference/minio-server/settings/core/#mc-conf.compression.extensions) 和 [`mime_types`](/docs/reference/minio-server/settings/core/#mc-conf.compression.mime_types) 选项设置为空列表：

```shell
mc admin config set ALIAS compression extensions= mime_types=
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

#### 按文件扩展名压缩对象 {#id12}

要压缩具有特定文件扩展名的对象，请使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 在 [`extensions`](/docs/reference/minio-server/settings/core/#mc-conf.compression.extensions) 参数中设置所需的文件扩展名。

以下命令会压缩扩展名为 `.bin` 和 `.txt` 的文件：

```shell
mc admin config set ALIAS compression extensions=".bin, .txt"
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

新的文件扩展名列表会替换之前的列表。 如果要添加或删除扩展名，请使用完整的待压缩扩展名列表重新执行 [`extensions`](/docs/reference/minio-server/settings/core/#mc-conf.compression.extensions) 命令。

以下命令会将 `.pdf` 添加到上一个示例中的文件扩展名列表：

```shell
mc admin config set ALIAS compression extensions=".bin, .txt, .pdf"
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

#### 按媒体类型压缩对象 {#id13}

要压缩特定媒体类型的对象，请使用 [`mc admin config set`](/docs/reference/minio-mc-admin/mc-admin-config/#mc.admin.config.set) 将 [`compression`](/docs/reference/minio-server/settings/core/#mc-conf.compression) 键的 [`mime_types`](/docs/reference/minio-server/settings/core/#mc-conf.compression.mime_types) 选项设置为所需类型的列表。

以下示例会压缩类型为 `application/json` 和 `image/bmp` 的文件：

```shell
mc admin config set ALIAS compression mime_types="application/json, image/bmp"
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。

新的媒体类型列表会替换之前的列表。 如果要添加或删除类型，请使用完整的待压缩类型列表重新执行 [`mime_types`](/docs/reference/minio-server/settings/core/#mc-conf.compression.mime_types) 命令。

你可以使用 `*` 指定某一媒体类型下的所有子类型。 以下命令会将所有 `text` 子类型添加到上一个示例中的列表：

```shell
mc admin config set ALIAS compression mime_types="application/json, image/bmp, text/*"
```

- 将 `ALIAS` 替换为已配置 MinIO 部署的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。