import System.Environment

f :: Rational -> Rational
f 1 = 1
f n = (2*(2*n-1)/(n+1)) * f(n-1)

main = do a <- (fmap (read . head) getArgs);
          print (f a)

