---
title: "原生软件包迁移"
linkTitle: "原生软件包迁移"
description: "silo RPM/DEB 软件包相对 minio 软件包的变化：文件布局、服务账号、接管语义与注意事项。"

weight: 20
type: docs
icon: fa-solid fa-box
---

Silo 为 `amd64`/`arm64` 发布 RPM、DEB 与 APK 软件包，托管于 [GitHub Releases](https://github.com/pgsty/silo/releases)，附 SHA-256 校验和与构建溯源 attestation。本页记录相对 `minio` 软件包安装的变化：文件布局、服务账号与注意事项。迁移的总体范围见[迁移指南](/docs/compatibility/migration/)。

## 文件布局 {#layout}

| MinIO 安装             | Silo 软件包                                                     |
|:---------------------|:-------------------------------------------------------------|
| `/usr/bin/minio`     | `/usr/bin/silo`（同时提供 `silo healthcheck`）                     |
| `minio.service`      | `/usr/lib/systemd/system/silo.service`                       |
| `/etc/default/minio` | 仍然优先读取；`/etc/default/silo` 按变量覆盖（`noreplace/conffile`，升级不覆盖） |
| OS User `minio-user` | `silo:silo`，声明于 `/usr/lib/sysusers.d/silo.conf`，安装时创建        |
| -                    | `/usr/share/doc/silo/LICENSE`、`NOTICE`（AGPL-3.0-or-later）    |

Silo 提供的 RPM DEB 包可以与 minio 包并存安装，且不会覆盖原有文件。DEB 包不提供安装自动启动。

## 服务账号 {#user}

unit 默认 `User=silo`，而现有数据、TLS 私钥与 KMS 凭据属于原 MinIO 用户。不要 chown 数据，用 drop-in 让 Silo 以现属主运行：

```bash
ls -ld /path/to/your/data              # 记录属主，例如 minio-user
sudo mkdir -p /etc/systemd/system/silo.service.d
sudo tee /etc/systemd/system/silo.service.d/10-legacy-user.conf <<'EOF'
[Service]
User=minio-user
Group=minio-user
EOF
sudo systemctl daemon-reload
```

这同时保证 TLS 可用：Silo 从运行用户的家目录解析证书（`~/.silo/certs`，仅存在旧 `~/.minio/certs` 时回退使用），现有 `public.crt`/`private.key`/`CAs/` 无需拷贝即被找到。缺少 drop-in 时，TLS 部署启动失败：

```text
FATAL Unable to start the server: HTTPS specified in endpoints,
      but no TLS certificate is found on the local machine
```

改用 `silo` 账号是之后的可选变更：把证书移到 `silo` 可读路径、在 `MINIO_OPTS` 中设置 `--certs-dir`，并在迁移窗口之外转移数据属主。

## 接管与回滚 {#takeover}

这是一个接管型 unit：

```ini
[Unit]
After=network-online.target minio.service
Conflicts=minio.service

[Service]
Type=notify
EnvironmentFile=-/etc/default/minio
EnvironmentFile=-/etc/default/silo
ExecStart=/usr/bin/silo server $MINIO_OPTS $MINIO_VOLUMES
Restart=always
```

- `Conflicts=minio.service`：systemd 不允许两者同时运行，起一个即停另一个，双向实现接管与回滚。
- `EnvironmentFile` 链使 `/etc/default/minio` 中的 `MINIO_VOLUMES`、`MINIO_OPTS`、凭据与 KMS 配置原样生效。
- `Type=notify`：`systemctl start` 仅在服务端真正就绪后返回成功。

切换：

```bash
sudo systemctl disable --now minio.service
sudo systemctl enable  --now silo.service
silo healthcheck --url https://127.0.0.1:9000 ready    # 未启用 TLS 用 http://
mc admin info <现有别名>
```

回滚（无需还原任何东西——数据属主、证书与旧 unit 均未被触碰）：

```bash
sudo systemctl disable --now silo.service
sudo systemctl enable  --now minio.service
```

## 注意事项 {#caveats}

- **集群所有节点一起切换。** 任意两个不同的二进制都无法组成集群——MinIO 与 Silo 之间如此，两个不同版本的 Silo 之间亦然；混跑节点无限停在 `activating`（[细节](/docs/compatibility/migration/#one-binary)）。先在所有节点完成准备（装包、建 drop-in），再快速连续翻转所有节点：`systemctl disable --now minio && systemctl enable --now --no-block silo`。回滚与将来的升级同理，所有节点一起。
- **非软件包安装同样适用。**`/usr/local/bin/minio` 加自定义 unit 的部署以相同方式被接管，只要其配置位于 `/etc/default/minio`。
- **崩溃循环有频率限制。** 配置错误（如缺证书）时 `Restart=always` 反复重启，直至触发 systemd 启动限制（`Start request repeated too quickly`）。修复根因后执行 `systemctl reset-failed silo && systemctl start silo`。
- **保留回滚窗口。** 验证完成前保留 `minio` 软件包、unit 与二进制；已禁用的 unit 没有开销，之后可按需移除旧包。
- **迁移后的滚动重启**：每次重启前用 `silo healthcheck --maintenance cluster` 把关；退出码 `0` 表示停掉本节点仍保有写 quorum，HTTP `412` 表示不能停。
