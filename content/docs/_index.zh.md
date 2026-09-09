---
title: "PGSTY SILO 文档"
linkTitle: "文档"
description: "pgsty/silo 20260903 文档手册"
type: docs
icon: fa-solid fa-book
sidebar_root_for: self
sidebar_root_link_self: true
menus:
    main:
        identifier: docs
        weight: 20
cascade:
    type: docs
    footer_style: slim
---


> [!WARNING]
> SILO 是由 Pigsty 社区维护的 MinIO 分支。本项目并非 MinIO, Inc. 的关联项目，也未获得其认可、赞助或背书。"MinIO" 是 MinIO, Inc. 的商标，此处仅用于标识上游项目。源码与许可信息详见[归属与署名](/about/)。

SILO 在保留 S3 API、配置与运维契约的同时，为现有 MinIO 部署提供开放的发行与安全维护路径。本站覆盖安装、迁移、管理、开发、版本发布与兼容边界。

## 快速开始

### Docker

下面的命令固定到当前 SILO 服务端发行版。示例凭据仅适用于本地评估。

#### 启动 SILO

```bash
docker run -d --name silo \
  -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=silo-admin \
  -e MINIO_ROOT_PASSWORD=replace-with-a-strong-secret \
  -v silo-data:/data \
  pgsty/silo:RELEASE.2026-09-03T13-18-01Z \
  server /data --console-address :9001
```

#### 检查就绪状态

```bash
docker exec silo silo healthcheck ready
```

退出码为 0 表示本地服务已就绪。该探针内置于每个 SILO 二进制，不依赖容器内的第二个客户端。

#### 打开管理控制台

访问 http://127.0.0.1:9001，使用上面的凭据登录。投入生产前，请启用 TLS、设置唯一强凭据、固定经过测试的镜像标签或摘要，并实际验证备份恢复。

持久化宿主机路径、服务管理与生产注意事项见[容器部署指南](/docs/operations/deployments/baremetal-deploy-minio-as-a-container/)。

### Linux 软件包

在[下载与安装](/docs/compatibility/binary/)页面选择对应架构的 RPM、DEB、APK 或独立归档。正式发布制品同时提供 SHA-256 校验和与构建溯源证明。

原生软件包将服务端安装为 `/usr/bin/silo`，并继续使用既有的 `MINIO_*` 环境变量契约。替换现有 minio 软件包前，请阅读[二进制与软件包兼容说明](/docs/compatibility/binary/)。

### 现有 MinIO

替换镜像或二进制前，请先阅读[迁移指南](/docs/compatibility/migration/)。保留数据卷与配置，停止所有运行旧二进制的节点，再让所有节点统一启动同一个固定版本的 SILO。不要在两种二进制之间滚动迁移，也不要对需要保留的数据执行 `docker compose down -v`。

### Kubernetes

已归档的 MinIO Operator v7.1.1 可以运行使用 SILO 镜像的 Tenant：将镜像覆盖为 `pgsty/silo`，并固定经过测试的标签或摘要。请遵循 Tenant Helm 指南，并把该 Operator 版本视为冻结的兼容基线，而不是仍在维护的依赖。
