---
title: Collections 与 CollectionUtils 对比实战 —— 仓库标准规程与增值服务的分工
description: 从 null 列表炸出线上 NPE 与 retainAll 改坏源集合的两起事故出发，讲透 Java 8 下 JDK Collections 与 Commons-Collections4 CollectionUtils 的分工与互补：判空防御、无副作用集合代数、排序查找、受控视图陷阱、谓词筛选与归并，附手写集合运算的演进对比与选型决策树。
weight: 3
---

# 为什么需要 CollectionUtils？

想象你管理着一个仓库群（集合）。有两类日常作业经常出事故：

**事故一：空仓库炸了收银台（null 列表 NPE）。**

```java
// ❌ 上游 RPC 返回了 null（对方接口就是这么设计的），本方直接取值
List<String> trackingNos = rpcClient.queryTracking(userId);   // 返回 null
System.out.println(trackingNos.size());                        // 💥 NullPointerException
```

**事故二：求交集把源集合改坏了（retainAll 的副作用）。**

```java
List<String> monthlyCustomers = new ArrayList<>(Arrays.asList("张三", "李四", "王五"));
List<String> vipCustomers = Arrays.asList("李四", "王五", "赵六");

monthlyCustomers.retainAll(vipCustomers);   // 意图：算出「既是本月客户又是 VIP」的名单
// monthlyCustomers 被原地改成了 [李四, 王五] —— 原始名单没了！
// 而且 vipCustomers 若来自 Arrays.asList，遇不可变集合还会直接抛 UnsupportedOperationException
```

JDK 自带一个工具类 `java.util.Collections`，但它管的是「排序、翻转、封装受控视图」这类**对已有 List/Map 的原地操作**；「集合可能是 null」「想要无副作用的交并差」「想一行筛出一个新集合」这些诉求，它一个都不管。Community 侧的答案就是 commons-collections4 的 `CollectionUtils`。

| 没有 CollectionUtils 的痛苦 | 有了 CollectionUtils 的改善 |
|---------------------------|---------------------------|
| `list != null && !list.isEmpty()` 判空三连到处复制 | `isEmpty(list)` 一行，null 当空处理 |
| 交并差要么 retainAll 改坏源集合，要么手写循环 + 临时集合 | `intersection`/`subtract` 一行返回新集合，源集合毫发无损 |
| 两个集合「内容相同」要自己排序再比 | `isEqualCollection` 顺序无关直接比 |
| 往「不许 null 的列表」里塞数据前手写 if | `addIgnoreNull` 拒收 null 一行搞定 |

> ### 💡 新人小结：Collections 和 CollectionUtils 是什么关系？
>
> 把集合操作想象成仓库作业：
> - **Collections** 是仓库官方颁发的**《标准操作规程》手册**：怎么把货架重新排序（sort）、怎么把台账二分查找（binarySearch）、怎么把贵重品锁进玻璃展柜（unmodifiable）——规程权威，但只对「货架本体」负责
> - **CollectionUtils** 是外包的**增值服务团队**：帮你确认仓库是不是空的（isEmpty，null 也算空）、替你核算多家分仓的并单与差单（union/subtract，全程不动你的原始货架）
> - 名字长得像，分工完全不同：一个管「怎么操作」，一个管「安全地算」
>
> **一句话总结：Collections 负责「操作集合」，CollectionUtils 负责「集合运算不炸、不脏、不啰嗦」。**

**学习路线图**：

```
核心概念 → 判空防御 → 集合代数 → 排序查找 → 受控视图 → 谓词筛选 → 演进对比 → 互补守则
定位分野    isEmpty 族   交并差无副作用  sort/binarySearch  视图≠拷贝  select/collate  手写对比   决策树
```

**本文涉及的专有名词**（先解释后使用）：

| 术语 | 全称 | 含义（用自己的话） | 在本文中的角色 |
|------|------|--------------------|----------------|
| Collections | java.util.Collections | JDK 自带的集合工具类，纯静态方法，操作 List/Map/Set 的算法与视图工厂 | 本文主角之一 |
| CollectionUtils | org.apache.commons.collections4.CollectionUtils | commons-collections4 的集合工具类，null 安全判定 + 集合代数 | 本文主角之二 |
| 集合代数 | set algebra | 并集、交集、差集、对称差这一套「把集合当数字做运算」的数学操作 | CollectionUtils 的核心卖点 |
| 基数 | cardinality | 一个元素在集合里出现的次数（List 允许重复，同一元素基数可为 2、3...） | union/intersection 定义重复元素如何取舍 |
| 受控视图 | controlled view | 包装原集合的「壳」：empty/singleton/unmodifiable/synchronized 四类，本身不存数据 | Collections 的另一大职能，含经典陷阱 |
| 防御性拷贝 | defensive copy | 先 `new ArrayList<>(src)` 复制一份再操作，避免共享可变状态 | 修复「视图陷阱」的标准手法 |

