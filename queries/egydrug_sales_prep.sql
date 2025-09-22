INSERT INTO prep_egydrug_sales (Year,Month,Item_Code,Item_Name,CUSTOMER_CODE,CUSTOMER_NAME,
                                CUSTOMER_ADDRESS,BRANCH_NAME,sheet_src,Sales_Units,Bonus_Units,Dist_name)
SELECT
    Year,
    Month,
    ITEM_CODE AS Item_Code,
    ITEM_NAME AS Item_Name,
    CUSTOMER_CODE ,
    CUSTOMER_NAME,
    CUSTOMER_ADDRESS,
    BRANCH_NAME,
    sheet_src,

    CASE
        WHEN STATUS_NAME not LIKE '%بونص%' AND STATUS_DESC not  LIKE '%بونص%'
        THEN QTY_INVOICE + RETURN_QTY
        ELSE 0
    END AS Sales_Units,

    CASE
        WHEN STATUS_NAME LIKE '%بونص%' OR STATUS_DESC LIKE '%بونص%'
        THEN QTY_INVOICE + RETURN_QTY
        ELSE 0
    END AS Bonus_Units,

   
    
    'EgyDrug' AS Dist_name
FROM native_egydrug_sales
where Month = :month AND Year =:year;

   