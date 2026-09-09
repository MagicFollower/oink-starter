---
title: "软件检查清单"

weight: 30
---

<a id="minio-software-checklists"></a>
<a id="id1"></a>

在为生产级分布式 MinIO 部署规划软件配置时，请使用以下检查清单。

## MinIO 前置条件 {#minio}

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>运行 Linux 操作系统且内核版本为 6.6+ 的服务器。Red Hat Enterprise Linux (RHEL) 10 或 Ubuntu LTS 22.04.01+ 默认提供这类内核。
确保所选操作系统使用 LTS 且仍受支持的 6.6+ Linux 内核版本。</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>一种在节点之间同步时间的方法，例如 <code>ntp</code>、<code>timedatectl</code> 或 <code>timesyncd</code>。
具体使用哪种方法取决于操作系统。
请查阅你的操作系统文档，了解如何与时间服务器同步时间。</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>禁用会对文件系统、系统级调用或内核级调用进行索引、扫描或审计的系统服务。
这些服务可能因资源争用或拦截 MinIO 操作而降低性能。</p><p>MinIO 强烈建议在运行 MinIO 的主机上卸载或禁用以下服务：</p><ul><li><p><code>mlocate</code> 或 <code>plocate</code></p></li><li><p><code>updatedb</code></p></li><li><p><code>auditd</code></p></li><li><p>Crowdstrike Falcon</p></li><li><p>杀毒软件 (<code>clamav</code>)</p></li></ul><p>上述列表列出了在 MinIO 这类高性能系统上，最常见的、已知会引发性能或行为问题的服务或软件。
对于在 MinIO 主机上功能与上述项目类似的其他服务或软件，也应考虑移除或禁用。</p><p>或者，将这些服务配置为忽略或排除 MinIO 服务端进程，以及 MinIO 访问的 <em>全部</em> 驱动器或驱动器路径。</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>对远程服务器具有系统管理员访问权限</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>一种分布式系统管理工具，例如 Ansible、Terraform，或在编排环境中使用 Kubernetes。
Kubernetes 基础设施应使用 MinIO Operator 以获得最佳效果。</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>用于处理请求路由的负载均衡器（例如 <a href="https://www.nginx.com/">NGINX</a>）</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>用于监控和指标采集的 <a href="/docs/operations/monitoring/collect-minio-metrics-using-prometheus/#minio-metrics-collect-using-prometheus">Prometheus</a> 或兼容 Prometheus 的方案</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>已完成 <a href="/docs/operations/monitoring/grafana/#minio-grafana">Grafana 配置</a>，用于仪表板展示</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>（可选）在本地主机系统上安装 <a href="/docs/reference/minio-mc/#command-mc"><code>mc</code></a></p></td>
    </tr>
  </tbody>
</table>

## 安装 MinIO {#id3}

在部署中的所有节点上安装相同版本的 MinIO。

## 安装后任务 {#id4}

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>（可选）从本地机器使用 <a href="/docs/reference/minio-mc/mc-alias-set/#command-mc.alias.set"><code>mc alias set</code></a> 为每台服务器创建 <a href="/docs/reference/minio-mc/mc-alias/#command-mc.alias"><code>mc alias</code></a>，以便通过命令行从本地管理 MinIO 部署</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>配置 <a href="/docs/administration/bucket-replication/bucket-replication-requirements/#minio-bucket-replication-requirements">存储桶复制</a>，将一个存储桶中的内容复制到另一个存储桶位置</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>配置 <a href="/docs/operations/replication/multi-site-replication/#minio-site-replication-overview">站点复制</a>，同步多个分散数据中心位置的内容</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>使用 <a href="/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management">生命周期管理</a> 配置对象保留规则，以管理对象何时过期</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>使用分层配置 <a href="/docs/administration/object-management/object-lifecycle-management/#minio-lifecycle-management-tiering">对象存储级别规则</a>，在热、温、冷存储之间移动对象，以最大化存储成本效率</p></td>
    </tr>
  </tbody>
</table>

> [!NOTE]
> **磁盘独占访问**
>
> MinIO **要求** 对用于对象存储的磁盘或卷拥有 *独占* 访问权限。 任何其他进程、软件、脚本或人员都不应直接对提供给 MinIO 的磁盘或卷， 或 MinIO 在其上放置的对象或文件执行 *任何* 操作。
>
> 除非得到 MinIO Engineering 的明确指示，否则不要使用脚本或工具直接修改、 删除或移动这些磁盘上的任何数据分片、校验分片或元数据文件，包括在磁盘或节点 之间迁移这些文件。 这类操作极有可能导致大范围损坏和数据丢失，超出 MinIO 的自愈能力。

## 第三方身份提供商任务 {#id5}

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td>使用 <a href="/docs/developers/security-token-service/#minio-security-token-service">Security Token Service (STS)</a> 对 MinIO 进行身份验证<br />启用该功能需要 MinIO 支持。<br /></td>
    </tr>
  </tbody>
</table>