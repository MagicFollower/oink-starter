---
title: "Rust 快速入门指南"
description: "使用 MinIO Rust SDK 从 Rust 应用连接 SILO。"

aliases:
  - "/developers/rust/quickstart/"
  - "/developers/rust/API/"
weight: 70
icon: fa-brands fa-rust
---

## MinIO Rust SDK {#rust-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Rust 应用可以直接使用上游 [MinIO Rust SDK](https://github.com/minio/minio-rs)。该 crate 提供异步、强类型的请求构建器 API。

> [!NOTE]
> 本页按 `minio` crate `0.4.0` 校验。该 crate 目前没有声明最低支持的 Rust 版本，请核对[当前软件包元数据](https://crates.io/crates/minio)与 [API 文档](https://docs.rs/minio/latest/minio/)，并用项目固定的工具链完成验证。

## 安装软件包 {#install}

在 `Cargo.toml` 中加入 SDK 与 Tokio 运行时：

```toml
[dependencies]
minio = "0.4.0"
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

## 配置连接 {#configure}

```shell
export S3_ENDPOINT=http://127.0.0.1:9000
export S3_ACCESS_KEY=silo-admin
export S3_SECRET_KEY=replace-with-a-strong-secret
```

`S3_ENDPOINT` 是包含 `http://` 或 `https://` 协议的完整 URL。请把凭据保存在源码仓库之外。

## 创建存储桶并上传对象 {#upload}

```rust
use minio::s3::builders::ObjectContent;
use minio::s3::creds::StaticProvider;
use minio::s3::http::BaseUrl;
use minio::s3::response::BucketExistsResponse;
use minio::s3::types::{BucketName, ObjectKey, S3Api};
use minio::s3::{MinioClient, MinioClientBuilder};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let endpoint = env::var("S3_ENDPOINT")?;
    let access_key = env::var("S3_ACCESS_KEY")?;
    let secret_key = env::var("S3_SECRET_KEY")?;

    let base_url = endpoint.parse::<BaseUrl>()?;
    let provider = StaticProvider::new(&access_key, &secret_key, None);
    let client: MinioClient = MinioClientBuilder::new(base_url)
        .provider(Some(provider))
        .build()?;

    let bucket = BucketName::new("rust-quickstart")?;
    let object = ObjectKey::new("hello.txt")?;

    let exists: BucketExistsResponse = client
        .bucket_exists(bucket.clone())?
        .build()
        .send()
        .await?;

    if !exists.exists() {
        client
            .create_bucket(bucket.clone())?
            .build()
            .send()
            .await?;
    }

    client
        .put_object_content(
            bucket,
            object,
            ObjectContent::from("hello from SILO\n"),
        )?
        .build()
        .send()
        .await?;

    println!("Uploaded hello.txt");
    Ok(())
}
```

使用 `cargo run` 运行示例。仓库的[维护中示例](https://github.com/minio/minio-rs/tree/master/examples)与 [API 文档](https://docs.rs/minio/latest/minio/)涵盖文件上传、流处理、加密、通知、对象锁定等操作。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 同时固定并验证 Rust 工具链、SDK、Tokio、HTTP、TLS 与密码学特性。
- 定义超时，并显式处理错误、重试、任务取消与未完成的分段上传。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。