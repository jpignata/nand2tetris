import sys
import re
from collections import defaultdict


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
    POINTER = '@THIS', '@THAT'

    def null():
        return Null

    def length(self):
        return len(self.asm())


class Null(Command):
    def asm(self, namespace=None, position=0):
        return ()


class Push(Command):
    def __init__(self, segment, index):
        self.segment = segment
        self.index = index

    def asm(self, namespace=None, position=0):
        statements = [f'@{self.index}', 'D=A']

        if self.segment in self.BASE_ADDRESS:
            symbol = self.BASE_ADDRESS[self.segment]
            statements += [f'@{symbol}', 'A=M+D', 'D=M']
        elif self.segment == 'temp':
            statements += ['@R5', 'A=A+D', 'D=M']
        elif self.segment == 'pointer':
            pointer = self.POINTER[self.index]
            statements += [pointer, 'D=M']
        elif self.segment == 'static':
            qualified_symbol = f'@{namespace}.{self.index}'
            statements += [qualified_symbol, 'D=M']

        statements += ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        return statements


class Pop(Command):
    def __init__(self, segment, index):
        self.segment = segment
        self.index = index

    def asm(self, namespace=None, position=0):
        statements = [f'@{self.index}', 'D=A']

        if self.segment in self.BASE_ADDRESS:
            symbol = self.BASE_ADDRESS[self.segment]
            statements += [f'@{symbol}', 'D=M+D', '@R13', 'M=D']
        elif self.segment == 'temp':
            statements += ['@R5', 'D=A+D', '@R13', 'M=D']
        elif self.segment == 'pointer':
            pointer = self.POINTER[self.index]
            statements += [pointer, 'D=A', '@R13', 'M=D']
        elif self.segment == 'static':
            qualified_symbol = f'@{namespace}.{self.index}'
            statements += [qualified_symbol, 'D=A', '@R13', 'M=D']

        statements += ['@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        return statements


class Add(Command):
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=M+D',
                '@SP',
                'M=M+1')


class Sub(Command):
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=M-D',
                '@SP',
                'M=M+1')


class Eq(Command):
    def asm(self, namespace=None, position=0):
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
    def asm(self, namespace=None, position=0):
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
    def asm(self, namespace=None, position=0):
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
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=D&M',
                '@SP',
                'M=M+1')


class Or(Command):
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'M=D|M',
                '@SP',
                'M=M+1')


class Neg(Command):
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'D=M',
                'M=M-D',
                'M=M-D',
                '@SP',
                'M=M+1')


class Not(Command):
    def asm(self, namespace=None, position=0):
        return ('@SP',
                'AM=M-1',
                'M=-M',
                'M=M-1',
                '@SP',
                'M=M+1')


pattern = re.compile(r'(?P<command>\w+) ?(?P<arg1>\w+)? ?(?P<arg2>\d+)?')
commands = defaultdict(Command.null)

commands['push'] = Push
commands['pop'] = Pop
commands['add'] = Add
commands['eq'] = Eq
commands['lt'] = LT
commands['gt'] = GT
commands['sub'] = Sub
commands['neg'] = Neg
commands['and'] = And
commands['or'] = Or
commands['not'] = Not

with open(sys.argv[1]) as infile:
    fname = sys.argv[1].split('/')[-1].split('.')[0]

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
                    command = commands[cmd](arg1, int(arg2))
                else:
                    command = commands[cmd]()

                writer.lines(command.asm(namespace=fname, position=length - 1))
                length += command.length()
