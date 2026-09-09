---
title: "JavaScript 快速入门指南"
description: "使用 MinIO JavaScript SDK 从 Node.js 应用连接 SILO。"

weight: 50
icon: fa-brands fa-js
---

## MinIO JavaScript SDK {#javascript-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Node.js 应用可以直接使用上游 [MinIO JavaScript SDK](https://github.com/minio/minio-js)。请选择受所用软件包版本支持、且仍在维护的 Node.js 版本。

## 安装软件包 {#install}

```shell
npm install minio
```

该软件包已内置 TypeScript 类型声明，不要再安装旧的 `@types/minio` 软件包。

## 配置连接 {#configure}

```shell
export S3_ENDPOINT=127.0.0.1
export S3_PORT=9000
export S3_ACCESS_KEY=silo-admin
export S3_SECRET_KEY=replace-with-a-strong-secret
export S3_USE_SSL=false
```

不要把凭据写进源码仓库。连接启用 TLS 的部署时，请将 `S3_USE_SSL` 设为 `true`，并使用对应的 TLS 服务端口。

## 创建存储桶并上传对象 {#upload}

将下面的内容保存为 `quickstart.mjs`：

```js
import * as Minio from 'minio'

const required = (name) => {
  const value = process.env[name]
  if (!value) throw new Error(`${name} is required`)
  return value
}

const client = new Minio.Client({
  endPoint: required('S3_ENDPOINT'),
  port: Number(process.env.S3_PORT || 9000),
  useSSL: process.env.S3_USE_SSL === 'true',
  accessKey: required('S3_ACCESS_KEY'),
  secretKey: required('S3_SECRET_KEY'),
})

const bucket = 'javascript-quickstart'
const objectName = 'hello.txt'

if (!(await client.bucketExists(bucket))) {
  await client.makeBucket(bucket, 'us-east-1')
}

await client.putObject(
  bucket,
  objectName,
  Buffer.from('hello from SILO\n'),
  { 'Content-Type': 'text/plain' },
)

const stat = await client.statObject(bucket, objectName)
console.log(`Uploaded ${objectName}: ${stat.size} bytes`)
```

运行：

```shell
node quickstart.mjs
```

存储桶策略、通知、对象锁、预签名 URL、分段操作与其他 API 见仓库的 [API 参考](https://github.com/minio/minio-js/blob/master/docs/API.md)和[持续维护的示例目录](https://github.com/minio/minio-js/tree/master/examples)。长期文档应优先链接稳定目录，而不是持续复制单个示例文件名的假设。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 一并固定并验证 SDK 版本、Node.js 运行时、超时行为与重试策略。
- 显式处理数据流、请求错误、未完成的分段上传与进程退出。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。