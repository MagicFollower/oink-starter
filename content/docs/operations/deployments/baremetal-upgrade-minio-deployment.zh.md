---
title: "升级 Silo 部署"

weight: 20
---

<a id="minio"></a>
<a id="minio-upgrade"></a>

> [!WARNING]
> **从上游旧版本迁移**
>
> 如果部署仍运行早于 [`RELEASE.2024-03-30T09-41-56Z`](https://github.com/minio/minio/releases/tag/RELEASE.2024-03-30T09-41-56Z) 的上游 MinIO，且启用了 AD/LDAP，请先阅读上游 [`RELEASE.2024-04-18T19-09-19Z`](https://github.com/minio/minio/releases/tag/RELEASE.2024-04-18T19-09-19Z) 的发布说明，并完成其中的迁移步骤，再切换到 Silo。这里的名称与链接用于标识上游发布契约，刻意保留不改。

升级 Silo 时，应先在每个节点安装经过校验的服务端制品，再把整个部署作为一次协调操作重启。全量集群重启会造成短暂不可用；应用应重试失败或中断的请求，对象操作的原子性并不能替代重试处理。

本页覆盖由 `systemctl` 管理和手工管理的裸机部署。若服务由 Ansible、Terraform、容器或其他编排器管理，请通过该工具落实同样的发布、校验与重启边界，不要手工修改其管理的文件。

## 升级前准备 {#id2}

1. **备份集群设置。** 使用 [`mc admin cluster bucket export`](/docs/reference/minio-mc-admin/mc-admin-cluster-bucket-export/#command-mc.admin.cluster.bucket.export) 与 [`mc admin cluster iam export`](/docs/reference/minio-mc-admin/mc-admin-cluster-iam-export/#command-mc.admin.cluster.iam.export) 导出存储桶元数据和 IAM 配置。
2. **选择已经公开发布的 Silo 版本。** 以[下载与安装](/zh/download/#server)、[Silo 发布说明](/blog/release/)和 [GitHub Releases](https://github.com/pgsty/silo/releases)为准。本地标签、分支提交、草稿 Release 或上传到草稿中的制品都不等于公开发布。
3. **校验制品。** 将 SHA-256 摘要与该精确版本随附的校验和核对；所有节点固定到同一个版本。
4. **阅读跨越的全部发布说明。** 特别关注格式、身份认证、配置和降级限制。
5. **在低环境验证完全相同的升级。** 上生产前覆盖代表性的读写、策略、生命周期、复制、通知与恢复流程。
6. **禁用继承的原地更新器。** 在服务端环境中设置 `MINIO_UPDATE=off`，并重启服务让配置生效。
7. **检查桶级策略中的对象级资源。** 在导出的 IAM 配置里，查找那些把十二个桶级写动作之一（或 `s3:*`）授在含 `/` 的资源模式上、且同一个桶没有裸桶 ARN 的语句。这些语句不再授权那些动作。请在对象模式旁边补上裸桶 ARN，参见[存储桶资源与对象资源](/docs/administration/identity-access-management/policy-based-access-control/#bucket-and-object-resources)。内置策略以及任何使用 `arn:aws:s3:::*` 的语句都不受影响。

> [!CAUTION]
> **不要对 Silo 使用 `mc admin update ALIAS`**
>
> 截至 2026-08-05，最新公开 Silo 服务端在省略更新 URL 时，仍会选择上游 `dl.min.io` 发布源和上游 MinIO 签名密钥。因此该命令可能把 Silo 替换成上游二进制。请使用下面经过校验的软件包或二进制流程。另一个客户端命令 [`mc update`](/docs/reference/minio-mc/mc-update/#command-mc.update) 已被禁用，不能执行升级。

<a id="minio-upgrade-systemctl"></a>

## `systemctl` 管理的部署 {#systemctl-minio}

1. 从[下载与安装](/zh/download/#server)为每个节点下载同一个公开服务端版本，并校验其摘要。
2. 在 **不单独重启部分集群** 的前提下，在每个节点安装软件包或替换二进制：

   {{< tabs group="rpmrhel-debdebianubuntu-tab3" >}}
   {{< tab label="RPM（RHEL 系）" value="rpmrhel" >}}
   ```shell
   sudo dnf install /path/to/minio.rpm
   ```
   {{< /tab >}}
   {{< tab label="DEB（Debian/Ubuntu）" value="debdebianubuntu" >}}
   ```shell
   sudo dpkg -i /path/to/minio.deb
   ```
   {{< /tab >}}
   {{< tab label="二进制" value="tab3" >}}
   ```shell
   sha256sum ./minio
   sudo install -m 0755 ./minio /usr/local/bin/minio
   ```

   如果安装位置不同，请把 `/usr/local/bin/minio` 替换成 `command -v minio` 返回的路径。
   {{< /tab >}}
   {{< /tabs >}}

3. 在每个节点运行 `minio --version`。只有所有节点都报告同一个预期版本时才能继续。
4. 把所有服务端进程作为一次协调操作重启。管理 API 可用时执行：

   ```shell
   mc admin service restart ALIAS
   ```

   否则通过自动化在所有节点协调执行 `systemctl restart minio`。除非目标发布明确支持混合版本，否则不要临时改成滚动升级。
5. 使用 [`mc admin info`](/docs/reference/minio-mc-admin/mc-admin-info/#command-mc.admin.info) 验证部署，然后测试代表性的 S3 读写、控制台访问、身份登录以及已配置的复制或通知。
6. 从[下载与安装](/zh/download/#client)单独升级客户端。独立制品使用 `mcli`，源码构建与容器保留 `mc`。

<a id="id8"></a>

## 手工管理的部署 {#minio-upgrade-mc-admin-update}

对于由用户脚本或其他 supervisor 管理的进程，请在每个节点下载并校验同一个 Silo 二进制，替换 supervisor 实际使用路径上的可执行文件，确认 `minio --version`，再把所有节点作为一次协调操作重启。服务账户必须能够执行新二进制，执行替换的运维用户必须能够写入安装路径。

重启后执行与上文相同的验证。验证完成前保留上一个经过校验的二进制，使任何回滚决定都能遵循目标版本发布说明中的降级限制。