---
title: Apache Fesod 核心 API 与实战 —— 高性能电子表格读写
weight: 1
description: POI 全量加载大文件 OOM？EasyExcel 停止维护？Apache Fesod（Incubating）是高性能、低内存的 Java 电子表格读写库，从 EasyExcel 到 FastExcel 再到 Apache 孵化的演进终章。本文详解核心 API（FesodSheet 流式读写）、注解体系（@ExcelProperty / @ExcelIgnore / @ColumnWidth）、监听器机制（ReadListener / PageReadListener）、自定义转换器、多 Sheet 操作、CSV 支持，覆盖官方与社区最常遇到的问题排查。
---

## 为什么需要 Apache Fesod？

Java 生态处理 Excel 文件，长期面临三个痛点：

**痛点一：POI 全量加载，大文件直接 OOM。**

Apache POI 的 `XSSFWorkbook` 会把整个 Excel 文件加载到内存——一个 10 万行的 Excel 轻松吃掉 1GB+ 堆内存。生产环境遇到百万行报表，直接 `OutOfMemoryError`。

**痛点二：EasyExcel 进入维护模式，不再有新特性。**

阿里 EasyExcel 曾是解决大文件读写的明星方案，但已明确进入维护模式——只修 bug，不加新功能。

**痛点三：手写 POI SAX 解析，复杂度高、易出错。**

POI 提供了 `XSSF EventModel`（SAX 模式）实现流式读取，但 API 极其底层——需要自己处理 Sheet/Row/Cell 事件回调、数据类型判断、合并单元格处理，开发成本很高。

Apache Fesod（Incubating）正是为解决这三个问题而生的：

```
演进路线：
EasyExcel（阿里，维护模式）→ FastExcel（社区延续）→ Apache Fesod（Apache 孵化，活跃开发）
```

Fesod 这个名字是 **"fast easy spreadsheet and other documents"** 的缩写，读作 /ˈfɛsɒd/。

> ### 💡 新人小结：Fesod 是什么？
>
> 把 Excel 文件想象成**仓库货架**：
> - **Sheet** = 货架的一层
> - **Row** = 这一层的一个货位
> - **Cell** = 货位里的货物
>
> POI 的做法是把**整个货架搬回家**——货多的时候搬不动（OOM）。
> Fesod 的做法是给你一台**智能叉车**——按需取货，一次只搬一层，搬完再搬下一层。
>
> 一句话总结：**Fesod 是 Java 电子表格的高性能读写引擎，流式处理大文件不 OOM。**

**学习路线图**

```
演进背景 → 依赖引入 → 核心 API → 注解 → 监听器 → 转换器 → 读实战 → 写实战 → CSV → 多Sheet → 常见问题
从哪来      怎么装      怎么用      怎么映射   怎么处理    怎么转换    怎么读     怎么写    表格外   多张表    怎么避坑
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| FesodSheet | — | Fesod 的核心入口类，提供 read/write 静态方法 | 所有操作的起点 |
| ExcelProperty | @ExcelProperty | 注解：标记 Java 字段与 Excel 列的映射关系 | 字段 ↔ 列的绑定 |
| ExcelIgnore | @ExcelIgnore | 注解：标记不参与读写的字段 | 排除某些字段 |
| ReadListener | ReadListener\<T\> | 读取监听器接口：每读一行触发一次回调 | 逐行处理数据 |
| PageReadListener | PageReadListener\<T\> | Fesod 内置的分页批量监听器 | 批量处理而非逐行 |
| Converter | Converter\<T\> | 转换器接口：自定义字段类型与单元格值的互转 | 处理特殊格式 |
| ExcelReader | — | 读取器：控制读取生命周期，支持多 Sheet 读取 | 高级读取控制 |
| ExcelWriter | — | 写入器：控制写入生命周期，支持多 Sheet 写入 | 高级写入控制 |
| AnalysisContext | — | 读取上下文：包含当前行号、Sheet 信息等 | 监听器中获取元数据 |

---

## 演进背景与包名变更

| 阶段 | 项目名 | Maven groupId | 状态 |
|------|--------|---------------|------|
| 1.0 | EasyExcel | `com.alibaba` | 维护模式，不再有新特性 |
| 2.0 | FastExcel | `cn.idev.excel` | 社区延续，后捐给 Apache |
| 3.0 | Apache Fesod | `org.apache.fesod` | Apache 孵化中，活跃开发 |

**包名变更对照**（迁移时全局替换）：

| 旧包名（FastExcel） | 新包名（Fesod） |
|---------------------|-----------------|
| `cn.idev.excel` | `org.apache.fesod.sheet` |
| `com.alibaba.excel` | `org.apache.fesod.sheet` |

> 如果项目从 EasyExcel/FastExcel 迁移，除了改包名和 Maven 坐标，API 用法基本一致——Fesod 保持了向后兼容。官方还提供了基于 OpenRewrite 的自动迁移方案。

---

## Maven 依赖

```xml
<dependency>
    <groupId>org.apache.fesod</groupId>
    <artifactId>fesod-sheet</artifactId>
    <version>2.0.2-incubating</version>
