---
title: "批量过期"

weight: 30
---

<a id="minio-batch-framework-expire-job"></a>
<a id="id1"></a>

> [!NOTE]
> **新增: MinIO**
>
> RELEASE.2023-12-02T10-51-33Z

MinIO 批处理框架允许你使用 YAML 格式的作业定义文件（“batch file”）创建、管理、监控和执行作业。 批处理作业直接在 MinIO 部署上运行，从而利用服务端处理能力，而不受运行 [MinIO Client](/docs/reference/minio-mc/#minio-client) 的本地机器限制。

`expire` 批处理作业会将 [对象自动过期](/docs/administration/object-management/create-lifecycle-management-expiration-rule/#minio-lifecycle-management-create-expiry-rule) 的行为应用到单个存储桶。 该作业根据提供的配置判断对象是否符合过期条件，且独立于任何已配置的过期规则。

## 行为 {#id3}

### 对象立即过期 {#id4}

批量过期会作为批处理作业的一部分立即执行，这与 [passive scanner-based application of expiration rules](/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-scanner) 不同。 具体来说，批量过期不会让位于应用 I/O，因此可能影响部署上常规读写操作的性能。

### 过期资格在批处理运行时确定 {#id5}

批量过期按存储桶工作，并且每次运行都会一次性执行直至完成。 该作业在运行时判断对象是否符合过期条件，并且 *不会* 定期重新扫描或重新检查新对象。

如果要处理任何新近满足过期条件的对象，请重新运行该批处理作业。

### 过期规则仅检查最新对象 {#id6}

批量过期作业只会使用每个对象的最新版本或“current”版本来匹配各条批量过期规则。

<a id="minio-batch-framework-expire-job-ref"></a>

## `expire` 批处理作业参考 {#expire}

<table>
  <tbody>
    <tr>
      <td><p>字段</p></td>
      <td><p>说明</p></td>
    </tr>
    <tr>
      <td><p><code>expire</code></p></td>
      <td><p><em>必需</em></p><p>过期作业类型的顶层字段。</p></td>
    </tr>
    <tr>
      <td><p><code>apiVersion</code></p></td>
      <td><p><em>必需</em></p><p>设为 <code>v1</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>bucket</code></p></td>
      <td><p><em>必需</em></p><p>指定该作业运行所在的存储桶名称。</p></td>
    </tr>
    <tr>
      <td><p><code>prefix</code></p></td>
      <td><p><em>可选</em></p><p>指定该作业运行所在的存储桶前缀。</p></td>
    </tr>
    <tr>
      <td><p><code>rules</code></p></td>
      <td><p><em>必需</em></p><p>一个包含一条或多条过期规则的数组，用于应用到指定 <code>bucket</code> 和 <code>prefix</code> （如有）中的对象。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].type</code></p></td>
      <td><p><em>必需</em></p><p>支持以下两个值之一：</p><ul><li><p><code>object</code> - 仅应用于当前版本<strong>不是</strong> <code>DeleteMarker</code> 的对象。</p></li><li><p><code>deleted</code> - 仅应用于当前版本<strong>是</strong> <code>DeleteMarker</code> 的对象。</p></li></ul><p>有关 <code>DeleteMarker</code> 或版本控制存储桶中删除操作的更完整文档，请参见 <a href="/docs/administration/object-management/object-delete/#minio-object-delete">对象删除</a>。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].name</code></p></td>
      <td><p><em>可选</em></p><p>指定用于过滤对象的匹配字符串。</p><p>支持 glob 风格通配符（<code>*</code>、<code>?</code>）。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].olderThan</code></p></td>
      <td><p><em>可选</em></p><p>指定对象年龄以过滤对象。
该规则仅应用于年龄超过指定时间单位的对象。</p><p>例如，<code>72h</code> 或 <code>3d</code> 会选择年龄超过三天的对象。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].createdBefore</code></p></td>
      <td><p><em>可选</em></p><p>指定一个 <a href="https://datatracker.ietf.org/doc/html/rfc3339.html"><strong>RFC3339</strong></a> 日期时间来过滤对象。</p><p>该规则仅应用于在指定时间戳<em>之前</em>创建的对象。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].tags</code></p></td>
      <td><p><em>可选</em></p><p>指定一个键值对数组，用于描述对象标签并据此过滤对象。
