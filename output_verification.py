from lark import Lark
import re


def import_xyce_quick_parse():

    return Lark("""

    start : sp_f

    sp_f : sp_ln+

    sp_ln : xyce_cmd "\n"
        | xyce_comp_line "\n"

    xyce_cmd : CMD XYCE_PARAM*

    xyce_comp_line : comp

    comp : ECE_COMP list_of_nodes list_of_params

    list_of_nodes : COMP_NODE+
    list_of_params : COMP_PARAMS*

    CMD : /\.[a-zA-Z][a-zA-Z0-9_\-]*/
    CNAME : /[a-zA-Z_][a-zA-Z0-9_\.]*/
    XYCE_PARAM : /[a-zA-Z_][a-zA-Z0-9_\.=\-()]*/

    ECE_COMP : /[VvCcIiRrLl]/
    CSTM_COMP : /[Yy][a-zA-Z][a-zA-Z0-9_\.]/

    COMP_NODE : /[0-9]+/
    COMP_PARAMS : /[a-zA-Z_][a-zA-Z0-9_]*\=[a-zA-Z0-9_]+/

""")
    #
    # ECE_COMP : /[BbCcDdEeFfGgVvCcIiRr]/


channel_flow_ref = r"[Yy]\w*\s+\n"
serp_flow_ref = r""
mix_flow_ref = r""

channel_chem_ref = r""
serp_chem_ref = r""
mix_chem_ref = r""

channel_heat_ref = r""
serp_heat_ref = r""
mix_heat_ref = r""

# line parse regex

comment = r"\*.*$"

xyce_cmd = r"\.\w+"

ece_comp = r"[VvIiRrCcLl][a-zA-Z0-9_]"
y_comp = r"[Yy][\w]*"

y_comp_inst = r"[a-zA-Z_][a-zA-Z0-9_]*"

node_reg = r"\d+"
comp_param = r"[a-zA-Z_][a-zA-Z0-9_]*\=[a-zA-Z0-9_][a-zA-Z0-9_]*"

pump_reg = r"[Yy]pressurePump"
chan_reg = r"[Yy]channel"
serp_reg = r"[Yy]serpentine_\d+px_\d+"
mixr_reg = r"[Yy]diffmix_\d+px_\d+"

#   number of nodes
# node : [flow, chem, heat]
comp_reg = {
    chan_reg: {
        "nodes": [2, 4, 6],
        "": ""
    },
    serp_reg: {
        "nodes": [2, 4, 6],
        "": ""
    },
    mixr_reg: {
        "nodes": [3, 6, 9],
        "": ""
    },
}


"""
main parse function
sim_type:
    0 - flow
    1 - chem
    2 - heat transfer
"""


def parse_line(in_line, sim_type=0):
    tokens = in_line.split()

    if re.match(tokens[0], xyce_cmd):
        parse_xyce_cmd(tokens)
    elif re.match(tokens[0], ece_comp):
        parse_ece_comp(tokens)
    elif re.match(tokens[0], y_comp):
        parse_y_comp(tokens, sim_type)


"""
Line parsers
"""


def parse_xyce_cmd(tkn):
    if tkn[0] == '.print':
        pass
    elif tkn[0] == '.tran':
        pass
    elif tkn[0] == '.end':
        pass
    else:
        pass


def parse_cmd_pring(tkn):
    if tkn[1] == 'tran':
        pass
    elif tkn[1] == '':
        pass


def parse_print_node_access(tkn):
    for nd_tkn in tkn[2:]:
        if re.match(nd_tkn, r""):
            pass
        elif re.match(nd_tkn, r""):
            pass
        else:
            raise ValueError(f"Invalid definition {nd_tkn}")


def parse_y_comp(tkn, sim_type=0):

    nd_num = None

    for reg in comp_reg.keys():
        if re.match(reg, tkn):
            nd_num = comp_reg[reg]["nodes"][sim_type]

    if nd_num is None:
        raise ValueError(f"Could not identify component '{tkn[0]}'")

    # check the number of nodes


def parse_ece_comp(tkn):
    pass


def verify_write_spice_output(spice_file):

    pass
