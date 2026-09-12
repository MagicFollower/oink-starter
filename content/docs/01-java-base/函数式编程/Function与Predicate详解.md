---
title: Function 与 Predicate 详解 —— 转换与判断的函数接口
description: 从写死的转换逻辑与 if 条件爆炸出发，讲透 Function/Predicate 的签名设计、变体家族命名规律、andThen/compose 与 and/or/negate 组合器，附命令式与函数式的演进对比。
weight: 3
---

# 为什么需要 Function 和 Predicate？

想象你经营一个快递中转场。生意做大了以后，两个岗位的需求暴涨：

- **转运岗**：进站一个包裹，出站时变成了另一个包裹——贴新面单、换外箱、合并订单。**进什么型、出什么型，不同线路完全不同**。
- **安检岗**：检查一个包裹，给出「放行 / 扣下」的结论。**检查标准经常变**——今天查易碎品，明天查超重，后天两个标准一起查。

在 Java 里，这两类需求对应两种写死代码的痛：

**痛点一：转换逻辑写死，无法复用。**

```java
// ========== Java 8 之前：每换一种转换就要复制一个方法 ==========
static List<String> extractUserNames(List<User> users) {
    List<String> names = new ArrayList<>();
    for (User u : users) { names.add(u.getName()); }   // 转换规则写死：取名字
    return names;
}

static List<Integer> extractUserAges(List<User> users) {
    List<Integer> ages = new ArrayList<>();
    for (User u : users) { ages.add(u.getAge()); }     // 又复制一遍，只改了一行
    return ages;
}
```

方法骨架 100% 相同，只有「转换规则」一行不同——但 Java 8 之前，**规则本身无法作为参数传递**。

**痛点二：判断条件爆炸。**

```java
// ========== Java 8 之前：条件一多，if 组合指数级增长 ==========
if (pkg.getWeight() <= 20 && pkg.isFragile() == false && pkg.getRegion().equals("华东")) { ... }
// 明天产品说「易碎品但轻于 5kg 的也放行」—— 再写一个 if？还是把老 if 改了？
```

Java 8 的解法：`Function<T,R>` 把「转换规则」抽象成类型，`Predicate<T>` 把「判断规则」抽象成类型——并且两者都自带**组合器**，规则可以像积木一样拼装。

| 对比项 | Java 8 之前 | Java 8 之后（Function / Predicate） |
|--------|------------|-------------------------------------|
| 转换规则 | 写死在方法体里 | `Function<T,R>` 参数传入 |
| 判断规则 | 写死在 `if` 里 | `Predicate<T>` 参数传入 |
| 复用方式 | 复制粘贴改一行 | 同一实例多处引用、自由组合 |
| 可测试性 | 必须跑完整方法 | 规则可独立单元测试 |

> ### 💡 新人小结：Function 和 Predicate 管什么？
>
> 四大函数接口里，上一篇的 Supplier/Consumer 只管「给」和「收」，而这两位管「加工」：
> - `Function<T,R>` 是**转运站**：拆箱重组，进来 T 出去 R
> - `Predicate<T>` 是**安检员**：只检查不改造，放行 true / 扣下 false
> - 组合器（`andThen`/`compose`/`and`/`or`）是多级转运、多重安检的**交接单**
>
> **一句话总结：Function 负责「变」，Predicate 负责「断」，组合器让它们变成流水线。**

**学习路线图**

```
签名与变体 → Function 组合 → Predicate 组合 → 演进对比 → 官方实践 → Q&A
四类金刚     andThen/compose  and/or/negate    循环 vs 组合   JDK 怎么用   出错怎么办
```

**本文涉及的专有名词**（先解释后使用；「目标类型」「effectively final」见《Lambda表达式详解》）：

