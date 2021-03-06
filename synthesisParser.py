"""
  Todo:
    Add block that checks the count of translate_on/translate_off directives in each file.
"""

"""
  Check for correct Python Version.
"""
import sys

if sys.hexversion < 0x03020000:
  raise Exception("This tool requires python 3.2 or greater.")

import os
import re
from getopt import getopt
from subprocess import Popen, PIPE
from shlex import split

def usage():
  """
    Single function for displaying how this script is used.
  """
  print("Usage:\n")
  print("\tsynthesisParser -i <path/to/srr/file>.srr [-f <design module file name, or 'all'>]")
  print("\t\t[--rawwarnings|--onlycounts|--onlyunusedports|--onlyundrivenports|--onlyportwidthmismatches|")
  print("\t\t--onlysimulationmismatches|--onlyunusedsignals|--onlyregisterprunes|--onlyequivalencyprunes|")
  print("\t\t--onlyblackboxes|--onlysensitivitylists|--onlysynthesisdirectives|--onlyconstraints|")
  print("\t\t--onlyregisterreplicated|--onlycounters|--onlycomparators]")
  print("\t\t[--dontprintemptymodules]\n")
  print("\n")
  print("\t--rawwarnings\t\t\tGroups all warnings found in the srr file by module name without further")
  print("\t\t\t\t\tprocessing.")
  print("\n")
  print("\t--onlycounts\t\t\tPrints all module names that are found in the srr file and displays total")
  print("\t\t\t\t\twarnings for each.")
  print("\t--onlyunusedports\t\tPrints only the warnings detected regarding unused ports in a module.")
  print("\t--onlyundrivenports\t\tPrints only the warnings detected regarding undriven ports in a module.")
  print("\t--onlyportwidthmismatches\tPrints only the warnings detected regarding port width mismatches")
  print("\t\t\t\t\tof assigned nets to a module's ports.")
  print("\t--onlysimulationmismatches\tPrints only the warnings detected regarding other occurences of warnings")
  print("\t\t\t\t\tthan those above the tool determines could cause a simulation and actual")
  print("\t\t\t\t\thardware mismatch in a module.")
  print("\t--onlyunusedsignals\t\tPrints only the warnings detected regarding unused but declared signals")
  print("\t\t\t\t\tin a module.")
  print("\t--onlyregisterprunes\t\tPrints only the warnings detected regarding register pruning that occurs")
  print("\t\t\t\t\tdue to optimization in a module.")
  print("\t--onlyequivalencyprunes\t\tPrints only the warnings detected regarding logic cells in a module that")
  print("\t\t\t\t\tare determined by the synthesis tool to be equivalent to other logic cells")
  print("\t\t\t\t\tthroughout the design and are thus pruned.")
  print("\t--onlyblackboxes\t\tPrints only the warnings detected regarding black boxes within a module.")
  print("\t--onlysensitivitylists\t\tPrints only the warnings detected regarding incomplete sensitivity")
  print("\t\t\t\t\tlists within a module.")
  print("\t--onlysynthesisdirectives\tPrints only the warnings detected regarding any synthesis directives")
  print("\t\t\t\t\tused within a module. No printouts mean all directives in a module were")
  print("\t\t\t\t\tapplied correctly.")
  print("\t--onlyconstraints\t\tPrints only the warnings detected regarding constraints applied to a")
  print("\t\t\t\t\tdesign limiting this section to an SDC or PDC file.")
  print("\n")
  print("\t--onlyregisterreplicated\tPrints only the notes detected regarding replicated registers in a")
  print("\t\t\t\t\tmodule. No printouts mean all registers within a module were not replicated.")
  print("\t--onlycounters\t\t\tPrints all counters detected by the synthesis tool within a module.")
  print("\t--onlycomparators\t\tPrints all comparators detected by the synthesis tool within a module.")
  print("\n")
  print("\t--dontprintemptymodules\t\tThis flag limits the printouts per section to only those modules")
  print("\t\t\t\t\tthat contain respective section warnings or notes.")

"""
  Parse Terminal Arguments with property flags
"""
limited_report = 0
limited_options = []
empty_module_limit_print = 0
srr_file = ""
selectedBlockName = "all"
try:
  opts,args = getopt(sys.argv[1:], "hi:f:", ["rawwarnings","onlycounts","onlyunusedports","onlyundrivenports","onlyportwidthmismatches","onlysimulationmismatches","onlyunusedsignals","onlyregisterprunes","onlyequivalencyprunes","onlyblackboxes","onlysensitivitylists","onlysynthesisdirectives","onlyregisterreplicated","onlycounters","onlycomparators","onlyconstraints","dontprintemptymodules"])
