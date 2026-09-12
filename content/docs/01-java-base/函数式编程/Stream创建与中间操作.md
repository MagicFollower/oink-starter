---
title: Stream 创建与中间操作 —— 搭建数据处理流水线
description: 从外部迭代的耦合之痛出发，讲透 Java 8 Stream 的六种创建方式、八类中间操作、map 与 flatMap 的辨析、惰性求值与短路机制，附 for 循环与流水线的演进对比及高频陷阱。
weight: 7
---

# 为什么需要 Stream？

继续快递中转场的故事。现在你接到一批订单，要求是：**从订单列表里挑出金额大于 100 的，取出前 3 个订单号**。Java 8 之前的写法：

```java
// ========== Java 8 之前：for 循环一肩挑 ==========
List<Order> hits = new ArrayList<>();
for (Order o : orders) {                 // 关注点 1：怎么遍历
    if (o.getAmount() > 100) {           // 关注点 2：怎么过滤
        hits.add(o);
        if (hits.size() == 3) {          // 关注点 3：怎么截断
            break;
        }
    }
}
List<String> result = new ArrayList<>();
for (Order o : hits) {                   // 关注点 4：怎么转换（再来一个循环）
    result.add(o.getOrderNo());
}
```

四个关注点挤在两段循环里：**遍历机制、过滤规则、截断逻辑、转换规则全部焊死**。想并行？整个循环重写。想换过滤条件？翻循环体改 if。想复用？对不起，复制粘贴。

Java 8 的 Stream 把这段代码翻译成一条**声明式流水线**：

```java
// ========== Java 8：说清楚「做什么」，不写「怎么遍历」 ==========
List<String> result = orders.stream()          // 上传送带
        .filter(o -> o.getAmount() > 100)      // 工位 1：过滤
        .limit(3)                              // 工位 2：只取前 3
        .map(Order::getOrderNo)                // 工位 3：转成订单号
        .collect(Collectors.toList());         // 终点：装车（终端操作）
```

| 对比项 | for 外部迭代 | Stream 内部迭代 |
|--------|-------------|----------------|
| 关注点 | 遍历与业务逻辑混杂 | 只写业务逻辑 |
| 中间容器 | 每步手建中间 List | 零中间集合 |
| 改并行 | 重写循环 | `.parallel()` 一个词 |
| 截断短路 | 手写 break 与计数器 | `limit`/`findFirst` 声明式 |

> ### 💡 新人小结：Stream 是什么？
>
> 把 Stream 想象成**中转场的传送带流水线**：
> - 集合是仓库，Stream 是把包裹搬上传送带的**过程**，不是仓库本身 —— Stream 不存数据
> - 中间操作是一个个**工位**：安检（filter）、改装（map）——包裹经过，工位干活
> - **终端操作是按下启动键**：不按键，流水线一寸都不转 —— 惰性求值
>
> **一句话总结：Stream = 数据源 + 工位清单 + 一个启动键，它描述流水线，不搬运仓库。**

**学习路线图**

```
Stream 三要素 → 六种创建方式 → 八类中间操作 → map vs flatMap → 惰性与短路 → 演进对比 → Q&A
流水线结构     数据怎么上带     工位怎么排      一对多怎么拆    为什么不立即执行  for对比   出错怎么办
```

**本文涉及的专有名词**（先解释后使用；Function/Predicate 见《Function与Predicate详解》）：

| 术语 | 全称 | 含义（用自己的话） | 在本文中的角色 |
|------|------|--------------------|----------------|
| 外部迭代 | external iteration | 调用方自己写 for/iterator 控制遍历 | 旧方案的工作方式 |
| 内部迭代 | internal iteration | 只声明「做什么」，遍历由库控制 | Stream 的工作方式，并行的前提 |
| 惰性求值 | lazy evaluation | 中间操作只登记不执行，终端操作触发整体运行 | 解释「无限流」「peek 不输出」等现象 |
| 短路操作 | short-circuit operation | 不必处理全部元素即可得出结果的操作 | `limit`/`findFirst` 让无限流可用 |
| 无限流 | infinite stream | 元素按需生成、理论上没有尽头的流 | `generate`/`iterate` 创建，必须配短路 |

---

## 核心概念：流水线的三要素

```text
数据源（集合/数组/生成器） → 中间操作 0..n 个（返回 Stream，可链式） → 终端操作恰好 1 个（产出结果）
        上带                    登记工位，惰性                                  按启动键
```

**三条铁律**：

1. **Stream 不存数据**：它只是「数据源上的操作描述」，数据始终在源里，Stream 操作也不修改源。
2. **中间操作返回 Stream**：所以能 `.` 下去链式书写；每次调用都产生**新的**流对象。
3. **终端操作只有一次**：流被终端操作「消费」后即关闭，再用抛 `IllegalStateException`。

