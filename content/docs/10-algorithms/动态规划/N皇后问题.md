---
title: N 皇后问题
description: N 皇后问题的回溯算法详解——逐行放置、冲突检测、回退策略，以及位运算优化方案。
weight: 2
---

# 为什么需要 N 皇后？

国际象棋中，皇后是最强大的棋子——横、竖、斜都能攻击。

现在有一个经典难题：**在 8×8 的棋盘上放 8 个皇后，让她们互不攻击**。

听起来简单？试试就知道了：

```
第 1 行放第 0 列 → 第 2 行放第 2 列 → 第 3 行放第 4 列 → ...
走到某一步发现放不下去了 → 回退 → 换个位置再试
```

这就是**回溯算法**的核心思想：**尝试 → 发现不行 → 回退 → 换一条路再试**。

**N 皇后的实际意义**：

| 应用场景 | N 皇后的影子 |
|---------|-------------|
| 调度系统 | N 个任务分配到 N 个时间槽，互不冲突 |
| 编译器设计 | 寄存器分配（不冲突的资源分配） |
| 约束求解 | 数独、八数码等谜题的求解 |
| 面试考点 | 回溯算法的经典代表 |

> ### 💡 新人小结：什么是回溯？
>
> 把回溯想象成「走迷宫」：
> - 走到一个路口，先选左边 → 走到死胡同 → 回退到路口 → 选右边
> - 这就是回溯：尝试 → 失败 → 回退 → 换路
>
> N 皇后也一样：每行放一个皇后，放到某行发现没位置了 → 回退到上一行换个位置 → 继续往下放

**学习路线图**：

```
本文学习路线

 ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────┐
 │ 问题定义      │ →  │ 回溯算法          │ →  │ 位运算优化        │ →  │ 复杂度分析    │
 │ 规则与约束    │    │ 放置 → 递归 → 回退│    │ 冲突检测 O(1)   │    │ 剪枝的威力    │
 └──────────────┘    └──────────────────┘    └──────────────────┘    └──────────────┘
```

---

## 问题定义

在 N × N 的国际象棋棋盘上放置 N 个皇后，使得任意两个皇后都不能相互攻击。

**皇后的攻击范围**：同一行、同一列、同一对角线（左上到右下、右上到左下）。

| N | 解的数量 |
|---|---------|
| 1 | 1 |
| 4 | 2 |
| 8 | 92 |
| 12 | 14200 |
| 14 | 365596 |

---

## 回溯算法核心思想

### 痛点引入

暴力法：在 N×N 的棋盘上放 N 个皇后，有 C(N², N) 种放法。8 皇后就有 C(64, 8) ≈ 44 亿种组合。

**关键优化**：逐行放置，每行只放一个皇后——这样行冲突自动消除，只需检测列和对角线。

**逐行放置**：从第 0 行开始，每行尝试在某一列放置皇后，然后递归处理下一行。如果当前放置导致后续无法继续，则**回退**（撤销当前选择），尝试下一列。

**为什么逐行放置？** 每行恰好放一个皇后，天然避免了行冲突，只需检测列冲突和对角线冲突。

---

## 约束检查

对于第 `row` 行第 `col` 列的候选位置，需要检查：

1. **列冲突**：之前某行的皇后是否在同一列 → `queens[i] == col`
2. **主对角线冲突**（左上到右下）：行差等于列差 → `|i - row| == |queens[i] - col|`
3. **副对角线冲突**（右上到左下）：同上，因为两个方向的对角线都满足行距 = 列距

> 实际上，主对角线和副对角线的判断条件相同：`|row1 - row2| == |col1 - col2|`

---

## Java 实现

```java
public class NQueens {

    private int n;
    private int[] queens;   // queens[i] = 第 i 行皇后的列位置
    private int count;      // 解的总数

    public NQueens(int n) {
        this.n = n;
        this.queens = new int[n];
        this.count = 0;
    }

    /**
     * 求解并打印所有方案
     */
    public void solve() {
        placeQueen(0);
        System.out.println(n + " 皇后问题共有 " + count + " 种解法");
    }

    /**
     * 在第 row 行放置皇后
     */
    private void placeQueen(int row) {
        if (row == n) {
            // 所有行都已放置成功，找到一个解
            printBoard();
            count++;
            return;
        }

        for (int col = 0; col < n; col++) {
            if (isSafe(row, col)) {
                queens[row] = col;        // 放置
                placeQueen(row + 1);      // 递归下一行
                // 回溯：不需要显式撤销，下一次循环会覆盖 queens[row]
            }
        }
    }

    /**
     * 检查第 row 行第 col 列是否可以安全放置
     */
    private boolean isSafe(int row, int col) {
        for (int i = 0; i < row; i++) {
            // 列冲突
            if (queens[i] == col) return false;
            // 对角线冲突
            if (Math.abs(i - row) == Math.abs(queens[i] - col)) return false;
        }
        return true;
    }

    /**
     * 打印棋盘
     */
    private void printBoard() {
        for (int row = 0; row < n; row++) {
            for (int col = 0; col < n; col++) {
                System.out.print(queens[row] == col ? "Q " : ". ");
            }
            System.out.println();
        }
        System.out.println();
    }

    // ========== 测试 ==========
    public static void main(String[] args) {
        new NQueens(8).solve();
    }
}
```

