#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

import click
from typing import TextIO

from src.semantics.macro import MacroSystem
from src.semantics.term_utils import term_is_val
from src.semantics.typechecker import LambdaTypeError, TypedLambdaTypechecker
from src.parser import TypedLambdaParser
from src.semantics.debruijn_indexer import DebruijnIndexer
from src.sprdpl.parse import ParseError
from src.semantics.evaluator import TypedLambdaEvaluator, NoEvalRuleApplies, Transition
from src.lambda_program import TypedLambdaProgram


def evaluate(program: TypedLambdaProgram):
    evaluator = TypedLambdaEvaluator(program.name_context)
    current_state = program.state
    print(program)
    while True:
        try:
            transition = evaluator.single_step(current_state)
            print_transition(transition)
            current_state = transition.new_state
        except NoEvalRuleApplies:
            if term_is_val(current_state.term):
                print("---- finished successfully")
            else:
                print("---- stuck")
            return

def print_transition(t: Transition):
    print(f'-> {t.new_state.pretty_str(t.name_context)}  [{t.rule.name}]')
    print_witnesses(t)


def print_witnesses(t: Transition, level: int = 0):
    if len(t.witnesses) == 0:
        return

    tab = "   " * (level + 1)
    deriv_symb = "|: "
    for witness in t.witnesses:
        print(f"{tab}{deriv_symb}{witness.old_state.pretty_str(witness.name_context)} -> {witness.new_state.pretty_str(witness.name_context)}  [{witness.rule.name}]")
        print_witnesses(witness, level + 1)


def typecheck(parsing_result: TypedLambdaProgram):
    TypedLambdaTypechecker().typecheck(parsing_result)


@click.command()
@click.argument('file', type=click.File('r'))
def evaluate_file(file: TextIO) -> None:
    raw_program = file.read()
    try:
        ast = TypedLambdaParser().parse(raw_program)
        program = DebruijnIndexer().remove_names(ast)
        expanded_program = MacroSystem().expand(program)
        typecheck(expanded_program)
        evaluate(expanded_program)
    except ParseError as pe:
        pe.print()
    except LambdaTypeError as lte:
        print(lte)


if __name__ == '__main__':
    evaluate_file()