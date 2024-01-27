(\x:<u:Unit, b:Bool, n:Nat>. case x of
      <u = x> => { f = x }
    | <b = x> => { f = x }
    | <n = x> => { f = x }) <u = unit>