---

## 核心概念：两套工具的定位分野

```text
一个集合交给工具类 →
   ├── 对 List/Map 做原地算法（排序/洗牌/翻转/二分）  → Collections（JDK）
   ├── 要一个空集合/单例/重复拷贝的「制式凭证」        → Collections（emptyXxx/singletonXxx/nCopies）
   ├── 把集合包成只读/线程安全壳                      → Collections（unmodifiableXxx/synchronizedXxx）
   ├── 判空（可能是 null）、集合代数、谓词筛选          → CollectionUtils（commons-collections4）
   └── 无副作用的 retainAll/removeAll 替代品           → CollectionUtils（retainAll/removeAll 返回新集合）
```

**引入依赖（GAV）**：

```xml
<!-- ========== Maven：commons-collections4 ========== -->
<!-- 截至 2026-09，最新稳定版 4.6.0（2026-08-06 发布），官方要求 Java 8 及以上；
     4.4（2019 年发布）是使用最广的长期稳定版，两者 API 完全兼容 Java 8 -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-collections4</artifactId>
    <version>4.6.0</version>
</dependency>
```

```groovy
// ========== Gradle 写法 ==========
implementation 'org.apache.commons:commons-collections4:4.6.0'
```

**null 语义要先立规矩**（官方 javadoc 明确）：CollectionUtils **不是**全库 null-safe——判定类方法（isEmpty 族）null 进返回安全布尔；但集合代数方法（union/intersection/disjunction/subtract）的参数**必须非 null**，传 null 抛 NPE。null 防御要先用 `emptyIfNull` 兜一层，详见场景二。

**版本与包名注意**：包名必须是 `org.apache.commons.collections4`。老 commons-collections 2.x/3.x 的包名是 `org.apache.commons.collections`，3.x 已停止维护且泛型支持残缺；另有 Spring 自带的 `org.springframework.util.CollectionUtils`（只有 isEmpty 等少量方法）——IDE 补全时看清 import 行，别串包。

---

## 主体内容

