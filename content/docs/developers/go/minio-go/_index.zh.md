---
title: "Go 快速入门指南"
description: "使用 MinIO Go SDK 从 Go 应用连接 SILO。"

weight: 10
icon: fa-brands fa-golang
---

## MinIO Go SDK {#go-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Go 应用可以直接使用上游 [MinIO Go SDK](https://github.com/minio/minio-go)。当前主版本的模块路径为 `github.com/minio/minio-go/v7`。

> [!NOTE]
> SDK 版本与 Go 版本要求会独立于 SILO 演进。固定依赖前，请核对[当前发布记录](https://github.com/minio/minio-go/releases)与[软件包文档](https://pkg.go.dev/github.com/minio/minio-go/v7)。

## 安装模块 {#install}

在现有 Go 模块中执行：

```shell
go get github.com/minio/minio-go/v7
```

## 配置连接 {#configure}

```shell
export S3_ENDPOINT=127.0.0.1:9000
export S3_ACCESS_KEY=silo-admin
export S3_SECRET_KEY=replace-with-a-strong-secret
export S3_USE_SSL=false
```

`S3_ENDPOINT` 只填写主机名和可选端口，不带 `http://` 或 `https://` 前缀。请把凭据保存在源码仓库之外；端点启用 TLS 时，将 `S3_USE_SSL` 设为 `true`。

## 创建存储桶并上传对象 {#upload}

将以下内容保存为 `main.go`：

```go
package main

import (
	"bytes"
	"context"
	"fmt"
	"log"
	"os"

	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

func required(name string) string {
	value := os.Getenv(name)
	if value == "" {
		log.Fatalf("%s is required", name)
	}
	return value
}

func main() {
	ctx := context.Background()
	client, err := minio.New(required("S3_ENDPOINT"), &minio.Options{
		Creds: credentials.NewStaticV4(
			required("S3_ACCESS_KEY"),
			required("S3_SECRET_KEY"),
			"",
		),
		Secure: os.Getenv("S3_USE_SSL") == "true",
	})
	if err != nil {
		log.Fatal(err)
	}

	const bucket = "go-quickstart"
	const object = "hello.txt"

	exists, err := client.BucketExists(ctx, bucket)
	if err != nil {
		log.Fatal(err)
	}
	if !exists {
		if err = client.MakeBucket(ctx, bucket, minio.MakeBucketOptions{
			Region: "us-east-1",
		}); err != nil {
			log.Fatal(err)
		}
	}

	payload := []byte("hello from SILO\n")
	info, err := client.PutObject(
		ctx,
		bucket,
		object,
		bytes.NewReader(payload),
		int64(len(payload)),
		minio.PutObjectOptions{ContentType: "text/plain"},
	)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Uploaded %s: %d bytes\n", info.Key, info.Size)
}
```

运行示例：

```shell
go run .
```

预签名 URL、对象锁定、加密、通知、分段上传等操作见 SDK 的 [API 文档](https://pkg.go.dev/github.com/minio/minio-go/v7)与[维护中示例](https://github.com/minio/minio-go/tree/master/examples)。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 同时固定并验证 SDK 与 Go 版本。
- 为请求设置截止时间，并显式处理重试、取消与未完成的分段上传。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。