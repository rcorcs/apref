f :: Integer -> Integer
f 0 = 1
f n = n * f(n-1)
