#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

from src.sprdpl import lex
from src.type import LambdaType


@dataclass()
class TermBuildingError(Exception):
    msg: str
    info: lex.Info

    def __str__(self) -> str:
        return f"{self.msg} at {self.info}"


@dataclass(frozen=True, eq=True)
class Info:
    '''
    Class containing debug info about the terms.

    Attributes:
        - lineno: int
            line number, where the term has been found
        - column: int
            column number, where the term has been found

    Static Methods:
        - from_sprdl_info(info: lex.Info) -> Info:
            helper to build info based on the internal parser representation
        - dummy_info() -> Info:
            creates dummy info object
    '''
    lineno: int
    column: int

    @staticmethod
    def from_sprdl_info(info: lex.Info) -> Info:
        return Info(info.lineno, info.column)

    @staticmethod
    def dummy_info() -> Info:
        return Info(-1, -1)


@dataclass(frozen=True, eq=True)
class BaseTerm(ABC):
    '''
    Base abstract class for all the terms.

    Attributes:
        - info: Info
            contains debug info about the given term
    '''
    info: Info


@dataclass(frozen=True, eq=True)
class TmNamedVar(BaseTerm):
    '''
        Term related to the lambda calculus variables.
        Used only during the parsing, later we remove the name and replace it with index.

        Attributes:
            - id: str
                variable identifier
    '''
    id: str

    def __str__(self) -> str:
        return self.id


@dataclass(frozen=True, eq=True)
class TmVar(BaseTerm):
    '''
        Term related to the lambda calculus variables.
        Uses the de Bruijn nameless representation.

        Attributes
        ----------
        index: int
            de Bruijn index of the variable
        context_length: int
            how "deep" is the variable situated
            useful for debug purposes
    '''
    index: int
    context_length: int

    def __str__(self) -> str:
        return f"var<{self.index}>"


V = TypeVar('V', TmVar, TmNamedVar)
T = TypeVar('T', bound= 'BaseTerm')


@dataclass(frozen=True, eq=True)
class TmAbs(BaseTerm, Generic[T]):
    '''
        Term related to the lambda calculus abstraction.

        Attributes:
            - arg: str
                name of the bound variable
                used to print the term in a pretty way
            - arg_type: Type
                type of the argument
            - body: Term
                body of the binder — just a term

    '''
    arg: str
    arg_type: LambdaType
    body: T

    def __str__(self) -> str:
        return f"(\{self.arg}:{self.arg_type}.{self.body})"


@dataclass(frozen=True, eq=True)
class TmApp(BaseTerm, Generic[T]):
    '''
        Term related to the lambda calculus beta-reduction.

        Attributes:
            - function: Term
                function applied on the argument
            - arg: Term
                The argument that will be used to substitute variables.
    '''
    function: T
    arg: T

    def _print_template(self) -> str:
        return "({} {})"

    def __str__(self) -> str:
        return self._print_template().format(self.function, self.arg)


@dataclass(frozen=True, eq=True)
class TmTrue(BaseTerm):
    def __str__(self) -> str:
        return "true"


@dataclass(frozen=True, eq=True)
class TmFalse(BaseTerm):
    def __str__(self) -> str:
        return "false"


@dataclass(frozen=True, eq=True)
class TmIf(BaseTerm, Generic[T]):
    condition: T
    if_true: T
    if_else: T

    @staticmethod
    def _print_template() -> str:
        return "if {} then {} else {}"

    def __str__(self) -> str:
        return TmIf._print_template().format(self.condition, self.if_true, self.if_else)


@dataclass(frozen=True, eq=True)
class TmZero(BaseTerm):

    def __str__(self) -> str:
        return "0"


@dataclass(frozen=True, eq=True)
class TmUnit(BaseTerm):

    def __str__(self) -> str:
        return "unit"


@dataclass(frozen=True, eq=True)
class TmSucc(BaseTerm, Generic[T]):
    number: T

    def __str__(self) -> str:
        return f"succ {self.number}"


