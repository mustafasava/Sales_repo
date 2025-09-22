INSERT INTO prep_ibs (Year,Month,Item_Code,Item_Name,Brick,Territory,Governorate_Name,Sales_Units,Bonus_Units,Dist_name)

SELECT
    Year,
    Month,
    "Item Code" AS Item_Code,
    "Item Name" AS Item_Name,
    Brick,
    "Governorate Name" AS Governorate_Name ,
    CASE 
        WHEN "Territory Name" = 'Template District                       '
            THEN "Brick Name"
        WHEN "Territory Name" = 'QENA I /RED SEA RED SEA                 '
            THEN "Governorate Name"
        WHEN "Territory Name" = 'NASR CITY NASR CITY                     '
             AND (
                 "Governorate Name" = 'القاهره الجديده     '
                 OR "Governorate Name" LIKE '%عاصم%'
             )
            THEN 'القاهره الجديده     '
        ELSE "Territory Name"
    END AS Territory_Name,
    QTY AS Sales_Units,
    FU  AS Bonus_Units,
    'IBS' AS Dist_name
FROM native_ibs
where Month = :month AND Year =:year;