#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from __future__ import annotations

from collections import OrderedDict
from functools import reduce
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
    InvalidArgType = "function expected subtype of '{}', got '{}'"
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

        # DONE: update rules for:
        # - TmIf and TmCase, so instead of DivergentBranches error they return the join type (TAPL, p. 220)
        match term:
            case TmFalse() | TmTrue():
                return BaseType.Bool
            case TmIf(_, t1, t2, t3):
                tyT1 = self._typecheck(t1, type_context)
                if tyT1 == BaseType.Bool:
                    tyT2 = self._typecheck(t2, type_context)
                    tyT3 = self._typecheck(t3, type_context)
                    # DONE: change lines below
                    # if tyT2 == tyT3:
                    #     return tyT2
                    # else:
                    #     raise_type_error(LambdaTypeErrorType.IfDivergentBranches, tyT2, tyT3)
                    return self._join(tyT2, tyT3)
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
                        # TODO: read the line below and understand it. 
                        #       Don't change anything, just appreciate ;)
                        if self._is_subtype(tyT2, tyT11):
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
            case TmRecord(_, ts):
                return RecordType(OrderedDict([(l, self._typecheck(t, type_context)) for l,t in ts.items()]))
            case TmProjection(_, t1, l):
                tyT1 = self._typecheck(t1, type_context)
                match tyT1:
                    case RecordType(ts):
                        if l in ts:
                            return ts[l]
                        else:
                            raise_type_error(LambdaTypeErrorType.InvalidProjLabel, l, list(ts.keys()))
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidProjArgType, tyT1)
            case TmTagging(_, l, t1):
                tyT1 = self._typecheck(t1, type_context)
                return VariantType(OrderedDict([(l, tyT1)]))
            case TmCase(_, t1, vars, branches):
                tyT1 = self._typecheck(t1, type_context)
                match tyT1:
                    case VariantType(vs):
                        v_labels = list(vs.keys())
                        c_labels = list(vars.keys())
                        if set(v_labels) != set(c_labels):
                            raise_type_error(LambdaTypeErrorType.CaseInvalidLabels, c_labels, v_labels)
                        branch_types = []
                        for label, branch in branches.items():
                            branch_type_context = type_context.extend_with_type(vs[label])
                            branch_types.append(self._typecheck(branch, branch_type_context))
                        #TODO: Change lines below
                        # if len(set(branch_types)) > 1:
                        #     raise_type_error(LambdaTypeErrorType.CaseDivergentBranches, branch_types)
                        # return branch_types[0]
                        return reduce(self._join, branch_types)
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidVariant, tyT1)
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
                    case ReferenceType():
                        assert isinstance(tyT1, ReferenceType)
                        if tyT1.stored_type != tyT2:
                            raise_type_error(LambdaTypeErrorType.IncompatibleAssignment, tyT2, tyT1)
                        return BaseType.Unit
                    case _:
                        raise_type_error(LambdaTypeErrorType.InvalidMemoryAccess, tyT1)

    def _is_subtype(self, sub_type: LambdaType, super_type: LambdaType) -> bool:
        # DONE: this method should check whether the `sub_type` is a subtype of `super_type`
        # cases to consider:
        # 1) they are the same types
        # 2) super_type is a Top type (TAPL, p. 212)
        # 3) sub_type and super_type are Arrows
        # 4) sub_type and super_type are Records
        # 5) sub_type and super_type are Variants
        # tip. in cases 3-5 please use the prepared methods: _is_subtype_arrow, _is_subtype_record, _is_subtype_variant
        if sub_type == super_type:
            return True
        if super_type == BaseType.Top:
            return True
        match (sub_type, super_type):
            case (ArrowType(sub_left, sub_right), ArrowType(super_left, super_right)):
                return self._is_subtype_arrow(sub_left, sub_right, super_left, super_right)
            case (RecordType(sub_cases), RecordType(super_cases)):
                return self._is_subtype_record(sub_cases, super_cases)
            case (VariantType(sub_cases), VariantType(super_cases)):
                return self._is_subtype_variant(sub_cases, super_cases)
            case _:
                return False


    def _is_subtype_arrow(self, sub_left: LambdaType, sub_right: LambdaType,
                          super_left: LambdaType, super_right: LambdaType) -> bool:
        # DONE: check if `sub_left` -> `sub_right` is subtype of `super_left` -> `super_right`
        #       tip. TAPL, p. 212 (SA-Arrow)
        return self._is_subtype(super_left, sub_left) and self._is_subtype(sub_right, super_right)

    def _is_subtype_record(self, sub_cases: OrderedDict[str, LambdaType],
                           super_cases: OrderedDict[str, LambdaType]) -> bool:
        # DONE: check if Record type with fields `sub_cases` is subtype of Record with fields `super_cases`
        #       tip. TAPL, p. 212 (SA-RCD)
        for label, inner_type in super_cases.items():
            if label not in sub_cases:
                return False
            if not self._is_subtype(sub_cases[label], inner_type):
                return False
        return True

    def _is_subtype_variant(self, sub_cases: OrderedDict[str, LambdaType],
                            super_cases: OrderedDict[str, LambdaType]) -> bool:
        # DONE: check if Varant type with cases `sub_variants` is subtype of Variant with cases `super_variants`
        #       tip 1. it's very similar to records TAPL, p. 212 (SA-RCD)
        #       tip 2. the differences are described in TAPL, p. 197
        for label, inner_type in sub_cases.items():
            if label not in super_cases:
                return False
            if not self._is_subtype(inner_type, super_cases[label]):
                return False
        return True

    def _join(self, left: LambdaType, right: LambdaType) -> LambdaType:
        # DONE: find join type ('\/' - TAPL, p. 219) of tho given types
        #       (join type ~ the smallest supertype of the types)
        # cases:
        #   1. the types may be the same
        #   2. one may be a subtype of another
        #   3. Arrows
        #   4. Records
        #   5. Variants
        #   6. in the worst case (no structural shared supertype) — return Top
        #   in cases 3-5. use dedicated methods _join_arrows, _join_records, _join_variants
        if left == right:
            return left
        if self._is_subtype(left, right):
            return right
        if self._is_subtype(right, left):
            return left
        match (left, right):
            case (ArrowType(left_l, left_r), ArrowType(right_l, right_r)):
                return self._join_arrows(left_l, left_r, right_l, right_r)
            case (RecordType(left_fields), RecordType(right_fields)):
                return self._join_records(left_fields, right_fields)
            case (VariantType(left_cases), VariantType(right_cases)):
                return self._join_variants(left_cases, right_cases)
            case _:
                return BaseType.Top

    def _join_arrows(self, left_l: LambdaType, left_r: LambdaType,
                     right_l: LambdaType, right_r: LambdaType) -> LambdaType:
        # DONE: find join type of two arrows: `left_l` -> `left_r` and `right_l` -> `right_r`
        #       tips.
        #       - the result is `left_l` /\ `right_l` -> `left_r` \/ `right_r`
        #           where /\ is a meet, \/ is a join
        #       - if there is no meet for the args, return Top
        args_meet = self._meet(left_l, right_l)
        if args_meet is None:
            return BaseType.Top
        values_join = self._join(left_r, right_r)
        return ArrowType(args_meet, values_join)

    def _join_records(self, left_fields: OrderedDict[str, LambdaType],
                      right_fields: OrderedDict[str, LambdaType]) -> RecordType:
        # DONE: find join type of two records with fields `left_records` and `right_records`
        #       tips.
        #       - the result should contain only labels shared by both records
        #       - the type of the shared label should be a join type of its types in the original records
        left_labels = set(left_fields.keys())
        right_labels = set(right_fields.keys())

        shared_labels = left_labels.intersection(right_labels)

        result_fields = OrderedDict()
        for label in shared_labels:
            result_fields[label] = self._join(left_fields[label], right_fields[label])

        return RecordType(result_fields)

    def _join_variants(self, left_cases: OrderedDict[str, LambdaType],
                       right_cases: OrderedDict[str, LambdaType]) -> VariantType:
        # DONE: find join type of two variants with cases `left_cases` and `right_cases`
        #       tips.
        #       - the result should contain all labels from all the cases
        #       - the type of the shared label should be a join type of its types in the original cases
        left_labels = set(left_cases.keys())
        right_labels = set(right_cases.keys())

        result_labels = left_labels.union(right_labels)

        result_cases = OrderedDict()
        for label in result_labels:
            if label in left_cases and label in right_cases:
                result_cases[label] = self._join(left_cases[label], right_cases[label])
            elif label in left_cases:
                result_cases[label] = left_cases[label]
            else:
                result_cases[label] = right_cases[label]

        return VariantType(result_cases)

    def _meet(self, left: LambdaType, right: LambdaType) -> LambdaType | None:
        # DONE: find meet type ('/\' - TAPL, p. 219) of tho given types
        #       (meet type ~ the biggest subtype of the types)
        # cases:
        #   1. the types may be the same
        #   2. one may be a subtype of another
        #   3. Arrows
        #   4. Records
        #   5. Variants
        #   6. in the worst case (no structural shared subtype) — return None
        #   in cases 3-5. use dedicated methods _meet_arrows, _meet_records, _meet_variants
        if left == right:
            return left
        if self._is_subtype(left, right):
            return left
        if self._is_subtype(right, left):
            return right
        match (left, right):
            case (ArrowType(left_l, left_r), ArrowType(right_l, right_r)):
                return self._meet_arrows(left_l, left_r, right_l, right_r)
            case (RecordType(left_fields), RecordType(right_fields)):
                return self._meet_records(left_fields, right_fields)
            case (VariantType(left_cases), VariantType(right_cases)):
                return self._meet_variants(left_cases, right_cases)
            case _:
                return None

    def _meet_arrows(self, left_l: LambdaType, left_r: LambdaType,
                     right_l: LambdaType, right_r: LambdaType) -> ArrowType | None:
        # DONE: find meet type of two arrows: `left_l` -> `left_r` and `right_l` -> `right_r`
        #       tips.
        #       - the result is `left_l` \/ `right_l` -> `left_r` /\ `right_r`
        #           where /\ is a meet, \/ is a join
        #       - if there is no meet for the results, return None
        results_meet = self._meet(left_r, right_r)
        if results_meet is None:
            return None
        args_join = self._join(left_l, right_l)
        return ArrowType(args_join, results_meet)

    def _meet_records(self, left_fields: OrderedDict[str, LambdaType],
                      right_fields: OrderedDict[str, LambdaType]) -> RecordType | None:
        # DONE: find meet type of two records with fields `left_fields` and `right_fields`
        #       tips.
        #       - the result should contain all labels from all the cases
        #       - the type of the shared label should be a meet type of its types in the original fields
        #           * if there is no such a meet, return None
        left_labels = set(left_fields.keys())
        right_labels = set(right_fields.keys())

        result_labels = left_labels.union(right_labels)

        result_fields = OrderedDict()
        for label in result_labels:
            if label in left_fields and label in right_fields:
                result_fields[label] = self._meet(left_fields[label], right_fields[label])
                if result_fields[label] is None:
                    return None
            elif label in left_fields:
                result_fields[label] = left_fields[label]
            else:
                result_fields[label] = right_fields[label]

        return RecordType(result_fields)

    def _meet_variants(self, left_cases: OrderedDict[str, LambdaType],
                       right_cases: OrderedDict[str, LambdaType]) -> VariantType | None:
        # DONE: find meet type of two variants with cases `left_cases` and `right_cases`
        #       tips.
        #       - the result should contain only labels shared by both variants
        #       - the type of the shared label should be a meet type of its types in the original cases
        #           * if there is no such meet type, return None
        left_labels = set(left_cases.keys())
        right_labels = set(right_cases.keys())

        result_labels = left_labels.intersection(right_labels)

        result_cases = OrderedDict()
        for label in result_labels:
            result_cases[label] = self._meet(left_cases[label], right_cases[label])
            if result_cases[label] is None:
                return None

        return VariantType(result_cases)
