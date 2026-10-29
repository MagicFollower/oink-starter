# Harbor 私有镜像仓库（本机真实安装）

这个目录是 [3.10 私有镜像仓库](/docs/03-镜像构建/交出去/BuildKit私有仓库标签策略与构建排错/) 那篇的「真实案例」侧：**在 Windows + Docker Desktop 上把 Harbor 装起来、开 HTTPS、并把本机 docker 配成用它**。不是抄文档步骤——每一条读数都在本机跑过，跑不通的地方留的是报错原文。

当前状态（2026-10-27 实测）：Harbor **v2.14.6**（`systeminfo` 自证 `v2.14.6-f435c950`）九个容器全 healthy，入口 `https://localhost:8443`，`docker push` / `docker pull` 双向 rc=0，`/data` 共 52.7 MB。**按约定保留在跑**，供段⑥ 与 6.x 复用；不推任何远端。

## 想读什么，按这个顺序挑

| 文件 | 一句话 |
|---|---|
| `01-为什么要用Harbor.md` | `registry:2` 37.4 MB 与 Harbor 3.46 GB 的取舍；Harbor 多给的每一项能力都标了「本机能不能验」；什么时候**不该**上 Harbor |
| `02-组件与架构.md` | 九个容器各自干什么、只有一张网、`/v2/` 为什么先经 core、一次 `docker push` 在机器里走的七步、cap_add 与数据库表清单 |
| `03-历史与版本迭代.md` | 前生今世与里程碑（CNCF 2018-07-31 接纳 / 2018-11-14 孵化 / 2020-06-15 毕业）、v1→v2 的六条 breaking、每条 minor 线的发布日与代表作、ChartMuseum/Notary/Clair 的移除链、「同时维护三条线」的 EOL 规律、v2.16.0-rc1 展望 |
| `04-快速入门.md` | 五条命令从零到第一次推拉，含前置闸门、每步预期读数、最小闭环四判据、三个最常见失败 |
| `05-本机存储目录.md` | `/data` 七个目录逐个是谁挂的、blob 落在哪（含一个 alpine 的完整落盘路径与三块字节数）、`secret/` 四件套为什么必须和数据库一起备份 |
| `06-配置HTTPS.md` | **四层信任模型**（服务端 / daemon / 客户端 / 组件间）各在哪生效、SAN 与 `ca.key` 的硬规矩、指纹三处一致的生效判据、Windows Schannel 不认 `--cacert` 的区分实验、四条走不通的路 |
| `07-本机安装与判据实录.md` | 安装全过程原文（含十条判据表）、本轮新撞的两条坑、未验证项总表 |

`README.md`（本篇）只负责导航与状态；原来写在这里的安装记录已整体搬到 `07`。

**这套文档的写法**（七篇统一，读的时候可以按这个预期找东西）：每篇第一节先讲**痛点**（为什么会需要它），中段讲**设计与机制**（配架构图与真实读数），后段讲**具体怎么用**（命令 + 判据），末节是**要点总结**；讲复杂概念时插入 `💡 新人小结` 给一个日常类比。写作与检查口径由 `.staging/audit-示例文体.py`（文体）与 `.staging/check-具名引用.py`（小节引用不能指空）两支脚本守住，本轮读数是 `AUDIT_CLEAN files=7` 与 `REFS_OK`（20 处指代）。

## 目录里有什么

| 项 | 说明 |
|---|---|
| `harborctl.py` | 唯一实现，八个子命令 `cert`/`config`/`prepare`/`up`/`status`/`trust`/`verify`/`down`，一条只做一件事 |
| `Harbor.cmd` | ASCII-only + CRLF 的转发包装（逻辑不在里面），方便双击与 `cmd /c` |
| `官方安装包留档/` | 在线包 5 个文件原件（`prepare`、`install.sh`、`common.sh`、`harbor.yml.tmpl`、`LICENSE`），留着是为了对照我改了哪几行 |
| `harbor.yml` / `input/harbor.yml` | 本机实参：345 行 = 官方模板 339 行 + 6 行说明头，只动 6 个键 |
| `docker-compose.yml` / `common/config/` | **全部由官方 `prepare` 容器生成**（256 行 / 5,886 字节；配置 13 个文件 10,461 字节），不要手改 |
| `certs/harbor-ca.crt` | 自签 CA（1,127 字节），给 `curl --cacert`、浏览器与 CI 用 |

## 三十秒判断这套东西还活着

```console
Harbor.cmd status       # 九个容器 Up (healthy) + /api/v2.0/health 带 -k 出 JSON、不带 -k 出 http=000
Harbor.cmd verify       # 十条判据链：登录 → 建项目(409/201) → push → pull → 查制品 → 统计 → 匿名 V2
```

跑之前只需要两样：能用的 Docker（本机 `Server=29.8.0 API=1.56`）与 Python 3。宿主不需要 openssl、不需要 python 依赖、不需要 go——证书生成与配置生成都在容器里做。

## 已证 / 未证（这一栏是本目录的口径）

| 已在本机证过 | 没证，别照着做 |
|---|---|
| 在线包装 → 九容器 healthy → push/pull 闭环（`07` 十条判据）；`hostname` 的 IP 拒绝与 `localhost` 可通过；daemon 对回环段不验证书（`InsecureRegistryCIDRs` 读数）；带 CA 与不带 CA 在同一非回环入口上的 200/000 对照；TLS 1.1 被拒、1.2/1.3 可协商；`/data` 与 API 统计的字节对账；重跑 `prepare` 后必须 `up -d` 否则 pull 401 | Trivy 扫描（`WITH_TRIVY=False`，没装该组件）；机器人账户/复制/GC/保留策略；**daemon 侧 `/etc/docker/certs.d` 到底读不读**（本机非回环入口 TCP 层就不通，判不了）；proxy 端口全网卡暴露的实际风险；Docker Desktop 重启后数据是否原样回来；浏览器目测 UI；`certutil` 装系统信任库；官方 `install.sh` 全流程 |

未证项的完整原因写在 `07` 的未验证项一节；版本事实与出处、取证命令在 `03`。
