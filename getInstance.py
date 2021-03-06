#!/usr/local/bin/python3.4

import getopt
import sys
from os import getcwd
from os import getenv

try:
  import pyperclip
except ImportError:
  print("pyperclip (>= v1.3) is required for this tool. Please run:\n")
  print("\tpip install pyperclip\n")
  print("Also please note that on Gnome, xclip is required and on KDE klipper\n")
  print("is required for pyperclip to work correctly.\n")
  sys.exit()
  

"""
  The purpose of this script is to provide a quick pasteable instance
  code block from a target HDL file. The designer will launch this
  script with a file as an argument and this script will parse the 
  file and push the instance code into the clipboard of the OS for easy 
  pasting into another code file.
"""

###################################################
# SystemVerilog Stripping Function
def stripSv(line,portFlag,bits):
  """
    This function removes specific keywords from different lines of an
    SV file.
  """
  portDict = {
    1 : "in",
    2 : "out",
    3 : "inout"
  }
  if("//" in line):
    line,*blah = line.split("//")
  if("module" in line):
    line = line.replace("module", "")
  if("parameter" in line):
    line = line.replace("parameter", "")
  if("input" in line):
    line = line.replace("input", "")
    portFlag = 1
  if("output" in line):
    line = line.replace("output", "")
    portFlag = 2
  if("inout" in line):
    line = line.replace("inout", "")
    portFlag = 3
  if("reg" in line):
    line = line.replace("reg", "")
  if("wire" in line):
    line = line.replace("wire", "")
  if("logic" in line):
    line = line.replace("logic", "")
  if(" " in line):
    line = line.replace(" ", "")
  if("=" in line):
    line = line.replace("=", ",%")
    line,*blah = line.split("%")
  if("[" in line):
    line = line.replace("[", "%")
    line = line.replace("]", "%")
    line = line.split("%")
    newLine = ""
    newannotate = ("// %s "%(portDict[portFlag]))
    for part in line:
      if(not(":" in part)):
        if("," in part):
          part = part.replace(",","")
        newLine = newLine+part
      else:
        newannotate += ("[%s]"%(part))
    line = newLine+newannotate+","
  elif(portFlag != 0):
    line = line.replace(",", "// %s [1],"%(portDict[portFlag]))
    if(";" in line):
      line = line.replace(");", "// %s [1]);"%(portDict[portFlag]))
  return line,portFlag,bits

def structureSvInstance(stackedLine, tabSpace, alignCol, alignCom):
  """
    This function restructures an input "stacked line" module declaration
    from a .sv file. Expecting a module declaration on one line in the form
    of:
      blockName#(param1,param2,param3,...)(port1,port2,port3,...)
    or:
      blockName(port1,port2,port3,...)

    It will return a string of the form:
      blockName blockName_0 #(
        .param1             (param1),
        .param2             (param2),
        .param3             (param3),
      ...
        .paramN             (paramN)
      )(
        .port1              (port1),     // in 1 bit
        .port2              (port2),     // out 3 bits
        .port3              (port3),     // in Multidimensional Bus
      ...
        .portN              (portN)      // inout 3 bits
      );

    or:
      blockName blockName_0 (
        .port1              (port1),
        .port2              (port2),
        .port3              (port3),
      ...
        .portN              (portN)
      );
  """
  newStackedPorts = ""
  # There are parameters in this module
  if("#" in stackedLine):
    modName,remainder = stackedLine.split("#(")
    paramList,remainder = remainder.split(")(")
    paramList = paramList.split(",")
    newParams = ""
    for param in paramList:
      if(newParams == ""):
        newParams = (" "*tabSpace)
        newParams = newParams+"."+param
        newParams = newParams+(" "*(alignCol-len(param)))
        newParams = newParams+"("+param+")"
      else:
        newParams = newParams+",\n"
        newParams = newParams+(" "*tabSpace)
        newParams = newParams+"."+param
        newParams = newParams+(" "*(alignCol-len(param)))
        newParams = newParams+"("+param+")"
    paramList = newParams
    portList,remainder = remainder.split(")")
    portList = portList.split(",")
    newPorts = ""
    nextAnnotate = ""
    afterPortLen = 0
    for ports in portList:
      # Rip Out the annotation
      ports,annotate = ports.split("//")
      annotate = "//"+annotate
      if(newPorts == ""):
        newPorts = (" "*tabSpace)
        newPorts = newPorts+"."+ports
        newPorts = newPorts+(" "*(alignCol-len(ports)))
        newPorts = newPorts+"("+ports+")"
        afterPortLen = len(ports)+2
      else:
        newPorts = newPorts+(",")
        newPorts = newPorts+(" "*(alignCom-afterPortLen))
        newPorts = newPorts+("%s\n"%nextAnnotate)
        newPorts = newPorts+(" "*tabSpace)
        newPorts = newPorts+"."+ports
        newPorts = newPorts+(" "*(alignCol-len(ports)))
        newPorts = newPorts+"("+ports+")"
        afterPortLen = len(ports)+2
      nextAnnotate = annotate
    portList = newPorts+(" "*(alignCom-afterPortLen+1))
    portList = portList+("%s"%nextAnnotate)
    newStackedPorts = modName+" #(\n"+paramList+"\n) "+modName+"_0 (\n"+portList+"\n);"
    stackedLine = newStackedPorts
  else:
    modName,remainder = stackedLine.split("(")
    modName = modName+" "+modName+"_0 ("
    portList,remainder = remainder.split(")")
    portList = portList.split(",")
    newPorts = ""
    for ports in portList:
      if(newPorts == ""):
        newPorts = (" "*tabSpace)
        newPorts = newPorts+"."+ports
        newPorts = newPorts+(" "*(alignCol-len(ports)))
        newPorts = newPorts+"("+ports+")"
      else:
        newPorts = newPorts+",\n"
        newPorts = newPorts+(" "*tabSpace)
        newPorts = newPorts+"."+ports
        newPorts = newPorts+(" "*(alignCol-len(ports)))
        newPorts = newPorts+"("+ports+")"
    portList = newPorts
    newStackedPorts = modName+"\n"+portList+"\n);"
  return newStackedPorts

