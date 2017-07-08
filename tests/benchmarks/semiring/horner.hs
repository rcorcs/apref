import System.Environment

x = 200

cs :: Integer -> Rational
cs n = 2.718281828*(fromIntegral n)

f :: Integer -> Rational
f 0 = (cs 1)
f n = f(n-1) * x + (cs n)

main = do a <- (fmap (read . head) getArgs);
          print (f a)

