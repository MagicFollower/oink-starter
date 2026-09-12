---
title: JVM 启动参数实战：Apollo 启动脚本剖析
linkTitle: JVM 启动参数实战
description: 以真实 Apollo 配置中心启动脚本为例，逐个拆解 -server、-Xms/-Xmx、-Xss、-XX:MetaspaceSize 等参数的设计意图、常见误解与自查方法。
weight: 1
---

# 痛点：不敢动的启动脚本

新人接手项目，第一件事是把服务跑起来，然后就会拿到一份这样的脚本——以下摘自 Apollo v2.5.2（配置中心）Windows 一键启动脚本 `start-apollo.bat`，这是本地开发环境启动 ConfigService、AdminService、Portal 三个 Java 进程的真实案例：

```bat
rem  JVM 参数（本地开发环境，按需调整）
set CONFIG_SERVICE_JVM_OPTS=-server -Xms512m -Xmx512m -Xss256k -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m
set ADMIN_SERVICE_JVM_OPTS=-server -Xms512m -Xmx512m -Xss256k -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m
set PORTAL_SERVICE_JVM_OPTS=-server -Xms512m -Xmx512m -Xss256k -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m

rem  Portal Meta Server 地址（必须通过 -D 参数传入）
set META_SERVER_OPTS=-Duat_meta=http://localhost:8080

start /max "Apollo-ConfigService" cmd /k "echo ConfigService 启动中... && java %CONFIG_SERVICE_JVM_OPTS% -Dspring.config.additional-location=file:%CONFIG_SERVICE_CONF% -jar apollo-configservice-2.5.2.jar"
```

面对这一行，多数人的反应是三连问：

1. 三个服务共用同一组参数，**512m 的堆够用吗？**
2. `MetaspaceSize=128m` 是「给元空间预分配 128m」吗？
3. `-Duat_meta=http://localhost:8080` 和前面的 `-Xms512m` 是一类东西吗？

答不上来很正常——背参数口诀的人多，理解语义的人少。不理解语义的代价，是三类高频线上事故：

| 事故 | 根源 | 涉及参数 |
| --- | --- | --- |
| 容器里进程被 OOM Killer 杀死，日志连 OutOfMemoryError 都没有 | 只盯着 `-Xmx` 设内存限额，忽略了堆外内存 | `-Xmx`、`-XX:MaxMetaspaceSize` |
| Spring 应用启动阶段频繁 Full GC，启动耗时翻倍 | 不知道 `MetaspaceSize` 的默认水位线极低 | `-XX:MetaspaceSize` |
| 上线几天后随机抛 StackOverflowError | 照抄别人的 `-Xss256k`，自己的应用有深递归 | `-Xss` |

本文就用这份真实脚本，把 6 个 JVM 参数逐个拆开讲透。读完你不仅能看懂 Apollo 为什么这么配，还能推导出自己项目该配什么。

学习路线如下：

```text
拿到启动脚本 → 识别参数家族 → 逐个拆解含义 → 拼出内存账本 → 迁移到自己的项目
  读什么        先分类再深入    每个参数管什么   进程真实吃多少   怎么定自己的值
```

# 全景：从 bat 变量到 java 命令行

先看参数是怎么生效的。脚本用 `set` 把参数存进 Windows 环境变量，启动时用 `%变量名%` 展开拼接进 `java` 命令：

```text
set CONFIG_SERVICE_JVM_OPTS=-server -Xms512m ...（定义变量）
        ↓
java %CONFIG_SERVICE_JVM_OPTS% -Dspring.config.additional-location=file:... -jar apollo-configservice-2.5.2.jar
        ↓
JVM 解析参数 → 划分内存区域 → 加载类、启动 Spring Boot → ConfigService 就绪（http://localhost:8080）
```

参数本身分四个家族，**先分类是读懂任何启动脚本的第一步**：

| 家族 | 归属 | 稳定性 | 本例中的参数 |
| --- | --- | --- | --- |
| 标准参数（无 `-X`/`-XX` 前缀） | Java 官方规范 | 所有 JVM 发行版保证支持 | `-server`、`-jar` |
| `-X` | 非标准参数 | HotSpot 系通用，非 HotSpot 可能不识别 | `-Xms512m`、`-Xmx512m`、`-Xss256k` |
| `-XX` | 不稳定选项 | 官方明确不保证兼容，随版本演进 | `-XX:MetaspaceSize=128m`、`-XX:MaxMetaspaceSize=256m` |
| `-D` | 系统属性 | 属于 Java 语言规范 | `-Duat_meta=http://localhost:8080`、`-Dspring.config.additional-location=...` |