###################################################
# User Parse Function
def userParse(fileName, tabSpace, alignCol, alignCom):
  """
    Core of the script. Parses the user-specified HDL file and creates an
    instance block to be pasted into another HDL file.
    pyperclip.copy("No options entered")
  """
  instanceBeginning = 0
  stackedLine = ""
  portFlag = 0
  bits = 0
  with open(fileName, "r") as fh:
    for line in fh:
      if("module" in line):
        instanceBeginning = 1
        stackedLine,portFlag,bits = stripSv(line.strip(),portFlag,bits)
        if((")" in line) and not("#" in line)):
          instanceBeginning = 0
          break
      elif(instanceBeginning == 1):
        if(");" in line):
          instanceBeginning = 0
          new_sl,portFlag,bits = stripSv(line.strip(),portFlag,bits)
          stackedLine = stackedLine+new_sl
          break
        else:
          new_sl,portFlag,bits = stripSv(line.strip(),portFlag,bits)
          stackedLine = stackedLine+new_sl
  # Final String Tweaks
  if(",)" in stackedLine):
    stackedLine = stackedLine.replace(",)", ")")
  stackedLine = structureSvInstance(stackedLine,tabSpace,alignCol,alignCom)
  pyperclip.copy(stackedLine)
  #print(stackedLine)

###################################################
# Test Parse Function
def testParse():
  """
    Test Function of the script. Verifies the script works as expected.
  """
  svFileList = [
    "tests/SVFile1.sv",
    "tests/SVFile2.sv",
    "tests/SVFile3.sv",
    "tests/SVFile4.sv",
    "tests/SVFile5.sv",
    "tests/SVFile6.sv",
    "tests/SVFile7.sv",
    "tests/SVFile8.sv",
    "tests/SVFile9.sv",
    "tests/SVFile10.sv"
  ]

  for fileName in svFileList:
    print("\n\nTesting variation: %s"%fileName)
    userParse(fileName, 2, 32, 10)

###################################################
# Get the input from the terminal
try:
  args, opts = getopt.getopt(sys.argv[1:], "", ["test","path"])
  if(args == [] and opts == [] or len(opts) != 4):
    print("Invalid number of options entered. Please execute using the following")
    print("format:\n")
    print("  ./getInstance.py path/to/file.sv <tabSpace> <column align> <comment align>")
  else:
    #print("The following arguments were used: %s"%(args))
    #print("The following options were used: %s"%(opts))
    if(any("--test" in element for element in args)):
      testParse()
    elif(any("--path" in element for element in args)):
      thisScriptPath = getcwd()
      print("Current working directory is: %s"%thisScriptPath)
      shellPath = getenv("SHELL")
      print("Current shell is: %s"%shellPath)
      aliasFilePath = getenv("HOME")+"/.alias"
      with open(aliasFilePath, "a") as aliasFile:
        # Write to bash alias
        if(shellPath == "/bin/bash"):
          aliasFile.write("alias getInstance='python3 %s/getInstance.py'"%(thisScriptPath))
        # Write to csh alias
        elif(shellPath == "/bin/csh"):
          aliasFile.write("alias getInstance 'python3 %s/getInstance.py'"%(thisScriptPath))
    else:
      userParse(opts[0], int(opts[1]), int(opts[2]), int(opts[3]))
except getopt.error:
  print("That option is not supported.")
