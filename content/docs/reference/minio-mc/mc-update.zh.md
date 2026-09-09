---
title: "mc update"

weight: 420
---

<a id="mc-update"></a>

<a id="command-mc.update"></a>

## 语法 {#id2}

Pigsty 维护版客户端为保持命令行兼容而保留 [`mc update`](#command-mc.update)，但 **刻意禁用了自更新**。该命令不会访问发布源、下载二进制，也不会替换已安装的 `mc`/`mcli`；它会打印错误并以状态码 `1` 退出。

请通过[下载与安装](/zh/download/#client)、[Pigsty 软件仓库](https://pigsty.cc/docs/repo/infra/list/#object-storage)或 [GitHub Releases](https://github.com/pgsty/mc/releases)升级。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令会报告自更新已禁用，并以状态码 `1` 退出：

```shell
mc update
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] update [--json] [RELEASE-URL]
```

- 方括号 `[]` 表示可选参数。
- `RELEASE-URL` 仅为兼容性而接受，不会被访问。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

非 JSON 模式的错误文本为：

```text
Self-update is disabled in the Pigsty mc fork; upgrade only through the Pigsty package repository or https://github.com/pgsty/mc/releases.
```

### 全局参数 {#id3}

##### `--json` {#mc.update.-json}

*mc-cmd*

*Optional*

把“更新已禁用”的错误格式化为一条 [JSON Lines](https://jsonlines.org/)<a id="json-lines"></a> 对象。该参数不会启用更新。

例如：

```shell
mc update --json
```