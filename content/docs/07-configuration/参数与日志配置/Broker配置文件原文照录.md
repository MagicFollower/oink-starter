---
title: RocketMQ 4.x broker.conf 配置模板（原文照录）
description: 用户提供的 4.x broker.conf 完整模板逐字节照录，集群身份、网络注册、角色与刷盘、存储路径、行为开关、磁盘清理与线程池七组参数及中文注释全部原样；模板里两处键名与三处默认值说法已被本机 4.9.8 运行态实测更正，逐键解读见《Broker 配置文件逐项详解》。
weight: 3
---

> [!IMPORTANT] 原文照录声明：正文一字未改，以下四处已被本机 4.9.8 实测更正
>
> | 模板原文 | 4.9.8 实测更正 | 判据 |
> |---|---|---|
> | `mapedFileSizeCommitLog=1073741824` | 键名拼错，正确键名是 `mappedFileSizeCommitLog`（两个 p）。照模板写会被服务端当成不认识的键静默忽略，等于没配 | `getBrokerConfig` 回显里有 `mappedFileSizeCommitLog`，且搜不到任何 `maped` 开头的键 |
> | 「ConsumeQueue 单个文件存储的条目数，默认 30 万条」 | 实测 `mappedFileSizeConsumeQueue = 6000000`（600 万条一个文件），键名同样要带 `pp`。按 30 万条做的容量规划要整体重算 | 实测回显 |
> | 「磁盘最大使用空间比率，默认 90% 左右」 | 本机实测默认 75。按 90 设告警阈值，等于磁盘写到 75% 时 Broker 已开始拒绝写入而监控还在绿 | 实测回显 |
> | `fileReservedTime=48`「默认 48 小时」 | 48 是发行包示例配置里的显式值而非默认值；本机运行默认 72。上游 4.x 参数表自身也不自洽（描述栏写 72、默认值栏印 120），本站并列记录、不做裁决 | 实测 + `docs/06-parameterConfiguration/02server.md` |
>
> 另有一处是「注释值不等于默认值」而非笔误：模板把 `sendMessageThreadPoolNums` 与 `pullMessageThreadPoolNums` 的注释都写成 128，本机实测分别是 4 和 64，且两者不对称——未显式配置时由运行时按机器情况决定，不能拿注释当默认值用。
>
> 逐键的官方口径、本机实测值与生产是否建议显式写出，见 [Broker 配置文件逐项详解](/docs/07-configuration/参数与日志配置/broker配置文件逐项详解/)。

以下是一份适用于 RocketMQ 4.x 的完整 `broker.conf` 配置模板，包含了核心参数、常用调优项及中文注释，并附上了 Linux 和 Windows 下的启动命令。

---

### 📄 Broker 配置文件模板 (`conf/broker.conf`)

你可以将以下内容保存为 `conf/broker.conf`。这份模板整合了**集群身份、网络、存储、高可用角色**等核心配置，是搭建单机或主从集群的基础蓝图。

