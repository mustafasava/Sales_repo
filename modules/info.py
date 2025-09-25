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
    "ibs": [cln_ibs, prep_ibs],
    "pos": [cln_pos, prep_pos],
    "sofico": [cln_sofico, prep_sofico],
    "epda": [cln_epda, prep_epda],
    "egydrug": [cln_egydrug, prep_egydrug],
}


dist_list = {
    "ibs": [cln_ibs,prep_ibs],
    "pos": [cln_pos,prep_pos],
    "sofico": [cln_sofico,prep_sofico],
    "epda": [cln_epda,prep_epda],
    "egydrug": [cln_egydrug,prep_egydrug]}


auth = {"user1": ["admin", "1234", "all"],
        "user2": ["sales", "1234", "alex"],
        "user3": ["sales", "1234", "cairo"]}