### 场景一：判空与空集合防御——isEmpty 族与 emptyList 的组合拳

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class NullSafeDemo {
    public static void main(String[] args) {
        List<String> fromRpc = rpcLike();            // 可能返回 null

        // ❌ 手写防御：判空三连，每个调用点都要复制一遍
        if (fromRpc != null && !fromRpc.isEmpty()) {
            System.out.println("手写版：有 " + fromRpc.size() + " 单");
        }

        // ✅ CollectionUtils.isEmpty：null 视同空，一行搞定
        if (CollectionUtils.isNotEmpty(fromRpc)) {
            System.out.println("工具版：有 " + fromRpc.size() + " 单");
        }

        // ✅ emptyIfNull：null 直接换成不可变空集合，后续代码再也不用判 null
        List<String> safe = CollectionUtils.emptyIfNull(fromRpc);
        System.out.println(safe.size());             // 输出: 0（null 已被兜成空集合）

        // size / sizeIsEmpty：连 Map、数组、Iterator 都能统一定长与判空
        System.out.println(CollectionUtils.size(new String[]{"a", "b"}));   // 输出: 2（数组也能量）
    }

    static List<String> rpcLike() {
        return null;                                 // 模拟上游返回 null 的接口
    }
}
```

**参数解释**：

| 方法 | null 输入 | 说明 |
|------|----------|------|
| `isEmpty(coll)` | 返回 `true` | null 视同空集合 |
| `isNotEmpty(coll)` | 返回 `false` | isEmpty 取反 |
| `emptyIfNull(coll)` | 返回**不可变空集合** | 非 null 时原样返回同一引用 |
| `size(obj)` | 抛 NPE | 支持 Collection/Map/数组/Iterator/Enumeration 的统一取长 |
| `sizeIsEmpty(obj)` | 返回 `true` | 对 Map/数组/迭代器的判空版 |

与之配套的 JDK 侧规矩：**方法返回集合时返回 `Collections.emptyList()` 而不是 null**。`Collections.emptyList()` 是全局单例的不可变空 List，零分配开销；往里 add 会抛 `UnsupportedOperationException`——这恰恰是把「这个集合不该被改」表达在类型契约里（呼应本板块《Optional 优雅处理空值》的结论：集合类型不要包 Optional，空集合就是最好的「没有」）。

> ### 💡 新人小结：判空防御像什么？
>
> 像站点值班员的晨检：
> - **手写三连**是每次开工都要念一遍的口诀——念漏一句就砸
> - **isEmpty** 是把口诀交给了值班制度：null 仓库、空仓库，一律按「今天没货」处理
> - **emptyIfNull** 更进一步：发现「仓库不存在」，直接给你挂一块「空货架」的牌子（emptyList 凭据），后续流程照常走
>
> **一句话总结：对外的每个集合入口先过 isEmpty 或 emptyIfNull，null 就再也伤不到 size() 了。**

### 场景二：无副作用的集合代数——union / intersection / disjunction / subtract

先记住四则运算的**基数规则**（官方 javadoc 定义，List 有重复元素时按基数取舍）：

| 方法 | 数学含义 | 基数规则 | 源集合是否被修改 |
|------|---------|---------|----------------|
| `union(a, b)` | 并集 a ∪ b | 每个元素取 **max**（两边出现次数的较大值） | 否，返回新集合 |
| `intersection(a, b)` | 交集 a ∩ b | 每个元素取 **min** | 否，返回新集合 |
| `disjunction(a, b)` | 对称差（只在其中一边的） | **max − min** | 否，返回新集合 |
| `subtract(a, b)` | 差集 a − b | a 的基数减去 b 中出现的部分 | 否，返回新集合 |

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class AlgebraDemo {
    public static void main(String[] args) {
        List<String> lastMonth = new ArrayList<>(Arrays.asList("张三", "李四", "王五"));
        List<String> thisMonth = new ArrayList<>(Arrays.asList("李四", "王五", "赵六"));

        System.out.println(CollectionUtils.subtract(thisMonth, lastMonth));  // 输出: [赵六]（本月新增）
        System.out.println(CollectionUtils.subtract(lastMonth, thisMonth));  // 输出: [张三]（本月流失）
        System.out.println(CollectionUtils.intersection(lastMonth, thisMonth));  // 输出: [李四, 王五]（连续在册）
        System.out.println(CollectionUtils.union(lastMonth, thisMonth));     // 输出: [张三, 李四, 王五, 赵六]（去重合并）
        System.out.println(CollectionUtils.disjunction(lastMonth, thisMonth));   // 输出: [张三, 赵六]（变动全景）
        // 原集合毫发无损：
        System.out.println(lastMonth);   // 输出: [张三, 李四, 王五]
    }
}
```

**对比 JDK 原生写法的两处坑**：

```java
// ❌ 坑一：List.retainAll / removeAll 是「原地修改」
List<String> copy = new ArrayList<>(Arrays.asList("张三", "李四"));
copy.retainAll(Arrays.asList("李四"));    // copy 被改成 [李四] —— 源数据没了

// ❌ 坑二：Arrays.asList 的产物是不可变长度集合，直接参与 retainAll 会炸
List<String> fixed = Arrays.asList("张三", "李四");
// fixed.retainAll(Arrays.asList("李四"));   // 💥 UnsupportedOperationException

// ✅ CollectionUtils.retainAll / removeAll：同样语义，但返回新集合
List<String> kept = CollectionUtils.retainAll(fixed, Arrays.asList("李四"));
System.out.println(kept);    // 输出: [李四]
System.out.println(fixed);   // 输出: [张三, 李四]（原集合没动）
```

**含重复元素 + null 时的基数行为详解**：

上面的坑一示例元素都不重复，看不出 `retainAll` 对重复元素的处理逻辑。下面用含重复 + null 的数据彻底拆解：

```java
List<String> strings  = new ArrayList<>(Arrays.asList("hello", "aworld", "aworld", "aworld", null, "full"));
List<String> strings1 = Arrays.asList("aworld", "aworld", null, "full", "full");

// ===== retainAll：保留 strings 中「也在 strings1 里」的元素 =====
strings.retainAll(strings1);
System.out.println("strings = " + strings);
// 输出: strings = [aworld, aworld, aworld, null, full]

// ===== removeAll：删除 strings 中「在 strings1 里出现过」的元素 =====
strings  = new ArrayList<>(Arrays.asList("hello", "aworld", "aworld", "aworld", null, "full"));
strings1 = Arrays.asList("aworld", "aworld", null, "full", "full");
strings.removeAll(strings1);
System.out.println("strings = " + strings);
// 输出: strings = [hello]
```