> 💡 **新人小结**：JVM 参数像四种货币。标准参数和 `-D` 是「法定货币」（规范保证），`-X` 是「区域流通货币」（HotSpot 世界通用），`-XX` 是「纪念币」（官方不担保、版本间常变）。拿到任何脚本先按前缀分类，心里就有底了——前缀越「稀有」的参数，越要查当前 JDK 版本的文档。

# 逐个拆解

## 1. `-server`：只剩仪式感的历史参数

`-server` 的历史要回到 JDK 1.2 时代。当年 HotSpot 有两个版本：

- **Client VM**：启动快、JIT 编译激进程度低，适合图形界面程序；
- **Server VM**：启动慢（分层预热久）、JIT 优化激进，适合长期运行的服务端程序。

`-client` 与 `-server` 就是在这两者之间二选一。但从 JDK 8 起，64 位 HotSpot **只内置 Server VM**，`-server` 已经没有任何实际作用——可以自己验证：

```bash
java -version
# 输出中会有一行：Java HotSpot(TM) 64-Bit Server VM (build ...)
```

那这行 `-server` 是错的吗？也不是。它有两个存在理由：

1. **向下兼容**：万一脚本被拿到 32 位 JDK 或极老的机器上跑，`-server` 保证拿到 Server VM；
2. **行业习惯**：老一辈写的模板脚本，后人照抄，谁也不敢删。

```bat
rem 正例：现代 JDK 上无害，兼容老机器，保留无妨
java -server -jar apollo-configservice-2.5.2.jar

rem 反例（认知错误）：以为「加了 -server 应用就快」
rem 真正决定服务端性能的是堆配置与 GC 选择，-server 在现代 JDK 上是空操作
```

## 2. `-Xms512m` 与 `-Xmx512m`：堆的起点与天花板

这两个参数管 JVM 最大的内存区域——堆。先明确它们控制的空间结构：

```text
JVM 堆（-Xms 定初始大小，-Xmx 定上限；本例两者相等，堆固定为 512m）
    年轻代（Eden 区 + 两个 Survivor 区） → 新对象出生地，Minor GC 的主战场
    老年代                               → 长期存活的对象晋升至此，Major/Mixed GC 的主战场
```

关键设计是 **`-Xms` 与 `-Xmx` 相等**（初始堆 = 最大堆 = 512m），即「启动即定形」。这样做有三个理由：

1. **避免运行期扩容抖动**：堆从 512m 扩到更大需要 GC 配合迁移，伴随停顿；固定堆让 GC 行为从头到尾稳定可测。
2. **容量规划确定**：压测时 512m 撑得住，生产就不会突然需要 1g——水位曲线是平的。
3. **防止「温水煮青蛙」**：允许扩堆时，内存泄漏不会立刻暴露，堆被慢慢撑到上限才崩，排障时机被推迟。

不这么写的反例和风险：

```bat
rem 反例 1：只设上限不设初始值（-Xms 默认为物理内存的 1/64）
rem 后果：启动后随负载上升经历多次堆扩容，每次扩容都伴随 GC 行为变化
java -Xmx512m -jar app.jar

rem 反例 2：完全不设 -Xmx（默认为物理内存的 1/4）
rem 后果：在一台 32G 的开发机上，JVM 默认可以拿到 8G 堆，本地调试时把机器吃穿
java -jar app.jar
```

> 💡 **新人小结**：把堆想象成餐厅座位。`-Xms` 是开业当天就摆好的桌椅数，`-Xmx` 是场地允许的最大桌椅数。两个数设成一样，等于「不做临时加桌」——客人再多也是这个规模，服务员（GC）永远按同一张地图干活。中小型服务「初始 = 上限」是社区共识。

## 3. `-Xss256k`：一个线程的标价

