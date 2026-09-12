---
title: Lombok 命名规范与核心注解
description: Lombok getter/setter 命名规则与 Jackson 字段名错位（aNum 变 anum）的深度分析、@RequiredArgsConstructor 构造器注入与 Spring Boot 集成、@FieldNameConstants 消灭魔法字符串。
weight: 2
---

# 为什么注解没坏，字段却「变味」了？

想象你是一个电商后端开发，接手了一个「灵异事件」排查：

- 前端反馈：接口传 `{"aNum": 5}`，后端拿到的却是 `null`；抓包对比老接口，发现线上 JSON 里这个字段叫 **`anum`**——全小写。没人改过代码，字段名自己「变了」
- 排查注入问题：`@Qualifier("mysqlDataSource")` 明明写在字段上，启动却报 `NoUniqueBeanDefinitionException`——注解像被丢掉了一样
- 改了个实体字段名 `userName`，编译一片绿，上线后 MyBatis 查询全部报「列不存在」——魔法字符串没人替你把关

| 事故 | 表象 | 真正的根源 |
|------|------|-----------|
| `aNum` 变 `anum` | 反序列化拿不到值 | Lombok 生成规则 + Jackson 属性名推导规则**不一致** |
| `@Qualifier` 失效 | 多 Bean 注入报错 | 注解没被复制到 Lombok **生成的构造器参数**上 |
| 列名字符串失效 | 运行时才报错 | 字段名以**字符串**引用，重构不联动 |

这三件事的共同点：**问题不在注解本身，而在注解生成的代码与下游框架的「约定」之间**。

> ### 💡 新人小结：Lombok 的边界在哪？
>
> 把 Lombok 想象成「盖章机」：
> - 它只负责在你画好的位置盖章（生成 getter/setter/构造器）
> - 盖出来的章**符合它自己的规则**（首字母大写），不一定符合 JavaBeans 规范原文
> - 下游框架（Jackson、Spring、MyBatis）各自按**自己的阅读习惯**解释这些章
>
> **当盖章规则与阅读习惯不一致时，字段名就在中间「变了味」——理解每套规则，才能堵住缝隙**。

**学习路线图**：

```text
命名规范 → RequiredArgsConstructor → FieldNameConstants
谁改了我的名字    构造器注入的坑       消灭魔法字符串
三套规则对照      生成规则与集成       编译期常量联动
```

---

## 一、getter/setter 生成规范与 Jackson 兼容性

### 痛点：三套规则，各说各话

字段名的「真相」取决于**谁在看**。同一个字段 `aNum`，三套规则给出三个答案：

| 规则体系 | 规则内容 | `aNum` 的结果 | 使用方 |
|---------|---------|--------------|--------|
| **JavaBeans 官方规范**（`Introspector.decapitalize`） | 方法名剥掉 get/set 前缀后：**前两个字母均大写 → 属性名原样保留**；否则首字母转小写 | `getaNum()` → `aNum`（规范期望的 getter 写法） | Spring `BeanUtils`、`java.beans.Introspector` |
| **Lombok 生成规则** | 字段名**首字母直接大写**拼前缀（不看第二个字母） | `aNum` → `getANum()` / `setANum()` | Lombok（与部分 IDE 生成器一致） |
| **Jackson 默认推导**（legacy mangling） | 剥掉前缀后，**前导连续大写字母全部转小写**，直到遇到非大写字符 | `getANum()` → `anum` | Spring Boot Web 默认 `ObjectMapper` |

三套规则单独看都「有道理」，叠在一起就出事。下面逐环拆解。

### 现象复现：5 分钟还原事故

最小可运行环境：Spring Boot Web + Lombok。

```java
// ========== SkuDTO.java：Lombok 默认生成 ==========
@Data
public class SkuDTO {
    private Long id;
    private String name;
    private Integer aNum;   // 「A 数量」，小写开头 + 第二个字母大写
}
```

```java
// ========== SkuController.java：原样回显 ==========
@RestController
public class SkuController {

    @PostMapping("/sku")
    public SkuDTO echo(@RequestBody SkuDTO dto) {
        return dto;   // 序列化回去，看看字段名变成了什么
    }
}
```

请求与响应：

```text
请求:  curl -X POST http://localhost:8080/sku \
         -H "Content-Type: application/json" \
         -d '{"id":1,"name":"sku","aNum":5}'

响应:  {"id":1,"name":"sku","anum":5}     ← aNum 变成了 anum

反序列化: dto.getANum() == null          ← 传 aNum 根本没被绑定
```

