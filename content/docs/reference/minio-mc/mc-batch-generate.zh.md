---
title: "mc batch generate"

weight: 30
---

<a id="mc-batch-generate"></a>
<a id="minio-mc-batch-generate"></a>

<a id="command-mc.batch.generate"></a>

> [!NOTE]
> **变更: MinIO**
>
> RELEASE.2022-10-09T21-10-59Z or later

## 语法 {#id1}

[`mc batch generate`](#command-mc.batch.generate) 命令会为指定作业类型创建一个基础的 YAML 格式模板文件。

MinIO 创建该文件后，请在你偏好的文本编辑器中打开并进一步自定义。 每个批处理文件中只能定义一个作业任务定义。

请参阅 [job types](#minio-batch-job-types) 了解可生成的受支持作业。

{{< tabs group="example-syntax" >}}
{{< tab label="EXAMPLE" value="example" >}}
以下命令会为 `myminio` 别名下 `mybucket` 存储桶上的 replicate 作业创建一个基础 YAML 文件。

```shell
mc batch generate myminio replicate
```
{{< /tab >}}
{{< tab label="SYNTAX" value="syntax" >}}
该命令语法如下：

```shell
mc [GLOBALFLAGS] batch generate \
                       ALIAS   \
                       JOBTYPE
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id2}

##### `ALIAS` {#mc.batch.generate.ALIAS}

*mc-cmd*

*Required*

用于生成 YAML 模板文件的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。 指定的 `alias` 不会限制你可使用该生成文件的部署位置。

例如：

```text
mc batch generate myminio replicate
```

##### `JOBTYPE` {#mc.batch.generate.JOBTYPE}

*mc-cmd*

*Required*

要生成 YAML 文档的作业类型。

支持以下取值：

- [replicate](#minio-mc-batch-generate-replicate-job)
- [keyrotate](#minio-mc-batch-generate-keyrotate-job)
- [expire](#minio-mc-batch-generate-expire-job) (Added `mc.RELEASE.2023-12-02T11-24-10Z`)

### 全局标志 {#id3}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id4}

### 为 Replicate 作业类型生成 `yaml` 文件 {#replicate-yaml}

以下命令会为 replicate 类型批处理作业生成 YAML 蓝图，并将文件命名为 `replicate`，扩展名为 `.yaml`：

```shell
mc batch generate alias replicate > replicate.yaml
```

- 将 `alias` 替换为用于生成 yaml 文件的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 `replicate` 替换为要生成 yaml 文件的作业类型。

  [`mc batch`](/docs/reference/minio-mc/mc-batch/#command-mc.batch) 支持 `replicate` 和 `keyrotate` 作业类型。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。

<a id="id5"></a>

## 作业类型 {#minio-batch-job-types}

[`mc batch`](/docs/reference/minio-mc/mc-batch/#command-mc.batch) 当前支持以下作业任务类型：

- [replicate](#minio-mc-batch-generate-replicate-job)

  在两个 MinIO 部署之间复制对象。 以批处理作业形式提供与 [bucket replication](/docs/administration/bucket-replication/#minio-bucket-replication) 类似的功能，而不是持续扫描功能。
- [keyrotate](#minio-mc-batch-generate-keyrotate-job)

  > [!NOTE]
  > **新增: MinIO**
  >
  > RELEASE.2023-04-07T05-28-58Z

  为 MinIO 部署中静态对象的 sse-s3 或 sse-kms 密钥执行轮换。
- [expire](#minio-mc-batch-generate-expire-job)

  > [!NOTE]
  > **新增: MinIO**
  >
  > RELEASE.2023-12-02T10-51-33Z

  依据与 [对象自动过期](/docs/administration/object-management/create-lifecycle-management-expiration-rule/#minio-lifecycle-management-create-expiry-rule) 类似的语义使对象过期。

<a id="minio-mc-batch-generate-replicate-job"></a>

### `replicate` {#replicate}

你可以将以下示例配置作为构建自定义复制批处理作业的起点：

```yaml
replicate:
  apiVersion: v1
  # source of the objects to be replicated
  source:
    type: TYPE # valid values are "s3" or "minio"
    bucket: BUCKET
    prefix: PREFIX # 'PREFIX' is optional
    # If your source is the 'local' alias specified to 'mc batch start', then the 'endpoint' and 'credentials' fields are optional and can be omitted
    # Either the 'source' or 'remote' *must* be the "local" deployment
    endpoint: "http[s]://HOSTNAME:PORT" 
    # path: "on|off|auto" # "on" enables path-style bucket lookup. "off" enables virtual host (DNS)-style bucket lookup. Defaults to "auto"
    credentials:
      accessKey: ACCESS-KEY # Required
      secretKey: SECRET-KEY # Required
    # sessionToken: SESSION-TOKEN # Optional only available when rotating credentials are used
    snowball: # automatically activated if the source is local
      disable: false # optionally turn-off snowball archive transfer
      batch: 100 # upto this many objects per archive
      inmemory: true # indicates if the archive must be staged locally or in-memory
      compress: false # S2/Snappy compressed archive
      smallerThan: 5MiB # create archive for all objects smaller than 5MiB
      skipErrs: false # skips any source side read() errors

  # target where the objects must be replicated
  target:
    type: TYPE # valid values are "s3" or "minio"
    bucket: BUCKET
    prefix: PREFIX # 'PREFIX' is optional
    # If your source is the 'local' alias specified to 'mc batch start', then the 'endpoint' and 'credentials' fields are optional and can be omitted

    # Either the 'source' or 'remote' *must* be the "local" deployment
    endpoint: "http[s]://HOSTNAME:PORT"
    # path: "on|off|auto" # "on" enables path-style bucket lookup. "off" enables virtual host (DNS)-style bucket lookup. Defaults to "auto"
    credentials:
      accessKey: ACCESS-KEY
      secretKey: SECRET-KEY
    # sessionToken: SESSION-TOKEN # Optional only available when rotating credentials are used

  # NOTE: All flags are optional
  # - filtering criteria only applies for all source objects match the criteria
  # - configurable notification endpoints
  # - configurable retries for the job (each retry skips successfully previously replaced objects)
  flags:
    filter:
      newerThan: "7d" # match objects newer than this value (e.g. 7d10h31s)
      olderThan: "7d" # match objects older than this value (e.g. 7d10h31s)
      createdAfter: "datetime" # match objects created after this date and time in RFC3339 format
      createdBefore: "datetime" # match objects created before this date and time in RFC3339 format

      ## NOTE: tags are not supported when "source" is remote.
      # tags:
      #   - key: "name"
      #     value: "pick*" # match objects with tag 'name', with all values starting with 'pick'

      # metadata:
      #   - key: "content-type"
      #     value: "image/*" # match objects with 'content-type', with all values starting with 'image/'

    notify:
      endpoint: "https://notify.endpoint" # notification endpoint to receive job status events
      token: "Bearer xxxxx" # optional authentication token for the notification endpoint

    retry:
      attempts: 10 # number of retries for the job before giving up
      delay: "500ms" # least amount of delay between each retry

```

有关各个键更完整的文档，请参阅 [复制批处理作业参考](/docs/administration/batch-framework-job-replicate/#minio-batch-framework-replicate-job-ref)。

<a id="minio-mc-batch-generate-keyrotate-job"></a>

### `keyrotate` {#keyrotate}

你可以将以下示例配置作为构建自定义密钥轮换批处理作业的起点：

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

有关各个键更完整的文档，请参阅 [密钥轮换批处理作业参考](/docs/administration/batch-framework-job-keyrotate/#minio-batch-framework-keyrotate-job-ref)。

<a id="minio-mc-batch-generate-expire-job"></a>

### `expire` {#expire}

你可以将以下示例配置作为构建自定义过期批处理作业的起点：

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

有关各个键更完整的文档，请参阅 [expire 批处理作业参考](/docs/administration/batch-framework-job-expire/#minio-batch-framework-expire-job-ref)。