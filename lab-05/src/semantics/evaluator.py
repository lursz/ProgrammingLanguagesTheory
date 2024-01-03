#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy

from src.semantics.term_utils import term_substitute, term_is_val, term_is_numeric_val
from src.term import Term, TmAbs, TmVar, TmApp, TmTrue, TmFalse, TmZero, TmSucc, TmIf, TmIsZero, Info, TmPred, TmLet, \
    TmFix, TmRecord, TmProjection, TmTagging, TmCase
from src.lambda_program import TypedLambdaProgram
from dataclasses import dataclass
from enum import Enum, auto


class EvalRule(Enum):
    App1 = 0
    App2 = auto()
    AppAbs = auto()
    IfTrue = auto()
    IfFalse = auto()
    If = auto()
    Succ = auto()
    PredZero = auto()
    PredSucc = auto()
    Pred = auto()
    IsZeroZero = auto()
    IsZeroSucc = auto()
    IsZero = auto()
    LetV = auto()
    Let = auto()
    Fix = auto()
    FixBeta = auto()
    Rcd = auto()
    Proj = auto()
    ProjRcd = auto()
    Variant = auto()
    Case = auto()
    CaseVariant = auto()

    def __str__(self):
        return f"E-{self.name}".replace('_', '')

    def __repr__(self):
        return f"EvalRule.{self.name}"


@dataclass(frozen=True)
class Transition:
    old_state: TypedLambdaProgram
    new_state: TypedLambdaProgram
    rule: EvalRule
    witnesses: tuple[Transition] = ()

    def __str__(self):
        return f"{self.old_state.__str__()} -> {self.new_state.__str__()}"


class NoEvalRuleApplies(Exception):
    def __init__(self, state: Term):
        self.state = state

    def __str__(self):
        return f"No evaluation rule applies to state: {self.state}"


class TypedLambdaEvaluator:
    '''
        Class representing semantics of the untyped lambda calculus.

        Attributes:
            - name_context: list[str]
                This list stores names of the free variables in order to print them in a pretty way :)
    '''
    def __init__(self, name_context: list[str]):
        self.name_context = name_context


    def single_step(self, state_before: Term) -> Transition:
        '''
             This static method checks whether the term is a value.
             Based on the 'eval1' function from the TAPL p. 87

             :param state_before: a Lambda Calculus term
             :return: a transition applied according the Lambda Calculus semantics
        '''

        def transition(new_state: Term, rule: EvalRule, witnesses: tuple(Transition) = ()) -> Transition:
            ''' Just a helper function to quickly create a transition'''
            return Transition(TypedLambdaProgram(state_before, self.name_context), TypedLambdaProgram(new_state, self.name_context), rule, witnesses)

        # TODO: Fill missing code for the:
        # - TmRecord, TmProjection (refer to TPL, p. 129)
        #   tip. TmRecord may have some useful methods
        # - TmTagging, TmCase (refer to TPL, p. 136)
        #
        # tip. check `term_utils.py` and fix the `term_is_val` function
        match state_before:
            case TmProjection(_, TmRecord() as record, label) if term_is_val(record):
                return transition(record.records[label], EvalRule.ProjRcd)
            case TmProjection(fi, t1, label):
                witness = self.single_step(t1)
                return transition(TmProjection(fi, witness.new_state.term, label), EvalRule.Proj, (witness,))
            case TmRecord(_, fields) as record if not term_is_val(record):
                for label, term in fields.items():
                    if not term_is_val(term):
                        subterm_transition = self.single_step(term)
                        reduced_subterm = subterm_transition.new_state.term
                        reduced_record = record.replace(label, reduced_subterm)
                        return transition(reduced_record, EvalRule.Rcd, (subterm_transition,))
                return transition(state_before, EvalRule.Rcd)
            case TmCase(_, TmTagging() as tagging, _, branches) if term_is_val(tagging):
                branch = branches[tagging.label]
                new_state = term_substitute(tagging.term, branch)
                return transition(new_state, EvalRule.CaseVariant)
            case TmCase(fi, t1, x, branches):
                witness = self.single_step(t1)
                return transition(TmCase(fi, witness.new_state.term, x, branches), EvalRule.Case, (witness,))
            case TmTagging(info, label, t, tagging_type) if not term_is_val(t):
                witness = self.single_step(t)
                new_t = witness.new_state.term
                return transition(TmTagging(info, label, new_t, tagging_type), EvalRule.Variant, (witness,))
            case TmApp(_, TmAbs(_, _, _, function), arg) if term_is_val(arg):
                new_state = term_substitute(arg, function)
                return transition(new_state, EvalRule.AppAbs)
            case TmApp(fi, function, arg) if not term_is_val(function):
                witness = self.single_step(function)
                return transition(TmApp(fi, witness.new_state.term, arg), EvalRule.App1, (witness,))
            case TmApp(fi, function, arg) if not term_is_val(arg):
                witness = self.single_step(arg)
                return transition(TmApp(fi, function, witness.new_state.term), EvalRule.App2, (witness,))
            case TmIf(_, TmTrue(_), t2, _):
                return transition(t2, EvalRule.IfTrue)
            case TmIf(_, TmFalse(_), _, t3):
                return transition(t3, EvalRule.IfFalse)
            case TmIf(fi, t1, t2, t3):
                witness = self.single_step(t1)
                return transition(TmIf(fi, witness.new_state.term, t2, t3), EvalRule.If, (witness,))
            case TmSucc(fi, t1):
                witness = self.single_step(t1)
                return transition(TmSucc(fi, witness.new_state.term), EvalRule.Succ, (witness,))
            case TmPred(_, TmZero(_)):
                return transition(TmZero(Info.dummy_info()), EvalRule.PredZero)
            case TmPred(_, TmSucc(_, nv)) if term_is_numeric_val(nv):
                return transition(nv, EvalRule.PredSucc)
            case TmPred(fi, t1):
                witness = self.single_step(t1)
                return transition(TmPred(fi, witness.new_state.term), EvalRule.Pred, (witness,))
            case TmIsZero(_, TmZero(_)):
                return transition(TmTrue(Info.dummy_info()), EvalRule.IsZeroZero)
            case TmIsZero(_, TmSucc(_, nv)) if term_is_numeric_val(nv):
                return transition(TmFalse(Info.dummy_info()), EvalRule.IsZeroSucc)
            case TmIsZero(fi, t1):
                witness = self.single_step(t1)
                return transition(TmIsZero(fi, witness.new_state.term), EvalRule.IsZero, (witness,))
            case TmLet(_, _, rvalue, body) if term_is_val(rvalue):
                new_state = term_substitute(rvalue, body)
                return transition(new_state, EvalRule.LetV)
            case TmLet(fi, var, rterm, body):
                witness = self.single_step(rterm)
                return transition(TmLet(fi, var, witness.new_state.term, body), EvalRule.Let, (witness,))
            case TmFix(_, TmAbs(_, x, xt, function)):
                y = TmFix(Info.dummy_info(), TmAbs(Info.dummy_info(), x, xt, function))
                new_state = term_substitute(y, function)
                return transition(new_state, EvalRule.FixBeta)
            case TmFix(fi, t1) if not term_is_val(t1):
                witness = self.single_step(t1)
                return transition(TmFix(fi, witness.new_state.term), EvalRule.Fix, (witness,))
            case _:
                raise NoEvalRuleApplies(state_before)
