---
title: Stream 排序反转实战问题归档 —— 一行 sorted 引发的 NPE 与方案选型
weight: 14
description: 一段含 null 的 List 交给 stream().sorted(Comparator.comparing(x->x.toString()).reversed()) 的真实排障记录：为什么 NPE 发生在 sorted 而不是 forEach、toString 为何歪打正着、ObjectUtils.compare 如何让 null 视作最大、排序后反转为什么应该反转比较器而不是反转数据（稳定性陷阱），以及完整的语义矩阵与方案总评。
---

这是本系列第一篇**实战问题归档**：它不是新知识点教程，而是一次真实排障的完整记录——问题代码、易错点剖析、处理方案、方案对比与沉淀清单。前 13 篇讲的是函数式编程的「应然」，这一篇记录的是实战中的「实然」。

## 一、原始问题：一段跑不通的排序

某业务里有一个可能含 `null` 的字符串列表，想倒序打印，写出了这样一行代码：

```java
List<String> strings = Arrays.asList("hello", "world", null);

strings.stream()
       .sorted(Comparator.comparing(x -> x.toString()).reversed())
       .forEach(System.out::println);
```

运行结果：**`NullPointerException`，一行都没打印**。下面按排障顺序拆解三个易错点。

### 易错点 1：NPE 发生在 sorted 阶段，forEach 根本执行不到

`Comparator.comparing(x -> x.toString())` 的 keyExtractor 会作用于**每一个**参与比较的元素。列表里的 `null` 一进入 `sorted` 内部的两两比较，`null.toString()` 直接抛 NPE——此时流还在中间操作阶段，`forEach` 一个元素都没收到。

由此得出第一条结论：**在 forEach 外面 try-catch 是救不了这种 NPE 的**（它根本不是 forEach 抛的），修复点必须落在**比较器本身**。

堆栈也印证这一点——顶帧不在业务代码，而在 `Comparator` 的合成 lambda 里（不同 JDK 版本帧名略有差异，下面是示意）：

```text
Exception in thread "main" java.lang.NullPointerException
    at java.util.Comparator$$Lambda$5/1831932724.compare(Unknown Source)
    at java.util.TimSort.countRunAndMakeAscending(TimSort.java:355)
    ...
```

看到顶帧落在比较器实现里、下一帧是排序算法，修复点自然就定位到了比较器。

### 易错点 2：toString() 是歪打正着

`sorted(Comparator.comparing(x -> x.toString()).reversed())` 里的 lambda 参数 `x` 是什么类型？由于链上隔着 `.reversed()`，`sorted` 的目标类型传不进去，隐式 lambda 的参数被推断为 `Object`——`x.toString()` 恰好是 `Object` 的方法，所以**碰巧编译通过**。验证方法：换成 `x -> x.length()` 立刻编译失败。

而 `String` 本身就是 `Comparable<String>`，`toString()` 这一步毫无意义：它把「按字符串自然序」写成了「按 toString 结果序」，多绕一步还引入了 NPE。正确的最小写法本来是：

```java
.sorted(Comparator.<String>naturalOrder().reversed())   // 想要倒序，直接自然序反转
```

### 易错点 3：reversed() 与 null 语义的组合陷阱

修复 null 不能只想着「过滤掉再说」——如果 null 是合法业务值（如「未填写」），就要让比较器自己容忍它。而一旦引入「null 视作最大」的语义，又和 `.reversed()` 产生了组合问题（后文语义矩阵详述）。

## 二、方案一：ObjectUtils.compare 让 null 视作最大

commons-lang3 的 `ObjectUtils.compare(c1, c2, nullGreater)` 提供了 null 安全的两两比较，null 语义由第三参决定（双 null 恒返回 0）：

