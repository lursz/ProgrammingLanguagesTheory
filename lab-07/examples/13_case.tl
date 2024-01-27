(\x:<u:Unit, b:Bool, n:Nat>. case x of
      <u = x> => 0
    | <b = x> => 0
    | <n = x> => x) <u = unit>