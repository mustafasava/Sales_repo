from cleaning import *
from dbs_export import *
from preparing import *


from datetime import datetime


print(datetime.now())

print(egydrug_sales_prep(*egydrug_exp(*egydrug_cln("D:\\Project Sales\\Distributors sheets\\EgyDrug 2025-5.xlsx")))[0])

print(datetime.now())


