import sys
import re
from collections import defaultdict

pattern = re.compile(r'(?P<command>\w+) ?(?P<arg1>\w+)? ?(?P<arg2>\d+)?')

class Writer:
    def __init__(self, f):
        self.file = f

    def line(self, line):
        self.file.write(f'{line}\n')

    def lines(self, lines):
        self.file.write('\n'.join(lines))
        self.file.write('\n')

class Command:
    BASE_ADDRESS = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS',
                    'that': 'THAT'}

    def null():
        return Null

    def length(self):
        return len(self.asm())

class Null(Command):
    def asm(self, position=0):
        return ()

class Push(Command):
    def __init__(self, segment, index):
        self.segment = segment
        self.index = index

    def asm(self, position=0):
        statements = [f'@{self.index}',
                      'D=A']

        if self.segment != 'constant':
            statements += [f'@{self.BASE_ADDRESS[self.segment]}',
                           'A=M+D', 'D=A']

        statements += ['@SP',
                       'A=M',
                       'M=D',
                       '@SP',
                       'M=M+1']

        return statements


class Add(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=M+D',
                '@SP',
                'M=M+1')

class Sub(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=M-D',
                '@SP',
                'M=M+1')

class Eq(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M-D',
                f'@{position + 14}',
                'D; JEQ',
                '@SP',
                'A=M',
                'M=0',
                f'@{position + 17}',
                '0; JMP',
                '@SP',
                'A=M',
                'M=-1',
                '@SP',
                'M=M+1')

class LT(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M-D',
                f'@{position + 14}',
                'D; JLT',
                '@SP',
                'A=M',
                'M=0',
                f'@{position + 17}',
                '0; JMP',
                '@SP',
                'A=M',
                'M=-1',
                '@SP',
                'M=M+1')

class GT(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M-D',
                f'@{position + 14}',
                'D; JGT',
                '@SP',
                'A=M',
                'M=0',
                f'@{position + 17}',
                '0; JMP',
                '@SP',
                'A=M',
                'M=-1',
                '@SP',
                'M=M+1')

class And(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=D&M',
                '@SP',
                'M=M+1')

class Or(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=D|M',
                '@SP',
                'M=M+1')

class Neg(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                'M=M-D',
                'M=M-D',
                '@SP',
                'M=M+1')

class Not(Command):
    def asm(self, position=0):
        return ('@SP',
                'AM=M-1',
                'M=-M',
                'M=M-1',
                '@SP',
                'M=M+1')

commands = defaultdict(Command.null)
commands['add'] = Add
commands['push'] = Push
commands['eq'] = Eq
commands['lt'] = LT
commands['gt'] = GT
commands['sub'] = Sub
commands['neg'] = Neg
commands['and'] = And
commands['or'] = Or
commands['not'] = Not

with open(sys.argv[1]) as infile:
    with open(sys.argv[2], 'w') as outfile:
        writer = Writer(outfile)
        length = 0

        for line in infile:
            current_line = line.strip()

            if len(current_line) > 0 and current_line[0] != '/':
                writer.line(f'// {current_line}')

                matches = pattern.match(current_line)
                cmd, arg1, arg2 = matches.group('command', 'arg1', 'arg2')

                if cmd == 'push' or cmd == 'pop':
                    command = commands[cmd](arg1, arg2)
                else:
                    command = commands[cmd]()

                writer.lines(command.asm(position=length - 1))
                length += command.length()
