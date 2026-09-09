---
title: "原生健康检查与 Distroless 镜像"
linkTitle: "健康检查"
description: "设计笔记：silo 二进制为何新增 healthcheck 子命令、mc ready 为何必须退役、单二进制 Distroless 镜像如何规划。"

weight: 10
type: docs
icon: fa-solid fa-heart-pulse
---

> **状态**：P1（子命令，`2ff594f4b`）与 P2（distroless 镜像 + CI 门禁，`4c34d2309`）已在 `pgsty/silo` 落地；P3（Helm 探针）与 P4（文档）待办 · **决策日期**：2026-08-06 · **归属**：[`pgsty/silo`](https://github.com/pgsty/silo)（命令、镜像、Helm chart）与本站（文档）

Silo 将新增一个原生的 `silo healthcheck` 子命令，并在现有容器镜像之外发布一个新的 **Distroless** 镜像变体——里面真正要紧的文件只有一个：`silo` 二进制。本文在动手实现之前把推理过程和设计决策记录下来，让代码有一份可以对照检验的规格，也让"为什么要做成这样"永远有出处可查。

## 背景 {#background}

今天的发布镜像（`docker.io/pgsty/silo`）基于 `ubi-micro`，装了四样活动部件：`silo` 服务端、`mcli` 客户端（带 `mc` 别名）、一个静态链接的 `curl`，以及一个 POSIX shell 入口脚本。Compose 示例用镜像内置的客户端做容器健康检查：

```yaml
healthcheck:
  test: ["CMD", "mc", "ready", "local"]
```

这套安排继承自上游 MinIO，其脆弱性有案可查：`mc` 曾短暂从镜像中消失，用户的健康检查随之失效，"除了禁用别无选择"（[#9](https://github.com/pgsty/silo/issues/9)）。上游自己的历史也如出一辙——2023 年 MinIO 切换到 `ubi-micro` 丢掉 `curl` 时，维护者的答复是更加依赖 `mc ready local`（minio/minio#18373、#18389）；而上游 `minio/minio` 如今已经归档，其二进制自始至终只有 `server` 一个子命令。上游不会有人来修这件事了。

Distroless 镜像把这个问题逼到了台面上。没有 shell、没有 `curl`、没有 `mc`——这正是 Distroless 的定义。容器里唯一保证存在的程序就是服务端二进制本身。如果这个镜像还想拥有 Docker 层面的健康检查，就只能由这个二进制自己来提供。

## `mc ready` 为何必须从探针岗位上退役 {#why}

细读 `mc` 的实现（`cmd/ready-main.go`）会发现：现在的健康检查是"碰巧能用"，不是设计出来的。四个彼此独立的缺陷：

1. **它自己永远不报告失败。**`mc ready` 是一个"等到就绪为止"的循环：每 5 秒重试一次，只在成功时以零退出码结束，连接被拒也不会跳出循环。作为 Docker healthcheck 使用时，"unhealthy" 的判定完全来自 Docker 的 `timeout` 把进程杀掉——探测语义是 SIGKILL 的副作用。
2. **它检查的尺度是错的。**`mc ready` 请求的是 `/minio/health/cluster`——全集群写 quorum。于是每个容器的"健康"反映的都是整个集群的状态，这恰好是 Kubernetes 文档明确警告的级联失败反模式：quorum 一丢，所有节点同时被判不健康。
3. **它有隐藏故障模式。** 它需要可写的 `~/.mc` 配置目录（只读 rootfs 或 OpenShift 任意 UID 下，服务器明明健康、探测却先失败了）；首次运行会向 stdout 打印配置创建噪音；内置的 `local` 别名硬编码为 `http://localhost:9000`——一旦启用 TLS 或改了端口就立即失效，上游用户对此公开抱怨过。
4. **它是镜像里捆绑第二个二进制的最后一个功能性理由。**`mcli` 和钉版本的静态 `curl` 都有持续的供应链与维护成本（curl 被钉死在 v8.11.0，因为后续版本砍掉了 aarch64 构建），而这些事一个现有二进制的子命令用约 150 行代码就能做完。

## 决策 {#decisions}

三条轨道，刻意解耦：

| # | 决策 |
| --- | ---------- |
| **D1** | `silo` 二进制新增 `healthcheck` 子命令——服务端现有 `/minio/health/*` 端点的匿名 HTTP 薄客户端。它随每一个构建发布，所有镜像和裸机安装同时获得这项能力。 |
| **D2** | **现有镜像不动**。`mcli`、`curl`、shell 入口脚本、`mc ready local` 示例全部保留。当前镜像的用户若想用新探针，覆盖自己的 `healthcheck.test` 即可选择加入——不拿走任何东西，不移动任何默认行为。 |
| **D3** | 并行发布一个新的 **Distroless 变体** 作为试点：单二进制、无 shell、原生 `HEALTHCHECK` 内置。试点验证充分后，它将成为推荐默认并完成切换；无论如何，经典镜像都会为兼容性继续保留。 |

D2 与 D3 回答了那个显而易见的问题——"为什么不直接给主镜像瘦身？"——因为主镜像的内容物本身就是兼容性表面。[#9](https://github.com/pgsty/silo/issues/9) 的存在，正是因为这个表面曾经在用户脚下被抽换过一次。Distroless 镜像用一个新名字承载一份新契约：在它接受检验期间，没有任何人现有的健康检查、`docker exec mc` 习惯或入口脚本假设会被破坏。

## `silo healthcheck` 命令 {#command}

```text
silo healthcheck [FLAGS] [CHECK]

CHECK —— 位置参数，与 /minio/health/<path> 一一对应：
  live          进程在提供服务（默认；不触碰任何外部系统）
  ready         live + KMS 与 etcd 可达（若有配置）
  cluster       全集群写 quorum
  cluster-read  全集群读 quorum

FLAGS：
  --address value   探测目标 host:port（EnvVar: MINIO_ADDRESS；默认 ":9000"，
                    空 host 补全为 127.0.0.1）
  --url value       完整基址覆盖（http[s]://host:port）；优先于 --address
                    与 TLS 自动判定（EnvVar: MINIO_HEALTHCHECK_URL）
  --maintenance     仅 cluster 有效：附加 ?maintenance=true——问"现在把这个
                    节点下线安全吗？"（HTTP 412 = 不安全，会破坏高可用）
  --timeout value   总超时；默认：live/ready 5s，cluster* 15s
  另继承全局旗标：--certs-dir、--config-dir、--json、--quiet

退出码：  0 = 健康 / 可安全操作 · 1 = 其余一切
输出：    单行，例如
  live: ok (200, 2ms)
  cluster: unhealthy (503) server-status=iam-offline write-quorum=3 healing-drives=2
```

这个形态背后的设计原则：

1. **薄客户端，单一事实源。** 命令永远只是规范健康 API 的 HTTP 客户端，绝不在进程内重新实现任何检查——"健康"的语义只存在于一个地方：服务端处理器。
2. **CLI 词汇 = API 词汇。** 检查名就是端点路径。没有新概念要学，没有第二套词汇要同步。
3. **共享服务器自己的配置。** 端口来自服务器同一份 `--address`/`MINIO_ADDRESS` 契约；http 还是 https，由服务器启动时自己执行的那个证书检查（certs 目录下的 `public.crt` + `private.key`）来决定。这是 Traefik `healthcheck` 的模式——最接近的业界先例，它从与服务端相同的静态配置里解析 ping 端点——并把 Traefik 留成 `// TODO` 的 TLS 处理真正实现掉。这也是对 `mc ready`"端口靠猜"缺陷的正面修复。
4. **默认检查是节点本地的。**`live` 回答"这个进程是否在服务"，而这是单容器健康状态唯一应该回答的问题。集群尺度的检查存在，但只放在显式参数之后，并沿用 `mc ready` 的 `--cluster-read`/`--maintenance` 词汇，让运维语言得以延续。
5. **退出码只有 0 和 1。** Dockerfile 参考手册明文保留退出码 2（`vault status` 用 2 表示 sealed，是现成的反面教材）。丰富的诊断信息放进那一行输出里——Docker 会把探测输出的前 4096 字节存进 `docker inspect`，而命令会把服务端的诊断响应头（`x-minio-server-status`、`x-minio-write-quorum`、`x-minio-healing-drives`）解码进去；这些正是裸 `curl -f` 会丢掉的细节。
6. **跳过 TLS 证书校验，v1 不提供开关。** 这是对匿名端点的环回自探，不传输任何数据——而 kubelet 对 HTTPS `httpGet` 探针的文档行为恰好也是跳过校验。与之对齐意味着同一套 TLS 部署在 Docker 和 Kubernetes 下得到同一个结论；默认校验只会制造假阴性，因为自签服务器证书极少包含 `127.0.0.1` 的 SAN。

两条从源码里挖出来的实现约束——它们是承重墙，不是风格偏好：

- **请求必须严格匿名。** 健康路由之所以能豁免保留路径守卫，仅限于被服务器判定为匿名的请求；带上 `Authorization` 头会改变请求的分类，结果不是得到应答而是被 *拒绝*（`ErrAllAccessDisabled`）。
- **HTTP 传输层必须设置 `Proxy: nil`。** 容器经常继承 `HTTP_PROXY` 却没有把 `127.0.0.1` 写进 `NO_PROXY`；环回探测绝不能被路由进公司代理。（Traefik 的 healthcheck 出于同样的原因特意这样做了。）

还有一个看似随意、实则不然的数字：cluster 检查的默认超时是 15 秒，因为服务端评估集群健康时自身受 10 秒 `cluster_deadline` 约束——客户端若在 5 秒就放弃，等不到服务器深思熟虑后给出的 503，连同所有诊断头一起丢失。对抗性评审后补充了两个细节：`--url` 支持环境变量（`MINIO_HEALTHCHECK_URL`），因为探针进程看不到服务端的命令行——当服务端的地址或 TLS 配置来自 CLI 参数时，这是矫正内置 `HEALTHCHECK` 的正式途径；另外任何外层（Docker）超时都必须大于探针自身的截止时间，否则探针会在打印诊断行之前先被 SIGKILL。

## 这些端点到底在做什么 {#endpoints}

下表对照的是处理器源码，不是文档转述——并且修正了一个常见的误读：

| 端点 | 返回 200 的条件 | 失败形态 | 备注 |
| --- | --- | --- | --- |
| `/minio/health/live` | 几乎总是——**对象层尚未初始化时也返回 200**（该状态只通过 `x-minio-server-status: offline` 响应头传递） | 请求队列饱和时 503 | 不触碰外部系统；唯一安静到适合高频探测的端点 |
| `/minio/health/ready` | 同 `live`，**外加** KMS 能生成密钥、etcd 能应答读取——各自仅在配置了的情况下 | KMS/etcd 故障；队列饱和 | **没有 KMS 与 etcd 时，`ready` 与 `live` 是同一条代码路径** |
| `/minio/health/cluster` | 对象层、桶元数据、IAM 均已初始化，**且每一个纠删集** 都有写 quorum | 503 附带 quorum 诊断头；带 `?maintenance=true` 时失败为 **412** | 每次评估失败都会在服务端写一条日志——不要高频轮询它 |
| `/minio/health/cluster/read` | 上一行的读 quorum 版本 | 同上 | |

值得点破的推论：`live` 和 `ready` 是 *存活* 级别的信号——它们不能告诉你节点能否服务对象，只有 `cluster` 这一对能。这正是 cluster 端点必须远离单容器探针的原因（尺度错位、日志噪音、级联重启），也正是它适合回答运维问题的原因——"我现在可以把这个节点下线吗？"（`--maintenance`：200 表示安全，412 表示会失去高可用）。

## Distroless 变体 {#distroless}

**基底**：`gcr.io/distroless/static-debian12`——够用，因为 `silo` 以 `CGO_ENABLED=0` 构建。这个基底恰好带着服务器真正需要 rootfs 提供的四样东西：CA 证书（KMS/webhook/STS 出站 TLS）、tzdata、`/tmp`，以及带 `root`/`nonroot` 条目的 `/etc/passwd`。没有 shell、没有包管理器、没有 libc。

契约草图：

```dockerfile
FROM gcr.io/distroless/static-debian12:latest
COPY silo /usr/bin/silo
COPY LICENSE NOTICE CREDITS /licenses/
ENV HOME=/tmp
# /data 在镜像层内创建、全员可写——见 issue #55：
# 这里已经没有入口脚本可以在运行时修补属主了。
VOLUME ["/data"]
EXPOSE 9000
HEALTHCHECK --interval=30s --timeout=10s --start-period=2m --start-interval=2s --retries=3 \
  CMD ["/usr/bin/silo", "healthcheck", "ready"]
ENTRYPOINT ["/usr/bin/silo"]
```

草图里折叠的决策：

- **`ENTRYPOINT` 就是二进制本身。**`docker run pgsty/silo:distroless server /data`——没有 argv 翻译脚本，因为没有 shell 来跑脚本。经典镜像的 `MINIO_USERNAME`/`MINIO_GROUPNAME` 降权路径（依赖 GNU `chroot` 和可写的 `/etc/passwd`）在此变体中 **不受支持**；受支持的机制是 `--user` / Kubernetes `runAsUser`。
- **`/data` 在镜像层内创建、mode 0777，试点期默认用户保持 root。** Issue [#55](https://github.com/pgsty/silo/issues/55) 证明了：只声明 `VOLUME ["/data"]` 而不创建它，会让 *所有* 非 root 运行方式失败，而且事后没有任何入口脚本能修补——Distroless 里更是压根没有入口脚本。在层内以全员可写方式创建它，是唯一让全部权限模式（包括 `--user`）都能工作的选项，同时与经典镜像保持即插即用的对等；其暴露面被"镜像只运行一个进程"这一事实所限定。nonroot 默认（uid 65532）的姿态经过考虑后推迟：它会在 UID 不匹配时破坏文档记载的 bind-mount 工作流，而试点的任务是测量摩擦，不是制造摩擦。晋升为默认推荐时再议，可能以 `-nonroot` 标签的形式出现。
- **健康检查内置、exec 形式。** Shell 形式的 `HEALTHCHECK` 字符串需要 `/bin/sh`，在这里不可能存在；JSON 数组形式是唯一选择。Compose 会自动继承镜像的 `HEALTHCHECK`（逃生门是 `disable: true`），所以这个变体的 compose 用户零配置就能得到可用的 `depends_on: condition: service_healthy`。选 `ready` 而不是 `live`，是因为 Docker 健康状态的主要用途是 *门控*（启动顺序），那是就绪语义——况且在没有 KMS/etcd 时两者本就相同。
- **一项发布前必须完成的验证**：`HEALTHCHECK` 是 Docker 扩展，不在 OCI 镜像规范里（opencontainers/image-spec#749 至今开放），OCI 媒体类型的构建会静默丢弃它。发布流水线必须断言推送后的 manifest 上 `docker inspect` 能看到 `Health` 配置，否则就调整构建的媒体类型直到能看到为止。
- **命名**：`docker.io/pgsty/silo:<RELEASE>-distroless`，外加滚动的 `distroless` 标签。服务端仓库新增 `Dockerfile.distroless`——它没有任何下载阶段，完全离线，因此可以在每次发布的 CI 里真实构建并断言，顺带堵上 #55 记录的那个"门禁测的是合成镜像而非发布镜像"的覆盖缺口。
- **变体文档里要诚实写明用户失去了什么**：没有 `docker exec <container> sh` 式调试（改用 `docker debug` / `kubectl debug` 临时容器）；镜像内没有 `mc`（改用 `pgsty/mc` 镜像或宿主机安装的 `mcli`）；没有 `MINIO_USERNAME` 路径（改用 `--user`）。

## Kubernetes 完全不需要镜像配合 {#kubernetes}

值得明说，因为它划定了问题的边界：Kubernetes **完全忽略** Dockerfile 的 `HEALTHCHECK`——kubelet 探针在 Pod spec 里配置，从容器外部以 `httpGet` 请求执行。因此两个镜像变体在 Kubernetes 下的探测方式完全相同：

```yaml
startupProbe:            # 启动预算：5s × 60 = 5 分钟，护住大规模 IAM 加载
  httpGet: { path: /minio/health/live, port: 9000 }
  periodSeconds: 5
  failureThreshold: 60
livenessProbe:           # 何时重启：只看进程级信号
  httpGet: { path: /minio/health/live, port: 9000 }
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3
readinessProbe:          # 何时摘除流量：可以包含硬依赖（KMS/etcd）
  httpGet: { path: /minio/health/ready, port: 9000 }
  periodSeconds: 15
  timeoutSeconds: 5
  failureThreshold: 3
```

任何这类配置旁边都应放上三条警示：`cluster` 端点永远不进探针（放进 liveness 意味着 quorum 一丢整个集群同时重启；放进 readiness 会与分布式引导互相纠缠——chart 的 headless service 设置 `publishNotReadyAddresses: true` 正是为此）；`live` 在请求队列持续饱和时会有意返回 503，所以饱和节点约 90 秒后被重启是设计使然；`scheme: HTTPS` 下 kubelet 跳过证书校验，自签部署无需任何额外配置。

Silo 的 Helm chart 目前 **一个探针都没有**（上游的 chart 也一样，尽管其文档写了探针示例）。把上面三个探针补进 chart 是计划中的独立后续项——它不依赖任何一条镜像轨道，而且相对上游这是差异化优势，不是兼容性风险。

## 落地路线 {#rollout}

| 阶段 | 范围 | 仓库 |
| --- | --- | --- |
| **P1** | `silo healthcheck` 子命令 + 测试；随下一个发布版二进制交付（所有镜像同时继承该能力，镜像行为零变化） | `pgsty/silo` |
| **P2** | `Dockerfile.distroless` + CI 构建与健康门禁 + 以试点身份发布 `-distroless` 标签 | `pgsty/silo` |
| **P3** | Helm chart：补三探针；刷新过期的默认镜像标签 | `pgsty/silo` |
| **P4** | 文档：命令参考、探针指南、Distroless 迁移说明；试点反馈 → 决定是否将 Distroless 晋升为推荐默认 | 本站 |

贯穿所有阶段的兼容性承诺：经典镜像的内容物与示例不变；`mc ready local` 在今天能用的地方继续能用；健康 HTTP API 不动（子命令纯属增量）；`/minio/health/*` 路径与本分支的其他所有 `/minio/*` 路由一样，作为兼容性表面继续冻结。

## 推迟的决定 {#deferred}

记录在案，免得将来从零重新争论：

- **`--wait` 模式**（阻塞等待直至健康——`mc ready` 那个循环唯一真正的正当用途）：推迟——仓库内暂无消费者，日后添加完全向后兼容，旗标命名空间已预留。
- **Distroless 镜像默认 nonroot**：推迟至晋升默认推荐时再议，理由见上文。
- **`--json` 的输出 schema**：遵循全局旗标惯例；确切 schema 在实现时定稿并写入命令参考。
