---
title: "mc rm"

weight: 340
---

<a id="mc-rm"></a>

<a id="command-mc.rm"></a>

## 语法 {#id2}

[`mc rm`](#command-mc.rm) 命令用于从 MinIO 部署的存储桶中 [删除对象](/docs/administration/object-management/object-delete/#minio-object-delete)。 如需彻底删除存储桶，请改用 [`mc rb`](/docs/reference/minio-mc/mc-rb/#command-mc.rb)。

你也可以对本地文件系统使用 [`mc rm`](#command-mc.rm)，以获得与 `rm` 命令行工具类似的结果。

有关 MinIO 如何对对象执行 `DELETE` 操作的更多信息，请参见 [对象删除](/docs/administration/object-management/object-delete/#minio-object-delete)。

> [!WARNING]
> **重要**
>
> [`mc rm`](#command-mc.rm) 支持在一条命令中删除多个对象 *或* 文件。 建议使用 [`--dry-run`](#mc.rm.-dry-run) 选项验证操作仅作用于预期的对象/文件。

{{< tabs group="tab1-tab2" >}}
{{< tab label="示例" value="tab1" >}}
以下命令从 `myminio` MinIO 部署的 `mydata` 存储桶中删除多个对象：

```shell
mc rm --recursive myminio/mydata
```
{{< /tab >}}
{{< tab label="语法" value="tab2" >}}
命令语法如下：

```shell
mc [GLOBALFLAGS] rm  \
                 [--bypass]               \
                 [--dangerous]            \
                 [--dry-run]              \
                 [--force]*               \
                 [--incomplete]           \
                 [--newer-than "string"]  \
                 [--non-current]          \
                 [--older-than "string"]  \
                 [--recursive]            \
                 [--rewind "string"]      \
                 [--stdin]                \
                 [--version-id "string"]* \
                 [--versions]             \
                 ALIAS [ALIAS ...]
```

- 方括号 `[]` 表示可选参数。
- 同一行中的参数彼此相互依赖。
- 使用管道符 `|` 分隔的参数彼此互斥。

请先将示例复制到文本编辑器中并按需修改，再在终端 / shell 中运行命令。

[`mc rm --force`](#mc.rm.-force) 是多个参数的必需项。 [`mc rm --version-id`](#mc.rm.-version-id) 与多个 参数互斥。更多信息请参见参考文档。
{{< /tab >}}
{{< /tabs >}}

### 参数 {#id3}

##### `ALIAS` {#mc.rm.ALIAS}

*mc-cmd*

*Required*

MinIO 部署的 [alias](/docs/reference/minio-mc/mc-alias-set/#alias)，以及要删除对象的完整路径。 例如：

```shell
mc rm play/mybucket/object.txt
```

你可以在同一个或不同的 MinIO 部署上指定多个对象。 例如：

```shell
mc rm play/mybucket/object.txt play/mybucket/otherobject.txt
```

如果指定的是存储桶或存储桶前缀路径，**必须** 同时 指定 [`--recursive`](#mc.rm.-recursive) 和 [`--force`](#mc.rm.-force) 参数。例如：

```shell
mc rm --recursive --force play/mybucket/

mc rm --recursive --force play/mybucket/myprefix/
```

建议先使用 [`--dry-run`](#mc.rm.-dry-run) 标志运行命令，验证 递归删除操作的范围。

若要从本地文件系统删除文件，请指定该文件的完整路径：

```shell
mc rm ~/data/myoldobject.txt
```

##### `--bypass` {#mc.rm.-bypass}

*mc-cmd*

*Optional*

允许删除受 [GOVERNANCE](/docs/administration/object-management/object-retention/#minio-object-locking-governance) 对象锁保护的对象。

##### `--dangerous` {#mc.rm.-dangerous}

*mc-cmd*

*Optional*

当 [`ALIAS`](#mc.rm.ALIAS) 指定 MinIO 部署的根路径（所有存储桶）时， 允许执行 [`mc rm`](#command-mc.rm)。

与 [`--versions`](#mc.rm.-versions) 结合使用时， 此标志会指示 [`mc rm`](#command-mc.rm) 永久删除 `ALIAS` 目标中的所有对象 *以及* 所有版本。

建议先使用 [`--dry-run`](#mc.rm.-dry-run) 运行命令， 验证站点范围删除操作的范围。

> [!CAUTION]
> **警告**
>
> 搭配 [`--versions`](#mc.rm.-versions) 标志运行 [`mc rm --dangerous`](#mc.rm.-dangerous) 是不可逆操作。执行前请尽可能 审慎核查，确保命令只应用于预期的 `ALIAS` 目标。

##### `--dry-run` {#mc.rm.-dry-run}

*mc-cmd*

*Optional*

输出命令结果，但不会实际删除任何文件。 使用此标志可测试命令配置是否仅删除你希望删除的对象。

##### `--force` {#mc.rm.-force}

*mc-cmd*

*Optional*

允许 [`mc rm`](#command-mc.rm) 与以下任一参数一起运行：

- [`--recursive`](#mc.rm.-recursive)
- [`--versions`](#mc.rm.-versions)
- [`--stdin`](#mc.rm.-stdin)

##### `--incomplete, I` {#mc.rm.-incomplete}

*mc-cmd*

*Optional*

删除指定对象的不完整上传。

如果任一 [`ALIAS`](#mc.rm.ALIAS) 指定了存储桶， 则 **必须** 同时指定 [`--recursive`](#mc.rm.-recursive) 和 [`--force`](#mc.rm.-force)。

##### `--newer-than` {#mc.rm.-newer-than}

*mc-cmd*

*Optional*

删除新于指定时长的对象。请使用 `#d#hh#mm#ss` 格式的字符串。例如：`--newer-than 1d2hh3mm4ss`

默认为 `0`（所有对象）。

##### `--non-current` {#mc.rm.-non-current}

*mc-cmd*

*Optional*

从指定的 [`ALIAS`](#mc.rm.ALIAS) 中删除所有 [非当前](/docs/administration/object-management/object-versioning/#minio-bucket-versioning-delete) 对象版本。

对未启用 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的存储桶，此选项无效。

##### `--older-than` {#mc.rm.-older-than}

*mc-cmd*

*Optional*

删除早于指定时间限制的对象。请使用 `#d#h#m#s` 格式的字符串。例如：`--older-than 1d2h3m4s`。

默认为 `0`（所有对象）。

##### `--recursive, r` {#mc.rm.-recursive}

*mc-cmd*

*Optional*

递归删除每个 [`ALIAS`](#mc.rm.ALIAS) 存储桶或存储桶前缀的内容。

如果指定 [`--recursive`](#mc.rm.-recursive)，则 **必须** 同时 指定 [`--force`](#mc.rm.-force)。

对启用了 [版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的存储桶， 此选项默认会为每个被删除对象生成一个删除标记。 添加 [`--versions`](#mc.rm.-versions) 标志可递归删除存储桶中的 所有对象 *以及* 对象版本。

建议先使用 [`--dry-run`](#mc.rm.-dry-run) 标志运行命令，验证 递归删除操作的范围。

与 [`mc rm --version-id`](#mc.rm.-version-id) 互斥

##### `--rewind` {#mc.rm.-rewind}

*mc-cmd*

*Optional*

指示 [`mc rm`](#command-mc.rm) 仅对指定时间点存在的对象版本执行操作。

- 如需回溯到过去的特定日期，请将该日期指定为 ISO8601 格式的时间戳。 例如：`--rewind "2020.03.24T10:00"`。
- 如需按时间长度回溯，请将该时长指定为 `#d#hh#mm#ss` 格式的字符串。 例如：`--rewind "1d2hh3mm4ss"`。

[`--rewind`](#mc.rm.-rewind) 要求指定的 [`ALIAS`](#mc.rm.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

##### `--stdin` {#mc.rm.-stdin}

*mc-cmd*

*Optional*

从 `STDIN` 读取对象名称或存储桶。

##### `--versions` {#mc.rm.-versions}

*mc-cmd*

*Optional*

指示 [`mc rm`](#command-mc.rm) 对存储桶中存在的所有对象版本执行操作。

[`--versions`](#mc.rm.-versions) 要求指定的 [`ALIAS`](#mc.rm.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

将 [`--versions`](#mc.rm.-versions) 与 [`--rewind`](#mc.rm.-rewind) 一起使用，可删除某一特定时间点 存在的对象的所有版本。

##### `--version-id, vid` {#mc.rm.-version-id}

*mc-cmd*

*Optional*

指示 [`mc rm`](#command-mc.rm) 仅对指定的对象版本执行操作。

[`--version-id`](#mc.rm.-version-id) 要求指定的 [`ALIAS`](#mc.rm.ALIAS) 指向支持 [存储桶版本控制](/docs/administration/object-management/object-versioning/#minio-bucket-versioning) 的 S3 兼容服务。对于 MinIO 部署， 请使用 [`mc version`](/docs/reference/minio-mc/mc-version/#command-mc.version) 启用或禁用存储桶版本控制。

与以下任一标志互斥：

- [`--versions`](#mc.rm.-versions)
- [`--rewind`](#mc.rm.-rewind)
- [`--recursive`](#mc.rm.-recursive)

### 全局标志 {#id8}

此命令支持 [全局标志](/docs/reference/minio-mc/#minio-mc-global-options) 中的任意选项。

## 示例 {#id9}

### 删除单个对象 {#id10}

```shell
mc rm ALIAS/PATH
```

- 将 [`ALIAS`](#mc.rm.ALIAS) 替换为已配置的 S3 兼容服务的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.rm.ALIAS) 替换为对象路径。

### 递归删除存储桶内容 {#id11}

将 [`mc rm`](#command-mc.rm) 与 [`--recursive`](#mc.rm.-recursive) 和 [`--force`](#mc.rm.-force) 选项结合使用， 可递归删除存储桶内容。

```shell
mc rm --recursive --force ALIAS/PATH
```

- 将 [`ALIAS`](#mc.rm.ALIAS) 替换为已配置的 S3 兼容服务的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.rm.ALIAS) 替换为存储桶路径。

此操作 *不会* 删除存储桶本身。请使用 [`mc rb`](/docs/reference/minio-mc/mc-rb/#command-mc.rb) 删除存储桶 及其全部内容和关联配置。

### 删除对象的所有不完整上传文件 {#id12}

将 [`mc rm`](#command-mc.rm) 与 [`--incomplete`](#mc.rm.-incomplete) 选项结合使用， 可删除某个对象的不完整上传文件。

```shell
mc rm --incomplete --recursive --force ALIAS/PATH
```

- 将 [`ALIAS`](#mc.rm.ALIAS) 替换为已配置的 S3 兼容服务的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.rm.ALIAS) 替换为对象路径。

### 将对象回滚到先前版本 {#id13}

将 [`mc rm`](#command-mc.rm) 与 [`--versions`](#mc.rm.-versions) 和 [`--newer-than`](#mc.rm.-newer-than) 结合使用，可删除新于指定时长的 所有对象版本。这会有效地将对象“回滚”到该时间点的状态。

> [!WARNING]
> **重要**
>
> 删除对象的特定版本属于 *破坏性* 操作。你无法恢复 已删除的对象版本。

```shell
mc rm ALIAS/PATH --versions --newer-than DURATION
```

- 将 [`ALIAS`](#mc.rm.ALIAS) 替换为已配置的 S3 兼容服务的 [`alias`](/docs/reference/minio-mc/mc-alias/#command-mc.alias)。
- 将 [`PATH`](#mc.rm.ALIAS) 替换为对象路径。 例如：`/mybucket/myobject`。
- 将 [`DURATION`](#mc.rm.-newer-than) 替换为相对于当前主机时间的过去时长， 操作将从该时间点开始删除对象版本。例如，要删除过去 30 天内 创建的所有对象版本，请指定 `"30d"`。

## 行为 {#id14}

### 删除存储桶内容 {#id15}

使用 [`mc rm`](#command-mc.rm) 删除存储桶中的全部内容时，不会删除存储桶本身。 与该存储桶关联的配置会保留，例如 [`default object lock settings`](/docs/reference/minio-mc/mc-retention-set/#mc.retention.set.-default)。

如需彻底删除存储桶，请使用 [`mc rb`](/docs/reference/minio-mc/mc-rb/#command-mc.rb)，而不是 [`mc rm`](#command-mc.rm)。

### MinIO 在删除对象时会清理空前缀 {#minio}

[`mc rm`](#command-mc.rm) 依赖 [`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 来移除对象。在删除存储桶前缀中的最后一个对象时， [`mc`](/docs/reference/minio-mc/#command-mc) 还会递归删除直到存储桶根为止的每一个空前缀。[`mc`](/docs/reference/minio-mc/#command-mc) 只会对在对象写入 操作过程中 *隐式* 创建的前缀执行这种递归删除，也就是说，该前缀不是通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 这类显式目录创建命令创建的。

例如，假设存储桶 `photos` 中有以下对象前缀：

- `photos/2021/january/myphoto.jpg`
- `photos/2021/february/myotherphoto.jpg`
- `photos/NYE21/NewYears.jpg`

`photos/NYE21` 是 *唯一* 通过 [`mc mb`](/docs/reference/minio-mc/mc-mb/#command-mc.mb) 显式创建的前缀。其余所有前缀 都是在向该前缀写入对象时 *隐式* 创建的。

如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `myphoto.jpg`，删除 API 会自动裁剪空的 `/january` 前缀。如果后续某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令又删除了 `myotherphoto.jpg`， 删除 API 会自动裁剪 `/february` 前缀，以及此时已经为空的 `/2021` 前缀。 如果某个 [`mc`](/docs/reference/minio-mc/#command-mc) 命令删除了 `NewYears.jpg`，由于 `/NYE21` 是 *显式* 创建的，因此该前缀会保留不变。

如果将 [`mc rm`](#command-mc.rm) 用于文件系统操作，[`mc`](/docs/reference/minio-mc/#command-mc) 也会采用相同行为，递归裁剪直到 根目录的所有空目录。不过，[`mc`](/docs/reference/minio-mc/#command-mc) 的删除 API 无法区分某个目录路径是显式 创建的，还是隐式创建的。如果 [`mc rm`](#command-mc.rm) 删除了某个文件系统路径上的最后一个对象， [`mc`](/docs/reference/minio-mc/#command-mc) 会在删除过程中递归删除从该路径向上直到根目录的所有空目录。

### 版本化存储桶中的删除操作 {#id16}

MinIO 支持在单个存储桶中保留对象的多个 [版本](/docs/administration/object-management/object-versioning/#minio-bucket-versioning)。 在版本化存储桶中 [删除](/docs/administration/object-management/object-versioning/#minio-bucket-versioning-delete) 对象时， 会生成一种特殊的 `DeleteMarker` 墓碑记录，将对象标记为已删除， 同时保留该对象的所有先前版本。

- 要从存储桶中删除对象的特定版本，请使用 [`mc rm --version-id`](#mc.rm.-version-id)
- 要从存储桶中删除对象的所有版本，请使用 [`mc rm --versions`](#mc.rm.-versions)
- 要从存储桶中删除对象的所有非当前版本，请使用 [`mc rm --non-current`](#mc.rm.-non-current)

> [!NOTE]
> **变更: mc**
>
> RELEASE.2023-03-20T17-17-53Z
>
> 输出会显示版本化文件的修改时间。 与 `--dry-run` 搭配使用时，这有助于确认你选择了正确的删除对象。

### S3 兼容性 {#s3}

**`mc`** 命令行工具以兼容 AWS S3 API 为目标构建，并针对 MinIO 和 AWS S3 进行了测试，以验证预期的功能与行为。

对于其他 S3 兼容服务，MinIO 不提供任何保证，因为这些服务的 S3 API 实现未知， 因此不在支持范围内。虽然 **`mc`** 命令 *可能* 仍能按文档说明工作，但此类 用法需要你自行承担风险。