**逐元素拆解**：

| 元素 | strings 基数 | strings1 基数 | retainAll 结果 | removeAll 结果 |
|------|-------------|--------------|---------------|---------------|
| `"hello"` | 1 | 0（不在） | 移除（strings1 没有） | **保留**（strings1 没有） |
| `"aworld"` | 3 | 2 | **全部保留** 3 个（contains 返回 true） | **全部移除**（contains 返回 true） |
| `null` | 1 | 1 | **保留** 1 个 | **移除** |
| `"full"` | 1 | 2 | **保留** 1 个 | **移除** |

**规律总结**：

- **`retainAll`** 的判断逻辑是 `contains()`——只要元素在目标集合中**存在**，源集合中该元素的**所有副本全部保留**，不管目标集合里有几个。所以 3 个 "aworld" 全留、1 个 "full" 也留。这和 `CollectionUtils.intersection` 的 min 基数规则**不同**——intersection 会取 min(3,2)=2 个 "aworld"，retainAll 直接留 3 个
- **`removeAll`** 的判断逻辑同样是 `contains()`——只要元素在目标集合中**出现过**，源集合中该元素的**所有副本全部删除**。和 `CollectionUtils.subtract` 的基数相减也**不同**——subtract 会用 3−2=1 还剩 1 个 "aworld"，removeAll 直接清零
- **null 安全**：两者都能处理 null 元素（`contains(null)` 返回 true），不会 NPE

> 与 CollectionUtils 代数方法对照：`retainAll` ≠ `intersection`（retainAll 按存在性全留，intersection 按 min 基数截取）；`removeAll` ≠ `subtract`（removeAll 按存在性清零，subtract 按基数相减）。JDK 原生方法只看「在不在」，CollectionUtils 代数方法看「有几个」。需要精确基数语义时，用 CollectionUtils。

**参数解释**：四个代数方法的参数都**不允许为 null**（javadoc 标注 must not be null）——上游可能给 null 时，先 `emptyIfNull` 兜一层再运算。`retainAll(collection, retain)` 与 `removeAll(collection, remove)` 是 JDK `List.retainAll/removeAll` 的「无副作用版」，官方 javadoc 原话：适用于「不想修改原集合、因此没法调 collection.removeAll」的场景。

**顺序提示**：union/intersection/disjunction 的返回集合**不保证保持输入顺序**——上面示例的输出按语义书写，需要稳定顺序时把结果转入 `TreeSet` 或自行排序后再使用。

> ### 💡 新人小结：集合代数像什么？
>
> 像仓库群之间的账目服务：
> - **union** 是并单：两家分仓的货合并铺货，重复 SKU 只摆一份（max 基数）
> - **intersection** 是共同库存：两边都有的才算
> - **subtract** 是差单：我有你没有的那部分
> - 最关键的规矩：**服务团队只出报表，绝不动你的原始货架**——所有结果都是新集合
>
> **一句话总结：算交并差用 CollectionUtils，源集合只读不动；JDK 的 retainAll 是「在你家现场改账本」。**

