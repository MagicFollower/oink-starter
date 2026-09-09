---
title: "从 MinIO 迁移到 Silo"
linkTitle: "迁移指南"
description: "哪些改变、哪些不变，以及容器部署如何切换。软件包安装见《原生软件包迁移》。"

weight: 10
type: docs
icon: fa-solid fa-arrow-right-arrow-left
---

从 MinIO 迁移到 Silo 是一次原地二进制替换，不是数据迁移。不导出、不重新导入任何东西。容器部署中，唯一必须修改的是镜像名。RPM/DEB 安装见[原生软件包迁移](/docs/compatibility/binary/)。

## 哪些改变 {#scope}

按重要性从大到小：

1. **容器镜像**：`minio/minio`、`quay.io/minio/minio`、`pgsty/minio` 统一替换为 `docker.io/pgsty/silo`。
2. **软件包、systemd 服务与服务端二进制**：`minio` → `silo`。
3. **上游服务**：原地更新器与 MinIO 官方 callhome/SUBNET 被禁用；升级通过软件包、镜像或编排系统进行。
4. **默认操作系统服务账号**：`silo`——仅影响全新安装；迁移场景继续以数据现属主运行。
5. **品牌呈现**：启动横幅、Console 外观、日志措辞与产品链接显示 Silo。

## 哪些不变 {#unchanged}

- **对象数据与 `.minio.sys` 元数据目录——磁盘格式未变，同一份数据与 MinIO 双向通用。**
- Bucket、版本、用户、Access Key、策略、生命周期规则、复制状态、加密元数据。
- S3 API、SigV4 签名、SDK、`mc`/`mcli`、预签名 URL 行为。
- 端点主机名、API 端口 `9000`、Console 端口、卷挂载。
- `MINIO_*` 环境变量与既有服务端参数。
- `/minio/*` 路由、`x-minio-*` 头、`minio_*` 指标。

没有数据转换步骤。若你的 MinIO 版本已很陈旧，需要在预发环境验证的是版本跨度本身——那是一次大版本软件升级，不是格式变化。

## Docker 迁移 {#docker}

无论当前使用哪个镜像，统一替换为：

```text
docker.io/pgsty/silo:<RELEASE-tag>
```

tag：不可变的 `RELEASE.YYYY-MM-DDTHH-MM-SSZ`（建议钉住）、滚动 `latest`，以及下述 `-distroless` 变体。旧的 `pgsty/minio` 仓库保持已发布状态，冻结在最后一个 tag。

Compose 中只改镜像一行：

```yaml
services:
  minio:                              # 服务名可继续为 "minio"
    image: docker.io/pgsty/silo:<RELEASE-tag>
    command: server /data --console-address ":9001"
    environment:                      # MINIO_* 不变
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    ports: ["9000:9000", "9001:9001"]
    volumes:
      - minio-data:/data              # 同一卷、同一份数据
volumes:
  minio-data:
```

```bash
docker compose pull minio && docker compose up -d minio
```

entrypoint 会翻译旧的第一个参数，继承下来的 `command: minio server /data` 继续可用；写死的 `entrypoint: /usr/bin/minio` 需改为 `/usr/bin/silo`。现有 `mc ready local` 健康检查继续可用，原生替代为 `test: ["CMD", "silo", "healthcheck", "ready"]`（[参考](/docs/compatibility/feature/healthcheck/)）。不要执行 `docker compose down -v`——`-v` 会删除数据卷。

### Distroless 变体 {#distroless}

`pgsty/silo:<RELEASE-tag>-distroless` 只包含 `silo` 二进制：没有 shell、没有 `mc`、没有 `curl`。内置 `HEALTHCHECK`（即原生探针），任意 `--user` 下均可运行：

```bash
docker run -d --name silo \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=change-me-long-password \
  -v silo-data:/data \
  docker.io/pgsty/silo:<RELEASE-tag>-distroless \
  server /data --console-address ":9001"
```

同一部署的 Compose 写法：

```yaml
services:
  silo:
    image: docker.io/pgsty/silo:<RELEASE-tag>-distroless
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: change-me-long-password
    ports: ["9000:9000", "9001:9001"]
    volumes:
      - silo-data:/data
volumes:
  silo-data:
```

`depends_on: condition: service_healthy` 无需配置 `healthcheck:` 即可生效。卷上的数据格式与经典镜像、MinIO 完全一致——几种镜像可在同一份数据上互换使用。TLS 证书挂载到 `/tmp/.silo/certs`。若命令行 flag 改动了监听地址，用 `MINIO_HEALTHCHECK_URL` 指定内置探针的目标。镜像内没有 shell，调试用 `docker debug` / `kubectl debug`。

### Kubernetes {#kubernetes}

