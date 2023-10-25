#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations
from dataclasses import dataclass
from src.sprdpl import lex

@dataclass(frozen=True)
class Info:
    lineno: int
    column: int

    @staticmethod
    def from_sprdl_info(info: lex.Info) -> Info:
        return Info(info.lineno, info.column)

    @staticmethod
    def dummy_info() -> Info:
        return Info(-1, -1)


@dataclass(frozen=True)
class Term:
    info: Info

    def is_numerical(self) -> bool:
        # DONE:
        # match cases according to the chapter 4 of the book, function isnumericval
        match self:
            case TmZero():
                return True
            case TmSucc(_, number):
                return number.is_numerical()
            case _:
                return False

    def is_val(self) -> bool:
        # !DONE:
        # match cases according to the chapter 4 of the book, function isval
        match self:
            case TmTrue(_):
                return True
            case TmFalse(_):
                return True
            case term if term.is_numerical():
                return True
            case _:
                return False

@dataclass(frozen=True)
class TmTrue(Term):
   def __str__(self) -> str:
       return "true"

@dataclass(frozen=True)
class TmFalse(Term):
    def __str__(self) -> str:
        return "false"

@dataclass(frozen=True)
class TmIf(Term):
    condition: Term
    if_true: Term
    if_else: Term

    def __str__(self) -> str:
        return f"if {self.condition} then {self.if_true} else {self.if_else}"

@dataclass(frozen=True)
class TmZero(Term):

    def __str__(self) -> str:
        return "0"


@dataclass(frozen=True)
class TmSucc(Term):
    number: Term

    def __str__(self) -> str:
        return f"succ {self.number}"

@dataclass(frozen=True)
class TmPred(Term):
    number: Term

    def __str__(self) -> str:
        return f"pred {self.number}"

@dataclass(frozen=True)
class TmIsZero(Term):
    number: Term

    def __str__(self) -> str:
        return f"iszero {self.number}"