| 调用 | 返回 | 说明 |
|------|------|------|
| `compare(null, "a", true)` | `1` | nullGreater=true：null 视作更大 |
| `compare(null, "a", false)` | `-1` | nullGreater=false：null 视作更小 |
| `compare("a", "b", 任意)` | `a.compareTo(b)` | 非 null 走自然序 |
| `compare(null, null, 任意)` | `0` | 双 null 视为相等 |

基本修复（null 视作最大 + 升序 → null 排最后）：

```java
strings.stream()
       .sorted((a, b) -> ObjectUtils.compare(a, b, true))
       .forEach(System.out::println);
// 输出: hello → world → null
```

**注意不能写 `ObjectUtils::compare` 方法引用**——方法引用绑定的是二参重载（等价 `nullGreater=false`，null 视作最小、升序排最前），想传 `true` 必须用 lambda。

若要保留原始问题的**倒序**语义，把比较器提成变量再反转，null 会跟着翻到最前：

```java
Comparator<String> nullMax = (a, b) -> ObjectUtils.compare(a, b, true);
strings.stream().sorted(nullMax.reversed()).forEach(System.out::println);
// 输出: null → world → hello
```

### 语义矩阵：「null 视作最大」不等于「null 排最后」

这是整个问题里最容易糊的地方——**「视作最大/最小」是比较器的代数语义，「排最前/最后」是视觉结果，降序会把后者翻转**：

| 写法 | null 代数语义 | 字符串顺序 | null 视觉位置 |
|------|-------------|-----------|--------------|
| `(a,b) -> ObjectUtils.compare(a,b,true)` | null = 最大 | 升序 | 最后 |
| 同上 + `.reversed()` | null = 最大 | 降序 | **最前**（被反转） |
| `ObjectUtils::compare`（二参版） | null = 最小 | 升序 | 最前 |
| 同上 + `.reversed()` | null = 最小 | 降序 | **最后**（被反转） |

如果需求是「降序 + null 仍然垫底」，参数对调一步到位（升序比较器把 b 放第一参，等价于反转方向但 null 语义跟随位移）：

```java
strings.stream()
       .sorted((a, b) -> ObjectUtils.compare(b, a, true))
       .forEach(System.out::println);
// 输出: world → hello → null
```

### JDK 原生对照：不引依赖的等价写法

`ObjectUtils.compare` 的 null 分支与 JDK 组合器逐分支等价，可互相印证：

| ObjectUtils 写法 | JDK 等价写法 |
|------------------|--------------|
| `(a,b) -> ObjectUtils.compare(a,b,true)` | `Comparator.nullsLast(Comparator.naturalOrder())` |
| `ObjectUtils::compare`（二参） | `Comparator.nullsFirst(Comparator.naturalOrder())` |
| `(a,b) -> ObjectUtils.compare(b,a,true)` | `Comparator.nullsLast(Comparator.reverseOrder())` |

`nullsLast` 的 javadoc 原话是 considers null to be **greater** than non-null（null 视作大于非 null），且它的裁决优先级高于内部比较器——无论内部是升序还是降序，null 恒排末尾。

一句话记矩阵：**nullGreater 定代数语义，reversed 翻视觉位置；要钉死位置，nullsXxx 放最外层**。

## 三、方案二与延伸：排序后反转，有哪些方案、哪个最优

原始问题之外的追问：如果就是想要「排好序之后反转」，有哪些方案？

### 结论先行：把方向写进比较器，而不是反转数据

```java
// 降序 + null 垫底：不需要"先正序再反转"
strings.stream()
       .sorted(Comparator.nullsLast(Comparator.reverseOrder()))
       .forEach(System.out::println);
// 输出: world → hello → null
```

理由有三：**单遍**（流式管道不产生中间集合）；**稳定**（见下一节，这点最容易被忽视）；**意图直白**（「按降序排」读到即懂，「排完再翻过来」要读者心算）。

`.reversed()` 自身还有两个工程细节坑：