---

## 主体内容

### 六种创建方式：数据怎么上带

```java
import java.util.*;
import java.util.stream.*;

public class CreateStream {
    public static void main(String[] args) {
        // 方式 1：集合（Collection.stream）—— 最常用
        List<String> warehouse = Arrays.asList("包裹A", "包裹B", "包裹C");
        Stream<String> s1 = warehouse.stream();

        // 方式 2：数组（Arrays.stream 重载覆盖对象数组与原始类型数组）
        int[] weights = {12, 5, 30};
        java.util.stream.IntStream s2 = Arrays.stream(weights);   // 注意：得到的是数值流

        // 方式 3：Stream.of 零散元素
        Stream<String> s3 = Stream.of("包裹D", "包裹E");

        // 方式 4：Stream.empty 显式空流
        Stream<String> s4 = Stream.empty();

        // 方式 5：Stream.generate(Supplier) —— 无限流，呼应《Supplier与Consumer详解》
        Stream<String> s5 = Stream.generate(() -> "自动生成的新包裹").limit(2);

        // 方式 6：Stream.iterate(seed, Function) —— 无限流，按规则迭代
        Stream<Integer> s6 = Stream.iterate(1, n -> n * 2).limit(5);   // 1,2,4,8,16

        s5.forEach(System.out::println);   // 输出: 自动生成的新包裹（两次）
        s6.forEach(System.out::println);   // 输出: 1 2 4 8 16
    }
}
```

**参数解释**：

| 创建方式 | 适用场景 | 注意 |
|----------|---------|------|
| `collection.stream()` | 已有集合加工 | `parallelStream()` 直接得到并行流（见并行流篇） |
| `Arrays.stream(arr)` | 数组加工；原始类型数组自动得到 `IntStream` 等 | 对象数组与原始类型数组行为不同 |
| `Stream.of(e1, e2, ...)` | 手头就是几个零散元素 | `Stream.of(null)` 直接 NPE，可空值用 `Stream.ofNullable`——那是 Java 9，Java 8 需先判空 |
| `Stream.generate(supplier)` | 常量值、随机数、按需生产 | 无限流，**必须**配 `limit` 等短路操作 |
| `Stream.iterate(seed, f)` | 等差/等比/有规律的序列 | 同为无限流；三参数版（带终止条件）是 Java 9 API，Java 8 用 `limit` |
| `Files.lines(path)` | 按行读文件 | 必须放 try-with-resources 中关闭底层文件句柄 |

> ### 💡 新人小结：创建方式像什么？
>
> - 集合/数组 = **仓库现货**，整仓上传送带
> - `Stream.of` = **手头零散几件**，直接放上传送带
> - `generate` = **无限补货机**，需要多少造多少
> - `iterate` = **连锁反应工位**，上一件的输出是下一件的输入
>
> **一句话总结：先想清楚数据从哪来（现货还是按需生成），再想流水线怎么排。**

### 八类中间操作：工位怎么排

| 操作 | 形参（函数接口） | 作用 | 类比 |
|------|-----------------|------|------|
| `filter` | `Predicate<T>` | 留下判定为 true 的元素 | 安检门 |
| `map` | `Function<T,R>` | 一对一转换 | 改装工位 |
| `flatMap` | `Function<T, Stream<R>>` | 一对多展开后**压平**成一条流 | 拆箱倒货 |
| `distinct` | — | 去重（依赖 `equals`/`hashCode`） | 查重台 |
| `sorted` | `Comparator<T>`（无参按自然序） | 排序 | 分拣机 |
| `peek` | `Consumer<T>` | 途经观察（调试），不改变元素 | 监控摄像头 |
| `limit(n)` | long | 保留前 n 个（短路） | 截流闸 |
| `skip(n)` | long | 跳过前 n 个 | 跳过闸 |

```java
List<String> names = Arrays.asList("alice", "bob", "carol", "dave", "eve");

List<String> result = names.stream()
        .filter(n -> n.length() >= 3)     // 留下 alice, bob→(3≥3 保留), carol, dave, eve
        .map(String::toUpperCase)         // 全转大写
        .sorted()                         // 自然序排序
        .limit(3)                         // 只取前 3
        .collect(Collectors.toList());
System.out.println(result);               // 输出: [ALICE, BOB, CAROL]
```

**参数解释**：链上的顺序**就是执行顺序**（对每个元素依次经过各工位，详见惰性求值一节）；`sorted` 无参版要求元素实现 `Comparable`，否则运行时 `ClassCastException`。

### map 与 flatMap：一对一与一对多（高频混淆点）

**map**：每个包裹变成另一个包裹，**进 1 出 1**，流长度不变。
**flatMap**：每个包裹被**拆开倒出若干小件**，所有小件汇成一条新流，**进 1 出 n**。