```properties
# ===================================================================
# RocketMQ 4.x Broker 核心配置文件 (broker.conf)
# 官方参数参考: https://rocketmq.apache.org/docs/4.x/parameterConfiguration/02server/
# ===================================================================

# ------------------- 集群与身份标识 -------------------
# 所属集群名称。同一集群内的所有Broker节点需保持一致
brokerClusterName=DefaultCluster

# Broker名称。同名者互为主从关系（如Master为broker-a，其Slave也为broker-a）
brokerName=broker-a

# Broker ID。0 表示 Master，大于 0 表示 Slave（Slave ID 必须唯一）
brokerId=0

# ------------------- 网络与注册 -------------------
# NameServer 地址，Broker 启动后会向此地址注册路由信息。
# 集群模式下用分号(;)分隔多个地址，例如: 192.168.1.1:9876;192.168.1.2:9876
namesrvAddr=127.0.0.1:9876

# Broker 对外服务的监听端口，默认 10911
listenPort=10911

# (可选) 手动指定 Broker 对外暴露的 IP。
# 在多网卡或容器化环境中，若自动探测的IP有误，可在此强制指定
# brokerIP1=192.168.1.100

# ------------------- 角色与持久化策略 (高可用核心) -------------------
# Broker 角色：
#   ASYNC_MASTER: 异步复制主 (高性能，Master写入成功后即返回，异步同步至Slave)
#   SYNC_MASTER : 同步复制主 (高可靠，Master和Slave均写入成功后才返回)
#   SLAVE       : 从节点
brokerRole=ASYNC_MASTER

# 刷盘方式：
#   ASYNC_FLUSH: 异步刷盘 (高性能，消息写入PageCache后即返回成功)
#   SYNC_FLUSH : 同步刷盘 (高可靠，消息必须落盘至磁盘后才返回成功)
# 线上推荐组合：同步复制 + 异步刷盘 (兼顾可靠性与吞吐)
flushDiskType=ASYNC_FLUSH

# ------------------- 存储路径 -------------------
# Broker 存储根目录。强烈建议修改至独立的、容量较大的数据盘
storePathRootDir=/data/rocketmq/store/broker-a

# (默认) CommitLog 存储路径，存放所有消息的物理文件
# storePathCommitLog=${storePathRootDir}/commitlog

# (默认) ConsumeQueue 存储路径，消息的消费队列索引
# storePathConsumeQueue=${storePathRootDir}/consumequeue

# (默认) IndexFile 存储路径，消息的哈希索引文件
# storePathIndex=${storePathRootDir}/index

# (默认) Checkpoint 文件存储路径，用于异常恢复
# storeCheckpoint=${storePathRootDir}/checkpoint

# ------------------- 关键行为开关 -------------------
# 是否允许 Broker 自动创建 Topic。生产环境通常建议设为 false，由运维统一管理
autoCreateTopicEnable=true

# 是否允许 Broker 自动创建订阅组。同上，生产环境建议关闭
autoCreateSubscriptionGroup=true

# 发送消息时，若 Topic 不存在，自动创建的默认队列数
defaultTopicQueueNums=8

# 是否启用 ACL 权限控制（需要配合 plain_acl.yml 使用）
# aclEnable=true

# 是否开启消息轨迹追踪
# traceTopicEnable=true

# ------------------- 文件与磁盘清理 -------------------
# 每天执行过期文件删除操作的时间点（24小时制），默认凌晨4点
deleteWhen=04

# 文件保留时长（单位：小时）。CommitLog 文件超过此时间可被清理，默认 48 小时
fileReservedTime=48

# 磁盘最大使用空间比率（%）。超过此阈值，消息写入会直接报错，默认 90% 左右
diskMaxUsedSpaceRatio=90

# ------------------- 性能与线程池 (按需调整) -------------------
# CommitLog 单个文件的大小，默认 1GB (1073741824 字节)
mapedFileSizeCommitLog=1073741824

# ConsumeQueue 单个文件存储的条目数，默认 30 万条
mapedFileSizeConsumeQueue=300000

# 发送消息的线程池数量
# sendMessageThreadPoolNums=128

# 拉取消息的线程池数量
# pullMessageThreadPoolNums=128
```

> **参数说明**：以上为最常用的核心配置项。如需查阅全部参数及其默认值，可以参考 Apache RocketMQ 官方的 **Server Configuration** 页面，其中包含了从 `accessMessageInMemoryMaxRatio` 到 `brokerRole` 等详尽的列表。

---

### 🚀 指定配置文件的启动命令

启动 Broker 时，必须通过 **`-c`** 参数指定你的配置文件路径。同时，建议保留 **`-n`** 参数显式指定 NameServer 地址，作为 `namesrvAddr` 配置项之外的双重保障。

#### 🐧 Linux 启动命令

```bash
# 进入 RocketMQ 根目录
cd /opt/rocketmq

# 方式一：前台启动（便于观察日志，关闭终端后进程会停止）
sh bin/mqbroker -c conf/broker.conf -n 127.0.0.1:9876

# 方式二：后台启动（生产环境推荐）
nohup sh bin/mqbroker -c conf/broker.conf -n 127.0.0.1:9876 > broker.log 2>&1 &
```
*   **`-c`**：指定配置文件路径。
*   **`-n`**：指定 NameServer 地址（即使配置文件中已写，也建议显式带上）。
*   **`> broker.log 2>&1 &`**：将标准输出和错误输出重定向到日志文件，并让进程在后台运行。

#### 🪟 Windows 启动命令

在 Windows 的 `cmd` 命令行中，首先需要进入 `bin` 目录。

```cmd
:: 进入 RocketMQ 的 bin 目录
cd C:\rocketmq\bin

:: 启动 Broker 并指定配置文件（相对路径或绝对路径均可）
start mqbroker.cmd -c ../conf/broker.conf -n 127.0.0.1:9876
```
*   `start` 命令会打开一个新的命令行窗口来运行 Broker，便于在 Windows 环境下管理。
*   如果配置文件路径不同，请将 `../conf/broker.conf` 替换为你的实际路径。