```java
// 坑 1：隐式 lambda 会被断链后推断为 Object，编译失败
strings.stream().sorted(Comparator.comparing(s -> s.length()).reversed());      // 编译错
// 修法：显式类型 / 类型见证 / 方法引用
strings.stream().sorted(Comparator.<String, Integer>comparing(s -> s.length()).reversed());
strings.stream().sorted(Comparator.comparingInt(String::length).reversed());    // 方法引用无此问题

// 坑 2：方法引用不能直接链式调 .reversed()
Comparator<String> c = ObjectUtils::compare;
strings.stream().sorted(c.reversed()).forEach(System.out::println);             // 先落变量再反转
```

### 稳定性陷阱：反转结果 ≠ 反向排序

`Collections.reverse` 是对结果的机械翻转；反向比较器则是**稳定排序**（JDK 官方保证 `Arrays.sort(Object[])` 与 TimSort 系排序稳定）。两者在「排序键相等的元素」上顺序不同：

```java
List<String> words = Arrays.asList("ab", "cd", "efg");   // "ab" 与 "cd" 等长

List<String> asc = words.stream()
        .sorted(Comparator.comparingInt(String::length))
        .collect(Collectors.toList());
// [ab, cd, efg] —— 稳定排序：等长元素保持原序
Collections.reverse(asc);
// [efg, cd, ab] —— cd 反到了 ab 前面（相等元素逆原序）

List<String> desc = words.stream()
        .sorted(Comparator.comparingInt(String::length).reversed())
        .collect(Collectors.toList());
// [efg, ab, cd] —— ab/cd 仍保持原序（稳定降序）
```

业务上要的通常是「**降序的稳定排序**」，而不是「升序结果的镜像」——用 reverse 会悄悄打乱相等元素的相对顺序，且极难被发现。这是「最优解选比较器反转」的深层原因。

### 结果集已生成的场合：反转数据的正当用法

如果 List 是排好的现成结果（来自外部接口、不可重排、或多处复用）：

```java
// 1. 原地翻转（对可变副本）
List<String> copy = new ArrayList<>(sorted);
Collections.reverse(copy);

// 2. 流内"收集即反转"一步到位
List<String> result = strings.stream()
        .sorted(Comparator.nullsLast(Comparator.naturalOrder()))
        .collect(Collectors.collectingAndThen(
                Collectors.toList(),
                l -> { Collections.reverse(l); return l; }));
// [hello, world, null] → [null, world, hello]（null 跑最前、相等元素逆原序）

// 3. 只读反向展示：视图，O(1) 不复制（Guava，可选引入）
List<String> view = com.google.common.collect.Lists.reverse(sorted);   // 随源列表联动
```

### null 组合矩阵（反转场景）

| 需求 | 最优写法 | 说明 |
|------|---------|------|
| 降序 + null 垫底 | `Comparator.nullsLast(Comparator.reverseOrder())` 或 `(a,b) -> ObjectUtils.compare(b, a, true)` | 不经反转直接达成 |
| 降序 + null 在首 | `nullsLast(naturalOrder())` 的 `.reversed()` | null 语义被外层反转 |
| 升序结果反着看 | `collectingAndThen` 或 `Collections.reverse` | 仅当结果已生成 |

口诀：**null 的视觉位置由最外层的 nullsXxx/比较器决定**——`nullsLast(...).reversed()` 里 `reversed()` 在外层，null 会跑位；要钉死 null 位置，就用 `nullsLast(反向比较器)` 一步写成。

### 方案总评

| 方案 | 遍历 | 中间集合 | 稳定性 | 适用场景 | 评价 |
|------|------|---------|--------|---------|------|
| 反向比较器直接排 | 1 | 无 | 相等元素保持原序 | 流式、就地排序 | **最优，默认选它** |
| `comparator.reversed()` | 1 | 无 | 保持原序 | 已有比较器想换向 | 优秀，注意推断坑 |
| `Collections.reverse` | +1 | 无（原地） | 逆原序 | 可变结果集临时反向 | 可用，语义弱一档 |
| `collectingAndThen` | 1 | 1 个结果集 | 逆原序 | 流内一步收集 | 优雅，注意 null 跑位 |
| Guava `Lists.reverse` | O(1) 视图 | 无 | 视图随源 | 只读反向展示 | 依赖取舍问题 |

