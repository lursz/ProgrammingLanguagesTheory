from unittest import TestCase
from parameterized import parameterized

from src.term import *

class TestTerm(TestCase):
    @parameterized.expand([
        (TmSucc(Info.dummy_info(), TmZero(Info.dummy_info())), True),
        (TmZero(Info.dummy_info()), True),
        (TmPred(Info.dummy_info(), TmZero(Info.dummy_info())), False),
        (TmSucc(Info.dummy_info(), TmTrue(Info.dummy_info())), False),
        (TmFalse(Info.dummy_info()), False),
        (TmIf(Info.dummy_info(), TmTrue(Info.dummy_info()), TmTrue(Info.dummy_info()), TmTrue(Info.dummy_info())),
         False),
        (TmIsZero(Info.dummy_info(), TmZero(Info.dummy_info())), False)
    ])
    def test_is_numerical(self, term: Term, expected: bool):
        self.assertEqual(term.is_numerical(), expected, f"{term} should be classified as a numerical value" if expected else f"{term} shouldn't be classified a numerical value")

    @parameterized.expand([
        (TmSucc(Info.dummy_info(), TmZero(Info.dummy_info())), True),
        (TmZero(Info.dummy_info()), True),
        (TmPred(Info.dummy_info(), TmZero(Info.dummy_info())), False),
        (TmSucc(Info.dummy_info(), TmTrue(Info.dummy_info())), False),
        (TmFalse(Info.dummy_info()), True),
        (TmIf(Info.dummy_info(), TmTrue(Info.dummy_info()), TmTrue(Info.dummy_info()), TmTrue(Info.dummy_info())),
         False),
        (TmIsZero(Info.dummy_info(), TmZero(Info.dummy_info())), False)
    ])
    def test_is_val(self, term: Term, expected: bool):
        self.assertEqual(term.is_val(), expected, f"{term} should be classified as a value" if expected else f"{term} shouldn't be classified as a value")