用 `javap` 验证 Lombok 到底生成了什么：

```text
$ javap SkuDTO
public java.lang.Long getId();
public void setId(java.lang.Long);
...
public java.lang.Integer getANum();      ← 注意：是 getANum，不是 getaNum
public void setANum(java.lang.Integer);
```

### 原因链分析：字段名的四次「变形」

```text
源码字段 aNum
  ↓ Lombok 生成访问器：首字母直接大写
getter = getANum() / setter = setANum()
  ↓ Jackson 剥掉 get/set 前缀
得到候选名 "ANum"
  ↓ Jackson legacy mangling：前导连续大写 A、N、U 全部转小写
属性名 = "anum"
  ↓ 结果对比
"anum" ≠ "aNum"  → 序列化输出 anum，反序列化只认 anum
```

每个环节单独看都符合各自实现的设计：

1. **Lombok**：把首字母大写是最简单、可预期的实现，社区长期如此（[Lombok GitHub 已知问题讨论](https://github.com/projectlombok/lombok/issues)多年保持兼容不改）
2. **Jackson**：默认关闭 `USE_STD_BEAN_NAMING`，走自己的 legacy 规则，把连续大写「压平」成小写
3. **JavaBeans 规范**：`Introspector.decapitalize("ANum")` 因前两个字母均大写而**原样返回** `ANum`——与 Jackson 的 `anum` 又不一样

> ### 💡 新人小结：为什么会变成 anum？
>
> 把字段名的流转想象成「传话游戏」：
> - Lombok 写下的名字是 `getANum`（它只管把首字母盖章变大写）
> - Jackson 读书时习惯「连续大写压平」——读到 `ANum` 就念成 `anum`
> - Spring 的规范派则念成 `ANum`
>
> **同一个人写的名字，三个读者读出三个版本——错位不是谁写错了，而是规则没对齐**。

### 高风险命名模式

只要**字段名以小写字母开头、第二个字母是大写**，就会触发整套错位：

| 字段名 | Lombok 生成 | Jackson 属性名 | Introspector 属性名 | 与字段名一致？ |
|--------|------------|---------------|--------------------|--------------|
| `aNum` | `getANum()` | `anum` | `ANum` | ❌ 三家不同 |
| `uName` | `getUName()` | `uname` | `UName` | ❌ 三家不同 |
| `nCode` | `getNCode()` | `ncode` | `NCode` | ❌ 三家不同 |
| `qpsLimit` | `getQpsLimit()` | `qpslimit` | `QpsLimit` | ❌ 三家不同 |
| `userName` | `getUserName()` | `userName` | `userName` | ✅ 正常命名无风险 |
| `a`（单字母） | `getA()` | `a` | `a` | ✅ 单字母安全 |

**布尔字段的附加坑**：`boolean isSuccess` 这类 `is` 前缀命名——getter 生成 `isSuccess()`，Jackson 会剥掉 `is` 前缀，序列化输出为 `success`，与字段名又不一致。《阿里巴巴 Java 开发手册》对此有【强制】条款：**POJO 布尔类型变量不要加 `is` 前缀**。

### 五种解决方案对比

#### 方案一：预防性改名（根治）

```java
// ========== 推荐写法 ==========
private Integer numA;      // 或 quantityA：数字后置，避开小写+大写模式

// ========== 不推荐写法（仅展示） ==========
// ❌ private Integer aNum;  —— 一颗移动的雷
```

改名后所有框架推导全部回到 `numA`，无需任何额外配置。

#### 方案二：@JsonProperty 显式绑定

```java
@Data
public class SkuDTO {
    @JsonProperty("aNum")      // Jackson 序列化/反序列化都认 aNum
    private Integer aNum;
}
```

- Jackson 侧完全正确（输出 `aNum`、接收 `aNum`）
- **但只管 Jackson 一家**：`BeanUtils.copyProperties` 走 Introspector 得到 `ANum`，MyBatis 走 setter 推导得到 `ANum`——反射系框架仍然错位
- 每个高危字段都要记得标，**遗漏一个就是一个隐形坑**

#### 方案三：手写符合规范的访问器（多框架一致）

```java
// ========== 推荐写法：无法改名时的完整形态 ==========
@Data
public class SkuDTO {
    private Long id;
    private String name;

    // 第一步：排除 Lombok 对该字段的生成
    @Getter(AccessLevel.NONE)
    @Setter(AccessLevel.NONE)
    private Integer aNum;

    // 第二步：手写 getaNum / setaNum（首字母不大写）
    // Jackson 剥前缀得 "aNum"，首字母已小写 → legacy mangling 原样返回
    public Integer getaNum() {
        return aNum;
    }

    public void setaNum(Integer aNum) {
        this.aNum = aNum;
    }
}
```

**两个细节缺一不可**：

1. **必须排除 Lombok 生成**。若保留类级 `@Data` 而不排除，编译产物里会同时存在 `getaNum()` 和 `getANum()`——Jackson 会解析出 `aNum` 和 `anum` **两个属性**，序列化冗余、反序列化歧义
2. **首字母坚决不大写**。`getaNum` 剥前缀后是 `aNum`，Jackson 的 legacy 规则对「已小写开头」的名称原样放行，Introspector、MyBatis 同样得到 `aNum`——**所有框架第一次达成一致**

#### 方案四：全局切换 Jackson 标准命名（不推荐）

```java
// ========== 仅展示，不要这样做 ==========
@Bean
public Jackson2ObjectMapperBuilderCustomizer stdNaming() {
    return builder -> builder.featuresToEnable(MapperFeature.USE_STD_BEAN_NAMING);
    // ❌ getANum() 解析为 "ANum"——依然不等于 aNum，且影响全站所有接口
}
```

结果只是从 `anum` 换成 `ANum`，**仍然不是字段名 `aNum`**，还引入全站行为变更。

#### 方案五：自定义 PropertyNamingStrategy（仅特殊场景）

针对特定命名模式写全局翻译策略。实现成本高、排错难，除非整个存量库都是这类命名，否则不建议。

### 兼容性矩阵与选型决策

| 方案 | Jackson 属性 | BeanUtils 属性 | MyBatis 属性 | Swagger 文档 | 适用场景（侵入性） |
|------|-------------|---------------|-------------|-------------|------------------|
| 默认（Lombok `getANum`） | `anum` ❌ | `ANum` ❌ | setter 推导 `ANum` + 字段兜底 `aNum` | `anum` ❌ | 撞运气 |
| ① 改名 `numA` | `numA` ✅ | `numA` ✅ | `numA` ✅ | `numA` ✅ | 新字段首选（改字段名） |
| ② `@JsonProperty("aNum")` | `aNum` ✅ | `ANum` ❌ | `ANum` ❌ | `aNum` ✅ | 仅 Jackson 读写字段名（每字段一条注解） |
| ③ 手写 `getaNum/setaNum` | `aNum` ✅ | `aNum` ✅ | `aNum` ✅ | `aNum` ✅ | 无法改名 + 多框架一致（字段级排除 + 两个方法） |
| ④ `USE_STD_BEAN_NAMING` | `ANum` ❌ | `ANum` ❌ | `ANum` ❌ | `ANum` ❌ | 无（全局配置） |

两列补充说明：

- **BeanUtils 列**：`copyProperties` 基于 `java.beans.Introspector` 推导属性名——`getANum` 按规范规则得到 `ANum`。同一实体自复制（源目标同类）不受影响，但从 Lombok 实体复制到手写 `getaNum` 的类时会因属性名不一致而**静默丢失字段**
- **Swagger 列**：springdoc-openapi 直接复用 Jackson 的属性推导，接口文档显示的属性名与实际序列化结果一致——默认同样显示 `anum`，方案②③修正后显示 `aNum`

**决策树**：

```text
能否修改字段名？
│
├─ 能（新字段、内部模型）
│   └─ 方案①：改用 numA 等规范命名 —— 一次根治
│
├─ 不能（外部协议约定、历史接口）
│   ├─ 字段名只被 Jackson 读写
│   │   └─ 方案②：@JsonProperty("aNum") —— 最小改动
│   └─ BeanUtils/MyBatis 等也按字段名复制、映射
│       └─ 方案③：手写 getaNum/setaNum + 排除注解 —— 全框架一致
│
└─ 方案④/⑤ 全局开关 —— 不碰
```

**最终推荐**：

1. **新代码预防优先**：POJO 字段避开「小写开头 + 第二个字母大写」模式（`numA` 而非 `aNum`），这是唯一零成本根治的方案
2. **存量兼容用方案三**：对接既有协议无法改名时，手写 `getaNum()/setaNum()` 并配 `@Getter(AccessLevel.NONE) + @Setter(AccessLevel.NONE)` 排除——它让 Jackson、Spring、MyBatis 三套规则第一次输出同一个名字，也是实战中验证过的稳定方案
3. **方案二作为补充**：当字段只被 Jackson 使用时可用，但要意识到它对反射系框架无效

> ### 💡 新人小结：命名错位怎么防？
>
> 把 POJO 字段名想象成「快递单上的收件人姓名」：
> - 姓名写得越规范（`numA`），所有快递员（框架）都能读对
> - 遇到历史遗留的「花名」（`aNum`），就要亲自写一张「确认条」（手写访问器）贴在包裹上
>
> **新字段规范命名，老字段手写访问器——别指望全局开关替你擦屁股**。

---

## 二、@RequiredArgsConstructor 与 Spring Boot 集成

### 痛点：注入写的越多，错的可能越多

字段注入的老三样问题：

```java
// ========== 不推荐写法（仅展示） ==========
@Service
public class OrderService {
    @Autowired
    private OrderRepository orderRepository;   // ❌ 字段注入：无法 final、隐藏依赖、测试要反射
}
```

`@RequiredArgsConstructor` 的思路：**把依赖声明为 final，Lombok 生成带全参构造器，Spring 4.3+ 看到唯一构造器就自动注入**——一行注解同时拿到构造器注入的所有好处。

### 生成规则：哪些字段会进构造器

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;   // ✅ final 无初值 → 进构造器
    private final PayClient payClient;               // ✅ final 无初值 → 进构造器

    @NonNull
    private InvoiceClient invoiceClient;             // ✅ @NonNull → 进构造器（生成非空检查）

    private final int MAX_RETRY = 3;                 // ❌ final 有初值（常量）→ 不进
    private int timeoutSeconds;                      // ❌ 非 final → 不进
}
```

Lombok 等价生成的代码：

```java
public OrderService(OrderRepository orderRepository, PayClient payClient,
                    @NonNull InvoiceClient invoiceClient) {
    if (invoiceClient == null) {
        throw new NullPointerException("invoiceClient is marked non-null but is null");
    }
    this.orderRepository = orderRepository;
    this.payClient = payClient;
    this.invoiceClient = invoiceClient;
}
```

| 字段状态 | 是否进构造器 | 说明 |
|---------|-------------|------|
| `final` 无初值 | ✅ | 必须由构造器赋值，天然适合依赖 |
| `@NonNull` 非 final | ✅ | 进构造器并生成非空断言 |
| `final` 有初值 | ❌ | 编译期常量，不依赖外部 |
| 非 final 无注解 | ❌ | 可变状态，不走构造器 |
| `static` 字段 | ❌ | 静态成员不参与实例构造 |

参数顺序 = 字段在类中的声明顺序。

### 与 Spring 的隐式契约

Spring 4.3+ 起的规则：**类只有一个构造器时，无需任何注入注解**。

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final PayClient payClient;
    // Spring 启动时：发现唯一构造器 → 自动按类型注入两个参数
}
```