`-Xss` 设定**单个线程的栈大小**。每调用一个 Java 方法，JVM 就在当前线程的栈里压入一个栈帧（存放局部变量表、操作数栈等），方法返回就弹出一帧；栈压满了就抛 `StackOverflowError`。

HotSpot 在 64 位平台上默认 `-Xss1m`——那这份脚本为什么砍到 256k？看一笔线程账：

| 配置 | 单线程栈 | 200 个工作线程总占用 | 500 个线程总占用 |
| --- | --- | --- | --- |
| 默认 `-Xss1m` | 1m | 约 200m | 约 500m |
| 本例 `-Xss256k` | 256k | 约 50m | 约 125m |

Apollo ConfigService 对外提供配置读取，客户端靠 **HTTP 长轮询**（挂住连接 30~60 秒）感知配置变化，这类 IO 密集场景线程数天然偏高。线程栈是**按线程数线性分配的堆外内存**——在 512m 堆的小进程里，若每个线程白吃 1m 栈，栈内存可能反超堆本身。砍到 256k，同样的线程规模省下四分之三的栈内存。

代价与边界：

```java
// 反例：深递归应用照抄 -Xss256k
public class Factorial {
    static long fact(long n) {          // 每层递归压一个栈帧
        return n <= 1 ? 1 : n * fact(n - 1);
    }
    public static void main(String[] args) {
        fact(100_000);                  // 10 万层递归 → StackOverflowError
    }
}
```

```bat
rem 正例 1：IO 密集、调用链浅的服务（Apollo、普通 Web 服务）
java -Xss256k -jar app.jar

rem 反例 2：规则引擎 / 深度递归解析类应用照抄 256k，运行期随机 StackOverflowError
rem 这类应用应保持 1m 甚至更大
java -Xss256k -jar rule-engine.jar
```

注意下限：HotSpot 允许的 `-Xss` 最小值约 228k，低于它 JVM 直接拒绝启动（报 `The stack size specified is too small`）。256k 是贴着安全区的常见取值。

> 💡 **新人小结**：线程栈是每个线程的「个人工位」。工位越小，同一层楼（进程内存）能容纳的工人（线程）越多；但身高两米的员工（深递归、超长调用链）会被挤爆。给 IO 密集型服务瘦身栈内存是常规操作，给计算密集型服务抄这份配置就是灾难。

## 4. `-XX:MetaspaceSize=128m`：误解最深的水位线

这是全 Java 圈误解率最高的参数。先补背景：JDK 8 移除了永久代，类的元数据（类结构、方法字节码、运行时常量池等）搬进了**本地内存**，这块区域叫**元空间**。类加载器被回收时，它加载的类元数据可一并释放。

关键结论先行：

**`-XX:MetaspaceSize` 不是元空间的初始大小，而是首次触发 Full GC 的元空间占用水位线（High Water Mark）。**

机制展开：

```text
类持续加载 → 元空间占用上涨 → 越过 MetaspaceSize 水位线
        ↓
触发 Full GC（回收无用类 + 全堆停顿）→ 若空间仍不足，水位线自动上调
        ↓
重复循环，直到水位线稳定
```

JDK 8 中该水位线默认仅**约 21m**。而 Spring Boot 应用启动期正是一场「类加载风暴」——组件扫描、反射、CGLIB 动态代理、Apollo/Eureka 客户端的配置类，轻松生成上万个类。默认 21m 的水位线意味着：**应用启动到一半就撞线，触发一次完全没必要的 Full GC**，直接拖慢启动。脚本把它抬到 128m，意图就是让首次 Full GC 躲过类加载高峰。

配套的 `-XX:MaxMetaspaceSize=256m` 则是另一个语义——**元空间的硬上限**。两者对比：

| 参数 | 默认值 | 语义 | 不设置的后果 |
| --- | --- | --- | --- |
| `MetaspaceSize` | 约 21m | 首次 Full GC 的触发水位线 | 启动期大概率提前 Full GC |
| `MaxMetaspaceSize` | 无上限（仅受物理内存约束） | 元空间容量天花板 | 类加载器泄漏会静默吞掉数 G 物理内存，最终被操作系统 OOM Killer 杀进程，应用日志里连一行 OutOfMemoryError 都找不到 |

第二个参数是护栏，而且是**必设的护栏**——元空间在本地内存里，`-Xmx` 管不到它。热部署、动态代理缓存失控是它的两大泄漏源。

