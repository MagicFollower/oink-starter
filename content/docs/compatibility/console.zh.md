---
title: "Console 兼容性注记"
linkTitle: "Console"
description: "SILO Console 与上游 MinIO Console 的差异"

weight: 30
type: docs
icon: fa-solid fa-window-maximize
---

SILO Console 是 Silo 构建的 MinIO Console。本页记录二者在哪些地方可以互换使用，在哪些地方存在差异。

[`pgsty/silo-console`](https://github.com/pgsty/silo-console) 延续上游 `minio/console` 的历史，起点是其最终提交 [`feff71e4`](https://github.com/pgsty/silo-console/commit/feff71e48e39547834399a84a9460edb4fb50563)（2026-04-16），品牌重塑自 `50797deb`（2026-08-04）开始。上游仓库已不再公开 —— `github.com/minio/console` 现在返回 404，而 `minio/mc` 只是归档 —— 因此源码谱系只在这个分支中留存。Go 模块路径仍可解析，因为模块代理继续提供它此前缓存的版本。分支至今的发布版本：[v2.0.0](/blog/release/console-2.0.0/)、[v2.1.0](/blog/release/console-2.1.0/)、[v2.1.1]、[v2.2.0](/blog/release/console-2.2.0/)、[v2.2.1]。

## 原则 {#principles}

本分支遵循与 Silo 其余部分相同的规则：**交付物及其分发渠道改名，其它软件所依赖的接口不改。**

- **改名** —— 磁盘上的产物（`silo-console`）、界面与 `--version` 中的产品标识、分发渠道、签名密钥。
- **不变** —— Go 模块路径 `github.com/minio/console`、全部 `CONSOLE_*` 环境变量（含 `CONSOLE_MINIO_SERVER` 与 `CONSOLE_MINIO_REGION`）、Web 应用调用的 REST API 结构，以及打包标识 `minio-console.service`、`console-user`、`/etc/default/console` —— 因此原地升级软件包依然可用。
- **切断** —— 自动自更新、遥测、分析、信标、外部脚本与字体、以及 call-home。只有在显式配置时才会访问版本目录，入口是 `SILO_RELEASE_SERVICE_HOST`，并保留 `RELEASE_SERVICE_HOST` 作为兼容回退。
- **保留** —— 上游版权与 AGPL-3.0 许可证。运行时输出同时致谢 MinIO, Inc. 与 PGSTY。

> [!NOTE]
> SILO Console 不是通用 S3 浏览器。它的管理功能需要 Silo 在 S3 API 之外实现的 MinIO 兼容管理 API。

## 差异 {#changed}

### 1. 保留了完整的管理控制台 {#scope}

这是最大的功能差异，方向与通常的分支相反：上游把社区版控制台裁剪成了对象浏览器，SILO Console 保留了完整的管理界面 —— 仪表盘、健康状态、日志、诊断与速度测试；存储桶、对象、生命周期、复制、通知与分层管理；用户、用户组、服务账号、策略、身份提供方与 KMS 配置；以及服务器配置。

### 2. 仪表盘面向 Metrics V3 {#metrics}

仪表盘组件查询 **MinIO Metrics V3** 指标目录 —— 也就是当前部署实际抓取的那一套 —— 并针对其零值语义与按节点导出的语义做了保护，使面板能区分"真实的零"与"数据缺失"。映射关系记录在 [`docs/metrics-v3.md`](https://github.com/pgsty/silo-console/blob/main/docs/metrics-v3.md)。

### 3. 更小、更安静的产物 {#payload}

内嵌前端从约 10 MB 降到 3 MB 以内，可逐字节复现构建，并由发布门禁强制校验。没有任何形式的遥测，页面本身也没有外部网络依赖。

### 4. 双语界面 {#i18n}

界面、帮助内容与文档链接提供英文与中文，通过页面级切换使用，且未引入额外的运行时依赖。

### 5. 面向开发者：模块图 {#source}

Go 模块路径继续保留为 `github.com/minio/console`，作为兼容接口；但
Console 的维护源码已经直接 import 并 require
`github.com/pgsty/silo-pkg/v3` v3.13.2，不再通过上游路径的 replace 选择
共享包。`minio-go` 是明确例外，直接使用经过验证的上游版本。

维护图只剩一条 replace：在保留历史模块路径的同时选择已发布的
`pgsty/mc` 源码：

```go
replace (
	github.com/minio/mc => github.com/pgsty/mc ...
)
```

Go 不会继承依赖模块里的 replace，因此内嵌 Console 的 SILO 服务端必须
复制这条 `mc` 选择。发布硬门禁对应的是由 SILO、SILO Console、
`pgsty/mc` 与 `silo-pkg` 组成的 PGSTY 协调栈。

项目仍会尽最大努力探测上游 MinIO 与上游 `mc` 的构建兼容性，但这些
任务只是兼容信号，不是依赖下限或发布门禁：只在上游图中出现的失败会被
调查和记录，但不能以降级 `silo-pkg` 或复制其 API 为代价。少量
`github.com/minio/pkg/v3` 仍可能由 `minio/colorjson` 等历史依赖间接带入；
Console 的维护行为来自 `silo-pkg`。

> [!NOTE]
> 自 Console [v2.3.0]（2026-09-01）起，模块直接 require `github.com/pgsty/silo-pkg/v3`：`silo-pkg` v3.13.0 已迁到该模块路径。仍通过 `replace github.com/minio/pkg/v3 => …` 选择 `silo-pkg` 的服务端，必须先迁移自身 import 才能采用这一 Console 版本线。Silo 服务端内嵌的是 Console 提交 `43f8447fd`：v2.3.0 线上模块路径迁移之前的最后一个提交，含 v2.3.0 的全部安全修复。

## 迁移 {#migration}

已有的 MinIO Console 部署可以原地升级。服务单元、服务账号与配置文件名称都不变，全部 `CONSOLE_*` 变量按原样读取，因此通常的做法是用 `silo-console` 软件包覆盖安装后重启。

有两处行为会在首次启动后改变，值得提前预期：

- `silo-console` 不会自我更新。请通过软件包、镜像或编排系统来推送新版本。
- 任何依赖控制台访问 MinIO 运营服务的流程 —— 更新源、许可、遥测 —— 都不再有可访问的对端。

## 参见 {#see-also}

- [Silo 服务器兼容性](/docs/compatibility/server/) —— 本控制台所管理的服务器
- [MCLI 客户端兼容性](/docs/compatibility/mcli/) —— 命令行客户端
- [Console 发布说明](/zh/tags/console/) 与 [`CHANGELOG.md`](https://github.com/pgsty/silo-console/blob/main/CHANGELOG.md)

[v2.1.1]: https://github.com/pgsty/silo-console/releases/tag/v2.1.1
[v2.2.1]: https://github.com/pgsty/silo-console/releases/tag/v2.2.1
[v2.3.0]: https://github.com/pgsty/silo-console/releases/tag/v2.3.0
