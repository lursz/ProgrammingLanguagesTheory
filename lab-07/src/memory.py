#  Copyright (c) 2021-2021. Created by Mateusz Slazynski for the educational purposes.
#     Feel free to use/modify this code for any greater good.
#     It would be nice however if you mentioned me somewhere.
#     Still, no pressure - have a nice day!
from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
from src.term import Term, TmStoreLocation, Info


@dataclass(frozen=True,eq=True)
class Memory:
    '''
    Class representing an abstract memory addressable with TmStoreLocation terms.
    It is immutable, all mutating methods return new memory as the first result.

    Attributes:
    ===========
    space: tuple[Term]
        an indexed storage, nothing fancy

    Methods:
    ========
    put(term: Term) -> tuple[Memory, TmStoreLocation]
        creates a new memory containing the given term
        the result contains new memory and address of the memory cell holding the term
    def replace(location: TmStoreLocation, term: Term) -> Memory:
        creates a new memory with a replaced term stored at the given address
    def dereference(location: TmStoreLocation) -> Term:
        return term stored at the given address
    '''
    space: tuple[Term] = tuple()

    def put(self, term: Term) -> tuple[Memory, TmStoreLocation]:
        new_space = self.space + (term,)
        return Memory(new_space), TmStoreLocation(Info.dummy_info(), len(self.space))

    def replace(self, location: TmStoreLocation, term: Term) -> Memory:
        return Memory(self.space[:location.address] + (term,) + self.space[location.address+1:])

    def dereference(self, location: TmStoreLocation) -> Term:
        return self.space[location.address]

    def __str__(self) -> str:
        return "{" + ", ".join([f"@{i} <- {v}" for i, v in enumerate(self.space)]) + "}"