### 场景三：排序与查找——Collections 的主场（JDK 8 写法对照）

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class AlgorithmDemo {
    public static void main(String[] args) {
        List<Integer> weights = new ArrayList<>(Arrays.asList(12, 5, 30));

        // 排序：Java 8 起 List.sort 与 Collections.sort 等价（前者是 default 方法，内部转调）
        Collections.sort(weights);
        System.out.println(weights);                    // 输出: [5, 12, 30]

        // 翻转与洗牌：只对 List 有意义
        Collections.reverse(weights);
        System.out.println(weights);                    // 输出: [30, 12, 5]
        Collections.shuffle(weights);                   // 随机打乱（抽奖、抽样场景）

        // 二分查找：前提——列表必须已按同样规则排序
        List<Integer> sorted = new ArrayList<>(Arrays.asList(5, 12, 30));
        int hit = Collections.binarySearch(sorted, 12);
        int miss = Collections.binarySearch(sorted, 20);
        System.out.println(hit);                        // 输出: 1（命中下标）
        System.out.println(miss);                       // 输出: -2（负数！解码见下）

        // 最值与频次：一行顶一个循环
        System.out.println(Collections.max(sorted));            // 输出: 30
        System.out.println(Collections.frequency(sorted, 12));  // 输出: 1（元素出现次数）

        // 判「两个集合无交集」：disjoint 是 boolean 短路版
        System.out.println(Collections.disjoint(sorted, Arrays.asList(99)));  // 输出: true
    }
}
```

**binarySearch 负数解码**：返回值 `-插入点 - 1`。上例 `-2` 意味着插入点是 `1`（`20` 应插在下标 1 处保持有序）。公式保证「负数 = 未命中」永不与合法下标混淆——这是它的设计巧思，也是面试高频题。

**与 CollectionUtils 的互补**：想判定「两集合是否有共同元素」，`Collections.disjoint(a, b)` 是语义清晰的 JDK 写法；需要拿到共同元素本身，则用 `CollectionUtils.intersection(a, b)`。前者回答「有没有」，后者回答「是什么」。

### 场景四：受控视图——Collections 的另一张王牌与经典陷阱

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class ViewDemo {
    public static void main(String[] args) {
        // ========== 1. 制式凭证三件套：empty / singleton / nCopies ==========
        List<String> none   = Collections.emptyList();       // 全局单例空 List，零分配
        List<String> one    = Collections.singletonList("SF001");  // 不可变单元素
        List<String> banner = Collections.nCopies(3, "周末达");     // 3 份重复的不可变列表
        System.out.println(one + " / " + banner);            // 输出: [SF001] / [周末达, 周末达, 周末达]

        // ========== 2. unmodifiableXxx：只读【视图】，不是拷贝！ ==========
        List<String> shelf = new ArrayList<>(Arrays.asList("甲", "乙"));
        List<String> showcase = Collections.unmodifiableList(shelf);   // 玻璃展柜：包着 shelf
        // showcase.add("丙");                                 // 💥 UnsupportedOperationException（展柜只许看）
        shelf.add("丙");                                       // 但仓库本体还能动
        System.out.println(showcase);                          // 输出: [甲, 乙, 丙]（视图跟着源变了！）

        // ========== 3. 正确姿势：防御性拷贝 + 只读视图 ==========
        List<String> showcase2 = Collections.unmodifiableList(new ArrayList<>(Arrays.asList("甲", "乙")));
        System.out.println(showcase2);                         // 输出: [甲, 乙]（与源彻底脱钩）
    }
}
```

**陷阱机理**：`unmodifiableList` 的实现只是一个转发壳——get/size 转给源集合，add/set 一律抛异常。它拦截「通过这个引用改数据」，不拦截「通过源引用改数据」。要求「彻底不可变」，必须先防御性拷贝再包视图：`Collections.unmodifiableList(new ArrayList<>(src))`。（Java 9+ 有 `List.of(...)` 一步到位，Java 8 项目就用拷贝+视图这套组合。）

**线程安全视图同理要清醒**：`Collections.synchronizedList(list)` 只保证单个方法调用原子，**遍历仍需手动 synchronized**——多数业务场景更好的选择是 `java.util.concurrent.CopyOnWriteArrayList` 或并发集合。一个有力的旁证：commons-collections4 自己的 `synchronizedCollection`/`unmodifiableCollection` 自 4.1 起**标记废弃，javadoc 明确指回 `Collections.*`**——在「受控视图」这件事上，JDK 就是官方指定的唯一答案。

> ### 💡 新人小结：unmodifiableList 像什么？
>
> 像仓库里给贵重品装的**玻璃展柜**：
> - 展柜锁死了「从展柜这边动手」的路（add 抛异常）
> - 但展柜只是套在**原货架**外面的壳——仓库管理员从货架后面补货，展柜里的陈列跟着变
> - 想要「谁也改不了」的独立展品，得**先复制一份**放进展柜（防御性拷贝）
>
> **一句话总结：视图管得住引用管不住源头——「只读」和「不可变」隔着一次防御性拷贝。**

