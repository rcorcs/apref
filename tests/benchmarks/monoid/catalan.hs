f :: Rational -> Rational
f 1 = 1
f n = (2*(2*n-1)/(n+1)) * f(n-1)
