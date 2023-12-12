letrec plus : Nat->(Nat->Nat) = \x : Nat. \y : Nat.
    (if iszero y then x
    else ((plus (succ x)) (pred y)))
in  letrec fibonacci : Nat->Nat = \n : Nat.
        (if iszero n then 0
        else if iszero (pred n) then (succ 0)
        else ((plus (fibonacci (pred n))) (fibonacci (pred (pred n)))))
    in fibonacci {{input}}