except:
  usage()
  sys.exit()

# Go through all options passed from the terminal
for o, a in opts:
  if o == "-h":
    usage()
    sys.exit()
  elif o in ("--rawwarnings","--onlycounts","--onlyunusedports","--onlyundrivenports","--onlyportwidthmismatches","--onlysimulationmismatches","--onlyunusedsignals","--onlyregisterprunes","--onlyequivalencyprunes","--onlyblackboxes","--onlysensitivitylists","--onlysynthesisdirectives","--onlyregisterreplicated","--onlycounters","--onlycomparators","--onlyconstraints"):
    limited_options.append(o)
    limited_report = 1
  elif o in ("--dontprintemptymodules"):
    empty_module_limit_print = 1
  elif o == "-i":
    srr_file = a
  elif o == "-f":
    selectedBlockName = a

# Quit if there is no SRR File defined
if srr_file == "":
  # This might provide an interactive inline prompter but for now just print current usage
  usage()
  sys.exit()

"""
  These blocks parse all the warnings out of the synthesis report
  and assign them to a dictionary entry by block.
"""
countDict = dict()
lineDict = dict()

lineCount = 0

try:
  with open(srr_file) as text:
    try:
      for line in text:
        lineCount += 1
        line = line.strip()
        if(line.find(":") != -1):
          lineSplit = line.split(sep=":", maxsplit=6)
          if(str(len(lineSplit)) in countDict):
            countDict[str(len(lineSplit))] = countDict[str(len(lineSplit))] + 1
            lineDict[str(len(lineSplit))].extend([line])
          else:
            countDict[str(len(lineSplit))] = 1
            lineDict[str(len(lineSplit))] = list()
            lineDict[str(len(lineSplit))].extend([line])
        else:
          if("0" in countDict):
            countDict["0"] = countDict["0"] + 1
            lineDict["0"].extend([line])
          else:
            countDict["0"] = 1
            lineDict["0"] = list()
            lineDict["0"].extend([line])
    except UnicodeDecodeError:
      print("")
      print("Encoding error just after line %d"%(lineCount))
      print("\tThis is a known issue where Synplify Pro prints non-UTF8 encoded characters to the logfile.")
      print("\tThe fix is to replace the illegal characters with legal characters and rerun this script.")
      sys.exit(-1)
except FileNotFoundError:
  print("")
  print("Whoops, that srr file was not found. Please check your path and try again!")
  sys.exit(-1)

# Parse the warnings
blockWarnings = dict()
blockNotes = dict()
for line in lineDict["7"]:
  if(line.find("@W") != -1):
    lineSplit = line.split(sep=":", maxsplit=6)
    lineBlock = lineSplit[2].strip("\"").split(sep="/")[-1]
    lineText = lineSplit[-1].split(sep="|")[1]
    if(lineBlock in blockWarnings):
      if(lineText not in blockWarnings[lineBlock]):
        blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]].extend([lineSplit[-1].split(sep="|")[1]])
    else:
      blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]] = list()
      blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]].extend([lineSplit[-1].split(sep="|")[1]])
  elif(line.find("@N") != -1):
    lineSplit = line.split(sep=":", maxsplit=5)
    blockElement = 1
    # Because the notes can come in two different flavors, determine which this 
    # line is a part of
    if(lineSplit[blockElement].find("\"") != -1):
      # No note number
      lineBlock = lineSplit[blockElement].strip("\"").split(sep="/")[-1]
    elif(lineSplit[blockElement+1].find("\"") != -1):
      blockElement = 2
      # Note number, formatted like a warning, resplit the line
      lineSplit = line.split(sep=":", maxsplit=6)
      lineBlock = lineSplit[blockElement].strip("\"").split(sep="/")[-1]
    lineText = lineSplit[-1].split(sep="|")[1]
    lineText = re.sub(r'view:work.+inst ', 'inst ', lineText)
    # Some notes should be warnings
    if(lineText.find("is unused") != -1):
      if(lineBlock in blockWarnings):
        if(lineText not in blockWarnings[lineBlock]):
          blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]].extend([lineText])
      else:
        blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]] = list()
        blockWarnings[lineSplit[2].strip("\"").split(sep="/")[-1]].extend([lineText])
    else:
      if(lineBlock in blockNotes):
        if(lineText not in blockNotes[lineBlock]):
          blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([lineText])
      else:
        blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]] = list()
        blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([lineText])