## 四、变体实战：对象按字段排序，字段为 null

原始问题说的是「元素本身为 null」，实战中更高频的变体是「**对象非 null，但排序字段为 null**」——比如订单按支付时间排序，未支付订单的 `payTime` 是 null：

```java
// 极简示意类（省略构造器入参与 toString）
static class Order {
    final String no;
    final LocalDateTime payTime;   // null 表示未支付
    Order(String no, LocalDateTime payTime) { this.no = no; this.payTime = payTime; }
    LocalDateTime getPayTime() { return payTime; }
}

List<Order> orders = Arrays.asList(
        new Order("A002", LocalDateTime.of(2026, 9, 12, 10, 0)),
        new Order("A001", null),                                          // 未支付
        new Order("A003", LocalDateTime.of(2026, 9, 11, 18, 30)));

// 错误直觉：comparing(Order::getPayTime) —— null 键走进 naturalOrder 的 compareTo 同样 NPE
// 正解：comparing 两参版，keyComparator 专管「键」的 null 与排序
orders.sort(Comparator.comparing(
        Order::getPayTime,
        Comparator.nullsLast(Comparator.naturalOrder())));   // 按支付时间升序，未支付垫底
```

**参数解释**：`comparing(keyExtractor, keyComparator)` 的第二个参数作用于**键**（`getPayTime()` 的返回值），`nullsLast(naturalOrder())` 负责键的 null 容错——这是 null 容错的第二条路，也是对象字段排序最常用的形态。时间字段的类型选择与格式化参见《DateTime 日期时间增强》。

| 写法 | 适用场景 | 注意 |
|------|---------|------|
| `comparing(Order::getPayTime, nullsLast(naturalOrder()))` | 单字段、键可能为 null | 首选，一行搞定 |
| 手写两段式 lambda（先判字段 null 再比较） | 多级排序、null 需要特殊业务语义 | 啰嗦但灵活 |
| 先 `filter(o -> o.getPayTime() != null)` 再排 | 未支付订单本就不该参与榜单 | 源头治理，同第一部分结论 |

### 多级排序：每级独立声明 null 语义

真实榜单往往不止一级：先按支付时间，平局再按单号。`thenComparing` 也有单参与两参（键 + 键比较器）两个形态，**null 容错在每一级独立声明，互不影响**：

```java
orders.sort(Comparator
        .comparing(Order::getPayTime,
                Comparator.nullsLast(Comparator.naturalOrder()))   // 一级：支付时间，null 垫底
        .thenComparing(o -> o.no, Comparator.reverseOrder()));     // 二级：单号倒序，平局垫底
// 输出顺序：A003(09-11 18:30) → A002(09-12 10:00) → A001(null 未支付垫底)
```

一个精细的类型推断差异值得注意：**首级 `comparing` 的 T 未绑定，隐式 lambda 会推断失败；而后级 `thenComparing` 的 T 已由前级确定，`o -> o.no` 可以直接写**——同样是隐式 lambda，位置不同推断能力不同。

`thenComparing` 共有三个重载：接比较器、接键提取器、接「键提取器 + 键比较器」，多级场景下每一级的 null 语义都像第一部分那样独立可控——这正是「nullsXxx 放最外层」口诀在多级世界的版本：**每一级就是一个完整的比较器世界**。

### `.reversed()` 在多级链上的位置：反转整链还是只反一级

最后一个高频易错点：`.reversed()` 是**整链反转**，而 `Comparator.reverseOrder()` 是**单级反转**——

