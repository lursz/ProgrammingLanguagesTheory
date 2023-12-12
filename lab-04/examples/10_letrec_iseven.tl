letrec iseven : Nat->Bool = \x:Nat.
               (if iszero x then true
               else if iszero (pred x) then false
               else iseven (pred (pred x)))
in iseven (succ (succ (succ (succ (succ 0)))))