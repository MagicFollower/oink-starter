---
title: "软件开发工具包（SDK）"

weight: 190
icon: fa-solid fa-cubes
---

<a id="sdk"></a>
<a id="minio-drivers"></a>

MinIO 提供以下软件开发工具包（SDK）：

- [Go](#go-sdk)
- [Python](#python-sdk)
- [Java](#java-sdk)
- [.NET](#dotnet-sdk)
- [JavaScript](#javascript-sdk)
- [Haskell](#haskell-sdk)
- [C++](#cpp-sdk)
- [Rust](#rust-sdk)

<a id="go-sdk"></a>

## Go {#go}

GitHub: [minio/minio-go](https://github.com/minio/minio-go)

最新版本：GOVERSION

快速入门：[Go 快速入门指南](/docs/developers/go/minio-go/)

参考：[MinIO Go SDK API](https://pkg.go.dev/github.com/minio/minio-go/v7)

通过 GitHub 下载

> ```shell
> go get github.com/minio/minio-go/v7
> ```

<a id="python-sdk"></a>

## Python {#python}

GitHub: [minio/minio-py](https://github.com/minio/minio-py)

最新版本：PYTHONVERSION

快速入门：[Python 快速入门指南](/docs/developers/python/minio-py/)

参考：[MinIO Python SDK](https://github.com/minio/minio-py)

**安装**

> - pip
>
>   ```shell
>   pip3 install minio
>   ```
>
> - 源码
>
>   ```shell
>   git clone https://github.com/minio/minio-py
>   cd minio-py
>   python setup.py install
>   ```

<a id="java-sdk"></a>

## Java {#java}

GitHub: [minio/minio-java](https://github.com/minio/minio-java)

最新版本：JAVAVERSION

快速入门：[Java 快速入门指南](/docs/developers/java/minio-java/#minio-java-quickstart)

参考：[MinIO Java SDK](https://github.com/minio/minio-java)

**安装**

> - Maven
>
>   ```java
>   <dependency>
>       <groupId>io.minio</groupId>
>       <artifactId>minio</artifactId>
>       <version>JAVAVERSION</version>
>   </dependency>
>   ```
>
> - Gradle
>
>   ```java
>   dependencies {
>       implementation("io.minio:minio:JAVAVERSION")
>   }
>   ```
>
> - JAR
>
>   从 Sonatype Maven Central Repository 下载与 SDK 版本 JAVAVERSION 对应的最新 JAR 文件。

<a id="dotnet-sdk"></a>

## .NET {#net}

GitHub: [minio/minio-dotnet](https://github.com/minio/minio-dotnet)

最新版本：DOTNETVERSION

快速入门：[.NET 快速入门指南](/docs/developers/dotnet/minio-dotnet/)

参考：[MinIO .NET SDK](https://github.com/minio/minio-dotnet)

**从 NuGet 下载**

> 在 NuGet Package Manager Console 中运行以下命令。
>
> ```shell
> PM> Install-Package Minio
> ```

<a id="javascript-sdk"></a>

## JavaScript {#javascript}

GitHub: [minio/minio-js](https://github.com/minio/minio-js)

最新版本：JAVASCRIPTVERSION

快速入门：[JavaScript 快速入门指南](/docs/developers/javascript/minio-javascript/)

参考：[MinIO JavaScript SDK](https://github.com/minio/minio-js)

**安装**

> - NPM
>
>   ```shell
>   npm install --save minio
>   ```
>
> - 源码
>
>   ```shell
>   git clone https://github.com/minio/minio-js
>   cd minio-js
>   npm install
>   npm install -g
>   ```

<a id="haskell-sdk"></a>

## Haskell {#haskell}

GitHub: [minio/minio-hs](https://github.com/minio/minio-hs)

最新版本：HASKELLVERSION

快速入门：[Haskell 快速入门指南](/docs/developers/haskell/minio-haskell/)

**安装**

> 将 `minio-hs` 添加到项目 `.cabal` 的 `dependencies` 部分。
>
> 或
>
> 如果你使用 `hpack`，请将 `minio-hs` 添加到 `package.yaml` 文件中。

<a id="cpp-sdk"></a>

## C++ {#c}

GitHub: [minio/minio-cpp](https://github.com/minio/minio-cpp)

参考：[MinIO C++ SDK Reference](https://minio-cpp.min.io/)

**安装**

> - `vcpkg`
>
>   ```shell
>   vcpkg install minio-cpp
>   ```
>
> - 源码
>
>   ```shell
>   git clone https://github.com/minio/minio-cpp
>   cd minio-cpp
>   wget --quiet -O vcpkg-master.zip https://github.com/microsoft/vcpkg/archive/refs/heads/master.zip
>   unzip -qq vcpkg-master.zip
>   ./vcpkg-master/bootstrap-vcpkg.sh
>   ./vcpkg-master/vcpkg integrate install
>   cmake -B ./build -DCMAKE_BUILD_TYPE=Debug -DCMAKE_TOOLCHAIN_FILE=./vcpkg-master/scripts/buildsystems/vcpkg.cmake
>   cmake --build ./build --config Debug
>   ```

<a id="rust-sdk"></a>

## Rust {#rust}

GitHub: [minio/minio-rs](https://github.com/minio/minio-rs)

**最新版本**

> RUSTVERSION

参考：[MinIO Rust SDK Reference](https://docs.rs/minio/latest/minio/)

快速入门：[Rust 快速入门指南](/docs/developers/rust/minio-rust/)