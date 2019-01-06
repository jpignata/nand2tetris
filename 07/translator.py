import sys
import re
from collections import defaultdict


class Writer:
    def __init__(self, f):
        self.file = f

    def comment(self, line):
        self.file.write(f'// {line}\n')

    def lines(self, lines):
        self.file.write('\n'.join(lines))
        self.file.write('\n')


class Command:
    BASE_ADDRESS = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS',
                    'that': 'THAT'}
    POINTER = '@THIS', '@THAT'

    def __init__(self, arg1, arg2):
        pass

    def length(self):
        return len(self.asm())

    def compare(self, method, position):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                'D=M-D',
                f'@{position + 14}',
                f'D; J{method}',
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

    def operate(self, operator):
        return ('@SP',
                'AM=M-1',
                'D=M',
                '@SP',
                'AM=M-1',
                f'M=M{operator}D',
                '@SP',
                'M=M+1')


class Push(Command):
    def __init__(self, segment, index):
        self.segment = segment
        self.index = int(index)

    def asm(self, namespace='Default', position=None):
        statements = (f'@{self.index}',
                      'D=A')

        if self.segment in self.BASE_ADDRESS:
            statements += (f'@{self.BASE_ADDRESS[self.segment]}',
                           'A=M+D',
                           'D=M')
        elif self.segment == 'temp':
            statements += ('@R5',
                           'A=A+D',
                           'D=M')
        elif self.segment == 'pointer':
            statements += (self.POINTER[self.index],
                           'D=M')
        elif self.segment == 'static':
            statements += (f'@{namespace}.{self.index}',
                           'D=M')

        return statements + ('@SP',
                             'A=M',
                             'M=D',
                             '@SP',
                             'M=M+1')


class Pop(Command):
    def __init__(self, segment, index):
        self.segment = segment
        self.index = int(index)

    def asm(self, namespace='Default', position=None):
        statements = (f'@{self.index}',
                      'D=A')

        if self.segment in self.BASE_ADDRESS:
            statements += (f'@{self.BASE_ADDRESS[self.segment]}',
                           'D=M+D',
                           '@R13',
                           'M=D')
        elif self.segment == 'temp':
            statements += ('@R5',
                           'D=A+D',
                           '@R13',
                           'M=D')
        elif self.segment == 'pointer':
            statements += (self.POINTER[self.index],
                           'D=A',
                           '@R13',
                           'M=D')
        elif self.segment == 'static':
            statements += (f'@{namespace}.{self.index}',
                           'D=A',
                           '@R13',
                           'M=D')

        return statements + ('@SP',
                             'AM=M-1',
                             'D=M',
                             '@R13',
                             'A=M',
                             'M=D')


class EQ(Command):
    def asm(self, namespace=None, position=None):
        return self.compare('EQ', position)


class LT(Command):
    def asm(self, namespace=None, position=None):
        return self.compare('LT', position)


class GT(Command):
    def asm(self, namespace=None, position=None):
        return self.compare('GT', position)


class Add(Command):
    def asm(self, namespace=None, position=None):
        return self.operate('+')


class Sub(Command):
    def asm(self, namespace=None, position=None):
        return self.operate('-')


class Neg(Command):
    def asm(self, namespace=None, position=None):
        return ('@SP',
                'AM=M-1',
                'D=M',
                'M=M-D',
                'M=M-D',
                '@SP',
                'M=M+1')


class And(Command):
    def asm(self, namespace=None, position=None):
        return self.operate('&')


class Or(Command):
    def asm(self, namespace=None, position=None):
        return self.operate('|')


class Not(Command):
    def asm(self, namespace=None, position=None):
        return ('@SP',
                'AM=M-1',
                'M=-M',
                'M=M-1',
                '@SP',
                'M=M+1')


def null():
    def _(arg1, arg2):
        raise NotImplementedError

    return _


pattern = re.compile(r'(\w+) ?(\w+)? ?(\d+)?')
commands = defaultdict(null, {'push': Push, 'pop': Pop, 'eq': EQ, 'lt': LT,
                              'gt': GT, 'add': Add, 'sub': Sub, 'neg': Neg,
                              'and': And, 'or': Or, 'not': Not})
namespace = sys.argv[1].split('/')[-1].split('.')[0]
position = -1

with open(sys.argv[2], 'w') as outfile:
    writer = Writer(outfile)

    with open(sys.argv[1]) as infile:
        for line in [line.strip() for line in infile]:
            if len(line) > 0 and line[0] != '/':
                cmd, arg1, arg2 = pattern.match(line).group(1, 2, 3)
                command = commands[cmd](arg1, arg2)
                asm = command.asm(namespace=namespace, position=position)
                position += command.length()

                writer.comment(line)
                writer.lines(asm)
