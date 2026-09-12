---
title: Supplier 与 Consumer 详解 —— Java 8 函数接口入门
description: 从痛点出发讲透 Java 8 两大函数接口 Supplier 与 Consumer 的设计、用法、变体及高频踩坑，附 Stream/Optional 官方实践与常见问题排查。
weight: 2
---

# 为什么需要 Supplier 和 Consumer？

想象你是一个快递驿站的老板。每天有两类人和你打交道：

- **寄件人**：什么都不带进来需求，只交给你一个包裹（**生产**东西给你）。
- **收件人**：不给你任何东西，只把包裹取走（**消费**你的东西）。

在 Java 8 之前，如果你想把这个「生产」或「消费」的动作本身作为参数传来传去，唯一的办法是定义一个匿名内部类：

```java
// ========== Java 8 之前：传递一个"动作"有多痛苦 ==========
ExecutorService executor = Executors.newSingleThreadExecutor();

// 只想延迟执行一段逻辑，却要写 5 行模板代码
executor.submit(new Callable<String>() {
    @Override
    public String call() {
        return loadFromDatabase(); // 真正关心的只有这一行
    }
});
```

5 行代码里只有 1 行是业务逻辑，其余全是「仪式性代码」。更痛的是：**JDK 无法为每一个「传入什么、返回什么」的组合都发明一个接口**，`Callable` 有，那「无参返回 int」呢？「无参返回 double」呢？「接收两个参数无返回」呢？接口爆炸不可避免。

Java 8 的解法：**用 Lambda 表达式 + 一套标准化函数接口（`java.util.function` 包）**，把「函数签名」本身抽象成类型。

| 对比项 | Java 8 之前（匿名内部类） | Java 8 之后（Lambda + 函数接口） |
|--------|--------------------------|--------------------------------|
| 代码量 | 4-6 行模板代码 | 1 行表达式 |
| 语义 | `new Callable<...>() {...}` 噪音大 | `() -> loadFromDatabase()` 直白 |
| 复用性 | 每处各自定义接口 | 42 个标准接口全覆盖 |
| 组合能力 | 无 | 与 Stream / Optional / CompletableFuture 无缝配合 |

> ### 💡 新人小结：函数接口到底是什么？
>
> 把函数接口想象成「**快递单模板**」：
> - 快递单规定了「从哪收（参数）」和「送到哪（返回值）」—— 函数接口规定了方法签名
> - 你填的内容每次不同 —— Lambda 是你填的具体逻辑
> - 驿站不关心包裹里是什么 —— 调用方只认签名，不认实现
>
> **一句话总结：函数接口 = 一张只有格式的快递单，Lambda = 你填写的内容。**

**学习路线图**

```
核心概念 → 基础用法 → 常用变体 → 官方实战 → 踩坑排查
是什么      怎么写      家族成员    Stream里怎么用  出错怎么办
```

---

## 核心概念：什么是函数接口（Functional Interface）

**函数接口** = 有且仅有一个抽象方法的接口（`default` / `static` 方法不计入）。用 `@FunctionalInterface` 注解标记后，编译器会强制检查这一约束。

`java.util.function` 包按「**参数个数 T → 返回值 R**」的组合，提供了 42 个标准接口，其中最核心的是四大金刚：

| 接口 | 抽象方法 | 语义 | 快递类比 |
|------|---------|------|---------|
| `Supplier<T>` | `T get()` | 无参，**生产**一个 T | 寄件人：交出包裹 |
| `Consumer<T>` | `void accept(T)` | 收一个 T，**消费**掉，无返回 | 收件人：取走包裹 |
| `Function<T,R>` | `R apply(T)` | 收 T，转换成 R | 转运站：拆箱重组 |
| `Predicate<T>` | `boolean test(T)` | 收 T，判断真假 | 安检员：放行或扣下 |

本文聚焦前两个——它们是「生产者 / 消费者」这对最基础的方向。

---

## 主体内容

### Supplier：只生产，不索取

#### 痛点

你有没有写过这样的代码——日志打印前先拼好了字符串，结果日志级别不够，拼接白做了：

```java
// ❌ 即使 logger.debug 不输出，" expensiveToString(obj) " 也会先执行
// 白白浪费了字符串拼接的开销
logger.debug("对象详情: " + expensiveToString(obj));
```

问题的本质是：**Java 是严格求值语言，参数在调用前必然先算好**。我们需要的其实是「先承诺一个生产逻辑，等真正需要时再执行」——也就是**延迟执行**。

