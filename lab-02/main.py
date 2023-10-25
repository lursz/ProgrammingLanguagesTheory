#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

import click
from typing import TextIO
from src.parser import LambdaParser
from src.sprdpl.parse import ParseError
from src.semantics import LambdaSemantics, NoRuleApplies, Transition
from src.lambda_program import LambdaProgram


def evaluate(program: LambdaProgram):
    semantics = LambdaSemantics(program.free_names)
    current_state = program

    print(current_state)
    while True:
        try:
            transition = semantics.single_step(current_state.term)
            print_transition(transition)
            current_state = transition.new_state
        except NoRuleApplies:
            if LambdaSemantics.is_term_val(current_state.term):
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
        parsing_result = LambdaParser().parse(raw_program)
        evaluate(parsing_result)
    except ParseError as pe:
        pe.print()

if __name__ == '__main__':
    evaluate_file()