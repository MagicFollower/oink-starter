---
title: Apache Fesod 十二大高频场景实战 —— 从导入校验到异步导出的完整案例集
weight: 3
description: 基于前两篇核心 API 与 Spring Boot 集成基础，本文从企业实际项目中的 12 个高频使用场景切入：批量导入校验、条件筛选导出、百万级流式导出、动态列导出、按维度分 Sheet、样式报表、模板填充、异步导出下载中心、去重增量更新、敏感数据脱敏、多文件合并、Excel/CSV 双向转换。每个场景从场景分析、需求分析、方案设计、代码实现、注意事项五个角度展开，提供完整可编译的最小使用案例，遵循官方与社区最佳实践。
---

## 为什么需要这篇文档？

前两篇文档分别讲解了 Fesod 的核心 API 和 Spring Boot 集成方式。但在实际项目中，需求往往不是简单的「读一个文件」或「写一个文件」——你需要处理校验、筛选、分页、样式、模板、异步、脱敏等复杂场景。

本文从 **12 个企业级高频场景** 出发，每个场景提供：

- **场景分析**：什么业务需要这个能力
- **需求分析**：输入/输出/约束条件
- **方案设计**：技术选型与核心 API 选择
- **代码实现**：完整可编译的最小案例
- **注意事项**：坑点与最佳实践

> ### 💡 新人小结：这篇文档像什么？
>
> 如果说前两篇是**叉车操作手册**（认识按钮、学会推拉），这篇就是**仓库实战攻略**——12 个真实任务，每个任务告诉你：货物从哪来、要搬到哪去、遇到特殊情况怎么处理。
>
> 一句话总结：**前两篇学工具，这篇用工具解决真实问题。**

**学习路线图**

```
场景 01  批量导入校验     逐行校验 + 错误报告     导入基本功
   ↓
场景 02  条件筛选导出     动态查询 + 导出         最常见的导出需求
   ↓
场景 03  百万级流式导出   游标查询 + 分批写入     大数据量不 OOM
   ↓
场景 04  动态列导出       用户选择列 + 按需生成   灵活报表
   ↓
场景 05  按维度分 Sheet   数据分组 + 多 Sheet     结构化报表
   ↓
场景 06  样式报表导出     表头样式 + 合并单元格   正式报表格式
   ↓
场景 07  模板填充导出     占位符 + 数据填充       复杂格式报表
   ↓
场景 08  异步导出         任务队列 + 轮询下载     大数据量不超时
   ↓
场景 09  去重增量更新     upsert + 唯一键         重复导入不怕
   ↓
场景 10  敏感数据脱敏     自定义 Converter        安全合规
   ↓
场景 11  多文件合并       遍历读取 + 统一写入     汇总报表
   ↓
场景 12  Excel/CSV 转换   双向格式转换            系统对接
```

---

## 专有名词表

| 术语 | 全称 | 含义（通俗版） | 在本文中的角色 |
|------|------|----------------|---------------|
| DTO | Data Transfer Object | 数据传输对象，用于层间传递参数 | 封装导出查询条件 |
| upsert | update + insert | 存在则更新、不存在则新增 | 导入去重的核心操作 |
| BOM | Byte Order Mark | UTF-8 编码标识字节（EF BB BF） | CSV 中文不乱码 |
| SXSS | Streaming XML SpreadSheet | POI 的流式写入工作簿 | 大文件导出的底层支撑 |
| Cursor | 数据库游标 | 逐行读取结果集的数据库机制 | 百万级数据不一次性加载 |
| ResultHandler | MyBatis 结果处理器 | 每读到一行结果就回调一次 | 配合游标实现流式查询 |
| WriteHandler | Fesod 写入处理器 | 在写入过程中拦截并修改行为 | 合并单元格、自定义样式 |
| LoopMergeStrategy | 循环合并策略 | 按固定行数合并单元格的内置策略 | 报表中的行合并 |
| FillConfig | 填充配置 | 模板填充时的配置对象 | 控制列表填充行为 |

---

## 场景 01：员工批量导入（含逐行校验与错误报告）

### 场景分析

HR 部门上传一份员工 Excel 花名册，后端需要逐行解析并入库。但 Excel 数据质量参差不齐——有人漏填姓名、有人把工号写成文字、有人日期格式不对。如果因为一行数据有问题就整体失败，用户体验极差。

### 需求分析

- **输入**：MultipartFile（.xlsx）
- **输出**：`{successCount, errorCount, errors: [{row, message}]}`
- **约束**：单行错误不中断整体导入；空行跳过；类型转换异常要捕获并记录行号

### 方案设计

```
上传文件 → MultipartFile.getInputStream()
→ FesodSheet.read() + 自定义 ImportListener
→ invoke() 逐行校验（必填/格式/范围）
→ onException() 捕获转换异常，记录行号
→ doAfterAllAnalysed() 批量入库 + 返回结果
```

核心选择：自定义 `ReadListener` 而非 `PageReadListener`，因为需要逐行校验并收集错误信息。

### 代码实现

