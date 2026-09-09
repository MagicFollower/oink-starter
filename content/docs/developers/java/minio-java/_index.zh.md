---
title: "Java 快速入门指南"
description: "使用 MinIO Java SDK 从 Java 应用连接 SILO。"

weight: 40
icon: fa-brands fa-java
---

## MinIO Java SDK {#java-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Java 应用可以直接使用上游 [MinIO Java SDK](https://github.com/minio/minio-java)。SDK 支持 Java 8 及更高版本；请同时考虑应用框架对运行时的支持范围。

> [!NOTE]
> 本页按 SDK `9.0.3` 校验。固定依赖前，请核对[当前发布记录](https://github.com/minio/minio-java/releases)与 [Maven Central 元数据](https://central.sonatype.com/artifact/io.minio/minio)。

## 安装软件包 {#install}

在 Maven 中添加依赖：

```xml
<dependency>
  <groupId>io.minio</groupId>
  <artifactId>minio</artifactId>
  <version>9.0.3</version>
</dependency>
```

或在 Gradle 中添加：

```kotlin
implementation("io.minio:minio:9.0.3")
```

## 配置连接 {#configure}

```shell
export S3_ENDPOINT=http://127.0.0.1:9000
export S3_ACCESS_KEY=silo-admin
export S3_SECRET_KEY=replace-with-a-strong-secret
```

与部分 MinIO SDK 不同，Java 构造器接受完整的端点 URL，需要包含 `http://` 或 `https://` 协议。请把凭据保存在源码仓库之外。

## 创建存储桶并上传对象 {#upload}

```java
import io.minio.BucketExistsArgs;
import io.minio.MakeBucketArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;

public final class Quickstart {
  private static String required(String name) {
    String value = System.getenv(name);
    if (value == null || value.isBlank()) {
      throw new IllegalStateException(name + " is required");
    }
    return value;
  }

  public static void main(String[] args) throws Exception {
    MinioClient client =
        MinioClient.builder()
            .endpoint(required("S3_ENDPOINT"))
            .credentials(required("S3_ACCESS_KEY"), required("S3_SECRET_KEY"))
            .build();

    String bucket = "java-quickstart";
    String object = "hello.txt";
    byte[] payload = "hello from SILO\n".getBytes(StandardCharsets.UTF_8);

    boolean exists =
        client.bucketExists(BucketExistsArgs.builder().bucket(bucket).build());
    if (!exists) {
      client.makeBucket(MakeBucketArgs.builder().bucket(bucket).build());
    }

    try (ByteArrayInputStream stream = new ByteArrayInputStream(payload)) {
      client.putObject(
          PutObjectArgs.builder()
              .bucket(bucket)
              .object(object)
              .stream(stream, payload.length, -1)
              .contentType("text/plain")
              .build());
    }

    System.out.printf("Uploaded %s: %d bytes%n", object, payload.length);
  }
}
```

预签名 URL、加密、通知、对象锁定、分段上传等操作见 SDK 的 [Javadoc](https://javadoc.io/doc/io.minio/minio/latest/index.html)与[维护中示例](https://github.com/minio/minio-java/tree/master/examples)。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书与信任库。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 同时固定并验证 JDK、SDK、HTTP 客户端与应用框架版本。
- 配置超时，并显式处理 SDK 异常、重试、流资源与未完成的分段上传。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。