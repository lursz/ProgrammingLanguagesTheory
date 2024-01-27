#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeVar, Generic

from src.memory import Memory
from src.term import Term, TmAbs, TmApp, TmVar, TmZero, TmFalse, TmTrue, TmIf, TmIsZero, TmPred, TmSucc, TmLet, TmFix, \
    UnexpandedTerm, TmLetRec, TmRecord, TmProjection, TmTagging, TmCase, TmUnit, TmStoreLocation, TmReference, \
    TmDereference, TmAssignment, TmSequence

T = TypeVar('T', Term, UnexpandedTerm)


@dataclass(frozen=True)
class LambdaProgramState(Generic[T]):
    """
    Represents a state of our abstract virtual machine.

    Attributes:
    ===========
    term: T
        current term left to be evaluated
    memory: Memory
        current memory contents

    Methods:
    ========
    replace_term(term: T) -> LambdaProgramState[T]
        creates a new state with a replaced term
    replace_memory(term: T) -> LambdaProgramState[T]
        creates a new state with a replaced memory
    pretty_str(name_context: list[str]) -> str:
        prints the current state in a pretty way given names of the free variables
    """
    term: T
    memory: Memory = Memory()

    def replace_term(self, term: T) -> LambdaProgramState[T]:
        return LambdaProgramState(term, self.memory)

    def replace_memory(self, memory: Memory) -> LambdaProgramState[T]:
        return LambdaProgramState(self.term, memory)

    def pretty_str(self, name_context: list[str]) -> str:
        def _pick_fresh_name(context: list[str], suggestion: str) -> tuple[list[str], str]:
            """
                This method generates new fresh name based on the suggestion and and list of already used names.

                :param context: already used variable names in the scope
                :param suggestion: suggested name
                :return: tuple containing new context and fresh name
            """
            fresh_name = suggestion
            while fresh_name in context:
                fresh_name = f"{fresh_name}'"
            new_context = [fresh_name] + context
            return new_context, fresh_name

        def _find_name(context: list[str], index: int) -> str:
            """
                This method finds a variable name based on the list of the used names.

                :param context: already used variable names in the scope
                :param index: index of a variable
                :return: name corresponding the the index
            """
            if index < len(context):
                return context[index]
            else:
                return name_context[index - len(context)]

        def _pretty_str(context: list[str], term: T) -> str:
            """
                This method prints the term with correct variable names.
                It's based on the "printtm" function from page 85 in the TAPL book.

                :param context: already used variable names in the scope
                :param term: term to be printed
                :return: pretty textual representation
            """
            match term:
                case TmAbs(_, arg, arg_type, body):
                    new_context, name = _pick_fresh_name(context, arg)
                    return f"(\\{name}:{arg_type}.{_pretty_str(new_context, body)})"
                case TmLet(_, var, rvalue, body):
                    new_context, name = _pick_fresh_name(context, var)
                    return f"(let {name} = {_pretty_str(context, rvalue)} in {_pretty_str(new_context, body)}"
                case TmApp(_, function, arg):
                    return f"({_pretty_str(context, function)} {_pretty_str(context, arg)})"
                case TmVar(_, index, ctx_length):
                    assert ctx_length == len(context), f"{index}: {ctx_length} != {len(context)}"
                    return _find_name(context, index)
                case TmZero() | TmFalse() | TmTrue() | TmUnit() | TmStoreLocation():
                    return str(term)
                case TmIf(_, cond, if_act, else_act):
                    pretty_cond = _pretty_str(context, cond)
                    pretty_if_act = _pretty_str(context, if_act)
                    pretty_else_act = _pretty_str(context, else_act)
                    return f"if {pretty_cond} then {pretty_if_act} else {pretty_else_act}"
                case TmIsZero(_, arg):
                    return f"iszero {_pretty_str(context, arg)}"
                case TmPred(_, arg):
                    return f"pred {_pretty_str(context, arg)}"
                case TmSucc(_, arg):
                    return f"succ {_pretty_str(context, arg)}"
                case TmFix(_, arg):
                    return f"fix {_pretty_str(context, arg)}"
                case TmLetRec(_, var, vartype, fun, body):
                    new_context, name = _pick_fresh_name(context, var)
                    return f"(letrec {name} : {vartype} = {_pretty_str(new_context, fun)} in {_pretty_str(new_context, body)}"
                case TmRecord(_, records):
                    return "{" + ", ".join([f"{l} = {_pretty_str(context, v)}" for l, v in records.items()]) + "}"
                case TmProjection(_, t, label):
                    return f"{t}.{label}"
                case TmTagging(_, label, term):
                    return f"<{label}:{_pretty_str(context, term)}>"
                case TmCase(_, term, vars, branches):
                    str_repr = f"case {_pretty_str(context, term)} of "
                    str_cases = []
                    for label, var in vars.items():
                        branch = branches[label]
                        new_context, name = _pick_fresh_name(context, var)
                        str_cases.append(f"<{label}={name}> => {_pretty_str(new_context, branch)}")
                    str_repr += " | ".join(str_cases)
                    return str_repr
                case TmReference(_, term):
                    return f"ref {_pretty_str(context, term)}"
                case TmDereference(_, term):
                    return f"!({_pretty_str(context, term)})"
                case TmAssignment(_, left, right):
                    return f"{_pretty_str(context, left)} := {_pretty_str(context, right)}"
                case TmSequence(_, head, tail):
                    return f"{head}; {tail}"

        empty_context: list[str] = []
        return f"({_pretty_str(empty_context, self.term)} | {self.memory})"


@dataclass(frozen=True)
class TypedLambdaProgram(Generic[T]):
    """
    Class representing a "program" written in the lambda calculus.

    Attributes:
        - state: LambdaCalculusState[T]
            Lambda calculus state
        - name_context: list[str]
            This list stores names of the free variables in order to print them in a pretty way :)
    """
    state: LambdaProgramState[T]
    name_context: list[str]

    def __str__(self) -> str:
        return self.state.pretty_str(self.name_context)


