---
title: Collectors 收集器详解 —— 数据分拣与打包的艺术
description: 从手写分组循环的样板之痛出发，讲透 Java 8 Collectors 全家：toMap 冲突与保序、groupingBy 与下游收集器、partitioningBy、mapping 组合与自定义收集器五要素，附命令式分组的演进对比。
weight: 9
---

# 为什么需要收集器？

流水线终点最常见的产出不是「一个值」，而是**容器**——尤其是报表型需求。看这个经典任务：**按地区统计订单总金额**。Java 8 之前的写法：

```java
// ========== Java 8 之前：双层 Map + 嵌套循环 + 手写合并 ==========
Map<String, Double> totalByRegion = new HashMap<>();
for (Order o : orders) {
    String region = o.getRegion();
    Double old = totalByRegion.get(region);      // 判空、取旧值
    totalByRegion.put(region, old == null ? o.getAmount() : old + o.getAmount());
}
```

十行样板里只有一行是业务。更复杂的报表——「按地区分组、组内再按品类分组、各品类报总数」——嵌套循环直接失控：

```text
报表需求一层层加 → 循环一层层套 → 中间 Map 一层层 new → 改一个口径全方法重写
```

Java 8 的解法：`collect` 终端操作 + `Collectors` 工厂提供的**收集器（Collector）**。收集器是「分拣打包方案」的标准化封装，嵌套收集器对应嵌套报表，声明即完成：

```java
// ========== 当前方案：一行业务，零样板 ==========
Map<String, Double> totalByRegion = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion, Collectors.summingDouble(Order::getAmount)));
```

| 对比项 | 命令式分组 | 收集器 |
|--------|-----------|--------|
| 分组一层 | 循环 + 判空 + put | `groupingBy(键提取器)` |
| 统计口径 | 再加一层循环与累加变量 | 换一个下游收集器 |
| 嵌套报表 | 循环套循环 | 收集器套收集器 |

> ### 💡 新人小结：收集器是什么？
>
> 终端 `collect` 是**分拣打包车间的开工指令**，`Collectors.xxx()` 是**一张张打包方案单**：
> - `toList()` = 全部装进一个大箱
> - `groupingBy(地址)` = 按目的地分拣上架
> - `toMap(单号, 重量)` = 按面单号合并成台账
> - 分拣单里还能嵌分拣单 = 报表的「组内再分组」
>
> **一句话总结：collect 执行，Collector 定义方案——嵌套收集器就是嵌套报表。**

**学习路线图**

```
基础收集器 → toMap 防炸 → groupingBy 家族 → partitioningBy → 组合与定制 → 演进对比 → Q&A
五大基础     键冲突处理    下游收集器      布尔两分法    mapping/五要素   手写分组对比  出错怎么办
```

**本文涉及的专有名词**（先解释后使用；可变归约见《Stream终端操作与归约》）：

| 术语 | 全称 | 含义（用自己的话） | 在本文中的角色 |
|------|------|--------------------|----------------|
| 收集器 | Collector | 封装「往哪个容器、怎么装、怎么合并、怎么收尾」的方案对象 | collect 的方案参数 |
| 分类函数 | classifier | 从元素提取分组键的函数（如 `Order::getRegion`） | groupingBy 的第一参数 |
| 下游收集器 | downstream collector | 嵌套在内层、处理同组元素的收集器 | 嵌套报表的积木 |
| 完成器 | finisher | 容器装满后的最后一步转换（容器 → 最终结果） | collectingAndThen 的落点 |

---

## 核心概念：collect 与 Collector 的分工

```text
stream.collect(Collector) 终端操作
        ↓ 按 Collector 的方案执行「可变归约」
supplier 建容器 → accumulator 逐件装 → combiner 并行合并 → finisher 收尾出结果
```

`Collectors` 工厂类提供 40+ 个现成方案，常用五件套先上手：

```java
import java.util.stream.*;

List<String> list  = names.stream().collect(Collectors.toList());        // List
java.util.Set<String> set = names.stream().collect(Collectors.toSet());  // Set（去重）

// toCollection：指定容器类型（toList 不保证实现类，想要 LinkedList 用它）
java.util.LinkedList<String> linked =
        names.stream().collect(Collectors.toCollection(java.util.LinkedList::new));

// joining：字符串拼接（直接收 CharSequence 流）
String manifest = names.stream().collect(Collectors.joining(", ", "[", "]"));
System.out.println(manifest);   // 输出: [包裹A, 包裹B, 包裹C]

// toMap：键提取器 + 值提取器
Map<String, Integer> weightOf = names.stream()
        .collect(Collectors.toMap(n -> n, String::length));
```

**参数解释**：