### 场景五：谓词筛选与归并——CollectionUtils 的增值技能

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class PredicateDemo {
    public static void main(String[] args) {
        List<String> waybills = Arrays.asList("SF001", "YT002", "SF003", "JD004");

        // 1. select / reject：按条件分流成两个新集合（源集合不动）
        List<String> sfOnly = new ArrayList<>();
        CollectionUtils.select(waybills, s -> s.startsWith("SF"), sfOnly);
        System.out.println(sfOnly);        // 输出: [SF001, SF003]

        // 2. Java 8 首选还是 Stream（主流社区实践）：
        List<String> sfByStream = waybills.stream()
                .filter(s -> s.startsWith("SF"))
                .collect(java.util.stream.Collectors.toList());
        System.out.println(sfByStream);    // 输出: [SF001, SF003]

        // 3. collate：两条【已排序】名单 O(n) 归并成一条有序 List（两参版默认保留重复）
        List<Integer> lineA = Arrays.asList(1, 3, 5);
        List<Integer> lineB = Arrays.asList(2, 3, 6);
        System.out.println(CollectionUtils.collate(lineA, lineB));            // 输出: [1, 2, 3, 3, 5, 6]（保留重复）
        System.out.println(CollectionUtils.collate(lineA, lineB, false));     // 输出: [1, 2, 3, 5, 6]（includeDuplicates=false 去重合并）

        // 4. addIgnoreNull：null 元素拒收，返回 boolean 表示集合是否变化
        List<String> shelf = new ArrayList<>();
        CollectionUtils.addIgnoreNull(shelf, "SF001");
        System.out.println(CollectionUtils.addIgnoreNull(shelf, null));       // 输出: false（null 被拒收）
        System.out.println(shelf);                                            // 输出: [SF001]

        // 5. isEqualCollection：顺序无关、按基数判等（盘点核对）
        System.out.println(CollectionUtils.isEqualCollection(
                Arrays.asList("a", "b", "b"), Arrays.asList("b", "a", "b"))); // 输出: true
        System.out.println(Arrays.asList("a", "b", "b").equals(
                Arrays.asList("b", "a", "b")));                               // 输出: false（List.equals 顺序敏感）
    }
}
```

**参数解释**：

| 方法 | null 行为 | 说明 |
|------|----------|------|
| `select(iterable, predicate)` | 谓词为 null 时结果为空集合 | 返回新集合；三参版可指定输出容器，四参版同时分出 rejected |
| `collate(a, b)` | 参数必须非 null | 两个输入必须**已排序**，O(n) 归并；两参版默认保留重复（源码委托 `includeDuplicates=true`），传 `false` 才去重 |
| `addIgnoreNull(coll, obj)` | **coll 本身**必须非 null，obj 为 null 则不加 | 返回集合是否发生变化 |
| `isEqualCollection(a, b)` | 返回 boolean | 元素与各自出现次数完全一致才 true |

**选型提示**：Java 8 以后，**过滤与转换的主流是 Stream**（`filter`/`map`/`collect`，可读性与组合能力最强）；`select`/`reject` 的价值在于「一行拿到新集合、不引入流式样板」以及与 commons 谓词生态（`Predicate` 装饰器）配合的存量代码。`collate` 则是 Stream 没有直接对应的实用工具——归并两条已排序数据。

### 场景六：统一取值入口——get(Object, int)

`CollectionUtils.get(obj, index)` 给 Map、List、数组、迭代器提供了**同一个按下标取值的入口**：

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;

public class GetDemo {
    public static void main(String[] args) {
        Map<String, String> status = new LinkedHashMap<>();
        status.put("SF001", "已签收");
        status.put("YT002", "运输中");

        // Map 没有 get(1)——get 统一按「第 N 个条目」取（依赖迭代顺序，LinkedHashMap 稳定）
        System.out.println(CollectionUtils.get(status, 0));   // 输出: SF001=已签收（Map.Entry）

        List<String> list = Arrays.asList("a", "b", "c");
        System.out.println(CollectionUtils.get(list, 2));     // 输出: c（对 List 等价 list.get(2)）

        // ⚠️ 注意：越界【仍然抛异常】，它的价值是统一入口，不是越界兜底
        // CollectionUtils.get(list, 9);   // 💥 IndexOutOfBoundsException
    }
}
```

**参数解释**：`get(Object, int)` 按 Map（取第 N 个 Entry）/List（等价 get）/数组（取下标）三类分发，其余类型抛 IllegalArgumentException；越界抛 IndexOutOfBoundsException——**没有越界兜底语义**，生产代码按「先判长度再取值」使用。

---

## 演进对比：手写集合运算 vs CollectionUtils

统一场景：把「本月名单」中已离职的人员剔除，并找出连续两月都在册的客户。

**旧方案：迭代器 + retainAll 手写组合（可运行，但坑都在细节里）。**

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

