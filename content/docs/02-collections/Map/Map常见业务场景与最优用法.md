---
title: Map 常见业务场景与最优用法
description: 20 个高频 Map 业务场景的「痛点 → 设计 → 用法」全解析，涵盖 Java 8+ default 方法、Stream 操作、并发安全与有序性深度分析。
weight: 1
---

# 为什么需要专门研究 Map？

想象你是一个仓库管理员，每天要处理上千件包裹。每件包裹都有一个编号，你需要快速找到对应的包裹。

- **方案 A**：从第 1 个包裹开始，一个一个翻找（线性查找）→ 1000 件包裹要翻 1000 次
- **方案 B**：按编号分门别类放到货架上，通过编号直接定位（Map 键值对）→ 一次定位，瞬间找到

**Map 就是程序员的「智能货架」**——把「键」和「值」关联起来，实现快速查找、分组、统计。

**然而，许多开发者仍然在用老旧的写法**：

| 老旧写法（Java 7） | 现代写法（Java 8+） |
|-------------------|-------------------|
| `if (map.get(key) == null) map.put(key, new ArrayList<>())` | `map.computeIfAbsent(key, k -> new ArrayList<>())` |
| `if (map.containsKey(key)) { ... }` | `map.getOrDefault(key, defaultValue)` |
| 循环 + `if` 统计频次 | `map.merge(word, 1, Integer::sum)` |

本文梳理了 **20 个高频业务场景**，每个场景按照 **「痛点 → 设计 → 具体用法」** 的结构展开。

> ### 💡 新人小结：Map 到底是什么？
>
> 把 Map 想象成一本**通讯录**：
> - 每个「名字」（键 Key）对应一个「电话号码」（值 Value）
> - 通过名字找电话，一次就能定位，不用从头翻到尾
> - Java 8 给通讯录加了很多「快捷操作」：自动建卡、一键更新、批量处理……

**方法选型速查表**（遇到场景先查这里）：

```
你要做什么？
│
├─ 取值 → 键可能不存在？
│         ├─ 是 → getOrDefault（给默认值）
│         └─ 否 → get（直接取）
│
├─ 放值 → 键已存在时怎么办？
│         ├─ 保留旧值 → putIfAbsent
│         ├─ 用函数计算新值 → compute / computeIfAbsent / computeIfPresent
│         ├─ 合并旧值和新值 → merge
│         └─ 直接覆盖 → put
│
├─ 批量操作 → 用什么方式？
│             ├─ 分组统计 → Collectors.groupingBy
│             ├─ List 转 Map → Collectors.toMap（记得处理键冲突！）
│             ├─ 排序 → Stream.sorted + LinkedHashMap
│             └─ 过滤 → Stream.filter + collect
│
└─ 并发环境 → ConcurrentHashMap + 原子操作（merge / computeIfAbsent）
```

---

## 1. 初始化 Map

### 痛点
在 Java 8 之前，初始化一个带有初始键值对的 `Map` 通常需要：
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);
```
或者使用笨拙的双花括号（匿名内部类），存在内存泄漏和反序列化问题。

### 设计
Java 9 引入了 `Map.of()` 和 `Map.ofEntries()`，Java 8 则可以通过 `Stream` 或第三方库（如 Guava）实现简洁初始化。但若团队仍使用 Java 8，推荐使用 `Stream` 配合 `Collectors.toMap` 或自定义工具方法。

### 具体用法（Java 8 兼容）
```java
// 方式一：双花括号（不推荐，仅展示）
Map<String, Integer> map1 = new HashMap<String, Integer>() {{
    put("a", 1);
    put("b", 2);
}};

// 方式二：Stream + 二维数组（推荐，Java 8 可用）
Map<String, Integer> map2 = Stream.of(new Object[][] {
    {"a", 1},
    {"b", 2}
}).collect(Collectors.toMap(data -> (String) data[0], data -> (Integer) data[1]));