#### 设计

`Supplier<T>` 的设计哲学只有一句话：**把"生产 T"这个动作本身打包成值，四处传递，需要时才调用 `get()` 触发执行**。

```java
@FunctionalInterface
public interface Supplier<T> {
    T get();
}
```

#### 具体用法

```java
import java.util.function.Supplier;

public class SupplierDemo {

    static String loadFromDatabase() {
        System.out.println(">>> 真正访问数据库了!");
        return "user-data";
    }

    public static void main(String[] args) {
        // ========== 推荐写法：Lambda ==========
        Supplier<String> supplier = () -> "hello"; // 无参，直接返回
        System.out.println(supplier.get());
        // 输出: hello

        // ========== 延迟执行：定义时不跑，get() 时才跑 ==========
        Supplier<String> lazy = SupplierDemo::loadFromDatabase; // 方法引用
        System.out.println("--- 定义完成，还没有访问数据库 ---");
        // 输出: --- 定义完成，还没有访问数据库 ---
        System.out.println(lazy.get());
        // 输出: >>> 真正访问数据库了!
        //       user-data

        // ========== 不推荐写法（仅展示） ==========
        // ❌ 等号右边会立刻执行 loadFromDatabase()，"延迟"彻底失效
        Supplier<String> eager = loadResult -> loadResult; // 概念演示
        String result = loadFromDatabase();          // 已经执行！
        Supplier<String> wrapped = () -> result;      // 包的只是现成结果
    }
}
```

**要点解释：**

| 写法 | 执行时机 | 是否延迟 |
|------|---------|---------|
| `Supplier<String> s = () -> loadFromDatabase();` | 调用 `s.get()` 时 | ✅ 是 |
| `String r = loadFromDatabase(); Supplier<String> s = () -> r;` | 定义第 1 行时 | ❌ 否 |
| `Supplier<String> s = SupplierDemo::loadFromDatabase;` | 调用 `s.get()` 时 | ✅ 是（方法引用同 Lambda） |

> ### 💡 新人小结：Supplier 是「自动售货机的按钮」
>
> - 按钮（Supplier）本身不出货 —— 定义 Lambda 时什么都不执行
> - 按下去（`get()`）才掉出饮料（返回 T） —— 触发时机完全由你控制
> - 按一次出一次，每次现做 —— `get()` 每次调用都会重新执行逻辑
>
> **一句话总结：Supplier 把「生产动作」变成了可以揣在兜里、想按才按的按钮。**

### Consumer：只消费，不归还

#### 痛点

遍历一个集合并对每个元素做点事，Java 8 之前要写 `for` 循环样板；框架开发者更痛——想提供一个「回调」让使用者自定义处理逻辑，只能自定义监听器接口，导致每个框架一套回调规范。

#### 设计

`Consumer<T>` 把「**接收 T 并处理掉**」这个动作标准化。它不返回任何东西——就像包裹被收件人拿走后就「没了」，你不会再得到反馈。

```java
@FunctionalInterface
public interface Consumer<T> {
    void accept(T t);

    default Consumer<T> andThen(Consumer<? super T> after) { // 链式组合
        return (T t) -> { accept(t); after.accept(t); };
    }
}
```

注意它自带一个 `default` 方法 `andThen`——这是函数接口可以拥有多个非抽象方法的活例子，也是「消费动作可拼接」的关键设计。

#### 具体用法

```java
import java.util.function.Consumer;

public class ConsumerDemo {
    public static void main(String[] args) {
        // ========== 推荐写法：基础用法 ==========
        Consumer<String> printer = msg -> System.out.println("[LOG] " + msg);
        printer.accept("服务启动");
        // 输出: [LOG] 服务启动

        // ========== andThen 链式组合：先打印，再统计长度 ==========
        Consumer<String> pipeline = printer
                .andThen(msg -> System.out.println("[LEN] " + msg.length()));
        pipeline.accept("hello");
        // 输出: [LOG] hello
        //       [LEN] 5

        // ========== 不推荐写法（仅展示） ==========
        // ❌ 在 Consumer 的 Lambda 里 return 值是编译错误，语义也不符
        // Consumer<String> wrong = msg -> msg.length(); // 编译不过：void 不兼容

        // ❌ 用 Consumer 去做"转换"工作，结果无处安放
        // 转换场景应该用 Function<T, R>
    }
}
```

**参数/方法解释：**

