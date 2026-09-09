---
title: "mc idp ldap rm"

weight: 60
---

<a id="mc-idp-ldap-rm"></a>
<a id="minio-mc-idp-ldap-rm"></a>

<a id="command-mc.idp.ldap.rm"></a>

<a id="command-mc.idp.ldap.remove"></a>

## 说明 {#id2}

[`mc idp ldap rm`](#command-mc.idp.ldap.rm) 命令移除 AD/LDAP 提供方的现有配置。

[`mc idp ldap rm`](#command-mc.idp.ldap.rm) 也称为 [`mc idp ldap remove`](#command-mc.idp.ldap.remove)。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例移除 `myminio` 部署的 AD/LDAP 提供方设置。

```shell
mc idp ldap rm       \
            myminio
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
该命令的语法如下：

```shell
mc [GLOBALFLAGS] idp ldap rm     \
                          ALIAS
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以移除 AD/LDAP 集成。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.remove.ALIAS}

*mc-cmd*

*Required*

要移除其当前 AD/LDAP 配置的 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap rm myminio
```

### 全局标志 {#id4}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id5}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。