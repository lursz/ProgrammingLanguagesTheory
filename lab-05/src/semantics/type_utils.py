#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from src.type import LambdaType, InvalidType, ArrowType, RecordType, VariantType


def type_is_invalid(t: LambdaType) -> bool:
    # TODO:
    # You should check here whether RecordType and VariantType are valid
    match t:
        case InvalidType():
            return True
        case ArrowType(left, right):
            return type_is_invalid(left) or type_is_invalid(right)
        case RecordType(internal_types):
            return any(map(type_is_invalid, internal_types.values()))
        case VariantType(internal_types):
            return any(map(type_is_invalid, internal_types.values()))
        case _:
            return False