</dependency>
```

**POI 冲突排除**：Fesod 底层依赖 Apache POI 5.5.1。如果你的项目已经引入了其他版本的 POI，需要手动排除避免冲突：

```xml
<dependency>
    <groupId>org.apache.fesod</groupId>
    <artifactId>fesod-sheet</artifactId>
    <version>2.0.2-incubating</version>
    <exclusions>
        <exclusion>
            <groupId>org.apache.poi</groupId>
            <artifactId>poi</artifactId>
        </exclusion>
        <exclusion>
            <groupId>org.apache.poi</groupId>
            <artifactId>poi-ooxml</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- 然后显式声明你需要的 POI 版本 -->
```

**底层依赖一览**（来自官方文档）：

| 依赖 | 版本 | 用途 |
|------|------|------|
| Apache POI | 5.5.1 | Excel 文件处理 |
| Apache Commons CSV | 1.14.1 | CSV 文件支持 |
| Ehcache | 3.9.11 | 缓存功能 |

---

## 核心 API 一览

Fesod 的所有操作都从 `FesodSheet` 这个入口类开始——它提供 `read()` 和 `write()` 两个静态方法，覆盖所有场景。

### 读取 API

```java
// 最简读取：文件路径 + 实体类 + 监听器
FesodSheet.read("demo.xlsx", DemoData.class, new DemoDataListener())
    .sheet()          // 指定 Sheet（不指定则默认第一个）
    .doRead();        // 执行读取

// 从 InputStream 读取（适合 Spring Boot 文件上传场景）
FesodSheet.read(inputStream, DemoData.class, new DemoDataListener())
    .sheet()
    .doRead();

// 读取所有 Sheet
FesodSheet.read("demo.xlsx", DemoData.class, new DemoDataListener())
    .doReadAll();     // 遍历所有 Sheet
```

### 写入 API

```java
// 最简写入：文件路径 + 实体类 + 数据
FesodSheet.write("demo.xlsx", DemoData.class)
    .sheet("模板")    // 指定 Sheet 名称
    .doWrite(data()); // 执行写入

// 写入到 OutputStream（适合 Spring Boot 文件下载场景）
FesodSheet.write(response.getOutputStream(), DemoData.class)
    .sheet("模板")
    .doWrite(dataList);
```

> ### 💡 新人小结：核心 API 就两个方法
>
> - **`FesodSheet.read(数据源, 实体类, 监听器)`** → 链式调用 `.sheet().doRead()`
> - **`FesodSheet.write(输出目标, 实体类)`** → 链式调用 `.sheet("名称").doWrite(数据)`
>
> 就像叉车操作手册：`read` 是取货，`write` 是放货，`.sheet()` 是选择哪一层。

---

## 注解体系

注解定义了 Java 字段与 Excel 列之间的映射关系——这是 Fesod 最核心的设计。

### @ExcelProperty：字段 ↔ 列映射

```java
public class Employee {

    // 按列名映射（推荐）：Excel 表头为「编号」的列 → empNo 字段
    @ExcelProperty("编号")
    private Long empNo;

    // 按列索引映射（第 0 列 = A 列）：不受表头文字影响
    @ExcelProperty(index = 1)
    private String name;

    // 多列名匹配：表头为「姓名」或「名字」都能匹配
    @ExcelProperty({"姓名", "名字"})
    private String name2;
}
```

> **注意**：按列名匹配时，Excel 表头文字**必须完全一致**——多一个空格、少一个字都匹配不上，该列数据会为空。这是社区最高频的问题之一。

### @ExcelIgnore：排除字段

```java
public class Employee {
    @ExcelProperty("编号")
    private Long empNo;

