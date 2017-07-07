f :: Integer -> String
f 0 = ""
f n = (show n) ++  f(n-1) ++ (show n)