```java
import org.apache.fesod.sheet.context.AnalysisContext;
import org.apache.fesod.sheet.exception.ExcelDataConvertException;
import org.apache.fesod.sheet.read.listener.ReadListener;

public class EmployeeImportListener implements ReadListener<Employee> {

    private final List<Employee> successList = new ArrayList<>();
    private final List<Map<String, Object>> errorList = new ArrayList<>();

    @Override
    public void invoke(Employee data, AnalysisContext context) {
        int rowIndex = context.readRowHolder().getRowIndex();
        // 跳过空行
        if (data.getEmpName() == null && data.getEmpNo() == null) {
            return;
        }
        // 业务校验
        if (data.getEmpName() == null || data.getEmpName().trim().isEmpty()) {
            addError(rowIndex, "姓名为空");
            return;
        }
        if (data.getEmpAge() != null && (data.getEmpAge() < 18 || data.getEmpAge() > 65)) {
            addError(rowIndex, "年龄超出范围(18-65): " + data.getEmpAge());
            return;
        }
        successList.add(data);
    }

    @Override
    public void doAfterAllAnalysed(AnalysisContext context) {
        // 读取完成后批量入库
        if (!successList.isEmpty()) {
            employeeService.batchInsert(successList);
        }
    }

    @Override
    public void onException(Exception exception, AnalysisContext context) {
        int rowIndex = context.readRowHolder().getRowIndex();
        if (exception instanceof ExcelDataConvertException) {
            ExcelDataConvertException ex = (ExcelDataConvertException) exception;
            addError(rowIndex, "第" + ex.getColumnIndex() + "列类型转换失败: " + ex.getCellData());
        } else {
            addError(rowIndex, "读取异常: " + exception.getMessage());
        }
        // 不抛异常 → 跳过错误行，继续读取
    }

    private void addError(int rowIndex, String message) {
        Map<String, Object> error = new HashMap<>();
        error.put("row", rowIndex + 1);  // 展示给用户时从 1 开始
        error.put("message", message);
        errorList.add(error);
    }

    public int getSuccessCount() { return successList.size(); }
    public List<Map<String, Object>> getErrorList() { return errorList; }
}
```

Controller 层：

```java
@PostMapping("/import")
public ResponseEntity<Map<String, Object>> importEmployees(
        @RequestParam("file") MultipartFile file) throws Exception {
    EmployeeImportListener listener = new EmployeeImportListener();
    FesodSheet.read(file.getInputStream(), Employee.class, listener)
        .sheet().doRead();

    Map<String, Object> result = new HashMap<>();
    result.put("successCount", listener.getSuccessCount());
    result.put("errorCount", listener.getErrorList().size());
    result.put("errors", listener.getErrorList());
    return ResponseEntity.ok(result);
}
```

### 注意事项

- `onException` 中**不要抛出异常**，否则后续行全部跳过
- 空行判断要同时检查多个关键字段为 null，不能只判一个
- 批量入库放在 `doAfterAllAnalysed` 中，确保读取完成后再入库
- 如果数据量很大（>1 万行），`successList` 本身也会占内存，可改为分批入库

---

## 场景 02：条件筛选导出（日期范围 + 部门 + 关键词）

### 场景分析

管理后台的员工列表页面，用户可以按日期范围、部门、关键词筛选后点击「导出」——这是企业项目中最常见的导出需求。

### 需求分析

- **输入**：ExportQueryDTO（startDate / endDate / department / keyword）
- **输出**：按条件筛选后的 Excel 文件下载
- **约束**：条件可选（为空则不过滤）；数据量大时走流式

### 方案设计

```
前端传参 → ExportQueryDTO
→ Service 构建动态查询条件（MyBatis QueryWrapper）
→ 查询数据 → FesodSheet.write(response.getOutputStream())
→ 设置响应头 → 下载
```

### 代码实现

DTO：

```java
@Data
public class EmployeeExportQuery {
    private LocalDate startDate;
    private LocalDate endDate;
    private String department;
    private String keyword;
}
```

Service：

```java
public List<Employee> queryByCondition(EmployeeExportQuery query) {
    LambdaQueryWrapper<Employee> wrapper = new LambdaQueryWrapper<>();
    if (query.getStartDate() != null) {
        wrapper.ge(Employee::getCreateTime, query.getStartDate());
    }
    if (query.getEndDate() != null) {
        wrapper.le(Employee::getCreateTime, query.getEndDate());
    }
    if (query.getDepartment() != null && !query.getDepartment().isEmpty()) {
        wrapper.eq(Employee::getDepartment, query.getDepartment());
    }
    if (query.getKeyword() != null && !query.getKeyword().trim().isEmpty()) {
        wrapper.like(Employee::getEmpName, query.getKeyword().trim());
    }
    return employeeMapper.selectList(wrapper);
}
```

Controller：

```java
@PostMapping("/export")
public void exportByCondition(@RequestBody EmployeeExportQuery query,
        HttpServletResponse response) throws Exception {
    List<Employee> dataList = employeeService.queryByCondition(query);

    String fileName = URLEncoder.encode("员工列表_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .sheet("员工列表").doWrite(dataList);
}
```

### 注意事项

- 导出接口建议用 `@PostMapping`（查询条件可能很复杂，GET 参数长度有限制）
- 数据量超过 5 万行时，应改用场景 03 的流式导出方案
- `like` 查询注意 SQL 注入——MyBatis 的 `like` 方法已自动处理参数化

---

## 场景 03：百万级数据流式导出（游标查询 + 分批写入）

### 场景分析

