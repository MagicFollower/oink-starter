---
title: "Silo 与 MinIO 服务端兼容性"
linkTitle: "服务端 Silo"
description: "经过源码验证的 Silo 服务端分叉兼容性审计：二进制、配置、S3 与管理行为、存储内部协议、软件包、容器与 Helm。"

weight: 10
type: docs
icon: fa-solid fa-server
---

Silo 是持续维护的 MinIO 服务端分叉。它保留了面向 S3 客户端和磁盘数据的兼容性，但 **绝不是一次在运维层面完全无感的二进制改名**。本页是从上游基线迁移到 2026-08-06 所准备 Silo 源码时的兼容性契约。

> [!WARNING]
> **替换 MinIO 部署前请先阅读本页。** 二进制、软件包、服务账号、systemd 单元、默认本地配置目录、容器路径、Helm 资源名、内嵌控制台、更新行为、若干授权判定及部分错误响应已经改变；数据盘和 `MINIO_*` 配置命名空间没有随产品改名。

## 审计范围与方法 {#scope}

这是一份源码审计，而不是对 release note 的简单汇编。

| 边界      | 审计值                                                                                                                                                 |
|:--------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| 上游基线    | [`minio/minio@7aac2a2c5b7c882e68c1ce017d8256be2feea27f`](https://github.com/minio/minio/commit/7aac2a2c5b7c882e68c1ce017d8256be2feea27f)，2026-02-11 |
| Silo 快照 | `pgsty/silo@219670d3176a5b27ded60914390d5ee7e763cf58`，2026-08-06                                                                                    |
| 提交集合    | `7aac2a2c..219670d3`：共 96 个可达提交；审计时其中 93 个位于 `origin/main`，最后 3 个已在本地提交                                                                             |
| 源码净差异   | 523 个文件，新增 36,715 行，删除 21,450 行                                                                                                                     |
| 解释口径    | 记录最终快照的行为；后来被替换或删除的中间状态，不会被写成当前行为                                                                                                                   |

范围内每个提交都经过检查。Release 与 Security 文章只用来索引“预期变化”，随后仍以最终实现、测试、依赖图、构建配方、软件包载荷、容器入口和渲染后的 Helm 清单逐项核实。[完整提交覆盖账本](#ledger)确保文档、CI 或被后续替代的提交也不会静默漏出范围。

该范围按 Git 可达性定义，而不是按 author date 排序。因此它包含 `d4cd4b433`：该提交的作者日期是 2025 年 12 月，但后来才接入基线后的提交图；它不是一条未记录的额外基线。

已打标签的 [`RELEASE.2026-08-04T00-00-00Z`](https://github.com/pgsty/silo/releases/tag/RELEASE.2026-08-04T00-00-00Z) 停在 `d88f46cce`，比本次审计 HEAD 少 18 个提交。因此本页记录的是 **2026-08-06 准备中的源码状态**，并不声称最后 18 个变化已经进入公开软件包、镜像、标签或线上网站。

## 兼容性总览 {#matrix}

| 表面            | 状态                    | 实际结论                                                                                   |
|:--------------|:----------------------|:---------------------------------------------------------------------------------------|
| S3 线协议        | 除明确列出的例外外保持兼容         | 路由、XML/JSON 模式、SigV4、S3 头、端口与常规错误码沿用 MinIO 契约；下列安全与正确性修复会有意拒绝部分旧代码曾接受的请求               |
| 数据盘           | 兼容                    | `.minio.sys`、纠删码元数据、桶/对象布局、修复、复制和加密格式保留原名与模式；被污染或不可用的元数据会更早被拒绝                         |
| 配置            | 基本兼容                  | 既有 `MINIO_*` 变量、配置键、KMS/KES、IAM、通知与存储设置都保留；用户级默认目录变为 `~/.silo`，并带有确定性的 `~/.minio` 回退   |
| 指标与自动化 API    | 兼容                    | `minio_*` Prometheus 指标、`/minio/*` 路由、`x-minio-*` 头、管理/S3 错误标识及 release tag 语法不变       |
| 二进制与分发        | 已改名                   | `minio` 变为 `silo`；软件包、单元、镜像、Chart、归档、校验文件及路径改用 Silo 身份；服务端二进制没有安装兼容别名                  |
| 运行时身份         | 已改变                   | CLI 文本、启动横幅、HTTP `Server`、User-Agent 应用名、FTP 横幅、日志名、支持链接以及部分人类可读错误改为 Silo              |
| 上游网络服务        | 已禁用                   | 原地更新、更新轮询、callhome、SUBNET 注册与诊断上传不会联系 MinIO 服务                                         |
| 授权与安全         | 有意收紧                  | OIDC HMAC token、不安全 LDAP 失败、伪造复制元数据、对象资源对受保护桶写操作的越权、策略输入遮蔽、歧义版本 ID 以及若干畸形节点间请求均改变行为    |
| 内嵌 UI 与 Go 依赖 | 通过兼容 import path 使用分叉 | Silo Console、MCLI 与 Silo Pkg 由 `replace` 选中，同时保留 `github.com/minio/...` 模块/import path |
| 混合版本集群        | 此迁移边界不支持              | 私有 `ReadMultiple` storage-REST 操作已删除，却没有提升 storage REST v63；所有节点应作为同一构建整体升级            |

## 明确保留的兼容契约 {#same}

### 协议、存储与配置名称 {#stable-contract}

下列 MinIO 标识属于兼容性标识，并非尚未完成的品牌替换，必须继续可见：

- Go 模块路径 `github.com/minio/minio` 及继承的 `github.com/minio/...` import；
- `MINIO_*` 环境变量命名空间，包括 `MINIO_ROOT_USER`、`MINIO_ROOT_PASSWORD`、`MINIO_VOLUMES`、`MINIO_OPTS` 和通知变量；
- `/minio/*` 下的 S3/管理路由、`x-minio-*` 头、MinIO 特有 S3 扩展及既有 API 错误码；
- `minio_*` Prometheus 指标名称；
- `.minio.sys` 内部卷及所有既有磁盘元数据名称；
- 默认 S3 端口 `9000`、既有 `--address` / `--console-address` 参数，以及 `RELEASE.YYYY-MM-DDTHH-MM-SSZ` 标签格式；
- 配置 KV 格式、IAM 数据、KMS/KES 配置、加密元数据、桶元数据、复制状态与修复状态。

自动化 rebrand 基线记录了 137 个兼容 import、437 个环境变量名、19 个指标命名空间、84 个头、334 条路由、1 个内部根目录、3 个 Grid 命名空间、15 个 storage-REST 标识、58 个策略标识和 9,014 个导出符号。Guard 会把任何未评审的基线漂移视为兼容性失败。

同一组数据盘从 MinIO 切到 Silo 时不需要复制数据或重写元数据。但这并不意味着一切畸形历史对象都会继续被接受：下文的存储加固会拒绝不安全路径、非法纠删码几何、负 part size 以及过去可能继续向下传播的污染元数据。

### 源码兼容性 {#source-compatibility}

服务端模块仍为 `github.com/minio/minio`。Silo 在不强迫调用方改写 import 的情况下选择维护中的分叉：

```go
replace github.com/minio/console => github.com/pgsty/silo-console ...
replace github.com/minio/mc      => github.com/pgsty/mc ...
replace github.com/minio/pkg/v3  => github.com/pgsty/silo-pkg/v3 v3.11.0
```

这保留了大部分源码兼容性，但不表示所有私有或导出 Go 符号永久冻结。内部 `ReadMultiple` 存储接口已删除，所选 `silo-pkg` 版本也包含[依赖章节](#dependencies)所述的开发者可见变化。

维护中的源码 remote 是 `github.com/pgsty/silo`，默认分支为 `main`；原 `minio` 分支已归档。`go install github.com/minio/minio@...` 仍会解析到上游项目，而不是 Silo，因此需要 clone Silo 仓库或使用显式 module `replace`。贡献不再要求 MinIO CLA，但提交必须带 DCO sign-off（`git commit -s`）。

## 身份、二进制与外联服务变化 {#identity}

| 表面              | 上游基线                              | Silo 快照                                                                               | 兼容性影响                                            |
|:----------------|:----------------------------------|:--------------------------------------------------------------------------------------|:-------------------------------------------------|
| 服务端可执行文件        | `minio` / `minio.exe`             | `silo` / `silo.exe`                                                                   | 脚本及绝对路径必须修改；归档、软件包和镜像不会安装 `/usr/bin/minio` 服务端别名 |
| 版本输出            | MinIO 身份                          | Silo release/commit/runtime、AGPL、上游版权、PGSTY 修改版权与 MinIO 技术沿革                          | 解析器应依赖稳定字段，不能 grep `MinIO` 文案                    |
| 本地配置主目录         | `~/.minio`                        | 新用户主目录默认 `~/.silo`                                                                    | 见下述回退规则；与数据盘无关                                   |
| HTTP 身份         | `Server: MinIO` 与 MinIO 应用 UA     | `Server: Silo`；内部 batch/fan-out/perf UA 使用 `silo-*` / Silo 名称                         | `x-minio-*` 等协议头保持不变；按产品身份匹配的监控需要调整              |
| 人类可读文本          | MinIO 横幅、帮助、错误、样例、FTP 欢迎语、支持链接    | Silo 身份；样例优先 `mysilo`                                                                 | 精确匹配文本的日志解析器和快照会变化；除另行列出外，状态码/错误码不变              |
| 集成可见标签          | MinIO NATS/Redis 连接名与 Veeam model | NATS 名 `Silo Notification`、Redis `CLIENT SETNAME Silo`、Veeam model `"Silo <release>"` | Broker 看板、连接名过滤器及 Veeam Inventory 展示会改变          |
| KMS 校验文案        | 带 MinIO 品牌的冲突错误                   | 中性的“同时存在 KMS/KES/static-key 配置”错误                                                     | 配置规则不变；精确匹配文本的自动化会改变                             |
| 更新器             | release 轮询与原地更新路径                 | 永久禁用                                                                                  | `MINIO_UPDATE` 会被解析但无法重新开启；管理更新路由保留并稳定失败，而不是消失   |
| Callhome/SUBNET | 注册、callhome、支持上传、内嵌 MinIO 支持公钥    | 为迁移保留配置解析但强制关闭；不注册/上传/POST；没有兜底加密公钥                                                   | 删除依赖 MinIO 运营服务的自动化；请求方公钥的 inspect 加密仍可用         |
| 内嵌控制台           | 上游快照已移除 Console                   | Silo Console v2.1.1，中英双语、Metrics V3、无 SUBNET UI                                       | 浏览器行为和资源发生变化；S3/Admin API 仍由服务端契约约束              |
| OCI 内置客户端       | 没有维护分叉契约                          | `/usr/bin/mcli` 与 `/usr/bin/mc -> mcli`                                               | 这里的 `mc` 只是客户端兼容别名，从来不是服务端别名                     |
| 温层探针            | 临时对象内容为 `MinIO`                   | 同长度探针内容为 `Silo!`                                                                      | 只可能通过后端检查或清理失败残留观察到；协议语义不变                       |
| 日志轮转默认名         | `minio-*.log`                     | `silo-*.log`                                                                          | 按文件名匹配的采集器需要修改                                   |

被删除的 `/api/health/upload` 引用是一个 **出站 SUBNET URL 路径**，并不是 Silo 本地 HTTP 路由。正确的兼容性描述是“Silo 不再发起该 POST”，不能写成“删除了服务端 API”。

### 默认配置目录选择 {#config-dir}

未显式给出 `--config-dir` 时，Silo 会在启动时作一次选择：

| 用户主目录状态       | 选择目录       | 提示             |
|:--------------|:-----------|:---------------|
| 两者都不存在        | `~/.silo`  | 无              |
| 只有 `~/.silo`  | `~/.silo`  | 无              |
| 只有 `~/.minio` | `~/.minio` | 旧目录提示；不会移动任何文件 |
| 两者都存在         | `~/.silo`  | 歧义警告           |

`--config-dir` 始终优先。除非同时指定 `--certs-dir`，证书目录跟随所选配置目录。自动化应明确传入 `--config-dir`，不要依赖文件系统探测。

分叉只新增了三个会实质改变兼容行为的服务端配置控制项；不存在一套并行的 `SILO_*` 替换命名空间：

| 设置                                                                         | 用途                  | 默认值                     |
|:---------------------------------------------------------------------------|:--------------------|:------------------------|
| `MINIO_API_TRUSTED_PROXIES`                                                | 通用来源地址信任边界          | 未设置：精确保留历史 trust-any 行为 |
| `MINIO_IDENTITY_LDAP_STS_TRUSTED_PROXIES` / LDAP key `sts_trusted_proxies` | LDAP STS 失败限流的来源分桶  | 不信任代理；使用 socket peer    |
| `MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH`                                   | 受保护桶/对象 IAM 边界的临时回滚 | off                     |

通知 KV 注册修复不会重命名既有环境变量。`MINIO_UPDATE`、SUBNET 与 callhome 输入仅作为被忽略/迁移兼容的输入保留，详见下一节。`SILO_OPTS` 只出现在自动生成的 inspect helper 内，不是 `MINIO_OPTS` 的通用替代品。

### 更新器、callhome、SUBNET 与 inspect {#offline-services}

- 启动过程不再轮询 `dl.min.io`；release URL 与上游 minisign 根公钥已移除。
- 要求开启更新的 `MINIO_UPDATE` 值会产生警告并被忽略。公开及节点间管理更新 handler 仍然注册，返回 `MethodNotAllowed` 或稳定的“原地更新已禁用”错误。
- 旧 `subnet` 与 `callhome` 键仍可解析，让旧配置能够启动；注册状态恒为 false，Console 的 SUBNET 变量被清空，callhome 强制关闭，不上传诊断或许可证负载。
- Inspect 只会用请求方提供的公钥加密，不再回退到 MinIO 内置支持公钥。帮助脚本名为 `start-silo.sh`、执行 `silo`，`cluster.info` 只出现在请求方公钥流程中。
- 请通过包管理器、镜像滚动或编排器升级；不要把针对 Silo 的 `mc admin update` / `mcli admin update` 当作升级方案。

## 安装与部署兼容性 {#delivery}

### RPM、DEB 与 APK {#packages}

Linux amd64/arm64 软件包名为 `silo`，关键载荷如下：

```text
/usr/bin/silo
/usr/lib/systemd/system/silo.service
/etc/default/silo                 (config, noreplace)
/usr/lib/sysusers.d/silo.conf
/usr/share/doc/silo/LICENSE
/usr/share/doc/silo/NOTICE
```

软件包会创建无 home 的系统账号 `silo:silo`。它 **不会** chown 既有数据、迁移所有权、在安装时停止运行中的 MinIO 服务，也不会在包管理器层面对 `minio` 声明 `Provides`、`Obsoletes`、`Replaces` 或 `Conflicts`。因此两个包可以同时安装，但使用随附 unit 时两个服务不能同时运行。

`silo.service` 声明 `Conflicts=minio.service`，以 `silo:silo` 运行，先读 `/etc/default/minio`，再读 `/etc/default/silo`。随包的 Silo 文件没有有效赋值，所以管理员在后一个文件显式覆盖前，旧文件仍然生效。启动命令为：

```text
/usr/bin/silo server $MINIO_OPTS $MINIO_VOLUMES
```

切换 unit 前，必须确保 `silo` 可读取所有数据、证书、KMS 凭据和环境文件，并可写所有应写路径。由 `minio:minio` 持有的旧部署否则会启动失败。真正卸载软件包时会停止/禁用 `silo.service`；升级时 pre-remove 不会有意停掉运行中的服务。

### 容器镜像 {#container}

源码仓库是 `github.com/pgsty/silo`，预期镜像名是 `docker.io/pgsty/silo`；不存在 `pgsty/minio` 在 Registry 层必然重定向到它的承诺。

- 服务端只存在于 `/usr/bin/silo`；显式执行 `/usr/bin/minio ...` 会失败。
- entrypoint 会把 argv 第一个词 `minio` 翻译为 `silo`；当 argv 以 `server`、`fmt-gen` 或选项开头时前置 `silo`。因此常见的 `command: minio server /data` 形式仍然可用。
- 显式指定的 shell 或其他工具保持原样。
- 所有降权路径最终都使用 `exec`，服务端成为 PID 1 并收到 `SIGTERM` 完成优雅退出，不会再隔着 entrypoint 超时。
- 镜像默认 `HOME=/tmp`；任意 UID 或旧 `MINIO_USERNAME` 降权流程也会把 HOME 归一到可写目录。
- 端口 `9000`、`/data` 与 `MINIO_*` 接口不变。amd64/arm64 镜像 manifest 还包含经过校验的 MCLI `RELEASE.2026-08-06T00-00-00Z`（在本审计头之后的发布提交中提升）和只面向客户端的 `mc` 符号链接。
- OCI 法律材料位于 `/licenses/{LICENSE,NOTICE,CREDITS}`。

### Helm Chart {#helm}

继承的 `helm/minio` Chart、`helm-releases`、根 Chart 索引与重建脚本已删除。维护中的 Chart 为 `helm/silo`；20260806 发布的 Chart 版本为 `7.0.1`（审计头当时仍是 `7.0.0`）。

大多数 values 刻意保留原名，包括 `minioAPIPort`、`minioConsolePort` 及所有 `MINIO_*` 环境设置。迁移时需要关注：

- 镜像仓库改为 `pgsty/silo`；
- 生成的资源名和 label 跟随 Chart 名 `silo`；
- 默认服务账号改为 `silo-sa`；
- 证书/客户端挂载路径从 `/etc/minio/{certs,mc}` 改为 `/etc/silo/{certs,mc}`；
- 默认不再创建不安全的 `console/console123` 用户（`users: []`）；
- post-job 样例优先使用别名 `mysilo`，同时注册 `myminio`，让继承的 `customCommands` 仍能解析；
- 新 Chart 执行 `silo`，因此只把镜像回滚到旧 MinIO 镜像并不安全。

使用新 Chart 且需要保留旧 Kubernetes 对象身份时，应从完整旧 values 开始，至少设置：

```yaml
nameOverride: minio
fullnameOverride: <旧的完整 release 名>   # 例如 my-release-minio
serviceAccount:
  name: minio-sa
image:
  repository: pgsty/silo
mcImage:
  repository: pgsty/silo
```

应用前分别渲染新旧 Chart，比较 Service、selector、StatefulSet/Deployment、PVC 模板、Secret、服务账号、存储挂载、环境变量和端口。回滚时必须把 **Chart 与镜像一起回滚**。

### 归档、来源证明与法律文件 {#artifacts}

Release 归档命名为 `silo_<version>_<os>_<arch>`，包含可执行文件、README、LICENSE 和 NOTICE。校验清单名为 `silo_<version>_checksums.txt`；每个归档带有 SPDX JSON SBOM，校验集合配有无密钥 Sigstore bundle。静态、禁用 CGO、带 `kqueue` tag 的二进制只发布 Linux、macOS、Windows 的 amd64/arm64 组合；过去只做编译检查但从不分发的架构不再作为 release gate。RPM/DEB/APK 目标为 Linux amd64/arm64，使用 `YYYYMMDDHHMMSS.0.0` 形式的时间戳包版本（RPM release `1`），并有独立软件包校验清单。常规构建不再把构建机 GOPATH/GOROOT 写入二进制，提高了可复现性并消除路径泄漏。

上游基线 Docker 配方会下载并验证 `dl.min.io` 的预编译服务端；Silo release 镜像则消费所选 tag 上由源码构建、带 attestation 的精确归档。镜像发布是 GitHub Release 之后显式 dispatch 的独立流程；构建成功本身不会发布镜像。

`CREDITS` 根据实际链接进服务端的模块重新生成，并由 CI guard 保护。OCI 镜像包含它；考虑到约 1.8 MB 的体积，软件包与归档有意省略。上游 AGPL 与版权声明保留，同时加入 PGSTY 修改声明。

## 运行时与安全行为变化 {#runtime}

即使是漏洞修复，只要用户可感知，也属于兼容性变化。下文的“收紧”表示过去可能成功、或以另一种方式失败的请求、策略、token、配置或损坏内部消息，现在会被拒绝。

### 认证、IAM 与请求身份 {#auth-iam}

| 变化                                                           | 最终行为                                                                                                                                                      | 谁需要处理                                                                                           |
|:-------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| OIDC JWT 校验（`d24f449e0`）                                     | client secret 不再作为验签 key。只接受非对称 JWKS 算法 `RS256/384/512`、`ES256/384/512`、`RS3256/3384/3512`、`ES3256/3384/3512`。`HS256/384/512` 失败；未知 `kid` 仍走既有 JWKS 刷新/重试 | 使用 HMAC 为 Silo token 签名的 IdP 必须迁移到非对称 JWKS key                                                  |
| LDAP STS 错误（`3b950f8fa`）                                     | 未知用户与错误密码共享同一个外部 `InvalidParameterValue` 认证失败；LDAP 基础设施错误仍是服务端错误并记日志                                                                                      | 客户端不能再从响应文本判断账号是否存在                                                                             |
| LDAP STS 限流（`18b712d49`、`9e10f6d9a`、`f44110890`、`5e40665ac`） | 每来源、每节点内存桶：突发 10 次，每 6 秒补 1 个 token，空闲 TTL 15 分钟。只有认证失败消耗 token，成功与基础设施失败会退回。耗尽返回 HTTP 429、`ThrottlingException`、`Retry-After: 6`                         | 代理应配置独立的 `MINIO_IDENTITY_LDAP_STS_TRUSTED_PROXIES`                                              |
| LDAP 可信代理来源                                                  | socket peer 在允许列表中时，优先干净的 `X-Real-IP`；否则从右向左遍历 XFF 并跳过可信 hop。忽略 RFC 7239 `Forwarded`。代理 **必须覆盖** X-Real-IP                                                 | 审核 Ingress 头部清洗；该限流不是分布式账号锁                                                                     |
| LDAP service-account 查找                                      | 对“User DN not found”的匹配改为大小写不敏感，依赖消息大小写变化时仍能得到预期 Admin no-such-user / login-name 错误分类                                                                     | 只有依赖偶然错误分类的脆弱客户端会观察到变化                                                                          |
| 桶/对象 IAM 边界（`97b7d2804`）                                     | 12 个受保护桶写操作不再仅因 `arn:aws:s3:::bucket/*` Allow 而获准，必须有裸桶 ARN。Deny/NotResource 与内置 `*` 策略语义不变                                                               | 自定义策略中确实需要桶写操作时加入 `arn:aws:s3:::bucket`；或临时使用全局逃生开关 `MINIO_API_LEGACY_BUCKET_RESOURCE_MATCH=on` |
| 受保护操作                                                        | 删除/强删桶；写/删桶策略；写复制、生命周期、对象锁、版本、CORS；删 CORS；写桶 QoS 或 Inventory 配置                                                                                           | 读/list、创建桶、标签、加密与通知仍沿用历史匹配行为                                                                    |
| 有效策略输入（`2f55347f7`）                                          | 服务端派生条件不能被同名 header/query 遮蔽；策略包中精确 key 优先。已有/请求标签、存储类、content/copy/checksum、对象锁、签名年龄与 list 参数均来自操作实际消费的值                                                 | 误依赖攻击者可控遮蔽值的策略不再匹配                                                                              |
| 请求标签                                                         | PutObject、CreateMultipartUpload、PutObjectTagging 把 `s3:RequestObjectTag/*` 绑定到已解析输入；ExistingObjectTag 只来自已存元数据；其他操作路径保留旧 header 回退                        | 重新测试带标签条件的写策略                                                                                   |
| `s3:signatureAge`                                            | 只在已经验证的 presigned SigV4 请求中出现                                                                                                                             | 注入原始 `x-amz-signature-age` 不再产生该条件                                                              |
| `s3:versionid`（`744a9dcd7`）                                  | 缺失就真正缺失；空白被归一；DeleteObject/MultiDelete 使用每个对象的有效版本。URL version 不能诱骗不同 XML version                                                                         | 重测基于版本的删除策略及依赖 Null 的策略                                                                         |
| 复制元数据（`56fa63bfd`）                                           | 普通 PUT/COPY 不能注入内部复制状态/时间元数据；经认证的 replica 请求必须拥有 `ReplicateObjectAction`；multipart 与 Snowball 的合法复制流程保留                                                   | 自定义复制调用方必须走受授权的复制路径                                                                             |

桶边界逃生开关在启动时全局生效，而且是全有或全无；它用于迁移，不是长期混合策略模式。空或无法解析的 LDAP 来源不会被放入一个共享限流桶；在能派生出可用来源前不对它限流。

### 通用来源地址信任 {#trusted-proxies}

`fe6dc4780` 新增 `MINIO_API_TRUSTED_PROXIES`，因为所选客户端地址会进入 `aws:SourceIp`、审计 `remotehost`、事件 `Host`、管理 trace 及节点间转发。

| 值              | 结果                                                                                     |
|:---------------|:---------------------------------------------------------------------------------------|
| 未设置            | 精确保留历史行为：相信任何 peer 提供的来源头；依次选择最左 XFF、X-Real-IP、`Forwarded`                             |
| `none` 或 `off` | 忽略三种来源地址头，使用 TCP peer                                                                  |
| IP/CIDR 列表     | 只有 TCP peer 在列表中时才相信头；XFF 从右向左越过可信 hop（最多 100 个），随后取最后一行 X-Real-IP，再从右向左遍历 `Forwarded` |

畸形配置、非空但没有任何代理的列表，或远程 `env://` 读取失败都会 fail closed 并阻止启动，而不是回退到 trust-any。收到的链中无效值会跳过；没有可用地址时回退 peer。只在 FTP/SFTP peer bridge 中隐式信任 loopback，不会把链内任意 loopback 当成可跳过 hop。

继承的 `_MINIO_API_XFF_HEADER=off` 保持旧语义和初始化时点：它只关闭 XFF 解析，不影响 X-Real-IP 或 `Forwarded`，因而不是安全边界。需要把所有合法转发请求的集群节点加入列表，并确保边缘代理覆盖或剥离客户端提供的三种来源头。

### S3 请求与响应行为 {#s3-behavior}

| 范围                     | 变化与兼容性影响                                                                                                                                                 |
|:-----------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| Presigned 流式认证         | query/presigned SigV4 请求声明 `STREAMING-UNSIGNED-PAYLOAD-TRAILER` 时返回 `SignatureVersionNotSupported`，不能降级为匿名授权；header SigV4 会在读取 body 前验证                  |
| Snowball               | 先授权后解包 tar；流式 trailer 绕过无法在后续失败前写入对象                                                                                                                     |
| S3 Select 记录限制         | CSV 输入、JSON Lines 输入和输出记录超过 1 MiB 时返回 `OverMaxRecordSize` 事件。JSON Lines 始终使用有界 reader（在支持 SIMD 的 CPU 上可能变慢），JSON 解析错误为 `JSONParsingError`，已完成记录可先于终止错误送达 |
| 流式响应                   | tracking writer 实现 `Flush`；Write/Flush 会记录隐式 HTTP 200。ListenBucketNotification/watch 流及 S3 Select keepalive 能及时送达，审计/状态指标也能记录已提交状态                       |
| Multipart 整对象 checksum | FULL_OBJECT CRC32/CRC32C/CRC64NVME 完成时可完全省略每 part checksum；只要提供任意一个仍会校验；COMPOSITE 仍要求每个 part。即使不提供对象 checksum value，显式 completion type 仍会校验：不匹配返回 `BadDigest`，未知 type 返回 `InvalidArgument`。CRC64NVME canonicalization 保持不变。零字节 multipart 对象 checksum 会正确保存 |
| CopyObject checksum 响应 | CopyObject XML 与 HTTP header 使用目标加密上下文报告已提交 checksum。SSE-C 源 key A 与目标 key B 严格分开；同对象换钥会用新 key 返回 checksum 字段。存储数据与 checksum format 均不改变 |
| Multipart part 顺序      | 重复或非递增 part number 在组装前以 `InvalidPartOrder` 失败；允许空洞及不从 1 开始；upload 保留供重试                                                                                 |
| 纠删码读缓冲池                | 恢复正确 shard buffer 所有权，避免池失效以及可能造成卡死、损坏或严重性能下降的错误缓冲关联                                                                                                     |
| 更新缓冲                   | 返回的下载 buffer 具有正确所有权；公开更新器随后已禁用，所以当前受支持升级路径不会运行该代码                                                                                                       |

### 分布式存储与私有 API {#storage-rest}

这些变化通常对 S3 客户端不可见，但会影响混合版本集群、自定义内部调用方、损坏磁盘及恶意 peer。

- `ReadMultiple` 及私有 storage-REST `/rmpl` endpoint、客户端方法、导出 Go 类型和指标均已删除。外部 S3 List/Get 不变。`storageRESTVersion` 仍为 v63，不能据此推断混合节点兼容。
- 每个远程 StorageAPI 路径字段、嵌套元数据名和原始 volume sink 都在存储边界验证，包括 peer-S3 Grid 消息；拒绝词法遍历、volume root alias 及 Windows 分隔符/盘符形式。
- 所有解码 sink 及 CheckParts/VerifyFile 都会拒绝非法纠删码几何、非正 block、负 part size 及不可用已存纠删码元数据。
- 节点间分配声明受限：AppendFile 预分配最多 1 MiB 但仍接受 body；DeleteVersions 边解码边增长并拒绝负声明；旧 ReadFile 上限为 5 GiB。
- 有 deadline 的工作会把 worker panic 转成错误并记录有界堆栈，不再让进程崩溃。
- `ReadParts` 会跨 keepalive frame 保留真实后端错误；空 part 列表成功返回空结果，不触发 trace panic 或 goroutine 泄漏。
- `ReadMultiple` 删除后遗留的 HTTP stream helper 随后被清理；该清理没有额外公开行为变化。

该 containment 是词法层面的，不解析文件系统符号链接；审计也没有原生 Windows 服务端 CI。应整体升级所有节点，即使节点间端口有 root 凭据与输入验证，也不要向不可信客户端暴露。

### 通知配置与审计输出 {#notify-audit}

- NATS 现在注册解析器实际读取的 `user_credentials`、`nkey_seed`、`tls_handshake_first`；AMQP 注册 `immediate`；既有环境变量名不变。
- 旧字面量 `MINIO_NOTIFY_NATS_USER_CREDENTIALS` 仍只对 NATS 接受；优先级为环境变量、新 key、旧迁移 key。
- AMQP 旧配置迁移会正确映射 `immediate`。非法通知配置错误只标识名称，不再回显凭据值。
- PostgreSQL 与 MySQL 通知配置使用规范 `connection_string` 或 `dsn_string`，显式连接串原样透传。保留的 PostgreSQL 内部 fallback builder 会正确引用参数并使用 `user` 关键字，但离散字段不是受支持的 KV 输入。
- dangling object 删除审计重新在 `merrs` 中包含每块盘的错误。

提交 `f1ba68358` 已关闭继承的数据库通知迁移风险：迁移不再写入未注册的离散连接 key。缺少 `connection_string` 或 `dsn_string` 的已启用 pre-KV target 现在会以不含凭据的错误中止启动。升级前必须转换、禁用或删除这类 target；修复前导出的诊断包可能含有历史明文数据库密码，应据此处置。

## 工具链、依赖与内嵌组件 {#dependencies}

构建声明从 Go 1.24 + 1.24.8 toolchain 迁移到 `go 1.26.5`。即便没有修改 Silo 源码，这也可能改变 TLS、HTTP、DNS、调度器、GC 及标准库边缘行为。Go-Jose、OpenTelemetry、Go crypto/network 模块、云 SDK、etcd、NATS 与压缩库等安全敏感依赖也已升级。

这些升级带来的可观察边缘修正包括：Go TLS/X.509/URL/archive、MQTT 超长 UTF-8 packet 编码、畸形 Azure NTLM challenge、Thrift framed transport 与 32 位编译、NATS 认证/授权/身份/拒绝服务，以及 Prometheus remote-read/write 与 UI 加固。它们属于依赖行为变化，但不表示每条 advisory 路径都能从 Silo 到达。jsonparser 的 CVE-2026-32285 调查没有产生补丁：解析到的 v1.1.2 已包含修复，也没有发现可达的脆弱符号，所以本范围内没有相应兼容性差异。

重要的有意依赖决策如下：

| 组件         | 最终选择                                                         | 兼容性理由/影响                                                                 |
|:-----------|:-------------------------------------------------------------|:-------------------------------------------------------------------------|
| Console    | `pgsty/silo-console` v2.1.1，保持 `github.com/minio/console` 路径 | 恢复内嵌 UI，应用 Silo 品牌和双语文本，加入 Metrics V3，移除 SUBNET 流程并修复指标图例未翻译问题           |
| 客户端库       | `pgsty/mc`，保持 `github.com/minio/mc` 路径                       | Console import path 不变，同时使用维护中的 MCLI 分叉                                  |
| 公共包        | `pgsty/silo-pkg/v3` v3.11.0，保持 `github.com/minio/pkg/v3` 路径  | 提供 IAM 精确匹配的一半、LDAP TLS/StartTLS/deadline/close 修复、证书 watcher 清理和 RNG 修复 |
| Kafka      | Sarama 1.45.1                                                | 固定以避免破坏性的 broker 协商漂移                                                    |
| PostgreSQL | lib/pq 1.10.9                                                | 固定以避免 nil `[]byte` / PostgreSQL 14 以前版本的行为回归；自动 DSN 引用在服务端代码中修复          |
| 压缩         | klauspost/compress 1.18.7                                    | 显式安全/正确性升级                                                               |
| Thrift     | 0.24.0                                                       | 修复 32 位构建                                                                |
| systemd 库  | require 22.7，replace 为 22.6                                  | 在上游修复单调时钟回归前保留 NetBSD 编译能力                                               |

LDAP 包现在会在 `ldaps://` 中使用 TLS 字段；即便开启 `server_insecure`，StartTLS 仍保持启用；还修复了 nil TLS panic、StartTLS deadline 以及失败后连接关闭。证书 watcher 停止时不再泄漏；Windows 上轮询可能让 reload 最多延迟约十秒。RNG subkey 熵/reset 行为也已修正，不过服务端不会走 reset 路径。

对外部 `silo-pkg` Go 使用者，有两项变化比服务端自身调用路径更宽：`xtime.Duration` JSON 从整数纳秒变为 duration 字符串；部分 AIStor action 词汇/受保护 action helper 与上游不同。特别是 `Policy.IsAllowedActions` 可能在受保护 action 上产生不同结论，但服务端并不调用它。服务端通过 YAML/msgp 保存相关状态，也没有调用这些有差异的 AIStor/action helper 路径，因此没有发现由这些库变化引起的服务端数据迁移或授权变化。

新工具链重新生成了 `String()` 文件。合法枚举输出不变；差异来自生成器来源与非法值格式化机制，不单独宣称为 S3 行为变化。

## 2026-08-06 审计之后的变更 {#since-20260806}

上文各节描述的是 `219670d3` 快照。下表记录此后合并进 `main`、并在 20260903 版本中统一交付的行为变更。

| 领域 | 变更 | 出处 |
|:-----|:-----|:-----|
| 授权 | 显式删除版本按 `s3:DeleteObjectVersion` 授权，`DeleteObjects` 逐条目授权；用户与组状态变更要求与目标状态匹配的动作；策略写入拒绝裸 ARN 前缀 | [#104](https://github.com/pgsty/silo/pull/104)、`58735ee38`、`229fe2b3c`、`eee05a17c`（SN-2026-005、-009、-010） |
| 复制信任 | 仅当精确标记与 `s3:ReplicateObject` / `s3:ReplicateDelete` 同时成立，复制专用 header 才获得复制语义；否则在签名验证后被移除 | [#101](https://github.com/pgsty/silo/pull/101)（SN-2026-008） |
| SSE-C | 零字节对象与 `GetObjectAttributes` 校验客户密钥；null 版本与原地换钥复制不再把对象重写成不可读密文；CopyObject 以目标密钥报告校验和 | `b73581b05`、`474cd5801`、`05df6e70d`、`ffb70eb37`、`e73436c99`（SN-2026-006、-007） |
| 校验和 | 服务端计算分片校验和、联邦 `UploadPartCopy`、`CompleteMultipartUpload` 返回 `ChecksumType`、与 AWS 对齐的完成错误码、拒绝未知算法与 `CRC64NVME` + `COMPOSITE` | `7fea6d5a5`、`8d76a255c`、`d014a12cf`、`5d152416d`、`7c103389f`、`d28885d0e` |
| 列表 | 对不存在的桶，`ListObjects` 在原先返回空列表的捷径路径上改为返回 `NoSuchBucket` | `e9c5340be` |
| 桶级 CORS | 真实的 `?cors` API；桶配置覆盖全局策略；预鉴权查找只读驻留元数据，否则应用全局策略；站点复制以 last-writer-wins 寄存器收敛 CORS | [#71](https://github.com/pgsty/silo/pull/71)、[#80](https://github.com/pgsty/silo/pull/80)、[#101](https://github.com/pgsty/silo/pull/101) |
| 桶元数据 | `metadata.lock` 串行化所有桶配置写入；`ForceCreate` 与站点 adoption 保留既有配置；启用 lock 的桶始终使用纯 Enabled 版本控制 | [#103](https://github.com/pgsty/silo/pull/103)、`dd3bdb808` |
| 站点复制 | Object Lock 配置以独立字段复制（仍接受旧的 `Tags` 载体）；按站点统计状态；有效性探针在规则前缀下校验权限 | `3861f33cb`、`fb406fdc9`、`c9ad74673`、`5db7be4ee` |
| 配置 | 旧版数据库通知目标必须有 DSN；`MINIO_CONFIG_ENV_FILE` 使用保留命名目标的专用解析器 | `f1ba68358`、`6b0998157`、`2aea7fe9c` |
| 工具链与组件 | Go 1.27.1；上游 `minio-go` 固定到 `0e78d3f18efe`（`silo-go` 分叉已退役）；`silo-pkg` v3.13.2；Console v2.3.0（见 [Console 页](/compatibility/console/)）；捆绑 [mcli 20260903](/blog/release/mcli-20260903/) | `43f4bb7ed`、`4d6e1ea8e`、最终依赖刷新 |

## 已知残余风险与未修复项 {#limits}

本次审计不会把继承的限制包装成兼容性承诺：

1. **默认来源 IP 仍可伪造。** 未设置 `MINIO_API_TRUSTED_PROXIES` 时刻意保留上游 trust-any 行为。直连部署设为 `none`，代理部署使用精确 allowlist。
2. **版本条件仍有缺口。** MultiDelete governance bypass 的二次授权仍读取 query/缺失 version，而非每个 XML entry；Snowball 在逐文件授权后才读 PAX `minio.versionId`。`username`、`userid`、`signatureversion`、`authType` 条件 key 仍无条件插入空值，因此对它们使用 `Null` 仍是“存在但为空”的语义。
3. **Multipart parser 防御尚未完整。** Handler 已修复顺序，但 object layer 没有独立 uniqueness 防线；XML root 验证和继承的非数字 part 错误映射未修改。
4. **旧通知迁移仍有风险。** 按上文说明审核。
5. **存储路径校验为词法层面。** 不解析符号链接；未独立覆盖原生 Windows 执行。
6. **私有 API 不是稳定兼容承诺。** `ReadMultiple` 表明即便 storage REST 协议号不变，操作仍可能消失。不要跨越该边界滚动运行混合构建。
7. **源码结果不等于已发布制品。** 在逐渠道验证前，本页不声称 GitHub 标签、软件包、OCI manifest、签名或线上站点已经包含仅存在于审计 HEAD 的最后三个提交。
8. **信息性 HTTP 响应的跟踪仍不完整。** response tracking 层会把 1xx 当成最终响应；Flush/隐式 200 修复没有引入该行为，也没有声称修复它。
9. **未实现条件删除。** `DeleteObject` 忽略 HTTP `If-Match` 头，`DeleteObjects` 忽略每个 `<Object><ETag>` 元素，两者都执行无条件删除（[#10](https://github.com/pgsty/silo/issues/10)）。
10. **多站点删除桶配置不会收敛。** 在一个站点删除桶策略、SSE、标签或配额配置后，仍持有该配置的对端可能把它恢复回来（[#77](https://github.com/pgsty/silo/issues/77)）；只有桶级 CORS 使用带 tombstone 的寄存器。依赖多站点同步删除这些配置的部署，删除后必须逐站核对。

## 迁移检查清单 {#migration}

从 MinIO 切换到 Silo 时，建议按此顺序执行：

1. 记录精确 MinIO 二进制/tag、Chart 与 values、镜像 digest、包载荷、service unit、环境文件、配置目录、数据所有权、IAM 策略、OIDC/LDAP 设置、通知 target 与代理拓扑。
2. 备份配置与 IAM 元数据。Silo 原地读取旧磁盘，但回滚仍需要旧可执行文件/配置/Chart，以及可用的原所有权。
3. 把服务端执行名改为 `silo`，不要假设 `/usr/bin/minio` 存在。容器可翻译 argv 层的 `minio server`，不能翻译绝对路径。
4. 明确决定配置目录：用 `--config-dir ~/.minio` 复用，或让“只有旧目录”回退选中它。不要意外创建空 `~/.silo`，再误以为旧配置丢失。
5. 使用软件包时，授予 `silo:silo` 对数据、证书、secret 和日志的权限。把有意覆盖移入 `/etc/default/silo`，并理解它会覆盖 `/etc/default/minio`。
6. 使用 Helm 时，以完整旧 values 分别渲染新旧 Chart；需要时用 `nameOverride` / `fullnameOverride` / `serviceAccount.name` 保留名称；Chart 与镜像原子切换。
7. 删除 updater、callhome、SUBNET 注册和支持上传自动化，改用软件包/镜像/编排器滚动及自己的诊断传输渠道。
8. 把 HMAC OIDC token 改为非对称 JWKS。分别测试 LDAP 成功、错密码、未知用户、后端故障和限流路径。
9. 为 12 个受保护 action 加裸桶 ARN；测试有效 tag、signature-age、source-IP 和逐版本删除条件。旧桶开关只作为临时回退杆。
10. 设置 `MINIO_API_TRUSTED_PROXIES=none` 或精确列表，清洗三种来源地址头，并加入会转发认证请求的集群 peer。
11. 测试超大 S3 Select 记录、流式通知、unsigned trailer 拒绝、multipart 整对象 checksum、重复 part、复制、修复、KMS、每个通知 target、审计摄取及容器优雅关停。
12. 把分布式集群所有节点作为同一构建升级。回滚时旧 Chart 与旧镜像成对使用，绝不能只回滚一个。

## 验证证据 {#verification}

本次审计以最终源码为准，而不是只相信文字。在记录的快照上：

| 检查               | 结果/边界                                                                                                                                     |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------------------------|
| 提交枚举             | 下方账本对 96/96 个提交完成分类；`origin/main` 93 个，本地准备态 HEAD 另 3 个                                                                                   |
| 净差异审查            | 523 个变化路径全部归入服务端运行时、内部协议、依赖、分发、文档、测试或被替代变化                                                                                                |
| Rebrand 兼容 guard | 通过；兼容 manifest、分发/运行时断言及 Docker argv 测试保持稳定                                                                                               |
| Go 测试            | 在 `219670d31` 上完整 `go test ./...` 通过，包括 `cmd`、OIDC、LDAP、notify、event target、Grid、handler、hash 与全部 S3 Select 包                             |
| Helm 迁移          | `buildscripts/verify-helm-migration.sh` 通过：lint、render、旧版升级、归档及 7 个渲染资源的身份比较                                                              |
| 软件包生命周期          | `buildscripts/package/lifecycle_test.sh` 通过；包载荷/provenance 断言覆盖空 DEB conflict 元数据、unit/default 路径与法律文件                                    |
| 站点               | 严格 `make check` 通过：模块校验、warning-fatal Hugo 渲染（617 EN / 615 ZH 页）以及 1,084 个 HTML 文件中的 388,962 个内部引用；`git diff --check`、双语锚点及 96/96 提交覆盖也通过 |

Security 文章提供更深入的威胁模型和测试向量，但其中历史性的“已发布/未发布”状态只描述写作当日。与最终快照冲突时，以本页审计边界为准。

## 完整提交覆盖账本 {#ledger}

哈希按图顺序排列。Merge、文档、测试和 CI 提交也全部列入，因为分发行为和兼容性主张的证据强度同样会影响用户；“无独立运行时差异”只表示这一点，不表示没有审查。

| 分类                           | 提交                                                                                                                                                                                                                                              | 验证后的净效果                                                                                                                                                         |
|:-----------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 初始分叉、Console、CI 与依赖基线        | `d4cd4b433`、`8630937e7`、`68521b37f`、`00f3cf74f`、`5abd9a80f`、`377fc616d`、`f2f9a40dc`、`ee55e5391`、`ce1c537eb`、`68e0ba997`、`1869bd30b`、`ff58df949`、`e4fa06394`                                                                                     | Go/SDK 演进；恢复/分叉内嵌 Console；OCI 内加入 MCLI；替换 CI；修复 LDAP TLS 回归；升级安全依赖。两个 merge 提交没有超出父提交的额外差异                                                                      |
| 四月安全系列                       | `d24f449e0`、`3b950f8fa`、`56fa63bfd`、`3252d5b7f`、`f444b6f37`、`efb6e5b00`、`db4c0fd5e`、`18b712d49`、`9e10f6d9a`、`f44110890`、`f48dbe777`                                                                                                             | OIDC、LDAP STS、复制元数据、S3 Select、unsigned trailer/Snowball、Go 1.26.2、限流计数/来源加固及安全文档                                                                                |
| 五至六月可靠性与私有 API               | `65795ee1f`、`5e40665ac`、`fd69c89d0`、`73ac52472`、`df627ff89`、`3e61b1d3a`、`d495d30d5`                                                                                                                                                             | HTTP Flush、最终 LDAP 分桶、完整 S3 Select 边界、删除 ReadMultiple、Go 1.26.4/依赖更新及文档链接变化                                                                                     |
| 八月前的组件集成                     | `ce01ccbdc`、`4dfc27ce3`、`b7f52ca43`、`7babc0c39`、`c1aec0518`、`15fcc3c8a`、`3f192f3f0`                                                                                                                                                             | 历史 Chart 镜像切换、安全依赖更新、通知流 merge、可移植依赖 pin、压缩库、MCLI replace、Console v2.0                                                                                          |
| 八月运行时正确性/安全                  | `c8590413f`、`3e14733f1`、`924717926`、`89d346bf5`、`8069a32ac`、`a36fd8fff`、`ca7baa670`、`80e8eaa42`、`b6f70ab08`、`1af351a70`、`38366f654`、`22c1e41fd`、`97b7d2804`、`2f55347f7`、`744a9dcd7`、`fe6dc4780`、`162ded343`、`0c14d8151`、`9dd1dc172`、`2602177ef` | Multipart、纠删码 buffer、响应提交、panic containment、路径/元数据/分配/ReadParts containment、遗留清理、IAM/有效值/version ID/source trust、通知/libpq 与审计细节                                 |
| Chart 加固与审计文档                | `dfe669862`、`5f4513fd4`、`b42ee4e8a`、`8eae745ab`                                                                                                                                                                                                 | 安全的 Chart 用户默认值、门户/文档路由、维护者 ignore 规则与 advisory；只有 Chart 默认值直接改变运行时分发行为                                                                                         |
| 到 20260804 标签的发布工程           | `9c799f42d`、`10c7670b8`、`cf7df097b`、`32863c852`、`632ade111`、`1814ae52f`、`475236c79`、`11d79fddc`、`3b8a55dee`、`ca674a696`、`4c185d5a6`、`2ca4971d9`、`e064b5555`、`aa5139369`、`021110b45`、`d88f46cce`                                                 | RPM/DEB/APK、provenance、OCI 发布 gate、固定 lint/generation、修复 S3 Select 测试竞态、广泛 CI、PID 1 信号、已发布目标交叉构建、安全 release dispatch、可复现性、删除陈旧配置、systemd 路径、真实失败 gate 与运行镜像关停断言 |
| Silo 切换与 2026-08-06 准备态 HEAD | `15def34dc`、`77bdc4c0c`、`15ab10833`、`30749911b`、`e071bb77e`、`bd8df5166`、`6613c2a3c`、`fd2ca1c6d`、`c46b16ec6`、`c47733abc`、`f1c77d5a2`、`62717d7bf`、`6740e6978`、`b57275be3`、`05be686b8`、`a6d6d9b02`、`6bd9cf77e`、`219670d31`                         | 清理未发布 MinIO 分发残留；Silo 运行身份/离线边界；改名软件包、OCI、Helm 与迁移 guard；固定 fixture；文档/仓库切换；Console 2.1.0→2.1.1；Node 24 action；DCO/法律/文档完善；重生成 CREDITS；交付 LICENSE/NOTICE        |

账本共 96 个唯一提交。范围内被替换的变化——例如 Console 2.0 → 2.1.0 → 2.1.1、历史 `pgsty/minio` 镜像/Chart 状态，以及更新器禁用后的下载 buffer 代码——只在留下最终兼容性影响时描述。

## 参见 {#see-also}

- [MCLI](/docs/compatibility/mcli/) —— 客户端制品、配置目录、更新、SUBNET 与命令兼容性
- [Silo 20260804 Release Note](/blog/release/silo-20260804/) —— 更早的已打标签边界，不是完整 2026-08-06 审计 HEAD
- [Silo Pkg 3.11.0](/blog/release/pkg-3.11.0/) —— 公共 IAM、LDAP、watcher、RNG 与开发者可见变化
- [OIDC JWT 加固](/blog/security/cve-2026-33322/)、[LDAP STS 加固](/blog/security/cve-2026-33419/)、[复制元数据](/blog/security/cve-2026-34204/)、[S3 Select 限制](/blog/security/cve-2026-39414/)与 [ReadMultiple 删除](/blog/security/cve-2026-42600/)
- [Unsigned-trailer query 认证](/blog/security/cve-2026-41145/)、[Snowball 认证](/blog/security/cve-2026-40344/)与 [jsonparser 无需改动结论](/blog/security/cve-2026-32285/)
- [节点间路径 containment](/blog/security/internode-path-containment/)、[重复 multipart part](/blog/security/duplicate-part-numbers/)、[桶/对象 IAM 边界](/blog/security/object-grant-bucket-reach/)、[version-ID 条件](/blog/security/s3-versionid-conditions/)、[来源地址信任](/blog/security/source-address-trust/)与[通知 key 注册](/blog/security/notify-keyspace-registration/)
