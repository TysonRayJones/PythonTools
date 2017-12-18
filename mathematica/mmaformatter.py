
import os
import re


'''
A library for generating strings readable by Mathematica's Get[ ] from Python objects

author: Tyson Jones
        tyson.jones@materials.ox.ac.uk
date:   25 Nov 2017
'''


# defaults to get_mma optional arguments
_DEFAULT_PRECISION    = 5
_DEFAULT_KEEP_INTS    = True  
_DEFAULT_KEEP_SYMBOLS = False

_INDENT_CHAR = ' '*4

# formats of MMA objects            
_STRING_FORMAT      = '"%s"'             
_BASE_TEN_FORMAT    = '*10^'           
_COMPLEX_FORMAT     = '%s%s%sI'
_ARRAY_OUTER_FORMAT = '{%s}'        
_ARRAY_JOIN_FORMAT  = ', '            
_DICT_OUTER_FORMAT  = '<|\n%s\n|>'
_DICT_JOIN_FORMAT   = ',\n'           
_DICT_ITEM_FORMAT   = '%s -> %s'      



def _enquote(thing):
    return _STRING_FORMAT % str(thing)


def _get_mma_string(
        string,
        keep_symbols=_DEFAULT_KEEP_SYMBOLS):
    
    return string if keep_symbols else _enquote(string)


def _get_mma_bool(
        boolean):
    
    return str(boolean)


def _get_mma_real(
        num,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS):
    
    if keep_ints:
        if isinstance(num, int) or type(num).__name__=='long':
            return str(num)
        if isinstance(num, float) and num.is_integer():
            return str(int(num))
    
    return format(num, '.%de' % precision).replace('e', _BASE_TEN_FORMAT)


def _get_mma_complex(
        num,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS):

    real = _get_mma_real(num.real, precision=precision, keep_ints=keep_ints)
    imag = _get_mma_real(num.imag, precision=precision, keep_ints=keep_ints)
    sign = '+' if (num.imag > 0) else '' # negative numbers already carry sign

    # MMA treats trailing I as factor, not exponent
    return _COMPLEX_FORMAT % (real, sign, imag)


def _get_mma_array(
        array,
        keep_symbols=_DEFAULT_KEEP_SYMBOLS,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS,
        single_line=True):
    
    return  _ARRAY_OUTER_FORMAT % _ARRAY_JOIN_FORMAT.join(
        get_mma(item,
                keep_symbols=keep_symbols,
                precision=precision,
                keep_ints=keep_ints,
                single_line=single_line)
        for item in array)


def _get_mma_dict(
        dic,
        key_order=None, # not passed on
        keep_symbols=_DEFAULT_KEEP_SYMBOLS,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS,
        single_line=True):
    
    items = []
    for key in (key_order if key_order else dic):
        items.append(
            ('' if single_line else _INDENT_CHAR) + 
            _DICT_ITEM_FORMAT % (
                get_mma(key,
                        keep_symbols=keep_symbols,
                        precision=precision,
                        keep_ints=keep_ints,
                        single_line=True),
                get_mma(dic[key],
                        keep_symbols=keep_symbols,
                        precision=precision,
                        keep_ints=keep_ints,
                        single_line=True)))
        
    return (_DICT_OUTER_FORMAT % _DICT_JOIN_FORMAT.join(items)).replace(
        '\n', ' ' if single_line else '\n') 