@dataclass(frozen=True, eq=True)
class TmPred(BaseTerm, Generic[T]):
    number: T

    def __str__(self) -> str:
        return f"pred {self.number}"


@dataclass(frozen=True, eq=True)
class TmIsZero(BaseTerm, Generic[T]):
    number: T

    def __str__(self) -> str:
        return f"iszero {self.number}"


@dataclass(frozen=True, eq=True)
class TmLet(BaseTerm, Generic[T]):
    var: str
    rvalue: T
    body: T

    def __str__(self) -> str:
        return f"let {self.var} = {self.rvalue} in {self.body}"


@dataclass(frozen=True, eq=True)
class TmFix(BaseTerm, Generic[T]):
    arg: T

    def __str__(self) -> str:
        return f"fix {self.arg}"


@dataclass(frozen=True, eq=True)
class TmLetRec(BaseTerm, Generic[T]):
    var: str
    type: LambdaType
    function: T
    body: T

    def __str__(self) -> str:
        return f"letrec {self.var} : {self.type} = {self.function} in {self.body}"


U = TypeVar('U', bound='BaseType')


@dataclass(frozen=True, eq=True)
class TmRecord(BaseTerm, Generic[T]):
    '''
    Class representing a record.

    Attributes:
    ===========
        records: OrderedDict[str, T]
            this dictionary maps record labels to the corresponding terms

    Methods:
    ========
        replace(label: str, term: T) -> TmRecord[T]:
            replaces a field at the given label in the record with the term
        map_items(f: Callable[[T], U]) -> TmRecord[U]:
            returns a new record with all fields transformed by the given function

    Static methods:
    ===============
        from_raw_data(info: lex.Info, raw_items: list[tuple(str, NamedTerm) | NamedTerm]) -> TmRecord[NamedTerm]:
            creates a new record form the raw parsed data
    '''
    records: OrderedDict[str, T]

    def replace(self, label: str, term: T) -> TmRecord[T]:
        new_records = deepcopy(self.records)
        new_records[label] = term
        return TmRecord(self.info, new_records)

    def map_items(self, f: Callable[[T], U]) -> TmRecord[U]:
        return TmRecord(
            self.info,
            OrderedDict([(l, f(t)) for l, t in self.records.items()])
        )

    @staticmethod
    def from_raw_data(info: lex.Info, raw_items: list[tuple(str, NamedTerm) | NamedTerm]) -> TmRecord[NamedTerm]:
        items = []
        for (idx, ri) in enumerate(raw_items):
            match ri:
                case tuple():
                    items.append(ri)
                case _:
                    items.append((str(idx + 1), ri))

        labels = [i[0] for i in items]
        if len(labels) > len(set(labels)):
            raise TermBuildingError("Parsed record contains repeating labels", info)
        return TmRecord(Info.from_sprdl_info(info), OrderedDict(items))

    def __str__(self) -> str:
        return "{" + ','.join([f"{l} = {i}" for l,i in self.records.items()]) + "}"


@dataclass(frozen=True, eq=True)
class TmProjection(BaseTerm, Generic[T]):
    '''
    Class representing a projection.

    Attributes:
    ===========
        record: T
            a term (that supposed in the end to be a record) that is being projected
        label: str
            name of the field used in the projection
    '''
    record: T
    label: str

    def __str__(self) -> str:
        return f"{self.record}.{self.label}"


@dataclass(frozen=True, eq=True)
class TmTagging(BaseTerm, Generic[T]):
    '''
    Class representing a tagged term.

    Attributes:
    ===========
        label: str
            name pointing at which variant type does the term belongs to
        term: T
            tagged ("packed") term
    '''
    label: str
    term: T

    def __str__(self) -> str:
        return f"<{self.label}={self.term}>"



