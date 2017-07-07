xs :: Integer -> Rational
xs n = 3.1415926*100*(fromIntegral n)

f :: Integer -> Rational
f 0 = 5000
f n = 0.1* f(n-1) + ((1-0.10)*(xs n))