    @ExcelIgnore    // 这个字段不参与读写
    private String internalNote;
}
```

### @ColumnWidth：列宽

```java
@ExcelProperty("创建时间")
@ColumnWidth(20)    // 指定列宽为 20 个字符宽度
private LocalDateTime createTime;
```

不指定列宽时，Excel 按默认宽度显示，日期等长内容可能显示为 `####`。

### @DateTimeFormat：日期格式

```java
@ExcelProperty("入职日期")
@DateTimeFormat("yyyy-MM-dd")    // 指定日期格式
private LocalDate hireDate;
```

---

## 监听器机制

监听器是 Fesod 读取数据的核心处理方式——每读到一行数据，就触发一次回调。

### ReadListener\<T\> 接口

```java
public class EmployeeListener implements ReadListener<Employee> {

    // 每读取一行数据触发一次
    @Override
    public void invoke(Employee employee, AnalysisContext context) {
        System.out.println("读取到: " + employee);
        // 这里可以做数据校验、入库等操作
    }

    // 一个 Sheet 全部读完后触发
    @Override
    public void doAfterAllAnalysed(AnalysisContext context) {
        System.out.println("全部读取完成");
    }

    // 读取异常时触发（可选覆写）
    @Override
    public void onException(Exception exception, AnalysisContext context) throws Exception {
        System.err.println("第 " + context.readRowHolder().getRowIndex() + " 行读取失败");
        if (exception instanceof ExcelDataConvertException) {
            ExcelDataConvertException ex = (ExcelDataConvertException) exception;
            System.err.println("第 " + ex.getRowIndex() + " 行, 第 " + ex.getColumnIndex()
                + " 列转换异常: " + ex.getCellData());
        }
        // 不抛异常则继续读取下一行；抛出异常则终止读取
    }
}
```

### PageReadListener：内置分页批量处理

逐行处理太慢？`PageReadListener` 按批次收集数据，攒够一批后统一处理：

```java
// 每 100 条触发一次批量处理
FesodSheet.read("demo.xlsx", Employee.class,
    new PageReadListener<Employee>(dataList -> {
        // dataList 最多 100 条，批量入库
        employeeMapper.batchInsert(dataList);
    }, 100))    // 第二个参数：每批大小，默认 100
    .sheet()
    .doRead();
```

> ### 💡 新人小结：监听器像什么？
>
> 监听器就像**流水线上的质检员**：
> - `invoke()` = 每来一件检查一件（逐行处理）
> - `PageReadListener` = 攒够一箱再统一检查（批量处理）
> - `doAfterAllAnalysed()` = 所有货物过完流水线后的总结报告
> - `onException()` = 遇到坏件时的报警机制

---

## 转换器

转换器定义了 Java 字段类型与 Excel 单元格值之间的**互转规则**。

### 内置转换器

| Java 类型 | 默认转换行为 |
|-----------|-------------|
| String | 直接读写字符串 |
| Integer / Long / Double | 数字 ↔ 数值单元格 |
| BigDecimal | 数字 ↔ 数值单元格（高精度） |
| Date / LocalDate / LocalDateTime | 日期 ↔ 日期单元格（可用 @DateTimeFormat 指定格式） |
| Boolean | true/false ↔ 布尔单元格 |

### 自定义转换器

当内置转换不满足需求时（比如性别字段：Java 中是 Integer 1/0，Excel 中要显示「男」/「女」），需要自定义转换器：

```java
public class GenderConverter implements Converter<Integer> {

    // Excel → Java：从单元格读取时调用
    @Override
    public Integer convertToJavaData(ReadConverterContext<?> context) {
        String value = context.getReadCellData().getStringValue();
        if ("男".equals(value)) return 1;
        if ("女".equals(value)) return 0;
        return -1;  // 保密
    }

    // Java → Excel：写入单元格时调用
    @Override
    public WriteCellData<?> convertToExcelData(WriteConverterContext<Integer> context) {
        Integer value = context.getValue();
        if (value != null && value == 1) return new WriteCellData<>("男");
        if (value != null && value == 0) return new WriteCellData<>("女");
        return new WriteCellData<>("保密");
    }
}
```

使用方式——在 `@ExcelProperty` 中指定：

```java
@ExcelProperty(value = "性别", converter = GenderConverter.class)
private Integer gender;
```

---

## 读实战

### 读取单个 Sheet

```java
// 默认读取第一个 Sheet
FesodSheet.read("employee.xlsx", Employee.class, new PageReadListener<Employee>(
    dataList -> dataList.forEach(System.out::println)
)).sheet().doRead();
```