<code>value</code> 条目支持 glob 风格通配符（<code>*</code>、<code>?</code>）。</p><p>例如，以下配置会将该规则过滤为仅匹配具有相应标签的对象：</p><pre><code class="language-yaml">tags:
  - key: archive
    value: True</code></pre><p>此键与 <code>rules.[n].type: deleted</code> 不兼容。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].metadata</code></p></td>
      <td><p><em>可选</em></p><p>指定一个键值对数组，用于描述对象元数据并据此过滤对象。
<code>value</code> 键支持 glob 风格通配符（<code>*</code>、<code>?</code>）。</p><p>例如，以下配置会将该规则过滤为仅匹配具有相应元数据的对象：</p><pre><code class="language-yaml">metadata:
  - key: content-type
    value: image/*</code></pre><p>此键与 <code>rules.[n].type: deleted</code> 不兼容。</p></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].size</code></p></td>
      <td><p><em>可选</em></p><p>指定对象大小范围以过滤对象。</p><ul><li><p><code>lessThan</code> - 匹配大小小于指定数值的对象（例如 <code>MiB</code>、<code>GiB</code>）。</p></li><li><p><code>greaterThan</code> - 匹配大小大于指定数值的对象（例如 <code>MiB</code>、<code>GiB</code>）。</p></li></ul></td>
    </tr>
    <tr>
      <td><p><code>rules.[n].purge.retainVersions</code></p></td>
      <td><p><em>可选</em></p><p>指定在执行过期时要保留的对象版本数量。</p><p>默认为 <code>0</code>，即删除所有对象版本（最快）。</p></td>
    </tr>
    <tr>
      <td><p><code>notify.endpoint</code></p></td>
      <td><p><em>可选</em></p><p>用于发送通知事件的预定义端点。</p></td>
    </tr>
    <tr>
      <td><p><code>notify.token</code></p></td>
      <td><p><em>可选</em></p><p>用于访问 <code>notify.endpoint</code> 的可选 JSON Web Token (JWT)。</p></td>
    </tr>
    <tr>
      <td><p><code>retry.attempts</code></p></td>
      <td><p><em>可选</em></p><p>在放弃之前完成该批处理作业的重试次数。</p></td>
    </tr>
    <tr>
      <td><p><code>retry.delay</code></p></td>
      <td><p><em>可选</em></p><p>每次尝试之间的等待时间（<code>ms</code>）。</p></td>
    </tr>
  </tbody>
</table>

## `expire` 作业类型的 YAML 示例 {#expire-yaml}

使用 [`mc batch generate`](/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate) 创建基础 `expire` 批处理作业，再进行进一步定制。

```yaml
expire:
  apiVersion: v1
  bucket: mybucket # Bucket where this job will expire matching objects from
  prefix: myprefix # (Optional) Prefix under which this job will expire objects matching the rules below.
  rules:
    - type: object  # objects with zero ore more older versions
      name: NAME # match object names that satisfy the wildcard expression.
      olderThan: 70h # match objects older than this value
      createdBefore: "2006-01-02T15:04:05.00Z" # match objects created before this date and time in RFC3339 format
      tags:
        - key: name
          value: pick* # match objects with tag 'name', all values starting with 'pick'
      metadata:
        - key: content-type
          value: image/* # match objects with 'content-type', all values starting with 'image/'
      size:
        lessThan: 10MiB # match objects with size less than this value (e.g. 10MiB)
        greaterThan: 1MiB # match objects with size greater than this value (e.g. 1MiB)
      purge:
          # retainVersions: 0 # (default) delete all versions of the object. This option is the fastest.
          # retainVersions: 5 # keep the latest 5 versions of the object.

    - type: deleted # objects with delete marker as their latest version
      name: NAME # match object names that satisfy the wildcard expression.
      olderThan: 10h # match objects older than this value (e.g. 7d10h31s)
      createdBefore: "2006-01-02T15:04:05.00Z" # match objects created before this date and time in RFC3339 format
      purge:
          # retainVersions: 0 # (default) delete all versions of the object. This option is the fastest.
          # retainVersions: 5 # keep the latest 5 versions of the object including delete markers.

  notify:
    endpoint: https://notify.endpoint # notification endpoint to receive job completion status
    token: Bearer xxxxx # optional authentication token for the notification endpoint

  retry:
    attempts: 10 # number of retries for the job before giving up
    delay: 500ms # least amount of delay between each retry

```