// 方式三：使用 Arrays.asList + SimpleEntry（较繁琐但类型安全）
Map<String, Integer> map3 = new HashMap<>(Map.of("a", 1, "b", 2)); // Java 9+，此处不展开
```

**参数解释**：
- `Stream.of(T... values)`：创建流，每个元素是 `Object[]`。
- `collect(Collectors.toMap(keyMapper, valueMapper))`：将流元素收集为 Map，第一个函数提取键，第二个函数提取值。

> ### 💡 新人小结：初始化 Map
>
> 想象你要建一个通讯录，传统方法是先买一个空本子，再一页页写名字和电话。`Map.of()` 就像直接买一本已经印好几页的通讯录，而 `Stream` 方法相当于用流水线快速把名单贴到本子上。**双花括号** 相当于在本子上夹了一张临时纸，用完容易忘记拿走，所以不推荐。

---

## 2. 安全获取值（getOrDefault）

### 痛点
从 Map 中取一个不存在的键会返回 `null`，如果直接使用返回值（如 `.intValue()`）会抛 `NullPointerException`。传统写法：
```java
Integer value = map.get(key);
if (value == null) {
    value = defaultValue;
}
```

### 设计
Java 8 的 `getOrDefault(Object key, V defaultValue)` 将"取值+判空+给默认值"合并为一步，语义更清晰。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("count", 10);
int count = map.getOrDefault("count", 0);      // 10
int missing = map.getOrDefault("missing", 0); // 0
```

**参数解释**：
- `key`：要查找的键。
- `defaultValue`：当键不存在或映射值为 `null` 时返回的默认值。

> ### 💡 新人小结：getOrDefault
>
> 就像自动售货机：你投币选"可乐"，如果机器里没有，它会直接掉出一瓶"矿泉水"（默认值），而不是让你干等着或者报错。

---

## 3. 键不存在时自动计算值（computeIfAbsent）

### 痛点
常见的"如果键不存在则创建并放入"模式：
```java
List<String> list = map.get(key);
if (list == null) {
    list = new ArrayList<>();
    map.put(key, list);
}
list.add(value);
```
代码重复且在多线程下不安全。

### 设计
`computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)` 会检查键是否存在（或值为 `null`），若不存在则调用函数生成新值并放入 Map，然后返回该值。**原子性**在 `ConcurrentHashMap` 中更优。

### 具体用法
```java
Map<String, List<String>> map = new HashMap<>();
map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("apple");
map.computeIfAbsent("fruits", k -> new ArrayList<>()).add("banana");
System.out.println(map); // {fruits=[apple, banana]}
```

**参数解释**：
- `key`：需要检查的键。
- `mappingFunction`：当键缺失时调用的函数，输入是键，输出是新值。**注意**：如果函数返回 `null`，则不会放入 Map，且方法返回 `null`。

> ### 💡 新人小结：computeIfAbsent
>
> 就像去图书馆借书，如果某本书没有被借阅记录（键不存在），管理员会先新建一个借阅卡（空列表），然后你把名字写上去。第二次借同一本书时，直接使用已有的借阅卡。

---

## 4. 键存在时才更新（computeIfPresent）

### 痛点
有时只想在键已经存在的情况下修改值，不存在则不做任何操作。传统写法需要先 `containsKey` 判断再 `put`。

### 设计
`computeIfPresent(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` 仅在键存在且值不为 `null` 时执行函数，并将返回值作为新值（若返回 `null` 则删除该键）。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 10);
map.computeIfPresent("a", (k, v) -> v + 5);   // a=15
map.computeIfPresent("b", (k, v) -> v + 5);   // 无操作，因为 b 不存在
```

**参数解释**：
- `key`：目标键。
- `remappingFunction`：接收 `(键, 旧值)`，返回新值。若返回 `null`，则删除该键。

> ### 💡 新人小结：computeIfPresent
>
> 像是给老客户发优惠券：只有已经注册过的用户（键存在）才能享受折扣，新用户不参与。如果优惠后金额为 0，就把这个用户从名单中移除。

---

## 5. 无条件更新值（compute）

### 痛点
无论键是否存在，都需要根据键和旧值计算一个新值并放入（或删除）。

### 设计
`compute(K key, BiFunction<? super K, ? super V, ? extends V> remappingFunction)` 是最通用的方法，它总是调用函数，并根据返回值决定放入、更新或删除。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 10);
map.compute("a", (k, v) -> (v == null) ? 100 : v + 1); // a=11
map.compute("b", (k, v) -> (v == null) ? 100 : v + 1); // b=100
```

**参数解释**：
- `key`：目标键。
- `remappingFunction`：接收 `(键, 旧值)`，旧值可能为 `null`。返回新值；若返回 `null`，则删除该键。

