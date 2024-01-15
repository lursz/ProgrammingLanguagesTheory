#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations

from collections import OrderedDict
from typing import Optional

from src.semantics.type_utils import type_is_invalid
from src.term import Term, TmAbs, TmVar, TmApp, TmTrue, TmFalse, TmZero, TmSucc, TmIf, TmIsZero, Info, TmPred, TmLet, \
    TmFix, TmUnit, TmRecord, TmProjection, TmTagging, TmCase, TmStoreLocation, TmReference, TmDereference, TmAssignment
from src.lambda_program import TypedLambdaProgram
from dataclasses import dataclass
from enum import Enum, auto
from src.type import LambdaType, BaseType, InvalidType, ArrowType, RecordType, VariantType, ReferenceType


class LambdaTypeErrorType(Enum):
    """
    This enum represent all possible type errors, the typechecker can detect.
    Each type is accompanied with a message template, that can be used to print the error, e.g.
        LambdaTypeErrorType.IfDivergentBranches.value.format("type1", "type2")
    would produce an error message corresponding to IfDivergentBranches.
    The strings also self-document the enum :)
    """
    IfInvalidGuard = "guard of conditional is not a boolean, got '{}'"
    IfDivergentBranches = "branches of conditional have different types: '{}' and '{}'"
    UnnaturalArg = "argument is not a natural number, got '{}'"
    UnknownType = "a variable has no known type"
    InvalidType = "program uses an invalid type: '{}'"
    InvalidArgType = "function expected type '{}', got '{}'"
    InvalidFunType = "expected arrow type, got '{}'"
    InvalidRecFunType = "recursive function is expected to have same types as input and output, got '{}' and '{}'"
    InvalidProjArgType = "projection operator expects a record as its input, got {}"
    InvalidProjLabel = "projection uses label {} that doesn't belong to the argument with labels {}"
    InvalidVariant = "expected type to be a variant, instead it is {}"
    TagInvalidLabel = "type ascribed to a tagged term is missing label {}, instead it contains labels {}"
    TagInvalidType = "type ascribed to a tagged term has inconsistent type — expected {}, got {}"
    CaseInvalidLabels = "case term should exactly cover the variant's labels, it doesn't — it covers {}, should cover {}"
    CaseDivergentBranches = "branches of case term have divergent types: {}"
    IllegalTerm = "the term '{}' should not appear in the static context"
    InvalidMemoryAccess = "tried to access memory address {}, it is not a ref type"
    IncompatibleAssignment = "tried to store type '{}' in memory type '{}'"


@dataclass
class LambdaTypeError(Exception):
    """
        A type error class. Nothing fancy,

        Attributes:
        ===========
        msg: str
            a message explaining the error
        term: Term
            the mistyped term
        type_context: TypeContext
            context associated with the error
        error_type: LambdaTypeErrorType
            type of the error
    """
    msg: str
    term: Term
    type_context: TypeContext
    error_type: LambdaTypeErrorType

    def __str__(self):
        return f"[Type Error] {self.msg}\n" \
               f"- program: {self.term}\n" \
               f"- type context: {self.type_context}\n" \
               f"- position: {self.term.info}"


@dataclass(frozen=True)
class TypeContext:
    """
        A typing context, contains info about types of the bound variables.

        Attributes:
        ===========
        _context: List[LambdaType]
            list of types corresponding to the de Bruijn indices

        Static Methods:
        ===============
        empty() -> TypeContext:
            create an empty context

        Methods:
        ========
        type_of(index: int) -> Optional[LambdaType]
            returns type of the variable with a given de Bruijn index
            if the variable is free, the result is None
        extend_with_type(type: LambdaType) -> TypeContext:
            creates a new context with a new type binding
    """
    _context: list[LambdaType]

    @staticmethod
    def empty() -> TypeContext:
        return TypeContext([])

    def type_of(self, index: int) -> Optional[LambdaType]:
        if index < len(self._context):
            return self._context[index]
        return None

    def extend_with_type(self, type: LambdaType) -> TypeContext:
        return TypeContext([type] + self._context)

    def __str__(self) -> str:
        return f"{[str(t) for t in self._context]}"