kubelet 探针是 pod spec 中的 `httpGet` 请求；Docker `HEALTHCHECK` 被忽略，两个镜像变体的探测方式完全相同，现有探针配置继续可用。Helm 部署用 `nameOverride`/`fullnameOverride` 保持 release 身份，应用前比对 `helm template` 输出（[细节](/docs/compatibility/server/#helm)）。

### 回滚 {#rollback}

磁盘格式未变、两侧通用：把 `image:` 改回记录的 MinIO tag，`docker compose up -d`。同一卷保持挂载，Silo 运行期间写入的数据 MinIO 仍可读取。

## 从 RELEASE.2026-08-06 升级 {#since-20260806}

`RELEASE.2026-08-06T00-00-00Z` 之后的版本收紧了若干 20260806 曾接受的行为。升级前请逐项核对：

1. **显式删除版本需要 `s3:DeleteObjectVersion`。** 带 `versionId` 的 `DeleteObject` 与 `DeleteObjects` 条目按 `s3:DeleteObjectVersion` 授权，与 AWS 一致。给需要删除特定版本的主体授予该权限；凡是用 `Deny s3:DeleteObject` 来阻止永久删除的策略，都要同时加上 `Deny s3:DeleteObjectVersion`。
2. **启用与禁用是两个独立的管理动作。** `admin:EnableUser` / `admin:DisableUser` 及组的对应动作按请求的目标状态检查；只授予其中一个的策略会失去另一个操作。
3. **新建与更新的策略拒绝裸 ARN 前缀**（如 `arn:aws:s3:::`）以及同时含 `Resource` 与 `NotResource` 的语句。已存储的策略照常加载；重复下发此类策略的自动化会失败。
4. **旧版数据库通知目标必须有连接串。** 已启用的 pre-KV PostgreSQL 或 MySQL 目标若缺少 `connection_string` / `dsn_string`，启动会以不含凭据的错误停止；20260806 在同样情况下会静默丢掉全部通知目标。
5. **校验和请求会被校验。** 未知的 `x-amz-checksum-*` 算法、`CRC64NVME` 与 `COMPOSITE` 的组合、与上传矛盾的校验和类型断言都返回 `400`。AWS SDK、`minio-go` 与 `mcli` 的默认行为不受影响。
6. **桶级 CORS 真正生效。** 设置了自身 CORS 配置的桶只按该配置响应；`MINIO_API_CORS_ALLOW_ORIGIN` 只作用于没有配置的桶。在站点复制组里，等所有站点都运行新版本后再配置桶级 CORS：旧对端会接受但忽略该配置，并持续报告 CORS 不一致。
7. **回滚后数据仍可读。** 20260806 忽略桶级 CORS 配置，并会在重写该桶元数据时把它丢掉；再次升级后请重新创建。

### 9 月 3 日版本的 Console 回归 {#console-0903}

`RELEASE.2026-09-03T13-18-01Z` 不再识别未配置的本机代理转发的客户端地址，同时清除了四个 `CONSOLE_WS_MAX_*` 连接配置。这会改变 IP Allow/Deny 策略的判断，并使管理员无法提高每个地址默认八条匿名连接的限额。

包含修复的构建会恢复内嵌 Console 对环回 TCP 对端的信任，除非设置了 `MINIO_API_TRUSTED_PROXIES=none`/`off`；同时保留环境变量或 `MINIO_CONFIG_ENV_FILE` 中的四个限额配置。远程代理仍需显式配置 IP/CIDR 列表。独立 Console 的默认行为、转发链信任规则和连接预算保持不变，非法配置会在启动时报错。策略表与配置约束见 [Console 设置](/docs/reference/minio-server/settings/console/#embedded-compatibility)。发布进展见 [#147](https://github.com/pgsty/silo/issues/147) 和 [#148](https://github.com/pgsty/silo/issues/148)；0903 镜像尚不包含这些修复。

在 0903 上，显式将本机代理对端加入 `MINIO_API_TRUSTED_PROXIES` 可恢复客户端地址识别，但也会将 9000 端口的 S3 监听器切换到列表模式，需要同时列出它所需的其他代理。自定义 WebSocket 限额则需要包含修复的 Server 构建或独立 Console。

## 一个集群只运行一种二进制 {#one-binary}

分布式节点在 bootstrap 时相互校验二进制。起进不同二进制对端之间的节点不会报错退出，而是无限停在 `activating`，日志记录：

```text
Expected Silo binary checksum: ..., seen: ...
Waiting for at least 1 remote servers with valid configuration to be online
```

该约束适用于任意两个不同的二进制：MinIO 与 Silo 之间如此，两个不同版本的 Silo 之间同样如此。因此不要逐节点迁移——将来升级也一样。所有节点一次切换：全部停旧二进制，再全部起新二进制（Compose 中一次编辑改完所有节点的镜像，执行一次 `docker compose up -d`）。单机部署不受影响。回滚同理。同一二进制的滚动重启正常可用，重启前用 `silo healthcheck --maintenance cluster` 把关（退出码 `0` = 停掉本节点安全）。

## 验证 {#verification}

```bash
silo healthcheck ready                   # 本节点在服务；退出码 0/1
silo healthcheck cluster                 # 集群级写 quorum
mc admin info <现有别名>                  # 所有节点在线、新版本、旧别名直连
```

随后下载一个已知对象比对校验和，用现有 SDK 跑通一个应用，重启服务一次并复查。
