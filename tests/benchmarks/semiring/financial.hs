import System.Environment

f :: Integer -> Rational
f 0 = 2000
f n = (1 + 0.005) * f(n-1) * 1 + 100

main = do a <- (fmap (read . head) getArgs);
          print (f a)

