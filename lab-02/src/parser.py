#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from src.lambda_program import LambdaProgram
from src.sprdpl.parse import ParseResult
from src.sprdpl import parse
from src.term import *

class Index(dict):
    def __missing__(self, key):
        self[key] = len(self)
        return self[key]

    def to_list(self):
        result = ["" for _ in self]
        for k,v in self.items():
            result[v] = k
        return result

class LambdaParser:

    def __init__(self):
        self.tokens = {
            'LAMBDA': r'\\',
            'DOT': r'\.[ \t\n]*',
            'IDENTIFIER': r'[a-zA-Z][\w]*',
            'LPAR': r'\(',
            'RPAR': r'\)',
            'SPACE':  r'[ \t\n]+'
        }

        def reduce_app(p: ParseResult) -> TmApp:
            if p[1] is None:
                return p[0]
            return TmApp(p[0].info, p[0], p[1][1])

        def reduce_par_app(p: ParseResult) -> TmApp:
            if p[3] is None:
                return p[1]
            return TmApp(p[1].info, p[1], p[3][1])

        def reduce_abs_app(p: ParseResult) -> TmAbs:
            if p[1] is None:
                return p[0]
            return TmAbs(p[0].info, p[0].arg, TmApp(p[0].info, p[0].body, p[1][1]))

        self.grammar = [
            ['term', ('variable term_p', reduce_app)],
            ['term', ('abstraction term_p', reduce_abs_app)],
            ['term', ('LPAR term RPAR term_p', reduce_par_app)],
            ['term_p', ('SPACE term')],
            ['term_p', '{}'],
            ['variable', ('IDENTIFIER', lambda p: TmNamedVar(p.get_info(0), p[0]))],
            ['abstraction', ('LAMBDA IDENTIFIER DOT term', lambda p: TmAbs(p.get_info(0), p[1], p[3]))],
        ]

    def parse(self, input: str) -> LambdaProgram:
        lexer = lex.Lexer(self.tokens)
        parser = parse.Parser(self.grammar, 'term')
        tokens = lexer.input(input)
        named_term = parser.parse(tokens)
        program = self._remove_names(named_term)
        return program

    def _remove_names(self, named_term: BaseTerm) -> LambdaProgram:
        index = Index()
        context: list[str] = []
        term = self._replace_vars(named_term, index, context)
        return LambdaProgram(term, index.to_list())

    def _replace_vars(self, named_term: BaseTerm, index: Index, context: list[str]) -> Term:
        match named_term:
            case TmNamedVar(info, id):
                if id in context:
                    return TmVar(info, context.index(id), len(context))
                else:
                    return TmVar(info, len(context) + index[id], len(context))
            case TmAbs(info, arg, body):
                new_context = [arg] + context
                return TmAbs(info, arg, self._replace_vars(body, index, new_context))
            case TmApp(info, fun, arg):
                return TmApp(info, self._replace_vars(fun, index, context), self._replace_vars(arg, index, context))