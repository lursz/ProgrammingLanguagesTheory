#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations

from typing import Optional

from src.term import Term, TmAbs, TmVar, TmApp, TmTrue, TmFalse, TmZero, TmSucc, TmIf, TmIsZero, Info, TmPred
from src.lambda_program import TypedLambdaProgram
from dataclasses import dataclass
from enum import Enum, auto
from src.type import LambdaType, BaseType, InvalidType, ArrowType


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

    def typecheck(self, program: TypedLambdaProgram) -> LambdaType:
        return self._typecheck(program.term, TypeContext.empty())

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

        def process_arg_type(term_type: LambdaType, first_version: LambdaType):
            match term_type:
                case BaseType():
                    return term_type
                case ArrowType(left_arr, right_arr):
                    processed_left = process_arg_type(left_arr, first_version)
                    processed_right = process_arg_type(right_arr, first_version)

                    return ArrowType(processed_left, processed_right)
                case _:
                    raise_type_error(LambdaTypeErrorType.InvalidType, first_version)

        # TODO:
        # Fill missing code based on the typeof function (TAPL book, p. 115).
        # Differences:
        # - TAPL handles only the Bool (BaseType.Bool), not the Nat type (BaseType.Nat)
        #   refer to the TAPL p. 93 for the Nat rules
        # - TAPL code doesn't handle "invalid type" (InvalidType), our parser doesn't validate type annotations
        #   just remember that ArrowType with InvalidType on any side is also invalid
        # - use raise_type_error to raise errors
        #   be sure you have handled all the error types from LambdaTypeErrorType

        match term:
            case TmTrue(_) | TmFalse(_):
                return BaseType.from_text("Bool")
            case TmZero(_):
                return BaseType.from_text("Nat")
            case TmIf(_, t1, t2, t3):
                t1_type = self._typecheck(t1, type_context)
                t2_type = self._typecheck(t2, type_context)
                t3_type = self._typecheck(t3, type_context)

                if t1_type != BaseType.from_text("Bool"):
                    raise_type_error(LambdaTypeErrorType.IfInvalidGuard, t1_type)

                if t2_type != t3_type:
                    raise_type_error(LambdaTypeErrorType.IfDivergentBranches, t2_type, t3_type)

                return t2_type
            case TmSucc(_, t):
                t_type = self._typecheck(t, type_context)

                if t_type == BaseType.from_text("Nat"):
                    return t_type
                else:
                    raise_type_error(LambdaTypeErrorType.UnnaturalArg, t_type)
            case TmPred(_, t):
                t_type = self._typecheck(t, type_context)

                if t_type == BaseType.from_text("Nat"):
                    return t_type
                else:
                    raise_type_error(LambdaTypeErrorType.UnnaturalArg, t_type)
            case TmIsZero(_, t):
                t_type = self._typecheck(t, type_context)

                if t_type == BaseType.from_text("Nat"):
                    return BaseType.from_text("Bool")
                else:
                    raise_type_error(LambdaTypeErrorType.UnnaturalArg, t_type)
            case TmVar(_, index, _):
                return type_context.type_of(index)
            case TmAbs(_, _, arg_type, body):
                arg_type_processed = process_arg_type(arg_type, arg_type)

                body_type = self._typecheck(body, type_context.extend_with_type(arg_type))

                new_type = ArrowType(arg_type_processed, body_type)
                return new_type
            case TmApp(_, t1, t2):
                t1_type = self._typecheck(t1, type_context)
                t2_type = self._typecheck(t2, type_context)

                match t1_type:
                    case ArrowType(left, right):
                        if t2_type != left:
                            raise_type_error(LambdaTypeErrorType.InvalidArgType, left, t2_type)
                        return right
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidFunType, t1_type)
            case _:
                raise_type_error(LambdaTypeErrorType.UnknownType)