**8 皇后输出**（共 92 种解，展示前 2 种）：

```
Q . . . . . . .
. . . . Q . . .
. . . . . . . Q
. . . . . Q . .
. . Q . . . . .
. . . . . . Q .
. Q . . . . . .
. . . Q . . . .

Q . . . . . . .
. . . . . Q . .
. . . . . . . Q
. . Q . . . . .
. . . . . . Q .
. . . Q . . . .
. Q . . . . . .
. . . . Q . . .

... (共 92 种)

8 皇后问题共有 92 种解法
```

---

## 统计所有解的数量

如果只需要统计解的数量而不需要打印棋盘：

```java
public class NQueensCounter {

    private int n;
    private int[] queens;
    private int count;

    public NQueensCounter(int n) {
        this.n = n;
        this.queens = new int[n];
        this.count = 0;
    }

    public int countSolutions() {
        placeQueen(0);
        return count;
    }

    private void placeQueen(int row) {
        if (row == n) {
            count++;
            return;
        }
        for (int col = 0; col < n; col++) {
            if (isSafe(row, col)) {
                queens[row] = col;
                placeQueen(row + 1);
            }
        }
    }

    private boolean isSafe(int row, int col) {
        for (int i = 0; i < row; i++) {
            if (queens[i] == col) return false;
            if (Math.abs(i - row) == Math.abs(queens[i] - col)) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 12; n++) {
            System.out.println(n + " 皇后: " + new NQueensCounter(n).countSolutions() + " 种解");
        }
    }
}
```

**输出**：

```
1 皇后: 1 种解
2 皇后: 0 种解
3 皇后: 0 种解
4 皇后: 2 种解
5 皇后: 10 种解
6 皇后: 4 种解
7 皇后: 40 种解
8 皇后: 92 种解
9 皇后: 352 种解
10 皇后: 724 种解
11 皇后: 2680 种解
12 皇后: 14200 种解
```

---

## 位运算优化方案

### 痛点引入

标准回溯的 `isSafe()` 方法需要循环检查之前所有行，时间复杂度 O(n)。

**优化思路**：用三个整数的 bit 位分别记录列、主对角线、副对角线的占用情况，冲突检测降到 O(1)。

使用三个整数分别标记已占用的列、主对角线和副对角线，将冲突检测从 O(n) 降到 O(1)：

```java
public class NQueensBitwise {

    private int n;
    private int count;

    public NQueensBitwise(int n) {
        this.n = n;
        this.count = 0;
    }

    public int countSolutions() {
        solve(0, 0, 0, 0);
        return count;
    }

    /**
     * @param row    当前行
     * @param cols   列占用标记（位图）
     * @param diag1  主对角线占用标记
     * @param diag2  副对角线占用标记
     */
    private void solve(int row, int cols, int diag1, int diag2) {
        if (row == n) {
            count++;
            return;
        }
        // 计算当前行可以放置的列（取反后与 n 位掩码做与运算）
        int available = ((1 << n) - 1) & ~(cols | diag1 | diag2);
        while (available != 0) {
            int pos = available & (-available);  // 取最低位的 1
            available ^= pos;                     // 清除该位
            solve(row + 1,
                  cols | pos,
                  (diag1 | pos) >> 1,
                  (diag2 | pos) << 1);
        }
    }

    public static void main(String[] args) {
        for (int n = 1; n <= 14; n++) {
            System.out.println(n + " 皇后: " + new NQueensBitwise(n).countSolutions() + " 种解");
        }
    }
}
```

**位运算优化原理**：

- `cols`：每一位代表一列是否被占用
- `diag1`：主对角线（左移方向），每下一行右移 1 位
- `diag2`：副对角线（右移方向），每下一行左移 1 位
- `available & (-available)`：提取最低位的 1，即最右边可放置的位置

---

## 复杂度分析

| 指标 | 值 |
|------|-----|
| 时间复杂度 | O(N!) — 最坏情况，实际远小于 N!（剪枝效果显著） |
| 空间复杂度 | O(N) — 递归深度 + queens 数组 |
| 位运算优化 | 冲突检测 O(1)，常数级加速 |

---

# 要点总结

1. **逐行放置**天然消除行冲突，只需检测列和对角线
2. **回溯核心**：放置 → 递归 → 撤销（本实现中下一轮循环自动覆盖）
3. **对角线判断**：`|row1 - row2| == |col1 - col2|`
4. **位运算优化**将冲突检测从循环降到位操作，是 N 皇后问题的经典优化
5. N 皇后问题的解数量没有封闭公式，只能通过搜索得到

---

> ### 💡 新人小结：N 皇后学完了，记住这 3 点
>
> 1. **回溯 = 走迷宫**：尝试 → 失败 → 回退 → 换路，直到找到所有解
> 2. **逐行放置**：每行只放一个皇后，行冲突自动消除，只需检测列和对角线
> 3. **位运算优化**：用三个整数的 bit 位记录占用情况，冲突检测从 O(n) 降到 O(1)
