-- 真数据：5000 行 + 一列 MD5 派生的校验字段，用来做「重启/备份/恢复」前后的同一性判据
CREATE TABLE IF NOT EXISTS kbdb.t_note (
  id INT PRIMARY KEY,
  body VARCHAR(255) NOT NULL,
  tag VARCHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  crc CHAR(8) NOT NULL
);
-- 递归 CTE 的深度上限默认 1000（@@cte_max_recursion_depth）；不设这一行，
-- 下面那条 5000 行的 INSERT 会在第 1001 次迭代被中止：
--   ERROR 3636 (HY000) at line 9: Recursive query aborted after 1001 iterations.
--   Try increasing @@cte_max_recursion_depth to a larger value.
-- 而 mysql 入口脚本遇到这个错误只是退出，datadir 已经非空，之后 init 不再重跑
-- —— 容器仍然 healthy，表却一行都没有。这一条本身就是本案例要讲的故障之一。
SET SESSION cte_max_recursion_depth = 10000;

INSERT INTO kbdb.t_note (id, body, tag, crc)
SELECT n, CONCAT('row-', n, '-payload-payload'), IF(n % 2 = 0, 'even', 'odd'),
       SUBSTRING(MD5(CONCAT('salt-', n)), 1, 8)
FROM (WITH RECURSIVE seq AS (SELECT 1 n UNION ALL SELECT n + 1 FROM seq WHERE n < 5000) SELECT n FROM seq) s
ON DUPLICATE KEY UPDATE body = VALUES(body);
SELECT COUNT(*) AS rows_now, SUM(CRC32(CONCAT(id, body, tag, crc))) AS agg_crc FROM kbdb.t_note;
