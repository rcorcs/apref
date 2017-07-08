# APReF: Automatic Parallelizer of REcursive Functions

This is a source-to-source Haskell compiler that automatically identifies and rewrites recursive functions in a parallel form.

### Example

Given the following sequential recursive function:
```
f :: Integer -> [Integer]
f 0 = []
f n = [n] ++ f(n-1) ++ [n]
```
the source-to-source compiler is able to rewrite it as in the following parallel version:
```
f_g_1 :: Integer -> [Integer]
f_g_1 i = [i]
f_g_2 :: Integer -> [Integer]
f_g_2 i = [i]
f :: Integer -> [Integer]
f n = let k = n
      in (parFoldr (++) (map f_g_1 (reverse [1..k]))) ++ [] ++
         (parFoldr (++) (map f_g_2 [1..k]))
```

### Usage

By passing a Haskell file to the source-to-source compiler,
any parallelizable function will be rewritten in their parallel counterparts.
Auxiliary packages and functions will also be added.

```
python apref.py -f <haskell-file> --scan --constfold
```

The flag '--scan' enables a scan-based optimization.
Similarly, the '--constfold' enables a constant folding optimization.

