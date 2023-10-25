#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!

from dataclasses import dataclass

from src.term import Term, TmAbs, TmApp, TmVar


@dataclass(frozen=True)
class LambdaProgram:
    '''
    Class representing a "program" written in the lambda calculus.

    Attributes:
        - term: Term
            Lambda calculus term
        - free_names: list[str]
            This list stores names of the free variables in order to print them in a pretty way :)
    '''
    term: Term
    free_names: list[str]

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

        #DONE:
        # if term is:
        #   - an abstraction (TmAbs), then pick a fresh name (self._pick_fresh_name) with suggestion
        #       supplied by the TmAbs.arg
        #       and return text "(\<name>.<pretty_body>), where:
        #           * <name> is a fresh name
        #           * <pretty_body> should be constructed using recursive _pretty_str call
        #   - an application (TmApp), then return text: "(<pretty_function> <pretty_arg>)", where:
        #       both pretty things should be constructed using recursive _pretty_str calls
        #   - a variable (TmVar):
        #       * first, make sure that the length of the context is the same as context_length in the variable
        #           use "assert"
        #       * then, find a name using self._find_name
        #
        match term:
            case TmAbs(_, arg, body):
                new_context, pretty_name = self._pick_fresh_name(context, arg)
                pretty_body = self._pretty_str(new_context, body)
                return f"(\\{pretty_name}.{pretty_body})"
            case TmApp(_, fun, arg):
                pretty_fun = self._pretty_str(context, fun)
                pretty_arg = self._pretty_str(context, arg)
                return f"({pretty_fun} {pretty_arg})"
            case TmVar(_, index, context_length):
                assert len(context) == context_length
                return self._find_name(context, index)



    def _pick_fresh_name(self, context: list[str], suggestion: str) -> tuple[list[str], str]:
        '''
            This method generates new fresh name based on the suggestion and and list of already used names.
            It's based on the "printtm" function from page 85 in the TAPL book.

            :param context: already used variable names in the scope
            :param suggestion: suggested name
            :return: tuple containing new context and fresh name
        '''
        #DONE:
        # if suggested name is already in the context, add 'prim' suffix, e.g. "x" -> "x'"
        # add "prims" as long as the name is in the context
        # when you find a correct name, create a new context with the new name at the beginning and the old rest
        # then return a tuple (new_context, fresh_name)
        set_of_names = set(context)
        while suggestion in set_of_names:
            suggestion += '\''
        return ([suggestion] + context, suggestion)

    def _find_name(self, context: list[str], index: int) -> str:
        '''
            This method finds a variable name based on the list of the used names.

            :param context: already used variable names in the scope
            :param index: index of a variable
            :return: name corresponding the the index
        '''
        # DONE:
        # if index doesn't go beyond the context, just return the corresponding context name
        # in other case we have to deal with a free variable
        # names for the free variables are stored in the self.free_names list
        # to find the correct index one has to subtract size of the context from the variable index
        return context[index] if len(context) > index else self.free_names[index - len(context)]