| 方法 | 说明 |
|------|------|
| `accept(T t)` | 执行消费逻辑，无返回值 |
| `andThen(after)` | 返回新 Consumer，先执行当前逻辑，再执行 `after`；调用顺序 = 书写顺序 |
| `Consumer.andThen(a, b)` 中的异常 | 前一个抛异常，后一个不会执行（无事务性回滚概念） |

> ### 💡 新人小结：Consumer 是「快递签收员」
>
> - 签收员收下包裹（`accept`），不会退回任何东西 —— void 返回
> - 签收员可以是一个小组，按顺序处理（`andThen` 链）—— 先登记再入库
> - 你把签收规则写给驿站，包裹到了驿站照规则办 —— 回调的标准化
>
> **一句话总结：Consumer 把「处理动作」变成了参数，接收方照单全收、绝不退还。**

### 常用变体：一个家族，各管一摊

基础版只能处理对象类型。为了消除自动装箱开销和支持双参数，官方提供了变体：

| 接口 | 抽象方法 | 典型场景 |
|------|---------|---------|
| `BooleanSupplier` | `boolean getAsBoolean()` | 无参判断，如 `List::isEmpty` |
| `IntSupplier` / `LongSupplier` / `DoubleSupplier` | `int/long/double getAsXxx()` | 无参生产原始类型，避免装箱 |
| `BiConsumer<T,U>` | `void accept(T t, U u)` | 消费两个参数，如遍历 Map |
| `ObjIntConsumer<T>` 等 | `void accept(T t, int value)` | 一个对象 + 一个原始类型 |

```java
import java.util.HashMap;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.IntSupplier;

public class VariantDemo {
    public static void main(String[] args) {
        // ========== 原始类型 Supplier：避免装箱 ==========
        IntSupplier counter = () -> 42;
        System.out.println(counter.getAsInt());
        // 输出: 42

        // ❌ 不推荐：Supplier<Integer> 每次调用都触发 int -> Integer 装箱
        // Supplier<Integer> boxed = () -> 42; // 高频调用时有额外开销

        // ========== BiConsumer：Map.forEach 的标准姿势 ==========
        Map<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 90);
        scores.put("Bob", 85);

        BiConsumer<String, Integer> print = (name, score) ->
                System.out.println(name + " => " + score);
        scores.forEach(print);
        // 输出: Alice => 90
        //       Bob => 85
    }
}
```

> ### 💡 新人小结：变体是「不同规格的快递箱」
>
> - 小箱子（`IntSupplier`）装小件（int），没必要塞进大箱子（`Supplier<Integer>`）再拆 —— 避免装箱
> - 双格箱（`BiConsumer`）一次装两样 —— Map 的 key 和 value
>
> **一句话总结：变体接口 = 按内容物规格定制的包装箱，选对箱子就是省运费（性能）。**

---

## 官方 / 社区实践

Supplier 和 Consumer 不是孤立的语法糖，它们是 JDK API 的「接口语言」，大量核心 API 直接以它们为参数：

```java
// ========== 1. Optional：空安全的两大利器 ==========
Optional<User> user = findUser(42);

user.orElseGet(() -> createDefaultUser());   // Supplier：为空才生产，延迟兜底
user.ifPresent(u -> sendWelcomeMail(u));      // Consumer：有值才消费
user.ifPresentOrElse(
        u -> sendWelcomeMail(u),              // 有值：消费
        () -> log.warn("user not found"));     // 无值：兜底（Java 9+，无值侧是 Runnable）

// ========== 2. Stream：终端操作全是 Consumer 思想 ==========
List<String> names = List.of("Alice", "Bob");
names.stream()
     .filter(n -> n.startsWith("A"))  // Predicate
     .map(String::toUpperCase)        // Function
     .forEach(n -> System.out.println(n)); // Consumer：流水线终点

// ========== 3. 工厂与注册 API ==========
// Collectors.toMap 的 merge 参数：BiConsumer，冲突时如何合并
// HashMap.computeIfAbsent(key, k -> new ArrayList<>()) // Function 侧
// Objects.requireNonNull(obj, () -> "msg不能为空")     // Java 8 优秀实践：
// ❌ 写法 verify(() -> "msg") 每次都拼字符串；Supplier 版本只在抛异常时才拼接

// ========== 4. 日志框架的延迟求值（社区惯用） ==========
// SLF4J 占位符 + Supplier 思想：debug 关闭时，拼接逻辑根本不执行
logger.debug("对象详情: {}", () -> expensiveToString(obj)); // log4j2 支持 Supplier 重载
```

**官方 API 速查表（面试常考）：**

