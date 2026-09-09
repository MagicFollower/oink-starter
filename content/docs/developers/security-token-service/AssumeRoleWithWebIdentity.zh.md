---
title: "AssumeRoleWithWebIdentity"

weight: 30
---

<a id="assumerolewithwebidentity"></a>
<a id="minio-sts-assumerolewithwebidentity"></a>

MinIO Security Token Service (STS) `AssumeRoleWithWebIdentity` API 端点使用由 [已配置的 OpenID Identity Provider (IDP)](/docs/operations/external-iam/configure-openid-external-identity-management/#minio-external-identity-management-openid-configure) 返回的 JSON Web Token (JWT) 生成临时访问凭证。本文档说明 MinIO 服务器的 `AssumeRoleWithWebIdentity` 端点。关于如何使用 S3 兼容 SDK 实现 STS，请参阅对应 SDK 的文档。

MinIO STS `AssumeRoleWithWebIdentity` API 端点参考了 AWS [AssumeRoleWithWebIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html) 端点，并共享部分请求/响应元素。本文档说明 MinIO 特有语法，并链接到 AWS 参考文档以获取 所有共享元素的说明。

## 请求端点 {#id2}

`AssumeRoleWithWebIdentity` 端点格式如下：

```shell
POST https://minio.example.net?Action=AssumeRoleWithWebIdentity[&ARGS]
```

以下示例使用了所有受支持参数。请将 `minio.example.net` 主机名替换为你的 MinIO 集群对应 URL：

```shell
POST https://minio.example.net?Action=AssumeRoleWithWebIdentity
&WebIdentityToken=TOKEN
&Version=2011-06-15
&DurationSeconds=86000
&Policy={}
```

<a id="id3"></a>

### 请求查询参数 {#minio-assumerolewithwebidentity-query-parameters}

该端点支持以下查询参数：

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
      <td><p><code>WebIdentityToken</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必填</em></p><p>指定由
<a href="/docs/operations/external-iam/configure-openid-external-identity-management/#minio-external-identity-management-openid-configure">已配置的 OpenID Identity Provider</a>
返回的 JSON Web Token (JWT)。</p></td>
    </tr>
    <tr>
      <td><p><code>Version</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必填</em></p><p>指定 <code>2011-06-15</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>DurationSeconds</code></p></td>
      <td><p>integer</p></td>
      <td><p><em>可选</em></p><p>指定临时凭证过期前的秒数。
默认为 <code>3600</code>。</p><ul><li><p>最小值为 <code>900</code>，即 15 分钟。</p></li><li><p>最大值为 <code>604800</code>，即 7 天。</p></li></ul><p>如果省略 <code>DurationSeconds</code>，MinIO 在使用默认时长前会先检查 JWT token 中的
<code>exp</code> claim。有关 JSON Web Token 过期时间的更多信息，请参见
<a href="https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4">RFC 7519 4.1.4: Expiration Time Claim</a>。</p></td>
    </tr>
    <tr>
      <td><p><code>Policy</code></p></td>
      <td><p>string</p></td>
      <td><p><em>可选</em></p><p>指定 URL 编码、JSON 格式的 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a>，
作为内联会话策略使用。</p><ul><li><p>最小字符串长度为 <code>1</code>。</p></li><li><p>最大字符串长度为 <code>2048</code>。</p></li></ul><p>临时凭证的最终权限是 <a href="/docs/administration/identity-access-management/oidc-access-management/#minio-external-identity-management-openid-access-control">JWT claim</a>
中指定策略与所给内联策略的交集。应用只能执行那些已被显式授权的操作。</p><p>内联策略可以指定 JWT claim 策略所允许权限的子集。
应用绝不会获得超出 JWT claim 策略所指定范围的权限。</p><p>省略该参数则仅使用 JWT claim 策略。</p><p>有关 MinIO 认证与授权的更多信息，请参见 <a href="/docs/administration/identity-access-management/#minio-access-management">Access Management</a>。</p></td>
    </tr>
    <tr>
      <td><p><code>RoleArn</code></p></td>
      <td><p>string</p></td>
      <td><p><em>可选</em></p><p>用于所有用户认证请求的角色 Amazon Resource Number (ARN)。
如果使用该参数，必须通过 <code>role_policy</code> 配置参数或 <code>MINIO_IDENTITY_OPENID_ROLE_POLICY</code> 环境变量，
为 RoleArn 对应的 provider 定义匹配的 OIDC RolePolicy。</p><p>使用时，所有有效的授权请求都会假定同一组由 RolePolicy 提供的权限。
你可以使用 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy-variables-oidc">OpenID Policy Variables</a> 创建策略，
以编程方式管理每个用户可访问的内容。</p><p>如果未提供 RoleArn，MinIO 会尝试通过基于 JWT 的 claim 进行授权。</p></td>
    </tr>
  </tbody>
</table>

## 响应元素 {#id4}

该 API 端点的 XML 响应与 AWS [AssumeRoleWithWebIdentity response](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html#API_AssumeRoleWithWebIdentity_ResponseElements) 类似。具体而言，MinIO 返回 `AssumeRoleWithWebIdentityResult` 对象， 其中 `AssumedRoleUser.Credentials` 对象包含 MinIO 生成的临时 凭证：

- `AccessKeyId` - 应用用于认证的访问密钥。
- `SecretKeyId` - 应用用于认证的 Secret Key。
- `Expiration` - 凭证过期的 <a id="index-0"></a>[**RFC3339**](https://datatracker.ietf.org/doc/html/rfc3339.html) 日期和时间。
- `SessionToken` - 应用用于认证的会话 token。某些 SDK 在使用临时凭证时可能需要此字段。

以下示例与 MinIO STS `AssumeRoleWithWebIdentity` 端点返回的响应类似：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AssumeRoleWithWebIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
<AssumeRoleWithWebIdentityResult>
   <AssumedRoleUser>
      <Arn/>
      <AssumeRoleId/>
   </AssumedRoleUser>
   <Credentials>
      <AccessKeyId>Y4RJU1RNFGK48LGO9I2S</AccessKeyId>
      <SecretAccessKey>sYLRKS1Z7hSjluf6gEbb9066hnx315wHTiACPAjg</SecretAccessKey>
      <Expiration>2019-08-08T20:26:12Z</Expiration>
      <SessionToken>eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NLZXkiOiJZNFJKVTFSTkZHSzQ4TEdPOUkyUyIsImF1ZCI6IlBvRWdYUDZ1Vk80NUlzRU5SbmdEWGo1QXU1WWEiLCJhenAiOiJQb0VnWFA2dVZPNDVJc0VOUm5nRFhqNUF1NVlhIiwiZXhwIjoxNTQxODExMDcxLCJpYXQiOjE1NDE4MDc0NzEsImlzcyI6Imh0dHBzOi8vbG9jYWxob3N0Ojk0NDMvb2F1dGgyL3Rva2VuIiwianRpIjoiYTBiMjc2MjktZWUxYS00M2JmLTg3MzktZjMzNzRhNGNkYmMwIn0.ewHqKVFTaP-j_kgZrcOEKroNUjk10GEp8bqQjxBbYVovV0nHO985VnRESFbcT6XMDDKHZiWqN2vi_ETX_u3Q-w</SessionToken>
   </Credentials>
</AssumeRoleWithWebIdentityResult>
<ResponseMetadata/>
</AssumeRoleWithWebIdentityResponse>
```

## 错误元素 {#id5}

该 API 端点的 XML 错误响应与 AWS [AssumeRoleWithWebIdentity response](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html#API_AssumeRoleWithWebIdentity_Errors) 类似。