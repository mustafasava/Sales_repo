INSERT INTO prep_pos (Year,Month,Item_Code,Item_Name,Territory_Code,Territory_Name,Sales_Units,Bonus_Units,Dist_name)
SELECT
    Year,
    Month,
    "Product Code" AS Item_Code,
    "Product Name" AS Item_Name,
    "Territory Code" As Territory_Code,
    "Territory Name" As Territory_Name,
    Sales / 2 AS Sales_Units,
    Bonus / 2 AS Bonus_Units,
    'POS' AS Dist_name
FROM native_pos
WHERE "Territory Code" in ('280C6','406C6','407C6','M0009')  AND  Month = :month AND Year = :year 





UNION ALL

SELECT
    Year,
    Month,
    "Product Code" AS Item_Code,
    "Product Name" AS Item_Name,
    "N9999999" As Territory_Code,
    "New Cairo" As Territory_Name,
    Sales / 2 AS Sales_Units,
    Bonus / 2 AS Bonus_Units,
    'POS' AS Dist_name
FROM native_pos
WHERE "Territory Code" in ('280C6','406C6','407C6','M0009') AND  Month = :month AND Year = :year

UNION ALL

SELECT
    Year,
    Month,
    "Product Code" AS Item_Code,
    "Product Name" AS Item_Name,
    "Territory Code" As Territory_Code,
    "Territory Name" As Territory_Name,
    Sales  AS Sales_Units,
    Bonus  AS Bonus_Units,
    'POS' AS Dist_name
FROM native_pos
WHERE "Territory Code" not in ('280C6','406C6','407C6','M0009') AND  Month = :month AND Year = :year;


