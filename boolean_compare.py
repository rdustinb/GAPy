#!/usr/bin/python
from math import log2
import time

'''
  User-supplied Boolean Equations to compare

  Example:
    eq0 = lambda x: not(x[0] or x[1] and (x[2] and x[3]))
    eq1 = lambda x: and(not(x[0]) or x[1] or x[2] or x[3])
'''
eq0 = lambda x: (
  x[0] and x[1] and x[2] and x[3] and x[4] and x[5] and x[6] and x[7] and
  x[8] and x[9] and x[10] and x[11] and x[12] and x[13] and x[14] and x[15] and
  x[16] and x[17] and x[18] and x[19] and x[20] and x[21] and x[22] and x[23] and
  x[24] and x[25] and x[26] and x[27] and x[28] and x[29] and x[30] and x[31]
)

eq1 = lambda x: not(
  not(x[0]) or not(x[1]) or not(x[2]) or not(x[3]) or not(x[4]) or
  not(x[5]) or not(x[6]) or not(x[7]) or not(x[8]) or not(x[9]) or
  not(x[10]) or not(x[11]) or not(x[12]) or not(x[13]) or not(x[14]) or
  not(x[15]) or
  not(x[16]) or not(x[17]) or not(x[18]) or not(x[19]) or not(x[20]) or
  not(x[21]) or not(x[22]) or not(x[23]) or not(x[24]) or not(x[25]) or
  not(x[26]) or not(x[27]) or not(x[28]) or not(x[29]) or not(x[30]) or
  not(x[31])
)

'''
  Bench marking of checking all space of a particular bit size is as follows:

    8-bits    ~135 micro-seconds
    16-bits   ~0.584 seconds
    32-bits   ~62862 seconds

  Yes, python is not very efficient for boolean algebraic functions but this
  script was developed to allow a designer to fairly quickly compare two
  boolean equations across the entire space of a bit vector.
'''

def regress_boolean_values(maxValue):
  '''
    Regressively test all values in a boolean reduction equation, comparing its 
    results with another boolean reduction equation. All equations must reduce
    to a single bit.
  '''
  return_val = 0
  for count, result1, result2 in pair_result(maxValue):
    if(result1 != result2):
      print("Error >> Logical arithmetic failed with input: %i" % (count))
      return_val = 1
  return return_val

def pair_result(maxValue):
  '''
    Iterator function, returns the result from each of the two defined boolen
    equations reducing memory usage.
  '''
  for x in range(maxValue):
    x_vect = format(x, ('0%sb'%(int(log2(maxValue)))))
    x_vect = [bool(int(i)) for i in x_vect]
    # y = eval(eq1%tuple(x_vect))
    # z = eval(eq2%tuple(x_vect))
    y = eq0(x_vect)
    z = eq1(x_vect)
    yield x, y, z

def xor(*store):
  '''
  Description
    Dynamic XOR function for boolean algebra. It is a recursive call that
    the user may input any number of 1s and/or 0s.
  
  Usage
    xor(<bit n>, <bit n-1>, ... , <bit 2>, <bit 1>, <bit 0>)
  
  Example
    xor(1, 0, 1, 0, 0, 1)
    This would represent the binary number: b101001
    Or the hexidecimal number: 0x29
  
  Returns
    Boolean
  '''
  if(len(store) == 2):
    b = store[0]
    a = store[1]
    return bool((a or b) and not(a and b))
  else:
    b = store[0]
    remaining = store[1:]
    return bool((xor(*remaining) or b) and not(xor(*remaining) and b))


# Example 32-bit Boolean
start_time = time.time()
if(regress_boolean_values(4294967296) == 0):
  print("All tests passed!")
print(time.time() - start_time)