这一契约正是构造器注入能「零注解化」的基础——Lombok 生成构造器，Spring 自动认领。

### 关键集成配置：@Qualifier 复制

事故场景二复盘：多 Bean 场景下，**字段上的 `@Qualifier` 不会出现在生成的构造器参数上**（构造器是编译期生成的，源码里没有参数可标注）：

```java
// ========== 不推荐写法（仅展示）：注入失效 ==========
@Service
@RequiredArgsConstructor
public class ReportService {
    @Qualifier("mysqlDataSource")          // ❌ 字段注解不会传到构造器参数
    private final DataSource dataSource;   // 容器里有两个 DataSource → 启动报 NoUniqueBeanDefinitionException
}
```

官方解法是在 `lombok.config`（项目根目录）中声明**注解复制**：

```properties
config.stopBubbling = true
# 把指定注解从字段复制到 Lombok 生成的方法/构造器参数上
lombok.copyableAnnotations += org.springframework.beans.factory.annotation.Qualifier
lombok.copyableAnnotations += org.springframework.beans.factory.annotation.Value
```

配置后编译产物等效于：

```java
public ReportService(@Qualifier("mysqlDataSource") DataSource dataSource) { ... }
```

`@Qualifier` 随参数进入注入点，Spring 正确选择指定 Bean。`@Value` 同理——配合 `private final` 字段可实现构造期注入配置值。

