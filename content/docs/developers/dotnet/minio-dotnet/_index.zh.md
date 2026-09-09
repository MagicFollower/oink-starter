---
title: ".NET 快速入门指南"
description: "使用 MinIO .NET SDK 从 .NET 应用连接 SILO。"

weight: 30
icon: fa-brands fa-microsoft
---

## MinIO .NET SDK {#dotnet-sdk}

SILO 实现兼容 S3 的服务端契约，因此应用可以直接使用上游 [MinIO .NET SDK](https://github.com/minio/minio-dotnet)，无需 SILO 专用客户端分支。本指南使用稳定的 NuGet 软件包，并通过环境变量传入凭据。

> [!NOTE]
> SDK 的运行时要求与 API 会独立于 SILO 演进。为应用选择版本前，请核对[当前 NuGet 软件包](https://www.nuget.org/packages/Minio/)与 [SDK 发布记录](https://github.com/minio/minio-dotnet/releases)。

## 安装软件包 {#install}

在现有 .NET 项目中添加 `Minio` 软件包：

```shell
dotnet add package Minio
```

## 配置连接 {#configure}

设置 SILO 部署的端点与凭据，不要把密钥写进源码仓库。

```shell
export S3_ENDPOINT=127.0.0.1:9000
export S3_ACCESS_KEY=silo-admin
export S3_SECRET_KEY=replace-with-a-strong-secret
export S3_USE_SSL=false
```

`S3_ENDPOINT` 只填写主机名和可选端口，不带 `http://` 或 `https://` 前缀。端点启用 TLS 时，将 `S3_USE_SSL` 设为 `true`。

## 创建存储桶并上传对象 {#upload}

```csharp
using Minio;
using Minio.DataModel.Args;

var endpoint = Environment.GetEnvironmentVariable("S3_ENDPOINT")
    ?? throw new InvalidOperationException("S3_ENDPOINT is required");
var accessKey = Environment.GetEnvironmentVariable("S3_ACCESS_KEY")
    ?? throw new InvalidOperationException("S3_ACCESS_KEY is required");
var secretKey = Environment.GetEnvironmentVariable("S3_SECRET_KEY")
    ?? throw new InvalidOperationException("S3_SECRET_KEY is required");
var useSsl = bool.TryParse(Environment.GetEnvironmentVariable("S3_USE_SSL"), out var ssl)
    && ssl;

var client = new MinioClient()
    .WithEndpoint(endpoint)
    .WithCredentials(accessKey, secretKey)
    .WithSSL(useSsl)
    .Build();

const string bucket = "dotnet-quickstart";
const string objectName = "hello.txt";
const string filePath = "hello.txt";

var exists = await client.BucketExistsAsync(
    new BucketExistsArgs().WithBucket(bucket));

if (!exists)
{
    await client.MakeBucketAsync(
        new MakeBucketArgs().WithBucket(bucket));
}

await client.PutObjectAsync(
    new PutObjectArgs()
        .WithBucket(bucket)
        .WithObject(objectName)
        .WithFileName(filePath)
        .WithContentType("text/plain"));

Console.WriteLine($"Uploaded {objectName} to {bucket}");
```

创建 `hello.txt`，然后运行项目：

```shell
dotnet run
```

ASP.NET Core 依赖注入与更多操作见 SDK 的[当前 README](https://github.com/minio/minio-dotnet#readme)。维护分支还提供[简单控制台示例](https://github.com/minio/minio-dotnet/tree/master/Minio.Examples.Simple)和[基于 Host 的示例](https://github.com/minio/minio-dotnet/tree/master/Minio.Examples.Host)；把代码复制到固定版本的应用前，请先核对示例所在分支与软件包版本。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书。
- 从密钥管理系统或受保护的环境中加载凭据，不要写入源码。
- 只授予应用实际需要的存储桶与对象权限。
- 把 SDK 版本固定与验证纳入应用自身的依赖生命周期。
- 显式处理 SDK 异常、请求取消、重试与分段上传清理。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。