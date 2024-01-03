#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from abc import ABC, abstractmethod
from collections import OrderedDict
from copy import copy
from functools import partial

from src.lambda_program import TypedLambdaProgram
from src.term import Term, TmVar, TmAbs, TmLet, TmApp, TmZero, TmFalse, TmTrue, TmIf, TmIsZero, TmSucc, TmPred, \
    TmLetRec, TmFix, Info, DerivedTerm, UnexpandedTerm, TmRecord, TmProjection, TmTagging, TmCase


class Macro(ABC):
    '''
    Class representing a basic syntactic macro.

    Methods:
    ========
        expand(term: DerivedTerm) -> Term | None:
            takes a term and expands it, if it possible, returning new term
            if macro is not applicable, this method should return None
    '''
    @abstractmethod
    def expand(self, term: DerivedTerm) -> Term | None:
        pass


class LetRecMacro(Macro):

    def expand(self, term: DerivedTerm) -> Term | None:
        match term:
            case TmLetRec(fi, x, xt, f, b):
                result = TmLet(Info.dummy_info(), x, TmFix(Info.dummy_info(), TmAbs(Info.dummy_info(), 'x', xt, f)), b)
                return result
            case _:
                return None


class MacroSystem:
    '''
    This class is responsible for expanding derived terms.
    It allows to define macros that transform the program into a more basic form.

    Methods:
    ========
        expand(p: TypedLambdaProgram[UnexpandedTerm]) -> TypedLambdaProgram[Term]:
            translates given program to a form without derived terms
    '''
    def __init__(self, macros: None | list[Macro] = None):
        self.macros : list[Macro] = macros if macros is not None else [LetRecMacro()]

    def _expand_macros(self, term: UnexpandedTerm) -> Term:
        for macro in self.macros:
            expanded_term = macro.expand(term)
            if expanded_term is not None:
                return expanded_term
        return term

    def _expand_term(self, t: UnexpandedTerm) -> Term:
        def term_is_derived(t: UnexpandedTerm) -> bool:
            return isinstance(t, DerivedTerm.__origin__)

        match t:
            case t if term_is_derived(t):
                et = self._expand_macros(t)
                return self._expand_term(et)
            case TmVar() | TmZero() | TmFalse() | TmTrue():
                return copy(t)
            case TmAbs(fi, x, xt, t1):
                return TmAbs(fi, x, xt, self._expand_term(t1))
            case TmApp(fi, t1, t2):
                return TmApp(fi, self._expand_term(t1), self._expand_term(t2))
            case TmIf(fi, t1, t2, t3):
                return TmIf(fi, self._expand_term(t1), self._expand_term(t2), self._expand_term(t3))
            case TmIsZero(fi, t1):
                return TmIsZero(fi, self._expand_term(t1))
            case TmSucc(fi, t1):
                return TmSucc(fi, self._expand_term(t1))
            case TmPred(fi, t1):
                return TmPred(fi, self._expand_term(t1))
            case TmFix(f, t1):
                return TmFix(f, self._expand_term(t1))
            case TmLet(fi, x, rvalue, body):
                return TmLet(fi, x, self._expand_term(rvalue), self._expand_term(body))
            case TmRecord():
                expander = partial(self._expand_term)
                assert isinstance(t, TmRecord)
                return t.map_items(expander)
            case TmProjection(fi, rec, label):
                return TmProjection(fi, self._expand_term(rec), label)
            case TmTagging(fi, label, term, type):
                return TmTagging(fi, label, self._expand_term(term), type)
            case TmCase(fi, term, vars, branches):
                expanded_branches = []
                for label, branch in branches.items():
                    expanded_branches.append((label, self._expand_term(branch)))
                return TmCase(fi, self._expand_term(term), vars, OrderedDict(expanded_branches))

    def expand(self, p: TypedLambdaProgram[UnexpandedTerm]) -> TypedLambdaProgram[Term]:
        return TypedLambdaProgram(self._expand_term(p.term), p.name_context)
