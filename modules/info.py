from cln_ibs import cln_ibs
from cln_pos import cln_pos
from cln_sofico import cln_sofico
from cln_epda import cln_epda
from cln_egydrug import cln_egydrug


dist_list = {
    "ibs": cln_ibs,
    "pos": cln_pos,
    "sofico": cln_sofico,
    "epda": cln_epda,
    "egydrug": cln_egydrug}


auth = {"user1": ["admin", "1234", "all"],
        "user2": ["sales", "1234", "alex"],
        "user3": ["sales", "1234", "cairo"]}



