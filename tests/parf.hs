
import Control.Parallel.Strategies
import Control.Parallel
import Data.List

parFoldr1 _ [x] = x
parFoldr1 mappend xs  = (ys `par` zs) `pseq` (ys `mappend` zs) where
  len = length xs
  (ys', zs') = splitAt (len `div` 2) xs
  ys = parFoldr1 mappend ys'
  zs = parFoldr1 mappend zs'

x = 200


cs :: Integer -> Rational
cs n = 2.718281828*(fromIntegral n)
f_g_2 _HOP_i = (cs (_HOP_i))
f_g_4 _HOP_i = x
f_BETA_2 f_BETA_k f_BETA_i = (f_g_2 f_BETA_i)*((f_g_4 0)^(f_BETA_k-f_BETA_i))
f_PHI_2 k = (parFoldr1 (+) (map (f_BETA_2 k) [1..(k-1)])) + (f_g_2 k)
f_PHI_4 k = (f_g_4 1)*(f_g_4 0)^(k-1)
f :: Integer -> Rational
f 0 = (cs 1)
f n = let k = n
 in ((cs 1))*(f_PHI_4 k)+(f_PHI_2 k)
main = print (f 100)