| 术语 | 全称 | 含义（用自己的话） | 在本文中的角色 |
|------|------|--------------------|----------------|
| 高阶函数 | higher-order function | 接收函数作参数、或返回函数的方法 | 接收 Function/Predicate 的方法都是高阶函数 |
| 组合器 | combinator | 把多个函数拼成一个新函数的方法 | andThen/compose/and/or/negate 全是组合器 |
| 短路求值 | short-circuit evaluation | `&&`/`||` 左边能定结果就不再算右边 | Predicate 组合沿用了这一行为 |
| 装箱 | boxing | 原始类型 int 与包装对象 Integer 的自动互转 | 引出「为什么要有 ToIntFunction 变体」 |

---

## 核心概念：两个签名，两种使命

| 接口 | 抽象方法 | 语义 | 中转场类比 |
|------|---------|------|-----------|
| `Function<T,R>` | `R apply(T t)` | 收 T，加工，还你 R | 转运站：拆箱重组 |
| `Predicate<T>` | `boolean test(T t)` | 收 T，判断，回 true/false | 安检员：放行或扣下 |

两者都是 `java.util.function` 包的标准函数接口（SAM 接口，可用 Lambda 实例化——见《Lambda表达式详解》）。

```java
// ========== Function：一进一出 ==========
Function<String, Integer> toLength = s -> s.length();
Integer len = toLength.apply("包裹ABC");          // 输出: 5

// ========== Predicate：一进一断 ==========
Predicate<String> isHeavy = s -> s.length() > 10;
boolean gate = isHeavy.test("大件包裹-超重疑似-XXL");  // 输出: true
```

**参数解释**：

| 泛型位 | 含义 | 类比 |
|--------|------|------|
| `T`（Function 入参 / Predicate 入参） | 进站包裹类型 | 收什么货 |
| `R`（Function 出参） | 出站包裹类型 | 发什么货 |
| `boolean`（Predicate 返回） | 安检结论 | 放行 true / 扣下 false |

---

## 主体内容

### Function：转换规则作为参数

先解决痛点一——「提取字段」这个动作本身参数化：

```java
public class ExtractDemo {
    // ✅ 一个方法吃下所有「列表转换」需求：规则由调用方给
    static <T, R> List<R> mapAll(List<T> source, Function<T, R> mapper) {
        List<R> result = new ArrayList<>();
        for (T item : source) {
            result.add(mapper.apply(item));   // 转换规则不再写死
        }
        return result;
    }

    public static void main(String[] args) {
        List<User> users = new java.util.ArrayList<>(java.util.Arrays.asList(new User("阿明", 26), new User("小陈", 19)));

        List<String> names = mapAll(users, u -> u.getName());   // 取名字
        List<Integer> ages  = mapAll(users, u -> u.getAge());   // 取年龄，同一个方法
        System.out.println(names);   // 输出: [阿明, 小陈]
        System.out.println(ages);    // 输出: [26, 19]
    }
}
```

`mapAll` 是一个**高阶函数**：它的形参 `mapper` 本身是函数。从此「转换规则」从方法体里解放出来，变成可以传递、可以复用、可以测试的值。

### 变体家族：命名规律比死记硬背重要

`java.util.function` 里 Function 系有 20+ 个变体，全部遵循两条命名规律：

| 命名模式 | 含义 | 典型接口 | 签名 |
|----------|------|---------|------|
| `IntFunction<R>` | **入参**是原始类型 | `IntFunction<R>` | `R apply(int)` |
| `ToIntFunction<T>` | **返回值**是原始类型 | `ToIntFunction<T>` | `int applyAsInt(T)` |
| `XxxOperator` | 入参出参**同为**同一类型 | `UnaryOperator<T>`、`IntBinaryOperator` | `T apply(T)` / `int applyAsInt(int, int)` |
| `Bi` 前缀 | **两个**入参 | `BiFunction<T,U,R>` | `R apply(T, U)` |
| `Unary`/`Binary` | 一个 / 两个同型入参 | `UnaryOperator<T>`、`BinaryOperator<T>` | `T apply(T)` / `T apply(T,T)` |