### 构造器注入 vs 字段注入

| 维度 | 构造器注入（`@RequiredArgsConstructor`） | 字段注入（`@Autowired` 字段） |
|------|---------------------------------------|------------------------------|
| 不可变性 | 字段可 `final`，注入后不变 | 可被随意修改 |
| 依赖完整性 | 构造完成即可用，不可能出现半初始化 | 对象先创建后注入，存在 `null` 窗口 |
| 单元测试 | `new OrderService(mockRepo, mockPay)` 直接构造 | 需要 `ReflectionTestUtils` 反射塞值 |
| 循环依赖 | 启动**立即失败**，问题早暴露 | 三级缓存悄悄解开，问题晚爆发 |
| Spring 官方态度 | 推荐（官方文档明确表态） | 不推荐 |

特别说明循环依赖：Spring Boot 2.6 起**默认禁止循环依赖**（`spring.main.allow-circular-references=false`），构造器注入的循环依赖即使老版本也无法靠三级缓存解开。所以「构造器注入报循环依赖」不是缺陷——它把设计问题提前到了启动期。

### 常见坑与排查

| 坑 | 现象 | 原因与解法 |
|----|------|-----------|
| 多构造器歧义 | `NoSuchBeanDefinitionException` 或启动报错 | 手写了一个构造器后类内有两个构造器，Spring 不知注入哪个。**解法**：保持单一构造器；确需多个时在目标构造器上标 `@Autowired`（生成的构造器无法标注，所以只能标在手写的那个） |
| `@NonNull` 启动 NPE | 启动即抛 `NullPointerException` | 容器中依赖缺失/null。这是**快速失败**——比运行到一半才 NPE 好，按异常栈补齐 Bean 定义即可 |
| `@Value` 默认值不生效 | 注入结果为 null 或字面量 | `@Value` 想走构造器注入必须：配置 `copyableAnnotations` 复制 + 字段为 `final` 无初值 |
| IDE 参数名显示异常 | 调试时参数名是 `arg0` | 编译缺 `-parameters` 参数。与注入正确性无关，但影响日志与文档 |
| `@AllArgsConstructor` 并存 | 同上多构造器歧义 | `@RequiredArgsConstructor` 与 `@AllArgsConstructor` 不要同用 |

