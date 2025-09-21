SELECT 'DELETE FROM ' || name || ';' AS stmt
FROM sqlite_master
WHERE type = 'table'
  AND name NOT LIKE 'sqlite_%'
UNION ALL
SELECT 'DELETE FROM sqlite_sequence ; ';