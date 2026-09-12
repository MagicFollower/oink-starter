---
title: DateTime 日期时间增强 —— 让 Date 会说话、会算术
weight: 4
description: 老项目里 Date 无处不在，但裸的 Date 只有毫秒数、SimpleDateFormat 不能多线程共用、Calendar 改个字段要翻十几步。本篇以 hutool-core 的 DateTime 为主线：它与 Date 的兼容性为什么是「零成本接入」、高频场景如何一行搞定、mutable 可变语义的坑在哪里，以及与 JDK java.time 的分工。
---

仓库里十个老项目有九个在用 `java.util.Date`。它不是不能用，而是用起来处处硌手：格式化怕线程、加减要借 Calendar、打日志是一串英文。hutool-core 给出的答案是一个「增强版 Date」——`DateTime`：**它继承自 Date，却能格式化、能算术、能解析**。本篇从 Date 的三大痛点切入，逐步走到 DateTime 的日常用法与可变语义的坑。

## 一、先看没有它时的三处硌手

```java
// 痛点 1：SimpleDateFormat 不能多线程共用（JDK javadoc 明言 "Date formats are not synchronized"）
public class OrderController {
    private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd");
    // 多个请求并发调用 SDF.format(...)：偶发 NumberFormatException，或干脆输出错误日期
}

// 痛点 2：算「3 天后当天的最后一刻」，要跟 Calendar 打十来行交道
Calendar cal = Calendar.getInstance();
cal.setTime(orderTime);
cal.add(Calendar.DAY_OF_MONTH, 3);
cal.set(Calendar.HOUR_OF_DAY, 23);
cal.set(Calendar.MINUTE, 59);
cal.set(Calendar.SECOND, 59);
cal.set(Calendar.MILLISECOND, 0);
Date deadline = cal.getTime();

// 痛点 3：Date 自己不识字——打印出来人读不懂，取字段还得用已废弃的 getMonth()
System.out.println(new Date());   // Sat Sep 12 10:00:00 CST 2026（英文、带时区缩写，对用户毫无意义）
```

三处硌手指向同一个缺口：**Date 只有「毫秒数」这一个真本事，看、算、读全靠外援**。

> ### 💡 新人小结：把日期时间想成快递单
>
> - `java.util.Date` 是**一张裸运单**：上面只有一个毫秒数（运单编号）。快递系统内部流转全靠它，但顾客看不懂，窗口也不能直接在上面写字。
> - `SimpleDateFormat` 是**人工登记窗口**：一次只能服务一位顾客（线程不安全），多人挤一个窗口就会串单。
> - `Calendar` 是**老式操作手册**：改个收件日期要按手册翻十几个步骤，每步都可能翻错页。
> - `DateTime` 是**智能运单**：它本质上还是那张 Date 运单（`DateTime extends Date`），所有认 Date 的老窗口照单全收；但它自带打印格式、能直接加减天数、能报出年月日。
> - `DateUtil` 是**服务台总览牌**：把常用操作做成静态方法，一行一个动作。

本文学习路线（递进关系，自上而下）：

```text
与 Date 的兼容性（为什么敢说零成本接入）
        ↓
当前时间与格式化 → 解析字符串 → 时间算术（可变坑）→ 字段获取（0 基坑）
        ↓
间隔与年龄 → 与 Java 8 时间类互通 → 演进对比与选型守则
```

## 二、专有名词表

| 术语 | 全称 | 含义 | 本文角色 |
|------|------|------|---------|
| 时间戳 | Timestamp | 自 1970-01-01 00:00:00 UTC 起的毫秒数 | Date 内部唯一的真数据 |
| SimpleDateFormat | — | JDK 的日期格式化类 | 线程不安全，是要被替换的痛点 |
| FastDateFormat | — | Hutool 的线程安全格式化器 | `DateUtil.format` 的底层引擎 |
| 线程安全 | Thread-safe | 多线程同时调用不出错 | 格式化选型的分水岭 |
| 可变对象 | Mutable object | 方法会修改自身字段的返回值对象 | DateTime 的默认行为，本篇最大的坑 |
| 链式调用 | Method chaining | 调用返回自身，可连续点下去 | DateTime 的日常写法 |
| 门面 | Facade | 一组静态方法对外统一入口 | `DateUtil` 之于 `DateTime` |
| GAV | GroupId/ArtifactId/Version | Maven 坐标三要素 | 引入 hutool-core 的钥匙 |

## 三、引入依赖

