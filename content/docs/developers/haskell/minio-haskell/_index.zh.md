---
title: "Haskell 快速入门指南"
description: "使用 MinIO Haskell SDK 从 Haskell 应用连接 SILO。"

weight: 60
icon: fa-solid fa-code
---

## MinIO Haskell SDK {#haskell-sdk}

SILO 实现兼容 S3 的服务端契约，因此 Haskell 应用可以直接使用上游 [`minio-hs`](https://github.com/minio/minio-hs) 软件包。

> [!WARNING]
> 上游最新标签版本仍为 2023 年发布的 `1.7.0`，其软件包元数据列出的测试编译器为 GHC 8.10.7。采用前，请针对当前 GHC、resolver、TLS 栈与实际负载验证 `minio-hs`。更新的兼容信息见 [Hackage](https://hackage.haskell.org/package/minio-hs) 与[上游发布记录](https://github.com/minio/minio-hs/releases)。

## 安装软件包 {#install}

将 `minio-hs` 加入 Cabal 软件包的 `build-depends`，或加入 `package.yaml` 的依赖列表。要交互式查看已安装 API，可执行：

```shell
cabal repl
```

然后在 GHCi 中运行 `:browse Network.Minio`。

## 配置连接 {#configure}

1.7.0 提供的 `fromMinioEnv` 会读取以下凭据变量：

```shell
export S3_ENDPOINT=http://127.0.0.1:9000
export MINIO_ACCESS_KEY=silo-admin
export MINIO_SECRET_KEY=replace-with-a-strong-secret
```

`S3_ENDPOINT` 是包含 `http://` 或 `https://` 协议的完整 URL。请把凭据保存在源码仓库之外。

## 创建存储桶并上传对象 {#upload}

将以下内容保存为 `Main.hs`：

```haskell
{-# LANGUAGE OverloadedStrings #-}

import Control.Monad (unless)
import Data.String (fromString)
import Network.Minio
import System.Environment (getEnv)

main :: IO ()
main = do
  endpoint <- getEnv "S3_ENDPOINT"
  connection <-
    setCredsFrom [fromMinioEnv] (fromString endpoint :: ConnectInfo)

  result <- runMinio connection $ do
    let bucket = "haskell-quickstart"
        object = "hello.txt"

    exists <- bucketExists bucket
    unless exists $ makeBucket bucket Nothing
    fPutObject bucket object "hello.txt" defaultPutObjectOptions

  case result of
    Left err -> putStrLn $ "Upload failed: " ++ show err
    Right () -> putStrLn "Uploaded hello.txt"
```

创建 `hello.txt`，然后使用项目选定的构建工具与 resolver 运行程序。仓库的[示例目录](https://github.com/minio/minio-hs/tree/master/examples)与 [API 参考](https://hackage.haskell.org/package/minio-hs/docs/Network-Minio.html)涵盖流处理、预签名 URL、加密、通知、对象锁定等操作。

## 生产检查清单 {#production}

- 启用 TLS 并验证服务端证书，不要关闭证书校验。
- 从密钥管理系统或受保护的环境中加载凭据。
- 只授予应用实际需要的存储桶与对象权限。
- 同时固定并验证 GHC、resolver、SDK、TLS 与 HTTP 依赖版本。
- 定义超时，并显式处理 `MinioErr`、重试、资源清理与未完成的分段上传。

服务端策略配置见[身份与访问管理](/docs/administration/identity-access-management/)。