> ### 💡 新人小结：compute
>
> 相当于"无条件更新"按钮：无论这个键之前有没有值，你都可以根据它的旧状态（可能为空）计算一个新值，然后决定是覆盖还是删除。

---

## 6. 合并两个值（merge）

### 痛点
当需要将两个值合并（如累加、拼接）时，传统写法需要先 get、判断、再 put，容易出错。

### 设计
`merge(K key, V value, BiFunction<? super V, ? super V, ? extends V> remappingFunction)`：
- 如果键不存在或值为 `null`，直接将 `value` 放入。
- 如果键存在，使用函数将旧值和传入的 `value` 合并，返回新值；若函数返回 `null`，则删除该键。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 10);
map.merge("a", 5, Integer::sum);      // a=15
map.merge("b", 5, Integer::sum);      // b=5
map.merge("a", 20, (old, newVal) -> null); // 删除 a
```

**参数解释**：
- `key`：目标键。
- `value`：要合并进来的值。
- `remappingFunction`：接收 `(旧值, 新值)`，返回合并后的值；返回 `null` 则删除键。

> ### 💡 新人小结：merge
>
> 像银行账户合并：如果账户存在，就把两笔钱相加；如果不存在，就直接开户存入。如果合并后余额为 0 且你决定注销账户（返回 null），就删除这个账户。

---

## 7. 仅在键缺失时放入

### 痛点
`put` 会无条件覆盖旧值，但有时我们希望"如果键已存在则保留原值"。

### 设计
`putIfAbsent(K key, V value)` 只在键不存在或值为 `null` 时放入新值，否则保持原值，并返回旧值（或 `null`）。

### 具体用法
```java
Map<String, String> map = new HashMap<>();
map.put("key", "old");
String result1 = map.putIfAbsent("key", "new"); // result1="old", map 仍为 "old"
String result2 = map.putIfAbsent("key2", "new"); // result2=null, map 新增 key2="new"
```

**参数解释**：
- `key`：目标键。
- `value`：若键缺失时放入的值。

> ### 💡 新人小结：putIfAbsent
>
> 就像抢车位：如果车位已经被占了（键存在），你就不强行停进去，保持原样；如果车位空着，你才停进去。

### 7.1 putIfAbsent 和 computeIfAbsent 的区别

#### 方法签名与基本行为

- **`V putIfAbsent(K key, V value)`**  
    如果指定键尚未与任何值关联（或映射到 `null`），则将**给定的值**关联到该键。  
    → **无论键是否存在，`value` 参数都会被计算/创建**（因为它是作为实参传递的）。
    
- **`V computeIfAbsent(K key, Function<? super K, ? extends V> mappingFunction)`**  
    如果指定键缺失，则**调用函数计算值**。  
    → **只有当键缺失时，才会调用 `mappingFunction`**；如果键已存在，则不会调用该函数。

#### 对比表

| 场景 | `putIfAbsent` | `computeIfAbsent` |
|------|-------------|-------------------|
| 键不存在 | 插入给定的值，返回 `null` | 调用函数计算值并插入，返回计算值 |
| 键存在且值非 `null` | 不插入，返回旧值（**但值已被创建**） | 不调用函数，直接返回旧值 |
| 键存在但值为 `null` | 视为"不存在"，会插入给定的值 | 调用函数计算新值并插入 |

---

## 8. 批量更新所有值

### 痛点
需要对 Map 中的每个值执行相同的转换（例如所有价格打八折），传统写法需要遍历并重新 put。

### 设计
`replaceAll(BiFunction<? super K, ? super V, ? extends V> function)` 对每个条目应用函数，并用返回值替换旧值。**注意**：不能改变键。

### 具体用法
```java
Map<String, Double> prices = new HashMap<>();
prices.put("apple", 2.0);
prices.put("banana", 1.5);
prices.replaceAll((k, v) -> v * 0.8);
// {apple=1.6, banana=1.2}
```

> ### 💡 新人小结：replaceAll
>
> 超市全场八折：收银员不需要每个商品单独手动计算，系统自动对所有商品价格乘以 0.8。

---

## 9. 高效遍历

### 痛点
传统遍历方式：`keySet()` 再 `get(key)`，会导致多次哈希查找，效率低下。`entrySet()` 直接访问键值对。

### 设计
Java 8 推荐使用 `forEach(BiConsumer<? super K, ? super V> action)` 结合 `entrySet()` 或直接使用 lambda。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);

// 推荐：直接 forEach + lambda
map.forEach((k, v) -> System.out.println(k + "=" + v));

// 或者使用 entrySet 遍历（也是高效的）
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + "=" + entry.getValue());
}
```