```xml
<!-- 只要日期时间等核心能力：hutool-core 即可（本文基于 5.8.47） -->
<dependency>
    <groupId>cn.hutool</groupId>
    <artifactId>hutool-core</artifactId>
    <version>5.8.47</version>
</dependency>
```

**依赖选择速查**：

| 坐标 | 适用场景 | 说明 |
|------|---------|------|
| `cn.hutool:hutool-core` | 只想用 Date/Str/Coll 等核心工具 | 本篇主角 DateTime 在此模块 |
| `cn.hutool:hutool-all` | 想一次引入全部模块（http/json/db 等） | 官方模块汇总，最终以多个 jar 落地，可 exclude 裁剪 |

官方 README 声明：**Hutool 5.x 支持 JDK8+**（JDK7 请用已停止更新的 4.x）；5.x 对 Android 平台未做测试、不保证全部可用。另注意：Hutool 6.x 已启用新坐标 `org.dromara.hutool:*`（Maven Central 可查，2025 年起持续发布），升级前请对照官方迁移说明——本文以社区存量项目主流的 5.x 为准。

## 四、与 Date 的兼容性：零成本接入的底气

兼容性的全部秘密在一行类声明上（5.8.47 源码）：

```java
public class DateTime extends Date {
```

**DateTime 是 Date 的子类**，由此派生出一整套「哪里都能去」的通行证：

| 兼容场景 | 写法 | 为什么可行 |
|---------|------|-----------|
| 赋给 Date 变量 | `Date d = DateUtil.date();` | 子类即父类，向上转型天然合法 |
| 传给收 Date 的老接口 | `preparedStatement.setTimestamp(1, new Timestamp(dt.getTime()));` | 继承的方法全在，`getTime()` 直通毫秒数 |
| 放进 Date 集合 | `List<Date> list = new ArrayList<>(); list.add(dt);` | 泛型按父类收 |
| 与 Date 互转 | `DateTime dt = DateTime.of(date); Date back = dt.toJdkDate();` | `of` 对已是 DateTime 的入参直接返回自身；`toJdkDate()` 返回 `new Date(getTime())` **拷贝** |
| 接收 Java 8 时间对象 | `new DateTime(instant)`、`new DateTime(zonedDateTime)` | 构造器重载覆盖 Instant/ZonedDateTime/TemporalAccessor |

> ⚠️ 注意 `toJdkDate()` 的语义：它返回一个**新的纯 Date 拷贝**，不是把 this 强转出去。想「脱掉 DateTime 外衣但仍共享同一份毫秒数」，直接向上转型 `Date d = dt;` 即可——两者本就指向同一个对象，只是编译期类型不同。

**打日志也顺带受益**：DateTime 覆写了 `toString()`，默认输出 `yyyy-MM-dd HH:mm:ss`，不再是英文长串。若某些框架或日志规约强制要 JDK 原生格式，可全局切回：`DateTime.setUseJdkToStringStyle(true)`（静态开关，5.7.21+）。

## 五、方法选型速查表

| 想做什么 | 首选写法 | 备注 |
|---------|---------|------|
| 当前时间对象 | `DateUtil.date()` | 返回 DateTime |
| 当前时间字符串 | `DateUtil.now()` | yyyy-MM-dd HH:mm:ss |
| 当前日期字符串 | `DateUtil.today()` | yyyy-MM-dd |
| 格式化任意 Date | `DateUtil.format(date, "yyyy/MM/dd")` | 底层 FastDateFormat，线程安全 |
| 解析常见格式串 | `DateUtil.parse(str)` | 按长度智能识别，空串返回 null |
| 解析指定格式串 | `DateUtil.parse(str, "yyyy/MM/dd")` | 不识别就按格式来，最稳 |
| 时间加减 | `DateUtil.offset(date, DateField.DAY_OF_YEAR, 3)` | 静态版不改原对象 |
| 实例链式加减 | `dt.offset(DateField.DAY_OF_YEAR, 3)` | **默认修改自身并返回 this** |
| 取当天最后一刻 | `DateUtil.endOfDay(date)` | 在 DateUtil 上，返回新 DateTime |
| 两个日期差几天 | `DateUtil.betweenDay(begin, end, true)` | true=先抹掉时分秒再算 |
| 生日算年龄 | `DateUtil.ageOfNow(birthday)` | 传字符串或 Date 均可 |
| 转 LocalDateTime | `DateUtil.toLocalDateTime(date)` | Java 8 桥梁 |

## 六、高频场景实战

