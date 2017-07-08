import System.Environment

f :: Integer -> Integer
f 0 = 1
f n = n * f(n-1)

main = do a <- (fmap (read . head) getArgs);
          print (f a)