> ### 💡 新人小结：遍历方式
>
> 传统 `keySet()` 遍历就像你有一串钥匙，每次要打开对应的抽屉拿东西（get）。而 `entrySet()` 相当于直接把抽屉和里面的东西一起端出来，省去了一次次开锁。

### 9.1 for-each 中 entrySet() 只调用一次

增强型 for-each 循环是 Java 的语法糖，`map.entrySet()` 只在循环开始前被**调用一次**：

```java
// 你的代码：
for (Map.Entry<String, Integer> entry : map.entrySet()) { ... }

// 编译后等效于：
Set<Map.Entry<String, Integer>> set = map.entrySet();  // 只调用一次
Iterator<Map.Entry<String, Integer>> it = set.iterator();
while (it.hasNext()) {
    Map.Entry<String, Integer> entry = it.next();
    // 业务逻辑
}
```

---

## 10. 排序

### 痛点
`HashMap` 无序，但业务中常需要按键或按值排序输出。

### 设计
使用 `Stream` 对 `entrySet()` 排序，然后收集到 `LinkedHashMap`（保持插入顺序）或 `TreeMap`（按键自然顺序）。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("banana", 5);
map.put("apple", 10);
map.put("cherry", 3);

// 按键排序（升序）
Map<String, Integer> sortedByKey = map.entrySet().stream()
    .sorted(Map.Entry.comparingByKey())
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
        (oldVal, newVal) -> oldVal, LinkedHashMap::new));

// 按值排序（降序）
Map<String, Integer> sortedByValueDesc = map.entrySet().stream()
    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue,
        (oldVal, newVal) -> oldVal, LinkedHashMap::new));
```

> ### 💡 新人小结：排序
>
> `HashMap` 像一堆乱放的扑克牌，排序后相当于把牌按大小顺序重新排列，并且放进一个透明的牌盒（LinkedHashMap）里，顺序不会丢。

---

## 11. 按值分组

### 痛点
需要根据某个属性将对象列表分组到 Map 中，例如按部门分组员工。

### 设计
`Collectors.groupingBy(Function<? super T, ? extends K> classifier)` 返回 `Map<K, List<T>>`，也可以指定下游收集器。

### 具体用法
```java
List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT"),
    new Employee("Bob", "HR"),
    new Employee("Charlie", "IT")
);

Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));
// {IT=[Alice, Charlie], HR=[Bob]}
```

> ### 💡 新人小结：分组
>
> 像学校按班级分班：把一堆学生名单，根据班级字段分成多个小名单，每个班级一个列表。

---

## 12. List 转 Map

### 痛点
将 `List` 转换为 `Map` 时，如果存在重复键会抛 `IllegalStateException`。

### 设计
`Collectors.toMap(keyMapper, valueMapper, mergeFunction)` 必须提供合并函数来处理键冲突，否则默认抛出异常。

### 具体用法
```java
List<Employee> employees = Arrays.asList(
    new Employee("Alice", "IT", 5000),
    new Employee("Bob", "HR", 4000),
    new Employee("Charlie", "IT", 6000)
);

// 键为 id，值为姓名（假设 id 唯一）
Map<Integer, String> idToName = employees.stream()
    .collect(Collectors.toMap(Employee::getId, Employee::getName));

// 键为部门，值为最高工资（处理重复键）
Map<String, Integer> deptMaxSalary = employees.stream()
    .collect(Collectors.toMap(
        Employee::getDepartment,
        Employee::getSalary,
        Integer::max
    ));
```

> ### 💡 新人小结：List 转 Map
>
> 如果把学生名单转成"学号→姓名"的对照表，学号重复就会冲突。你必须提前规定冲突时怎么办（例如保留第一个或合并）。

---

## 13. 统计频次（Map.merge）

### 痛点
统计一段文本中每个单词出现的次数，传统写法需要循环判断并累加。

### 设计
使用 `Map.merge` 一行完成计数，或者使用 `Collectors.groupingBy` + `Collectors.counting`。

### 具体用法
```java
String text = "apple banana apple orange banana apple";
Map<String, Integer> wordCount = new HashMap<>();
for (String word : text.split(" ")) {
    wordCount.merge(word, 1, Integer::sum);
}
// 或者使用 Stream
Map<String, Long> wordCountStream = Arrays.stream(text.split(" "))
    .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));