### 场景一：当前时间与格式化

```java
import cn.hutool.core.date.DatePattern;
import cn.hutool.core.date.DateUtil;
import cn.hutool.core.date.DateTime;

DateTime now = DateUtil.date();                          // 当前时间，DateTime 类型
String full = DateUtil.now();                            // 输出: 2026-09-12 10:00:00
String day  = DateUtil.today();                          // 输出: 2026-09-12

// 三种格式化姿势
String s1 = DateUtil.format(now, "yyyy/MM/dd HH:mm");    // 输出: 2026/09/12 10:00
String s2 = now.toString("yyyy年MM月dd日");               // 输出: 2026年09月12日（DateTime 实例版）
String s3 = now.toString();                              // 输出: 2026-09-12 10:00:00（覆写过的 toString）

// 常用格式不必手写，DatePattern 已预置常量（含对应的 static final 格式化器）
String norm = now.toString(DatePattern.NORM_DATETIME_PATTERN);   // yyyy-MM-dd HH:mm:ss
String pure = now.toString(DatePattern.PURE_DATETIME_PATTERN);   // yyyyMMddHHmmss
```

**参数解释**：`DateUtil.format(date, format)` 的 null 语义——date 为 null **或** format 为空白时返回 null（源码前置判空），不抛异常；入参若是 DateTime，格式化还会沿用其内部时区。`toString(String format)` 与静态版同源，底层都是 FastDateFormat。

**和 SimpleDateFormat 的正面对比**：

| 维度 | SimpleDateFormat | DateUtil.format / DatePattern 常量 |
|------|-----------------|----------------------------------|
| 线程安全 | 否（JDK javadoc 明言 not synchronized） | 是，可多处共享 |
| 复用方式 | 每次新建或 ThreadLocal 包装 | `DatePattern.NORM_DATETIME_FORMAT` 等直接 static final 常量 |
| null 入参 | 抛 NullPointerException | 约定返回 null |

### 场景二：解析字符串——智能识别与显式指定

```java
// 1. 泛用版：按长度智能识别常见格式（yyyy-MM-dd HH:mm:ss、yyyy/MM/dd、yyyy.MM.dd、yyyy年MM月dd日 等）
DateTime t1 = DateUtil.parse("2026-09-12 10:00:00");
DateTime t2 = DateUtil.parse("2026/09/12");
DateTime t3 = DateUtil.parse("2026年09月12日");

// 2. 专项版：语义更明确
DateUtil.parseDateTime("2026-09-12 10:00:00");   // 日期+时间，四种写法自动归一
DateUtil.parseDate("2026-09-12");                // 只要日期，忽略时分秒
DateUtil.parseTime("10:00:00");                  // 只有时间，日期部分默认 1970-01-01
DateUtil.parseTimeToday("10:00:00");             // 只有时间，日期部分默认今天（5.x 可用）

// 3. 显式指定格式：来源不可靠的字符串，别赌智能识别
DateTime t4 = DateUtil.parse("12/09/2026", "dd/MM/yyyy");

// 4. 多格式逐个尝试：全都不匹配时抛 DateException
DateTime t5 = DateUtil.parse(str, "yyyy-MM-dd", "yyyy/MM/dd", "yyyyMMdd");
```

**参数解释**：单参 `parse` 对空白串返回 null、对纯数字串按数字规则处理（时间戳/定长格式），其余按长度识别；识别不了或格式不符时抛 `DateException`。`parse(str, patterns...)` 的官方 javadoc 原话是「传入的日期格式会逐个尝试，直到解析成功……否则抛出 DateException 异常」。

**选型提示**：内部可信数据（数据库导出、自家前端）用泛用 `parse` 省心；**外部输入（用户手填、第三方接口）一律显式传格式**——「01/02/2026」这种串，智能识别猜不出它是 1 月 2 日还是 2 月 1 日。

### 场景三：时间算术——可变语义是最大的坑

