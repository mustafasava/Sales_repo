from cln_ibs import cln_ibs
from prep_ibs import prep_ibs
from cln_pos import cln_pos
from prep_pos import prep_pos
from cln_sofico import cln_sofico
from prep_sofico import prep_sofico
from cln_epda import cln_epda
from prep_epda import prep_epda
from cln_egydrug import cln_egydrug
from prep_egydrug import prep_egydrug


dist_list = {
    "ibs": [cln_ibs, prep_ibs,["brick_name", "governorate_name","brick_code"]],
    "pos": [cln_pos, prep_pos,["territory_name","brick_code"]],
    "sofico": [cln_sofico, prep_sofico,["territory_name", "address","brick_code"]],
    "epda": [cln_epda, prep_epda,["client_name", "client_code"]],
    "egydrug": [cln_egydrug, prep_egydrug,[ "customer_name","customer_address", "branch_name","brick_code"]]
}



auth = {"Mustafa Muhammed": ["admin", "sava1998", "all"],
        "Mohamed Youssef": ["sales", "alex123", "alex"],
        "Hossam Mohamed": ["sales", "cairo1234", "cairo"],
        "Ahmed Reda": ["sales", "upper12345", "upper"],
        "Mohamed Saleh": ["sales", "MS1234", "all"],
        "Mohamed Rayes": ["sales", "MR1234", "all"]   }