```java
public class FlatMapDemo {
    public static void main(String[] args) {
        List<String> sentences = Arrays.asList("java stream", "flat map");

        // map：转换后仍是「句子流」，长度不变（2 条）
        List<String[]> wrong = sentences.stream()
                .map(s -> s.split(" "))          // 每个 String 变成 String[]，流长度仍是 2
                .collect(Collectors.toList());
        System.out.println(wrong.size());        // 输出: 2  —— 拿到的是两个数组的列表，不是单词流

        // flatMap：把每个数组拆成元素压平，流变成 4 个单词
        List<String> words = sentences.stream()
                .flatMap(s -> Arrays.stream(s.split(" ")))
                .collect(Collectors.toList());
        System.out.println(words);               // 输出: [java, stream, flat, map]
    }
}
```

**参数解释**：`flatMap` 的函数返回值必须是 `Stream<R>`——它描述「这个元素能拆出哪些下游元素」。常见搭配：`Arrays.stream(数组)`、`list.stream()`、`string.chars()`。

**决策口诀**：

```text
每个元素 → 恰好一个结果          → map
每个元素 → 一堆结果（0..n 个）   → flatMap（再多的嵌套集合一层压平）
```

> ### 💡 新人小结：map 与 flatMap 像什么？
>
> - `map` 是**换箱**：一个包裹进去，一个新包裹出来，件数不变
> - `flatMap` 是**拆箱倒货**：整箱进去，箱内小件全部汇入下一条传送带
> - map 后如果得到「流的流」（`Stream<Stream<T>>`），几乎总是你想要 flatMap
>
> **一句话总结：长度不变用 map，长度要变用 flatMap。**

### 惰性求值与短路：为什么流水线不立即转

```java
// ========== 实验：中间操作不启动，流水线一寸不转 ==========
Stream<String> lazy = Stream.of("包裹1", "包裹2", "包裹3")
        .filter(p -> { System.out.println("安检经过：" + p); return true; });
System.out.println("流水线搭建完毕，但还没按下启动键");
lazy.forEach(System.out::println);   // 终端操作触发，安检输出才出现
// 输出:
// 流水线搭建完毕，但还没按下启动键
// 安检经过：包裹1
// 包裹1
// 安检经过：包裹2
// 包裹2
// 安检经过：包裹3
// 包裹3
```

**输出揭示两个真相**：

1. **终端不触发，中间操作一步不执行**（第一行输出在提示语之后）。
2. **逐元素垂直流动，不是逐工位水平流动**——「包裹1 安检→打印」完整走完才轮到包裹2，而不是「全部安检完再全部打印」。

```text
误以为（水平）： 安检1 安检2 安检3 → 打印1 打印2 打印3
实际（垂直）：   安检1→打印1 → 安检2→打印2 → 安检3→打印3
        ↓
这正是 limit/findFirst 能「短路」的原因：够数即停，后续元素根本不经过流水线
```

```java
// ========== 短路让无限流可用 ==========
Stream.iterate(1, n -> n + 1)          // 1,2,3,4,... 无限
      .map(n -> "包裹" + n)
      .limit(3)                        // 短路：拿到 3 个就停
      .forEach(System.out::println);   // 输出: 包裹1 包裹2 包裹3（不会无限打印）
```

**注意**：`peek` 依赖「元素真的流过」这一事实——配合 `findFirst` 等短路终端时，peek 对后面的元素不会执行，**因此 peek 只适合观察调试，绝不能承载业务副作用**（详见 Q&A）。

### 演进对比：for 外部迭代 vs Stream 内部迭代

统一场景（开头的需求）：金额大于 100 的前 3 个订单号。

**旧方案：for 循环（见开头代码）。** 四个关注点混杂，中间 List 手工维护，换并行要推倒重写。

**当前方案：Stream 流水线。**

```java
List<String> result = orders.stream()
        .filter(o -> o.getAmount() > 100)
        .limit(3)
        .map(Order::getOrderNo)
        .collect(Collectors.toList());
```

**对比分析表**：

| 对比维度 | 旧方案：for 外部迭代 | 当前方案：Stream 内部迭代 |
|----------|--------------------|--------------------------|
| 写法差异 | 遍历/过滤/截断/转换四段手写，中间集合自管 | 每个关注点一个工位，声明式链接 |
| 行为差异（短路） | 手写 break 与计数器，易漏易错 | `limit` 一个工位完成，与无限流天然兼容 |
| 行为差异（并行） | 改并行需拆任务、管共享状态、防竞态 | `.parallel()` 声明切换（正确性仍需守并行流篇的规则） |
| 行为差异（复用） | 逻辑焊死在方法体 | 过滤条件是 Predicate 值，转换是 Function 值，可复用可组合 |
| 迁移成本 | — | 团队需建立「流水线 + 惰性」心智模型；调试栈不如 for 直白 |
| 旧方案适用场景 | 索引敏感的双下标遍历、性能极致的小循环、流程中要频繁修改外部状态 | 集合的过滤/转换/归约等数据处理主流场景 |