```java
Comparator.comparing(Order::getPayTime,
                Comparator.nullsLast(Comparator.naturalOrder()))
          .thenComparing(o -> o.no, Comparator.reverseOrder());   // 只二级倒序：时间升 → 单号倒
// 若再链尾追加 .reversed() 则整链反转，所有级别一起翻
```

| 写法 | 反转范围 | 效果 |
|------|---------|------|
| 某级的键比较器写成 `reverseOrder()` | 仅该级 | 一级升序、二级倒序 |
| 链尾追加 `.reversed()` | 整个比较器 | 全部级别一起翻 |
| 中间某级包 `.reversed()` | 该级及其后已链的级别 | 极易写错，不推荐 |

想要「一级倒序、二级升序」，不要写 `reversed()`——把一级的 keyComparator 换成 `reverseOrder()`。多级链上 `.reversed()` 放错位置，每一级方向全变，且编译器不给任何提示。

## 五、问题复盘与检查清单

### 复盘表：问题 → 根因 → 处理 → 沉淀

| 现象 | 根因 | 处理 | 沉淀 |
|------|------|------|------|
| sorted 阶段 NPE | keyExtractor 作用于 null 元素 | 比较器改用 null 容错比较 | NPE 修复点在比较器层，包 forEach 无效 |
| toString() 多余 | 隐式 lambda 被推断为 Object | String 天然 Comparable，直接自然序 | 链式 `.reversed()` 会切断目标类型推断 |
| null 位置反直觉 | reversed 在外层翻转了 null 语义 | nullsLast(反向比较器) 一步写 | null 位置由最外层 nullsXxx 决定 |
| 相等元素顺序突变 | reverse 是机械翻转非稳定降序 | 用反向比较器排序 | 业务要的是稳定降序，不是升序镜像 |

### 下次遇到同类问题的检查清单

1. 列表可能含 null 吗？含 → 比较器必须 null 容错（`nullsLast/nullsFirst` 或 `ObjectUtils.compare` 三参版），且先确认 null 是脏数据还是合法业务值
2. null 是脏数据 → 源头 `filter(Objects::nonNull)` 最干净，比较器不用兜底；null 合法 → 把容错比较器提成 `static final` 常量复用，别在流里现写
3. 要降序？**直接用反向比较器**（`reverseOrder()` 或 `.reversed()`），不要先正序再 reverse——相等元素的顺序两者不同
4. 写 `.reversed()` 前检查：隐式 lambda 有没有显式类型？方法引用是不是先落了变量？
5. 想让 null 恒定垫底/置顶？检查 `nullsLast/nullsFirst` 是否在最外层——被 `reversed()` 包住就会跑位
6. 反转只是为了「取最大的前 N 个」？直接反向排 + `limit(N)`，把「反转整个结果集」这个概念删掉

### 沉淀为团队规约的三条建议

1. **null 容错比较器统一提常量**：项目内定义如 `Comparators.NULLS_LAST_NATURAL`，禁止各处现写匿名 lambda（口径不一、复查困难）
2. **外部输入禁赌默认序**：来自用户或第三方的数据，排序必须显式比较器（与解析必须显式格式同理）
3. **Code Review 三个检查点**：`comparing` 里带方法调用的 lambda（字段可能为 null 吗）、`reversed()` 前的类型推断链、`Collections.reverse` 是否破坏了稳定语义

## 六、补充 Q&A

**Q1：`ObjectUtils::compare` 为什么绑定了二参版？**

方法引用 `ObjectUtils::compare` 匹配 `Comparator<String>` 的 `compare(T, T)` 时只能选到二参重载；三参版多了 `boolean nullGreater`，签名对不上。想传 `true` 只能用 lambda。同类的 Hutool 工具是 `ObjectUtil`（无 s），也有 compare 方法但签名细节不同，使用前以官方文档为准。

**Q2：为什么不用 TreeSet 一劳永逸？**

