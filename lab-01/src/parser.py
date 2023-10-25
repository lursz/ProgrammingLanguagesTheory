#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from src.sprdpl import lex
from src.sprdpl import parse
from src.term import Info, TmTrue, TmFalse, TmIf, TmZero, TmSucc, TmPred, TmIsZero, Term


class ArithmeticParser:
    '''
    A basic parser for the language of "arithmetic"

    Methods:
    --------
    parse(input: str) -> Term
        returns a parsed code as a term
    '''

    def __init__(self):
        self.tokens = {
            'TRUE': r'true',
            'FALSE': r'false',
            'IF':  r'if',
            'THEN': r'then',
            'ELSE': r'else',
            'ZERO': r'0',
            'SUCC': r'succ',
            'PRED': r'pred',
            'ISZERO': r'iszero',
            'WHITESPACE': (r'[ \t\n]+', lambda t: None)
        }

        self.grammar = [
            ['term', 'true', 'false', 'if', 'zero', 'succ', 'pred', 'iszero'],
            ['true', ('TRUE', lambda p: TmTrue(Info.from_sprdl_info(p.get_info(0))))],
            ['false', ('FALSE', lambda p: TmFalse(Info.from_sprdl_info(p.get_info(0))))],
            ['if', ('IF term THEN term ELSE term', lambda p: TmIf(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['zero', ('ZERO', lambda p: TmZero(Info.from_sprdl_info(p.get_info(0))))],
            ['succ', ('SUCC term', lambda p: TmSucc(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['pred', ('PRED term', lambda p: TmPred(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['iszero', ('ISZERO term', lambda p: TmIsZero(Info.from_sprdl_info(p.get_info(0)), p[1]))]
        ]

    def parse(self, input: str) -> Term:
        lexer = lex.Lexer(self.tokens)
        parser = parse.Parser(self.grammar, 'term')
        tokens = lexer.input(input)
        return parser.parse(tokens)