public class LegacyOps {
    public static void main(String[] args) {
        List<String> thisMonth = new ArrayList<>(Arrays.asList("张三", "李四", "王五", "赵六"));
        List<String> leftStaff = Arrays.asList("赵六");
        List<String> lastMonth = Arrays.asList("李四", "王五", "钱七");

        // 剔除离职：用迭代器边遍历边删（直接 for-each 里 remove 会 ConcurrentModificationException）
        Iterator<String> it = thisMonth.iterator();
        while (it.hasNext()) {
            if (leftStaff.contains(it.next())) {
                it.remove();
            }
        }

        // 求共同客户：retainAll 原地修改——为保住原名单只能再拷贝一份
        List<String> keepBoth = new ArrayList<>(thisMonth);
        keepBoth.retainAll(lastMonth);

        System.out.println(thisMonth);   // 输出: [张三, 李四, 王五]（thisMonth 已被剔除改动）
        System.out.println(keepBoth);    // 输出: [李四, 王五]
    }
}
```

**当前方案：同场景两行代数。**

```java
import org.apache.commons.collections4.CollectionUtils;
import java.util.Arrays;
import java.util.List;

public class ModernOps {
    public static void main(String[] args) {
        List<String> thisMonth = Arrays.asList("张三", "李四", "王五", "赵六");
        List<String> leftStaff = Arrays.asList("赵六");
        List<String> lastMonth = Arrays.asList("李四", "王五", "钱七");

        List<String> onJob = CollectionUtils.subtract(thisMonth, leftStaff);   // 剔除离职：新集合
        List<String> keepBoth = CollectionUtils.intersection(thisMonth, lastMonth);  // 共同在册：新集合

        System.out.println(onJob);      // 输出: [张三, 李四, 王五]
        System.out.println(keepBoth);   // 输出: [李四, 王五]
        System.out.println(thisMonth);  // 输出: [张三, 李四, 王五, 赵六]（原始名单完好）
    }
}
```

**对比分析表**：

| 对比维度 | 旧方案：迭代器 + retainAll | 当前方案：CollectionUtils 代数 |
|----------|---------------------------|-------------------------------|
| 写法差异 | 每个运算一段循环或拷贝 + 原地修改，约 10 行 | 每个运算一行，意图即方法名 |
| 行为差异（副作用） | retainAll 原地改源集合，忘记拷贝就是数据事故 | 全部返回新集合，源集合只读 |
| 行为差异（健壮性） | for-each 里 remove 抛 ConcurrentModificationException；Arrays.asList 参与原地修改抛 UnsupportedOperationException | 无原地修改路径，不存在这两类异常 |
| 迁移成本与兼容性风险 | — | 引入一个 jar；方法名与 JDK 语义对齐，团队上手快 |
| 旧方案适用场景 | 极端性能敏感且集合规模可控的内核代码；不允许第三方依赖的项目 | 其余绝大多数业务代码 |

---

## 互补使用守则：什么时候用哪个？

```text
拿到一个集合需求，怎么选？
│
├─ 排序 / 洗牌 / 翻转 / 二分 / 取最值
│      → Collections（JDK 官方算法，List.sort 是 Java 8 的语法糖形式）
│
├─ 要空集合 / 单例 / n 份拷贝的「制式凭证」
│      → Collections.emptyList / singletonList / nCopies（返回值与默认值的规矩）
│
├─ 把集合包装成只读 / 线程安全壳
│      → Collections.unmodifiableXxx / synchronizedXxx（记得视图≠拷贝的陷阱）
│
├─ 判空（可能为 null）与空集合防御
│      → CollectionUtils.isEmpty / emptyIfNull
│
├─ 交并差 / 无副作用 retainAll / 顺序无关判等 / 有序归并
│      → CollectionUtils.intersection / subtract / isEqualCollection / collate
│
└─ 逐元素过滤转换的流水线
       → Java 8 Stream（主流首选）；一行式需求可用 select/reject
