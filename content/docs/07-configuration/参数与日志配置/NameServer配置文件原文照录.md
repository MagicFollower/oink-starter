---
title: RocketMQ 4.9.8 NameServer 配置文件模板（原文照录）
description: 用户提供的 4.9.8 namesrv.properties 模板与 Linux/Windows 启动命令、`-p` 验证方法逐字节照录；模板内四处键名与默认值说法经本机 4.9.8 的 `-p` 回显与配置类字段清单判定为无效或有误，而它写的 kvConfigPath 反而比站内照抄上游的 kvConfigpath 更正确。
weight: 4
---

> [!IMPORTANT] 原文照录声明：正文一字未改，以下判定全部来自本机 4.9.8 发行包
>
> 判据是发行包自带的两条命令：`java -cp "lib/*" org.apache.rocketmq.namesrv.NamesrvStartup -p` 打印 NameServer 的全部有效配置键与默认值（打印后直接退出，不启服务），`javap -p` 打印配置类的字段清单。
>
> | 模板原文 | 4.9.8 实测判定 | 判据 |
> |---|---|---|
> | `# serverSocketChannelMaxIdleTimeSeconds=` | 无此键。有效键名是 `serverChannelMaxIdleTimeSeconds`，默认 120 | `-p` 回显 + `NettyServerConfig` 字段清单 |
> | `# bindAddress=0.0.0.0`（称默认 0.0.0.0） | 4.9.8 的 `NettyServerConfig` 没有 `bindAddress` 字段，写进配置文件不会生效 | `javap -p` 字段清单无该字段 |
> | 「serverWorkerThreads 默认与 CPU 核数相关（如核数 + 1）」 | 实测默认固定为 8；同组另两项是 `serverCallbackExecutorThreads=0`、`serverSelectorThreads=3` | `-p` 回显 |
> | `# namesrvAddr=`（列在 NamesrvConfig 名下） | `NamesrvConfig` 无 `namesrvAddr` 字段，它是 Broker/客户端侧参数；NameServer 侧另有 `productEnvName=center` 与 `configBlackList` 两项，模板未列 | `javap -p` 字段清单 + `-p` 回显 |
>
> **一处反过来**：模板写 `kvConfigPath`（大写 P）与实测字段名一致；站内《客户端与服务端参数配置》照抄 4.x 上游参数表的 `kvConfigpath`（小写 p）反而不被识别。该键以本实测为准。
>
> 模板里 `listenPort=9876`、`rocketmqHome`、`clusterTest=false`、`orderMessageEnable=false`、`productEnvName` 各项与实测一致；末节「用 `-p` 查看实际生效的配置项」这条验证方法本身成立——本机实跑的是发行包内等价的 `java -cp "lib/*" org.apache.rocketmq.namesrv.NamesrvStartup -p`，RC=0 并回显上表全部键值；`bin/mqnamesrv` 只是拼这条 java 命令的包装脚本，本轮未单独重跑它。
>
> NameServer 与 Broker 参数分属不同配置类，逐行默认值见 [客户端与服务端参数配置](/docs/07-configuration/参数与日志配置/客户端与服务端参数配置/)。

以下是适用于 RocketMQ 4.9.8 的 NameServer 完整配置文件模板，以及 Linux 和 Windows 下指定该配置文件的启动命令。

### 📄 NameServer 配置文件模板 (`conf/namesrv.properties`)

RocketMQ 4.x 发行包中默认没有自带完整的 `namesrv.properties` 模板。下面这份配置基于官方文档中 `NamesrvConfig` 与 `NettyServerConfig` 的核心参数整理，包含了常用配置项及默认值注释，可直接保存使用。

```properties
# ============================================================
# RocketMQ 4.9.8 NameServer 配置文件
# 官方参数参考: Server Configuration - NameServer configuration
# ============================================================

# ---------- NamesrvConfig: 核心配置 ----------

# RocketMQ 主目录。默认从环境变量 ROCKETMQ_HOME 或系统属性 rocketmq.home.dir 读取
# rocketmqHome=/opt/rocketmq

# NameServer 自身的地址（通常用于 Broker/客户端，NameServer 启动时一般无需配置此项）
# namesrvAddr=

# KV 配置文件的存储路径，用于持久化顺序消息主题等配置信息
# 默认值: ${user.home}/namesrv/kvConfig.json
# kvConfigPath=/data/rocketmq/namesrv/kvConfig.json

# NameServer 配置文件路径（即本文件路径）。建议通过启动命令的 -c 参数指定，无需在此重复配置
# 默认值: ${user.home}/namesrv/namesrv.properties
# configStorePath=

# 产品环境名称标识，可用于区分开发、测试、生产等不同环境
# 默认值: "center"
# productEnvName=center

# 是否启用集群测试模式。生产环境务必保持 false
# 默认值: false
# clusterTest=false

# 是否支持顺序消息。NameServer 层面通常无需开启
# 默认值: false
# orderMessageEnable=false


# ---------- NettyServerConfig: 网络与线程配置 (常用项) ----------

# NameServer 监听端口，默认为 9876
listenPort=9876

# 绑定的监听地址。默认 0.0.0.0 表示监听所有网卡。
# 生产环境建议绑定内网 IP，例如 192.168.1.100，以限制外部直接访问
# 默认值: 0.0.0.0
# bindAddress=0.0.0.0

# Netty 业务工作线程池大小。默认值通常与 CPU 核数相关（如 CPU 核数 + 1），高并发场景可适当调大
# serverWorkerThreads=

# Netty 回调任务线程池大小
# serverCallbackExecutorThreads=

# Netty Selector 线程数
# serverSelectorThreads=

# 网络连接最大空闲时间（秒）。链接空闲超过此值将被服务端关闭
# serverSocketChannelMaxIdleTimeSeconds=
```

> **说明**：对于大多数部署场景，通常只需要关注 `listenPort`、`bindAddress` 以及可能的线程池参数。完整的可配置项列表（包括 `NettyServerConfig` 的全部网络参数）可参考官方 **Server Configuration** 页面中 “Network configuration properties” 章节。

---

### 🚀 指定配置文件的启动命令

启动 NameServer 时，通过 **`-c`** 参数指定上述配置文件。

#### 🐧 Linux

```bash
cd $ROCKETMQ_HOME

# 前台启动（便于观察启动日志，关闭终端后进程终止）
sh bin/mqnamesrv -c conf/namesrv.properties

# 后台启动（生产环境推荐）
nohup sh bin/mqnamesrv -c conf/namesrv.properties > namesrv_startup.log 2>&1 &
```

#### 🪟 Windows

在 `cmd` 中先进入 `bin` 目录：

```cmd
cd /d %ROCKETMQ_HOME%\bin

start mqnamesrv.cmd -c ../conf/namesrv.properties
```

`start` 会打开一个新的命令行窗口来运行 NameServer，**该窗口不能关闭**，否则 NameServer 会随之终止。

---

### 🔍 验证配置是否生效

启动后，可通过以下命令查看实际加载的配置项，确认文件中的参数（如 `listenPort`）已成功覆盖默认值：

```bash
# Linux
sh bin/mqnamesrv -p -c conf/namesrv.properties

# Windows
mqnamesrv.cmd -p -c ../conf/namesrv.properties
```
命令输出中会列出所有生效的 NameServer 配置项及其当前值。