#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from collections import OrderedDict
from copy import copy
from functools import partial
from typing import Callable

from src.term import TmVar, Term, TmAbs, TmPred, TmIsZero, TmApp, TmZero, TmFalse, TmTrue, TmIf, TmSucc, TmLet, \
    TmFix, TmUnit, TmRecord, TmProjection, TmTagging, TmCase, TmStoreLocation, TmReference, \
    TmDereference, TmAssignment, TmSequence


def term_is_numeric_val(t: Term) -> bool:
    match t:
        case TmZero():
            return True
        case TmSucc(_, v):
            return term_is_numeric_val(v)
        case _:
            return False


def term_is_val(t: Term) -> bool:
    '''
         This static method checks whether the term is a value.
         Based on the 'isval' function from the TAPL p. 87

         :param t: a Typed Lambda Calculus term
         :return: whether the term is a value
    '''
    if term_is_numeric_val(t):
        return True

    match t:
        case TmAbs():
            return True
        case TmTrue():
            return True
        case TmFalse():
            return True
        case TmUnit():
            return True
        case TmRecord(_, rs):
            return all([term_is_val(rv) for rv in rs.values()])
        case TmTagging(_, _, t):
            return term_is_val(t)
        case TmStoreLocation():
            return True
        case _:
            return False


def term_substitute(s: Term, t: Term) -> Term:
    '''
         This static makes a substitution in t. [var->s]t
         Based on the 'termSubstTop' function from the TAPL p. 87

         :param s: term that should replace the variable
         :param t: term containing variables to be replaced
         :return: new term create according to the substitution rules
    '''
    t1 = term_shift(1, s)
    t2 = term_substitute_step(0, t1, t)
    t3 = term_shift(-1, t2)

    return t3


def term_map_vars(t: Term, f: Callable[[TmVar, int], TmVar], c: int = 0) -> Term:
    match t:
        case TmVar():
            return f(t, c)
        case TmAbs(fi, x, xt, t1):
            return TmAbs(fi, x, xt, term_map_vars(t1, f, c + 1))
        case TmLet(fi, x, rvalue, body):
            return TmLet(fi, x, term_map_vars(rvalue, f, c), term_map_vars(body, f, c + 1))
        case TmApp(fi, t1, t2):
            return TmApp(fi, term_map_vars(t1, f, c), term_map_vars(t2, f, c))
        case TmZero() | TmFalse() | TmTrue() | TmUnit() | TmStoreLocation():
            return copy(t)
        case TmIf(fi, t1, t2, t3):
            return TmIf(fi, term_map_vars(t1, f, c), term_map_vars(t2, f, c), term_map_vars(t3, f, c))
        case TmIsZero(fi, t1):
            return TmIsZero(fi, term_map_vars(t1, f, c))
        case TmSucc(fi, t1):
            return TmSucc(fi, term_map_vars(t1, f, c))
        case TmPred(fi, t1):
            return TmPred(fi, term_map_vars(t1, f, c))
        case TmFix(fi, t1):
            return TmFix(fi, term_map_vars(t1, f, c))
        case TmRecord() as r:
            assert isinstance(r, TmRecord)
            mapper = partial(term_map_vars, f = f, c = c)
            return r.map_items(mapper)
        case TmProjection(fi, t, l):
            return TmProjection(fi, term_map_vars(t, f, c), l)
        case TmTagging(fi, l, t):
            return TmTagging(fi, l, term_map_vars(t, f, c))
        case TmCase(fi, t, vs, bs):
            mapped_term = term_map_vars(t, f, c)
            mapped_branches = [(l, term_map_vars(b, f, c + 1)) for l, b in bs.items()]
            return TmCase(fi, mapped_term, vs, OrderedDict(mapped_branches))
        case TmReference(fi, t1):
            return TmReference(fi, term_map_vars(t1, f, c))
        case TmDereference(fi, t1):
            return TmDereference(fi, term_map_vars(t1, f, c))
        case TmAssignment(fi, t1, t2):
            return TmAssignment(fi, term_map_vars(t1, f, c), term_map_vars(t2, f, c))
        case TmSequence(fi, t1, t2):
            return TmSequence(fi, term_map_vars(t1, f, c), term_map_vars(t2, f, c))


def term_shift(d: int, term: Term) -> Term:
    '''
         This static method shifts free variable indexes in the term.
         Based on the 'termShift' function from the TAPL p. 86

         :param d: how much the variables should be shifted
         :param term: Lambda Calculus term containing variables to be shifted
         :return: new term with shifted variables
    '''
    def map_var(t: TmVar, c: int) -> TmVar:
        if t.index >= c:
            return TmVar(t.info, t.index + d, t.context_length + d)
        else:
            return TmVar(t.info, t.index, t.context_length + d)

    return term_map_vars(term, map_var)


def term_substitute_step(j: int, s: Term, term: Term) -> Term:
    '''
         This static method substitutes variable with given index
         with a given term.
         Based on the 'termSubst' function from the TAPL p. 86

         :param j: index of the variable to be substituted
         :param s: term to be put at the variable place
         :param term: term containing variables to be substituted
         :return: new term with substituted variables
    '''

    def map_var(t: TmVar, c: int) -> TmVar:
        if t.index == j + c:
            return term_shift(c, s)
        else:
            return copy(t)

    return term_map_vars(term, map_var)
