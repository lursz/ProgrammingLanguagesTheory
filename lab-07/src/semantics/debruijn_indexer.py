#  Copyright (c) 2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from collections import OrderedDict
from functools import partial

from src.lambda_program import TypedLambdaProgram, LambdaProgramState
from src.memory import Memory
from src.term import NamedTerm, TmNamedVar, TmVar, TmAbs, TmLet, TmApp, TmZero, TmFalse, TmTrue, TmIf, TmIsZero, TmPred, \
    TmSucc, TmFix, TmLetRec, TmUnit, UnexpandedTerm, TmRecord, TmProjection, TmTagging, TmCase, TmReference, \
    TmDereference, TmAssignment, TmSequence


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
        return TypedLambdaProgram(LambdaProgramState(term), index.to_list())

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
            case TmRecord() as record:
                assert isinstance(record, TmRecord)
                mapper = partial(self._replace_vars, index=index, context=context)
                return record.map_items(mapper)
            case TmProjection(info, t, label):
                return TmProjection(info, self._replace_vars(t, index, context), label)
            case TmTagging(info, label, term):
                return TmTagging(info, label, self._replace_vars(term, index, context))
            case TmCase(info, term, vars, branches):
                idx_term = self._replace_vars(term, index, context)
                idx_branches = []
                for label, var in vars.items():
                    new_context = [var] + context
                    branch = branches[label]
                    idx_branch = self._replace_vars(branch, index, new_context)
                    idx_branches.append((label, idx_branch))
                return TmCase(info, idx_term, vars, OrderedDict(idx_branches))
            case TmReference(info, t1):
                return TmReference(info, self._replace_vars(t1, index, context))
            case TmDereference(info, t1):
                return TmDereference(info, self._replace_vars(t1, index, context))
            case TmAssignment(info, t1, t2):
                return TmAssignment(info, self._replace_vars(t1, index, context),
                                          self._replace_vars(t2, index, context))
            case TmSequence(info, t1, t2):
                return TmSequence(info, self._replace_vars(t1, index, context),
                                        self._replace_vars(t2, index, context))



