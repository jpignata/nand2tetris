import sys
import re

symbols = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'R0': 0, 'R1': 1,
           'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8,
           'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14,
           'R15': 15, 'SCREEN': 16384, 'KBD': 24576}
comps = {'0': 42, '1': 63, '-1': 58, 'D': 12, 'A': 48, 'M': 112, '!D': 13,
         '!A': 49, '!M': 113, '-D': 15, '-A': 51, '-M': 115, 'D+1': 31,
         'A+1': 55, 'M+1': 119, 'D-1': 14, 'A-1': 50, 'M-1': 114, 'D+A': 2,
         'D+M': 66, 'D-A': 19, 'D-M': 83, 'A-D': 7, 'M-D': 71, 'D&A': 0,
         'D&M': 64, 'D|A': 21, 'D|M': 85}
dests = {None: 0, 'M': 1, 'D': 2, 'MD': 3, 'A': 4, 'AM': 5, 'AD': 6, 'AMD': 7}
jumps = {None: 0, 'JGT': 1, 'JEQ': 2, 'JGE': 3, 'JLT': 4, 'JNE': 5, 'JLE': 6,
         'JMP': 7}
pattern = re.compile(r'(?:(?P<dest>\w+)=)?' + r'(?P<comp>[^;]*)' +
                     r'(?: *;? *(?P<jump>\w{3})?)?')
line_number = 0
variable_symbol = 16

with open(sys.argv[1]) as infile:
    lines = [re.sub(r'(.*) +//.*', '\g<1>', line).strip() for line in infile
             if len(line.strip()) > 0 and line.strip()[0] != '/']

for line in lines:
    if line[0] == '(':
        symbols[line[1:-1]] = line_number
    else:
        line_number += 1

with open(sys.argv[2], 'w') as outfile:
    for line in lines:
        if line[0] == '@':
            symbol = line[1:]
            if symbol.isdigit():
                outfile.write(format(int(symbol), '016b'))
            else:
                if symbol not in symbols:
                    symbols[symbol] = variable_symbol
                    variable_symbol += 1
                outfile.write(format(symbols[symbol], '016b'))
        elif line[0] != '(':
            matches = pattern.match(line)
            dest, comp, jump = matches.group('dest', 'comp', 'jump')
            outfile.write('111' + format(comps[comp], '07b') +
                          format(dests[dest], '03b') +
                          format(jumps[jump], '03b'))
        outfile.write('\n')
