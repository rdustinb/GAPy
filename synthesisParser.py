"""
  Check for correct Python Version.
"""
import os
import sys
import re
if sys.hexversion < 0x03020000:
  raise Exception("This tool requires python 3.2 or greater.")

def usage():
  """
    Single function for displaying how this script is used.
  """
  print("Usage:\n")
  print("\tsynthesisParser -i <path/to/srr/file>.srr -f <design module file name, or 'all'>\n")
  print("Optional customizations that limit the report to only one of the types of report blocks:\n")
  print("\t--onlycounts")
  print("\t--onlyunusedports")
  print("\t--onlyundrivenports")
  print("\t--onlyportwidthmismatches")
  print("\t--onlysimulationmismatches")
  print("\t--onlyregisterreplicated")
  print("\t--onlyregisterprunes")
  print("\t--onlyblackboxes")
  print("\t--onlycounters")
  print("\t--onlycomparators")
  print("\t--onlyconstraints")

"""
  Parse Terminal Arguments with propery flags
"""
limited_report = 0
limited_options = []
srr_file = ""
selectedBlockName = "all"
from getopt import getopt
try:
  opts,args = getopt(sys.argv[1:], "hi:f:", ["onlycounts","onlyunusedports","onlyundrivenports","onlyportwidthmismatches","onlysimulationmismatches","onlyregisterreplicated","onlyregisterprunes","onlyblackboxes","onlycounters","onlycomparators","onlyconstraints"])
except:
  usage()
  sys.exit()

# Go through all options passed from the terminal
for o, a in opts:
  if o == "-h":
    usage()
    sys.exit()
  elif o in ("--onlycounts","--onlyunusedports","--onlyundrivenports","--onlyportwidthmismatches","--onlysimulationmismatches","--onlyregisterreplicated","--onlyregisterprunes","--onlyblackboxes","--onlycounters","--onlycomparators","--onlyconstraints"):
    limited_options.append(o)
    limited_report = 1
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

with open(srr_file) as text:
  for line in text:
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
    if(lineBlock in blockNotes):
      if(lineText not in blockNotes[lineBlock]):
        blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([re.sub(r'view:work.+inst ', 'inst ', lineSplit[-1].split(sep="|")[1])])
    else:
      blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]] = list()
      blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([re.sub(r'view:work.+inst ', 'inst ', lineSplit[-1].split(sep="|")[1])])
"""
  --------------------------------------------------------------
  --------------------------------------------------------------
  --------------------------------------------------------------
"""
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
  # Print unused warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUnused Ports by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("unused") != -1):
            print("\t%s"%(warning))

if "--onlyundrivenports" in  limited_options or limited_report == 0:
  # Print undriven warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tUndriven Ports by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("Undriven") != -1):
            print("\t%s"%(warning))

if "--onlyportwidthmismatches" in  limited_options or limited_report == 0:
  # Print width mismatch warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tPort-width Mismatches by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("Port-width mismatch") != -1):
            print("\t%s"%(warning))

if "--onlysimulationmismatches" in  limited_options or limited_report == 0:
  # Simulation mismatch warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tSimulation Mismatches by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("simulation mismatch") != -1):
            print("\t%s"%(warning))

if "--onlyregisterreplicated" in  limited_options or limited_report == 0:
  # Prune warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tRegister Replications by HDL File")
  print("*"*75)
  for blockName, blockNoteList in blockNotes.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for note in blockNoteList:
          if(note.find("replicated") != -1):
            print("\t%s"%(note))

if "--onlyregisterprunes" in  limited_options or limited_report == 0:
  # Prune warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tRegister Prunes by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("Pruning") != -1):
            # Tweaks before printout
            warning = re.sub(' -- not in use ...', '', warning)
            print("\t%s"%(warning))

if "--onlyblackboxes" in  limited_options or limited_report == 0:
  # Black Box warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tBlack Boxes by HDL File")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for warning in blockWarnList:
          if(warning.find("black box") != -1):
            # Tweaks before printout
            warning = re.sub('Creating black box for empty module ', '', warning)
            print("\t%s"%(warning))

if "--onlycounters" in  limited_options or limited_report == 0:
  # Counters by HDL File
  print("\n\n")
  print("*"*75)
  print("\t\t\tCounters by HDL File")
  print("*"*75)
  try:
    for blockName, blockNoteList in blockNotes.items():
      if(".sdc" not in blockName):
        if((selectedBlockName == "all") or (blockName == selectedBlockName)):
          print("- %s -"%(blockName))
          for note in blockNoteList:
            if(note.find("Found counter") != -1):
              if("inst " in note):
                print("\t%s"%(note.split(sep="inst ")[1]))
              elif("instance " in note):
                print("\t%s"%(note.split(sep="instance ")[1]))
  except IndexError:
    print("Index is invalid in the Counters note.")

if "--onlycomparators" in  limited_options or limited_report == 0:
  # Comparators by HDL File
  print("\n\n")
  print("*"*75)
  print("\t\t\tComparators by HDL File")
  print("*"*75)
  for blockName, blockNoteList in blockNotes.items():
    if(".sdc" not in blockName):
      if((selectedBlockName == "all") or (blockName == selectedBlockName)):
        print("- %s -"%(blockName))
        for note in blockNoteList:
          if(note.find("comparator,") != -1):
            print("\t%s"%(note))

if "--onlyconstraints" in  limited_options or limited_report == 0:
  # Print unused warnings by block
  print("\n\n")
  print("*"*75)
  print("\t\t\tInvalid Synthesis Constraints")
  print("*"*75)
  for blockName, blockWarnList in blockWarnings.items():
    if((".sdc" in blockName) and (blockName == selectedBlockName)):
      print("- %s -"%(blockName))
      for warning in blockWarnList:
        if(warning.find("not found in netlist") != -1):
          print("\t%s"%(warning))

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