@dataclass(frozen=True, eq=True)
class TmCase(BaseTerm, Generic[T]):
    '''
    Class representing a "case" expresssion.

    Attributes:
    ===========
        term: T
            term we want to to "unpack"
        vars: OrderedDict[str, str]
            this dictionary maps labels to the corresponding variable names
        branches: OrderedDict[str, T]
            this dictionary maps labels to the corresponding branches


    Static methods:
    ===============
        from_raw_data(info: lex.Info, term: NamedTerm, raw_cases: list[tuple(str, str, NamedTerm)]) -> TmCase[NamedTerm]:
            this method build a case term from the raw parsed data
    '''

    term: T
    vars: OrderedDict[str, str]
    branches: OrderedDict[str, T]

    def __str__(self) -> str:
        return f"case {self.term} of " + " | ".join([f"<{l}={v}> => {self.branches[l]}" for l, v in self.vars.items()])

    @staticmethod
    def from_raw_data(info: lex.Info, term: NamedTerm, raw_cases: list[tuple(str, str, NamedTerm)]) \
            -> TmCase[NamedTerm]:
        vars = [(l,v) for (l,v,_) in raw_cases]
        branches = [(l,t) for (l,_,t) in raw_cases]
        labels = [l for l,_ in branches]
        if len(labels) > len(set(labels)):
            raise TermBuildingError("Parsed case term contains repeating labels", info)
        return TmCase(Info.from_sprdl_info(info), term, OrderedDict(vars), OrderedDict(branches))


@dataclass(frozen=True, eq=True)
class TmReference(BaseTerm, Generic[T]):
    arg: T

    def __str__(self) -> str:
        return f"ref {self.arg}"


@dataclass(frozen=True, eq=True)
class TmDereference(BaseTerm, Generic[T]):
    arg: T

    def __str__(self) -> str:
        return f"!{self.arg}"


@dataclass(frozen=True, eq=True)
class TmAssignment(BaseTerm, Generic[T]):
    left_side: T
    right_side: T

    def __str__(self) -> str:
        return f"{self.left_side} := {self.right_side}"


@dataclass(frozen=True, eq=True)
class TmStoreLocation(BaseTerm):
    address: int

    def __str__(self) -> str:
        return f"@{self.address}"


@dataclass(frozen=True, eq=True)
class TmSequence(BaseTerm, Generic[T]):
    first: T
    rest: T

    def __str__(self) -> str:
        return f"{self.first}; {self.rest}"



'''
Types used in the project:
- Term: is a de Bruijn term
- NamedTerm: is a named naive representation. Used only in the parsing phase.
- DerivedTerm: term that should be expanded by the macro system
'''
AtomicTerm = TmTrue | TmFalse | TmZero | TmUnit
NamedTerm = TmNamedVar | AtomicTerm \
    | TmAbs['NamedTerm'] | TmApp['NamedTerm'] \
    | TmPred['NamedTerm'] | TmSucc['NamedTerm'] | TmIsZero['NamedTerm'] \
    | TmIf['NamedTerm'] \
    | TmFix['NamedTerm'], TmLetRec['NamedTerm'] \
    | TmRecord['NamedTerm'] | TmProjection['NamedTerm'] \
    | TmTagging['NamedTerm'] | TmCase['NamedTerm'] \
    | TmSequence['NamedTerm'] \
    | TmReference['NamedTerm'] | TmDereference['NamedTerm'] | TmAssignment['NamedTerm']

Term = TmVar | AtomicTerm \
    | TmAbs['Term'] | TmApp['Term'] \
    | TmPred['Term'] | TmSucc['Term'] | TmIsZero['Term'] \
    | TmIf['Term'] \
    | TmFix['Term'] \
    | TmRecord['Term'] | TmProjection['Term'] \
    | TmTagging['Term'] | TmCase['Term'] \
    | TmReference['Term'] | TmDereference['Term'] | TmAssignment['Term'] | TmStoreLocation

DerivedTerm = TmLetRec[Term] | TmSequence[Term]
UnexpandedTerm = Term | DerivedTerm