### 读取指定 Sheet

```java
// 按索引读取（从 0 开始）
FesodSheet.read("employee.xlsx", Employee.class, new PageReadListener<Employee>(
    dataList -> dataList.forEach(System.out::println)
)).sheet(2).doRead();    // 读取第 3 个 Sheet

// 按名称读取
FesodSheet.read("employee.xlsx", Employee.class, new PageReadListener<Employee>(
    dataList -> dataList.forEach(System.out::println)
)).sheet("员工信息").doRead();
```

### 读取所有 Sheet

```java
// doReadAll() 遍历所有 Sheet，每读完一个 Sheet 触发一次 doAfterAllAnalysed
FesodSheet.read("employee.xlsx", Employee.class, new EmployeeListener())
    .doReadAll();
```

### 高级读取：ExcelReader 精细控制

```java
// 同时读取不同 Sheet，每个 Sheet 用不同的监听器
try (ExcelReader excelReader = FesodSheet.read("employee.xlsx").build()) {
    ReadSheet sheet1 = FesodSheet.readSheet(0)
        .head(Employee.class)
        .registerReadListener(new PageReadListener<Employee>(dataList -> {
            System.out.println("Sheet1 数据: " + dataList.size() + " 条");
        }))
        .build();

    ReadSheet sheet2 = FesodSheet.readSheet("销售报表")
        .head(SaleData.class)
        .registerReadListener(new PageReadListener<SaleData>(dataList -> {
            System.out.println("销售报表数据: " + dataList.size() + " 条");
        }))
        .build();

    excelReader.read(sheet1, sheet2);
}
```

### 跳过表头行

```java
FesodSheet.read("employee.xlsx", Employee.class, listener)
    .sheet()
    .headRowNumber(2)    // 跳过前 2 行（默认 1）
    .doRead();
```

---

## 写实战

### 写入单个 Sheet

```java
List<Employee> data = buildTestData();

FesodSheet.write("output.xlsx", Employee.class)
    .sheet("员工信息")
    .doWrite(data);
```

### 写入多个 Sheet

```java
List<Employee> employees = buildEmployeeData();
List<Employee> managers = buildManagerData();

// 用 ExcelWriter 控制写入生命周期
try (ExcelWriter writer = FesodSheet.write("multi-sheet.xlsx", Employee.class).build()) {
    // 第 1 个 Sheet
    WriteSheet sheet1 = FesodSheet.writerSheet(0, "普通员工").build();
    writer.write(employees, sheet1);

    // 第 2 个 Sheet
    WriteSheet sheet2 = FesodSheet.writerSheet(1, "管理层").build();
    writer.write(managers, sheet2);
}
// try-with-resources 自动关闭流
```

### 分批写入大量数据

```java
List<Employee> allData = getAllData();  // 假设 10 万条
int batchSize = 5000;

try (ExcelWriter writer = FesodSheet.write("big-data.xlsx", Employee.class).build()) {
    WriteSheet sheet = FesodSheet.writerSheet(0, "全量数据").build();
    for (int i = 0; i < allData.size(); i += batchSize) {
        List<Employee> batch = allData.subList(i, Math.min(i + batchSize, allData.size()));
        writer.write(batch, sheet);    // 分批写入，不一次性加载
    }
}
```

---

## CSV 支持

Fesod 不仅支持 Excel，还支持 CSV 文件的读写：

### 读取 CSV

```java
FesodSheet.read("data.csv", Employee.class, new PageReadListener<Employee>(
    dataList -> dataList.forEach(System.out::println)
))
.csv()                                    // 切换为 CSV 模式
.delimiter(CsvConstant.COMMA)            // 字段分隔符（默认逗号，可省略）
.quote(CsvConstant.DOUBLE_QUOTE, QuoteMode.MINIMAL)  // 引用符号（默认双引号，可省略）
.doRead();
```

### 写入 CSV