```java
DateTime launch = DateUtil.parse("2026-09-12 10:00:00");

// 实例版 offset：默认【修改自身】并返回 this！
DateTime a = launch.offset(DateField.DAY_OF_YEAR, 3);
System.out.println(launch);   // 输出: 2026-09-15 10:00:00（原对象被改了！）
System.out.println(a == launch);   // 输出: true（同一个对象）

// offsetNew：总是返回新对象，原对象不动
DateTime b = launch.offsetNew(DateField.DAY_OF_YEAR, 3);
System.out.println(launch);   // 输出: 2026-09-15 10:00:00（a 那步已改）
System.out.println(b);        // 输出: 2026-09-18 10:00:00

// 静态版：基于拷贝运算，原 date 永不改动（DateUtil.offset 内部先 dateNew(date) 再 offset）
Date origin = new Date();
DateUtil.offset(origin, DateField.DAY_OF_YEAR, 3);
System.out.println(origin);   // 输出: 原时间，毫秒未变

// 设定字段：同样遵循可变规则；「当天最后一刻」这样拼
DateTime end = DateUtil.parse("2026-09-12 10:00:00")
        .setField(DateField.HOUR_OF_DAY, 23)
        .setField(DateField.MINUTE, 59)
        .setField(DateField.SECOND, 59);
System.out.println(end);      // 输出: 2026-09-12 23:59:59

// 不想可变？一次性关闭（此后 offset/setField 都返回新对象）
DateTime immutable = DateUtil.date().setMutable(false);
```

**参数解释**：`DateField` 是对 Calendar 字段的枚举封装（`DAY_OF_YEAR`/`HOUR_OF_DAY` 等），offset 的 `ERA` 字段不支持，传入会抛 `IllegalArgumentException`。偏移量正数向后、负数向前。

**源码一句话**：`offset` 的实现是 `mutable ? this : ObjectUtil.clone(this)`——`mutable` 默认 `true`，这就是「默认改自身」的出处。可变换来的是链式调用时少一次对象分配，代价是共享引用时的副作用。

> 💡 **新人小结**：把 DateTime 想成**在原件上改单还是复写新单**——`offset` 是在原件上改（省纸，但原件变了），`offsetNew` 是复写一份再改（多一张纸，旧单完好）。拿不准时用 `offsetNew` 或静态版 `DateUtil.offset`，最保险。

另外两个高频「整点」操作也在 **DateUtil** 上（不在 DateTime 实例上，`date.beginOfDay()` 是编译不过的）：

```java
DateUtil.beginOfDay(launch);    // 输出: 2026-09-12 00:00:00（返回新 DateTime）
DateUtil.endOfDay(launch);      // 输出: 2026-09-12 23:59:59
DateUtil.beginOfMonth(launch);  // 输出: 2026-09-01 00:00:00
DateUtil.endOfMonth(launch);    // 输出: 2026-09-30 23:59:59（自动处理大小月）
```

### 场景四：取字段——先看清取值范围再下手

| 方法 | 取值范围 | 易错点 |
|------|---------|--------|
| `year()` | 如 2026 | 无 |
| `month()` | **0 ~ 11**（0=1 月） | 沿袭 Calendar.MONTH 的 0 基，别直接展示给用户 |
| `monthBaseOne()` | 1 ~ 12 | 5.4.1 起提供，专为纠正上一行 |
| `quarter()` | 1 ~ 4 | 官方从 1 开始计数 |
| `dayOfMonth()` | 1 ~ 31 | 无 |
| `dayOfWeek()` | 1 ~ 7（**1=周日**） | 沿袭 Calendar.DAY_OF_WEEK，与「周一=1」的直觉相反 |
| `monthEnum()` | Month 枚举 | 想要枚举语义（中文名、星期几等衍生判断）用它 |
| `isLeapYear()` | true/false | 按 year() 判断 |

```java
DateTime t = DateUtil.parse("2026-09-12 10:00:00");
System.out.println(t.month());        // 输出: 8（九月返回 8！0 基）
System.out.println(t.monthBaseOne()); // 输出: 9
System.out.println(t.dayOfWeek());    // 输出: 7（2026-09-12 是周六，周六=7）
System.out.println(t.isLeapYear());   // 输出: false
```

官方 javadoc 对 0 基的原话：「由于 Calendar 中的月份按照 0 开始计数，导致某些需求容易误解，因此如果想用 1 表示一月，2 表示二月则调用此方法（monthBaseOne）」。**给用户展示月份，永远用 `monthBaseOne()` 或格式化输出，不要裸用 `month()`。**

### 场景五：间隔与年龄

