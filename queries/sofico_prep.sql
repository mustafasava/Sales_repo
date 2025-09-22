INSERT INTO prep_sofico (Year,Month,Item_Code,Item_Name,Territory_Code,Territory_Name,ADDRESS,Sales_Units,Bonus_Units,Dist_name)
SELECT
    Year,
    Month,
    ItemID AS Item_Code,
    ItemName AS Item_Name,
    CASE
    WHEN ZipCode = 1101 
         AND (ADDRESS LIKE '%تجمع%' OR ADDRESS LIKE '%مدينت%')
        THEN 99009900
    WHEN ZipCode = 1102
        THEN OrderAccount
    ELSE ZipCode
    END AS Territory_Code,
    ZipCodeName AS Territory_Name,
    ADDRESS,
    SalesQty + ReturnQty AS Sales_Units,
    BonusQty + ReturnBonus AS Bonus_Units,
    'Sofico' AS Dist_name
FROM native_sofico
where Month = :month AND Year =:year;


   