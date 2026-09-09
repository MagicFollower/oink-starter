---
title: "mc license"

weight: 210
icon: fa-solid fa-certificate
---

<a id="mc-license"></a>

<a id="command-mc.license"></a>

## 说明 {#id2}

[`mc license`](#command-mc.license) 命令用于管理 [MinIO SUBNET](https://min.io/pricing?jmp=docs) 的集群注册。 可使用这些命令注册部署、显示集群当前许可证信息，或更新集群的许可证密钥。

## 子命令 {#id3}

[`mc license`](#command-mc.license) 包含以下子命令：

<table>
  <thead>
    <tr>
      <th><p>子命令</p></th>
      <th><p>说明</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-license-info/#command-mc.license.info"><code>info</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-license-info/#command-mc.license.info"><code>mc license info</code></a> 命令用于显示 MinIO 部署的许可证状态信息。
具体来说，用于确认该部署使用的是 AGPLv3 开源许可证，还是 <a href="https://min.io/product/subnet?ref=docs">MinIO Commercial License</a>。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-license-register/#command-mc.license.register"><code>register</code></a></p></td>
      <td><p><a href="/docs/reference/minio-mc/mc-license-register/#command-mc.license.register"><code>mc license register</code></a> 命令会将你的部署与 <a href="https://min.io/pricing?jmp=docs">MinIO SUBNET</a> 账户关联。</p></td>
    </tr>
    <tr>
      <td><p><a href="/docs/reference/minio-mc/mc-license-update/#command-mc.license.update"><code>update</code></a></p></td>
      <td><p>使用 <a href="/docs/reference/minio-mc/mc-license-update/#command-mc.license.update"><code>mc license update</code></a> 命令为部署替换许可证密钥。</p></td>
    </tr>
  </tbody>
</table>