| 收集器 | 形参 | 产出 |
|--------|------|------|
| `toList()` / `toSet()` | — | List / Set（实现类由库定） |
| `toCollection(容器工厂)` | `Supplier<C>` | 指定的容器类型 |
| `joining` | 分隔符、前缀、后缀 | String |
| `toMap` | 键函数、值函数（+ 合并函数、+ Map 工厂） | Map |

---

## 主体内容

### toMap 防炸三连：合并函数、保序、空值

`toMap` 是收集器里事故率最高的一个——**键重复直接抛 `IllegalStateException`**：

```java
// ========== 事故复现：同一订单号出现两次 ==========
// ❌ IllegalStateException: Duplicate key 1001
// Map<String, Double> wrong = orders.stream()
//         .collect(Collectors.toMap(Order::getOrderNo, Order::getAmount));

// ========== 解法一：三参版给合并函数 —— 键冲突时的仲裁规则 ==========
Map<String, Double> merged = orders.stream()
        .collect(Collectors.toMap(
                Order::getOrderNo,
                Order::getAmount,
                (oldVal, newVal) -> oldVal + newVal));   // 同单号金额累加

// ========== 解法二：四参版再指定 Map 类型 —— 想保序用 LinkedHashMap ==========
Map<String, Double> ordered = orders.stream()
        .collect(Collectors.toMap(
                Order::getOrderNo,
                Order::getAmount,
                (a, b) -> a,
                java.util.LinkedHashMap::new));          // 按遇流顺序存放

// ========== 解法三：值允许为 null 时 toMap 会 NPE —— 改用 forEach 收集 ==========
Map<String, String> withNull = new java.util.HashMap<>();
items.forEach(i -> withNull.put(i.getKey(), i.getMaybeNullValue()));
```

**参数解释**：

| 参数位 | 作用 | 不给的后果 |
|--------|------|-----------|
| 键函数 / 值函数 | 提取 Map 的 key/value | — |
| 合并函数 | 同键冲突仲裁 | 重复键抛 `IllegalStateException` |
| Map 工厂 | 指定实现类 | 默认 HashMap（无序） |

**注意**：`Collectors.toMap` 的值函数返回 null 也会抛 NPE（HashMap 内部 merge 语义限制）——可空值场景直接放弃 toMap，用 forEach。

### groupingBy 家族：分拣上架的三层形态

```java
// ========== 形态一：单参 —— Map<键, List<元素>> ==========
Map<String, List<Order>> byRegion = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion));

// ========== 形态二：二参 —— 换掉「组内装什么」= 下游收集器 ==========
Map<String, Long> countByRegion = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion, Collectors.counting()));

Map<String, Double> sumByRegion = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                Collectors.summingDouble(Order::getAmount)));

// ========== 形态三：三参 —— 再指定 Map 工厂（保序） ==========
Map<String, List<Order>> keptOrder = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                java.util.LinkedHashMap::new,
                Collectors.toList()));
```

**参数解释**：三个参数位依次是——分类函数（必给）、Map 工厂（默认 HashMap）、下游收集器（默认 `toList()`）。**下游收集器决定了「每组里怎么打包」**，这正是嵌套报表的核心积木。

**常用下游收集器速查**：

| 下游 | 产出 | 报表语义 |
|------|------|---------|
| `toList()` | List\<T\> | 组内明细 |
| `counting()` | Long | 组内条数 |
| `summingInt/Long/Double(fn)` | 数值 | 组内合计 |
| `averagingDouble(fn)` | Double | 组内均值 |
| `maxBy(cmp)` / `minBy(cmp)` | Optional\<T\> | 组内最值 |
| `mapping(fn, downstream)` | 取决于下游 | 先转换再收集 |
| `collectingAndThen(downstream, finisher)` | 转换后结果 | 收完再加工 |

**二级分组：报表的嵌套。**

```java
// 按地区分组，组内再按品类分组并计数
Map<String, Map<String, Long>> full = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                Collectors.groupingBy(Order::getCategory, Collectors.counting())));
// 结构: {华东={生鲜=3, 数码=5}, 华南={生鲜=2}}
```

> ### 💡 新人小结：groupingBy 像什么？
>
> 分拣车间的**多层货架**：
> - 第一参 = 按什么分拣（地址贴纸）
> - 下游收集器 = 每层货架上**怎么打包**（明细箱 / 计数牌 / 合计单）
> - 二级 groupingBy = 货架下再设小货架 —— 组内再分组
>
> **一句话总结：groupingBy 管「怎么分组」，下游收集器管「组内怎么打包」，嵌套即报表。**

### partitioningBy：布尔两分法的专用快车

按「是否满足条件」分成两堆，用 `groupingBy(布尔键)` 也能做，但 `partitioningBy` 是专用优化——**结果必含 true/false 两键**，哪怕一堆为空：

