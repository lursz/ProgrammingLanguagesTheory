#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from enum import Enum, auto

from src.sprdpl.parse import ParseResult
from src.sprdpl import parse
from src.term import *
from src.type import LambdaType, BaseType, ArrowType, RecordType, VariantType, ReferenceType


class TermConnector(Enum):
    APP = auto()
    PROJ = auto()
    SEQ = auto()
    ASSIGN = auto()


class TypedLambdaParser:

    def __init__(self):
        self.tokens = {
            'COMMENT': (r'#[^\n]*\n', lambda t: None),
            'LAMBDA': r'\\[ \t\n]*',
            'DOT': r'\.',
            'ARROW': r'[ \t\n]*->[ \t\n]*',
            'DARROW': r'[ \t\n]*=>[ \t\n]*',
            'CASE': r'case [ \t\n]*',
            'OF': r'[ \t\n]*of[ \t\n]*',
            'PIPE': r'[ \t\n]*\|[ \t\n]*',
            'TRUE': r'true',
            'FALSE': r'false',
            'UNIT': r'unit',
            'EXCLAMATION': r'!',
            'REF': r'ref[ \t\n]*',
            'REF_CAP' : r'Ref[ \t\n]*',
            'COLONEQ': r'[ \t\n]*:=[ \t\n]*',
            'AS': r'[ \t\n]as[ \t\n]*',
            'PRED': r'pred[ \t\n]*',
            'SUCC': r'succ[ \t\n]*',
            'ISZERO': r'iszero[ \t\n]*',
            'IF': r'if[ \t\n]*',
            'THEN': r'[ \t\n]*then[ \t\n]*',
            'ELSE': r'[ \t\n]*else[ \t\n]*',
            'LETREC': r'[ \t\n]*letrec[ \t\n]*',
            'LET': r'[ \t\n]*let[ \t\n]*',
            'IN': r'[ \t\n]*in[ \t\n]*',
            'FIX': r'[ \t\n]*fix[ \t\n]*',
            'EQ': r"[ \t\n]*=[ \t\n]*",
            'LPAR': r'\([ \t\n]*',
            'RPAR': r'[ \t\n]*\)',
            'LANGLE': r'<[ \t\n]*',
            'RANGLE': r'[ \t\n]*>',
            'LBRACE': r'\{[ \t\n]*',
            'RBRACE': r'[ \t\n]*\}',
            'SEMICOLON': r"[ \t\n]*;[ \t\n]*",
            'COMMA': r',[ \t\n]*',
            'COLON': r'[ \t\n]*:[ \t\n]*',
            'SPACE':  r'[ \t\n]+',
            'IDENTIFIER': r'[a-zA-Z_][\w]*',
            'ZERO': r'0',
            'POS_INTEGER': r'[1-9][\d]*'
        }

        def reduce_term(p: ParseResult) -> Term:
            if p[1] is None:
                return p[0]
            match p[1][0]:
                case TermConnector.APP:
                    return TmApp(p[0].info, p[0], p[1][1])
                case TermConnector.PROJ:
                    return TmProjection(p[0].info, p[0], p[1][1])
                case TermConnector.SEQ:
                    return TmSequence(p[0].info, p[0], p[1][1])
                case TermConnector.ASSIGN:
                    return TmAssignment(p[0].info, p[0], p[1][1])
                case _:
                    assert False

        def reduce_par_term(p: ParseResult) -> Term:
            return reduce_term([p[1], p[3]])

        def reduce_abs_term(p: ParseResult) -> Term:
            t = p[0]
            assert isinstance(t, TmAbs)
            if p[1] is None:
                return p[0]
            match p[1][0]:
                case TermConnector.APP:
                    return TmAbs(t.info, t.arg, t.arg_type, TmApp(p[0].info, t.body, p[1][1]))
                case TermConnector.PROJ:
                    return TmAbs(t.info, t.arg, t.arg_type, TmProjection(p[0].info, t.body, p[1][1]))
                case TermConnector.ASSIGN:
                    return TmAbs(t.info, t.arg, t.arg_type, TmAssignment(p[0].info, t.body, p[1][1]))
                case TermConnector.SEQ:
                    return TmAbs(t.info, t.arg, t.arg_type, TmSequence(p[0].info, t.body, p[1][1]))

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
            ['atomic_term', 'zero', 'unit', 'succ', 'pred', 'iszero', 'fix', 'if', 'true', 'false', 'variable', 'let', \
                            'letrec', 'record', 'tagging', 'case', 'ref', 'deref'],
            ['term', ('atomic_term term_p', reduce_term)],
            ['term', ('abstraction term_p', reduce_abs_term)],
            ['term', ('LPAR term RPAR term_p', reduce_par_term)],
            ['term_p', ('DOT record_label', lambda p: (TermConnector.PROJ, p[1]))],
            ['term_p', ('SPACE term', lambda p: (TermConnector.APP, p[1]))],
            ['term_p', ('SEMICOLON term', lambda p: (TermConnector.SEQ, p[1]))],
            ['term_p', ('COLONEQ term', lambda p: (TermConnector.ASSIGN, p[1]))],
            ['term_p', '{}'],
            ['true', ('TRUE', lambda p: TmTrue(Info.from_sprdl_info(p.get_info(0))))],
            ['false', ('FALSE', lambda p: TmFalse(Info.from_sprdl_info(p.get_info(0))))],
            ['if',
             ('IF term THEN term ELSE term', lambda p: TmIf(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['zero', ('ZERO', lambda p: TmZero(Info.from_sprdl_info(p.get_info(0))))],
            ['unit', ('UNIT', lambda p: TmUnit(Info.from_sprdl_info(p.get_info(0))))],
            ['succ', ('SUCC term', lambda p: TmSucc(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['pred', ('PRED term', lambda p: TmPred(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['iszero', ('ISZERO term', lambda p: TmIsZero(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['variable', ('IDENTIFIER', lambda p: TmNamedVar(Info.from_sprdl_info(p.get_info(0)), p[0]))],
            ['abstraction', ('LAMBDA IDENTIFIER COLON type INSIDE term', lambda p: TmAbs(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['INSIDE', 'DOT SPACE', 'DOT'],
            ['let', ('LET IDENTIFIER EQ term IN term', lambda p: TmLet(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5]))],
            ['letrec', ('LETREC IDENTIFIER COLON type EQ term IN term', lambda p: TmLetRec(Info.from_sprdl_info(p.get_info(0)), p[1], p[3], p[5], p[7]))],
            ['fix', ('FIX term', lambda p: TmFix(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['record', ('LBRACE record_item next_record_item* RBRACE', lambda p: TmRecord.from_raw_data(
                p.get_info(0),
                [p[1]] + p[2]
            ))],
            ['record_item', ('record_label EQ term', lambda p: (p[0], p[2]))],
            ['record_item', 'term'],
            ['next_record_item', ('COMMA record_item', lambda p: p[1])],
            ['record_label', 'IDENTIFIER', 'ZERO', 'POS_INTEGER'],
            ['tagging', ('tagged_term', lambda p: TmTagging(p[0][0], p[0][1], p[0][2]))],
            ['tagged_term', ('LANGLE IDENTIFIER EQ term RANGLE', lambda p: (Info.from_sprdl_info(p.get_info(0)), p[1], p[3]))],
            ['case', ('CASE term OF case_option next_case_option*', lambda p: TmCase.from_raw_data(
                p.get_info(0),
                p[1],
                [p[3]] + p[4]
            ))],
            ['case_option', ('tagged_var DARROW term', lambda p: (p[0][0], p[0][1], p[2]))],
            ['next_case_option', ('PIPE case_option', lambda p: p[1])],
            ['tagged_var', ('LANGLE IDENTIFIER EQ IDENTIFIER RANGLE', lambda p: (p[1], p[3]))],
            ['ref', ('REF term', lambda p: TmReference(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['deref', ('EXCLAMATION term', lambda p: TmDereference(Info.from_sprdl_info(p.get_info(0)), p[1]))],
            ['atomic_type', 'base_type', 'record_type', 'variant_type', 'ref_type'],
            ['type', ('atomic_type type_p', reduce_type)],
            ['type', ('LPAR type RPAR type_p', reduce_par_type)],
            ['base_type', ('IDENTIFIER', reduce_base_type)],
            ['record_type', ('LBRACE record_item_type next_record_item_type* RBRACE', lambda p: RecordType.from_raw_data(
                p.get_info(0),
                [p[1]] + p[2]
            ))],
            ['record_item_type', ('record_label COLON type', lambda p: (p[0], p[2]))],
            ['record_item_type', 'type'],
            ['next_record_item_type', ('COMMA record_item_type', lambda p: p[1])],
            ['variant_type', ('LANGLE variant_component next_variant_component* RANGLE', lambda p: VariantType.from_raw_data(
                p.get_info(0),
                [p[1]] + p[2]
            ))],
            ['variant_component', ('IDENTIFIER COLON type', lambda p: (p[0], p[2]))],
            ['next_variant_component', ('COMMA variant_component', lambda p: p[1])],
            ['ref_type', ('REF_CAP type', lambda p: ReferenceType(p[1]))],
            ['type_p', 'ARROW type', '{}']
        ]

    def parse(self, input: str) -> NamedTerm:
        lexer = lex.Lexer(self.tokens)
        parser = parse.Parser(self.grammar, 'term')
        tokens = lexer.input(input)
        named_term = parser.parse(tokens)
        return named_term
