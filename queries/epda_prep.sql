INSERT INTO prep_epda (Year,Month,Item_Code,Item_Name,Territory_Name,client_name,Sales_Units,Bonus_Units,Dist_name)
SELECT
    Year,
    Month,
    "item code" AS Item_Code,
    "item name" AS Item_Name,
    
    TRIM(
    COALESCE(
        NULLIF(SUBSTR("client name", INSTR("client name", '-') + 1), ''),   -- right part after "-"
        NULLIF(SUBSTR("client name", 1, INSTR("client name", '-') - 1), ''), -- left part before "-"
        "client name"                                             -- fallback to original
    )
    ) AS Territory_Name,
    "client name" As client_name,
    "sales Units" AS Sales_Units,
    0 AS Bonus_Units,
    'EPDA' AS Dist_name
FROM native_epda
where Month = :month AND Year =:year;

   