```java
DateTime begin = DateUtil.parse("2026-09-01 08:00:00");
DateTime end   = DateUtil.parse("2026-09-12 20:00:00");

// 相差毫秒/指定单位的绝对值（isAbs 默认 true，自动忽略先后顺序）
long ms   = DateUtil.between(begin, end, DateUnit.MS);
long days = DateUtil.between(begin, end, DateUnit.DAY);
System.out.println(days);            // 输出: 11

// 只关心「差几天」：isReset=true 先把双方归到当天 00:00:00 再算
long dayGap = DateUtil.betweenDay(DateUtil.parse("2026-09-01 23:00:00"),
                                  DateUtil.parse("2026-09-02 01:00:00"), true);
System.out.println(dayGap);          // 输出: 1（跨了自然日，而不是按 2 小时折算 0）

// 生日算年龄（字符串或 Date 都收）
int age = DateUtil.ageOfNow("2000-06-15");
System.out.println(age);             // 输出: 26（按当前日期计算法定年龄）
```

**参数解释**：`between` 拿到的单位由 `DateUnit` 决定（MS/SECOND/MINUTE/HOUR/DAY…）；`betweenDay` 的 `isReset=true` 是「自然日」语义——先 `beginOfDay` 抹掉时分秒再相减；传 false 则按 24 小时精确折算。若需要「负数表示 end 早于 begin」的方向感，用四参 `between(begin, end, unit, false)` 关闭绝对值。

### 场景六：与 Java 8 时间类互通——新旧两界的桥

Hutool 5.x 运行在 JDK8+ 上，`DateTime` 与 `java.time` 的互转是双车道：

```java
// java.time → DateTime（构造器重载直收）
LocalDateTime ldt = LocalDateTime.now();
DateTime fromLdt = new DateTime(ldt);            // TemporalAccessor 构造器
DateTime fromIns = new DateTime(Instant.now());  // Instant 构造器

// DateTime/Date → LocalDateTime
LocalDateTime back = DateUtil.toLocalDateTime(now);

// 字符串直出 LocalDateTime（不经 DateTime）
LocalDateTime ldt2 = DateUtil.parseLocalDateTime("2026-09-12 10:00:00");
```

**分工建议**：老接口边界、JDBC、旧框架的入参出参继续用 Date/DateTime 兜住；**核心域模型的新代码优先 java.time**（不可变、API 清晰），在边界用上面两行完成摆渡——这也是官方 `LocalDateTimeUtil` 与 `toLocalDateTime` 存在的意义。

## 七、演进对比：三件套 vs DateTime 链式

需求：订单下单时间 `orderTime`，算「3 天后当天最后一刻」，输出 `yyyy-MM-dd HH:mm:ss`。

```java
// 旧方案：Date + Calendar + SimpleDateFormat 三件套
Calendar cal = Calendar.getInstance();
cal.setTime(orderTime);
cal.add(Calendar.DAY_OF_MONTH, 3);
cal.set(Calendar.HOUR_OF_DAY, 23);
cal.set(Calendar.MINUTE, 59);
cal.set(Calendar.SECOND, 59);
cal.set(Calendar.MILLISECOND, 0);
String deadline = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(cal.getTime());

// 新方案：DateUtil + DateTime 链式
String deadline2 = DateUtil.endOfDay(
        DateUtil.offset(orderTime, DateField.DAY_OF_YEAR, 3)).toString();
```

| 维度 | 三件套 | DateUtil/DateTime |
|------|-------|-------------------|
| 代码量 | 8 行 | 2 行 |
| 线程安全 | SimpleDateFormat 需额外处理 | 格式化链路天然线程安全 |
| 字段语义 | Calendar 字段 int 常量，易传错 | DateField 枚举，编译期可查 |
| 可读性 | 步骤式，读代码像查手册 | 意图式，读到方法名即懂 |
| 副作用 | cal 对象被改（局部变量尚可） | 静态版基于拷贝，原对象无感 |
| 学习成本 | Calendar 体系概念多 | 会 Date 即会用，方法名自解释 |

## 八、互补守则与选型

```text
入参/出参/集合里已经是 Date（老接口、JDBC、旧框架）
        → DateTime 直接顶上（extends Date，零适配）

字符串与日期互转、加减偏移、算间隔
        → DateUtil 静态门面一行搞定

需要连续多次调整、且调用链里想继续当 Date 传
        → DateTime 实例链式（共享引用场景记得 offsetNew / setMutable(false)）

新写的核心域模型、复杂跨时区运算
        → 优先 JDK java.time，边界处用 toLocalDateTime/parseLocalDateTime 摆渡
```

**性能说明**：`format` 的底层 FastDateFormat 是线程安全设计，`DatePattern` 更是把常用格式预置成 static final 格式化器常量（如 `NORM_DATETIME_FORMAT`），反复格式化零额外构建成本；`DateTime` 的链式可变（默认复用自身）也省去了中间对象分配。常规业务规模下这些都构不成瓶颈，不必过度设计。

