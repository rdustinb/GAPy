#!/usr/local/bin/python3.4

import getopt
import sys
from os import getcwd
from os import getenv
import re

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
# This function creates a formatted instance based on the user input
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

###################################################
# This function creates a formatted instance based on the user input
def yankSvModule(fileName):
  """
    The purpose of this function is to pull out the full module declaration
    in an SV file and return it as a single line without whitespace
  """
  stackedModule = ""
  moduleName = ""
  instanceName = ""
  mode = "start"
  portDir = ""
  inModule = 0
  parameterRegEx = re.compile("^\s*parameter")
  inputRegEx = re.compile("^\s*input")
  outputRegEx = re.compile("^\s*output")
  inoutRegEx = re.compile("^\s*inout")
  closeRegEx = re.compile("^\s*\);")
  paramport1RegEx = re.compile("^\s*\)\s*\(")
  paramport2RegEx = re.compile("\s*\)\s*\(")
  modendRegEx = re.compile("\);")
  with open(fileName, "r") as fh:
    for line in fh:
      """
        There are two ways that a module can be declared in SystemVerilog:
          1) Module on one line (V95 Syntax).
          2) Module on multiple lines.

        This script will not support stupid syntax and bad coding that looks
        like shit. Properly format your code or this won't work.
      """
      # Rip out any comments
      if("//" in line):
        line,*blah = line.split("//")
      # This is somewhat bad coding, module declaration on one line
      if(("module" in line) and (");" in line)):
        pass
      elif(("module" in line) and not("#" in line) and not(");" in line)):
        moduleName = line.replace("("," ")
        moduleName = moduleName.replace("module"," ")
        moduleName = moduleName.strip()
        instanceName = moduleName+"_0"
        stackedModule = moduleName+" "+instanceName+" ("
        mode = "ports"
      # This is the best coding style, module declaration is on its own line
      elif(("module" in line) and ("#" in line) and not(");" in line)):
        moduleName = line.replace("#"," ")
        moduleName = moduleName.replace("("," ")
        moduleName = moduleName.replace("module"," ")
        moduleName = moduleName.strip()
        instanceName = moduleName+"_0"
        stackedModule = moduleName+" #("
        mode = "params"
      # Parsing Parameters
      elif(mode == "params"):
        # Check for parameter-port boundary-only line
        if(paramport1RegEx.match(line)):
          mode = "ports"
          stackedModule = stackedModule[:-1]+") "+instanceName+" ("
          continue
        elif(paramport2RegEx.match(line)):
          mode = "ports"
          # Handle Input Ports
          if(parameterRegEx.match(line)):
            line = re.sub(parameterRegEx,"",line)
          if("=" in line):
            line,*blah = line.split("=")
          line = line.replace(","," ")
          line = line.strip()
          stackedModule = stackedModule+line+") "+instanceName+" ("
        else:
          # Handle Input Ports
          if(parameterRegEx.match(line)):
            line = re.sub(parameterRegEx,"",line)
          if("=" in line):
            line,blah = line.split("=")
          line = line.replace(","," ")
          line = line.strip()
          stackedModule = stackedModule+line+","
      # Parsing Ports
      elif(mode == "ports"):
        # Check for module declaration ending-only line
        if(closeRegEx.match(line)):
          break
        # Handle Input Ports
        if(inputRegEx.match(line)):
          portDir = "input"
          line = re.sub(inputRegEx,"",line)
        # Handle Output Ports
        elif(outputRegEx.match(line)):
          portDir = "output"
          line = re.sub(outputRegEx,"",line)
        # Handle Inout Ports
        elif(inoutRegEx.match(line)):
          portDir = "inout"
          line = re.sub(inoutRegEx,"",line)
        # If we just switched from params
        if(mode == "params"):
          mode = "ports"
          stackedModule = stackedModule[:-1]+") "+instanceName+" ("
        elif(mode == "module"):
          mode = "ports"
          stackedModule = moduleName+"_0 ("
        line = re.sub(outputRegEx,"",line)
        line = line.strip()
        line = line.replace("reg","")
        if(line.count(",") > 1):
          line = line.split(",")
          for sline in line:
            if(sline == ""):
              continue
            else:
              sline = sline.replace(",","")
              sline = sline.replace(" ","")
              # Check for bus or single bit
              if("[" in sline):
                # Split on left brackets
                pass
              else:
                stackedModule = stackedModule+sline+"//~"+portDir+"~1~bit,"
        else:
          line = line.replace(",","")
          line = line.replace(" ","")
           # Check for bus or single bit
          if("[" in line):
            line = line.replace("][","~")
            line = line.replace("]","~")
            line = line.replace("[","~")
            fields = line.split("~")
            portName = ""
            portWidths = ""
            for field in fields:
              if(":" not in field):
                portName = field
              else:
                end,start = field.split(":")
                if(end.isdigit()):
                  end = str(int(end) + 1)
                portWidths = portWidths+end+"~"
            portWidths = portWidths[:-1]
            stackedModule = stackedModule+portName+"//~"+portDir+"~"
            stackedModule = stackedModule+portWidths+"~bits,"
          else:
            stackedModule = stackedModule+line+"//~"+portDir+"~1~bit,"
        # If this line contains the module declaration characters, break
        if(");" in stackedModule):
          stackedModule = stackedModule[:-1].replace(");","")
          break;
  print(stackedModule)
  print(moduleName)

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
  yankSvModule(fileName)
  # Copy Instance to Clipboard
  pyperclip.copy(stackedLine)

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