运营需要导出全量交易记录（100 万+行）。如果用 `selectList()` 一次性查出再 `doWrite()`，内存中同时存在百万级 Java 对象 + POI Workbook，直接 OOM。

### 需求分析

- **输入**：无筛选条件（全量导出）
- **输出**：100 万+ 行的 Excel 文件
- **约束**：内存占用不超过 500MB；不能超时

### 方案设计

```
MyBatis Cursor 游标查询（逐行从数据库读取）
→ 攒够一批（5000 条）→ ExcelWriter.write(batch, sheet)
→ 继续游标 → 再攒一批 → 再写入
→ 游标结束 → writer.finish()
```

核心选择：MyBatis `Cursor` 而非 `LIMIT/OFFSET` 分页——游标在数据库侧保持连接逐行返回，不需要每次重新查询，性能远优于深度分页。

### 代码实现

Mapper 接口：

```java
@Mapper
public interface TransactionMapper {
    @Select("SELECT * FROM t_transaction ORDER BY id")
    @Options(fetchSize = Integer.MIN_VALUE)  // MySQL 流式读取必须设置
    Cursor<Transaction> cursorAll();
}
```

Service：

```java
public void exportAll(OutputStream outputStream) throws Exception {
    try (ExcelWriter writer = FesodSheet.write(outputStream, Transaction.class).build()) {
        WriteSheet sheet = FesodSheet.writerSheet(0, "全量交易").build();

        List<Transaction> batch = new ArrayList<>(5000);
        try (Cursor<Transaction> cursor = transactionMapper.cursorAll()) {
            for (Transaction row : cursor) {
                batch.add(row);
                if (batch.size() >= 5000) {
                    writer.write(batch, sheet);
                    batch.clear();  // 清空让 GC 回收
                }
            }
        }
        // 写入最后一批
        if (!batch.isEmpty()) {
            writer.write(batch, sheet);
        }
    }
}
```

### 注意事项

- MySQL 的 `fetchSize = Integer.MIN_VALUE` 是触发流式读取的特殊标记，不是真的负数
- 游标查询期间数据库连接一直被占用，需要确保连接池足够大、事务超时足够长
- 如果数据库不支持游标（如某些旧版本），退而求其次用 `LIMIT/OFFSET` 分页
- Excel 单 Sheet 最大行数为 1,048,576——超过需要分 Sheet

---

## 场景 04：动态列导出（用户选择导出列）

### 场景分析

员工列表有 20 个字段，但不同部门关心的信息不同——HR 要全部，财务只要工号/姓名/工资，行政只要姓名/部门/工位。让每个部门用不同的导出接口不现实，需要一个「勾选列再导出」的功能。

### 需求分析

- **输入**：`List<String> includeFields`（用户勾选的字段名列表）
- **输出**：只包含勾选列的 Excel
- **约束**：至少保留一列；字段名必须与实体类属性名匹配

### 方案设计

```
前端勾选字段 → 传入 includeFields
→ 计算 excludedFields = 全部字段 - includeFields
→ FesodSheet.write().excludeColumnFieldNames(excludedFields)
→ 只输出勾选的列
```

### 代码实现

```java
// 实体类全部字段
@Data
public class Employee {
    @ExcelProperty("编号")   private Long empNo;
    @ExcelProperty("姓名")   private String empName;
    @ExcelProperty("年龄")   private Integer empAge;
    @ExcelProperty("部门")   private String department;
    @ExcelProperty("工资")   private BigDecimal empSalary;
    @ExcelProperty("手机")   private String phone;
    @ExcelProperty("邮箱")   private String email;
    // ... 更多字段
}

@PostMapping("/export-selected")
public void exportSelectedColumns(
        @RequestBody Map<String, List<String>> request,
        HttpServletResponse response) throws Exception {

    List<String> includeFields = request.get("includeFields");
    // 所有可导出字段
    Set<String> allFields = new LinkedHashSet<>(Arrays.asList(
        "empNo", "empName", "empAge", "department", "empSalary", "phone", "email"));

    // 计算需要排除的字段
    Set<String> excludedFields = new LinkedHashSet<>(allFields);
    if (includeFields != null && !includeFields.isEmpty()) {
        excludedFields.removeAll(new HashSet<>(includeFields));
    }
    // 至少保留一列
    if (excludedFields.size() == allFields.size()) {
        excludedFields.remove("empNo");  // 保底保留编号列
    }

    List<Employee> dataList = employeeService.findAll();
    String fileName = URLEncoder.encode("员工数据_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .excludeColumnFieldNames(excludedFields)
        .sheet("员工数据").doWrite(dataList);
}
```

### 注意事项

- `excludeColumnFieldNames` 接收的是 Java 属性名（不是 Excel 列名）
- 被 `@ExcelIgnore` 标注的字段始终不导出，不受动态列影响
- 列的顺序由实体类字段声明顺序决定，不是 `includeFields` 的传入顺序

---

## 场景 05：按业务维度分 Sheet 导出（部门/区域/月份）

### 场景分析

年度汇报需要一份 Excel，里面按部门拆分为多个 Sheet：「技术部」「市场部」「财务部」各一个 Sheet，方便各部门独立查看。

### 需求分析

- **输入**：全量数据（含部门字段）
- **输出**：一份 Excel，每个部门一个 Sheet
- **约束**：Sheet 名称不能含特殊字符；空部门归入「未分配」Sheet

