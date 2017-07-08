import System.Environment

f :: Integer -> String
f 0 = ""
f n = (show n) ++  f(n-1) ++ (show n)

main = do a <- (fmap (read . head) getArgs);
          print (f a)

