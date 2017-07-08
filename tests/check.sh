time -p ./seq$1 $2 +RTS -N1 > seq.txt
time -p ./par$1 $2 +RTS -N4 > par.txt

diff seq.txt par.txt

