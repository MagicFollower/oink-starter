---
title: Apache Fesod 与 Spring Boot 集成实战 —— Excel 上传下载与大文件导出
weight: 2
description: 在 Spring Boot 项目中集成 Apache Fesod 实现 Excel 导入导出：Controller 文件上传下载、HttpServletResponse 流式输出、ExcelWriter 分批写入避免 OOM、多 Sheet 导出、CSV 接口、multipart 配置调优，以及官方与社区最常遇到的集成问题排查。
---

## 为什么要在 Spring Boot 里集成 Fesod？

企业级 Web 项目中，Excel 导入导出几乎是标配功能：

- **导入**：用户上传 Excel 文件，后端解析入库
- **导出**：后端查询数据库，生成 Excel 文件供用户下载

用原生 POI 手写这些功能，代码量巨大——要处理 Workbook/Sheet/Row/Cell 的创建、样式设置、流关闭、响应头配置……一个导出接口动辄 100+ 行代码。

Apache Fesod 的价值在于：**你只需要定义实体类和注解，读写逻辑交给框架**。在 Spring Boot 中集成 Fesod，可以实现：

- 文件上传 → 自动解析 → 批量入库（3 行核心代码）
- 数据库查询 → 自动填充 → 文件下载（3 行核心代码）
- 百万行数据 → 分批写入 → 不 OOM（ExcelWriter 流式控制）

> ### 💡 新人小结：集成 Fesod 像什么？
>
> 把 Spring Boot 项目想象成一个**物流仓库**：
> - **Controller** = 前台接待（接收用户上传的文件 / 给用户提供下载）
> - **Fesod** = 后台叉车（负责把货物搬进搬出）
> - **HttpServletResponse** = 发货通道（文件从这里送到用户手里）
>
> 你不需要自己搬货（手写 POI），只需要告诉叉车往哪搬（定义实体类和注解）。
>
> 一句话总结：**Controller 负责接活，Fesod 负责干活，Response 负责交货。**

**学习路线图**

```
集成准备 → POJO 定义 → 文件上传（导入）→ 文件下载（导出）→ 流式大数据导出 → 多Sheet → CSV接口 → 配置调优 → 常见问题
依赖配置   实体类注解    MultipartFile      Response 流      ExcelWriter 分批    多张表     轻量格式    参数优化    怎么避坑
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| MultipartFile | — | Spring 的文件上传接口 | 接收用户上传的 Excel |
| HttpServletResponse | — | Servlet 响应对象 | 向用户输出 Excel 文件 |
| Content-disposition | HTTP 响应头 | 告诉浏览器这是附件下载 | 触发浏览器下载行为 |
| ExcelWriter | — | Fesod 写入器，控制写入生命周期 | 分批写入、多 Sheet 写入 |
| WriteSheet | — | 写入 Sheet 描述对象 | 指定 Sheet 名称和索引 |
| PageReadListener | — | Fesod 内置分页批量监听器 | 批量处理上传数据 |
| URLEncoder | java.net.URLEncoder | URL 编码工具 | 处理中文文件名乱码 |

---

## 集成准备

### pom.xml 依赖

```xml
<dependencies>
    <!-- Spring Boot Web -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <!-- Apache Fesod -->
    <dependency>
        <groupId>org.apache.fesod</groupId>
        <artifactId>fesod-sheet</artifactId>
        <version>2.0.2-incubating</version>
    </dependency>

    <!-- Lombok（简化实体类） -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

### application.yml 配置

```yaml
server:
  port: 8080

spring:
  servlet:
    multipart:
      # 单个文件上传大小限制
      max-file-size: 10MB
      # 同时上传多个文件时的总大小限制
      max-request-size: 100MB
```

> **为什么必须配置 multipart？** Spring Boot 默认的 `max-file-size` 是 1MB——用户上传一个稍大的 Excel 就会报 `MaxUploadSizeExceededException`。生产环境建议根据业务需求调整。

---

