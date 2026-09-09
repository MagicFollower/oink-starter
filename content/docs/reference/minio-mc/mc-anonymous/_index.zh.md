---
title: "mc anonymous"

weight: 30
icon: fa-solid fa-user-secret
---

<a id="mc-anonymous"></a>

<a id="command-mc.anonymous"></a>

## 说明 {#id2}

[`mc anonymous`](#command-mc.anonymous) 命令支持为存储桶及其内容设置或移除匿名 [policies](/docs/administration/identity-access-management/policy-based-access-control/#minio-policy)。 配置了匿名策略的存储桶允许公开访问，客户端无需进行 [authentication](/docs/administration/identity-access-management/#minio-authentication-and-identity-management) 即可执行策略授予的任意操作。

## 子命令 {#id3}

[`mc anonymous`](#command-mc.anonymous) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-get/#command-mc.anonymous.get"><code>get</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-get/#command-mc.anonymous.get"><code>mc anonymous get</code></a> 命令用于获取存储桶的匿名（即未认证或公共）访问
<a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">策略</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-get-json/#command-mc.anonymous.get-json"><code>get-json</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-get-json/#command-mc.anonymous.get-json"><code>mc anonymous get-json</code></a> 命令用于获取存储桶的匿名（即未经身份验证或公开）访问 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policies</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-links/#command-mc.anonymous.links"><code>links</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-links/#command-mc.anonymous.links"><code>mc anonymous links</code></a> 获取用于匿名（即未认证或公开）访问存储桶的 HTTP URL。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-list/#command-mc.anonymous.list"><code>list</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-list/#command-mc.anonymous.list"><code>mc anonymous list</code></a> 检索存储桶的所有匿名（即未经身份验证或公开）访问策略。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-set/#command-mc.anonymous.set"><code>set</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-set/#command-mc.anonymous.set"><code>mc anonymous set</code></a> 命令为存储桶设置匿名（即未认证或公开）访问
<a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">策略</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-set-json/#command-mc.anonymous.set-json"><code>set-json</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-anonymous-set-json/#command-mc.anonymous.set-json"><code>mc anonymous set-json</code></a> 命令使用 IAM <a href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-policy-language-overview.html">JSON policy document</a>
为存储桶设置匿名（即未认证或公开）访问 <a href="/docs/administration/identity-access-management/policy-based-access-control/#minio-policy">policies</a>。</p></td>
    </tr>
  </tbody>
</table>