```java
FesodSheet.write("output.csv", Employee.class)
.csv()
.nullString("N/A")    // null 值替换为 "N/A"
.doWrite(data);
```

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **@ExcelProperty 按名称匹配读不到数据** | Excel 表头文字与注解值不完全一致（多余空格、全角/半角字符） | 确保注解值与 Excel 表头**完全一致**；或用 `index` 按列索引匹配 |
| **POI 版本冲突（NoSuchMethodError）** | 项目已有 POI 依赖与 Fesod 自带的 POI 5.5.1 版本不一致 | 用 `mvn dependency:tree` 排查，排除冲突版本或统一 POI 版本 |
| **大文件读取仍然 OOM** | 监听器中把所有数据攒到 List 里没释放 | 用 `PageReadListener` 分批处理，每批处理完及时释放（如批量入库后清空） |
| **日期读取为数字（如 45123.0）** | Excel 内部以数字存储日期，需要指定格式转换 | 在字段上加 `@DateTimeFormat("yyyy-MM-dd")` |
| **写入后 Excel 打开显示 ####** | 列宽不够，日期/长文本被截断 | 加 `@ColumnWidth(20)` 指定足够宽度 |
| **CSV 读取中文乱码** | CSV 文件编码不是 UTF-8（如 GBK） | 确保 CSV 文件保存为 UTF-8 编码，或读取时指定编码 |
| **多 Sheet 写入只有第一个有数据** | 没有用 `ExcelWriter` 控制生命周期，每次 `doWrite()` 都创建新文件 | 用 `FesodSheet.write(...).build()` 获取 ExcelWriter，多次 `write(data, sheet)` |
| **@ExcelIgnore 不生效** | 字段同时在父类标注了 @ExcelProperty，子类标注 @ExcelIgnore | 检查继承关系，确保注解不冲突（Fesod 2.0.1+ 已修复此问题） |

---

## Q&A / 踩坑

**Q1：Fesod 和 EasyExcel 的 API 完全兼容吗？**

核心 API 兼容——`FesodSheet.read()` / `write()` 的用法与 EasyExcel 的 `EasyExcel.read()` / `write()` 几乎一致。主要区别是包名从 `com.alibaba.excel` 变为 `org.apache.fesod.sheet`，类名前缀从 `EasyExcel` 变为 `FesodSheet`。官方提供了 OpenRewrite 迁移方案可自动完成批量替换。

**Q2：不用注解，能用 Fesod 读写吗？**

可以。不指定实体类时，Fesod 以 `Map<Integer, String>` 形式返回每行数据（key = 列索引，value = 单元格值）：

```java
FesodSheet.read("demo.xlsx", null, new PageReadListener<Map<Integer, String>>(
    dataList -> dataList.forEach(System.out::println)
)).sheet().doRead();
```

**Q3：Fesod 支持 .xls（旧格式）吗？**

支持。Fesod 底层通过 POI 同时支持 `.xls`（HSSF，Excel 97-2003）和 `.xlsx`（XSSF，Excel 2007+）。API 层面不需要做任何区分——传入文件路径或流即可，Fesod 自动识别格式。

**Q4：PageReadListener 的默认批量大小是多少？**

默认 100 条。可以通过构造方法的第二个参数自定义：`new PageReadListener<>(consumer, 500)` 表示每 500 条触发一次。

---

## 要点总结

1. **演进路线**：EasyExcel → FastExcel → Apache Fesod（2.0.2-incubating），API 向后兼容，包名变为 `org.apache.fesod.sheet`
2. **核心入口**：`FesodSheet.read()` / `FesodSheet.write()`，流式 API 链式调用
3. **注解映射**：`@ExcelProperty`（按名称/索引）、`@ExcelIgnore`（排除）、`@ColumnWidth`（列宽）、`@DateTimeFormat`（日期格式）
4. **监听器**：`ReadListener<T>` 逐行处理；`PageReadListener` 批量处理（推荐，避免 OOM）
5. **转换器**：`Converter<T>` 自定义字段 ↔ 单元格互转规则；内置覆盖常用类型
6. **多 Sheet**：读取用 `doReadAll()` 或 `ExcelReader`；写入用 `ExcelWriter` + 多个 `WriteSheet`
7. **CSV 支持**：`.csv()` 切换模式，可配置分隔符、引用符号、null 替换值
8. **POI 冲突**：项目已有 POI 时需手动排除，避免版本冲突

---

> ### 💡 新人小结：Fesod 核心 API 学完了，记住这 3 点
>
> 1. **读文件三件套**：`FesodSheet.read(文件, 实体类, 监听器).sheet().doRead()`
> 2. **写文件三件套**：`FesodSheet.write(文件, 实体类).sheet("名称").doWrite(数据)`
> 3. **大文件用 PageReadListener**——分批处理不 OOM，别自己攒 List
>
> 接下来，翻开第二篇《Apache Fesod 与 Spring Boot 集成实战》，看看怎么在 Web 项目中实现 Excel 的上传下载。