## POJO 实体类定义

实体类定义了 Java 字段与 Excel 列的映射关系——这是导入导出的核心。

```java
@Data
public class Employee {

    @ExcelProperty(value = "编号", converter = LongStringConverter.class)
    @ColumnWidth(15)
    private Long empNo;

    @ExcelProperty("姓名")
    private String empName;

    @ExcelProperty("年龄")
    private Integer empAge;

    @ExcelProperty(value = "性别", converter = GenderConverter.class)
    private Integer empGender;    // 1=男, 0=女, -1=保密

    @ExcelProperty("工资")
    private BigDecimal empSalary;

    @ExcelProperty("创建时间")
    @ColumnWidth(20)
    private LocalDateTime createTime;
}
```

其中 `GenderConverter` 是自定义转换器（详见上一篇《Apache Fesod 核心 API 与实战》）：

```java
public class GenderConverter implements Converter<Integer> {

    @Override
    public Integer convertToJavaData(ReadConverterContext<?> context) {
        String value = context.getReadCellData().getStringValue();
        if ("男".equals(value)) return 1;
        if ("女".equals(value)) return 0;
        return -1;
    }

    @Override
    public WriteCellData<?> convertToExcelData(WriteConverterContext<Integer> context) {
        Integer value = context.getValue();
        if (value != null && value == 1) return new WriteCellData<>("男");
        if (value != null && value == 0) return new WriteCellData<>("女");
        return new WriteCellData<>("保密");
    }
}
```

---

## 文件上传（Excel 导入）

### 基础版：上传并返回解析结果

