---
title: Lombok 与 MapStruct 实战
description: Lombok 消除样板代码、MapStruct 自动生成对象映射、两者集成的注解顺序陷阱，以及 Spring Boot 下的完整配置与常见问题排查。
weight: 1
---

# 为什么需要编译期代码生成？

想象你是一个外卖平台的后端开发，每天要写大量的「搬运代码」：

- 一个 User 实体类有 20 个字段 → 手写 20 个 getter + 20 个 setter + toString + equals + hashCode = **200 行样板代码**
- 一个 UserEntity 要转成 UserDTO → 手写 15 行 `dto.setXxx(entity.getXxx())` → 加个字段就忘改一处 → 线上 NPE
- 项目里有 100 个实体类 → 100 × 200 行 = **20000 行纯搬运代码**

| 没有工具时 | 用 Lombok | 用 MapStruct | 用 Lombok + MapStruct |
|-----------|-----------|-------------|----------------------|
| 200 行 getter/setter | 1 个 `@Data` 注解 | 200 行 getter/setter | 1 个 `@Data` 注解 |
| 15 行手动 set 映射 | 15 行手动 set 映射 | 1 个 `@Mapping` 接口 | 1 个 `@Mapping` 接口 |
| 加字段忘改 → 线上 bug | 加字段忘改 → 线上 bug | 加字段 → 编译报错 | 加字段 → 编译报错 |
| **总计 215 行** | **15 行** | **215 行** | **1 行注解** |

**这两个工具的共同特点**：代码不是运行时生成的，而是在**编译期**由注解处理器（Annotation Processor）直接写入 `.class` 文件——零运行时开销。

> ### 💡 新人小结：编译期代码生成是什么？
>
> 把编译器想象成一台「自动缝纫机」：
> - 你只需要画一张「设计图」（写注解）
> - 编译器在编译时自动帮你「缝」出成品代码（getter/setter/映射逻辑）
> - 最终产出的 `.class` 文件和你手写的完全一样——只是不用你亲手缝了
>
> **编译期生成 = 零运行时开销 + 编译时就能发现错误**。

**学习路线图**：

```
Lombok → MapStruct → 集成配置 → Spring Boot 实战 → 常见问题排查
消除样板   自动映射    注解顺序陷阱   完整项目配置    踩坑与解决
```

---

## Lombok：消灭样板代码

### 痛点

每个 Java 开发者都经历过：新建一个实体类，然后 IDE 右键 → Generate → 一口气生成 getter、setter、toString、equals、hashCode。一个 20 字段的类，样板代码超过 200 行。

更要命的是：

- 加了个字段，**忘了重新生成 equals** → 两个「相同」的对象 `equals()` 返回 `false`
- 复制粘贴了另一个类的代码，**忘了改 serialVersionUID** → 序列化出错
- 写了 `@Slf4j` 但忘了加 `static final` → 日志对象没初始化

### 设计

Lombok 通过 **JSR 269 注解处理器 API** 在编译期直接修改 AST（抽象语法树），将注解对应的代码注入到编译产物中。

```
Lombok 工作原理

① javac 编译 → 解析源码生成 AST
② Lombok 注解处理器启动 → 扫描 @Data / @Builder 等注解
③ 在 AST 上插入 getter/setter/toString 等节点
④ 编译继续 → 最终 .class 文件包含生成的方法
⑤ 运行时完全感知不到 Lombok 的存在
```

> ### 💡 新人小结：Lombok 怎么做到「无中生有」的？
>
> Lombok 就像一个「隐形代笔」：
> - 你在合同上只签了个名（写了个注解）
> - 代笔在盖章前帮你把整份合同填好了（编译期注入代码）
> - 对方看到的是一份完整的合同（.class 文件里有完整方法）
> - 但签名确实只有你一个人签的（源码里只有一行注解）

### 核心注解速查表