### 方案设计

```
查询全量数据 → Collectors.groupingBy(department) 按部门分组
→ ExcelWriter 创建多个 WriteSheet
→ 遍历 Map，每个部门 write 到对应 Sheet
```

### 代码实现

```java
@GetMapping("/export-by-department")
public void exportByDepartment(HttpServletResponse response) throws Exception {
    List<Employee> allData = employeeService.findAll();

    // 按部门分组
    Map<String, List<Employee>> grouped = allData.stream()
        .collect(Collectors.groupingBy(
            e -> e.getDepartment() != null ? e.getDepartment() : "未分配",
            LinkedHashMap::new, Collectors.toList()));

    String fileName = URLEncoder.encode("部门汇总_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    try (ExcelWriter writer = FesodSheet.write(response.getOutputStream(), Employee.class).build()) {
        int sheetIndex = 0;
        for (Map.Entry<String, List<Employee>> entry : grouped.entrySet()) {
            // 清理 Sheet 名称中的非法字符
            String sheetName = sanitizeSheetName(entry.getKey());
            WriteSheet sheet = FesodSheet.writerSheet(sheetIndex++, sheetName).build();
            writer.write(entry.getValue(), sheet);
        }
    }
}

private String sanitizeSheetName(String name) {
    // Excel Sheet 名称不能包含 : \ / ? * [ ]
    return name.replaceAll("[:\\\\/?*\\[\\]]", "_");
}
```

### 注意事项

- Excel Sheet 名称不能包含 `:` `\` `/` `?` `*` `[` `]`，且长度不超过 31 字符
- 如果部门数量很多（>50），考虑合并小部门或只保留 Top N
- `LinkedHashMap` 保证 Sheet 顺序与数据出现顺序一致

---

## 场景 06：带样式表头与合并标题行的报表导出

### 场景分析

给领导看的正式报表，要求表头有背景色、加粗字体、边框；某些列需要合并（比如同一部门的多行数据，部门列合并为一个单元格）。

### 需求分析

- **输入**：数据列表
- **输出**：带样式的 Excel（表头背景色 + 字体加粗 + 指定列合并）
- **约束**：样式通过注解声明（非代码手动设置）

### 方案设计

```
实体类字段加 @HeadStyle / @HeadFontStyle / @ContentStyle 注解
→ FesodSheet.write() 时注册 MergeStrategy
→ 自动应用样式和合并
```

### 代码实现

实体类（样式注解）：

```java
import org.apache.fesod.sheet.annotation.write.style.*;
import org.apache.poi.ss.usermodel.FillPatternType;
import org.apache.poi.ss.usermodel.BorderStyle;
import org.apache.poi.ss.usermodel.IndexedColors;

@Data
public class ReportData {

    @ExcelProperty("部门")
    @ColumnWidth(15)
    @HeadStyle(fillPatternType = FillPatternType.SOLID_FOREGROUND,
               fillForegroundColor = IndexedColors.LIGHT_BLUE)
    @HeadFontStyle(bold = true, fontName = "微软雅黑", fontHeightInPoints = 12)
    @ContentStyle(horizontalAlignment = HorizontalAlignmentEnum.CENTER)
    private String department;

    @ExcelProperty("姓名")
    @ColumnWidth(12)
    @HeadStyle(fillPatternType = FillPatternType.SOLID_FOREGROUND,
               fillForegroundColor = IndexedColors.LIGHT_BLUE)
    @HeadFontStyle(bold = true, fontName = "微软雅黑")
    private String empName;

