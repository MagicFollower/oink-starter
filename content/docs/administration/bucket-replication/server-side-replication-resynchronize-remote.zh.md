---
title: "从远程副本重新同步存储桶"

weight: 50
---

<a id="minio-bucket-replication-resynchronize"></a>
<a id="id1"></a>

本页中的步骤使用健康的复制远端来重新同步 MinIO 存储桶中的内容。重新同步可用于在副本配置下的 MinIO 部署发生部分或全部数据丢失后进行恢复。

例如，考虑如下所示的 MinIO 主动-主动复制配置：

<img src="/images/replication/active-active-twoway-replication.svg" alt="主动-主动复制在两个远程部署之间同步数据。" style="max-width: 600px; height: auto;" />

重新同步允许使用其中一个参与复制的 MinIO 部署上的健康数据，作为重建另一个部署的源。

重新同步是按存储桶执行的过程。对于远端中每个遭受部分或全部数据丢失的存储桶，都必须重复执行重新同步。

> [!NOTE]
> **BC/DR 操作期间的专业支持**
>
> [MinIO SUBNET](https://min.io/pricing?jmp=docs) 用户可以 [登录](https://subnet.min.io/) 并创建与重新同步相关的新 issue。通过 SUBNET 与 MinIO Engineering 协调，可以确保重新同步成功并恢复正常运行，包括性能测试和健康诊断。
>
> 社区用户可以通过 [MinIO Community Slack](https://slack.min.io) 寻求支持。社区支持仅按尽力而为原则提供，不对响应速度提供 SLA。

<a id="id3"></a>

## 要求 {#minio-bucket-replication-serverside-resynchronize-requirements}

### MinIO 部署必须在线 {#minio}

重新同步要求源部署和目标部署都在线，并且能够接受读写操作。源端 *必须* 具备到远端的完整网络连通性。

远端部署可以处于“不健康”状态，即发生了部分或全部数据丢失。只要源端和目标端保持连通，重新同步就可以修复这些数据丢失问题。

### 重新同步要求现有复制配置 {#id4}

重新同步要求健康的源部署已经为不健康的目标存储桶配置好了复制配置。此外，重新同步仅适用于使用 [existing object replication](/docs/administration/bucket-replication/#minio-replication-behavior-existing-objects) 选项创建的那些复制规则。

使用 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 查看健康源存储桶已配置的复制规则和目标。

### 复制要求对象加密设置匹配 {#id5}

MinIO 支持复制使用 [SSE-KMS](/docs/administration/server-side-encryption/server-side-encryption-sse-kms/#minio-encryption-sse-kms) 和 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 加密的对象：

- 对于使用 SSE-KMS 加密的对象，MinIO *要求* 目标存储桶支持使用与源存储桶对象 加密时 *相同的密钥名称* 对对象执行 SSE-KMS 加密。
- 对于使用 [SSE-S3](/docs/administration/server-side-encryption/server-side-encryption-sse-s3/#minio-encryption-sse-s3) 加密的对象，MinIO *要求* 目标存储桶同样支持 SSE-S3 对象加密，而不考虑密钥名称。

在复制过程中，MinIO 会先在源存储桶上对对象进行 *解密*，再通过网络传输未加密的 对象。目标 MinIO 部署随后会使用目标端的加密设置重新对该对象进行加密。 因此，MinIO *强烈建议* 在源端和目标端部署上都 [启用 TLS](/docs/operations/network-encryption/#minio-tls)，以确保对象在传输过程中的安全。

MinIO *不* 支持复制客户端加密对象（SSE-C）。

### 复制要求使用 MinIO 部署 {#id6}

MinIO 服务端复制仅适用于 MinIO 部署之间。 源端和目标端部署 *都必须* 运行版本匹配的 MinIO Server。

如需在任意 S3 兼容服务之间配置复制，请使用 [`mc mirror`](/docs/reference/minio-mc/mc-mirror/#command-mc.mirror)。

### 复制要求启用版本控制 {#id7}

MinIO 依赖 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 提供的不可变性保护来支持 复制和重新同步。

使用 [`mc version info`](/docs/reference/minio-mc/mc-version-info/#command-mc.version.info) 验证源存储桶和远端存储桶的版本控制状态。 必要时使用 [`mc version enable`](/docs/reference/minio-mc/mc-version-enable/#command-mc.version.enable) 命令启用版本控制。

如果你在源存储桶中将某个前缀或文件夹排除在版本控制之外，MinIO 就无法复制该文件夹 或前缀中的对象。

### 复制要求对象锁定状态匹配 {#id8}

MinIO 支持复制受 [WORM 锁定](/docs/administration/object-management/object-retention/#minio-object-locking) 保护的对象。 两个复制存储桶 *都必须* 启用对象锁定，MinIO 才能复制被锁定的对象。 对于主动-主动配置，MinIO 建议在两个存储桶上使用 *相同的* 保留规则，以确保跨站点 行为一致。

根据 S3 的行为要求，你必须在创建存储桶时启用对象锁定。 随后，你可以在任何时候配置对象保留规则。 在开始此过程 *之前*，请先在状态异常的目标存储桶上配置所需规则。

## 注意事项 {#id9}

### 重新同步需要时间 {#id10}

重新同步是一个后台过程，会持续检查源 MinIO 存储桶中的对象，并在需要时将其复制到远端。完成复制所需的时间会因对象数量和大小、到远端 MinIO 部署的吞吐量以及源 MinIO 部署上的负载而异。由于这些变量的存在，总完成时间通常无法预测。

MinIO 建议在同步完成之前，通过配置负载均衡器或代理，仅将流量导向健康集群。以下命令可帮助了解重新同步状态：

- 在源端执行 [`mc replicate resync status`](/docs/reference/minio-mc/mc-replicate-resync/#mc.replicate.resync.status) 以跟踪重新同步进度。
- 在源端和远端执行 [`mc replicate status`](/docs/reference/minio-mc/mc-replicate-status/#command-mc.replicate.status) 以跟踪正常复制数据。
- 在源端和远端都运行 `mc ls -r --versions ALIAS/BUCKET | wc -l`，以验证两端的对象总数和对象版本总数。

## 在数据丢失后重新同步对象 {#id11}

此过程使用现有的 [MinIO replication configuration](/docs/administration/bucket-replication/#minio-bucket-replication-serverside)，将缺失数据恢复到参与该配置的某个 MinIO 部署。具体来说，一个健康的 MinIO 部署（即 `SOURCE`）会将其现有数据同步到不健康的 MinIO 部署（即 `TARGET`）。

此过程假定 `SOURCE` 已存在一个 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，并且该别名具有配置复制所需的 [necessary permissions](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway-permissions)。

你可以对每个需要重新同步的存储桶重复执行此过程。每个存储桶同时最多只能运行一个复制作业。

### 1) 列出健康源端上已配置的复制目标 {#id12}

运行 [`mc replicate ls`](/docs/reference/minio-mc/mc-replicate-ls/#command-mc.replicate.ls) 命令，列出健康 `SOURCE` 部署上针对需要重新同步的 `BUCKET` 已配置的远程目标。

```shell
mc replicate ls SOURCE/BUCKET --json
```

- 将 `SOURCE` 替换为源 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为要作为重新同步源的存储桶名称。

输出类似如下：

```shell
{
   "op": "",
   "status": "success",
   "url": "",
   "rule": {
      "ID": "cer1tuk9a3p5j68crk60",
      "Status": "Enabled",
      "Priority": 0,
      "DeleteMarkerReplication": {
         "Status": "Enabled"
      },
      "DeleteReplication": {
         "Status": "Enabled"
      },
      "Destination": {
         "Bucket": "arn:minio:replication::UUID:BUCKET"
      },
      "Filter": {
         "And": {},
         "Tag": {}
      },
      "SourceSelectionCriteria": {
         "ReplicaModifications": {
            "Status": "Enabled"
         }
      },
      "ExistingObjectReplication": {
         "Status": "Enabled"
      }
   }
}
```

输出中的每个文档都表示一条已配置的复制规则。 `Destination.Bucket` 字段指定该存储桶上某条规则对应的 ARN。 找出你希望从中重新同步对象的存储桶对应的正确 ARN。

### 2) 启动重新同步过程 {#id13}

运行 [`mc replicate resync start`](/docs/reference/minio-mc/mc-replicate-resync/#mc.replicate.resync.start) 命令以开始重新同步过程：

```shell
mc replicate resync start --remote-bucket "arn:minio:replication::UUID:BUCKET" SOURCE/BUCKET
```

- 将 `--remote-bucket` 的值替换为 `TARGET` MinIO 部署上不健康 `BUCKET` 的 ARN。
- 将 `SOURCE` 替换为源 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。
- 将 `BUCKET` 替换为健康 `SOURCE` MinIO 部署上的存储桶名称。

该命令会返回一个重新同步作业 ID，表示该过程已经开始。

### 3) 监控重新同步 {#id14}

在源部署上使用 [`mc replicate resync status`](/docs/reference/minio-mc/mc-replicate-resync/#mc.replicate.resync.status) 命令跟踪已接收的复制数据：

```shell
mc replicate resync status ALIAS/BUCKET
```

输出类似如下：

```shell
mc replicate resync status /data
Resync status summary:
● arn:minio:replication::6593d572-4dc3-4bb9-8d90-7f79cc612f01:data
   Status: Ongoing
   Replication Status | Size (Bytes)    | Count
   Replicated         | 2.3 GiB         | 18
   Failed             | 0 B             | 0
```

重新同步过程完成后，**Status** 会更新为 `Completed`。

### 4) 后续步骤 {#id15}

- 如果 `TARGET` 存储桶的损坏已波及复制规则，则必须重新创建这些规则，使其与之前的复制配置一致。更多指导请参见 [启用双向服务端存储桶复制](/docs/administration/bucket-replication/enable-server-side-two-way-bucket-replication/#minio-bucket-replication-serverside-twoway)。
- 执行基础验证，确认复制配置中的所有存储桶在 [`mc ls`](/docs/reference/minio-mc/mc-ls/#command-mc.ls) 和 [`mc stat`](/docs/reference/minio-mc/mc-stat/#command-mc.stat) 等命令下显示出相近的结果。
- 在恢复所有复制规则并验证站点间复制之后，你可以配置负责管理连接的反向代理、负载均衡器或其他网络控制平面，使其恢复向已重新同步的部署发送流量。