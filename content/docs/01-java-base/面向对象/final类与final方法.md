---
title: final 类与 final 方法
description: final 修饰类和方法的核心作用、JDK 经典案例（String、Math）剖析、使用场景与禁忌，以及 final 在继承体系中的完整影响。
weight: 1
---

# 为什么需要 final？

想象你写了一个「密码加密器」类，里面有一个 `encrypt()` 方法，安全性经过严格审计。某天，一个新人继承了这个类，**重写了 `encrypt()` 方法**——把加密逻辑改成了明文传输。系统上线后，数据泄露。

这不是假设场景，而是真实工程中反复出现过的事故。

**Java 的 `final` 关键字，就是用来防止这种「被篡改」的风险**：

| 修饰对象 | final 的效果 | 类比 |
|---------|-------------|------|
| 类 | 不可被继承 |  sealed 密封箱——不能拆开来扩展 |
| 方法 | 不可被子类重写 |  合同中的「不可修改条款」——签字后不能改 |
| 变量 | 不可重新赋值 |  刻在石头上的字——写死不能改 |

> ### 💡 新人小结：final 到底在保护什么？
>
> 把 `final` 想象成一个「锁定」按钮：
> - 锁定一个类 → 没有人能继承它、篡改它的行为
> - 锁定一个方法 → 子类不能重写这个方法的核心逻辑
> - 锁定一个变量 → 一旦赋值就不能再改（类似常量）
>
> 就像你把一份重要文件锁进保险箱——不是因为你不需要它，而是为了防止被人偷偷修改。

**学习路线图**：

```
核心作用 → JDK 经典案例 → 使用场景与禁忌 → 对比与辨析
final 锁什么  String/Math   什么时候用/不用   abstract/static
```

---

## 核心作用

### final 类：不可被继承

声明 `final` 的类**不能被继承**，所有方法自动成为 `final`（无需显式声明）。

```java
public final class Math {
    // Math 类的所有方法自动成为 final，不可被子类重写
    public static double abs(double a) { return (a <= 0.0) ? 0.0 - a : a; }
    public static int max(int a, int b) { return (a >= b) ? a : b; }
    // ...
}

// 以下代码编译报错：
// class MyMath extends Math { }  // ❌ Cannot inherit from final 'Math'
```

> ### 💡 新人小结：final 类像什么？
>
> `final` 类就像一个「密封配方」——可口可乐的配方，你可以买这个饮料来喝（使用这个类），但你不能修改配方（继承并篡改）。
>
> JDK 中的 `String`、`Math`、`Integer` 都是 final 类——它们的设计者认为这些类的行为不应该被改变。

### final 方法：不可被重写

声明 `final` 的方法**不能被子类重写**，但类本身仍然可以被继承。

```java
public class Account {
    private double balance;

    /** 核心校验逻辑，不允许子类篡改 */
    public final void withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("金额必须为正");
        if (amount > balance) throw new IllegalStateException("余额不足");
        balance -= amount;
    }

    /** 普通方法，子类可以重写 */
    public String getAccountType() {
        return "STANDARD";
    }
}

public class PremiumAccount extends Account {
    // ❌ 编译报错：Cannot override final method 'withdraw'
    // public void withdraw(double amount) { ... }

    // ✅ 可以重写非 final 方法
    @Override
    public String getAccountType() {
        return "PREMIUM";
    }
}
```

---

## JDK 经典案例剖析

### 案例一：`java.lang.String` — 为什么是 final 类？

```java
public final class String implements java.io.Serializable, Comparable<String>, CharSequence {
    private final char[] value;  // Java 9+ 改为 byte[]
    // ...
}
```

**String 被设计为 final 的三重原因**：

| 原因 | 说明 | 如果不 final 会怎样？ |
|------|------|---------------------|
| **安全性** | String 广泛用于类加载、网络连接、数据库连接等关键场景 | 子类可以重写 `hashCode()`、`equals()`，导致 HashMap 行为异常 |
| **不可变性** | String 的值创建后不可修改，是线程安全的 | 子类可以添加可变字段，破坏不可变性 |
| **性能** | String 的 `hashCode()` 可缓存，常量池可复用 | 子类修改内部状态后缓存失效 |

