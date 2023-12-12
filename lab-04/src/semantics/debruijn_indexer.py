#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from src.lambda_program import TypedLambdaProgram
from src.term import NamedTerm, TmNamedVar, TmVar, TmAbs, TmLet, TmApp, TmZero, TmFalse, TmTrue, TmIf, TmIsZero, TmPred, \
    TmSucc, TmFix, TmLetRec, TmUnit, UnexpandedTerm


class Index(dict):
    def __missing__(self, key):
        self[key] = len(self)
        return self[key]

    def to_list(self):
        result = ["" for _ in self]
        for k,v in self.items():
            result[v] = k
        return result


class DebruijnIndexer:

    def remove_names(self, named_term: NamedTerm) -> TypedLambdaProgram[UnexpandedTerm]:
        index = Index()
        context: list[int] = []
        term = self._replace_vars(named_term, index, context)
        return TypedLambdaProgram(term, index.to_list())

    def _replace_vars(self, named_term: NamedTerm, index: Index, context: list[str]) -> UnexpandedTerm:
        match named_term:
            case TmZero() | TmFalse() | TmTrue() | TmUnit():
                return named_term
            case TmNamedVar(info, id):
                if id in context:
                    return TmVar(info, context.index(id), len(context))
                else:
                    return TmVar(info, len(context) + index[id], len(context))
            case TmAbs(info, arg, arg_type, body):
                new_context = [arg] + context
                return TmAbs(info, arg, arg_type, self._replace_vars(body, index, new_context))
            case TmLet(info, var, rside, body):
                new_context = [var] + context
                return TmLet(info, var,
                             self._replace_vars(rside, index, context),
                             self._replace_vars(body, index, new_context))
            case TmApp(info, fun, arg):
                return TmApp(info, self._replace_vars(fun, index, context), self._replace_vars(arg, index, context))
            case TmIf(info, cond_named, if_act_named, else_act_named):
                cond = self._replace_vars(cond_named, index, context)
                if_act = self._replace_vars(if_act_named, index, context)
                else_act = self._replace_vars(else_act_named, index, context)
                return TmIf(info, cond, if_act, else_act)
            case TmIsZero(info, arg):
                return TmIsZero(info, self._replace_vars(arg, index, context))
            case TmPred(info, arg):
                return TmPred(info, self._replace_vars(arg, index, context))
            case TmSucc(info, arg):
                return TmSucc(info, self._replace_vars(arg, index, context))
            case TmFix(info, arg):
                return TmFix(info, self._replace_vars(arg, index, context))
            case TmLetRec(info, var, type, function, body):
                new_context = [var] + context
                return TmLetRec(info, var, type,
                                self._replace_vars(function, index, new_context),
                                self._replace_vars(body, index, new_context))