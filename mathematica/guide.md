# Convert Python structures to Mathematica structures

The module
```python
from mmaformatter import get_mma, save_as_mma
```
provides functions for converting Python floats, complex numbers, lists, tuples, sets and
dictionaries to their corresponding Mathematica form, 
e.g. scientific notation, associations. An equivalent module for C can be found [here](https://github.com/TysonRayJones/CTools/blob/master/mathematica/guide.md).


One can pass any nested structure of arrays, tuples, sets, dictionaries 
(of primitives ints, floats, comple numbers, bools and strings) to `get_mma` to get strings
of their Mathematica form.

For example
```python
>>> get_mma(-1/999)
'-1.00100*10^-03'

>>> get_mma(1/(3+2j), precision=2)
'2.31*10^-01-1.54*10^-01I'

>>> get_mma([1, 1/2, 3j])
'{1, 5.00000*10^-01, 0+3I}'
```
and here printing the output (for clarity)
```python
>>> get_mma({1:2, "cat":"dog"})
```

> ```
> <|  
>     1 -> 2,  
>     "cat" -> "dog"  
> |>
> ```

```python
>>> get_mma({"Tyson":(0,0,7), "nest":{"birds":4}}, keep_symbols=True)
```
> ```
> <|  
>     Tyson -> {0, 0, 7},  
>     nest -> <| birds -> 4 |>   
> |>
> ```

The function `save_as_mma` can take the same structures and write their Mathematica
form to file, to be read by Mathematica.

For example,
```python
data = [1.013, 10.331, .59102, 5.0, 6.0]
struc = {"patient":"Tyson", "trial":112, "conductivity":data}
save_as_mma(struc, "assoc.txt", precision=2)
```
produces a file "assoc.txt" with contents
```
<|
    "trial" -> 112,
    "patient" -> "Tyson",
    "conductivity" -> {1.01*10^+00, 1.03*10^+01, 5.91*10^-01, 5, 6}
|>
```
which can then be read into Mathematica via
```Mathematica
SetDirectory @ NotebookDirectory[];
assoc = Get["assoc.txt"]

ListLinePlot @ assoc["conductivity"]
```
which produces the very-terrific graph

![a terrible graph](https://qtechtheory.org/wp-content/uploads/2017/12/assoctestplot.png)

---------------------------

Both `get_mma` and `save_as_mma` accept optional arguments
- `key_order`: use explicit ordering in the Mathematica association for the keys in the passed dictionary
- `keep_symbols`: whether python strings should be converted to Mathematica symbols, else be enquoted to become strings
- `precision`: the number of decimal digits in the scientific notation format of floats
- `keep_ints`: whether integers should be kept formatted as such, else converted to scientific notation (at the precision supplied); applies to the real and imaginary components of complex numbers too