def get_mma(
        obj,
        key_order=None, # not passed on
        keep_symbols=_DEFAULT_KEEP_SYMBOLS,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS,
        single_line=False):
    '''
    Constructs a nested Mathematica expression from a python structure consisting
    of strings, numbers (including complex and py2.X longs), lists, tuples and sets
    (converted to lists) and dictionaries.
    
    key_order:    an explicit order for the keys in the passed dictionary
                  can only be given when the passed obj is a dictionary
    keep_symbols: whether python strings should be converted to Mathematica symbols,
                  else enquoted to become strings
    precision:    the number of decimal digits in scientific notation format of numbers
    keep_ints:    whether integers should be kept formatted as such, else converted to
                  scientific notation (at the precision supplied); applies to the real
                  and imaginary components of complex numbers too                 
    '''

    # check parameters are valid
    if key_order and not isinstance(obj, dict):
        raise ValueError('key_order can only be used by an outer-most dictionary')
    if key_order and any(key not in obj for key in key_order):
        raise ValueError('key_order contains a key not present in supplied dictionary')
    if key_order and any(key not in key_order for key in obj):
        raise ValueError('key_order does not contain all keys in supplied dictionary')

    # adjust object type
    if isinstance(obj, (tuple, set)):
        obj = list(obj)

    # format based on type (may recurse back to get_mma)
    if isinstance(obj, bool):
        return _get_mma_bool(obj)
    if isinstance(obj, str):
        return _get_mma_string(obj,
                               keep_symbols=keep_symbols)
    if isinstance(obj, (int, float)) or type(obj).__name__=='long':
        return _get_mma_real(obj, precision=precision,
                                  keep_ints=keep_ints)
    if isinstance(obj, complex):
        return _get_mma_complex(obj, precision=precision,
                                     keep_ints=keep_ints)
    if isinstance(obj, list):
        return _get_mma_array(obj, precision=precision,
                                   keep_ints=keep_ints,
                                   keep_symbols=keep_symbols,
                                   single_line=True)
    if isinstance(obj, dict):
        return _get_mma_dict(obj, key_order=key_order,
                                  precision=precision,
                                  keep_ints=keep_ints,
                                  keep_symbols=keep_symbols,
                                  single_line=single_line)
    
    raise TypeError("Encountered unsupported type '%s'" % type(obj).__name__)


def save_as_mma(
        obj, filename,
        key_order=None, # not passed on
        keep_symbols=_DEFAULT_KEEP_SYMBOLS,
        precision=_DEFAULT_PRECISION,
        keep_ints=_DEFAULT_KEEP_INTS):
    '''
    Constructs and writes to file a nested Mathematica expression from a python
    structure consisting of strings, numbers (including complex and py2.X longs),
    lists, tuples and sets (converted to lists) and dictionaries.
    
    key_order:    an explicit order for the keys in the passed dictionary
                  can only be given when the passed obj is a dictionary
    keep_symbols: whether python strings should be converted to Mathematica symbols,
                  else enquoted to become strings
    precision:    the number of decimal digits in scientific notation format of numbers
    keep_ints:    whether integers should be kept formatted as such, else converted to
                  scientific notation (at the precision supplied); applies to the real
                  and imaginary components of complex numbers too                 
    '''

    # generate mma string
    mma_str = get_mma(obj, key_order=key_order,
                           keep_symbols=keep_symbols,
                           precision=precision,
                           keep_ints=keep_ints)

    # save it to file (ensure direc exists)
    if ('/' in filename) or ('\\' in filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(mma_str)


def unit_tests():

    # bools
    assert get_mma(True) == 'True'

    # strings
    assert get_mma('a', keep_symbols=True) == 'a'
    assert get_mma('a', keep_symbols=False) == '"a"'

    # reals
    assert get_mma(0.12345, precision=3) == '1.235*10^-01'
    assert get_mma(50) == '50'
    assert get_mma(50, keep_ints=False, precision=2) == '5.00*10^+01'

    # complex
    assert get_mma(3-4j, keep_ints=True) == '3-4I'
    assert get_mma(3-4j, keep_ints=False, precision=2) == '3.00*10^+00-4.00*10^+00I'

    # arrays
    assert get_mma([1, 2, 3]) == '{1, 2, 3}'
    assert get_mma([1, .1], precision=3) == '{1, 1.000*10^-01}'
    assert get_mma([1,  2], precision=1, keep_ints=False) == '{1.0*10^+00, 2.0*10^+00}'
    assert get_mma([1j], keep_ints=True) == '{0+1I}'

    # tuples and sets
    assert get_mma((1, 2, 3)) == get_mma(set([1,2,3])) == get_mma([1, 2, 3])

    
    # dictionaries
    assert (get_mma({'a':True, 'b':.5},
                    key_order=['b','a'],
                    keep_symbols=True,
                    precision=2)
            == '<|\n'
               '    b -> 5.00*10^-01,\n'
               '    a -> True\n'
               '|>')
    assert (get_mma({'a':True, 'b':{'c':'d'}, 'e':[1, {'f':4}]},
                    key_order=['a', 'b', 'e'],
                    keep_symbols=True,
                    keep_ints=True)
            == '<|\n'
               '    a -> True,\n'
               '    b -> <| c -> d |>,\n'
               '    e -> {1, <| f -> 4 |>}\n'
               '|>')

    # errors
    try:
        get_mma({'a':1, 'b':2}, key_order=['a'])
        raise AssertionError
    except ValueError:
        pass

    try:
        get_mma({'a':1}, key_order=['a', 'b'])
        raise AssertionError
    except ValueError:
        pass


if __name__ == '__main__':

    unit_tests()