```java
// ========== 为什么要有原始类型特化变体？避免装箱 ==========
Function<Integer, Integer> boxed      = n -> n + 1;      // Integer 进 Integer 出，每步装箱拆箱
IntUnaryOperator unboxed = n -> n + 1;                   // int 进 int 出，无装箱
IntUnaryOperator chain = unboxed.andThen(unboxed).andThen(unboxed);  // 组合器照常可用
System.out.println(chain.applyAsInt(1));                 // 输出: 4
```

**参数解释**：`boxed` 版本每次 `apply` 都发生 Integer 对象创建与回收（装箱），数据量大时 GC 压力显著；`IntUnaryOperator` 全程操作栈上的 int。性能话题展开见《数值流与原始类型特化》。

> ### 💡 新人小结：变体命名像什么？
>
> 变体命名像快递面单的**规格编码**：
> - `Int` 开头 = 入口通道是散货（原始类型） —— `IntFunction<R>`
> - `ToInt` 开头 = 出口通道是散货 —— `ToIntFunction<T>`
> - `Bi` = 双入口通道 —— `BiFunction<T,U,R>`
> - 看懂编码就不用背清单 —— 42 个接口全部可推导
>
> **一句话总结：见名知义——前缀管入口，To 中缀管出口，Bi 管参数个数。**

### andThen 与 compose：最容易记反的两个组合器

Function 的两个组合器都生成「先 A 后 B」的链，区别只在**谁先谁后**：

```java
public class ComposeDemo {
    public static void main(String[] args) {
        Function<Integer, Integer> multiply10 = n -> n * 10;
        Function<Integer, Integer> add5 = n -> n + 5;

        // andThen：「我做完，然后（andThen）你做」 —— 先乘后加
        int r1 = multiply10.andThen(add5).apply(2);
        System.out.println(r1);   // 输出: 25   (2 * 10) + 5

        // compose：「compose(你)——你先做，我来收尾」 —— 先加后乘
        int r2 = multiply10.compose(add5).apply(2);
        System.out.println(r2);   // 输出: 70   (2 + 5) * 10
    }
}
```

**记忆口诀**：

```text
a.andThen(b).apply(x)  ==  b.apply(a.apply(x))     —— 从左往右读，执行顺序与书写顺序一致
a.compose(b).apply(x)  ==  a.apply(b.apply(x))     —— compose 的参数先执行
```

**参数解释**：

| 组合器 | 调用形式 | 实际执行顺序 |
|--------|---------|-------------|
| `andThen` | `f.andThen(g)` | 先 `f` 后 `g` |
| `compose` | `f.compose(g)` | 先 `g` 后 `f`（链上从右往左） |

**注意**：组合不会改变原函数——`f.andThen(g)` 返回**新的**函数对象，`f` 与 `g` 本身不变。这让同一条基础规则能安全地拼出多条业务链。

```text
基础规则：称重 → 计价 → 贴单（三个 Function 变量）
        ↓ 组合
华东线：称重.andThen(计价).andThen(贴单)
加急线：称重.andThen(计价.andThen(贴单)).andThen(打标"加急")
```

### Predicate：判断规则作为参数 + 三件组合套件

解决痛点二——条件不再写死在 `if` 里，还能自由拼装：

```java
public class PredicateDemo {
    public static void main(String[] args) {
        Predicate<String> notEmpty  = s -> !s.isEmpty();
        Predicate<String> shortName = s -> s.length() <= 10;
        Predicate<String> fromEast  = s -> s.contains("东");

        // and：两个都要满足 —— 且不满足第一个时第二个不再执行（短路）
        Predicate<String> valid = notEmpty.and(shortName);
        // or：满足其一即可
        Predicate<String> urgent = shortName.or(fromEast);
        // negate：取反
        Predicate<String> reject = valid.negate();

        System.out.println(valid.test("华东-包裹A"));      // 输出: true
        System.out.println(urgent.test("超长包裹名称-来自华南")); // 输出: true（or 生效）
        System.out.println(reject.test("华东-包裹A"));      // 输出: false
    }
}
```

**参数解释**：

