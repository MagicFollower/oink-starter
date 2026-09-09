---
title: "mc idp ldap enable"

weight: 30
---

<a id="mc-idp-ldap-enable"></a>
<a id="minio-mc-idp-ldap-enable"></a>

<a id="command-mc.idp.ldap.enable"></a>

## 描述 {#id2}

[`mc idp ldap enable`](#command-mc.idp.ldap.enable) 命令用于启用当前已配置的 AD/LDAP 提供程序。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例在 `myminio` 部署上启用 AD/LDAP 配置。

```shell
mc idp ldap enable   \
            myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令具有以下语法：

```shell
mc [GLOBALFLAGS] idp ldap enable  \
                          ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以启用 AD/LDAP 集成。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.enable.ALIAS}

*mc-cmd*

*Required*

要启用 AD/LDAP 集成的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap enable myminio
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。