```java
Map<Boolean, List<Order>> parts = orders.stream()
        .collect(Collectors.partitioningBy(o -> o.getAmount() > 100));

System.out.println(parts.get(true).size());    // 大额订单数
System.out.println(parts.get(false).size());   // 小额订单数（可能为 0，但键一定在）

// 与下游组合：大额订单取单号列表
Map<Boolean, List<String>> nos = orders.stream()
        .collect(Collectors.partitioningBy(o -> o.getAmount() > 100,
                Collectors.mapping(Order::getOrderNo, Collectors.toList())));
```

**参数解释**：分类函数必须是 `Predicate<T>`（产出布尔）。需要「键一定存在」的语义（如报表两栏都要展示）时选它；键多于两类立刻回 `groupingBy`。

### mapping 与 collectingAndThen：收尾组合件

```java
// mapping：分组后只保留转换结果（常救「组内只要一个字段」的场景）
Map<String, List<String>> noByRegion = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                Collectors.mapping(Order::getOrderNo, Collectors.toList())));

// collectingAndThen：收完再加工 —— 产出不可变结果
Map<String, List<Order>> frozen = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                Collectors.collectingAndThen(
                        Collectors.toList(),
                        Collections::unmodifiableList)));     // 每组列表不可变
```

**参数解释**：`mapping(转换, 下游)` 等价于「先 map 中间操作再分组」，但嵌进收集器后能与其他下游自由组合；`collectingAndThen(下游, 收尾函数)` 是收集器的「完成器」扩展点——不可变化、包装类型转换都走这里。

### 自定义收集器：五要素拼一台打包机

现成方案不满足时，用 `Collector.of` 五要素自造（supplier/accumulator/combiner/finisher/特性）：

```java
// 案例：把名字收集成一个「去重、按字母序」的字符串
String rank = names.stream().collect(
        java.util.stream.Collector.of(
                java.util.TreeSet<String>::new,                 // supplier：建容器（TreeSet 去重有序）
                (set, n) -> set.add(n),                         // accumulator：装一件
                (left, right) -> { left.addAll(right); return left; },   // combiner：并行合并
                set -> String.join(" | ", set)));               // finisher：容器 → 最终字符串
System.out.println(rank);   // 输出（示例）: alice | bob | carol
```

**参数解释**：五要素与《Stream终端操作与归约》reduce 三形态同源，多了 finisher（收尾转换）与特性标记（并发/无序等优化提示）。经验法则：**九成需求用现成收集器组合即可，自定义留给确有性能或格式要求的场景**。

### 演进对比：手写分组循环 vs groupingBy

统一场景（开头任务）：按地区统计订单总金额，再升级为「各地区大额订单数」。

**旧方案：命令式分组。**

```java
// 基础版：双层循环升级一次需求，样板翻倍
Map<String, Double> totalByRegion = new java.util.HashMap<>();
for (Order o : orders) {
    totalByRegion.merge(o.getRegion(), o.getAmount(), Double::sum);   // merge 是旧写法的最优形态
}

Map<String, Long> bigCountByRegion = new java.util.HashMap<>();
for (Order o : orders) {
    if (o.getAmount() > 100) {
        bigCountByRegion.merge(o.getRegion(), 1L, Long::sum);
    }
}
```

**当前方案：收集器。**

```java
Map<String, Double> totalByRegion2 = orders.stream()
        .collect(Collectors.groupingBy(Order::getRegion,
                Collectors.summingDouble(Order::getAmount)));

Map<String, Long> bigCountByRegion2 = orders.stream()
        .filter(o -> o.getAmount() > 100)
        .collect(Collectors.groupingBy(Order::getRegion, Collectors.counting()));
```

**对比分析表**：

| 对比维度 | 旧方案：手写分组循环 | 当前方案：Collectors |
|----------|--------------------|---------------------|
| 写法差异 | 判空、merge、中间 Map 样板每需求一份 | 声明「键 + 口径」两件事，其余归库 |
| 行为差异（口径变更） | 从「合计」改「计数」= 改循环体逻辑 | 换一个下游收集器，主结构不动 |
| 行为差异（嵌套报表） | 循环套循环，变量爆炸 | 收集器套收集器，结构即报表形状 |
| 行为差异（并行） | HashMap 共享可变状态，并行需换并发容器重写 | 流并行时 combiner 自动分段合并，收集器不改 |
| 迁移成本 | — | 需掌握下游组合与 toMap 防炸规则 |
| 旧方案适用场景 | 需要复杂跳过逻辑、边遍历边改外部状态的特殊流程 | 一切「分组/统计/映射产出容器」的标准场景 |

