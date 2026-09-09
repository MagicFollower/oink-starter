---
title: "在 Windows 上部署 Silo"

weight: 50
---

<a id="windows-minio"></a>
<a id="deploy-minio-windows"></a>

- [Object Storage Essentials](https://www.youtube.com/playlist?list=PLFOIsHSSYIK3WitnqhqfpeZ6fRFKHxIr7)
- [How to Connect to MinIO with JavaScript](https://www.youtube.com/watch?v=yUR4Fvx0D3E&list=PLFOIsHSSYIK3Dd3Y_x7itJT1NUKT5SxDh&index=5)

本页介绍如何在 Microsoft Windows 主机上部署 Silo，用于开发与评估。

Silo 为 x86-64 与 ARM64 发布 Windows 归档。当前项目 CI 在 Linux 上运行，没有覆盖 Windows 实机运行时，因此已删除继承自上游、已经过时的“正式支持 Windows 版本”清单。在生产使用前，请验证精确的 Windows 版本、文件系统、服务包装方式与工作负载。

本步骤包含对 单机多盘 (SNMD) 和 单机单盘 (SNSD) 拓扑的指导，适用于早期开发和评估环境。

本指南没有验证 Windows 主机上的多机多盘（MNMD）分布式配置。

## 注意事项 {#id2}

### 检查清单 {#id3}

在执行本步骤前，请先阅读我们发布的硬件、软件和安全检查清单。

### 纠删码校验 {#id4}

MinIO 会根据拓扑中的节点和驱动器总数，自动为集群确定默认的 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 配置。 你可以在设置集群时配置按对象生效的 [parity](/zh/glossary/#term-parity)，也可以让 MinIO 选择默认值（生产级集群默认为 `EC:4`）。

校验值决定了对象可用性与磁盘存储占用之间的关系。 可使用 MinIO [纠删码计算器](https://min.io/product/erasure-code-calculator) 选择适合你集群的纠删码校验级别。

虽然你可以随时更改纠删码校验设置，但以既有校验值写入的对象 **不会** 自动更新为新的校验设置。

## 步骤 {#id5}

### 1. 下载 Silo 二进制文件 {#minio}

从[下载与安装](/zh/download/#server)获取与架构对应的 Windows 归档，使用同一发布随附的校验和核验后，解压得到 `minio.exe`。

下一步说明如何运行该文件。请从 PowerShell 或命令提示符启动服务端，不要在资源管理器中双击运行。

### 2. 启动 MinIO Server {#minio-server}

在 PowerShell 或命令提示符中，切换到可执行文件所在目录，或将 `minio.exe` 文件路径加入系统 `$PATH`。

{{< tabs group="multi-drive-single-drive" >}}
{{< tab label="Multi-Drive" value="multi-drive" >}}
对于带有多个驱动器的 Windows 主机，你可以指定一组顺序驱动器，以便在 单机多盘 (SNMD) 拓扑中配置 MinIO：

```text
.\minio.exe server {D...G}:\minio --console-address :9001
```

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会将输出打印到系统控制台，类似如下：

```shell
API: http://192.0.2.10:9000  http://127.0.0.1:9000
RootUser: minioadmin
RootPass: minioadmin

Console: http://192.0.2.10:9001 http://127.0.0.1:9001
RootUser: minioadmin
RootPass: minioadmin

Command-line: https://silo.pgsty.com/docs/reference/minio-mc/
   $ mc alias set myminio http://192.0.2.10:9000 minioadmin minioadmin

Documentation: https://silo.pgsty.com/docs/

WARNING: Detected default credentials 'minioadmin:minioadmin', we recommend that you change these values with 'MINIO_ROOT_USER' and 'MINIO_ROOT_PASSWORD' environment variables.
```

该进程绑定到当前 PowerShell 或命令提示符窗口。 关闭窗口会停止 server 并结束该进程。
{{< /tab >}}
{{< tab label="Single-Drive" value="single-drive" >}}
使用此命令在 `C:\minio` 文件夹中启动本地 MinIO 实例。 你可以将 `C:\minio` 替换为本地主机上的其他驱动器或文件夹路径。

```text
.\minio.exe server C:\minio --console-address :9001
```

[`minio server`](/docs/reference/minio-server/#command-minio.server) 进程会将输出打印到系统控制台，类似如下：

```shell
API: http://192.0.2.10:9000  http://127.0.0.1:9000
RootUser: minioadmin
RootPass: minioadmin

Console: http://192.0.2.10:9001 http://127.0.0.1:9001
RootUser: minioadmin
RootPass: minioadmin

Command-line: https://silo.pgsty.com/docs/reference/minio-mc/
   $ mc alias set myminio http://192.0.2.10:9000 minioadmin minioadmin

Documentation: https://silo.pgsty.com/docs/

WARNING: Detected default credentials 'minioadmin:minioadmin', we recommend that you change these values with 'MINIO_ROOT_USER' and 'MINIO_ROOT_PASSWORD' environment variables.
```

该进程绑定到当前 PowerShell 或命令提示符窗口。 关闭窗口会停止 server 并结束该进程。
{{< /tab >}}
{{< /tabs >}}

### 3. 使用浏览器连接到 MinIO 服务端 {#id6}

使用浏览器（例如 Microsoft Edge）访问 `http://127.0.0.1:9001`，或访问 [`minio server`](/docs/reference/minio-server/#command-minio.server) 命令输出中列出的任意 Console 地址，以打开 [MinIO 控制台](/docs/administration/minio-console/#minio-console)。 例如，示例输出中的 `Console: http://192.0.2.10:9001 http://127.0.0.1:9001` 表示有两个可用于连接 Console 的地址。

尽管端口 `9000` 用于连接 API，MinIO 仍会自动将浏览器访问重定向到 MinIO Console。

使用输出中显示的 `RootUser` 和 `RootPass` 用户凭证登录 Console。 默认值为 `minioadmin | minioadmin`。

<img src="/images/silo-console/console-login.webp" alt="MinIO Console 显示登录界面" style="max-width: 600px; height: auto;" />

你可以使用 MinIO Console 执行常规管理任务，例如身份与访问管理、指标和日志监控，或 Server 配置。 每个 MinIO server 都包含自身内嵌的 MinIO Console。

<img src="/images/silo-console/console-object-browser.webp" alt="MinIO Console 显示存储桶起始界面" style="max-width: 600px; height: auto;" />

更多信息请参阅 [MinIO 控制台](/docs/administration/minio-console/#minio-console) 文档。

### 4. *(可选)* 安装 Silo 客户端 {#optional-minio-client}

[Silo 客户端](/docs/reference/minio-mc/#minio-client)允许你从 PowerShell 与部署交互。

从[下载与安装](/zh/download/#client)获取 Windows 客户端归档，校验后解压得到 `mcli.exe`。

在命令提示符或 PowerShell 中运行：

```text
\path\to\mcli.exe --help
```

通过已安装的 `mcli.exe` 执行 [`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set)，即可认证并连接到部署。

```shell
mcli.exe alias set local http://127.0.0.1:9000 minioadmin minioadmin
mcli.exe admin info local
```

[`mc alias set`](/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set) 需要四个参数：

- 别名名称
- MinIO server 的主机名或 IP 地址及端口
- MinIO [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 的 Access Key
- MinIO [用户](/docs/administration/identity-access-management/minio-user-management/#minio-users) 的 Secret Key

有关此命令的更多细节，请参阅 [mc alias set](/docs/reference/minio-mc/mc-alias-set/#alias)。

### 5. 后续步骤 {#id7}

- 在可信开发网络之外暴露服务前，先[启用 TLS](/docs/operations/network-encryption/enable-minio-tls/)。
- 替换示例凭据，并通过[身份与访问管理](/docs/administration/identity-access-management/)创建最小权限用户。
- 在依赖该部署保存持久数据前，配置[监控与告警](/docs/operations/monitoring/)。