| 组合器 | 语义 | 短路行为 | 对应运算符 |
|--------|------|---------|-----------|
| `other.and(this→other)` | 两个都真才真 | 左侧为 false 时右侧不执行 | `&&` |
| `or` | 一个真即真 | 左侧为 true 时右侧不执行 | `\|\|` |
| `negate` | 取反 | 无 | `!` |

**注意空指针陷阱**：`notEmpty.and(shortName)` 中若包裹为 null，`s.isEmpty()` 直接 NPE——组合器不会帮你判空，必要时先加 `Objects::nonNull` 条件。

```java
Predicate<String> safe = s -> s != null && !s.isEmpty();  // ✅ 判空放最前
```

> ### 💡 新人小结：组合器像什么？
>
> `and`/`or`/`negate` 像**多级安检口**的合并规则：
> - `and` = 连过两道安检门都放行才放行 —— 任一门扣下就走不到下一道
> - `or` = 走任意一道 VIP 通道即可 —— 第一道过了就不再看第二道
> - `negate` = 把「白名单」翻成「黑名单」 —— 同一批包裹，结论反转
>
> **一句话总结：单个 Predicate 是一道安检门，组合器把门串成安检流程，且全程短路。**

### 演进对比：命令式嵌套 vs 函数组合

统一场景：把一批包裹名中「名称超过 3 个字符」的转换成 `PKG-大写` 格式。

**旧方案：转换与判断耦合在一个循环里。**

```java
// ========== 旧方案（Java 8 之前惯用写法） ==========
static List<String> process(List<String> packages) {
    List<String> result = new ArrayList<>();
    for (String s : packages) {
        if (s.length() > 3) {                       // 判断规则写死
            result.add("PKG-" + s.toUpperCase());   // 转换规则写死
        }
    }
    return result;
}
```

**当前方案：规则独立成值，按需组装。**

```java
// ========== 当前方案（Java 8） ==========
Predicate<String> cond      = s -> s.length() > 3;
Function<String, String> fmt = s -> "PKG-" + s.toUpperCase();

List<String> result = packages.stream()
        .filter(cond)
        .map(fmt)
        .collect(Collectors.toList());
// Stream 细节见后续篇章；此处关注「规则成为一等公民」
```

**对比分析表**：

| 对比维度 | 旧方案：for 循环耦合 | 当前方案：函数组合 |
|----------|---------------------|-------------------|
| 写法差异 | 判断与转换揉在同一个循环体，改需求要改方法 | 各自独立为 `Predicate`/`Function` 变量，按需拼装 |
| 行为差异（复用） | 换条件/换格式必须复制整个方法 | 同一 `cond`/`fmt` 可服务多个流程，可再组合 |
| 行为差异（测试） | 只能构造完整入参跑整个方法 | `cond`、`fmt` 可各自单元测试 |
| 迁移成本 | — | 需要团队理解目标类型、组合顺序与短路语义 |
| 旧方案适用场景 | 一次性脚本、规则永不复用的简单逻辑 | 业务规则会被复用、组合、独立测试的任何正式代码 |

结论：函数组合把「业务规则」从「流程骨架」中剥离——这正是命令式与函数式的分水岭，也是 Stream 能声明式表达数据处理的前提。

---

## 官方 / 社区实践

JDK 中 `Function`/`Predicate` 的应用密度极高，看四个标配位置：

```java
// ========== 1. Stream：map 收 Function，filter 收 Predicate ==========
List<String> upper = names.stream().map(s -> s.toUpperCase()).collect(Collectors.toList());
List<String> short = names.stream().filter(s -> s.length() < 5).collect(Collectors.toList());

// ========== 2. Comparator.comparing：按「提取器函数」排序 ==========
users.sort(Comparator.comparing(u -> u.getAge()));      // Function<User, Integer> 决定按什么比

// ========== 3. Map.computeIfAbsent：键缺位时用 Function 补算 ==========
Map<Character, List<String>> byInitial = new HashMap<>();
for (String name : names) {
    byInitial.computeIfAbsent(name.charAt(0), k -> new ArrayList<>()).add(name);
}

// ========== 4. Optional：map 收 Function、filter 收 Predicate（详见《Optional优雅处理空值》） ==========
Optional.of(pkg).map(Package::getWeight).filter(w -> w <= 20).orElseThrow(IllegalStateException::new);
```

