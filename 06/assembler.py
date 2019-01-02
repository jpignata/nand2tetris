import sys, re

symbols = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'SCREEN': 16384,
           'KBD': 24576}
cinstr = re.compile(r'(?:(?P<dest>\w+)=)?' + r'(?P<comp>[^;]*)' +
                     r'(?: *;? *(?P<jump>\w{3})?)?')
comps = {'0': 42, '1': 63, '-1': 58, 'D': 12, 'A': 48, 'M': 112, '!D': 13,
         '!A': 49, '!M': 113, '-D': 15, '-A': 51, '-M': 115, 'D+1': 31,
         'A+1': 55, 'M+1': 119, 'D-1': 14, 'A-1': 50, 'M-1': 114, 'D+A': 2,
         'D+M': 66, 'D-A': 19, 'D-M': 83, 'A-D': 7, 'M-D': 71, 'D&A': 0,
         'D&M': 64, 'D|A': 21, 'D|M': 85}
dests = None, 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD'
jumps = None, 'JGT', 'JEQ', 'JGE', 'JLT', 'JNE', 'JLE', 'JMP'
line_number = 0
symbol_address = 16

for num in range(symbol_address + 1): symbols[f'R{num}'] = num

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
            value = line[1:]
            if value.isdigit():
                outfile.write(format(int(value), '016b') + '\n')
            else:
                if value not in symbols:
                    symbols[value] = symbol_address
                    symbol_address += 1
                outfile.write(format(symbols[value], '016b') + '\n')
        elif line[0] != '(':
            dest, comp, jump = cinstr.match(line).group('dest', 'comp', 'jump')
            outfile.write('111' + format(comps[comp], '07b') +
                          format(dests.index(dest), '03b') +
                          format(jumps.index(jump), '03b') + '\n')
