#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations
from src.term import *
from dataclasses import dataclass
from enum import Enum, auto

class Rule(Enum):
    '''
    Enum representing various semantic rules.
    '''
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

@dataclass(frozen=True)
class Transition:
    '''
    Class representing state transitions
    
    Attributes:
    ----------
    old_state: Term
        previous state
    new_state: Term
        a new state
    rule: Rule
        which rule was used to make the transition
    witnesses: tuple[Transistion, ...]
        list of transition that were required to make this one happen 
    '''
    old_state: Term
    new_state: Term
    rule: Rule
    witnesses: tuple[Transition, ...] = tuple()

class NoRuleApplies(Exception):
    '''
    Exception to be thrown when the evaluation ends.
    '''
    pass

class ArithmeticSemantics:

    @staticmethod
    def single_step(state_before: Term) -> Transition:
        '''
            Function applying correct rule to the given term.
        '''

        def transition(new_state: Term, rule: Rule, witnesses: tuple[Transition, ...] = ()):
            '''
                Just a helper function to create transition objects.
            '''
            return Transition(state_before, new_state, rule, witnesses)

        match state_before:
            # TODO:
            # match cases according to the chapter 4 of the book, function eval1
            # main difference:
            # - instead of returning term you should return a transition object (using the transition function helper)
            # - each transition can also store results of the intermediate steps, i.e. if a rule requires another rule
            #   to match, it should store this transition in the "witnesses" tuple
            # transitions are later used to display a derivation tree
            case TmPred(_, TmZero()):
                return transition(TmZero(Info.dummy_info()), Rule.PredZero)
            case TmPred(_, TmSucc(_, n)):
                return transition(n, Rule.PredSucc)
            case TmIsZero(_, TmZero()):
                return transition(TmTrue(Info.dummy_info()), Rule.IsZeroZero)
            case TmIsZero(_, TmSucc()):
                return transition(TmFalse(Info.dummy_info()), Rule.IsZeroSucc)
            case TmIf(_, TmTrue(), t2, t3):
                return transition(t2, Rule.IfTrue)
            case TmIf(_, TmFalse(), t2, t3):
                return transition(t3, Rule.IfFalse)
            case TmIf(info, t1, t2, t3):
                t1_transformed = ArithmeticSemantics.single_step(t1)
                return transition(TmIf(info, t1_transformed.new_state, t2, t3), Rule.If, (t1_transformed,))
            case TmSucc(info, t):
                t_transformed = ArithmeticSemantics.single_step(t)
                return transition(TmSucc(info, t_transformed.new_state), Rule.Succ, (t_transformed,))
            case TmPred(info, t):
                t_transformed = ArithmeticSemantics.single_step(t)
                return transition(TmPred(info, t_transformed.new_state), Rule.Pred, (t_transformed,))
            case TmIsZero(info, t):
                t_transformed = ArithmeticSemantics.single_step(t)
                return transition(TmIsZero(info, t_transformed.new_state), Rule.IsZero, (t_transformed,))
            case _:
                raise NoRuleApplies()