class TypedLambdaTypechecker:
    '''
        A type-checker for the Typed Lambda Calculus (with Nat and Bool types).

        Methods:
            - typecheck(program: TypedLambdaProgram) -> LambdaType
                returns type returned by the given lambda program
                in case of type error, raises LambdaTypeError
    '''
    def typecheck(self, program: TypedLambdaProgram[Term]) -> LambdaType:
        return self._typecheck(program.state.term, TypeContext.empty())

    def _typecheck(self, term: Term, type_context: TypeContext) -> LambdaType:
        """
        Given a type context, returns a type of a term.
        In case of an error, raises LambdaTypeError

        :param term: a typed lambda calculus term destined to be type-checked
        :param type_context: a type context (contains type info about the bound variables)
        :return: type of the term
        """

        def raise_type_error(error_type: LambdaTypeErrorType, *msg_args) -> None:
            """
            Helper to raise a type error based on its type.

            :param error_type: type of the raised
            :param msg_args: values used to fill format string associated to the error
            """
            error_msg = error_type.value.format(*msg_args)
            raise LambdaTypeError(error_msg, term, type_context, error_type)

        # DONE: fill missing rules for:
        # - TmStoreLocation, which shouldn't occur in the static (pre-runtime) context (LambdaTypeErrorType.IllegalTerm)
        # - TmReference
        # - TmDereference, possible error LambdaTypeErrorType.InvalidMemoryAccess
        # - TmAssignment, possible error LambdaTypeErrorType.InvalidMemoryAccess, LambdaTypeErrorType.IncompatibleAssignment
        #   tip. all rules are in TAPL, p. 167
        #   tip 2. you can ignore memory typing, as in the static (pre-runtime) context it's always empty
        match term:
            case TmStoreLocation():
                raise_type_error(LambdaTypeErrorType.IllegalTerm, term)
            case TmReference(_, t1):
                tyT1 = self._typecheck(t1, type_context)
                return ReferenceType(tyT1)
            case TmDereference(_, t1):
                tyT1 = self._typecheck(t1, type_context)
                match tyT1:
                    case ReferenceType(tyT11):
                        return tyT11
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidMemoryAccess, tyT1)
            case TmAssignment(_, t1, t2):
                tyT1 = self._typecheck(t1, type_context)
                tyT2 = self._typecheck(t2, type_context)
                match tyT1:
                    case ReferenceType(tyT11):
                        if tyT11 == tyT2:
                            return BaseType.Unit
                        else:
                            raise_type_error(LambdaTypeErrorType.IncompatibleAssignment, tyT2, tyT1)
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidMemoryAccess, tyT1)
            case TmFalse() | TmTrue():
                return BaseType.Bool
            case TmIf(_, t1, t2, t3):
                tyT1 = self._typecheck(t1, type_context)
                if tyT1 == BaseType.Bool:
                    tyT2 = self._typecheck(t2, type_context)
                    tyT3 = self._typecheck(t3, type_context)
                    if tyT2 == tyT3:
                        return tyT2
                    else:
                        raise_type_error(LambdaTypeErrorType.IfDivergentBranches, tyT2, tyT3)
                else:
                    raise_type_error(LambdaTypeErrorType.IfInvalidGuard, tyT1)
            case TmZero():
                return BaseType.Nat
            case TmUnit():
                return BaseType.Unit
            case TmSucc(_, t1) | TmPred(_, t1) | TmIsZero(_, t1):
                tyT1 = self._typecheck(t1, type_context)
                if tyT1 == BaseType.Nat:
                    match term:
                        case TmIsZero():
                            return BaseType.Bool
                        case _:
                            return BaseType.Nat
                else:
                    raise_type_error(LambdaTypeErrorType.UnnaturalArg, tyT1)
            case TmVar(_, index, _):
                ty = type_context.type_of(index)
                if ty is not None:
                    return ty
                else:
                    raise_type_error(LambdaTypeErrorType.UnknownType)
            case TmAbs(_, _, tyT1, t2):
                if type_is_invalid(tyT1):
                    raise_type_error(LambdaTypeErrorType.InvalidType, tyT1)
                else:
                    new_type_context = type_context.extend_with_type(tyT1)
                    tyT2 = self._typecheck(t2, new_type_context)
                    return ArrowType(tyT1, tyT2)
            case TmApp(_, t1, t2):
                tyT1 = self._typecheck(t1, type_context)
                tyT2 = self._typecheck(t2, type_context)
                match tyT1:
                    case ArrowType(tyT11, tyT12):
                        if tyT11 == tyT2:
                            return tyT12
                        else:
                            raise_type_error(LambdaTypeErrorType.InvalidArgType, tyT11, tyT2)
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidFunType, tyT1)
            case TmLet(_, _, t1, t2):
                tyT1 = self._typecheck(t1, type_context)
                new_context = type_context.extend_with_type(tyT1)
                return self._typecheck(t2, new_context)
            case TmFix(_, t1):
                tyT1 = self._typecheck(t1, type_context)
                match tyT1:
                    case ArrowType(tyT11, tyT12):
                        if tyT11 == tyT12:
                            return tyT11
                        else:
                            raise_type_error(LambdaTypeErrorType.InvalidRecFunType, tyT11, tyT12)
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidFunType, tyT1)
            case TmRecord():
                raise NotImplementedError("Hidden to prolong the lab-5 deadline")
            case TmProjection():
                raise NotImplementedError("Hidden to prolong the lab-5 deadline")
            case TmTagging():
                raise NotImplementedError("Hidden to prolong the lab-5 deadline")
            case TmCase():
                raise NotImplementedError("Hidden to prolong the lab-5 deadline")
