#!/usr/local/bin/python3.4

import getopt
import sys

"""
  The purpose of this script is to provide a quick pasteable instance
  code block from a target HDL file. The designer will launch this
  script with a file as an argument and this script will parse the 
  file and push the instance code into the clipboard of the OS for easy 
  pasting into another code file.
"""

# Get the input from the terminal
try:
  
  args, opts = getopt.getopt(sys.argv[1:], "", ["path"])
  if(args == [] and opts == []):
    print("No options entered")
  else:
    print("The following arguments were used: %s"%(args))
    print("The following options were used: %s"%(opts))
except getopt.error:
  print("That option is not supported.")