`TreeSet`/`TreeMap` 同样吃比较器，null 容错语义一致；但集合天然**去重**——本文场景的列表排序不涉及去重诉求，用 TreeSet 会静默丢元素。另外自然序下 `TreeSet.add(null)` 同样抛 NPE（TreeMap 的 null key），换成 nullsLast 比较器才放行——语义坑与 Stream 排序同源。

**Q3：稳定性是所有排序都有的保证吗？**

只有声明稳定的排序才有：JDK 的 `Arrays.sort(Object[])`、`Collections.sort`、`List.sort`、Stream 的 `sorted`（对对象）都是稳定的（TimSort）；但 `Arrays.sort(int[])` 等基本类型双轴快排**不涉及稳定性**（基本类型没有「相等但可区分」的概念，也无从体现）。

**Q4：`comparing` 的第二参数是干什么的？**

`Comparator.comparing(keyExtractor, keyComparator)` 的 keyComparator 作用于**键**（keyExtractor 的返回值），它处理的是「对象非 null、但字段 null」——这正是第四部分变体的正解。与「元素本身为 null」是两个维度：后者要用 `nullsLast(comparing(...))` 把 nullsLast 包在整个比较器**外面**。两层 null，两层防线，别混用。

**Q5：parallelStream 下 sorted 还稳定吗？**

稳定且结果确定：并行流对**有序流**（List 这类）保持相遇顺序（encounter order），sorted 的输出与顺序流一致，只是排序内部并行化。

**Q6：`Arrays.asList` 出来的列表能用 `list.sort(...)` 吗？**

能用——它只是长度固定（不支持 add/remove），`set` 是允许的，而 `List.sort` 的默认实现正是「取出再 set 回去」。本文全程用 `stream().sorted()` 则完全不碰源列表。

**Q7：`comparing` 单参版为什么要求键实现 `Comparable`？**

它的签名是 `comparing(Function<? super T, ? extends U> keyExtractor)`，其中 `U extends Comparable<? super U>`——键类型必须能自我比较。键是自定义类且没实现 Comparable 时，单参版编译不过；此时改用两参版传入自定义 keyComparator 即可（第四部分变体的 nullsLast 写法正属此类）。

## 七、要点总结

1. **NPE 的修复点在比较器**：keyExtractor 作用于每个元素，含 null 列表用 `comparing(x -> x.toString())` 必炸；try-catch 包 forEach 无效
2. **链式 `.reversed()` 会切断类型推断**：隐式 lambda 参数退化为 Object（`toString()` 歪打正着能编译）；修法是显式类型、类型见证或方法引用
3. **「null 视作最大」≠「null 排最后」**：降序会翻转视觉位置；语义矩阵四象限要能默写
4. **排序后反转的最优解是反向比较器**：单遍、稳定、意图清晰；`Collections.reverse` 会把相等元素逆原序，两者不是一回事
5. **null 位置由最外层 nullsXxx 决定**：`nullsLast(反向比较器)` 钉死垫底；`nullsLast(...).reversed()` 会让 null 跑位
6. **先判断 null 的业务身份**：脏数据源头过滤，合法值比较器容错并提成常量；Top-N 场景反向排 + limit，删掉「反转」概念

### 本篇与系列的呼应

- 《Lambda表达式详解》：隐式 lambda 的目标类型推断规则——本篇坑 1 的底层机制
- 《函数式编程思想与常见陷阱》：null 容错与防御式思维的方法论源头
- 常用工具类板块《String与StringUtils对比实战》《Collections与CollectionUtils对比实战》：`ObjectUtils` 与 `CollectionUtils` 同族的 null 语义约定
- 《DateTime 日期时间增强》：时间字段排序场景的格式化与 null 处理实战

---

**收尾三句话**：一行 `sorted` 炸出的不是巧合而是三层知识——比较器要对每个元素负责（null 容错）、类型推断会被链式调用切断（显式类型）、稳定排序与机械翻转不是一回事（反向比较器）。记住检查清单六条，同类问题下次十分钟收工。
