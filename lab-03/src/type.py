#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias, Union

'''
LambdaType unions all the possible types in our language 
'''
LambdaType : TypeAlias = Union['BaseType', 'ArrowType', 'InvalidType']


class BaseType(Enum):
    """
    This enum contains all the basic types in our language.

    Static Methods:
        ===============
        from_text(text: str) -> BaseType | InvalidType
            creates a base type based on the textual representation
            if the textual representation doesn't correspond to any type,
            an InvalidType is produced
    """
    Nat = "Nat"
    Bool = "Bool"

    def __str__(self):
        return self.value

    @staticmethod
    def from_text(text: str) -> BaseType | InvalidType:
        for bt in BaseType:
            if bt.value == text:
                return bt
        return InvalidType(text)


@dataclass(frozen=True)
class InvalidType:
    """
    Parser is not responsible for handling types.
    When a strange type annotation gets parsed, it results in an invalid type.

    Attributes:
    ===========
    raw_representation: str
        how the related type annotation looks in the code
    """
    raw_representation : str

    def __str__(self):
        return f"{self.raw_representation}"

@dataclass(frozen=True)
class ArrowType:
    """
        Type constructed using an arrow (->).
        In other words it's a function type.

        Attribute:
        ===============
        left: LambdaType
            type of the term on the left side of the arrow (LEFT -> right)
        right: LambdaType
            type of the term on the right side of the arrow (left -> RIGHT)
    """
    left: LambdaType
    right: LambdaType

    def __str__(self):
        match self.left:
            case ArrowType():
                return f"({self.left}) -> {self.right}"
            case _:
                return f"{self.left} -> {self.right}"