if("6" in lineDict.keys()):
  for line in lineDict["6"]:
    if(line.find("@W") != -1):
      lineSplit = line.split(sep=":", maxsplit=5)
      lineBlock = lineSplit[1].strip("\"").split(sep="/")[-1]
      lineText = lineSplit[-1].split(sep="|")[1]
      lineText = lineText.strip()
      if(lineBlock in blockWarnings):
        if(lineText not in blockWarnings[lineBlock]):
          blockWarnings[lineSplit[1].strip("\"").split(sep="/")[-1]].extend([lineText])
      else:
        blockWarnings[lineSplit[1].strip("\"").split(sep="/")[-1]] = list()
        blockWarnings[lineSplit[1].strip("\"").split(sep="/")[-1]].extend([lineText])
"""
  --------------------------------------------------------------
  --------------------------------------------------------------
  --------------------------------------------------------------
"""
if "--rawwarnings" in  limited_options:
  # Print unused warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tRaw Warnings by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find('Pruning') != -1):
              warning = re.sub(' -- not in use ...', '', warning)
              print("\t%s"%(warning))
            elif(warning.find('black box') != -1):
              warning = re.sub('Creating black box for empty module ', '', warning)
              print("\t%s"%(warning))
            elif(warning.find("it is equivalent to") != -1):
              warning = re.sub('To keep the instance, apply constraint syn_preserve=1 on the instance.', '', warning)
              print("\t%s"%(warning))
            else:
              print("\t%s"%(warning))

if "--onlycounts" in  limited_options or limited_report == 0:
  # Print warning counts by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tWarning Counts by HDL File")
  print("*"*75)
  maxnamesize = 0
  maxwarncount=0
  fieldindex = 0
  for blockName, blockWarnList in blockWarnings.items():
    if((selectedBlockName == "all") or (blockName == selectedBlockName)):
      if(len(blockName) > maxnamesize):
        maxnamesize = len(blockName)
      if(len(blockWarnList) > maxwarncount):
        maxwarncount = len(blockWarnList)
  maxwarncount = len(str(maxwarncount))
  maxnamesize += 2
  for blockName, blockWarnList in blockWarnings.items():
    if((selectedBlockName == "all") or (blockName == selectedBlockName)):
      #print(
      sys.stdout.write(
        '{filename:>{filefieldsize}} : {warncount:<{warnfieldsize}}  '.format(
          filename=blockName,
          filefieldsize=maxnamesize,
          warncount=len(blockWarnList),
          warnfieldsize=maxwarncount
        )
      )
      if (fieldindex == 3):
        print("")
        fieldindex = 0
      elif (fieldindex == 2 and maxnamesize > 15):
        print("")
        fieldindex = 0
      elif (fieldindex == 1 and maxnamesize > 40):
        print("")
        fieldindex = 0
      elif (fieldindex == 0 and maxnamesize > 80):
        print("")
        fieldindex = 0
      else:
        fieldindex += 1

if "--onlyunusedports" in  limited_options or limited_report == 0:
  thisKeyword = "is unused"
  # Print unused warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUnused Ports by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              print("\t%s"%(warning))

if "--onlyundrivenports" in  limited_options or limited_report == 0:
  thisKeyword = "Undriven"
  # Print undriven warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUndriven Ports by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              print("\t%s"%(warning))

if "--onlyportwidthmismatches" in  limited_options or limited_report == 0:
  thisKeyword = "Port-width mismatch"
  # Print width mismatch warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tPort-width Mismatches by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              print("\t%s"%(warning))

if "--onlysimulationmismatches" in  limited_options or limited_report == 0:
  thisKeyword = "imulation mismatch"
  # Simulation mismatch warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tSimulation Mismatches by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              print("\t%s"%(warning))

if "--onlyunusedsignals" in  limited_options or limited_report == 0:
  thisKeyword = "not assigned"
  # Simulation mismatch warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUnassigned Signals by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              print("\t%s"%(warning))

if "--onlyregisterprunes" in  limited_options or limited_report == 0:
  thisKeyword = "Pruning"
  # Prune warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tRegister Prunes by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              # Tweaks before printout
              warning = re.sub(' -- not in use ...', '', warning)
              print("\t%s"%(warning))

if "--onlyequivalencyprunes" in  limited_options or limited_report == 0:
  thisKeyword = "it is equivalent to"
  # Prune warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tPrunes Due to Equivalency by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              # Tweaks before printout
              warning = re.sub('To keep the instance, apply constraint syn_preserve=1 on the instance.', '', warning)
              warning = re.sub('Removing ', '', warning)
              warning = re.sub('user instance ', '', warning)
              warning = re.sub('sequential instance ', '', warning)
              warning = re.sub(',  because it is equivalent to instance ', ' -- EQUIVALENT --> ', warning)
              print("\t%s"%(warning))