自查当前水位的方法：

```bash
# 查看目标进程元空间实时占用（loaded/unloaded 类数量与容量）
jstat -gcmetacapacity <pid>

# 或启动时保留 GC 日志，观察首次 Full GC 出现的时机
java -verbose:gc -XX:MetaspaceSize=128m -jar app.jar
```

```bat
rem 反例：把 MetaspaceSize 当「初始分配」来「省内存」
rem 实际它只影响 GC 触发时机，设多小也不会让元空间少占一字节
java -XX:MetaspaceSize=32m -jar app.jar
```

> 💡 **新人小结**：把元空间想象成储物柜区。`MetaspaceSize` 是「免打扰额度」——占用没到这个数，管理员（GC）不来清场；`MaxMetaspaceSize` 才是「储物区总面积」。想控制元空间占多少内存，调的是后者；想让应用启动时少挨一次折腾，调的是前者。把这两个名字搞混，是面试和实战的双重高频翻车点。

# 协同：一个 512m 进程的真实内存账本

六个参数拆完了，把视角拉高。一个常见的认知陷阱：**`-Xmx512m` 不等于这个进程只占 512m 内存**。把 Apollo ConfigService 的完整账本算出来：

| 内存区域 | 由谁决定 | 本例估算 |
| --- | --- | --- |
| 堆 | `-Xmx512m` | 512m 以内 |
| 元空间 | `-XX:MaxMetaspaceSize=256m` | 256m 以内 |
| 线程栈 | `-Xss256k` × 线程数 | 200 线程 ≈ 50m |
| JIT 代码缓存 | 分层编译默认约 240m 预留，实际用几十 m | 约 50m |
| 直接内存/堆外 | NIO、Netty（Apollo 长轮询重度使用） | 数十 m 起 |
| GC 与 JIT 自身开销 | JVM 内部结构 | 数十 m |

合计下来：**一个「512m 的 Java 进程」在任务管理器里显示 1GB 以上完全正常**。

这正是开头事故表格里第一条的根源。推论有两条：

1. **本地**：脚本同时启动三个 JVM，每个账本约 1G，三个进程并行吃掉 3G 以上——这解释了为什么低配开发机跑 Apollo 三件套会明显变卡。
2. **容器**：给容器设内存限额时，绝不能按 `-Xmx` 来定，要按完整账本留余量；更现代的做法是用 `-XX:MaxRAMPercentage` 让 JVM 按容器限额自动分配，而不是写死 `-Xmx`。

```text
误把 Xmx 当进程内存 → 容器 limit = 512m → 堆外部分（元空间 + 栈 + 直接内存）持续增长
        ↓
cgroup 内存耗尽 → 内核 OOM Killer 直接杀进程 → 应用日志毫无征兆（进程被杀前来不及输出任何日志）
```

# 追问：三个服务为什么共用同一组参数？

脚本里 ConfigService、AdminService、Portal 三份 `JVM_OPTS` 一模一样。本地开发环境这么写完全合理：三个服务都是 Spring Boot 应用，负载都不重，一刀切最省心。

但照搬到生产就是偷懒。三个服务的负载画像并不相同：

| 服务 | 角色与负载特征 | 生产环境参数方向 |
| --- | --- | --- |
| ConfigService | 对外提供配置读取 + 客户端长轮询，连接数多、QPS 高 | 堆 1g~2g，`-Xss` 可维持 256k，重点保障直接内存 |
| AdminService | 供 Portal 调用的内部 CRUD 接口，低频 | 512m~1g 足够，随实例规模走 |
| Portal | 管理界面 + 批量发布/导入导出，偶发尖峰 | 堆 1g 左右，留意导入导出功能的堆与元空间波动 |

正确的推导路径不是「抄大厂脚本」，而是三步：

```text
画出负载画像（线程数、QPS、类数量、堆外行为） → 按账本模型估算各区域 → 写入参数并压测验证
```

参数没有标准答案，只有「基于负载画像 + 内存账本」推导出的当下最优值。

# `-D` 参数：传给应用，而不是 JVM

脚本里还藏着另一类参数：

