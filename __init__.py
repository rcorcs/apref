
import sys

from apref import *

if __name__=='__main__':

   if len(sys.argv)==4:
      filename  = sys.argv[1]
      useScan   = (sys.argv[2]=='True')
      constFold = (sys.argv[3]=='True')
      print parallelizeFile(filename,useScan,constFold)
   else:   
      setDebugMode(True)
      print parallelize('''fac :: Integer -> Integer
                           fac 1 = 1
                           fac n = n * fac(n-1)''')
      print ''

      #parallelize('''f :: Integer -> Integer
      #                       f 1 = y0
      #                       f n = y!!n + (1+r) * f(n-1)*2 + y!!n''')
      #parallelize('''f :: Integer -> Integer
      #                       f 1 = 1
      #                       f n = n + (1+1) * f(n-1)*2 + n''')
      #parallelize('''f :: Integer -> Integer
      #                       f 1 = 1
      #                       f n = (1+1) * f(n-1) + n''')

      #print parallelize('''f :: Rational -> Rational
      #                       f 0 = 2000
      #                       f n = (1 + 0.005) * f(n-1) + 100''',True,True)
      #print ''

      #print parallelize('''f :: Rational -> Rational
      #                       f 0 = 2000
      #                       f n = 100 + (1 + 0.005) * f(n-1)''')
      #print ''

      #print parallelize('''f :: Integer -> IMG_SET
      #                       f e_0 = y_0
      #                       f n = g_1(n) ++ f(n-e_1) ++ g_2(n)''')
      #print ''

      #print parallelize('''f :: Integer -> IMG_SET
      #                       f e_0 = y_0
      #                       f n = g_1(n) ++ g_3(n) *** f(n-e_1) *** g_4(n) ++ g_2(n)''')
      #print ''

      #print parallelize('''f :: Integer -> String
      #                     f 0 = ""
      #                     f n = (show n) ++  f(n-1) ++ (show n)''')
      #print ''

      #parallelize('''f :: Integer -> Rational
      #               f 1 = 1
      #               f n = (2*(2*n-1)/(n+1)) * f(n-1)''')

      #print parallelize('''f :: Integer -> Integer
      #               f 0 = 0
      #               f n = 1 + f(n-1)''')
      #print ''

