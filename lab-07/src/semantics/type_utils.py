#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from src.type import LambdaType, InvalidType, ArrowType, RecordType, VariantType, ReferenceType


def type_is_invalid(t: LambdaType) -> bool:
    match t:
        case InvalidType():
            return True
        case ArrowType(left, right):
            return type_is_invalid(left) or type_is_invalid(right)
        case RecordType(rs):
            return any([type_is_invalid(t) for t in rs.values()])
        case VariantType(vs):
            return any([type_is_invalid(t) for t in vs.values()])
        case ReferenceType(t):
            return type_is_invalid(t)
        case _:
            return False