| API | 参数类型 | 作用 |
|-----|---------|------|
| `Optional.orElseGet(Supplier)` | `Supplier<? extends T>` | 为空时才生产默认值 |
| `Optional.ifPresent(Consumer)` | `Consumer<? super T>` | 有值才消费 |
| `Stream.forEach(Consumer)` | `Consumer<? super T>` | 遍历消费每个元素 |
| `Stream.generate(Supplier)` | `Supplier<T>` | 无限流的数据源 |
| `Collectors.toMap(..., BiConsumer)` | merge 函数 | key 冲突合并策略 |
| `Map.forEach(BiConsumer)` | `BiConsumer<K,V>` | 遍历键值对 |
| `Logger.debug(String, Supplier)` | `Supplier<String>` | log4j2 延迟拼接日志 |
| `Objects.requireNonNull(obj, Supplier<String>)` | `Supplier<String>` | 延迟生成错误信息 |

---

## 高频问题与踩坑排查（Q&A）

以下是官方邮件列表、Stack Overflow、各大社区中关于这两个接口**出镜率最高**的问题，附原因分析与解决方案。

### Q1：`orElse` 和 `orElseGet` 有什么区别？为什么大对象要用 `orElseGet`？

**现象**：无论 Optional 是否有值，`orElse` 里的对象「都被创建了」。

```java
User u = findUser(42)
        .orElse(createDefaultUser());        // ❌ 100% 执行 createDefaultUser
User u2 = findUser(42)
        .orElseGet(() -> createDefaultUser()); // ✅ 只有为空才执行
```

**原因分析**：`orElse` 接收的是**已经算好的值**（严格求值，进入方法前必执行）；`orElseGet` 接收 `Supplier`，只在需要时才调用 `get()`。

**解决方案**：

| 场景 | 推荐写法 |
|------|---------|
| 默认值是常量/字面量（`0`、`""`、枚举） | `orElse(DEFAULT)`，更简洁 |
| 默认值需要创建对象/查库/计算 | `orElseGet(() -> build())`，避免无谓开销 |

### Q2：为什么我的 Lambda 里修改外部局部变量编译报错？

**现象**：`Local variable num defined in an enclosing scope must be final or effectively final`。

```java
int count = 0;
Consumer<String> bad = s -> count++; // ❌ 编译错误
```

**原因分析**：Lambda 捕获的是变量的**副本**（值捕获，不是引用捕获）。如果允许修改，Lambda 内改的是副本，外部看不到，语义会错乱，因此 Java 强制要求捕获变量「事实上 final」。注意：**对象引用的字段不受此限**。

**解决方案**：

```java
// ========== 方案 1：用可变容器（数组/Atomic 类） ==========
int[] count = {0};
Consumer<String> ok1 = s -> count[0]++;        // 数组技巧（不优雅但能用）

// ========== 方案 2（推荐）：改用 Stream 的 count / collect ==========
long n = list.stream().filter(s -> s.length() > 3).count();

// ========== 方案 3：单线程场景用 AtomicInteger ==========
java.util.concurrent.atomic.AtomicInteger ai = new AtomicInteger();
Consumer<String> ok3 = s -> ai.incrementAndGet();
```

### Q3：`forEach` 里用 `continue` / `break` / `return` 为什么不生效或编译不过？

**现象**：

```java
list.forEach(s -> {
    if (s.isEmpty()) continue; // ❌ 编译错误：Lambda 中不能用 continue/break
    process(s);
});
```

**原因分析**：`continue`/`break` 属于循环语法，而 Lambda 是「传给 `forEach` 的一个 Consumer」，它本身不是循环控制者——循环在外层 `forEach` 的实现里。`return` 在 Lambda 里**只表示结束当前这一次 `accept` 调用**，相当于 continue，无法终止整个遍历。

**解决方案**：

| 需求 | 正确姿势 |
|------|---------|
| 跳过部分元素 | Lambda 内 `if (cond) return;` 或先 `.filter()` |
| 提前终止遍历 | 改用 `for` 循环，或换 `Stream.anyMatch / takeWhile`（Java 9+） |
| 遍历 + 条件处理 | `.stream().filter(...).forEach(...)` 表达意图更清晰 |

### Q4：`Supplier.get()` 每次调用结果一样吗？

**现象**：以为 `Supplier` 是「缓存的值」，结果每次 `get()` 都重新执行，甚至重复查了数据库。

