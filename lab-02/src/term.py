#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from src.sprdpl import lex

@dataclass(frozen=True)
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

@dataclass(frozen=True)
class BaseTerm(ABC):
    '''
    Base abstract class for all the terms.

    Attributes:
        - info: Info
            contains debug info about the given term
    '''
    info: Info

@dataclass(frozen=True)
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

@dataclass(frozen=True)
class TmVar(BaseTerm):
    '''
        Term related to the lambda calculus variables.
        Uses the de Bruijn nameless representation.

        Attributes:
            - index: int
                de Bruijn index of the variable
            - context_length: int
                how "deep" is the variable situated
                useful for debug purposes
    '''
    index: int
    context_length: int

    def __str__(self) -> str:
       return f"{self.index}"


@dataclass(frozen=True)
class TmAbs(BaseTerm):
    '''
        Term related to the lambda calculus abstraction.

        Attributes:
            - arg: str
                name of the bound variable
                used to print the term in a pretty way
            - body: Term
                body of the binder — just a term
    '''
    arg: str
    body: Term

    def __str__(self) -> str:
        return f"(\{self.arg}.{self.body})"


@dataclass(frozen=True)
class TmApp(BaseTerm):
    '''
        Term related to the lambda calculus beta-reduction.

        Attributes:
            - function: Term
                function applied on the argument
            - arg: Term
                The argument that will be used to substitute variables.
    '''
    function: Term
    arg: Term

    def __str__(self) -> str:
        return f"({self.function} {self.arg})"

'''
Types used in the project:
- Term: is a de Bruijn term
- NamedTerm: is a named naive representation. Used only in the parsing phase.
'''
Term = TmVar | TmApp | TmAbs
NamedTerm = TmNamedVar | TmApp | TmAbs