**社区实践**：格式串尽量引用 `DatePattern` 常量而不是手写字符串（拼写错误在编译期就能暴露——常量不存在直接报红）；Hutool 官方 README 明确 5.x 对 Android 未做测试，移动端引入前先验证；关注 6.x 新坐标的迁移说明，但不必为迁移而迁移——5.x 仍在持续维护（本文基于 5.8.47）。

## 九、Q&A：高频疑问

**Q1：SimpleDateFormat 就不能继续用吗？**

能用，但要守住两条之一：每次方法内新建（浪费），或 ThreadLocal 各线程一份（样板代码）。而格式化的主流正解是 JDK8 的 `DateTimeFormatter`（不可变线程安全）或本文的 FastDateFormat 路线——`DateUtil.format` 已经替你选好了。

**Q2：`month()` 明明是 9 月却返回 8，是 bug 吗？**

不是。`month()` 直接映射 Calendar.MONTH 的 0 基设计（0=1 月）。展示与业务判断用 `monthBaseOne()`（1~12），输出字符串交给格式化。同理 `dayOfWeek()` 返回 1~7 且 1=周日，别按「周一=1」猜。

**Q3：`offset` 把共享的日期对象改了，怎么办？**

三条路按场景选：不需要原对象就用可变链式；需要保留原对象用 `offsetNew`（或静态版 `DateUtil.offset`，它内部基于拷贝）；整条链路都想要不可变风格，构造后立即 `setMutable(false)`。

**Q4：`date.beginOfDay()` 为什么编译不过？**

「归零到起点」这类操作在 `DateUtil` 静态门面上：`DateUtil.beginOfDay(date)`/`endOfDay`/`beginOfMonth`/`endOfMonth`，都返回**新的** DateTime。DateTime 实例的强项是 offset/setField/取字段与链式拼装，这些整点操作不在这条链上。

**Q5：`parse` 什么情况返回 null，什么情况抛异常？**

空白串返回 null（源码前置判空）；非空但识别不了、或与指定格式不符时抛 `DateException`。`parse(str, patterns...)` 是逐个格式尝试、全部失败才抛。外部数据建议显式传格式 + 捕获异常兜底。

**Q6：hutool-all 和 hutool-core 怎么选？**

按需引入选 hutool-core（体积小，本篇 DateTime 就在里面）；确定会用到 http/json/db/extra 等多个模块再上 hutool-all（官方模块汇总，可 exclude 裁剪）。二者坐标不同，混引容易出现版本漂移，统一选一种。

**Q7：老项目里 Date 无处不在，怎么渐进迁移？**

不必全量替换：在新代码里用 `DateUtil.parse/format/offset` 收敛散落的 SimpleDateFormat 和 Calendar；接口边界用 `DateTime.of(date)` 包一层做运算、算完 `toJdkDate()` 还回去；核心域模型再逐步切 java.time。DateTime 与 Date 的继承关系保证了这条迁移路每一步都能编译。

## 十、要点总结

1. **兼容零成本**：`DateTime extends Date`，赋值、传参、进集合处处可用；`toJdkDate()` 返回的是拷贝，想共享毫秒数直接向上转型
2. **格式化走 FastDateFormat**：线程安全、DatePattern 预置常量；`format` 对 null date/blank format 约定返回 null
3. **解析分层**：泛用 `parse` 智能识别但对外部输入要显式传格式；`parseTime` 默认 1970-01-01、`parseTimeToday` 默认今天，语义别用混
4. **可变是默认**：`offset`/`setField` 默认修改自身并返回 this（源码 `mutable ? this : clone`）；保原件用 `offsetNew`、`DateUtil.offset` 或 `setMutable(false)`
5. **字段有基约定**：`month()` 0 基、`dayOfWeek()` 周日=1；展示用 `monthBaseOne()` 或格式化，别裸输出
6. **静态门面补位**：beginOfDay/endOfDay/beginOfMonth/endOfMonth 在 `DateUtil` 上返回新对象；与 java.time 互通走 `toLocalDateTime`/`parseLocalDateTime` 双向桥

---

**收尾三句话**：Date 是裸运单，DateTime 是自带打印与算术的智能运单——继承关系让它无障碍进出所有老窗口；`offset` 默认改原件，这是便利也是唯一的坑，记住 `offsetNew` 这张复写纸；新代码的域模型交给 java.time，新旧边界交给 DateTime 摆渡，各守各的城。
