letrec plus: Nat -> (Nat -> Nat) =
    \x: Nat. \y: Nat. if iszero y
                        then x
                      else
                        (plus succ x) (pred y)
in
letrec fib: Nat -> Nat =
    \i: Nat. if iszero i
                then 0
             else if iszero pred i
                then succ 0
             else (plus (fib pred i)) (fib pred pred i)
in
fib {{input}}