结论：手写循环的最优形态（`merge`）已经接近天花板，但**口径一变就得动逻辑**；收集器把「分组结构」与「统计口径」解耦成两个可替换的参数——这正是声明式的价值。

---

## 官方 / 社区实践

```java
// ========== 1. groupingBy + counting：词频/日志级别统计 ==========
java.util.List<String> logLines = java.util.Arrays.asList(
        "2026-01-01 INFO 服务启动", "2026-01-01 WARN 磁盘水位偏高", "2026-01-01 INFO 收到心跳");
Map<String, Long> levelCount = logLines.stream()
        .collect(Collectors.groupingBy(line -> line.split(" ")[1], Collectors.counting()));
System.out.println(levelCount);   // 输出: {INFO=2, WARN=1}

// ========== 2. partitioningBy + mapping：两栏报表 ==========
Map<Boolean, java.util.List<String>> vipNos = orders.stream()
        .collect(Collectors.partitioningBy(Order::isVip,
                Collectors.mapping(Order::getOrderNo, Collectors.toList())));

// ========== 3. toMap + merge：库存台账合并 ==========
Map<String, Integer> stock = shipments.stream()
        .collect(Collectors.toMap(Shipment::getSku, Shipment::getQty, Integer::sum));
```

**参数解释**：三个案例分别是「计数报表」「两栏名单」「按主键合并台账」——业务代码中出现频率最高的三种收集器形态，可作为模板直接套用。

---

## 高频问题与踩坑排查（Q&A）

**Q1：toMap 抛 Duplicate key，怎么定位？**

两步：先确认是不是**预期内的键重复**（一对多关系误用 toMap）——是则换 `groupingBy` 或给合并函数；再检查键提取函数是否提错字段（比如把带时间戳的字段当唯一键）。合并函数不是可选装饰，**任何对「多对一」的业务都要显式写仲裁规则**。

**Q2：groupingBy 抛 NPE「element cannot be mapped to a null key」怎么回事？**

分类函数对某个元素返回了 null 键。收集器明确禁止 null 键（与 HashMap 本身允许 null key 不同）。解法：分类函数里兜底（`o -> o.getRegion() == null ? "未知" : o.getRegion()`）。

**Q3：想要不可变的收集结果怎么办？**

对整个 Map：`collectingAndThen(groupingBy(...), Collections::unmodifiableMap)`；对每组列表：把下游包一层 `collectingAndThen(toList(), Collections::unmodifiableList)`（见正文 frozen 案例）。语义上「报表结果不该被下游代码改」，不可变化值得付出这一行。

**Q4：并行流下收集器线程安全吗？**

无需担心，也**不要**往收集器里塞共享可变对象。并行时每个分片独立建容器累积，最后 combiner 合并——收集器全程无共享状态（这也是自定义收集器的要求）。真正要防的是 Q5。

**Q5：collect 的 lambda 里引用外部 List「顺手 add」算收集吗？**

不算，是反模式（同《Stream终端操作与归约》Q4）：并行流下直接数据竞争，串行流也绕开了 combiner 优化。外部容器想参与收集，用 `toCollection(() -> 那个List)` 明示容器来源——但先问自己为什么不用标准收集器。

**Q6：groupingBy 之后某组可能没有元素，怎么取？**

分组键来自元素本身，所以「出现过的键必有至少一个元素」；为空的只会是 `partitioningBy` 的 false 键（或你先 filter 了）。取值用 `map.getOrDefault(key, 默认值)`，不要裸 `get` 后假设非空。

---

## 要点总结

1. **collect 执行、Collector 定方案**：supplier 建容器 → accumulator 装 → combiner 并行合并 → finisher 收尾。
2. **toMap 三连防炸**：重复键给合并函数、保序给 LinkedHashMap 工厂、可空值放弃 toMap 改 forEach。
3. **groupingBy 三层形态**：单参出明细、二参换下游、三参换 Map 实现；下游收集器就是「组内口径」。
4. **partitioningBy 是布尔专车**：两键必全、自带空组，两分类报表优先用它。
5. **口径与结构解耦**：换统计口径 = 换下游收集器；嵌套报表 = 嵌套收集器；并行不需要改收集器。

> ### 💡 新人小结：收集器学完了，记住这 3 点
>
> 1. **报表 = 分组 × 口径两个旋钮** —— groupingBy 管分组，下游收集器管口径，两个旋钮自由组合
> 2. **toMap 不是默认安全的** —— 一对多关系先想 groupingBy，坚持 toMap 必带合并函数
> 3. **收集器没有共享状态** —— 并行安全的底气来自「分段建容器、最后合并」，别往里塞外部 List
>
> **一句话总结：把打包方案写成收集器，分拣车间就会替你把报表装订成型。**