> ### 💡 新人小结：String 为什么不能继承？
>
> 想象 String 是一张「身份证」：
> - 身份证号一旦生成就不能改（不可变性）
> - 所有人都信任这张身份证（安全性）
> - 系统可以快速验证（hashCode 缓存）
>
> 如果允许继承，有人可以做一张「假身份证」——号码一样但信息不同，整个系统就乱套了。

### 案例二：`java.lang.Math` — 工具类为什么是 final？

```java
public final class Math {
    private Math() {}  // 私有构造器，禁止实例化

    public static final double PI = 3.141592653589793;
    public static int max(int a, int b) { return (a >= b) ? a : b; }
    // ...
}
```

**Math 被设计为 final 的原因**：

- **工具类不需要继承**：Math 全是静态方法，没有实例状态
- **防止篡改**：如果 `Math.max()` 被重写，所有依赖它的代码都会出错
- **与私有构造器配合**：既不能实例化，也不能继承

### 案例三：`StringBuilder` — 为什么不是 final？

```java
public final class String { ... }      // final：不可变，不需要扩展
public class StringBuilder { ... }     // 非 final：需要灵活扩展
```

| 对比项 | String | StringBuilder |
|--------|--------|---------------|
| 是否 final | ✅ 是 | ❌ 否 |
| 可变性 | 不可变 | 可变 |
| 线程安全 | 安全 | 不安全 |
| 为什么这样设计 | 需要全局信任（常量池、hashCode 缓存） | 需要灵活性（append、insert 等扩展操作） |

---

## 使用场景与禁忌

### ✅ 推荐使用 final 的场景

| 场景 | 示例 | 理由 |
|------|------|------|
| **工具类** | `Math`、`Collections`（部分） | 工具方法不应被篡改 |
| **不可变类** | `String`、`Integer`、`LocalDate` | 继承会破坏不可变性 |
| **安全敏感类** | 加密器、校验器 | 防止恶意子类绕过安全检查 |
| **核心流程方法** | 模板方法中的固定步骤 | 确保子类不改变核心流程 |
| **依赖内部状态的方法** | 余额扣款、状态机转换 | 子类重写可能破坏状态一致性 |

### ❌ 禁忌：不要滥用 final

| 禁忌 | 说明 |
|------|------|
| **不要给普通业务类加 final** | 限制扩展性，违背开闭原则 |
| **避免 final 方法依赖可被子类修改的属性** | 子类无法重写方法，但可能通过其他方式修改状态，导致逻辑矛盾 |
| **抽象类不能是 final** | 抽象类的核心用途就是被继承/实现 |
| **接口不能是 final** | 接口的核心用途就是被实现 |

---

## final 与继承体系的完整对比

### final 在不同修饰下的行为

| 组合 | 是否合法 | 说明 |
|------|---------|------|
| `final class` | ✅ | 不可被继承，所有方法自动 final |
| `final method` | ✅ | 不可被重写，但类可被继承 |
| `final variable` | ✅ | 不可重新赋值（引用类型：引用不可变，内容可变） |
| `abstract final class` | ❌ | 矛盾：abstract 要求被继承，final 禁止继承 |
| `abstract final method` | ❌ | 矛盾：abstract 要求被实现，final 禁止重写 |
| `static final method` | ✅ | 静态方法不能重写（只能隐藏），final 无额外效果 |
| `private final method` | ✅ | 私有方法本身就不能被重写，final 无额外效果 |
| `final constructor` | ❌ | 构造器不能被继承，final 无意义 |

### 决策流程图

```
是否需要限制继承/重写？
│
├─ 是 → 整个类都不需要被继承？
│       │
│       ├─ 是 → final class（如 String、Math）
│       │
│       └─ 否 → 只有特定方法需要保护？
│               │
│               ├─ 是 → final method（如 Account.withdraw）
│               │
│               └─ 否 → 不使用 final
│
└─ 否 → 正常使用，不加 final
```

