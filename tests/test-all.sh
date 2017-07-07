

TESTDIR=$(pwd)

testBenchmark() {
   benchfile=$1
   echo $(basename $benchfile)
   cat $benchfile > seqf.hs


   python ../__init__.py ${TESTDIR}/seqf.hs True True > ${TESTDIR}/parf.hs
   if [ $? -ne 0 ]; then
      exit $?
   fi

   echo "main = print (f 100)" >> seqf.hs
   echo "main = print (f 100)" >> parf.hs

   sh build.sh f
   sh check.sh f >/dev/null
   if [ $? -eq 0 ]; then
      echo 'Outputs Matching [OK]'
   else
      echo 'Outputs NOT Matching [FAIL]'
      exit 0
   fi

   sh clean.sh
   rm -f seqf.hs
   #rm -f parf.hs
   rm -f parf
   rm -f seqf
}

echo 'Testing Monoid-based Benchmarks'
for benchfile in benchmarks/monoid/*; do
  testBenchmark $benchfile
done

echo 'Testing Semiring-based Benchmarks'
for benchfile in benchmarks/semiring/*; do
  testBenchmark $benchfile
done