> ### 💡 新人小结：@RequiredArgsConstructor 怎么用才稳？
>
> 把它想象成「点菜」：
> - `final` 字段是菜单上的「必点项」——构造器（厨房）必须一样不少地给你
> - Spring 看到这家店只有一套套餐（唯一构造器），直接上菜，不用你喊单（`@Autowired`）
> - `@Qualifier` 是「口味备注」——备注要写到订单（`lombok.config` 复制）才能传到厨房，写在餐巾纸（字段）上厨师看不见
>
> **一个类一套套餐 + 备注写进配置单，注入就再也不会翻车**。

---

## 三、@FieldNameConstants

### 痛点：魔法字符串

```java
// ========== 不推荐写法（仅展示） ==========
QueryWrapper<User> qw = new QueryWrapper<>();
qw.eq("user_name", "tom");     // ❌ 列名是手写字符串：字段改名后编译不报错，运行时才炸
```

字符串没有编译期检查，重构工具也不认识它。`@FieldNameConstants` 让**字段名本身变成常量**——改字段名时，所有引用同步失效于编译期。

### 生成机制

```java
@FieldNameConstants
public class User {
    private Long id;
    private String userName;
    private String email;
}
```

编译期生成的代码（`javap` 或 IDE 反编译可见）：

```java
// Lombok 生成的内部类
public static class FieldNameConstants {
    public static final String id = "id";
    public static final String userName = "userName";
    public static final String email = "email";
}
```

每个常量的**名称与值都是字段名**，与字段定义永远同步。

### 三个常用参数

```java
// ========== 参数组合示例 ==========
@FieldNameConstants(asEnum = true, innerTypeName = "F", onlyExplicit = true)
public class Config {
    private String host;                        // 被生成

    @FieldNameConstants.Exclude
    private String password;                    // 敏感字段排除
}
```

