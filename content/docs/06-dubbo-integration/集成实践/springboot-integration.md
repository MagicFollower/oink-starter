---
title: "Spring Boot 集成 ZooKeeper 与 Dubbo"
description: "从 Maven 依赖与 Curator 5 版本对齐开始，完成 ZooKeeper 连接、服务暴露、静态与动态引用、启动顺序和端到端验收，并记录真实成功与失败响应。"
weight: 1
---

## 为什么“加个依赖、写个地址”经常跑不起来？

一个最小的 Dubbo + ZooKeeper 集成看起来只有三件事：

1. 引入 Dubbo 和 ZooKeeper 客户端依赖。
2. 在配置文件里写 `dubbo.registry.address=zookeeper://...`。
3. 用 `@DubboService` 暴露、用 `@DubboReference` 引用。

实际动手时，常见的失败却分布在完全不同的层面：

- 启动报 `No such extension org.apache.dubbo.registry.RegistryFactory`，因为缺少 ZooKeeper 注册中心实现。
- 报 `ClassNotFoundException` 或 `NoSuchMethodError`，因为 Curator 版本与 Dubbo 不匹配。
- 服务启动了，但消费者一直 `No provider available`，因为两者连的不是同一个 ZooKeeper 或同一个命名空间。
- 提供者还没启动，消费者启动直接失败，因为 `check` 默认是 `true`。
- 两个提供者抢 22222 的 QOS 端口，或者 ZooKeeper 的 AdminServer 占了 8080。
- 调用超时、重复回调，因为 `timeout` 与 `retries` 没有按业务语义设置。

这一篇用一套可运行的 Spring Boot 2.7 + Dubbo 3.2.20 工程，把这些点串起来，并给出真实的成功与失败响应。

> ### 💡 新人小结：集成像装一套水电
>
> - 水管（依赖）型号不对，接口就接不上。
> - 总阀（注册地址）开错，房间（服务）有水也送不到。
> - 开关（check/timeout/retries）没调好，不是没水就是水漫出来。
>
> **先保证“接得上”，再保证“调得通”，最后才是“调得稳”。**

```mermaid
flowchart LR
    A["Maven 依赖对齐"] --> B["ZooKeeper 连接"]
    B --> C["Provider 暴露端口"]
    C --> D["写注册节点"]
    D --> E["Consumer 订阅"]
    E --> F["拿到地址列表"]
    F --> G["RPC 调用"]
    G --> H["成功/失败响应"]
```

---

## 工程与版本矩阵

本地工程是一个四模块的 Spring Boot 应用：两个仓库提供者、一个流程服务、一个门户消费者。

| 组件 | 版本/配置 | 说明 |
|------|-----------|------|
| Spring Boot | 2.7.18 | 父 POM 统一管理依赖 |
| Dubbo | 3.2.20 | `dubbo-spring-boot-starter` |
| ZooKeeper 客户端 | 由 `dubbo-dependencies-zookeeper-curator5` 引入 | Curator 5 系列，匹配 Dubbo 3.2 |
| ZooKeeper 服务端 | 3.8.7 | 本机独立临时实例，实验端口 2182 |
| Java | 源码目标 1.8 | 本机用 Dragonwell 8 运行 |
| Maven | 3.10.0 | 构建使用阿里云镜像 |
| 注册中心 | `zookeeper://127.0.0.1:2181` | 实验时通过启动参数覆盖为 2182 |

模块与端口：

| 模块 | 应用名 | 角色 | 端口 |
|------|--------|------|------|
| `xxx-raw-warehouse-service` | `xxx-raw-warehouse-service` | Provider | 20881 |
| `xxx-product-warehouse-service` | `xxx-product-warehouse-service` | Provider | 20882 |
| `xxx-flow-service` | `xxx-flow-service` | Provider + Consumer | 20880 |
| `xxx-portal` | `xxx-portal` | Consumer | 18080（HTTP） |

这套工程刻意保留了两个对照：

