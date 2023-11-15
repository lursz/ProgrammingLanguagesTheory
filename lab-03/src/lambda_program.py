#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from dataclasses import dataclass

from src.term import Term, TmAbs, TmApp, TmVar, TmZero, TmFalse, TmTrue, TmIf, TmIsZero, TmPred, TmSucc


@dataclass(frozen=True)
class TypedLambdaProgram:
    '''
    Class representing a "program" written in the lambda calculus.

    Attributes:
        - term: Term
            Lambda calculus term
        - name_context: list[str]
            This list stores names of the free variables in order to print them in a pretty way :)
    '''
    term: Term
    name_context: list[str]

    def __str__(self) -> str:
        context: list[str] = []
        return self._pretty_str(context, self.term)

    def _pretty_str(self, context: list[str], term: Term) -> str:
        '''
            This method prints the term with correct variable names.
            It's based on the "printtm" function from page 85 in the TAPL book.

            :param context: already used variable names in the scope
            :param term: term to be printed
            :return: pretty textual representation
        '''

        match term:
            case TmAbs(_, arg, arg_type, body):
                new_context, name = self._pick_fresh_name(context, arg)
                return f"(\\{name}:{arg_type}.{self._pretty_str(new_context, body)})"
            case TmApp(_, function, arg):
                return f"({self._pretty_str(context, function)} {self._pretty_str(context, arg)})"
            case TmVar(_, index, ctx_length):
                assert ctx_length == len(context), f"{index}: {ctx_length} != {len(context)}"
                return self._find_name(context, index)
            case TmZero() | TmFalse() | TmTrue():
                return str(term)
            case TmIf(_, cond, if_act, else_act):
                pretty_cond = self._pretty_str(context, cond)
                pretty_if_act = self._pretty_str(context, if_act)
                pretty_else_act = self._pretty_str(context, else_act)
                return f"if {pretty_cond} then {pretty_if_act} else {pretty_else_act}"
            case TmIsZero(_, arg):
                return f"iszero {self._pretty_str(context, arg)}"
            case TmPred(_, arg):
                return f"pred {self._pretty_str(context, arg)}"
            case TmSucc(_, arg):
                return f"succ {self._pretty_str(context, arg)}"


    def _pick_fresh_name(self, context: list[str], suggestion: str) -> tuple[list[str], str]:
        '''
            This method generates new fresh name based on the suggestion and and list of already used names.

            :param context: already used variable names in the scope
            :param suggestion: suggested name
            :return: tuple containing new context and fresh name
        '''
        fresh_name = suggestion
        while fresh_name in context:
             fresh_name = f"{fresh_name}'"
        new_context =  [fresh_name] + context
        return new_context, fresh_name

    def _find_name(self, context: list[str], index: int) -> str:
        '''
            This method finds a variable name based on the list of the used names.

            :param context: already used variable names in the scope
            :param index: index of a variable
            :return: name corresponding the the index
        '''
        if index < len(context):
            return context[index]
        else:
            return self.name_context[index - len(context)]