---

## 完整代码示例

```java
// ========== final 类示例 ==========
public final class PasswordEncoder {
    private static final String SALT = "oink2026";

    /** 编码密码——核心安全方法，不可被篡改 */
    public static String encode(String rawPassword) {
        if (rawPassword == null || rawPassword.isEmpty()) {
            throw new IllegalArgumentException("密码不能为空");
        }
        // 简化示例：实际应使用 BCrypt 等安全算法
        return Integer.toHexString((SALT + rawPassword).hashCode());
    }

    private PasswordEncoder() {}  // 禁止实例化
}

// ❌ 编译报错：Cannot inherit from final 'PasswordEncoder'
// class WeakEncoder extends PasswordEncoder { }

// ========== final 方法示例 ==========
public class BaseProcessor {

    /** 模板方法：核心流程不可改，扩展点留给子类 */
    public final void process(String data) {
        validate(data);       // 固定步骤，不可重写
        doProcess(data);      // 扩展点，子类实现
        log(data);            // 固定步骤，不可重写
    }

    private void validate(String data) {
        if (data == null) throw new IllegalArgumentException("数据不能为空");
    }

    /** 子类可以重写的扩展点 */
    protected void doProcess(String data) {
        System.out.println("默认处理: " + data);
    }

    private void log(String data) {
        System.out.println("日志: 已处理 " + data);
    }
}

public class SpecialProcessor extends BaseProcessor {
    // ❌ 编译报错：Cannot override final method 'process'
    // public void process(String data) { ... }

    // ✅ 可以重写非 final 的 protected 方法
    @Override
    protected void doProcess(String data) {
        System.out.println("特殊处理: " + data);
    }
}

// ========== 测试 ==========
public static void main(String[] args) {
    // final 类使用
    String encoded = PasswordEncoder.encode("123456");
    System.out.println("编码结果: " + encoded);

    // final 方法使用（模板方法模式）
    BaseProcessor processor = new SpecialProcessor();
    processor.process("测试数据");
    // 输出：
    // 特殊处理: 测试数据
    // 日志: 已处理 测试数据
}
```

---

## final 变量的补充说明

虽然本文聚焦 final 类和方法，但 final 变量也值得简要说明：

```java
// 基本类型：值不可变
final int MAX_SIZE = 100;
// MAX_SIZE = 200;  // ❌ 编译报错

// 引用类型：引用不可变，但内容可变
final List<String> list = new ArrayList<>();
list.add("hello");     // ✅ 内容可以修改
// list = new ArrayList<>();  // ❌ 编译报错：引用不可变

// final + static = 常量
public static final double PI = 3.141592653589793;
```

> ### 💡 新人小结：final 变量的「锁定」
>
> `final` 变量就像一个「快递包裹」：
> - 包裹的地址（引用）不能改——你不能把包裹送到别人家
> - 但包裹里面的东西（内容）可以改——你可以打开包裹拿出/放入东西
>
> 只有 `final` + 不可变类型（如 `String`、`Integer`）才是真正的「完全锁定」。

---

## 要点总结

1. **final 类**不可被继承，所有方法自动 final——用于工具类、不可变类、安全敏感类
2. **final 方法**不可被重写，但类可被继承——用于保护核心流程不被篡改
3. **JDK 经典案例**：`String`（不可变+安全）、`Math`（工具类+私有构造器）都是 final 类
4. **模板方法模式**：`final process()` + 可重写的 `doProcess()` 是经典的设计模式应用
5. **禁忌**：不要滥用 final，普通业务类不应加 final（违背开闭原则）

---

> ### 💡 新人小结：final 学完了，记住这 4 点
>
> 1. **final 类 = 密封箱**：不能继承，`String`、`Math` 都是这样
> 2. **final 方法 = 不可修改条款**：子类不能重写，保护核心逻辑
> 3. **abstract 和 final 是天敌**：不能同时修饰一个类或方法
> 4. **不要滥用**：只在「确实不需要被扩展」时才用 final，否则限制灵活性