**参数解释**：

- `Comparator.comparing(Function)`：比较器不再手写 `compare`，只声明「按哪个字段比」——Function 在此叫**键提取器**。
- `computeIfAbsent(K, Function<K,V>)`：懒加载惯用法，键不存在时才调用 Function 计算，常用于构建多值 Map。
- `Optional.map/filter`：与本文同名的组合语义，把空值处理也纳入函数式轨道。

社区实践（Spring、MyBatis-Plus 等）大量以 Function 作为「字段解析器」参数，替换反射按名字取值的字符串方案——行为可编译期检查，是函数接口价值的直接体现。

---

## 高频问题与踩坑排查（Q&A）

**Q1：andThen 和 compose 总记反，有没有彻底的记法？**

记住调用者视角的读法：`a.andThen(b)` 读作「a 做完**然后** b 做」，书写顺序 = 执行顺序；`a.compose(b)` 读作「a **合成** b 的结果」，即 b 的输出才是 a 的输入，b 先跑。拿 `multiply10`/`add5` 的 `25 vs 70` 案例跑一遍，肌肉记忆立刻建立。

**Q2：组合链抛异常，整个链的行为是什么？**

`andThen` 链上任何一环抛出异常，链条立即中断，异常沿调用栈向上传播——不存在「跳过坏环节继续跑」的容错语义。需要容错要自己在 Lambda 体内 try-catch（系统化方案见《自定义函数接口与高阶函数》）。

**Q3：Function<T,R> 声明为 `Function<? super T, ? extends R>` 是什么意思？**

接口内部方法（如 `Function.andThen`、`Comparator.comparing`）的泛型常这么写：`? super T` 表示「能吃下 T 的父类函数都行」（安检员会查大件就会查小件），`? extends R` 表示「产出 R 的子类也算数」。这是泛型通配符的 PECS 原则，深入展开见《泛型与反射》板块。

**Q4：Predicate 组合是短路吗？性能上要注意什么？**

是短路求值，行为与 `&&`/`||` 完全一致。性能要点：把**最可能先失败（and）/先成功（or）**的条件放在链条前面，让后续昂贵计算尽量不执行。

**Q5：什么时候不该用 Function 泛型版，要用 IntFunction 等特化版？**

泛型版只能持有包装类型，核心热点路径（大集合逐元素转换、数值计算循环）的装箱开销不可忽视。经验法则：数据量上千且纯数值运算，直接用 `ToIntFunction`/`IntUnaryOperator` 等特化版，或等价的数值流（见《数值流与原始类型特化》）；普通业务对象转换用泛型版即可。

---

## 要点总结

1. **Function<T,R> 管「变」，Predicate<T> 管「断」**——分别把转换规则与判断规则从代码里解放成可传递的值。
2. **变体看名知义**：`Int` 前缀管入口特化，`ToXxx` 管出口特化，`Bi` 管双参，`Operator` 管同型出入——42 个接口不必背。
3. **andThen 从左到右，compose 从右到左**；组合产生新函数，原函数不变。
4. **Predicate 的 and/or/negate 等价 `&&`/`||`/`!`**，全程短路；判空逻辑自己放在最前。
5. **函数组合是 Stream 声明式风格的根基**：map/filter 的形参就是它们，规则独立后流程只剩搭积木。

> ### 💡 新人小结：Function 与 Predicate 学完了，记住这 3 点
>
> 1. **转运站（Function）管重组，安检员（Predicate）管放行** —— 一个出值，一个出真假
> 2. **交接单（组合器）让岗位串成流水线** —— andThen 顺着读，compose 倒着跑
> 3. **规则独立后才能复用与单测** —— 还在 for 循环里写死 if + 转换，就是没毕业
>
> **一句话总结：把规则变成值，流程就变成了搭积木——这是「函数式」三个字的第一次兑现。**
