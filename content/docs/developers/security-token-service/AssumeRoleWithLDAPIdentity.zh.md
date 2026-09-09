---
title: "AssumeRoleWithLDAPIdentity"

weight: 20
---

<a id="assumerolewithldapidentity"></a>
<a id="minio-sts-assumerolewithldapidentity"></a>

MinIO Security Token Service (STS) `AssumeRoleWithLDAPIdentity` API 端点使用 Active Directory 或 LDAP 用户凭据生成临时访问凭据。本文档介绍 MinIO 服务端 `AssumeRoleWithLDAPIdentity` 端点。有关如何使用兼容 S3 的 SDK 实现 STS，请参考对应 SDK 的文档。

MinIO STS `AssumeRoleWithLDAPIdentity` API 端点以 AWS [AssumeRoleWithWebIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html) 端点为模型，并共享部分请求/响应元素。本文档介绍 MinIO 特有的语法，并为 所有共享元素提供指向 AWS 参考文档的链接。

## 请求端点 {#id2}

`AssumeRoleWithLDAPIdentity` 端点格式如下：

```shell
POST https://minio.example.net?Action=AssumeRoleWithLDAPIdentity[&ARGS]
```

以下示例使用了所有受支持参数。请将 `minio.example.net` 主机名替换为你的 MinIO 集群对应的 URL：

```shell
POST https://minio.example.net?Action=AssumeRoleWithLDAPIdentity
&LDAPUsername=USERNAME
&LDAPPassword=PASSWORD
&Version=2011-06-15
&Policy={}
```

### 请求查询参数 {#id3}

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
      <td><p><code>LDAPUsername</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必需</em></p><p>指定要进行认证的 AD/LDAP 用户名。</p></td>
    </tr>
    <tr>
      <td><p><code>LDAPPassword</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必需</em></p><p>指定 <code>LDAPUsername</code> 对应的密码。</p></td>
    </tr>
    <tr>
      <td><p><code>Version</code></p></td>
      <td><p>string</p></td>
      <td><p><em>必需</em></p><p>指定 <code>2011-06-15</code>。</p></td>
    </tr>
    <tr>
      <td><p><code>DurationSeconds</code></p></td>
      <td><p>integer</p></td>
      <td><p><em>可选</em></p><p>指定临时凭据在多少秒后过期。默认值为 <code>3600</code>。</p><ul><li><p>最小值为 <code>900</code>（15 分钟）。</p></li><li><p>最大值为 <code>604800</code>（7 天）。</p></li></ul><p>如果省略 <code>DurationSeconds</code>，MinIO 在使用默认时长前会先检查 JWT token
中是否包含 <code>exp</code> claim。有关 JSON web token 过期时间的更多信息，请参见
<a href="https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4">RFC 7519 4.1.4: Expiration Time Claim</a>。</p></td>
    </tr>
    <tr>
      <td><p><code>Policy</code></p></td>
      <td><p>string</p></td>
      <td><p><em>可选</em></p><p>指定 URL 编码的 JSON 格式 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policy</a>，作为内联会话策略使用。</p><ul><li><p>最小字符串长度为 <code>1</code>。</p></li><li><p>最大字符串长度为 <code>2048</code>。</p></li></ul><p>临时凭据的最终权限是以下两者的交集：与 <code>LDAPUsername</code> 的 Distinguished
Name (DN) 匹配的 <a href="/docs/operations/external-iam/#minio-external-identity-management-ad-ldap-access-control">policy</a>，以及指定的内联策略。
应用只能执行其被明确授权的操作。</p><p>内联策略可以指定 DN 策略允许权限的子集。应用可获取的权限绝不会超过 DN
策略中定义的权限。</p><p>省略该参数则仅使用 DN 策略。</p><p>有关 MinIO 认证与授权的更多信息，请参见 <a href="/docs/administration/identity-access-management/#minio-access-management">Access Management</a>。</p></td>
    </tr>
  </tbody>
</table>

## 响应元素 {#id8}

此 API 端点的 XML 响应与 AWS 的 [AssumeRoleWithLDAPIdentity response](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithLDAPIdentity.html#API_AssumeRoleWithLDAPIdentity_ResponseElements). 类似。具体而言，MinIO 返回 `AssumeRoleWithLDAPIdentityResult` 对象，其中 `AssumedRoleUser.Credentials` 对象包含 MinIO 生成的临时凭据：

- `AccessKeyId` - 应用用于认证的访问密钥。
- `SecretKeyId` - 应用用于认证的密钥。
- `Expiration` - 凭据过期时间，采用 <a id="index-0"></a>[**RFC3339**](https://datatracker.ietf.org/doc/html/rfc3339.html) 日期时间格式。
- `SessionToken` - 应用用于认证的会话令牌。某些 SDK 在使用临时凭据时可能需要此字段。

以下示例与 MinIO STS `AssumeRoleWithLDAPIdentity` 端点返回的响应类似：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<AssumeRoleWithLDAPIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
<AssumeRoleWithLDAPIdentityResult>
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
</AssumeRoleWithLDAPIdentityResult>
<ResponseMetadata/>
</AssumeRoleWithLDAPIdentityResponse>
```

## 错误元素 {#id9}

此 API 端点的 XML 错误响应与 AWS 的 [AssumeRoleWithLDAPIdentity response](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithLDAPIdentity.html#API_AssumeRoleWithLDAPIdentity_Errors).