```bat
set META_SERVER_OPTS=-Duat_meta=http://localhost:8080
java ... %META_SERVER_OPTS% -Dspring.config.additional-location=file:%PORTAL_SERVICE_CONF% -jar apollo-portal-2.5.2.jar
```

`-D` 与 `-X`/`-XX` 有本质区别：**JVM 完全不理解 `-D` 的内容**，它只是把键值对放进系统属性表，供应用代码通过 `System.getProperty("uat_meta")` 读取。`-Xms512m` 改变 JVM 自身行为，`-Duat_meta=...` 对 JVM 而言只是个普通字符串。

Apollo 用 `-D` 传 Meta Server 地址是一种「环境无关构建」设计：**同一个 jar 包，不同环境只换启动参数**，不需要为每个环境重新打包。这也是 Spring Boot 生态的惯例——`-Dspring.config.additional-location` 指定外部配置文件，同样是应用层语义。

一句话区分：`-X`/`-XX` 是「对 JVM 说话」，`-D` 是「借 JVM 的嘴对应用说话」。

# 常见误区与自查工具

| 误区 | 真相 |
| --- | --- |
| `-Xmx` 设成容器内存限额 | 进程还有元空间、线程栈、直接内存等堆外开销，照此配置容器必被 OOM Killer 杀 |
| `MetaspaceSize` 是元空间初始大小 | 它是首次 Full GC 的触发水位线；控制容量的是 `MaxMetaspaceSize` |
| 加 `-server` 应用更快 | 现代 64 位 JDK 上无任何作用，纯属历史习惯 |
| `-Xss` 越小越省越好 | 深递归、深调用链应用会随机 StackOverflowError；最小约 228k |
| 照抄大厂启动脚本 | 对方 64G 机器 `-Xmx8g`，放进 2G 容器直接窒息；参数必须按自己的账本推导 |
| `-D` 参数调优 JVM | `-D` 是系统属性，JVM 不解读，只透传给应用 |

写完参数如何确认真的生效？三条命令：

```bash
# 1. 查看运行中进程实际生效的参数
jinfo -flags <pid>

# 2. 打印某参数在当前 JDK 的默认值与说明（未显式设置时尤其有用）
java -XX:+PrintFlagsFinal -version | findstr MetaspaceSize

# 3. 启动横幅：把生效参数打印在日志第一行，便于留存归档
java -XX:+PrintCommandLineFlags -jar app.jar
```

第 2 条对本文最重要的价值：随手一敲就能亲眼看到 `MetaspaceSize` 的默认值只有 21m 左右——比背十遍结论都管用。

# 要点总结

| 参数 | 一句话结论 |
| --- | --- |
| `-server` | 现代 64 位 JDK 上无实际作用，保留是兼容与习惯 |
| `-Xms512m -Xmx512m` | 堆固定 512m，初始等于上限，消除运行期扩容抖动 |
| `-Xss256k` | 单线程栈 256k，用栈空间换线程容量；深递归应用慎用 |
| `-XX:MetaspaceSize=128m` | 元空间 128m 才触发首次 Full GC——是水位线，不是初始大小 |
| `-XX:MaxMetaspaceSize=256m` | 元空间硬上限，防类加载器泄漏静默吃光内存 |
| `-Dxxx=yyy` | 系统属性，JVM 只透传，供应用读取；实现环境无关构建 |

三句总纲：

1. **先分类再深读**：标准参数、`-X`、`-XX`、`-D` 四个家族，稳定性和语义完全不同。
2. **水位线思维**：`MetaspaceSize` 这类「Size」不一定是容量，先确认它触发的是什么行为。
3. **内存账本思维**：`-Xmx` 只是账本里最大的一行，进程内存 = 堆 + 元空间 + 线程栈 × 线程数 + 代码缓存 + 直接内存，给容器定限额必须算总账。

> 💡 **新人小结**：以后拿到任何启动脚本，先按前缀把参数分好类，再问自己三个问题——堆多大（`-Xms`/`-Xmx`）？类加载水位线在哪（`MetaspaceSize`）？线程栈多少钱一位（`-Xss`）？能答上这三问，再把进程内存账本算一遍，这份脚本就真正属于你了。Apollo 这份脚本没有一行魔法，每一项都是「负载画像 → 内存账本」的朴素推导——这也是你为自己的项目写参数的方法。
