---
title: "mc license update"

weight: 30
---

<a id="mc-license-update"></a>

<a id="command-mc.license.update"></a>

## 描述 {#id2}

使用 [`mc license update`](#command-mc.license.update) 命令为部署替换许可证密钥。

对于已在 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 注册的部署，MinIO 每月会自动检查并更新许可证。

## 示例 {#id3}

### 更新别名为 `minio1` 的部署许可证密钥 {#minio1}

```shell
mc license update minio1 license.key
```

## 语法 {#id4}

该命令具有以下语法：

```shell
mc [GLOBALFLAGS] license update                   \
                         ALIAS                    \
                         [LICENSE-FILE-WITH-PATH] \
                         [--airgap]
```

### 参数 {#id5}

##### `ALIAS` {#mc.license.update.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `LICENSE-FILE-WITH-PATH` {#mc.license.update.LICENSE-FILE-WITH-PATH}

*mc-cmd*

*Optional*

用于更新部署许可证的密钥文件路径（相对于当前工作目录）和文件名。

从 SUBNET 下载 API key：

1. 登录 [MinIO SUBNET](https://min.io/pricing?jmp=docs)
2. 转到 **Deployments** 选项卡
3. 在页面顶部、账户统计信息框右侧，选择 **API Key** 按钮
4. 选择 key 字段右侧的复制按钮，将 key 值复制到剪贴板

##### `--airgap` {#mc.license.update.-airgap}

*mc-cmd*

*Optional*

在无法通过网络访问 SUBNET 的环境中使用（例如 airgapped、firewalled 或类似配置）。

如果部署是 airgapped，但你使用 [minio client](/docs/reference/minio-mc/#minio-client) 的本地设备有网络访问能力，则无需使用 `--airgap` 标志。

### 全局标志 {#id6}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。