```java
@PostMapping("/upload")
public ResponseEntity<List<Employee>> uploadExcel(
        @RequestParam("file") MultipartFile file) {
    if (file.isEmpty()) {
        return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
    }
    try {
        List<Employee> result = new ArrayList<>();
        FesodSheet.read(file.getInputStream(), Employee.class,
            new PageReadListener<Employee>(result::addAll))
            .sheet()
            .doRead();
        return new ResponseEntity<>(result, HttpStatus.OK);
    } catch (Exception e) {
        return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

**核心流程**：

```
用户上传文件 → MultipartFile 接收 → getInputStream() 获取流
→ FesodSheet.read() 解析 → PageReadListener 批量收集 → 返回结果
```

### 进阶版：带业务处理与错误统计

```java
@PostMapping("/import")
public ResponseEntity<Map<String, Object>> importEmployees(
        @RequestParam("file") MultipartFile file) {

    List<Employee> successList = new ArrayList<>();
    List<String> errorMessages = new ArrayList<>();

    FesodSheet.read(file.getInputStream(), Employee.class,
        new ReadListener<Employee>() {
            @Override
            public void invoke(Employee employee, AnalysisContext context) {
                // 业务校验：姓名不能为空
                if (employee.getEmpName() == null || employee.getEmpName().isEmpty()) {
                    int rowIndex = context.readRowHolder().getRowIndex();
                    errorMessages.add("第 " + rowIndex + " 行：姓名为空");
                    return;    // 跳过这条，继续读下一行
                }
                successList.add(employee);
            }

            @Override
            public void doAfterAllAnalysed(AnalysisContext context) {
                // 读取完成，可以做收尾工作
            }

            @Override
            public void onException(Exception exception, AnalysisContext context) {
                int rowIndex = context.readRowHolder().getRowIndex();
                errorMessages.add("第 " + rowIndex + " 行数据转换异常: " + exception.getMessage());
                // 不抛异常 → 跳过错误行，继续读取
            }
        })
        .sheet()
        .doRead();

    Map<String, Object> result = new HashMap<>();
    result.put("successCount", successList.size());
    result.put("errorCount", errorMessages.size());
    result.put("errors", errorMessages);

    // 批量入库
    if (!successList.isEmpty()) {
        employeeService.batchInsert(successList);
    }

    return new ResponseEntity<>(result, HttpStatus.OK);
}
```

> ### 💡 新人小结：导入就像收快递
>
> 1. 前台（Controller）签收包裹（MultipartFile）
> 2. 拆开包裹（FesodSheet.read）
> 3. 逐件检查（Listener.invoke）——合格的入库，不合格的登记（errorMessages）
> 4. 全部检查完，汇报结果（返回 successCount / errorCount）

---

## 文件下载（Excel 导出）

### 基础版：查询数据生成 Excel 下载

```java
@GetMapping("/download")
public void downloadExcel(HttpServletResponse response) throws Exception {
    // 1. 准备数据（实际项目中从数据库查询）
    List<Employee> dataList = employeeService.findAll();

    // 2. 设置响应头
    String fileName = URLEncoder.encode("员工信息_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setCharacterEncoding("utf-8");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    // 3. 直接写入响应流
    FesodSheet.write(response.getOutputStream(), Employee.class)
        .sheet("员工信息")
        .doWrite(dataList);
}
```

**关键细节解析**：

| 代码 | 作用 |
|------|------|
| `URLEncoder.encode(..., "UTF-8")` | 对中文文件名进行 URL 编码，避免浏览器乱码 |
| `.replaceAll("\\+", "%20")` | URLEncoder 把空格编码为 `+`，需要替换回 `%20` |
| `Content-disposition: attachment;filename*=utf-8''...` | RFC 5987 标准，支持 UTF-8 文件名 |
| `response.getOutputStream()` | 直接写入响应流，不产生临时文件 |

> **注意**：`response.setContentType()` 必须在 `FesodSheet.write()` **之前**调用。一旦 Fesod 开始写入输出流，再修改响应头就会报 `IllegalStateException`。

---

## 流式大数据导出（避免 OOM）

### 问题：doWrite() 一次性写入的风险

`doWrite(dataList)` 会将整个 dataList 加载到内存再写入。当数据量超过 10 万行时，内存中同时存在：

- 原始数据 List
- POI 的 Workbook 对象（所有 Sheet/Row/Cell）
- 序列化缓冲区

三者叠加很容易突破 JVM 堆内存限制。

### 解决方案：ExcelWriter 分批写入

```java
@GetMapping("/export-large")
public void exportLargeExcel(HttpServletResponse response) throws Exception {
    // 设置响应头（同上，省略）
    setExcelResponseHeader(response, "大数据导出");

    int batchSize = 5000;    // 每批 5000 条
    int total = employeeService.count();    // 总数据量

    try (ExcelWriter writer = FesodSheet.write(response.getOutputStream(), Employee.class).build()) {
        WriteSheet sheet = FesodSheet.writerSheet(0, "全量数据").build();

        for (int offset = 0; offset < total; offset += batchSize) {
            // 分页查询数据库——每次只加载 5000 条到内存
            List<Employee> batch = employeeService.findByPage(offset, batchSize);
            writer.write(batch, sheet);
            // batch 在下次循环时可被 GC 回收
        }
    }
    // try-with-resources 自动调用 writer.finish()，关闭流
}
```

**流式导出的内存模型**：

```
传统 doWrite()：
内存 = 全部数据(10万条) + POI Workbook + 缓冲区 = 容易 OOM

ExcelWriter 分批写入：
内存 = 当前批次(5000条) + POI Workbook(增量) + 缓冲区 = 可控
```

> ### 💡 新人小结：分批导出像什么？
>
> 传统导出 = 一次性把 10 吨货物全装上卡车（车可能超载翻车）
> 分批导出 = 每次装 500 斤，装完一趟发一趟，再回来装下一趟
>
> 关键区别：**数据库分页查询** + **ExcelWriter 分批写入** = 内存永远只占一个批次的大小。

---

## 多 Sheet 导出

```java
@GetMapping("/export-multi-sheet")
public void exportMultiSheet(HttpServletResponse response) throws Exception {
    setExcelResponseHeader(response, "多Sheet导出");

    List<Employee> employees = employeeService.findByDept("普通员工");
    List<Employee> managers = employeeService.findByDept("管理层");
    List<Employee> interns = employeeService.findByDept("实习生");

    try (ExcelWriter writer = FesodSheet.write(response.getOutputStream(), Employee.class).build()) {
        // Sheet 1：普通员工
        WriteSheet sheet1 = FesodSheet.writerSheet(0, "普通员工").build();
        writer.write(employees, sheet1);

        // Sheet 2：管理层
        WriteSheet sheet2 = FesodSheet.writerSheet(1, "管理层").build();
        writer.write(managers, sheet2);

        // Sheet 3：实习生
        WriteSheet sheet3 = FesodSheet.writerSheet(2, "实习生").build();
        writer.write(interns, sheet3);
    }
}
```

---

## CSV 导出接口

CSV 比 Excel 更轻量——纯文本格式，适合数据交换场景：

```java
@GetMapping("/export-csv")
public void exportCsv(HttpServletResponse response) throws Exception {
    List<Employee> dataList = employeeService.findAll();

    String fileName = URLEncoder.encode("员工数据_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("text/csv; charset=utf-8");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".csv");

    // 写入 CSV 时添加 BOM 头，确保 Excel 打开不乱码
    response.getOutputStream().write(new byte[]{(byte) 0xEF, (byte) 0xBB, (byte) 0xBF});

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .csv()
        .nullString("N/A")    // null 值显示为 N/A
        .doWrite(dataList);
}
```

> **BOM 头的作用**：Windows 版 Excel 打开 CSV 时，如果没有 UTF-8 BOM（EF BB BF），会按 ANSI 编码解析，中文全部乱码。加上 BOM 头后 Excel 能正确识别为 UTF-8。

---

## 配置调优

### multipart 上传限制

| 配置项 | 默认值 | 建议值 | 说明 |
|--------|--------|--------|------|
| `spring.servlet.multipart.max-file-size` | 1MB | 10MB-50MB | 单个文件上限 |
| `spring.servlet.multipart.max-request-size` | 10MB | 100MB | 多文件总上限 |
| `spring.servlet.multipart.file-size-threshold` | 0 | 2MB | 超过此值写临时文件 |

### Fesod 读取批处理大小

`PageReadListener` 的默认批量大小为 100 条。对于大数据量导入，可以适当增大：

```java
// 每 500 条触发一次批量处理
new PageReadListener<Employee>(dataList -> {
    employeeService.batchInsert(dataList);
}, 500)
```

### 临时文件目录

Fesod 底层 POI 在处理大文件时可能产生临时文件。可以通过 JVM 参数指定临时目录：

```bash
java -Djava.io.tmpdir=/data/tmp -jar your-app.jar
```

---

## 官方 / 社区最常出现的问题

| 问题 | 原因分析 | 解决方案 |
|------|---------|---------|
| **上传文件报 MaxUploadSizeExceededException** | Spring Boot 默认 `max-file-size` 只有 1MB | 在 `application.yml` 中配置 `spring.servlet.multipart.max-file-size` |
| **下载文件名中文乱码** | 没有做 URL 编码或 Content-disposition 格式不对 | 用 `URLEncoder.encode()` + `filename*=utf-8''` 格式（RFC 5987） |
| **大文件导出 OOM** | 用 `doWrite()` 一次性写入全部数据 | 改用 `ExcelWriter` + 分批 `write()` + 数据库分页查询 |
| **下载接口报 IllegalStateException: response already committed** | 在 `FesodSheet.write()` 之后又修改了响应头或调用了 `forward()` | 确保响应头在写入之前设置；不要在写入后操作 response |
| **CSV 下载用 Excel 打开中文乱码** | 缺少 UTF-8 BOM 头 | 在写入 CSV 前先写入 BOM 字节 `EF BB BF` |
| **POI 版本冲突（NoSuchMethodError / ClassNotFoundException）** | 项目已有 POI 依赖与 Fesod 自带的 POI 5.5.1 冲突 | `mvn dependency:tree` 排查，统一 POI 版本 |
| **上传解析后数据为空** | Excel 表头与 `@ExcelProperty` 注解值不匹配 | 检查注解值与 Excel 表头是否完全一致（空格、大小写） |
| **并发导出时数据错乱** | 多个请求共用同一个 ExcelWriter 实例 | ExcelWriter 是线程不安全的，每次请求创建新实例（不要做成 Bean） |

---

## Q&A / 踩坑

**Q1：ExcelWriter 能做成 Spring Bean 单例复用吗？**

不能。`ExcelWriter` 内部维护了 Workbook 状态，是**线程不安全**的。每次导出请求都应该创建新的 ExcelWriter 实例。推荐用 try-with-resources 自动管理生命周期。

**Q2：导出时怎么设置单元格样式（背景色、字体、边框）？**

Fesod 提供了样式注解：

```java
@HeadStyle(fillPatternType = FillPatternType.SOLID_FOREGROUND, fillForegroundColor = IndexedColors.YELLOW)
@HeadFontStyle(fontName = "微软雅黑", bold = true, fontHeightInPoints = 12)
@ExcelProperty("姓名")
private String name;
```

这些注解在 `org.apache.fesod.sheet.annotation.write.style` 包下，支持 `@HeadStyle`、`@HeadFontStyle`、`@ContentStyle`、`@ContentFontStyle`、`@ColumnWidth`、`@RowHeight` 等。

**Q3：导入时怎么跳过空行？**

在自定义 Listener 的 `invoke()` 方法中判断：

```java
@Override
public void invoke(Employee employee, AnalysisContext context) {
    // 跳过所有字段都为 null 的行
    if (employee.getEmpNo() == null && employee.getEmpName() == null) {
        return;
    }
    // 正常处理
    successList.add(employee);
}
```

**Q4：导出文件名带日期，但浏览器显示异常？**

确保三点：
1. 用 `URLEncoder.encode(fileName, "UTF-8")` 编码
2. 替换 `+` 为 `%20`：`.replaceAll("\\+", "%20")`
3. Content-disposition 用 `filename*=utf-8''` 格式（注意是两个单引号）

---

## 要点总结

1. **集成三步**：引入 `fesod-sheet` 依赖 → 配置 multipart 上传限制 → 定义带注解的实体类
2. **导入**：Controller 接收 `MultipartFile` → `FesodSheet.read(inputStream, ...)` → 自定义 Listener 处理业务逻辑和错误统计
3. **导出**：设置响应头（Content-Type / Content-disposition）→ `FesodSheet.write(response.getOutputStream(), ...)` → 直接写入响应流
4. **大数据导出**：`ExcelWriter` + 数据库分页查询 + 分批 `write(data, sheet)` = 内存可控
5. **多 Sheet**：`ExcelWriter` + 多个 `WriteSheet`，每个 Sheet 写入不同数据
6. **CSV 导出**：`.csv()` 切换模式 + BOM 头（解决 Excel 打开中文乱码）
7. **线程安全**：ExcelWriter 不能做成 Bean 单例，每次请求创建新实例
8. **文件名乱码**：URLEncoder + `filename*=utf-8''`（RFC 5987 标准）

---

> ### 💡 新人小结：Spring Boot 集成 Fesod 的三句话
>
> 1. **导入**：`MultipartFile` → `FesodSheet.read(流, 实体类, 监听器)` → 逐行校验入库
> 2. **导出**：设响应头 → `FesodSheet.write(Response流, 实体类).sheet("名称").doWrite(数据)`
> 3. **大文件**：永远用 `ExcelWriter` 分批写，别用 `doWrite()` 一把梭
>
> 记住这三句话，90% 的 Excel 导入导出需求都能搞定。剩下 10% 的复杂场景（模板填充、复杂样式、图表）可以查阅 Fesod 官方文档进一步学习。