| 注解 | 生成内容 | 适用场景 |
|------|---------|---------|
| `@Getter` / `@Setter` | getter / setter 方法 | 单个字段或类级别 |
| `@ToString` | `toString()` 方法 | 调试日志输出 |
| `@EqualsAndHashCode` | `equals()` + `hashCode()` | 集合操作、Map 键 |
| `@NoArgsConstructor` | 无参构造器 | JPA / Jackson 反序列化 |
| `@AllArgsConstructor` | 全参构造器 | 需要一次性传入所有参数 |
| `@RequiredArgsConstructor` | `final` / `@NonNull` 字段的构造器 | 配合 Spring 构造器注入 |
| `@Data` | `@Getter` + `@Setter` + `@ToString` + `@EqualsAndHashCode` + `@RequiredArgsConstructor` | **实体类标配**（最常用） |
| `@Builder` | 建造者模式 API | 复杂对象构造 |
| `@Slf4j` | `private static final Logger log` | 日志（最常用） |
| `@Value` | 不可变类（所有字段 `private final`，只有 getter） | 配置类、值对象 |
| `@Accessors(chain = true)` | setter 返回 `this`（链式调用） | 流式 API 风格 |

### 具体用法

```java
// ========== 推荐写法：@Data 一步到位 ==========
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    private Long id;
    private String name;
    private Integer age;
    private String email;
}
// 编译后自动生成：4 个 getter + 4 个 setter + toString + equals + hashCode + 无参构造 + 全参构造
// 源码只有 7 行，手写等价物超过 100 行

// ========== 推荐写法：@Builder 建造者模式 ==========
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Order {
    private Long id;
    private String orderNo;
    private BigDecimal amount;
    private LocalDateTime createTime;
}

// 使用 Builder 构造对象（链式调用，可读性极强）
Order order = Order.builder()
    .orderNo("20260911001")
    .amount(new BigDecimal("99.90"))
    .createTime(LocalDateTime.now())
    .build();

// ========== 推荐写法：@Slf4j 日志 ==========
@Slf4j
@Service
public class UserService {
    public void createUser(User user) {
        log.info("创建用户: {}", user.getName());  // 直接使用 log 变量
        // ...
    }
}

// ========== 不推荐写法 ==========
// ❌ @Data 用在 JPA 实体上（会导致懒加载字段被 toString 触发）
@Data
@Entity
public class Order {
    @OneToMany(fetch = FetchType.LAZY)
    private List<OrderItem> items;  // toString() 会触发全表查询！
}
// ✅ 正确做法：JPA 实体用 @Getter @Setter @ToString(exclude = "items")
```

**参数解释**：
- `@Data`：组合注解，等于 `@Getter` + `@Setter` + `@ToString` + `@EqualsAndHashCode` + `@RequiredArgsConstructor`
- `@Builder`：生成内部 Builder 类，注意必须同时加 `@NoArgsConstructor` + `@AllArgsConstructor`（否则 Jackson 反序列化失败）
- `@Slf4j`：生成 `private static final Logger log = LoggerFactory.getLogger(当前类.class)`

> ### 💡 新人小结：@Data 和 @Builder 怎么选？
>
> - **@Data**：像「全家桶」——一个注解搞定所有样板，适合普通实体类
> - **@Builder**：像「定制套餐」——按需一步步构造对象，适合字段多、构造复杂的场景
> - **两者可以叠加用**，但必须同时加 `@NoArgsConstructor` + `@AllArgsConstructor`

---

## MapStruct：消灭手动映射

### 痛点

分层架构中，Entity → DTO → VO 的转换是日常开发中最繁琐的搬运工作：

```java
// ❌ 手动映射：100 个字段搬 100 次
public UserDTO toDTO(UserEntity entity) {
    UserDTO dto = new UserDTO();
    dto.setId(entity.getId());
    dto.setName(entity.getName());
    dto.setAge(entity.getAge());
    dto.setEmail(entity.getEmail());
    // ... 还有 96 个字段
    return dto;
}
```

**手动映射的三大痛点**：

1. **容易遗漏**：Entity 加了个字段，DTO 忘改 → 线上 NPE
2. **难以维护**：映射逻辑散落在 Service 里，改一处要找遍全项目
3. **性能隐患**：用 BeanUtils.copyProperties() 反射拷贝 → 慢 10-100 倍

### 设计

MapStruct 在**编译期**生成映射实现类——不是反射，是真正的 `getter/setter` 调用。性能与手写代码完全一致。

```
MapStruct 工作原理

① 你定义接口 + @Mapping 注解（声明「从哪到哪」）
② 编译器触发 MapStruct 注解处理器
③ MapStruct 读取源类和目标类的字段信息
④ 自动生成 XxxMapperImpl.java（纯 getter/setter 调用）
⑤ 运行时直接调用生成的实现类（无反射，零开销）
```

