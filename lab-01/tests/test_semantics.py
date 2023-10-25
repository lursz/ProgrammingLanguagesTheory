#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from unittest import TestCase
from parameterized import parameterized
from src.term import *
from src.semantics import *

class TestArithmeticSemantics(TestCase):

    @parameterized.expand([
        (
            TmIf(info=Info(lineno=1, column=0), condition=TmTrue(info=Info(lineno=1, column=3)), if_true=TmFalse(info=Info(lineno=1, column=13)), if_else=TmTrue(info=Info(lineno=1, column=24))),
            Transition(old_state=TmIf(info=Info(lineno=1, column=0), condition=TmTrue(info=Info(lineno=1, column=3)),
                                      if_true=TmFalse(info=Info(lineno=1, column=13)),
                                      if_else=TmTrue(info=Info(lineno=1, column=24))),
                       new_state=TmFalse(info=Info(lineno=1, column=13)), rule=Rule.IfTrue, witnesses=())
        ),
        (
            TmIf(info=Info(lineno=1, column=0), condition=TmFalse(info=Info(lineno=1, column=3)),
                     if_true=TmFalse(info=Info(lineno=1, column=14)), if_else=TmTrue(info=Info(lineno=1, column=25))),
            Transition(old_state=TmIf(info=Info(lineno=1, column=0), condition=TmFalse(info=Info(lineno=1, column=3)),
                                      if_true=TmFalse(info=Info(lineno=1, column=14)),
                                      if_else=TmTrue(info=Info(lineno=1, column=25))),
                       new_state=TmTrue(info=Info(lineno=1, column=25)), rule=Rule.IfFalse, witnesses=())
        ),
        (
            TmPred(info=Info(lineno=1, column=0), number=TmZero(info=Info(lineno=1, column=5))),
            Transition(old_state=TmPred(info=Info(lineno=1, column=0), number=TmZero(info=Info(lineno=1, column=5))),
                       new_state=TmZero(info=Info(lineno=-1, column=-1)), rule=Rule.PredZero, witnesses=())
        ),
        (
            TmPred(info=Info(lineno=1, column=0), number=TmSucc(info=Info(lineno=1, column=5),
                                                                number=TmSucc(info=Info(lineno=1, column=10),
                                                                              number=TmZero(
                                                                                  info=Info(lineno=1, column=15))))),
            Transition(old_state=TmPred(info=Info(lineno=1, column=0), number=TmSucc(info=Info(lineno=1, column=5),
                                                                                     number=TmSucc(
                                                                                         info=Info(lineno=1, column=10),
                                                                                         number=TmZero(
                                                                                             info=Info(lineno=1,
                                                                                                       column=15))))),
                       new_state=TmSucc(info=Info(lineno=1, column=10), number=TmZero(info=Info(lineno=1, column=15))),
                       rule=Rule.PredSucc, witnesses=())
        ),
        (
            TmIsZero(info=Info(lineno=1, column=0), number=TmZero(info=Info(lineno=1, column=7))),
            Transition(old_state=TmIsZero(info=Info(lineno=1, column=0), number=
                TmZero(info=Info(lineno=1, column=7))), new_state = TmTrue(
                info=Info(lineno=-1, column=-1)), rule = Rule.IsZeroZero, witnesses = ())
        ),
        (
            TmIsZero(info=Info(lineno=1, column=0),
                     number=TmSucc(info=Info(lineno=1, column=7), number=TmZero(info=Info(lineno=1, column=12)))),
            Transition(old_state=TmIsZero(info=Info(lineno=1, column=0),
                                          number=TmSucc(info=Info(lineno=1, column=7),
                                                        number=TmZero(info=Info(lineno=1, column=12)))),
                       new_state=TmFalse(info=Info(lineno=-1, column=-1)), rule=Rule.IsZeroSucc, witnesses=())
        ),
        (
            TmIf(info=Info(lineno=1, column=0),
                 condition=TmIf(info=Info(lineno=1, column=3), condition=TmFalse(info=Info(lineno=1, column=6)),
                                if_true=TmFalse(info=Info(lineno=1, column=17)),
                                if_else=TmFalse(info=Info(lineno=1, column=28))),
                 if_true=TmTrue(info=Info(lineno=1, column=39)), if_else=TmFalse(info=Info(lineno=1, column=49))),
            Transition(old_state=TmIf(info=Info(lineno=1, column=0), condition=TmIf(info=Info(lineno=1, column=3),
                                                                                    condition=TmFalse(
                                                                                        info=Info(lineno=1, column=6)),
                                                                                    if_true=TmFalse(
                                                                                        info=Info(lineno=1, column=17)),
                                                                                    if_else=TmFalse(info=Info(lineno=1,
                                                                                                              column=28))),
                                      if_true=TmTrue(info=Info(lineno=1, column=39)),
                                      if_else=TmFalse(info=Info(lineno=1, column=49))),
                       new_state=TmIf(info=Info(lineno=1, column=0), condition=TmFalse(info=Info(lineno=1, column=28)),
                                      if_true=TmTrue(info=Info(lineno=1, column=39)),
                                      if_else=TmFalse(info=Info(lineno=1, column=49))), rule=Rule.If, witnesses=(
                Transition(
                    old_state=TmIf(info=Info(lineno=1, column=3), condition=TmFalse(info=Info(lineno=1, column=6)),
                                   if_true=TmFalse(info=Info(lineno=1, column=17)),
                                   if_else=TmFalse(info=Info(lineno=1, column=28))),
                    new_state=TmFalse(info=Info(lineno=1, column=28)), rule=Rule.IfFalse, witnesses=()),))
        ),
        (
            TmSucc(info=Info(lineno=1, column=0), number=TmPred(info=Info(lineno=1, column=5),
                                                                number=TmSucc(info=Info(lineno=1, column=10),
                                                                              number=TmZero(
                                                                                  info=Info(lineno=1, column=15))))),
            Transition(old_state=TmSucc(info=Info(lineno=1, column=0), number=TmPred(info=Info(lineno=1, column=5),
                                                                                     number=TmSucc(
                                                                                         info=Info(lineno=1,
                                                                                                   column=10),
                                                                                         number=TmZero(
                                                                                             info=Info(lineno=1,
                                                                                                       column=15))))),
                       new_state=TmSucc(info=Info(lineno=1, column=0),
                                        number=TmZero(info=Info(lineno=1, column=15))), rule=Rule.Succ, witnesses=(
                Transition(old_state=TmPred(info=Info(lineno=1, column=5),
                                            number=TmSucc(info=Info(lineno=1, column=10),
                                                          number=TmZero(info=Info(lineno=1, column=15)))),
                           new_state=TmZero(info=Info(lineno=1, column=15)), rule=Rule.PredSucc, witnesses=()),))
        ),
        (
            TmPred(info=Info(lineno=1, column=0), number=TmPred(info=Info(lineno=1, column=5),
                                                                number=TmSucc(info=Info(lineno=1, column=10),
                                                                              number=TmZero(
                                                                                  info=Info(lineno=1, column=15))))),
            Transition(old_state=TmPred(info=Info(lineno=1, column=0), number=TmPred(info=Info(lineno=1, column=5),
                                                                                     number=TmSucc(
                                                                                         info=Info(lineno=1,
                                                                                                   column=10),
                                                                                         number=TmZero(
                                                                                             info=Info(lineno=1,
                                                                                                       column=15))))),
                       new_state=TmPred(info=Info(lineno=1, column=0),
                                        number=TmZero(info=Info(lineno=1, column=15))), rule=Rule.Pred, witnesses=(
                Transition(old_state=TmPred(info=Info(lineno=1, column=5),
                                            number=TmSucc(info=Info(lineno=1, column=10),
                                                          number=TmZero(info=Info(lineno=1, column=15)))),
                           new_state=TmZero(info=Info(lineno=1, column=15)), rule=Rule.PredSucc, witnesses=()),))
        ),
        (
            TmIsZero(info=Info(lineno=1, column=0), number=TmPred(info=Info(lineno=1, column=7),
                                                                  number=TmSucc(info=Info(lineno=1, column=12),
                                                                                number=TmZero(info=Info(lineno=1,
                                                                                                        column=17))))),
            Transition(old_state=TmIsZero(info=Info(lineno=1, column=0),
                                          number=TmPred(info=Info(lineno=1, column=7),
                                                        number=TmSucc(info=Info(lineno=1, column=12), number=TmZero(
                                                            info=Info(lineno=1, column=17))))),
                       new_state=TmIsZero(info=Info(lineno=1, column=0),
                                          number=TmZero(info=Info(lineno=1, column=17))), rule=Rule.IsZero,
                       witnesses=(Transition(old_state=TmPred(info=Info(lineno=1, column=7),
                                                              number=TmSucc(info=Info(lineno=1, column=12),
                                                                            number=TmZero(
                                                                                info=Info(lineno=1, column=17)))),
                                             new_state=TmZero(info=Info(lineno=1, column=17)), rule=Rule.PredSucc,
                                             witnesses=()),))
        )
    ])
    def test_single_step(self, state: Term, expected_transition: Transition):
        def assert_transition(transition, expected, header = ''):
            self.assertEqual(transition.new_state, expected.new_state,
                             f"{header}the single step semantics returns an incorrect state, term: {state}")
            self.assertEqual(transition.old_state, expected.old_state,
                             f"{header}the single step semantics starts with an an incorrect state, term: {state}")
            self.assertEqual(transition.rule, expected.rule,
                             f"{header}the single step semantics uses an incorrect rule, term: {state}")
            self.assertEqual(len(transition.witnesses), len(expected.witnesses),
                             f"{header}the single step semantics returns an incorrect number of witnesses, term: {state}")
            for i,witness in enumerate(transition.witnesses):
                assert_transition(witness, expected.witnesses[i], "[witness] ")
        try:
            assert_transition(ArithmeticSemantics.single_step(state), expected_transition)
        except:
            self.fail(f"transition failed unexpectedly, term:  {state}")

    @parameterized.expand([
        (TmZero(info=Info(lineno=1, column=0)),),
        (TmTrue(info=Info(lineno=1, column=0)),),
        (TmFalse(info=Info(lineno=1, column=0)),),
        (TmSucc(info=Info(lineno=1, column=0), number=TmZero(info=Info(lineno=1, column=5))),),
        (TmSucc(info=Info(lineno=1, column=0), number=TmSucc(info=Info(lineno=1, column=5), number=TmZero(info=Info(lineno=1, column=10)))),),
        (TmIsZero(info=Info(lineno=1, column=0), number=TmFalse(info=Info(lineno=1, column=7))),)
    ])
    def test_finished(self, state: Term):
        self.assertRaises(NoRuleApplies, lambda: ArithmeticSemantics.single_step(state))