**原因分析**：`Supplier` 只是「生产逻辑的包装」，**没有任何缓存语义**，`get()` 调 N 次就执行 N 次。

**解决方案**：需要缓存就在 Lambda 里自己包（或在调用侧只 `get()` 一次）：

```java
Supplier<List<User>> dbQuery = () -> userDao.findAll();
List<User> a = dbQuery.get(); // 第 1 次查询
List<User> b = dbQuery.get(); // 第 2 次查询！两次结果可能不同

// ✅ 需要单例语义：惰性初始化 + 缓存
// 单线程可用简单 memoization；多线程用 Guava Suppliers.memoize(...)
com.google.common.base.Supplier<List<User>> cached =
        com.google.common.base.Suppliers.memoize(() -> userDao.findAll());
```

### Q5：`andThen` 链中前一个 Consumer 抛异常，后面的还执行吗？

**现象**：链式消费中途抛异常，「后面半段」没有执行，也没有任何回滚。

**原因分析**：`andThen` 的实现是顺序调用 `accept(t); after.accept(t);`——前者抛异常，后者根本走不到；且 Consumer 没有「失败补偿」设计。

**解决方案**：

```java
Consumer<String> c1 = s -> { throw new IllegalStateException("boom"); };
Consumer<String> c2 = s -> System.out.println("c2");

// ❌ c2 永远不会执行
// c1.andThen(c2).accept("x");

// ✅ 需要隔离失败：自己包 try-catch 再组合
Consumer<String> safeC1 = s -> {
    try { c1.accept(s); }
    catch (Exception e) { System.err.println("c1 失败: " + e.getMessage()); }
};
safeC1.andThen(c2).accept("x");
// 输出: c1 失败: boom
//       c2
```

### Q6：`Supplier<Integer>` 和 `IntSupplier` 随便选一个行不行？

**现象**：高频调用（循环百万次）时，`Supplier<Integer>` 版本明显更慢，产生大量 `Integer[]` 垃圾。

**原因分析**：`Integer` 是包装类，`int -> Integer` 的自动装箱在每次 `get()` 时都会发生（超出 `IntegerCache` 范围时必然新建对象），GC 压力随之而来。

**解决方案**：原始类型场景固定使用 `IntSupplier` / `LongSupplier` / `DoubleSupplier`；批量数据用 `IntStream`。低频调用（如配置兜底）则无需纠结。

### Q7：方法引用 `Class::new` 和 Lambda `() -> new User()` 完全等价吗？

**现象**：想用 `User::new` 做 Supplier，但 `User` 有多个构造器，不知道匹配哪个。

**原因分析**：方法引用的匹配规则是**按目标函数接口的签名选构造器/方法**。赋给 `Supplier<User>` 时匹配无参构造器；赋给 `Function<String,User>` 时匹配 `User(String)`。

```java
Supplier<User> s1 = User::new;              // 匹配 User()
Function<String, User> f1 = User::new;      // 匹配 User(String)
```

**解决方案**：记住「**签名由目标类型决定**」即可；若类没有对应签名的构造器，编译器会直接报错，不会错配。

---

## 要点总结

1. **Supplier = 生产者**（`T get()`），核心价值是**延迟执行**；**Consumer = 消费者**（`void accept(T)`），核心价值是**把处理逻辑参数化（回调标准化）**。
2. `orElse` 立即求值、`orElseGet` 延迟求值——默认值有开销时永远选 `orElseGet`。
3. Lambda 捕获的局部变量必须是 effectively final；需要计数/累积时改用 Stream 聚合或 `Atomic` 类。
4. Lambda 内的 `return` 只跳过当前元素，不能 `break/continue`；需要提前终止就回到 `for` 或用 `Stream.takeWhile`。
5. `Supplier` 没有缓存语义，`get()` 调几次执行几次；原始类型用 `IntSupplier` 等变体避免装箱开销。

---

> ### 💡 新人小结：Supplier 与 Consumer 学完了，记住这 3 点
>
> 1. **它们是「动作的快递单」**——Supplier 只出货（`get()`），Consumer 只收货（`accept()`），签名即格式，Lambda 即内容。
> 2. **延迟执行是 Supplier 的灵魂**——凡是「可能不需要执行的开销」（默认值、日志拼接、错误信息），都值得问一句：要不要换成 Supplier？
> 3. **看到 `forEach`、`ifPresent`、`orElseGet`，脑子里要立刻映射到 Consumer / Supplier**——JDK 的新 API 都在说这门「函数接口语言」，学会它就读懂了半个现代 Java。