> ### 💡 新人小结：MapStruct 和 BeanUtils 有什么区别？
>
> - **BeanUtils.copyProperties()**：像「搬家公司」——把东西搬过去，但到了才发现尺寸不对（类型不匹配）、找不到门（字段名不同）→ 运行时才报错
> - **MapStruct**：像「定制家具」——在工厂（编译期）就量好尺寸、做好标记 → 到了直接放进去，放不进去当场就知道

### 核心注解速查表

| 注解 | 用途 | 示例 |
|------|------|------|
| `@Mapper` | 标记接口为映射器 | `@Mapper public interface UserMapper` |
| `@Mapping(source, target)` | 字段映射规则 | `@Mapping(source = "userName", target = "name")` |
| `@Mapping(ignore = true)` | 忽略某个字段 | `@Mapping(target = "password", ignore = true)` |
| `@Mapping(expression)` | 用 Java 表达式映射 | `@Mapping(target = "age", expression = "java(entity.getAge() + 1)")` |
| `@Mapping(defaultValue)` | 源为 null 时的默认值 | `@Mapping(target = "status", defaultValue = "ACTIVE")` |
| `@Mapping(qualifiedByName)` | 调用自定义转换方法 | `@Mapping(target = "createTime", qualifiedByName = "toDateStr")` |
| `@Mappings` | 多个映射规则（Java 8 需要） | `@Mappings({@Mapping(...), @Mapping(...)})` |
| `@Named` | 给自定义方法命名 | `@Named("toDateStr")` |
| `@IterableMapping` | 集合映射 | `@IterableMapping(elementTargetType = UserDTO.class)` |
| `@BeanMapping(ignoreByDefault = true)` | 默认忽略所有字段 | 只映射显式声明的字段 |

### 具体用法

```java
// ========== 1. 基本映射（字段名相同自动映射） ==========
@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDTO toDTO(UserEntity entity);
    // MapStruct 自动生成：dto.setId(entity.getId()); dto.setName(entity.getName()); ...
}

// ========== 2. 字段名不同时显式映射 ==========
@Mapper(componentModel = "spring")
public interface OrderMapper {
    @Mapping(source = "orderNo", target = "orderNumber")
    @Mapping(source = "createTime", target = "createdAt",
             qualifiedByName = "toLocalDate")
    @Mapping(target = "items", ignore = true)  // 忽略不映射的字段
    OrderDTO toDTO(OrderEntity entity);

    @Named("toLocalDate")
    default String toLocalDate(LocalDateTime dateTime) {
        return dateTime != null ? dateTime.toLocalDate().toString() : null;
    }
}

// ========== 3. 集合映射（List<Entity> → List<DTO>） ==========
@Mapper(componentModel = "spring")
public interface ProductMapper {
    ProductDTO toDTO(ProductEntity entity);

    // 自动复用上面的 toDTO 方法，逐个转换
    List<ProductDTO> toDTOList(List<ProductEntity> entities);
}

// ========== 4. 多源参数合并 ==========
@Mapper(componentModel = "spring")
public interface ReportMapper {
    @Mapping(source = "user.name", target = "userName")
    @Mapping(source = "order.orderNo", target = "orderNumber")
    @Mapping(source = "order.amount", target = "totalAmount")
    ReportDTO toReport(UserEntity user, OrderEntity order);
}

// ========== 不推荐写法 ==========
// ❌ 使用 BeanUtils 反射拷贝（运行时才知道对不对）
UserDTO dto = new UserDTO();
BeanUtils.copyProperties(entity, dto);  // 字段名不同？类型不匹配？运行时才报错
```

**参数解释**：
- `componentModel = "spring"`：让 MapStruct 生成的实现类自动注册为 Spring Bean（可用 `@Autowired` 注入）
- `source`：源对象的字段名（支持嵌套如 `"user.name"`）
- `target`：目标对象的字段名
- `ignore = true`：明确告诉 MapStruct 不映射这个字段（否则编译警告）
- `qualifiedByName`：调用 `@Named` 标记的自定义转换方法

> ### 💡 新人小结：MapStruct 的映射规则是什么？
>
> 想象你在做「翻译对照表」：
> - **名字一样** → 自动翻译（`entity.name` → `dto.name`）
> - **名字不同** → 写对照表（`@Mapping(source = "userName", target = "name")`）
> - **需要加工** → 请翻译官（`qualifiedByName = "toLocalDate"`）
> - **不需要翻译** → 划掉（`ignore = true`）

---

## Lombok + MapStruct 集成：注解顺序陷阱

### 痛点

