---
title: "mc license register"

weight: 20
---

<a id="mc-license-register"></a>

<a id="command-mc.support.register"></a>

<a id="command-mc.license.register"></a>

> [!WARNING]
> **重要**
>
> `mc license register` 需要 [MinIO Client](/docs/reference/minio-mc/#minio-client) `RELEASE.2023-11-20T16-30-59Z` 或更高版本。 虽非强制要求，但最佳实践是保持 [MinIO 客户端版本](/docs/reference/minio-mc/#mc-client-versioning) 与 MinIO 服务端版本一致。

## 描述 {#id2}

[`mc license register`](#command-mc.license.register) 命令会将你的部署与 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 账户关联。

注册后，你可以使用 [`mc support diag`](/docs/reference/minio-mc/mc-support-diag/#command-mc.support.diag) 命令将部署健康报告直接上传到 SUBNET。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
> 以下示例将 `minio` [alias](/docs/reference/minio-mc/mc-alias-set/#alias) 注册到 [MinIO SUBNET](https://min.io/pricing?jmp=docs)：

```shell
mc license register minio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] license register ALIAS                      \
                         [--airgap]                          \
                         [--api-key <string>]                \
                         [--license <path to license file>]  \
                         [--name <value>]
```
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.license.register.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

##### `--airgap` {#mc.license.register.-airgap}

*mc-cmd*

*Optional*

用于无法访问 SUBNET 网络的环境（例如 airgapped、受防火墙限制或类似配置）。

说明请参见 [airgap 示例](#minio-license-register-airgap)。

如果部署处于 airgapped 环境，但你运行 [minio client](/docs/reference/minio-mc/#minio-client) 的本地设备可以访问网络，则无需使用 `--airgap` 标志。

##### `--api-key` {#mc.license.register.-api-key}

*mc-cmd*

SUBNET 上账户的 API key。

对应环境变量 `MC_SUBNET_API_KEY`。

获取 API key 的步骤：

1. 登录 [MinIO SUBNET](https://min.io/pricing?jmp=docs)
2. 进入 **Deployments** 选项卡
3. 在页面顶部、账户统计信息框右侧，选择 **API Key** 按钮
4. 选择 key 字段右侧的复制按钮，将 key 值复制到剪贴板

##### `--license` {#mc.license.register.-license}

*mc-cmd*

*Optional*

用于注册部署的 license 文件路径。

你必须先从 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 下载该账户的 license 文件。

1. 登录 [MinIO SUBNET](https://min.io/pricing?jmp=docs)
2. 进入 **Deployments** 选项卡
3. 在页面顶部、账户统计信息框右侧，选择 **License** 按钮
4. 选择 license 字段右侧的复制按钮，将 key 值复制到剪贴板，或 选择 **Download** 按钮将 license 的 txt 文件保存到本地

##### `--name` {#mc.license.register.-name}

*mc-cmd*

*Optional*

指定一个不同于 alias 的名称，用于在 SUBNET 中关联该 MinIO 部署。

使用 `--name <value>`，将 `<value>` 替换为你希望在 SUBNET 上为该部署使用的名称。

## 示例 {#id4}

### 使用部署名称注册部署 {#id5}

将 alias 为 `minio1` 的 MinIO 部署注册到 SUBNET，并使用 `minio1` 作为部署名称：

```shell
mc license register minio1
```

如果尚未注册，系统会提示输入该部署的 SUBNET 凭证。

### 使用账户的 License 文件注册部署 {#license}

将 alias 为 `minio5` 的新 MinIO 部署注册到 SUBNET，并使用为该账户下载的 license 文件：

```shell
mc license register minio5 /path/to/minio.license
```

如果尚未下载，你可以从 SUBNET 下载 license 文件。

1. 登录 [MinIO SUBNET](https://min.io/pricing?jmp=docs)
2. 进入 **Deployments** 选项卡
3. 在页面顶部、账户统计信息框右侧，选择 **License** 按钮
4. 选择 **Download** 按钮将 license 的 txt 文件保存到本地

### 使用不同的部署名称注册部署 {#id6}

将 alias 为 `minio2` 的 MinIO 部署注册到 SUBNET，并使用 `second-deployment` 作为名称：

```shell
mc license register minio2 --name second-deployment
```

<a id="id7"></a>

### 在无法直接访问互联网时注册部署 {#minio-license-register-airgap}

将 alias 为 `minio3` 的 MinIO 部署注册到 SUBNET；该部署由于防火墙、airgap 或类似原因无法直接访问互联网。

> [!NOTE]
> **变更: mc**
>
> RELEASE.2022-07-29T19-17-16Z
>
> airgap 注册流程适用于 `RELEASE.2022-07-29T19-17-16Z` 或更高版本的 MinIO 客户端。 早期版本的 MinIO 客户端 无法注册 airgapped 部署。

```shell
mc license register minio3 --airgap
```

1. 运行命令，返回带有 token 的注册链接
2. 在 Web 浏览器中打开复制的注册链接，并登录 SUBNET
3. 选择部署 **License** 编号右侧的 **?** 按钮
4. 在弹窗中选择下载链接，并将 key 保存到你有访问权限的路径
5. 在命令行中运行以下命令

   ```shell
   mc license update minio3 <path-to-file>
   ```

   将 `<path-to-file>` 替换为你从 SUBNET 下载的文件路径。

## 语法 {#id8}

命令语法如下：

```shell
mc [GLOBALFLAGS] license register       \
                         ALIAS          \
                         [--name value] \
                         [--airgap]
```

### 全局标志 {#id9}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id10}

### 自动更新 License {#id11}

> [!NOTE]
> **新增: RELEASE.2023-01-18T04-36-38Z**

注册到 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 后，MinIO 会每月自动检查并更新 license。

在 airgapped 或其他服务器无法直接访问互联网的环境中，使用带文件路径的 [`mc license update`](/docs/reference/minio-mc/mc-license-update/#command-mc.license.update) 来更新注册。