#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy

from src.memory import Memory
from src.semantics.term_utils import term_substitute, term_is_val, term_is_numeric_val
from src.term import Term, TmAbs, TmVar, TmApp, TmTrue, TmFalse, TmZero, TmSucc, TmIf, TmIsZero, Info, TmPred, TmLet, \
    TmFix, TmRecord, TmProjection, TmTagging, TmCase, TmReference, TmDereference, TmAssignment, TmUnit, BaseTerm
from src.lambda_program import TypedLambdaProgram, LambdaProgramState
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
    RefV = auto()
    Ref = auto()
    DerefLoc = auto()
    Deref = auto()
    Assign = auto()
    Assign1 = auto()
    Assign2 = auto()

    def __str__(self):
        return f"E-{self.name}".replace('_', '')

    def __repr__(self):
        return f"EvalRule.{self.name}"


@dataclass(frozen=True)
class Transition:
    old_state: LambdaProgramState
    new_state: LambdaProgramState
    rule: EvalRule
    name_context: list[str]
    witnesses: tuple[Transition] = ()

    def __str__(self):
        return f"{self.old_state.pretty_str(self.name_context)} -> {self.new_state.pretty_str(self.name_context)}"


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

    def single_step(self, state_before: LambdaProgramState) -> Transition:
        """
             This static method performs a single step of computation.
             Based on the 'eval1' function from the TAPL p. 87

             :param state_before: a Lambda Calculus state
             :return: a transition applied according the Lambda Calculus semantics
        """

        def updated_state(update: Term | Memory | LambdaProgramState) -> LambdaProgramState:
            """
                Just a helper function to quickly update the state
                It will create a new state based on the old one and provided info.
            """
            match update:
                case BaseTerm():
                    return state_before.replace_term(update)
                case Memory():
                    return state_before.replace_memory(update)
                case LambdaProgramState():
                    return update

        def transition(update: Term | Memory | LambdaProgramState,
                       rule: EvalRule,
                       witnesses: tuple(Transition) = ()) -> Transition:
            """ Just a helper function to quickly create a transition """
            return Transition(state_before, updated_state(update), rule, self.name_context, witnesses)

        match state_before.term:
            case TmApp(_, TmAbs(_, _, _, function), arg) if term_is_val(arg):
                new_state = term_substitute(arg, function)
                return transition(new_state, EvalRule.AppAbs)
            case TmApp(fi, function, arg) if not term_is_val(function):
                witness = self.single_step(updated_state(function))
                new_state = witness.new_state.replace_term(TmApp(fi, witness.new_state.term, arg))
                return transition(new_state, EvalRule.App1, (witness,))
            case TmApp(fi, function, arg) if not term_is_val(arg):
                witness = self.single_step(updated_state(arg))
                new_state = witness.new_state.replace_term(TmApp(fi, function, witness.new_state.term))
                return transition(new_state, EvalRule.App2, (witness,))
            case TmIf(_, TmTrue(_), t2, _):
                return transition(t2, EvalRule.IfTrue)
            case TmIf(_, TmFalse(_), _, t3):
                return transition(t3, EvalRule.IfFalse)
            case TmIf(fi, t1, t2, t3):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term(TmIf(fi, witness.new_state.term, t2, t3))
                return transition(new_state, EvalRule.If, (witness,))
            case TmSucc(fi, t1):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term(TmSucc(fi, witness.new_state.term))
                return transition(new_state, EvalRule.Succ, (witness,))
            case TmPred(_, TmZero(_)):
                return transition(TmZero(Info.dummy_info()), EvalRule.PredZero)
            case TmPred(_, TmSucc(_, nv)) if term_is_numeric_val(nv):
                return transition(nv, EvalRule.PredSucc)
            case TmPred(fi, t1):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term(TmPred(fi, witness.new_state.term))
                return transition(new_state, EvalRule.Pred, (witness,))
            case TmIsZero(_, TmZero(_)):
                return transition(TmTrue(Info.dummy_info()), EvalRule.IsZeroZero)
            case TmIsZero(_, TmSucc(_, nv)) if term_is_numeric_val(nv):
                return transition(TmFalse(Info.dummy_info()), EvalRule.IsZeroSucc)
            case TmIsZero(fi, t1):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term(TmIsZero(fi, witness.new_state.term))
                return transition(new_state, EvalRule.IsZero, (witness,))
            case TmLet(_, _, rvalue, body) if term_is_val(rvalue):
                new_state = term_substitute(rvalue, body)
                return transition(new_state, EvalRule.LetV)
            case TmLet(fi, var, rterm, body):
                witness = self.single_step(updated_state(rterm))
                new_state = witness.new_state.replace_term(TmLet(fi, var, witness.new_state.term, body))
                return transition(new_state, EvalRule.Let, (witness,))
            case TmFix(_, TmAbs(_, x, xt, function)):
                y = TmFix(Info.dummy_info(), TmAbs(Info.dummy_info(), x, xt, function))
                new_term = term_substitute(y, function)
                return transition(new_term, EvalRule.FixBeta)
            case TmFix(fi, t1):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term((TmFix(fi, witness.new_state.term)))
                return transition(new_state, EvalRule.Fix, (witness,))
            case TmRecord(_, ts) as r if not term_is_val(r):
                l,t = next((l,t) for l,t in ts.items() if not term_is_val(t))
                witness = self.single_step(updated_state(t))
                assert isinstance(r, TmRecord)
                new_term = r.replace(l, witness.new_state.term)
                new_state = witness.new_state.replace_term(new_term)
                return transition(new_state, EvalRule.Rcd, (witness,))
            case TmProjection(_, t, l) if term_is_val(t):
                match t:
                    case TmRecord(_, rs):
                        return transition(rs[l], EvalRule.ProjRcd)
                    case _:
                        raise NoEvalRuleApplies(state_before)
            case TmProjection(fi, t, l):
                witness = self.single_step(updated_state(t))
                new_state = witness.new_state.replace_term(TmProjection(fi, witness.new_state.term, l))
                return transition(new_state, EvalRule.Proj, (witness,))
            case TmTagging(fi, l, t, tyT) if not term_is_val(t):
                witness = self.single_step(updated_state(t))
                new_state = witness.new_state.replace_term(TmTagging(fi, l, witness.new_state.term, tyT))
                return transition(new_state, EvalRule.Variant, (witness,))
            case TmCase(_, TmTagging(_, l, v), _, branches) if term_is_val(v):
                new_branch = term_substitute(v, branches[l])
                return transition(new_branch, EvalRule.CaseVariant)
            case TmCase(fi, t, vs, bs):
                witness = self.single_step(updated_state(t))
                new_state = witness.new_state.replace_term(TmCase(fi, witness.new_state.term, vs, bs))
                return transition(new_state, EvalRule.Case, (witness,))
            case TmReference(_, v) if term_is_val(v):
                new_memory, location = state_before.memory.put(v)
                new_state = LambdaProgramState(location, new_memory)
                return transition(new_state, EvalRule.RefV)
            case TmReference(fi, t):
                witness = self.single_step(updated_state(t))
                new_state = witness.new_state.replace_term(TmReference(fi, witness.new_state.term))
                return transition(new_state, EvalRule.Ref, (witness,))
            case TmDereference(_, v) if term_is_val(v):
                return transition(state_before.memory.dereference(v), EvalRule.DerefLoc)
            case TmDereference(fi, t):
                witness = self.single_step(updated_state(t))
                new_state = witness.new_state.replace_term(TmDereference(fi, witness.new_state.term))
                return transition(new_state, EvalRule.Deref, (witness,))
            case TmAssignment(_, v1, v2) if term_is_val(v1) and term_is_val(v2):
                new_memory = state_before.memory.replace(v1, v2)
                new_state = LambdaProgramState(TmUnit(Info.dummy_info()), new_memory)
                return transition(new_state, EvalRule.Assign)
            case TmAssignment(fi, t1, t2) if not term_is_val(t1):
                witness = self.single_step(updated_state(t1))
                new_state = witness.new_state.replace_term(TmAssignment(fi, witness.new_state.term, t2))
                return transition(new_state, EvalRule.Assign1, (witness,))
            case TmAssignment(fi, v1, t2):
                witness = self.single_step(updated_state(t2))
                new_state = witness.new_state.replace_term(TmAssignment(fi, v1, witness.new_state.term))
                return transition(new_state, EvalRule.Assign2, (witness,))
            case _:
                raise NoEvalRuleApplies(state_before)
