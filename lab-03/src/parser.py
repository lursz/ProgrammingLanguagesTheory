#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from src.lambda_program import TypedLambdaProgram
from src.sprdpl.parse import ParseResult
from src.sprdpl import parse
from src.term import *
from src.type import LambdaType, BaseType, ArrowType


class Index(dict):
    def __missing__(self, key):
        self[key] = len(self)
        return self[key]

    def to_list(self):
        result = ["" for _ in self]
        for k,v in self.items():
            result[v] = k
        return result


class TypedLambdaParser:

    def __init__(self):
        self.tokens = {
            'LAMBDA': r'\\[ \t\n]*',
            'DOT': r'\.[ \t\n]*',
            'ARROW': r'[ \t\n]*->[ \t\n]*',
            'TRUE': r'true',
            'FALSE': r'false',
            'ZERO': r'0',
            'PRED': r'pred[ \t\n]*',
            'SUCC': r'succ[ \t\n]*',
            'ISZERO': r'iszero[ \t\n]*',
            'IF': r'if[ \t\n]*',
            'THEN': r'[ \t\n]*then[ \t\n]*',
            'ELSE': r'[ \t\n]*else[ \t\n]*',
            'LPAR': r'\(',
            'RPAR': r'\)',
            'COLON': r'[ \t\n]*:[ \t\n]*',
            'SPACE':  r'[ \t\n]+',
            'IDENTIFIER': r'[a-zA-Z][\w]*',
        }

        def reduce_app(p: ParseResult) -> Term:
            if p[1] is None:
                return p[0]
            return TmApp(p[0].info, p[0], p[1][1])

        def reduce_par_app(p: ParseResult) -> Term:
            if p[3] is None:
                return p[1]
            return TmApp(p[1].info, p[1], p[3][1])

        def reduce_abs_app(p: ParseResult) -> Term:
            if p[1] is None:
                return p[0]
            return TmAbs(p[0].info, p[0].arg,  p[1][1], TmApp(p[0].info, p[0].body))

        def reduce_base_type(p: ParseResult) -> LambdaType:
            return BaseType.from_text(p[0])

        def reduce_type(p: ParseResult) -> LambdaType:
            if p[1] is None:
                return p[0]
            return ArrowType(p[0], p[1][1])

        def reduce_par_type(p: ParseResult) -> LambdaType:
            if p[3] is None:
                return p[1]
            return ArrowType(p[1], p[3][1])

        self.grammar = [
            ['term', 'zero', 'succ', 'pred', 'iszero', 'if', 'true', 'false'],
            ['term', ('variable term_p', reduce_app)],
            ['term', ('abstraction term_p', reduce_abs_app)],
            ['term', ('LPAR term RPAR term_p', reduce_par_app)],
            ['term_p', 'SPACE term'],
            ['term_p', '{}'],
            ['true', ('TRUE', lambda p: TmTrue(Info.from_sprdl_info(p.get_info(0))))],
            ['false', ('FALSE', lambda p: TmFalse(Info.from_sprdl_info(p.get_info(0))))],
            ['if',
             ('IF term THEN term ELSE term', lambda p: TmIf(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['zero', ('ZERO', lambda p: TmZero(Info.from_sprdl_info(p.get_info(0))))],
            ['succ', ('SUCC term', lambda p: TmSucc(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['pred', ('PRED term', lambda p: TmPred(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['iszero', ('ISZERO term', lambda p: TmIsZero(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['variable', ('IDENTIFIER', lambda p: TmNamedVar(Info.from_sprdl_info(p.get_info(0)), p[0]))],
            ['abstraction', ('LAMBDA IDENTIFIER COLON type DOT term', lambda p: TmAbs(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['type', ('base_type type_p', reduce_type)],
            ['type', ('LPAR type RPAR type_p', reduce_par_type)],
            ['base_type', ('IDENTIFIER', reduce_base_type)],
            ['type_p', 'ARROW type', '{}']
        ]

    def parse(self, input: str) -> TypedLambdaProgram:
        lexer = lex.Lexer(self.tokens)
        parser = parse.Parser(self.grammar, 'term')
        tokens = lexer.input(input)
        named_term = parser.parse(tokens)
        program = self._remove_names(named_term)
        return program

    def _remove_names(self, named_term: NamedTerm) -> TypedLambdaProgram:
        index = Index()
        context: list[int] = []
        term = self._replace_vars(named_term, index, context)
        return TypedLambdaProgram(term, index.to_list())

    def _replace_vars(self, named_term: NamedTerm, index: Index, context: list[str]) -> Term:
        match named_term:
            case TmNamedVar(info, id):
                if id in context:
                    return TmVar(info, context.index(id), len(context))
                else:
                    return TmVar(info, len(context) + index[id], len(context))
            case TmAbs(info, arg, arg_type, body):
                new_context = [arg] + context
                return TmAbs(info, arg, arg_type, self._replace_vars(body, index, new_context))
            case TmApp(info, fun, arg):
                return TmApp(info, self._replace_vars(fun, index, context), self._replace_vars(arg, index, context))
            case TmZero() | TmFalse() | TmTrue():
                return named_term
            case TmIf(info, cond_named, if_act_named, else_act_named):
                cond = self._replace_vars(cond_named, index, context)
                if_act = self._replace_vars(if_act_named, index, context)
                else_act = self._replace_vars(else_act_named, index, context)
                return TmIf(info, cond, if_act, else_act)
            case TmIsZero(info, arg):
                return TmIsZero(info, self._replace_vars(arg, index, context))
            case TmPred(info, arg):
                return TmPred(info, self._replace_vars(arg, index, context))
            case TmSucc(info, arg):
                return TmSucc(info, self._replace_vars(arg, index, context))