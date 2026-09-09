---
title: "以容器方式部署 Silo"

weight: 30
---

<a id="minio"></a>
<a id="deploy-minio-container"></a>

本页说明如何在支持容器化进程的操作系统上以容器方式部署 Silo。

本文档假定已安装 Docker、Podman 或其他支持标准容器镜像格式的类似 runtime。已发布的 `pgsty/silo` 发行镜像使用 [Red Hat Universal Base Image 9 Micro](https://catalog.redhat.com/software/container-stacks/detail/609560d9e2b160d361d24f98)。

Silo 容器的功能和性能可能会受到基础操作系统的限制。

本步骤包含对 单机多盘 (SNMD) 和 单机单盘 (SNSD) 拓扑的指导，适用于早期开发和评估环境。

> [!WARNING]
> **重要**
>
> 下面的示例仅覆盖用于开发或评估的单机单盘和单机多盘部署；它们不构成 Docker Compose、Docker Swarm 或其他容器编排器上的生产级多机多盘拓扑或升级契约。生产环境的分布式部署应使用经过验证的 [Kubernetes Tenant 流程](/docs/operations/deployments/k8s-deploy-minio-tenant-helm-on-kubernetes/)，并针对实际环境验证持久化、网络、故障域与升级。
>
> 为便于阅读，示例使用 `pgsty/silo:latest`。生产环境必须固定经过测试的 Silo 发行标签或镜像摘要；`latest` 不是版本契约。
>
> `MINIO_UPDATE=off` 用于刻意禁用服务端原地更新。当前更新器仍保留上游 MinIO 发布源与签名密钥，因此容器应通过替换为经验证的 Silo 标签或摘要升级，不要运行 `mc admin update`。

## 注意事项 {#id2}

### 检查清单 {#id3}

在执行本步骤前，请先阅读我们发布的硬件、软件和安全检查清单。

### 纠删码校验 {#id4}

Silo 会根据拓扑中的节点和驱动器总数，自动为集群确定默认的 [纠删码](/docs/operations/concepts/erasure-coding/#minio-erasure-coding) 配置。你可以在设置集群时配置按对象生效的 [parity](/zh/glossary/#term-parity)，也可以让 Silo 选择默认值（生产级集群默认为 `EC:4`）。

校验值决定了对象可用性与磁盘存储占用之间的关系。可使用上游 MinIO [纠删码计算器](https://min.io/product/erasure-code-calculator) 比较校验级别，但应将它视为上游规划工具，而不是 Silo 支持契约。

虽然你可以随时更改纠删码校验设置，但以既有校验值写入的对象 **不会** 自动更新为新的校验设置。

### 容器存储 {#id5}

本步骤假定你会将一个或多个专用存储设备挂载到容器中，作为 Silo 的持久化存储。

存储在容器临时路径上的数据会在容器重启或删除时丢失。 使用此类路径的风险需自行承担。

## 步骤 {#id6}

1. 启动容器

本步骤提供 Podman 和 Docker 在 rootfull 模式下的说明。 对于 rootless 部署，请参考各 runtime 自身的文档完成配置和容器启动。

对于其他容器 runtime，请参阅对应文档，并使用等效的选项、参数或配置。

{{< tabs group="podman-docker" >}}
{{< tab label="Podman" value="podman" >}}
以下命令会先在你的主目录中创建一个文件夹，然后使用 Podman 启动 Silo 容器：

```shell
mkdir -p ~/silo/data

podman run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name silo \
   -v ~/silo/data:/data \
   -e "MINIO_UPDATE=off" \
   -e "MINIO_ROOT_USER=ROOTNAME" \
   -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
   pgsty/silo:latest server /data --console-address ":9001"
```

该命令分别将端口 `9000` 和 `9001` 绑定到 S3 API 和 Web Console。

本地驱动器 `~/silo/data` 会挂载到容器内的 `/data` 目录。你可以按需修改 [`MINIO_ROOT_USER`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_USER) 和 [`MINIO_ROOT_PASSWORD`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_PASSWORD) 变量，以变更 root 登录信息。

对于多驱动器部署，请将每个本地驱动器或其所在文件夹绑定到容器中按顺序编号的路径。 然后修改 [`minio server`](/docs/reference/minio-server/#command-minio.server) 启动命令以指定这些路径：

```shell
mkdir -p ~/minio/data-{1..4}

podman run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name silo \
   -v /mnt/drive-1:/mnt/drive-1 \
   -v /mnt/drive-2:/mnt/drive-2 \
   -v /mnt/drive-3:/mnt/drive-3 \
   -v /mnt/drive-4:/mnt/drive-4 \
   -e "MINIO_UPDATE=off" \
   -e "MINIO_ROOT_USER=ROOTNAME" \
   -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
   pgsty/silo:latest server /mnt/drive-{1...4} --console-address ":9001"
```

对于 Windows 主机，请使用 Windows 文件系统语义指定本地文件夹路径，例如 `C:\minio\:/data`。
{{< /tab >}}
{{< tab label="Docker" value="docker" >}}
以下命令会先在你的主目录中创建一个文件夹，然后使用 Docker 启动 Silo 容器：

```shell
mkdir -p ~/silo/data

docker run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name silo \
   -v ~/silo/data:/data \
   -e "MINIO_UPDATE=off" \
   -e "MINIO_ROOT_USER=ROOTNAME" \
   -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
   pgsty/silo:latest server /data --console-address ":9001"
```

该命令分别将端口 `9000` 和 `9001` 绑定到 S3 API 和 Web Console。

本地驱动器 `~/silo/data` 会挂载到容器内的 `/data` 目录。你可以按需修改 [`MINIO_ROOT_USER`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_USER) 和 [`MINIO_ROOT_PASSWORD`](/docs/reference/minio-server/settings/root-credentials/#envvar.MINIO_ROOT_PASSWORD) 变量，以变更 root 登录信息。

对于多驱动器部署，请将每个本地驱动器或其所在文件夹绑定到容器中按顺序编号的路径。 然后修改 [`minio server`](/docs/reference/minio-server/#command-minio.server) 启动命令以指定这些路径：

```shell
mkdir -p ~/minio/data-{1..4}

docker run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name silo \
   -v /mnt/drive-1:/mnt/drive-1 \
   -v /mnt/drive-2:/mnt/drive-2 \
   -v /mnt/drive-3:/mnt/drive-3 \
   -v /mnt/drive-4:/mnt/drive-4 \
   -e "MINIO_UPDATE=off" \
   -e "MINIO_ROOT_USER=ROOTNAME" \
   -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
   pgsty/silo:latest server /mnt/drive-{1...4} --console-address ":9001"
```

对于 Windows 主机，请使用 Windows 文件系统语义指定本地文件夹路径，例如 `C:\minio\:/data`。
{{< /tab >}}
{{< /tabs >}}

### 2. 连接到部署 {#id7}

{{< tabs group="tab1-cli" >}}
{{< tab label="控制台" value="tab1" >}}
在浏览器中打开 [http://localhost:9001](http://localhost:9001) 以访问 [Silo Console](/docs/administration/minio-console/#minio-console) 登录页。

使用上一步中的 **MINIO_ROOT_USER** 和 **MINIO_ROOT_PASSWORD** 进行登录。

<img src="/images/silo-console/console-login.webp" alt="MinIO Console 登录页" style="max-width: 600px; height: auto;" />

你可以使用内嵌 Console 执行常规管理任务，例如身份与访问管理、指标和日志监控，或 Server 配置。
{{< /tab >}}
{{< tab label="CLI" value="cli" >}}
请按照 [Silo 客户端安装说明](/docs/reference/minio-mc/#mc-install) 安装 `mcli`，并运行 `mcli --version` 验证。已发布的独立归档与 Linux 软件包安装 `mcli`；源码构建和客户端容器则保留 `mc` 可执行文件名。

安装完成后，为该 Silo 部署创建一个别名：

```shell
mcli alias set silo http://localhost:9000 USERNAME PASSWORD
```

请根据你的部署修改主机名、用户名和密码。
{{< /tab >}}
{{< /tabs >}}