```

> ### 💡 新人小结：统计频次
>
> 就像用计数器记录每个商品的销量：每卖出一个"苹果"，就在苹果那行加 1，没有这个商品就先新建一行。

---

## 14. 缓存模式

### 痛点
需要实现"如果缓存中有则直接返回，没有则从数据库/文件加载并放入缓存"。

### 设计
`computeIfAbsent` 完美匹配此模式，且支持惰性加载。

### 具体用法
```java
private Map<String, User> userCache = new HashMap<>();

public User getUser(String id) {
    return userCache.computeIfAbsent(id, this::loadUserFromDb);
}

private User loadUserFromDb(String id) {
    return new User(id, "Name_" + id);
}
```

> ### 💡 新人小结：缓存模式
>
> 像是图书馆的查询系统：先查本地书架（缓存），如果没有，就去仓库（数据库）找，找到后登记到书架上，下次直接拿。

---

## 15. 按条件过滤

### 痛点
需要删除 Map 中不满足条件的条目，传统做法是遍历并使用迭代器删除，容易 `ConcurrentModificationException`。

### 设计
使用 `Stream` 的 `filter` 和 `collect` 生成新 Map，或者 Java 8 的 `removeIf` 在 `entrySet` 上操作。

### 具体用法
```java
Map<String, Integer> map = new HashMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// 方式一：生成新 Map（推荐）
Map<String, Integer> filtered = map.entrySet().stream()
    .filter(e -> e.getValue() > 1)
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

// 方式二：直接删除
map.entrySet().removeIf(e -> e.getValue() <= 1);
```

> ### 💡 新人小结：过滤
>
> 像清理冰箱：把过期食品（不满足条件）挑出来扔掉（removeIf），或者重新整理一个只装新鲜食品的新冰箱（filter + collect）。

---

## 16. Map 合并

### 痛点
将两个 Map 合并，如果键冲突如何处理？`putAll` 直接覆盖，无法自定义合并逻辑。

### 设计
使用 `merge` 循环合并，或者使用 `Stream.concat` + `Collectors.toMap` 指定合并函数。

### 具体用法
```java
Map<String, Integer> map1 = new HashMap<>();
map1.put("a", 1);
map1.put("b", 2);

Map<String, Integer> map2 = new HashMap<>();
map2.put("b", 3);
map2.put("c", 4);

// 方式一：putAll（简单覆盖）
Map<String, Integer> merged1 = new HashMap<>(map1);
merged1.putAll(map2); // {a=1, b=3, c=4}

// 方式二：merge 累加
Map<String, Integer> merged2 = new HashMap<>(map1);
map2.forEach((k, v) -> merged2.merge(k, v, Integer::sum)); // {a=1, b=5, c=4}

// 方式三：Stream 合并
Map<String, Integer> merged3 = Stream.concat(map1.entrySet().stream(), map2.entrySet().stream())
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, Integer::sum));
```

> ### 💡 新人小结：Map 合并
>
> 合并两个账本：`putAll` 是直接拿第二个账本的记录覆盖第一个；`merge` 是如果同一项目存在，就把金额相加。

---

## 17. 不可变 Map

### 痛点
某些配置或常量 Map 不应该被修改。

### 设计
Java 9 的 `Map.of()` 和 `Map.ofEntries()` 创建真正不可变 Map；Java 8 可以用 `Collections.unmodifiableMap`。

### 具体用法
```java
// Java 9+
Map<String, Integer> immutable = Map.of("a", 1, "b", 2); // 最多10对
Map<String, Integer> immutableMany = Map.ofEntries(
    Map.entry("a", 1), Map.entry("b", 2), Map.entry("c", 3)
);

// Java 8 兼容
Map<String, Integer> temp = new HashMap<>();
temp.put("a", 1); temp.put("b", 2);
Map<String, Integer> unmodifiable = Collections.unmodifiableMap(temp);
// 注意：temp 仍可修改，会影响 unmodifiable 视图
```

> ### 💡 新人小结：不可变 Map
>
> 不可变 Map 就像刻在石头上的名单，一旦刻好就不能修改。`Collections.unmodifiableMap` 只是给原名单加了一层玻璃罩，但原名单还能改；`Map.of` 则是直接刻在石头上，谁也改不了。

---

## 18. Map 扁平化

### 痛点
处理嵌套 Map 时，需要将内层键值展开为复合键或合并。

### 设计
使用 `Stream` 的 `flatMap` 将嵌套结构扁平化。

### 具体用法
```java
Map<String, Map<String, Integer>> nested = new HashMap<>();
Map<String, Integer> inner1 = new HashMap<>();
inner1.put("x", 1); inner1.put("y", 2);
nested.put("outer1", inner1);