**这是 Lombok + MapStruct 最常见的坑**：两个工具都是注解处理器，但 Lombok 必须**先于** MapStruct 执行。如果顺序反了，MapStruct 看到的类没有 getter/setter → 映射代码生成失败 → 编译报错。

```
❌ 错误现象

error: No property named "name" exists in source parameter(s).
Did you mean "null"?
```

**原因**：MapStruct 在 Lombok 之前运行，此时类还没有 getter/setter，MapStruct 找不到字段。

### 解决方案

**核心原则**：在注解处理器路径中，Lombok 必须排在 MapStruct **前面**。

#### Maven 配置（推荐方式）

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <configuration>
                <source>17</source>
                <target>17</target>
                <annotationProcessorPaths>
                    <!-- ⚠️ 顺序很重要！Lombok 必须在 MapStruct 前面 -->
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok</artifactId>
                        <version>1.18.30</version>
                    </path>
                    <path>
                        <groupId>org.projectlombok</groupId>
                        <artifactId>lombok-mapstruct-binding</artifactId>
                        <version>0.2.0</version>
                    </path>
                    <path>
                        <groupId>org.mapstruct</groupId>
                        <artifactId>mapstruct-processor</artifactId>
                        <version>1.5.5.Final</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>

<dependencies>
    <!-- Lombok（scope=provided，不打入 JAR） -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.30</version>
        <scope>provided</scope>
    </dependency>
    <!-- MapStruct 运行时 API -->
    <dependency>
        <groupId>org.mapstruct</groupId>
        <artifactId>mapstruct</artifactId>
        <version>1.5.5.Final</version>
    </dependency>
</dependencies>
```

**关键依赖解释**：
- `lombok`：核心库，`scope=provided` 表示只在编译期使用
- `lombok-mapstruct-binding`：**桥梁库**，让 Lombok 和 MapStruct 的注解处理器正确协作
- `mapstruct-processor`：MapStruct 编译期代码生成器
- `mapstruct`：MapStruct 运行时 API（`@Mapper` 等注解定义）

#### Gradle 配置

```groovy
plugins {
    id 'java'
}

dependencies {
    // Lombok
    compileOnly 'org.projectlombok:lombok:1.18.30'
    annotationProcessor 'org.projectlombok:lombok:1.18.30'

    // MapStruct
    implementation 'org.mapstruct:mapstruct:1.5.5.Final'
    annotationProcessor 'org.mapstruct:mapstruct-processor:1.5.5.Final'

    // ⚠️ 桥梁：让 Lombok 先于 MapStruct 执行
    annotationProcessor 'org.projectlombok:lombok-mapstruct-binding:0.2.0'

    // 测试
    testCompileOnly 'org.projectlombok:lombok:1.18.30'
    testAnnotationProcessor 'org.projectlombok:lombok:1.18.30'
}
```

> ### 💡 新人小结：为什么需要 binding 库？
>
> Lombok 和 MapStruct 就像两个厨师共用一个厨房：
> - Lombok 先做（生成 getter/setter）
> - MapStruct 后做（读取 getter/setter 来生成映射）
> - `lombok-mapstruct-binding` 就是「排班表」——确保 Lombok 先开工，MapStruct 再进场
> - 没有它，两个厨师可能同时开工 → MapStruct 发现没有 getter → 报错

---

## Spring Boot 集成实战

### 完整项目配置

#### 目录结构

```
src/main/java/com/example/demo/
├── entity/
│   └── UserEntity.java          ← 数据库实体（@Data）
├── dto/
│   └── UserDTO.java             ← 接口传输对象（@Data）
├── mapper/
│   └── UserMapper.java          ← MapStruct 映射接口
├── service/
│   └── UserService.java         ← 业务层（注入 Mapper）
└── controller/
    └── UserController.java      ← 控制层
```

#### Entity

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "t_user")
public class UserEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userName;      // 注意：数据库字段名和 DTO 不同

    private Integer age;

    private String email;

    private LocalDateTime createTime;
}
```

#### DTO

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDTO {
    private Long id;
    private String name;          // 对应 Entity 的 userName
    private Integer age;
    private String email;
    private String createTimeStr; // 对应 Entity 的 createTime（格式化为字符串）
}
```

#### Mapper

```java
@Mapper(componentModel = "spring")
public interface UserMapper {

    @Mapping(source = "userName", target = "name")
    @Mapping(target = "createTimeStr", qualifiedByName = "formatDateTime")
    UserDTO toDTO(UserEntity entity);

