#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

import click
from typing import TextIO
from src.parser import ArithmeticParser
from src.sprdpl.parse import ParseError
from src.semantics import ArithmeticSemantics, NoRuleApplies, Transition
from src.term import Term

def evaluate(program: Term):
    current_state = program
    print(current_state)
    while True:
        try:
            transition = ArithmeticSemantics.single_step(current_state)
            print_transition(transition)
            current_state = transition.new_state
        except NoRuleApplies:
            if current_state.is_val():
                print("---- finished successfully")
            else:
                print("---- stuck")
            return

def print_transition(t: Transition):
    print(f'-> {t.new_state}  [{t.rule.name}]')
    print_witnesses(t)

def print_witnesses(t: Transition, level: int = 0):
    if len(t.witnesses) == 0:
        return

    tab = "   " * (level + 1)
    deriv_symb = "|: "
    for witness in t.witnesses:
        print(f"{tab}{deriv_symb}{witness.old_state} -> {witness.new_state}  [{witness.rule.name}]")
        print_witnesses(witness, level + 1)

@click.command()
@click.argument('file', type=click.File('r'))
def evaluate_file(file: TextIO) -> None:
    raw_program = file.read()
    try:
        parsing_result = ArithmeticParser().parse(raw_program)
        evaluate(parsing_result)
    except ParseError as pe:
        print(pe)

if __name__ == '__main__':
    evaluate_file()