Map<String, Integer> inner2 = new HashMap<>();
inner2.put("z", 3);
nested.put("outer2", inner2);

// 扁平化为 "outer.key" -> value
Map<String, Integer> flatMap = nested.entrySet().stream()
    .flatMap(outer -> outer.getValue().entrySet().stream()
        .map(inner -> new AbstractMap.SimpleEntry<>(
            outer.getKey() + "." + inner.getKey(), inner.getValue())))
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
// {outer1.x=1, outer1.y=2, outer2.z=3}
```

> ### 💡 新人小结：Map 扁平化
>
> 像是把多层文件夹里的文件全部拿出来，在文件名前面加上文件夹路径，变成一层扁平的文件列表。

---

## 19. 并发 Map

### 痛点
多线程环境下使用 `HashMap` 会导致数据不一致或死循环（JDK7）。`Hashtable` 全表锁性能差。

### 设计
使用 `ConcurrentHashMap`，采用 CAS + synchronized（JDK8），并提供原子操作方法。

### 具体用法
```java
ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();

// 原子累加
concurrentMap.merge("key", 1, Integer::sum);

// 原子初始化
List<String> list = concurrentMap.computeIfAbsent("listKey", k -> new ArrayList<>());
list.add("item"); // 注意：返回的 list 可能被并发修改，需自行同步
```

> ### 💡 新人小结：并发 Map
>
> `HashMap` 像只有一个收银台的超市，大家挤在一起会乱；`ConcurrentHashMap` 像开了多个收银台，每个收银员处理自己的商品，互不干扰，还支持原子操作。

---

## 20. Map 与 JSON/POJO 互转

### 痛点
在 Web 开发中，经常需要将 Map 转为 JSON 字符串，或者将 JSON 反序列化为 Map。

### 设计
使用 Jackson 的 `ObjectMapper` 完成转换。

### 具体用法
```java
ObjectMapper objectMapper = new ObjectMapper();

// Map -> JSON
Map<String, Object> map = new HashMap<>();
map.put("name", "Alice"); map.put("age", 30);
String json = objectMapper.writeValueAsString(map); // {"name":"Alice","age":30}

// JSON -> Map
Map<String, Object> parsedMap = objectMapper.readValue(json, new TypeReference<Map<String, Object>>() {});