    List<UserDTO> toDTOList(List<UserEntity> entities);

    @Named("formatDateTime")
    default String formatDateTime(LocalDateTime dateTime) {
        return dateTime != null
            ? dateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
            : null;
    }
}
```

#### Service

```java
@Slf4j
@Service
@RequiredArgsConstructor   // Lombok 生成构造器，Spring 通过构造器注入
public class UserService {

    private final UserRepository userRepository;  // 自动注入
    private final UserMapper userMapper;          // 自动注入 MapStruct 生成的 Bean

    public List<UserDTO> listUsers() {
        List<UserEntity> entities = userRepository.findAll();
        log.info("查询到 {} 个用户", entities.size());
        return userMapper.toDTOList(entities);    // 一行搞定集合映射
    }

    public UserDTO getUser(Long id) {
        UserEntity entity = userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("用户不存在: " + id));
        return userMapper.toDTO(entity);
    }
}
```

> ### 💡 新人小结：Spring Boot 中怎么串起来？
>
> 整个流程像一条「流水线」：
> 1. **Controller** 收到请求 → 交给 Service
> 2. **Service** 从数据库取 Entity → 交给 Mapper 转换
> 3. **Mapper**（MapStruct 生成的实现类）自动把 Entity → DTO
> 4. **Service** 返回 DTO → Controller 返回给前端
>
> 你只需要定义接口（`UserMapper`），MapStruct 在编译时自动帮你写好实现类（`UserMapperImpl`），Spring 自动注入。

---

## 常见问题排查

### 问题一：Lombok + MapStruct 编译报错「No property named xxx exists」

**现象**：

```
error: No property named "name" exists in source parameter(s).
Did you mean "null"?
```

**原因**：注解处理器执行顺序错误——MapStruct 先于 Lombok 执行，此时类还没有 getter/setter。

**解决方案**：

| 方案 | 操作 | 推荐度 |
|------|------|--------|
| **添加 binding 库** | 在 `annotationProcessorPaths` 中加入 `lombok-mapstruct-binding` | ⭐⭐⭐ 最推荐 |
| **确保顺序** | Lombok 在 MapStruct 前面声明 | ⭐⭐ 基础要求 |
| **升级版本** | Lombok ≥ 1.18.20 + MapStruct ≥ 1.5.0 | ⭐⭐ 新版兼容性更好 |

```xml
<!-- ✅ 正确顺序 -->
<annotationProcessorPaths>
    <path>lombok</path>                    <!-- ① Lombok 先执行 -->
    <path>lombok-mapstruct-binding</path>  <!-- ② 桥梁 -->
    <path>mapstruct-processor</path>       <!-- ③ MapStruct 后执行 -->
</annotationProcessorPaths>
```

### 问题二：IDEA 中编译通过但 IDE 报红

**现象**：Maven/Gradle 编译成功，但 IDEA 中 Mapper 接口标红，提示「Cannot find implementation」。

**原因**：IDEA 没有正确识别 MapStruct 生成的 `Impl` 类。

**解决方案**：

1. **安装 MapStruct 插件**：IDEA → Settings → Plugins → 搜索「MapStruct Support」→ 安装
2. **清理重建**：`mvn clean compile` 或 Gradle → `clean` + `build`
3. **检查 annotation processing**：Settings → Build → Compiler → Annotation Processors → ✅ Enable

### 问题三：@Builder 导致 Jackson 反序列化失败

**现象**：

```
com.fasterxml.jackson.databind.exc.InvalidDefinitionException:
Cannot construct instance of `User`: cannot deserialize from Object value
(no delegate- or property-based Creator)
```

**原因**：单独使用 `@Builder` 时，Lombok 只生成全参构造器，不生成无参构造器。Jackson 反序列化需要无参构造器。

**解决方案**：

```java
// ✅ 正确写法：@Builder + @NoArgsConstructor + @AllArgsConstructor 三件套
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class User {
    private String name;
    private Integer age;
}
```

### 问题四：@Data 用在 JPA 实体上导致 StackOverflow

**现象**：

```
java.lang.StackOverflowError
    at User.toString(User.java:xx)
    at Order.toString(Order.java:xx)
    at User.toString(User.java:xx)  // 无限循环
```

**原因**：`@Data` 的 `@ToString` 会遍历所有字段。如果两个实体互相引用（`User → Order → User`），就会无限递归。

**解决方案**：

```java
// ✅ 方案一：排除关联字段
@Data
@Entity
public class User {
    private String name;