    @ExcelProperty("工资")
    @ColumnWidth(15)
    @ContentStyle(dataFormat = 4)  // #,##0 千分位格式
    private BigDecimal empSalary;
}
```

Controller（注册合并策略）：

```java
@GetMapping("/export-report")
public void exportReport(HttpServletResponse response) throws Exception {
    List<ReportData> dataList = reportService.getReportData();

    String fileName = URLEncoder.encode("部门报表_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    FesodSheet.write(response.getOutputStream(), ReportData.class)
        .registerWriteHandler(new LoopMergeStrategy(2, 0))
        // LoopMergeStrategy(每N行合并, 第几列) → 部门列每2行合并一次
        .sheet("部门报表").doWrite(dataList);
}
```

### 注意事项

- 样式注解在 `org.apache.fesod.sheet.annotation.write.style` 包下
- `LoopMergeStrategy(int eachRow, int columnIndex)`：从第 2 行数据开始，每 `eachRow` 行合并第 `columnIndex` 列
- `@ContentStyle(dataFormat = 4)` 中的数字是 POI 内置格式编号（4 = `#,##0`）
- 合并策略只影响数据行，不影响表头行

---

## 场景 07：基于模板的 Excel 填充导出

### 场景分析

财务部门提供了一份格式复杂的 Excel 模板（含公司 Logo、固定表头、合计行公式），只需要在指定位置填入数据。如果用代码从头创建这种格式，工作量巨大——而模板填充只需在模板中放好占位符，后端把数据灌进去。

### 需求分析

- **输入**：模板文件（classpath 下）+ 填充数据（单个对象或列表）
- **输出**：填充完成的 Excel 文件下载
- **约束**：模板中的公式、样式、Logo 必须保留

### 方案设计

```
模板文件放在 classpath:templates/ 下
→ 模板中用 {.name} {.age} 标记占位符
→ FesodSheet.write(output).withTemplate(templatePath).fill(data)
→ 模板格式完整保留，数据自动填充
```

### 代码实现

模板文件 `templates/salary_report.xlsx` 中的占位符格式：

```
A1: 员工薪资报表
A3: {.empName}    B3: {.department}    C3: {.empSalary}
```

Service：

```java
@Service
public class ReportFillService {

    public void fillSingleReport(OutputStream outputStream) throws Exception {
        String templatePath = "templates/salary_report.xlsx";

        Map<String, Object> data = new HashMap<>();
        data.put("empName", "张三");
        data.put("department", "技术部");
        data.put("empSalary", 15000.00);

        FesodSheet.write(outputStream)
            .withTemplate(templatePath)
            .fill(data);
    }

    public void fillListReport(OutputStream outputStream) throws Exception {
        String templatePath = "templates/salary_list_template.xlsx";
        List<Employee> employees = employeeService.findAll();

        FesodSheet.write(outputStream)
            .withTemplate(templatePath)
            .fill(FillWrapper.create("employees", employees),
                  FillConfig.builder().forceNewRowStrategyForList(true).build());
    }
}
```

Controller：

```java
@GetMapping("/export-template")
public void exportFromTemplate(HttpServletResponse response) throws Exception {
    String fileName = URLEncoder.encode("薪资报表_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");
    reportFillService.fillSingleReport(response.getOutputStream());
}
```

### 注意事项

- 模板文件放在 `src/main/resources/templates/` 下，打包后通过 classpath 读取
- 占位符格式 `{.fieldName}` 中 `fieldName` 对应 Map 的 key 或对象的属性名
- 列表填充时 `FillConfig.forceNewRowStrategyForList(true)` 会自动插入新行
- 模板中的 Excel 公式（如 SUM）在填充后仍然保留，打开文件时会自动重算

---

## 场景 08：异步导出与下载中心

### 场景分析

导出 50 万行数据可能需要 30 秒以上——HTTP 请求早就超时了。用户不能一直等着，需要一个「提交导出任务 → 后台异步生成 → 完成后通知下载」的机制。

### 需求分析

- **输入**：导出条件
- **输出**：任务 ID → 轮询状态 → 下载文件
- **约束**：异步线程中无法获取 HttpServletResponse；需要文件存储和清理策略

### 方案设计

```
用户点击导出 → POST /export/async → 创建 ExportTask（PENDING）
→ @Async 异步：查询数据 → 写文件到磁盘 → 更新状态=DONE
→ 轮询 GET /export/status/{taskId} → 返回状态和下载链接
→ 下载 GET /export/download/{taskId} → 返回文件流
```

### 代码实现

任务实体：

```java
@Data
@TableName("t_export_task")
public class ExportTask {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String fileName;
    private String filePath;
    private String status;        // PENDING / PROCESSING / DONE / FAILED
    private String errorMessage;
    private LocalDateTime createTime;
}
```

异步 Service：

```java
@Service
public class AsyncExportService {

    @Autowired
    private ExportTaskMapper exportTaskMapper;

    @Async("exportExecutor")
    public void asyncExport(ExportTask task, EmployeeExportQuery query) {
        try {
            exportTaskMapper.updateStatus(task.getId(), "PROCESSING");
            List<Employee> dataList = employeeService.queryByCondition(query);

            String filePath = "/data/exports/" + task.getId() + ".xlsx";
            FesodSheet.write(filePath, Employee.class)
                .sheet("员工数据").doWrite(dataList);

            task.setFilePath(filePath);
            task.setStatus("DONE");
            exportTaskMapper.updateById(task);
        } catch (Exception e) {
            task.setStatus("FAILED");
            task.setErrorMessage(e.getMessage());
            exportTaskMapper.updateById(task);
        }
    }
}
```

Controller（三个接口）：

```java
@RestController
@RequestMapping("/export")
public class ExportController {

    @PostMapping("/async")
    public ResponseEntity<Long> submitExportTask(@RequestBody EmployeeExportQuery query) {
        ExportTask task = new ExportTask();
        task.setFileName("员工数据_" + System.currentTimeMillis());
        task.setStatus("PENDING");
        task.setCreateTime(LocalDateTime.now());
        exportTaskMapper.insert(task);
        asyncExportService.asyncExport(task, query);
        return ResponseEntity.ok(task.getId());
    }

    @GetMapping("/status/{taskId}")
    public ResponseEntity<Map<String, Object>> getTaskStatus(@PathVariable Long taskId) {
        ExportTask task = exportTaskMapper.selectById(taskId);
        Map<String, Object> result = new HashMap<>();
        result.put("id", task.getId());
        result.put("status", task.getStatus());
        if ("DONE".equals(task.getStatus())) {
            result.put("downloadUrl", "/export/download/" + taskId);
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/download/{taskId}")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long taskId) throws Exception {
        ExportTask task = exportTaskMapper.selectById(taskId);
        Resource resource = new UrlResource(Paths.get(task.getFilePath()).toUri());
        return ResponseEntity.ok()
            .header("Content-disposition", "attachment;filename=\"" + task.getFileName() + ".xlsx\"")
            .body(resource);
    }
}
```

### 注意事项

- `@Async` 方法必须在**不同的 Bean** 中调用（Spring AOP 代理限制）
- 异步线程中**没有** HttpServletResponse，所以只能写文件到磁盘
- 需要配置定时任务清理过期的导出文件（如保留 7 天）
- 线程池要独立配置（`exportExecutor`），避免与业务线程池互相影响

---

## 场景 09：导入数据去重与增量更新（upsert）

### 场景分析

每月 HR 都会上传最新的员工花名册。有些员工是新增的，有些是信息变更（调薪、调岗），有些没变。需要一个智能导入：新来的插入，已有的更新，不要重复插入。

### 需求分析

- **输入**：Excel 文件（含工号作为唯一标识）
- **输出**：`{inserted: N, updated: N}`
- **约束**：按工号判断新旧；批量操作保证性能

### 方案设计

```
读取 Excel → 按批次收集（每 500 条一批）
→ 查询数据库中已存在的工号集合
→ 分流：已存在 → updateList / 不存在 → insertList
→ 分别批量 INSERT 和 UPDATE
```

### 代码实现

```java
public class UpsertImportListener implements ReadListener<Employee> {

    private final List<Employee> batch = new ArrayList<>(500);
    private final EmployeeMapper employeeMapper;
    private int inserted = 0, updated = 0;

    public UpsertImportListener(EmployeeMapper employeeMapper) {
        this.employeeMapper = employeeMapper;
    }

    @Override
    public void invoke(Employee data, AnalysisContext context) {
        batch.add(data);
        if (batch.size() >= 500) {
            processBatch();
            batch.clear();
        }
    }

    @Override
    public void doAfterAllAnalysed(AnalysisContext context) {
        if (!batch.isEmpty()) { processBatch(); }
    }

    private void processBatch() {
        List<Long> empNos = batch.stream()
            .map(Employee::getEmpNo).collect(Collectors.toList());
        Set<Long> existingNos = new HashSet<>(
            employeeMapper.selectEmpNosByNos(empNos));

        List<Employee> insertList = new ArrayList<>();
        List<Employee> updateList = new ArrayList<>();
        for (Employee emp : batch) {
            if (existingNos.contains(emp.getEmpNo())) {
                updateList.add(emp);
            } else {
                insertList.add(emp);
            }
        }
        if (!insertList.isEmpty()) {
            employeeMapper.batchInsert(insertList);
            inserted += insertList.size();
        }
        if (!updateList.isEmpty()) {
            employeeMapper.batchUpdate(updateList);
            updated += updateList.size();
        }
    }

    public int getInserted() { return inserted; }
    public int getUpdated() { return updated; }
}
```

### 注意事项

- 工号字段必须有**唯一索引**，否则 upsert 语义无法保证
- 分批处理（每 500 条一批）避免 IN 子句过长
- Listener 不是 Spring Bean，`@Transactional` 不生效——需要手动管理事务

---

## 场景 10：敏感数据脱敏导出（手机号/身份证/银行卡）

### 场景分析

导出员工信息给第三方合作机构时，手机号、身份证号不能明文暴露——需要自动脱敏（`138****1234`、`110***********1234`）。

### 需求分析

- **输入**：含敏感字段的实体类
- **输出**：导出时敏感字段自动脱敏的 Excel
- **约束**：脱敏规则可复用；导入时不脱敏

### 方案设计

```
自定义 Converter 实现脱敏逻辑
→ 实体类敏感字段标注 converter = PhoneMaskConverter.class
→ 导出时 Fesod 自动调用 convertToExcelData 转换
```

### 代码实现

```java
public class PhoneMaskConverter implements Converter<String> {

    @Override
    public String convertToJavaData(ReadConverterContext<?> context) {
        return context.getReadCellData().getStringValue();  // 导入时不脱敏
    }

    @Override
    public WriteCellData<?> convertToExcelData(WriteConverterContext<String> context) {
        String phone = context.getValue();
        if (phone == null || phone.length() < 7) return new WriteCellData<>(phone);
        String masked = phone.substring(0, 3) + "****" + phone.substring(phone.length() - 4);
        return new WriteCellData<>(masked);
    }
}

public class IdCardMaskConverter implements Converter<String> {

    @Override
    public String convertToJavaData(ReadConverterContext<?> context) {
        return context.getReadCellData().getStringValue();
    }

    @Override
    public WriteCellData<?> convertToExcelData(WriteConverterContext<String> context) {
        String idCard = context.getValue();
        if (idCard == null || idCard.length() < 8) return new WriteCellData<>(idCard);
        String masked = idCard.substring(0, 3) + "***********" + idCard.substring(idCard.length() - 4);
        return new WriteCellData<>(masked);
    }
}
```

实体类使用：

```java
@Data
public class EmployeeExportVO {
    @ExcelProperty("编号")   private Long empNo;
    @ExcelProperty("姓名")   private String empName;

    @ExcelProperty(value = "手机号", converter = PhoneMaskConverter.class)
    private String phone;

    @ExcelProperty(value = "身份证号", converter = IdCardMaskConverter.class)
    private String idCard;
}
```

### 注意事项

- 脱敏 Converter 只在**导出**时生效，导入时原样读取
- 建议为导出单独创建 VO 类，不要修改原始实体类
- 如果脱敏规则需要动态配置，可以通过 `ThreadLocal` 传递脱敏开关

---

## 场景 11：多 Excel 文件合并

### 场景分析

5 个分公司各自上报员工花名册 Excel，总部需要合并为一份汇总文件。手动复制粘贴太慢，需要一个接口上传多个文件后自动合并。

### 需求分析

- **输入**：多个 MultipartFile（.xlsx）
- **输出**：合并后的一份 Excel
- **约束**：各文件表头格式一致；跳过每个文件的表头行

### 方案设计

```
上传多个文件 → List<MultipartFile>
→ 遍历每个文件 FesodSheet.read() 收集数据
→ 一个 ExcelWriter 统一写入同一个 Sheet
```

### 代码实现

```java
@PostMapping("/merge")
public void mergeExcelFiles(
        @RequestParam("files") List<MultipartFile> files,
        HttpServletResponse response) throws Exception {

    if (files == null || files.isEmpty()) {
        throw new IllegalArgumentException("请上传至少一个文件");
    }

    List<Employee> mergedData = new ArrayList<>();
    for (MultipartFile file : files) {
        if (file.isEmpty()) continue;
        List<Employee> fileData = new ArrayList<>();
        FesodSheet.read(file.getInputStream(), Employee.class,
            new PageReadListener<Employee>(fileData::addAll))
            .sheet().headRowNumber(1).doRead();
        mergedData.addAll(fileData);
    }

    String fileName = URLEncoder.encode("合并汇总_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .sheet("汇总数据").doWrite(mergedData);
}
```

### 注意事项

- 各文件的表头格式必须一致——否则列错位
- `headRowNumber(1)` 确保表头行不被当数据读入
- 文件数量建议限制（如最多 50 个），避免内存压力
- 如需标注数据来源，可在 Employee 中增加 `sourceFile` 字段

---

## 场景 12：Excel 与 CSV 双向转换

### 场景分析

内部系统用 Excel 格式，但对接的外部系统只接受 CSV。反过来，外部推送的 CSV 数据需要转成 Excel 给业务人员查看。Fesod 同时支持 Excel 和 CSV 的读写，可以无缝转换。

### 需求分析

- **场景 A**：Excel → CSV（给外部系统）
- **场景 B**：CSV → Excel（给业务人员）
- **约束**：中文不乱码（BOM 头）；日期格式保持一致

### 方案设计

```
场景 A：FesodSheet.read(xlsx).sheet().doRead()
       → FesodSheet.write(csv).csv().doWrite()

场景 B：FesodSheet.read(csv).csv().doRead()
       → FesodSheet.write(xlsx).sheet().doWrite()
```

### 代码实现

Excel 转 CSV：

```java
@PostMapping("/convert/excel-to-csv")
public void excelToCsv(@RequestParam("file") MultipartFile file,
        HttpServletResponse response) throws Exception {

    List<Employee> dataList = new ArrayList<>();
    FesodSheet.read(file.getInputStream(), Employee.class,
        new PageReadListener<Employee>(dataList::addAll))
        .sheet().doRead();

    String fileName = URLEncoder.encode("转换结果_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("text/csv; charset=utf-8");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".csv");

    // BOM 头：确保 Excel 打开 CSV 时中文不乱码
    response.getOutputStream().write(new byte[]{(byte) 0xEF, (byte) 0xBB, (byte) 0xBF});

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .csv().nullString("N/A").doWrite(dataList);
}
```

CSV 转 Excel：

```java
@PostMapping("/convert/csv-to-excel")
public void csvToExcel(@RequestParam("file") MultipartFile file,
        HttpServletResponse response) throws Exception {

    List<Employee> dataList = new ArrayList<>();
    FesodSheet.read(file.getInputStream(), Employee.class,
        new PageReadListener<Employee>(dataList::addAll))
        .csv().delimiter(',').doRead();

    String fileName = URLEncoder.encode("转换结果_" + System.currentTimeMillis(), "UTF-8")
        .replaceAll("\\+", "%20");
    response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

    FesodSheet.write(response.getOutputStream(), Employee.class)
        .sheet("转换数据").doWrite(dataList);
}
```

### 注意事项

- CSV 导出时**必须写 BOM 头**（`EF BB BF`），否则 Windows Excel 打开中文乱码
- CSV 中的日期会转为字符串格式，不会保留 Excel 的日期类型
- CSV 字段中包含逗号或换行符时，Fesod 自动用双引号包裹（RFC 4180）
- 读取 GBK 编码的 CSV 需要先转码为 UTF-8

---

## 综合常见问题排查表

| 问题 | 涉及场景 | 原因分析 | 解决方案 |
|------|---------|---------|----------|
| **导入后数据为空** | 01, 09 | Excel 表头与 `@ExcelProperty` 注解值不一致 | 逐字比对表头和注解值；或用 `index` 按列索引匹配 |
| **导出文件名乱码** | 02-08, 11, 12 | URLEncoder 把空格编码为 `+` | `.replaceAll("\\+", "%20")` + `filename*=utf-8''` |
| **大数据导出 OOM** | 03, 08 | 用 `doWrite()` 一次性写入全部数据 | 用 `ExcelWriter` + 分批 `write()` + 游标/分页查询 |
| **Sheet 名称报错** | 05 | Sheet 名包含 `:` `/` `?` `*` 等非法字符 | 用 `sanitizeSheetName()` 替换非法字符 |
| **模板填充数据为空** | 07 | 占位符 `{.name}` 与 Map key 不匹配 | 检查占位符拼写与 Map key 完全一致 |
| **异步导出文件找不到** | 08 | 异步线程写文件时目录不存在 | 提前创建 `/data/exports/` 目录 |
| **CSV 打开中文乱码** | 12 | 缺少 UTF-8 BOM 头 | 写入前先写 `EF BB BF` 三字节 |
| **合并文件列错位** | 11 | 各文件表头格式不一致 | 导入前校验表头一致性；统一模板格式 |
| **脱敏 Converter 导入时也脱敏** | 10 | `convertToJavaData` 也做了脱敏 | 导入方法直接返回原值，只在 `convertToExcelData` 中脱敏 |
| **动态列导出全部列都没了** | 04 | `excludeColumnFieldNames` 传入了全部字段 | 确保至少保留一个字段；做保底逻辑 |

---

## Q&A / 踩坑

**Q1：12 个场景的代码能直接复制到项目中使用吗？**

代码基于 Fesod 2.0.2-incubating + Spring Boot + MyBatis-Plus 上下文编写，核心 API 调用均经过官方文档核实。但实际使用时需要根据项目调整：数据库表结构、Mapper 接口、Service 注入方式等。代码中的 import 语句已省略以节省篇幅，实际使用时 IDE 会自动补全。

**Q2：场景 03 的游标查询和分页查询怎么选？**

| 维度 | 游标查询（Cursor） | 分页查询（LIMIT/OFFSET） |
|------|-------------------|------------------------|
| 性能 | 数据库保持连接，逐行返回，无重复扫描 | 深度分页时 OFFSET 越大越慢 |
| 连接占用 | 长时间占用一个连接 | 每次查询独立，连接用完即释放 |
| 适用场景 | 数据量大（>10 万）、一次性导出 | 数据量适中、连接池紧张 |
| 事务要求 | 需要在事务内保持游标 | 无事务要求 |

**Q3：场景 08 的异步导出，文件存在服务器磁盘上安全吗？**

生产环境建议将导出文件存储在 OSS / MinIO 等对象存储中，避免服务器磁盘空间不足或服务器重启丢失。可以将 `filePath` 改为对象存储的 URL。

**Q4：场景 09 的 upsert，如果数据量很大怎么办？**

如果导入数据超过 10 万行，`selectEmpNosByNos()` 的 IN 子句可能过长。解决方案：
1. 分批查询（每 1000 个工号查一次）
2. 或者用临时表方案：先把导入数据写入临时表，再用 `LEFT JOIN` 区分新旧

---

## 要点总结

1. **批量导入**：自定义 `ReadListener`，`invoke()` 校验 + `onException()` 容错 + `doAfterAllAnalysed()` 批量入库
2. **条件导出**：DTO 封装查询条件 + 动态 QueryWrapper + `FesodSheet.write()` 写入响应流
3. **百万级导出**：MyBatis Cursor 游标查询 + ExcelWriter 分批写入，内存恒定可控
4. **动态列**：`excludeColumnFieldNames()` 排除不需要的列，至少保留一列
5. **分 Sheet**：`Collectors.groupingBy()` 分组 + ExcelWriter 多 WriteSheet，注意 Sheet 名称合法性
6. **样式报表**：`@HeadStyle` / `@HeadFontStyle` 注解 + `LoopMergeStrategy` 合并策略
7. **模板填充**：`withTemplate()` + `FillWrapper` + `FillConfig.forceNewRowStrategyForList()`
8. **异步导出**：`@Async` 写文件到磁盘 + 任务状态表 + 轮询/下载接口 + 定时清理
9. **去重更新**：按唯一键分流 insert/update，分批处理控制内存
10. **数据脱敏**：自定义 `Converter` 只在 `convertToExcelData` 中脱敏，导入不脱敏
11. **多文件合并**：遍历 `MultipartFile` 列表读取 + 一个 ExcelWriter 统一写入
12. **格式转换**：Fesod 同时支持 Excel 和 CSV 读写，转换只需「读一种格式 → 写另一种格式」

---

> ### 💡 新人小结：12 个场景学完了，记住这张速查表
>
> | 需求关键词 | 对应场景 | 核心 API |
> |-----------|---------|----------|
> | 导入 + 校验 | 场景 01 | ReadListener + onException |
> | 筛选 + 导出 | 场景 02 | QueryWrapper + write |
> | 百万行 + 不 OOM | 场景 03 | Cursor + ExcelWriter 分批 |
> | 选择列 + 导出 | 场景 04 | excludeColumnFieldNames |
> | 分 Sheet | 场景 05 | groupingBy + 多 WriteSheet |
> | 样式 + 合并 | 场景 06 | @HeadStyle + LoopMergeStrategy |
> | 模板填充 | 场景 07 | withTemplate + fill |
> | 大数据 + 不超时 | 场景 08 | @Async + 文件存储 |
> | 去重 + 更新 | 场景 09 | upsert + 分批处理 |
> | 脱敏 | 场景 10 | 自定义 Converter |
> | 合并文件 | 场景 11 | 遍历 read + 统一 write |
> | 格式转换 | 场景 12 | read Excel + write CSV（反向同理） |
>
> 遇到新需求时，先在这张表里找最近的场景，然后组合使用——实际项目中的需求往往是这 12 个场景的排列组合。
