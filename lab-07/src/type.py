#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias, Union

from src.sprdpl.lex import Info

'''
LambdaType unions all the possible types in our language 
'''
LambdaType : TypeAlias = Union['BaseType', 'ArrowType', 'InvalidType', 'RecordType', 'VariantType', 'ReferenceType']


@dataclass()
class TypeBuildingError(Exception):
    msg: str
    info: Info

    def __str__(self) -> str:
        return f"{self.msg} at {self.info}"


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
    Unit = "Unit"
    Top = "Top"

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


@dataclass(frozen=True)
class RecordType:
    """
        Basic record type.

        Attribute:
        ===============
        record_types: OrderedDict[str, LambdaType]
            this dictionary maps record labels to the corresponding types
    """
    records_types: OrderedDict[str, LambdaType]

    @staticmethod
    def from_raw_data(info: Info, raw_items: list[tuple(str, LambdaType) | LambdaType]) -> RecordType:
        items = []
        for (idx, ri) in enumerate(raw_items):
            match ri:
                case tuple():
                    items.append(ri)
                case _:
                    items.append((str(idx + 1), ri))

        labels = [i[0] for i in items]
        if len(labels) > len(set(labels)):
            raise TypeBuildingError("Parsed record type contains repeating labels", info)
        return RecordType(OrderedDict(items))

    def __str__(self) -> str:
        return "{" + ','.join([f"{l}: {t}" for l, t in self.records_types.items()]) + "}"


@dataclass(frozen=True)
class VariantType:
    """
        Basic variant type.

        Attribute:
        ===============
        variant_types: OrderedDict[str, LambdaType]
            this dictionary maps variant labels to the corresponding types
    """
    variants_types: OrderedDict[str, LambdaType]

    @staticmethod
    def from_raw_data(info: Info, items: list[tuple(str, LambdaType)]) -> VariantType:
        labels = [i[0] for i in items]
        if len(labels) > len(set(labels)):
            raise TypeBuildingError("Parsed variant type contains repeating labels", info)
        return VariantType(OrderedDict(items))

    def __str__(self) -> str:
        return "<" + ','.join([f"{l}: {t}" for l, t in self.variants_types.items()]) + ">"


@dataclass(frozen=True)
class ReferenceType:
    """
        Reference type.

        Attribute:
        ===============
        stored_type: LambdaType
            type of the referenced term
    """
    stored_type: LambdaType

    def __str__(self) -> str:
        return f"Ref {self.stored_type}"
