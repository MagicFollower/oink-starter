---
title: "AssumeRoleWithCustomToken"

weight: 10
---

<a id="assumerolewithcustomtoken"></a>
<a id="minio-sts-assumerolewithcustomtoken"></a>

MinIO Security Token Service (STS) 的 `AssumeRoleWithCustomToken` API 端点会生成一个令牌，用于配合 [MinIO External Identity Management Plugin](/docs/administration/identity-access-management/pluggable-authentication/#minio-external-identity-management-plugin) 使用。

## 请求端点 {#id2}

`AssumeRoleWithCustomToken` 端点的格式如下：

```shell
POST https://minio.example.net?Action=AssumeRoleWithCustomToken[&ARGS]
```

以下示例使用了所有受支持的参数。 请将 `minio.example.net` 主机名替换为你的 MinIO 集群对应 URL：

```shell
POST https://minio.example.net?Action=AssumeRoleWithCustomToken
&Token=TOKEN
&Version=2011-06-15
&DurationSeconds=86000
&RoleArn="external-auth-provider"
```

### 请求查询参数 {#id3}

此端点支持以下查询参数：

<table>
  <thead>
    <tr>
      <th><p>参数</p></th>
      <th><p>类型</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><code>Token</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必填</em></p><p>指定提交给外部身份管理器的 JSON Token。
MinIO 期望身份管理器解析该令牌，并判断是否使用该令牌对客户端请求进行认证。</p></td>
    </tr>
    <tr>
      <td><p><code>Version</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必填</em></p><p>指定 <code>2011-06-15</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>RoleArn</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必填</em></p><p>指定与此 STS 请求关联的 Identity Manager Plugin 配置 ARN。</p><p>更多信息请参见 <a href="/docs/reference/minio-server/settings/iam/minio-identity-plugin/#envvar.MINIO_IDENTITY_PLUGIN_ROLE_ID"><code>MINIO_IDENTITY_PLUGIN_ROLE_ID</code></a> 或 <a href="/docs/reference/minio-server/settings/iam/minio-identity-plugin/#mc-conf.identity_plugin.role_id"><code>identity_plugin role_id</code></a>。</p><p>请注意，MinIO 在生成 RoleArn 时会自动为已配置的 <code>ROLE_ID</code> 添加前缀 <code>idmp-</code>。
如有需要，请在 <code>ROLE_ID</code> 中包含该字符串。</p></td>
    </tr>
    <tr>
      <td><p><code>DurationSeconds</code></p></td>
      <td><p>integer</p></td>
      <td><p><em>可选</em></p><p>指定临时凭证在多少秒后过期。
默认值为 <code>3600</code>。</p><ul><li><p>最小值为 <code>900</code>，即 15 分钟。</p></li><li><p>最大值为 <code>604800</code>，即 7 天。</p></li></ul></td>
    </tr>
  </tbody>
</table>

## 响应元素 {#id4}

MinIO 返回一个 `AssumeRoleWithCustomTokenResult` 对象，其中 `AssumedRoleUser.Credentials` 对象包含 MinIO 生成的临时凭证：

- `AccessKeyId` - 应用程序用于认证的访问密钥。
- `SecretKeyId` - 应用程序用于认证的 Secret Key。
- `Expiration` - 凭证过期的 <a id="index-0"></a>[**RFC3339**](https://datatracker.ietf.org/doc/html/rfc3339.html) 日期和时间。
- `SessionToken` - 应用程序用于认证的会话令牌。某些 SDK 在使用临时凭证时可能要求此字段。

以下示例与 MinIO STS `AssumeRoleWithCustomToken` 端点返回的响应类似：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AssumeRoleWithCustomTokenResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
<AssumeRoleWithCustomTokenResult>
   <Credentials>
      <AccessKeyId>ACCESS_KEY</AccessKeyId>
      <SecretAccessKey>SECRET_KEY</SecretAccessKey>
      <Expiration>YYYY-MM-DDTHH:MM:SSZ</Expiration>
      <SessionToken>TOKEN</SessionToken>
   </Credentials>
   <AssumedUser>custom:Alice</AssumedUser>
</AssumeRoleWithCustomTokenResult>
<ResponseMetadata>
   <RequestId>UNIQUE_ID</RequestId>
</ResponseMetadata>
</AssumeRoleWithCustomTokenResponse>
```

## 错误元素 {#id5}

此 API 端点的 XML 错误响应与 AWS [AssumeRoleWithWebIdentity response](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html#API_AssumeRoleWithWebIdentity_Errors) 类似。