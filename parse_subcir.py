
import re

init_re = r''
subcmd = r'\.[Ss][Uu][Bb][Cc][Kk][Tt]'
cirname = r'(?P<subname>[\w]+)'
delim = r'\s+'

params = r'([Pp][Aa][Rr][Aa][Mm][Ss]:\s+((\w+=[\w\d]\s*?)*))?'

# end_re = r'$'
end_re = r''

subcir_reg = delim.join([
    init_re + subcmd,
    cirname,
    params + end_re
])

test_subcir_file = 'subcir.cir'


def get_subcir_from_include(in_file):

    print("REGEX:\n", subcir_reg)

    with open(in_file) as inf:

        sub_list = []

        for line in inf:

            re_out = re.search(subcir_reg, line)

            if re_out is not None:

                sub_name = re_out.groups('subname')[0]

                print("SUBCKT found:", sub_name)
                sub_list.append(sub_name)
            else:
                # print(' -no match-', line.replace('\n', ''))
                pass

        return sub_list