| 参数 | 作用 | 生成物 |
|------|------|--------|
| `asEnum = true` | 生成枚举替代字符串常量 | `enum F { host }` |
| `innerTypeName = "F"` | 自定义内部类名（默认 `FieldNameConstants`） | `Config.F.host` |
| `onlyExplicit = true` | 只为显式标注的字段生成 | 精确控制范围 |

配合 `@FieldNameConstants.Include` / `@FieldNameConstants.Exclude` 可做字段级取舍。

### 典型使用场景

```java
// 场景 1：QueryWrapper 列名（字段改名 → 编译报错，第一时间暴露）
QueryWrapper<User> qw = new QueryWrapper<>();
qw.eq(User.FieldNameConstants.userName, "tom");

// 场景 2：注解参数中的字段名（如 Jackson 绑定）——字段改名时引用处直接编译报错，
// 而不是像魔法字符串那样静默失效；常量在编译期内联，使用方与字段定义强绑定
public class UserVO {
    @JsonProperty(User.FieldNameConstants.email)
    private String email;
}

// 场景 3：Map 键、配置键等任何「字段名字符串」的位置
Map<String, Object> row = Map.of(User.FieldNameConstants.email, "a@b.com");

// 场景 4：枚举遍历做批量校验（asEnum = true 时）
for (Config.F f : Config.F.values()) {
    validate(f.name());
}
```

### 与手写常量类对比

| 维度 | 手写常量类 | @FieldNameConstants |
|------|-----------|--------------------|
| 新增字段 | 常量类要同步加一行 | 自动生成，零维护 |
| 字段改名 | 常量字符串容易漏改（值不变） | 常量随字段自动变 |
| 阅读直观 | ✅ 所见即所得 | 需要知道生成规则 |
| 团队上手成本 | 零 | 需要一次性理解 |

### 历史行为变更警告

**Lombok 1.16 → 1.18 的破坏性变更**：早期版本常量直接生成在类顶层（`User.userName`），1.18 起收纳进内部类（`User.FieldNameConstants.userName`）。从旧版本升级时，所有顶层引用会编译失败——这是升级 Lombok 时最常见的编译批量报错来源，全局替换即可。

> ### 💡 新人小结：@FieldNameConstants 是什么？
>
> 把它想象成「标签打印机」：
> - 每个字段出生时，打印机自动打出一张**同名的标签**（常量）
> - 字段改名，标签重打——贴出去的标签永远和字段对得上
> - 手写字符串则是「手抄标签」，抄错、漏抄都查不出来
>
> **凡是要写字段名字符串的地方，换成 FieldNameConstants 常量，让编译器替你把关**。

---

## 要点总结

1. **命名错位的根源是三套规则并存**：Lombok 生成 `getANum`，Jackson 读成 `anum`，Introspector 读成 `ANum`——字段 `aNum` 从未以任何身份出现在运行时
2. **高危模式**：小写开头 + 第二个字母大写（`aNum`/`uName`/`nCode`）；布尔字段加 `is` 前缀同样触发错位
3. **最优策略**：新字段规范命名（`numA`）根治；无法改名的存量字段手写 `getaNum()/setaNum()` 并配 `@Getter(AccessLevel.NONE) + @Setter(AccessLevel.NONE)`，全框架名称一致
4. **`@RequiredArgsConstructor`**：`final` 无初值 + `@NonNull` 字段进构造器；Spring 4.3+ 单构造器自动注入；`@Qualifier`/`@Value` 必须通过 `lombok.config` 的 `copyableAnnotations` 复制到参数
5. **`@FieldNameConstants`**：字段名常量随字段自动同步，消灭 QueryWrapper 列名等魔法字符串；注意 1.16 → 1.18 顶层常量改内部类的破坏性变更

---

> ### 💡 新人小结：Lombok 学完了，记住这 5 点
>
> 1. **字段名会过三道手**：Lombok 生成 → Jackson/Introspector 解读——每道手规则不同，`aNum` 类命名必踩坑
> 2. **新字段防患于未然**：避开小写+大写模式，布尔不加 `is` 前缀
> 3. **老字段手写访问器**：`getaNum/setaNum` + 排除注解，让所有框架读出同一个名字
> 4. **构造器注入是默认选择**：`final` 字段 + `@RequiredArgsConstructor` + `copyableAnnotations` 传递 `@Qualifier`
> 5. **字段名字符串全部常量化**：`@FieldNameConstants` 让重构在编译期暴露，而不是在运行时爆炸