结论：for 循环并没有被淘汰（索引类、双指针类算法仍首选 for）；被淘汰的是「在 for 里堆数据处理业务」的写法。

---

## 官方 / 社区实践

```java
// ========== 1. Files.lines：按行读日志并统计（Java 8，注意资源关闭） ==========
try (java.util.stream.Stream<String> lines =
             java.nio.file.Files.lines(java.nio.file.Paths.get("app.log"))) {
    long errors = lines.filter(line -> line.contains("ERROR")).count();
    System.out.println("错误行数：" + errors);
}

// ========== 2. 集合工具链的标配组合 ==========
Map<Character, List<String>> byInitial = names.stream()
        .collect(Collectors.groupingBy(s -> s.charAt(0)));   // 收集器见 Collectors 篇

// ========== 3. 数组与原始类型无缝接入 ==========
int total = Arrays.stream(weights).sum();    // IntStream 求和，详见《数值流与原始类型特化》
```

**参数解释**：`Files.lines` 必须置于 try-with-resources——底层文件句柄由流持有，流不关闭则句柄泄漏；这是 Java 8 中少数「流需要手动关闭」的场景。

---

## 高频问题与踩坑排查（Q&A）

**Q1：Stream 会修改原来的集合吗？**

不会。`filter`/`map` 等中间操作都不动源，结果由终端操作产出为新集合。函数式风格下「源不可变、产出新结果」是默认契约——想要原地修改集合，用 `list.removeIf` / `replaceAll` 这类集合 default 方法（它们是集合的方法，不是 Stream 操作）。

**Q2：同一个 Stream 能用两次吗？**

不能。终端操作后流即关闭：

```java
Stream<String> s = names.stream();
s.forEach(System.out::println);
// s.forEach(System.out::println);
// ❌ IllegalStateException: stream has already been operated upon or closed
```

需要多次消费就每次从源新开一条流（`names.stream()` 本身很廉价），或先把结果 collect 成集合。

**Q3：`Stream.of(null)` 为什么炸了？**

`Stream.of(T...)` 把单个 null 当作「包含一个 null 的数组」处理，随后多数操作 NPE。Java 8 的安全写法：

```java
String maybeNull = null;
Stream<String> safe = maybeNull == null ? Stream.empty() : Stream.of(maybeNull);
```

**Q4：peek 里写业务逻辑（如计数、修改外部对象）安全吗？**

不安全。peek 的执行受惰性与短路影响：`limit` 之后的元素不经过 peek，某些优化下（如 count 直接取源 size）整个 peek 都可能不执行。peek 只做观察；带副作用的操作放进终端操作（`forEach`/`collect`）。

**Q5：`sorted()` 抛 ClassCastException 怎么回事？**

无参 `sorted()` 按自然序排序，要求元素实现 `Comparable`。自定义类没实现就该用 `sorted(Comparator.comparing(XXX::getField))` 显式给比较器。

**Q6：filter 和 map 的顺序有讲究吗？**

有。先 filter 后 map 能让「被过滤掉的元素」不进入转换工位，通常更快；且 map 之后类型变了，filter 条件的书写复杂度也会变化。原则：**尽早过滤，推迟转换**。

---

## 要点总结

1. **三要素**：数据源 → 0..n 个中间操作 → 恰好 1 个终端操作；Stream 不存数据、不修改源。
2. **六种创建方式**：集合/数组/of/empty/generate/iterate；后两者是无限流，必须配短路。
3. **中间操作八件套**：filter/map/flatMap/distinct/sorted/peek/limit/skip；顺序即执行顺序。
4. **map 进 1 出 1，flatMap 拆箱倒货**；出现 `Stream<Stream<T>>` 基本就是该用 flatMap 的信号。
5. **惰性求值 + 垂直流动**：终端按键才启动，逐元素走完全程；短路操作让无限流与提前截断成为可能。

> ### 💡 新人小结：Stream 创建与中间操作学完了，记住这 3 点
>
> 1. **流水线不按键不转** —— 中间操作只是登记，终端才是启动键
> 2. **包裹逐件走完全程，不是全体排队过同一工位** —— 理解了垂直流动，limit/findFirst 的短路就通了
> 3. **换箱用 map，拆箱用 flatMap** —— 长度变不变，一眼选对工位
>
> **一句话总结：Stream 让你像画流程图一样写数据处理——工位画好，按下终端的启动键。**