```

**性能说明**：集合代数方法需要遍历两个入参完成元素比对，常规业务规模无感；`collate` 是严格 O(n) 归并，比「合并后再 sort」的 O((n+m)log(n+m)) 更优。`Collections` 的算法都是 JDK 内核级实现，无第三方开销。

**社区实践**：Spring 的 `org.springframework.util.CollectionUtils` 只提供 isEmpty 等少量工具（内部工具定位，不建议作为集合代数入口）；JDK 9+ 的 `List.of`/`Set.of` 解决「一步建不可变集合」，Java 8 项目则用「拷贝 + unmodifiable 视图」这套组合拳；commons-collections4 由 Apache 官方持续维护（4.6.0 发布于 2026-08），是 Java 集合运算领域广泛使用的第三方标准件。

---

## Q&A：高频问题与踩坑排查

**Q1：`Collections.unmodifiableList(list)` 之后往 `list` 里加元素，视图会变吗？**

会。视图只是转发壳，源集合变了视图必然跟着变——它拦截的是「通过视图引用修改」，不是「数据不可变」。要真正不可变：`Collections.unmodifiableList(new ArrayList<>(src))`。

**Q2：`Collections.emptyList()` 返回的集合能 add 吗？**

不能，抛 `UnsupportedOperationException`。这是特性不是缺陷：空集合常作为「无结果」的返回值，不可变保证调用方不会误以为可以往里塞数据。需要可变的空集合就 `new ArrayList<>()`。

**Q3：`Collections.binarySearch` 返回 -5 是什么意思？**

未命中，插入点是 `4`（解码公式：`-返回值 - 1 = 插入点`）。使用前提是列表**已按同一比较规则排序**，否则结果无意义；`List` 自身的 `Collections.sort` 与 `list.sort` 用同一套比较器即可保证。

**Q4：`CollectionUtils.union` 会保留重复元素吗？**

按基数取 max 保留：`[a, a]` 与 `[a]` 的 union 是 `[a, a]`（max(2,1)=2），不是 Set 语义的 `[a]`。需要去重语义请先包 `new HashSet<>(...)` 或使用 `Set` 入参。

**Q5：有了 Java 8 的 Stream，还需要 CollectionUtils 吗？**

需要，分工不同：Stream 强在「流水线组合」（filter→map→collect 一气呵成），CollectionUtils 强在「集合对集合的代数运算」（intersection/subtract/collate 用 Stream 写要么啰嗦要么性能差）与「null 防御判定」。两者在同一个项目里正常共存。

**Q6：collections4 和老的 commons-collections 3.x 有什么区别？**

包名不同（`collections4` vs `collections`）、4.x 全面泛型化（3.x 大量裸类型）、3.x 已停止维护。升级只需改 import 与依赖坐标，主流 API 名未变；混用两套会得到同名不同包的工具类，先查 import。

**Q7：听说 `CollectionUtils.forAllDo` 能遍历，能用吗？**

不要用——4.1 起已标记 `@Deprecated`，官方弃用说明指向 commons 自家的 `IterableUtils.forEach`；在 Java 8 代码中，更常见的选择是 `Iterable.forEach` 或 Stream。这也印证了本文的分工判断：「逐元素执行动作」在 Java 8 之后是 JDK 的主场，CollectionUtils 的价值集中在 JDK 没有的集合代数与 null 防御上。

---

## 要点总结

1. **定位分野**：Collections 管「操作与视图」（sort/emptyList/unmodifiable），CollectionUtils 管「null 防御与集合代数」（isEmpty/intersection/subtract）
2. **null 规矩要分层记**：isEmpty 族 null 进出安全布尔；union/intersection 等代数方法参数**必须非 null**（先 emptyIfNull 兜底）
3. **代数全是新集合**：union 取 max 基数、intersection 取 min、disjunction 取 max−min、subtract 取差——源集合永不改动
4. **视图≠拷贝**：unmodifiableXxx 拦得住引用拦不住源头，「彻底只读」必须先防御性拷贝
5. **binarySearch 的负数**是 `-(插入点)-1` 的编码，前提是列表已排序
6. **逐元素处理回归 JDK**：Java 8 之后过滤转换用 Stream、遍历用 forEach，collections4 自己的 forAllDo 也标记废弃（指向 IterableUtils.forEach）

---

> ### 💡 新人小结：Collections 与 CollectionUtils 学完了，记住这 3 点
>
> 1. **Collections 是官方规程手册，CollectionUtils 是增值服务团队**——排序封装找前者，判空代数找后者
> 2. **交并差绝不动原始货架**——所有代数方法返回新集合，retainAll 原地改集合的写法在业务代码里应当绝迹
> 3. **「只读视图」和「不可变」隔着一次防御性拷贝**——unmodifiable 包住可变源，就是一扇没锁的展柜
>
> **一句话总结：JDK 管操作，Commons 管安全——集合工具的正确姿势是「规程照手册、运算找服务、入口先防呆」。**
