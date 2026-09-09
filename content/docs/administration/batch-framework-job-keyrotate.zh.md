---
title: "批量密钥轮换"

weight: 20
---

<a id="minio-batch-framework-keyrotate-job"></a>
<a id="id1"></a>

> [!NOTE]
> **新增: MinIO**
>
> RELEASE.2023-04-07T05-28-58Z

MinIO Batch Framework 允许你使用 YAML 格式的作业定义文件（“批处理文件”）来创建、管理、监控和执行作业。 批处理作业直接在 MinIO 部署上运行，以利用服务端处理能力，而不受运行 [MinIO Client](/docs/reference/minio-mc/#minio-client) 的本地机器限制。

`keyrotate` 批处理作业类型会为 MinIO 部署上的加密对象轮换 [sse-s3 or sse-kms keys](/docs/operations/server-side-encryption/#minio-sse-data-encryption)。

YAML 配置支持按创建日期、标签、元数据或 kms key 进行过滤，将密钥轮换限制在特定对象集合上。 你还可以定义重试次数，或设置通知 endpoint 和 token。

<a id="id3"></a>

## 密钥轮换批处理作业参考 {#minio-batch-framework-keyrotate-job-ref}

> [!NOTE]
> **新增: MinIO**
>
> RELEASE.2023-04-07T05-28-58Z

使用 `keyrotate` 作业类型创建批处理作业，以轮换加密对象的 [sse-s3 or sse-kms keys](/docs/operations/server-side-encryption/#minio-sse-data-encryption)。

### 必填字段 {#id4}

> <table>
>   <tbody>
>     <tr>
>       <td><p><code>type:</code></p></td>
>       <td><p><code>sse-s3</code> 或 <code>sse-kms</code> 之一。</p></td>
>     </tr>
>     <tr>
>       <td><p><code>key:</code></p></td>
>       <td><p>仅用于 <code>sse-kms</code> 类型。
> 用于解封密钥保管库的密钥。</p></td>
>     </tr>
>   </tbody>
> </table>

### 可选字段 {#id5}

对于 **基于标志的过滤条件**

<table>
  <tbody>
    <tr>
      <td><p><code>newerThan:</code></p></td>
      <td><p>以 <code>#d#h#s</code> 格式表示时长的字符串。</p><p>仅为比指定时长更新的对象轮换密钥。
例如，<code>7d</code>、<code>24h</code>、<code>5d12h30s</code> 都是有效字符串。</p></td>
    </tr>
    <tr>
      <td><p><code>olderThan:</code></p></td>
      <td><p>以 <code>#d#h#s</code> 格式表示时长的字符串。</p><p>仅为比指定时长更旧的对象轮换密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>createdAfter:</code></p></td>
      <td><p>采用 <code>YYYY-MM-DDTHH:MM:SSZ</code> <a href="https://datatracker.ietf.org/doc/html/rfc3339.html"><strong>RFC3339</strong></a> 日期时间格式的日期。</p><p>仅为在该日期之后创建的对象轮换密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>createdBefore:</code></p></td>
      <td><p>采用 <code>YYYY-MM-DDTHH:MM:SSZ</code> <a href="https://datatracker.ietf.org/doc/html/rfc3339.html"><strong>RFC3339</strong></a> 日期时间格式的日期。</p><p>仅为在该日期之前创建的对象轮换密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>context:</code></p></td>
      <td><p>仅用于 <code>sse-kms</code> 类型。
执行操作时使用的上下文。</p></td>
    </tr>
    <tr>
      <td><p><code>tags:</code></p></td>
      <td><p>仅为标签与指定 <code>key:</code> 和 <code>value:</code> 匹配的对象轮换密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>metadata:</code></p></td>
      <td><p>仅为元数据与指定 <code>key:</code> 和 <code>value:</code> 匹配的对象轮换密钥。</p></td>
    </tr>
    <tr>
      <td><p><code>kmskey:</code></p></td>
      <td><p>仅为 KMS key-id 与指定值匹配的对象轮换密钥。
这仅适用于 <code>sse-kms</code> 类型。</p></td>
    </tr>
  </tbody>
</table>

对于 **通知**

<table>
  <tbody>
    <tr>
      <td><p><code>endpoint:</code></p></td>
      <td><p>用于发送通知事件的预定义 endpoint。</p></td>
    </tr>
    <tr>
      <td><p><code>token:</code></p></td>
      <td><p>用于访问 <code>endpoint</code> 的可选 JSON Web Token (JWT)。</p></td>
    </tr>
  </tbody>
</table>

对于 **重试**

如果作业被中断，你可以定义最大重试次数。 对于每次重试，你还可以定义两次尝试之间的等待时间。

<table>
  <tbody>
    <tr>
      <td><p><code>attempts:</code></p></td>
      <td><p>在放弃之前完成批处理作业的尝试次数。</p></td>
    </tr>
    <tr>
      <td><p><code>delay:</code></p></td>
      <td><p>每次尝试之间的等待时长。</p></td>
    </tr>
  </tbody>
</table>

## `keyrotate` 作业类型的 YAML 描述文件示例 {#keyrotate-yaml}

使用 [`mc batch generate`](/docs/reference/minio-mc/mc-batch-generate/#command-mc.batch.generate) 创建一个基础的 `keyrotate` 批处理作业，以便进一步自定义：

```yaml
keyrotate:
  apiVersion: v1
  bucket: BUCKET
  prefix: PREFIX
  encryption:
    type: sse-s3 # valid values are sse-s3 and sse-kms
    key: <new-kms-key> # valid only for sse-kms
    context: <new-kms-key-context> # valid only for sse-kms

  # optional flags based filtering criteria
  # for all objects
  flags:
    filter:
      newerThan: "7d" # match objects newer than this value (e.g. 7d10h31s)
      olderThan: "7d" # match objects older than this value (e.g. 7d10h31s)
      createdAfter: "date" # match objects created after this date and time in RFC3339 format
      createdBefore: "date" # match objects created before this date and time in RFC3339 format
      tags:
        - key: "name"
          value: "pick*" # match objects with tag 'name', with all values starting with 'pick'
      metadata:
        - key: "content-type"
          value: "image/*" # match objects with 'content-type', with all values starting with 'image/'
      kmskey: "key-id" # match objects with KMS key-id (applicable only for sse-kms)
    notify:
      endpoint: "https://notify.endpoint" # notification endpoint to receive job status events
      token: "Bearer xxxxx" # optional authentication token for the notification endpoint
    retry:
      attempts: 10 # number of retries for the job before giving up
      delay: "500ms" # least amount of delay between each retry

```