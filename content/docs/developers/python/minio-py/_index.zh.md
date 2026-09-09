---
title: "Python 快速入门指南"
description: "使用 MinIO Python SDK 从 Python 应用连接 SILO。"

weight: 20
icon: fa-brands fa-python
---

## MinIO Python SDK {#python-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Python 应用可以直接使用上游 [MinIO Python SDK](https://github.com/minio/minio-py)。

> [!NOTE]
> 支持的 Python 版本与 SDK API 会独立于 SILO 演进。固定依赖前，请核对[当前软件包元数据](https://pypi.org/project/minio/)与 [SDK 发布记录](https://github.com/minio/minio-py/releases)。

## 安装软件包 {#install}

在虚拟环境中安装 `minio`：

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install minio
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

将以下内容保存为 `quickstart.py`：

```python
import io
import os

from minio import Minio


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


client = Minio(
    required("S3_ENDPOINT"),
    access_key=required("S3_ACCESS_KEY"),
    secret_key=required("S3_SECRET_KEY"),
    secure=os.environ.get("S3_USE_SSL", "false").lower() == "true",
)

bucket = "python-quickstart"
object_name = "hello.txt"
payload = b"hello from SILO\n"

if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

client.put_object(
    bucket,
    object_name,
    io.BytesIO(payload),
    length=len(payload),
    content_type="text/plain",
)

stat = client.stat_object(bucket, object_name)
print(f"Uploaded {object_name}: {stat.size} bytes")
```

运行示例：

```shell
python quickstart.py
```

预签名 URL、服务端加密、通知、对象锁定、分段上传等操作见仓库的 [API 参考](https://github.com/minio/minio-py/blob/master/docs/API.md)与[维护中示例](https://github.com/minio/minio-py/tree/master/examples)。

## 生产检查清单 {#production}

- 启用 TLS，并验证服务端证书。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 同时固定并验证 Python 运行时、SDK 与 HTTP 依赖。
- 定义超时，并显式处理 SDK 异常、重试、流资源与未完成的分段上传。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。