if "--onlyblackboxes" in  limited_options or limited_report == 0:
  thisKeyword = 'black box'
  thatKeyword = 'Blackbox'
  # Black Box warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tBlack Boxes by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thatKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              # Tweaks before printout
              print("\t%s"%(warning))
            elif(warning.find(thatKeyword) != -1):
              print("\t%s"%(warning))

if "--onlysensitivitylists" in  limited_options or limited_report == 0:
  thisKeyword = "Incomplete sensitivity list"
  # Sensitivity List warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tIncomplete Sensitivity Lists by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              # Tweaks before printout
              #warning = re.sub('', '', warning)
              print("\t%s"%(warning))

if "--onlysynthesisdirectives" in  limited_options or limited_report == 0:
  thisKeyword = "Unrecognized synthesis directive"
  # Sensitivity List warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUnrecognized Synthesis Directives by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockWarnList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for warning in blockWarnList:
            if(warning.find(thisKeyword) != -1):
              # Tweaks before printout
              #warning = re.sub('', '', warning)
              print("\t%s"%(warning))

if "--onlyconstraints" in  limited_options or limited_report == 0:
  # Print unused warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tInvalid Synthesis Constraints")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          print("\t%s"%(warning))

if "--onlyregisterreplicated" in  limited_options or limited_report == 0:
  thisKeyword = "replicated"
  # Prune warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tRegister Replications by HDL File")
  print("*"*75)
  for blockName, blockNoteList in blockNotes.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockNoteList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for note in blockNoteList:
            if(note.find(thisKeyword) != -1):
              print("\t%s"%(note))

if "--onlycounters" in  limited_options or limited_report == 0:
  thisKeyword = "Found counter"
  # Counters by HDL File
  print("\n\n")
  print("*"*75)
  print("\t\t\tCounters by HDL File")
  print("*"*75)
  try:
    for blockName, blockNoteList in blockNotes.items():
      if(".sdc" not in blockName):
        if((selectedBlockName == "all") or (blockName == selectedBlockName)):
          if((empty_module_limit_print == 1 and len([x for x in blockNoteList if x.find(thisKeyword) != -1]) > 0) or
          (empty_module_limit_print == 0)):
            print("- %s -"%(blockName))
            for note in blockNoteList:
              if(note.find(thisKeyword) != -1):
                if("inst " in note):
                  print("\t%s"%(note.split(sep="inst ")[1]))
                elif("instance " in note):
                  print("\t%s"%(note.split(sep="instance ")[1]))
  except IndexError:
    print("Index is invalid in the Counters note.")

if "--onlycomparators" in  limited_options or limited_report == 0:
  thisKeyword = "comparator,"
  # Comparators by HDL File
  print("\n\n")
  print("*"*75)
  print("\t\t\tComparators by HDL File")
  print("*"*75)
  for blockName, blockNoteList in blockNotes.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        if((empty_module_limit_print == 1 and len([x for x in blockNoteList if x.find(thisKeyword) != -1]) > 0) or
        (empty_module_limit_print == 0)):
          print("- %s -"%(blockName))
          for note in blockNoteList:
            if(note.find(thisKeyword) != -1):
              print("\t%s"%(note))

print("\n\n")

p1 = Popen(['wc','-l',srr_file], stdout=PIPE)
p2 = Popen(split("awk '{print $1}'"), stdin=p1.stdout, stdout=PIPE)

expLineCount = str(p2.communicate()[0]).strip("b\\n'")

if(int(expLineCount) != int(lineCount)):
  print("Error > Parsed line count does not match actual length of srr file.")

print("Parsed %s lines from the srr file."%(lineCount))
print("Expected %s lines from the srr file."%(expLineCount))

print("\n")

# Get the split counts
#for i,v in countDict.items():
#  print("%2s : %5d"%(i,v))
# 1 Split
# None

# 2 Splits
# Simple informationals about files or synthesis. Also information about the
# build environment.

# 3 Splits
# Simple informationals about files or synthesis. Has a double-colon at the
# beginning of the line.

# 4 Splits
# Complete instance removal, actually batched with the 2 split as there are
# extra delimeters in the last field.

# 5 Splits
# Process Times only (from what I've seen so far)

# 6 Splits
# Standard Warnings, Notes, Informationals or Errors without a particular
# W/N/I/E numbers

# 7 Splits
# Standard Warning, Error, Information and Note field count

# >7 Splits
# Standard Warning, Error, Information and Note field count with the last field
# containing some extra delimeters that should be ignored.
