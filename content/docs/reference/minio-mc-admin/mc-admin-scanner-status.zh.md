---
title: "mc admin scanner status"

weight: 10
---

<a id="mc-admin-scanner-status"></a>

<a id="command-mc.admin.scanner.info"></a>

<a id="command-mc.admin.scanner.status"></a>

## 描述 {#id2}

[`mc admin scanner status`](#command-mc.admin.scanner.status) 命令会显示 MinIO Server 的 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) 信息的实时摘要。

该命令的别名为 `mc admin scanner info`。

> [!NOTE]
> **仅在 MinIO 部署上使用 `mc admin`**
>
> MinIO 不支持将 [`mc admin`](/docs/reference/minio-mc-admin/#command-mc.admin) 命令用于其他 S3 兼容服务， 无论这些服务声称与 MinIO 部署具有何种兼容性。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例返回扫描器进程当前状态的信息。

```shell
mc admin scanner status myminio
```

该命令返回的结果类似如下：

```shell
Overall Statistics
------------------
Last full scan time:   0d0h15m; Estimated 2879.79/month
Current cycle:         (between cycles)
Active drives: 0

Last Minute Statistics
----------------------
Objects Scanned:       3 objects; Avg: 67.611µs; Rate: 4320/day
Versions Scanned:      3 versions; Avg: 2.506µs; Rate: 4320/day
Versions Heal Checked: 0 versions; Avg: 0ms
Read Metadata:         3 objects; Avg: 40.817µs, Size: 395 bytes/obj
ILM checks:            3 versions; Avg: 714ns
Check Replication:     3 versions; Avg: 892ns
Verify Deleted:        0 folders; Avg: 0ms
Yield:                 18ms total; Avg: 6ms/obj
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc admin scanner status ALIAS
                       [--bucket <string>]     \
                       [--interval <value>]   \
                       [--max-paths <value>]  \
                       [-n <integer>]         \
                       [--nodes <string>]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.admin.scanner.status.ALIAS}

*mc-cmd*

*Required*

用于显示 [scanner](/docs/operations/concepts/scanner/#minio-concepts-scanner) API 操作的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--bucket` {#mc.admin.scanner.status.-bucket}

*mc-cmd*

*Optional*

将 scanner 统计信息过滤到指定存储桶。

##### `--interval` {#mc.admin.scanner.status.-interval}

*mc-cmd*

*Optional*

两次状态请求刷新之间等待的秒数。 如果未指定，状态每 3 秒刷新一次。

##### `--max-paths` {#mc.admin.scanner.status.-max-paths}

*mc-cmd*

*Optional*

要显示的活跃路径的最大数量。 使用 `-1` 表示不限制路径数量。

当被扫描的驱动器数量较大时，限制显示路径数量可以减少控制台窗口滚动。

如果未指定，结果将返回不限制数量的活跃路径。

##### `-n` {#mc.admin.scanner.status.-n}

*mc-cmd*

*Optional*

在自动退出前返回的状态请求数量。 使用 `0` 表示返回不限数量的状态结果。

如果未指定，结果会按指定间隔持续刷新，直到手动退出。

##### `--nodes` {#mc.admin.scanner.status.-nodes}

*mc-cmd*

*Optional*

返回指定节点的 scanner 状态信息。 使用逗号分隔列表指定多个节点。

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。