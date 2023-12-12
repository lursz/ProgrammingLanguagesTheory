#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from src.type import LambdaType, InvalidType, ArrowType


def type_is_invalid(t: LambdaType) -> bool:
    match t:
        case InvalidType():
            return True
        case ArrowType(left, right):
            return type_is_invalid(left) or type_is_invalid(right)
        case _:
            return False