// POJO -> Map
Employee emp = new Employee("Bob", "IT", 5000);
Map<String, Object> empMap = objectMapper.convertValue(emp, new TypeReference<Map<String, Object>>() {});
```

> ### 💡 新人小结：Map 与 JSON 互转
>
> 就像是翻译：把中文（Map）翻译成英文（JSON），或者把英文翻译回中文。`ObjectMapper` 就是那个翻译官。

---

## 总结对比表

| 场景 | 推荐方法 | 关键参数 | 注意事项 |
|------|---------|---------|----------|
| 初始化 | `Stream.of` + `Collectors.toMap` | keyMapper, valueMapper | Java 9+ 可用 `Map.of` |
| 安全获取 | `getOrDefault` | defaultValue | 返回默认值不修改 Map |
| 键缺失创建 | `computeIfAbsent` | mappingFunction | 函数返回 null 则不放入 |
| 键存在更新 | `computeIfPresent` | remappingFunction | 返回 null 删除键 |
| 无条件更新 | `compute` | remappingFunction | 通用方法 |
| 合并值 | `merge` | value, remappingFunction | 常用于累加 |
| 仅缺失放入 | `putIfAbsent` | value | 与 `computeIfAbsent` 区别：值总是被创建 |
| 批量更新 | `replaceAll` | function | 不能改变键 |
| 遍历 | `forEach` + `entrySet` | action | 避免 keySet+get |
| 排序 | `Stream.sorted` + `LinkedHashMap` | comparator | 按值排序必须用 Stream |
| 分组 | `Collectors.groupingBy` | classifier, downstream | 返回 `Map<K, List<T>>` |
| List转Map | `Collectors.toMap` | keyMapper, valueMapper, mergeFunction | 必须处理键冲突 |
| 统计频次 | `merge(key,1,Integer::sum)` | key, value, remappingFunction | 简单高效 |
| 缓存 | `computeIfAbsent` | mappingFunction | 惰性加载 |
| 过滤 | `Stream.filter` + `collect` | predicate | 或 `entrySet().removeIf` |
| Map合并 | `merge` 循环 / Stream.concat | remappingFunction | 注意冲突策略 |
| 不可变Map | `Map.of` (Java9+) | 键值对 | 不可修改 |
| 扁平化 | `flatMap` + `SimpleEntry` | function | 嵌套结构转一维 |
| 并发Map | `ConcurrentHashMap` 原子方法 | key, value, function | 线程安全 |
| JSON/POJO互转 | `ObjectMapper` 方法 | TypeReference | 泛型保留 |

---

## 深度分析：List 转 Map 与 GroupBy 的有序性

`Collectors.toMap` 和 `Collectors.groupingBy` 返回的 Map 默认是 `HashMap`（**无序**）。如果业务需要有序输出，需要指定 Map 实现。

### 三种常用 Map 的有序性

| Map 实现 | 有序性 | 说明 |
|----------|--------|------|
| `HashMap` | **无序** | 遍历顺序不可预测 |
| `LinkedHashMap` | **插入顺序** | 维护双向链表，遍历顺序与插入顺序一致 |
| `TreeMap` | **键自然顺序** | 基于红黑树，按键排序 |

### 如何保持插入顺序？

```java
// toMap 保持插入顺序
Map<Integer, String> idToName = employees.stream()
    .collect(Collectors.toMap(
        Employee::getId, Employee::getName,
        (oldVal, newVal) -> oldVal,
        LinkedHashMap::new    // 指定 Map 实现
    ));

// groupingBy 保持键首次出现顺序
Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        LinkedHashMap::new,   // 保持首次出现顺序
        Collectors.toList()
    ));
```

### 如何按键排序？

```java
// 使用 TreeMap
Map<Integer, String> idToName = employees.stream()
    .collect(Collectors.toMap(
        Employee::getId, Employee::getName,
        (oldVal, newVal) -> oldVal,
        TreeMap::new    // 按键自然顺序排序
    ));
```

> ### 💡 新人小结：Map 的有序性
>
> - `HashMap` 像一个**没有编号的储物柜**，取出来时不知道先拿到哪个
> - `LinkedHashMap` 像一个**排队队列**，先来后到
> - `TreeMap` 像一本**字典**，自动按字母/数字排序
>
> 默认得到的是“没有编号的储物柜”。想保持顺序，就额外传入一个 `mapFactory` 参数。

### 最佳实践建议

| 需求 | 推荐做法 |
|------|---------|
| 不关心顺序 | 使用默认 `toMap` / `groupingBy` |
| 保持源列表顺序 | 指定 `LinkedHashMap` 作为 Map 工厂 |
| 按键排序 | 指定 `TreeMap` 作为 Map 工厂 |
| 并行流 + 必须顺序 | 放弃并行流，或收集后手动排序 |

---

## 要点总结

1. **Java 8 的 Map default 方法**（`computeIfAbsent`、`merge`、`getOrDefault` 等）让常见操作一行搞定
2. **方法选型**：先查本文开头的「方法选型速查表」，快速定位正确方法
3. **Collectors.toMap 必须处理键冲突**，否则重复键会抛异常
4. **并发环境**用 `ConcurrentHashMap`，其 `merge`/`computeIfAbsent` 是原子操作
5. **有序性**：默认 HashMap 无序，需要有序时指定 `LinkedHashMap` 或 `TreeMap`

---

> ### 💡 新人小结：Map 实战学完了，记住这 5 点
>
> 1. **取值用 `getOrDefault`**：告别 null 判断
> 2. **放值先想清楚**：保留旧值用 `putIfAbsent`，计算新值用 `compute`，合并用 `merge`
> 3. **Stream 是批量操作利器**：分组用 `groupingBy`，转 Map 用 `toMap`（别忘了冲突处理）
> 4. **并发必选 ConcurrentHashMap**：别在多线程里用 HashMap
> 5. **需要有序就指定 Map 工厂**：`LinkedHashMap::new` 或 `TreeMap::new`
