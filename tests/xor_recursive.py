import sys

def xor(*store):
  print("---------------recursive call----------------")
  print(len(store))
  if(len(store) == 2):
    print("lowest level")
    b = store[0]
    a = store[1]
    print(b)
    print(a)
    return bool((a or b) and not(a and b))
  else:
    print("middle level")
    b = store[0]
    remaining = store[1:]
    print(b)
    print(remaining)
    return bool((xor(*remaining) or b) and not(xor(*remaining) and b))

if __name__ == '__main__':
  print("This is a testfile only, not to be used in production.")
  sys.exit()
  print("Expecting False: %s"%xor(0, 0, 0, 0)) # False
  print("Expecting True : %s"%xor(0, 0, 0, 1)) # True
  print("Expecting True : %s"%xor(0, 0, 1, 0)) # True
  print("Expecting False: %s"%xor(0, 0, 1, 1)) # False
  print("Expecting True : %s"%xor(0, 1, 0, 0)) # True
  print("Expecting False: %s"%xor(0, 1, 0, 1)) # False
  print("Expecting False: %s"%xor(0, 1, 1, 0)) # False
  print("Expecting True : %s"%xor(0, 1, 1, 1)) # True
  print("Expecting True : %s"%xor(1, 0, 0, 0)) # True
  print("Expecting False: %s"%xor(1, 0, 0, 1)) # False
  print("Expecting False: %s"%xor(1, 0, 1, 0)) # False
  print("Expecting True : %s"%xor(1, 0, 1, 1)) # True
  print("Expecting False: %s"%xor(1, 1, 0, 0)) # False
  print("Expecting True : %s"%xor(1, 1, 0, 1)) # True
  print("Expecting True : %s"%xor(1, 1, 1, 0)) # True
  print("Expecting False: %s"%xor(1, 1, 1, 1)) # False