- portal 用静态 `@DubboReference`，编译期就知道接口。
- flow-service 用编程式 `ReferenceConfig`，运行期才按 `businessType` 构造引用，编译期不依赖仓库模块。

---

## 依赖：为什么需要 curator5 的 pom

根 POM 里最关键的三段是 Spring Boot 父工程、Dubbo starter 和 ZooKeeper 注册中心依赖：

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.18</version>
</parent>

<properties>
    <dubbo.version>3.2.20</dubbo.version>
    <java.version>1.8</java.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.apache.dubbo</groupId>
            <artifactId>dubbo-spring-boot-starter</artifactId>
            <version>${dubbo.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.dubbo</groupId>
            <artifactId>dubbo-dependencies-zookeeper-curator5</artifactId>
            <version>${dubbo.version}</version>
            <type>pom</type>
            <exclusions>
                <exclusion>
                    <groupId>org.slf4j</groupId>
                    <artifactId>slf4j-reload4j</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
    </dependencies>
</dependencyManagement>
```

`dubbo-spring-boot-starter` 不包含 ZooKeeper 注册中心的 SPI 实现，所以必须额外引入 `dubbo-dependencies-zookeeper-curator5`。它的 `<type>` 是 `pom`，作用是把 Curator、ZooKeeper 客户端等一组依赖按 Dubbo 的兼容版本对齐。

排除 `slf4j-reload4j` 是因为 Spring Boot 自带 Logback，两个 SLF4J binding 同时存在会出现“multiple bindings”警告，日志实现也可能不确定。这个排除不是可选项，属于集成时必须处理的冲突。

| 依赖问题 | 症状 | 处理 |
|----------|------|------|
| 只有 starter，没有 ZooKeeper 实现 | `No such extension RegistryFactory` | 加 `dubbo-dependencies-zookeeper-curator5` |
| Curator 版本与 Dubbo 不匹配 | `NoSuchMethodError`、`ClassNotFoundException` | 用 Dubbo 提供的 BOM/POM 对齐版本，不手写版本号 |
| 多个 SLF4J binding | 启动日志警告，日志实现冲突 | 排除 `slf4j-reload4j` |
| Dubbo 3.2 搭配 Spring Boot 3 | 命名空间/依赖不兼容 | 本文组合是 Spring Boot 2.7 + Dubbo 3.2 |

构建命令：

```bash
mvn -s maven/settings-aliyun.xml -DskipTests package
```

如果本地 Maven 缓存不完整，离线构建可能因为 BOM 缺失失败；使用镜像在线补齐后再打包更稳妥。

---

## 配置：连接 ZooKeeper 与暴露端口

提供者的 `application.yml`：

```yaml
spring:
  application:
    name: xxx-raw-warehouse-service

dubbo:
  application:
    name: xxx-raw-warehouse-service
    qos-enable: false
  registry:
    address: zookeeper://127.0.0.1:2181
  protocol:
    name: dubbo
    port: 20881
```

消费者的 `application.yml`：

```yaml
server:
  port: 18080

spring:
  application:
    name: xxx-portal

dubbo:
  application:
    name: xxx-portal
    qos-enable: false
  registry:
    address: zookeeper://127.0.0.1:2181
```

配置项不多，但每一项都有边界：

| 配置 | 作用 | 注意点 |
|------|------|--------|
| `dubbo.application.name` | 应用名，应用级发现的 service name | 同一应用多实例必须一致；不同应用不能重复 |
| `dubbo.registry.address` | 注册中心地址 | 多地址用逗号分隔；协议必须是 `zookeeper://` |
| `dubbo.protocol.name` | RPC 协议 | 默认 `dubbo`；与消费者协议要匹配 |
| `dubbo.protocol.port` | 提供者监听端口 | 同机多实例必须不同；`20880` 是常见默认值 |
| `qos-enable` | Dubbo QOS 端口 | 默认 22222；同机多进程会冲突，示例统一关闭 |
| `provider.timeout` | 提供者超时参考 | 消费者也可以覆盖，最终以消费者配置为准 |

实验时没有改配置文件，而是用启动参数覆盖注册地址：

```bash
java -Ddubbo.registry.address=zookeeper://127.0.0.1:2182 \
  -jar xxx-raw-warehouse-service-1.0.0-SNAPSHOT.jar
```

这样既能复用同一份打包产物，又能把实验流量隔离到 2182，不碰本机已有的 2181 数据。

---

## 提供者：暴露服务

一个普通的查询服务只需要 `@DubboService`：

```java
@DubboService
@RequiredArgsConstructor
public class RawWarehouseQueryServiceImpl implements RawWarehouseQueryService {

    private final FlwRecordStatusStore store;

    @Override
    public List<FlwRecordStatusDTO> listFlowStatuses() {
        return store.list();
    }
}
```

带分组的回调服务用 `group` 区分多实现：

```java
@DubboService(group = FlowEventGroups.RAW_WAREHOUSE_GROUP)
@RequiredArgsConstructor
public class RawWarehouseFlowEventService implements FlowEventService {

    private final FlwRecordStatusStore store;

    @Override
    public void start(FlowEvent event) {
        record("start", event);
    }
}
```

| 注解/参数 | 作用 | 示例中的选择 |
|-----------|------|--------------|
| `@DubboService` | 声明提供者并触发暴露 | 查询服务与回调服务都使用 |
| `group` | 同一接口的多实现分组 | `RAW_WAREHOUSE`、`PRODUCT_WAREHOUSE` |
| `interface` | 默认取实现的第一个接口 | 不需要显式写 |
| `version` | 接口版本 | 示例未使用；生产变更接口时建议规划 |
| `timeout` | 提供者侧超时 | 示例在 flow-service 配置 5000ms |

启动后，日志会依次出现“暴露”和“注册”：

```text
[DUBBO] Export dubbo service ... to url dubbo://192.168.3.103:20881/...
[DUBBO] Registered dubbo service ... to registry service-discovery-registry://127.0.0.1:2182/...
[DUBBO] Registered dubbo service ... to registry zookeeper://127.0.0.1:2182/...
```

看到这两类 `Registered`，说明默认 `all` 模式同时写了应用级和接口级数据。只看到其中一条，说明注册模式或注册中心配置可能被改过。

---

## 消费者：静态与动态引用

### 静态引用

portal 在字段上直接声明：

```java
@DubboReference(check = false)
private FlowEngineService flowEngineService;

@DubboReference(check = false)
private RawWarehouseQueryService rawWarehouseQueryService;
```

`check=false` 表示启动时不校验提供者是否存在。对于 portal 这种“提供者可能晚于自己启动”的场景，它能避免应用启动失败；代价是调用时才会暴露“没有提供者”的问题。

### 动态引用

flow-service 面对的是编译期不认识的业务方。它只依赖 `FlowEventService` 接口和 `businessType → group` 路由表，运行期构造引用：

```java
private final ReferenceCache referenceCache = SimpleReferenceCache.getCache();

public <T> T getReference(Class<T> interfaceClass, String group) {
    ReferenceConfig<T> reference = new ReferenceConfig<>();
    reference.setInterface(interfaceClass);
    reference.setGroup(group);
    reference.setCheck(false);
    reference.setTimeout(3000);
    reference.setRetries(0);

    return referenceCache.get(reference);
}
```

这段代码有三个容易踩的点：

- Dubbo 3.x 已经删除 `ReferenceConfigCache`，对应替代是 `SimpleReferenceCache`；缓存 key 由 group、interface、version 组成。
- `ReferenceConfig` 是重量级对象，必须复用；每次调用都 new 一个会造成连接和内存泄漏。
- 回调是有副作用的动作，示例把 `retries` 设为 0，避免同一个事件被重复投递。

| 配置 | 静态引用 | 动态引用 | 说明 |
|------|----------|----------|------|
| `check` | `@DubboReference(check=false)` | `reference.setCheck(false)` | 启动不校验提供者 |
| `timeout` | 注解或全局配置 | `reference.setTimeout(3000)` | 超时以消费者为准 |
| `retries` | 注解或全局配置 | `reference.setRetries(0)` | 非幂等回调不重试 |
| `group` | 注解固定 | 运行期按路由表设置 | 多实现隔离 |
| 缓存 | Spring 管理代理 | `SimpleReferenceCache` | 避免重复创建 |

> ### 💡 新人小结：静态引用像自带钥匙，动态引用像到前台换钥匙
>
> - 静态引用在启动时就知道开哪扇门，钥匙（代理）直接挂在身上。
> - 动态引用先看业务类型，再去前台按 group 换对应钥匙。
> - 钥匙可以复用，但不能每次进门都重新配一把。
>
> **动态引用的重点是“延迟决定”，不是“每次重建”。**

---

## 启动与端到端验收

推荐的启动顺序是：ZooKeeper → 提供者 → 流程服务 → portal。提供者先上线，消费者启动时能拿到初始地址；即使顺序反过来，`check=false` 也能让消费者先启动，但首次调用可能失败。

本机实验的启动命令：

```bash
# 1. 启动独立 ZooKeeper（2182，独立 dataDir）
# 2. 两个仓库提供者
java -Ddubbo.registry.address=zookeeper://127.0.0.1:2182 -jar xxx-raw-warehouse-service.jar
java -Ddubbo.registry.address=zookeeper://127.0.0.1:2182 -jar xxx-product-warehouse-service.jar

# 3. 流程服务
java -Ddubbo.registry.address=zookeeper://127.0.0.1:2182 -jar xxx-flow-service.jar

# 4. 门户
java -Ddubbo.registry.address=zookeeper://127.0.0.1:2182 -jar xxx-portal.jar
```

### 验收一：端口与节点

```bash
netstat -ano | findstr ":20880 :20881 :20882 :18080"
```

四个端口都应处于 `LISTENING`。然后确认注册数据：

```bash
printf 'ls /services\nls /dubbo/com.xxx.xx.flow.api.FlowEventService/providers\nquit\n' \
  | zkCli.cmd -server 127.0.0.1:2182
```

预期能看到三个应用名，以及两个分组对应的提供者 URL。

### 验收二：真实调用

```bash
curl -s -X POST http://127.0.0.1:18080/api/flows \
  -H "Content-Type: application/json" \
  -d '{"starter":"alice","businessId":"b-1001","businessType":"RAW_WAREHOUSE"}'
```

成功响应：

```json
{"flowInstanceId":"FI000001","businessType":"RAW_WAREHOUSE","businessId":"b-1001","status":"RUNNING","starter":"alice","approver":null,"dispatchResult":"start:OK","createdAt":1792940649674,"updatedAt":1792940649960}
```

### 验收三：业务方缺席

停掉 RAW 仓库后再次调用，HTTP 仍然是 200，但 `dispatchResult` 记录失败：

```json
{"flowInstanceId":"FI000002","businessType":"RAW_WAREHOUSE","businessId":"b-1002","status":"RUNNING","starter":"bob","approver":null,"dispatchResult":"start:FAILED:ConnectException: Connection refused: no further information","createdAt":1792940671364,"updatedAt":1792940673394}
```

等会话超时、节点被清理后，错误会变成：

```text
start:FAILED:RpcException: No provider available from registry ...
```

这两种失败分别对应“有旧地址但连不上”和“没有地址”。能区分它们，排障就不会停留在“Dubbo 坏了”。

---

## 常见故障排查表

| 现象 | 常见原因 | 验证方式 | 处理 |
|------|----------|----------|------|
| `No such extension RegistryFactory` | 缺少 ZooKeeper 注册中心依赖 | 看依赖树是否有 curator5 POM | 加 `dubbo-dependencies-zookeeper-curator5` |
| `No provider available` | 提供者未注册、地址不一致、分组不匹配 | `ls /dubbo/{interface}/providers`、`ls /services/{app}` | 对齐注册地址、应用名、group、register-mode |
| `Connection refused` | 有旧地址但端口未监听 | `netstat` 看提供者端口 | 查进程、端口、会话超时与消费者缓存 |
| 启动时 `No provider` 直接失败 | 消费者 `check=true` | 看引用配置 | 设 `check=false`，或保证启动顺序 |
| 同机多提供者启动失败 | QOS 22222 或 Dubbo 端口冲突 | 看启动日志端口占用 | 关闭 QOS 或改端口 |
| 8080 被占用 | ZooKeeper AdminServer 默认开启 | `netstat` 看 8080 | `admin.enableServer=false` 或改 `admin.serverPort` |
| 日志有多个 SLF4J binding | 依赖重复 | 看启动警告与依赖树 | 排除 `slf4j-reload4j` |
| 回调重复执行 | `retries` 大于 0 且非幂等 | 看消费者配置与业务日志 | 非幂等操作设 `retries=0`，业务做幂等 |
| 调用超时 | 提供者处理慢或 `timeout` 太小 | 看耗时日志、线程池 | 调整超时，优化提供者，避免盲目加重试 |
| 只写了一套节点 | `register-mode` 被设为 interface/instance | 看启动参数与节点树 | 按消费者订阅方式选择模式 |

> ### 💡 新人小结：排障先分“没地址”还是“连不上”
>
> - `No provider` 是地址问题，查注册数据与分组。
> - `Connection refused` 是连接问题，查端口、进程、网络。
> - 启动失败是依赖或配置问题，先看异常栈第一行。
>
> **错误信息已经告诉你阶段，不要用一个“重启”覆盖所有线索。**

---

## 上线前检查清单

| 检查项 | 通过标准 |
|--------|----------|
| 依赖版本 | Dubbo、Curator、ZooKeeper 客户端由同一套 BOM 对齐 |
| 注册地址 | 提供者与消费者指向同一个 ZooKeeper 集群和同一命名空间 |
| 应用名 | 同一应用的多实例一致，不同应用不重复 |
| 注册模式 | 明确 `interface`/`instance`/`all`，并与消费者订阅方式匹配 |
| 端口 | Dubbo 端口、QOS 端口、AdminServer、HTTP 端口无冲突 |
| 超时 | 消费者 `timeout` 大于提供者正常处理时间，且小于上游超时 |
| 重试 | 非幂等操作不重试，幂等操作按业务容忍度设置 |
| 会话 | `sessionTimeout` 与网络质量匹配，监控会话过期 |
| 注册中心 | ZK 为奇数节点、跨故障域，磁盘与快照有监控 |
| 验收 | 成功调用、提供者缺席、提供者恢复三种场景都实测 |

---

## 要点总结

- 集成的第一道坎是依赖对齐：`dubbo-spring-boot-starter` 之外必须引入 `dubbo-dependencies-zookeeper-curator5`，并排除冲突的 SLF4J binding。
- 配置的核心是应用名、注册地址、协议端口和 QOS；同机多实例要给每个进程分配不同端口。
- 提供者用 `@DubboService` 暴露，分组用 `group` 区分多实现；消费者静态引用用 `@DubboReference`，动态引用用 `ReferenceConfig` + `SimpleReferenceCache`。
- `check=false` 解决启动顺序问题，但把错误推迟到调用期；`retries=0` 用于非幂等回调。
- 验收要覆盖成功、提供者缺席、提供者恢复三种场景，并区分 `No provider` 与 `Connection refused`。
- 上线前逐项检查依赖、地址、模式、端口、超时、重试、会话和注册中心高可用。

至此，Dubbo 集成的架构、选型、流程、原理、数据与工程实践已经串成一条线。建议从 [Dubbo 架构与调用链](/docs/06-dubbo-integration/架构与选型/dubbo-architecture/) 回看整体，再用 [Dubbo 在 ZooKeeper 中读写什么](/docs/06-dubbo-integration/注册与发现/data-in-zookeeper/) 对照自己环境里的真实节点。
