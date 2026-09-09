---
title: "mc idp ldap policy entities"

weight: 30
---

<a id="mc-idp-ldap-policy-entities"></a>
<a id="minio-mc-idp-ldap-policy-entities"></a>

<a id="command-mc.idp.ldap.policy.entities"></a>

## 说明 {#id2}

[`mc idp ldap policy entities`](#command-mc.idp.ldap.policy.entities) 命令显示用户、组和/或策略的映射关系列表。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下示例列出 `myminio` 部署中某个特定策略、一组用户组以及部分用户的所有映射关系。

具体包括：

- 映射到 `finteam-policy` 策略的用户。
- 分配给 `uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io` 用户的策略。
- 分配给 `cn=projectb,ou=groups,ou=swengg,dc=min,dc=io` 组的策略。

```shell
mc idp ldap policy entities myminio                                                  \
                            --policy finteam-policy                                  \
                            --user 'uid=bobfisher,ou=people,ou=hwengg,dc=min,dc=io'  \
                            --group 'cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] idp ldap policy entities                       \
                                 ALIAS                          \
                                 [--group `value`, -g `value`]  \
                                 [--policy value]               \
                                 [--user `value`, -u `value`]
```

- 将 `ALIAS` 替换为 MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，用于配置 AD/LDAP 集成。
- 在命令中可按需多次使用 `--user`、`--group` 和/或 `--policy` 标志。
- 对于每个标志，输出会列出映射到指定策略、用户或组的实体。
- 省略所有标志将返回所有策略的映射关系列表。

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.idp.ldap.policy.entities.ALIAS}

*mc-cmd*

*Required*

要显示实体映射关系的 MinIO 部署 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)。

例如：

```text
mc idp ldap policy entities myminio
```

##### `--group` {#mc.idp.ldap.policy.entities.-group}

*mc-cmd*

*Optional*

返回与指定组关联的用户和策略列表。 重复此标志可返回多个组的列表。

##### `--policies` {#mc.idp.ldap.policy.entities.-policies}

*mc-cmd*

*Optional*

返回与指定策略关联的用户和组列表。 重复此标志可返回多个策略的列表。

##### `--user` {#mc.idp.ldap.policy.entities.-user}

*mc-cmd*

*Optional*

返回该用户所属的组列表，以及与每个组关联的策略。 输出仅包含已分配策略的组。

重复此标志可返回多个用户的列表。

### 示例 {#id4}

以下示例列出 `myminio` 部署中映射到两个策略 `policy1` 和 `policy2` 的实体，以及映射到 `projectb` 组的实体：

```shell
mc idp ldap policy entities myminio                                                 \
                          policy1                                                 \
                          policy2                                                 \
                          --group='cn=projectb,ou=groups,ou=swengg,dc=min,dc=io'
```

### 全局标志 {#id5}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 行为 {#id6}

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。