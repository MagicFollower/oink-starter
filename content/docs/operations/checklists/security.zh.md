---
title: "安全检查清单"

weight: 20
---

<a id="minio-security-checklist"></a>
<a id="id1"></a>

在为生产级分布式 MinIO 部署规划安全配置时，请使用以下检查清单。

## 必做步骤 {#id3}

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>在 MinIO 或所选的第三方身份提供商（LDAP/Active Directory 或 OpenID）中定义组策略</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>在 MinIO 或所选的第三方身份提供商上定义单个访问策略</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>（仅 Kubernetes 部署）将租户配置为使用所选的第三方身份提供商</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>在防火墙中放行到 MinIO 服务端 S3 API 监听端口的 TCP 流量（默认：<code>9000</code>）。</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>在防火墙中放行到 <a href="/docs/administration/minio-console/#minio-console-port-assignment">MinIO Server Console 监听端口</a> 的 TCP 流量（推荐默认值：<code>9090</code>）。</p></td>
    </tr>
  </tbody>
</table>

## [静态数据加密](/docs/administration/server-side-encryption/#minio-sse) {#id4}

MinIO 通过 Key Encryption Service (KES) 支持以下外部 KMS 提供方：

- [HashiCorp Vault Root KMS](/docs/operations/server-side-encryption/configure-minio-kes/#minio-sse-vault)
- [AWS Root KMS](/docs/operations/server-side-encryption/configure-minio-kes/#minio-sse-aws)
- [Google Cloud Platform Secret Manager Root KMS](/docs/operations/server-side-encryption/configure-minio-kes/#minio-sse-gcp)
- [Azure Key Vault Root KMS](/docs/operations/server-side-encryption/configure-minio-kes/#minio-sse-azure)

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>下载并安装 MinIO Key Encryption Service (KES)</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>启用 TLS</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>为 KES 生成私钥和公钥</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>为 MinIO 生成私钥和公钥</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>创建 KES 配置文件并启动服务</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>为密钥管理服务（KMS）生成外部密钥</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>将 MinIO 连接到 KES</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>启用服务端加密</p></td>
    </tr>
  </tbody>
</table>

## [传输中加密（”In flight”）](/docs/operations/network-encryption/#minio-tls) {#in-flight}

<table>
  <tbody>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p><a href="/docs/operations/network-encryption/#minio-tls">启用 TLS</a></p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>为每个访问 MinIO 的内部和外部域名分别添加证书和密钥</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>使用 TLS 1.3 或 TLS 1.2 支持的 cipher 生成 TLS 私钥和公钥</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>配置受信任的 Certificate Authority (CA) 存储</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>暴露 Kubernetes Service，例如使用 NGINX</p></td>
    </tr>
    <tr>
      <td><p><svg version="1.1" width="1.0em" height="1.0em" class="sd-octicon sd-octicon-circle" viewBox="0 0 16 16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8z"></path></svg></p></td>
      <td><p>（可选）验证证书，例如使用 <a href="https://www.sslchecker.com/certdecoder">https://www.sslchecker.com/certdecoder</a></p></td>
    </tr>
  </tbody>
</table>