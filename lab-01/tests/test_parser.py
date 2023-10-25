#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from unittest import TestCase

from src.parser import ArithmeticParser
from src.term import *


class TestArithmeticParser(TestCase):
    def test_parse(self):
        parser = ArithmeticParser()
        result = parser.parse("if true then pred 0 else if succ 0 then false else true")
        expected = TmIf(info=Info(lineno=1, column=0), condition=TmTrue(info=Info(lineno=1, column=3)), if_true=TmPred(info=Info(lineno=1, column=13), number=TmZero(info=Info(lineno=1, column=18))), if_else=TmIf(info=Info(lineno=1, column=25), condition=TmSucc(info=Info(lineno=1, column=28), number=TmZero(info=Info(lineno=1, column=33))), if_true=TmFalse(info=Info(lineno=1, column=40)), if_else=TmTrue(info=Info(lineno=1, column=51))))
        self.assertEqual(result, expected)