    @ToString.Exclude      // toString 不包含此字段
    @EqualsAndHashCode.Exclude  // equals/hashCode 也不包含
    @OneToMany(mappedBy = "user")
    private List<Order> orders;
}

// ✅ 方案二：JPA 实体不用 @Data，改用 @Getter @Setter
@Getter
@Setter
@ToString(exclude = "orders")
@EqualsAndHashCode(exclude = "orders")
@Entity
public class User { ... }
```

### 问题五：MapStruct 映射后字段为 null

**现象**：映射执行成功，但目标对象的某些字段为 `null`。

**原因排查清单**：

| 可能原因 | 排查方法 |
|---------|---------|
| 字段名不匹配 | 检查源类和目标类的字段名是否一致（大小写敏感） |
| 字段名不同但没写 @Mapping | 加上 `@Mapping(source = "xxx", target = "yyy")` |
| 嵌套字段没展开 | 用 `"address.city"` 点号语法访问嵌套属性 |
| 类型不匹配 | 加 `qualifiedByName` 指定自定义转换方法 |
| 被 ignore 了 | 检查是否有 `@Mapping(target = "xxx", ignore = true)` |

**调试技巧**：查看 MapStruct 生成的 `Impl` 类（在 `target/generated-sources/` 目录下），看它到底映射了哪些字段。

### 问题六：多模块项目中 MapStruct 找不到 Mapper

**现象**：

```
No bean named 'userMapperImpl' available
```

**原因**：`@Mapper(componentModel = "spring")` 生成的实现类在另一个模块中，Spring 扫描不到。

**解决方案**：

```java
// ✅ 方案一：在 @MapperScan 中包含 Mapper 所在包
@SpringBootApplication(scanBasePackages = {"com.example"})
public class Application { ... }

// ✅ 方案二：确保 Mapper 接口和实现类在同一个 Spring 扫描路径下
// 推荐将 Mapper 接口放在 common/api 模块中，所有模块都能引用
```

### 问题速查表

| 问题 | 根因 | 一句话解决 |
|------|------|----------|
| 编译报「No property named xxx」 | 注解处理器顺序错误 | 加 `lombok-mapstruct-binding` |
| IDEA 报红但编译通过 | IDE 未识别生成的 Impl | 装 MapStruct 插件 + 开启 Annotation Processing |
| Jackson 反序列化失败 | `@Builder` 缺少无参构造 | 加 `@NoArgsConstructor` + `@AllArgsConstructor` |
| StackOverflow | `@Data` 递归 toString | `@ToString.Exclude` 排除关联字段 |
| 映射后字段为 null | 字段名不匹配 / 类型不匹配 | 加 `@Mapping` 或查看生成的 Impl 类 |
| 多模块找不到 Bean | Spring 扫描范围不够 | 扩大 `scanBasePackages` |

---

## 要点总结

1. **Lombok 消灭样板代码**：`@Data` 一个注解 = getter + setter + toString + equals + hashCode + 构造器
2. **MapStruct 消灭手动映射**：编译期生成映射代码，性能等同于手写，类型安全在编译期保证
3. **集成关键**：Lombok 必须先于 MapStruct 执行 → 加 `lombok-mapstruct-binding` 桥梁库
4. **Spring Boot 集成**：`@Mapper(componentModel = "spring")` 让 MapStruct 自动注册为 Spring Bean
5. **@Builder 三件套**：`@Builder` + `@NoArgsConstructor` + `@AllArgsConstructor`，否则 Jackson 反序列化失败
6. **@Data 慎用场景**：JPA 实体用 `@Getter @Setter` + `@ToString.Exclude` 替代 `@Data`

---

> ### 💡 新人小结：学完这一节，记住这六点
>
> 1. **Lombok = 自动缝纫机**：写注解 → 编译器帮你缝代码，运行时完全透明
> 2. **MapStruct = 定制翻译官**：定义接口 → 编译器帮你写映射，比反射快 100 倍
> 3. **顺序是生命线**：Lombok 先缝 → MapStruct 后裁，binding 库是排班表
> 4. **@Builder 必带三件套**：Builder + NoArgs + AllArgs，缺一不可
> 5. **@Data 不是万能的**：JPA 实体别用 @Data，关联字段会导致无限递归
> 6. **出了问题看 Impl**：MapStruct 生成的 Impl 类在 `target/generated-sources/` 下，打开一看就明白了
