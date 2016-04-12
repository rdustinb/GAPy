countDict = dict()
lineDict = dict()
"""
  These blocks parse all the warnings out of the synthesis report
  and assign them to a dictionary entry by block.
"""
with open("hstc_top.srr") as text:
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
    if(lineBlock in blockNotes):
      if(lineText not in blockNotes[lineBlock]):
        blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([lineSplit[-1].split(sep="|")[1]])
    else:
      blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]] = list()
      blockNotes[lineSplit[blockElement].strip("\"").split(sep="/")[-1]].extend([lineSplit[-1].split(sep="|")[1]])
"""
  --------------------------------------------------------------
  --------------------------------------------------------------
  --------------------------------------------------------------
"""

selectedBlockName = "all"

# Print warning counts by block
print("\n\n")
print("*"*75)
print("\t\t\tWarning Counts by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("%35s : %5d warnings"%(blockName,len(blockWarnList)))

# Print unused warnings by block
print("\n\n")
print("*"*75)
print("\t\t\tUnused Ports by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    blockUnusedCount = 0
    for warning in blockWarnList:
      if(warning.find("unused") != -1):
        print("\t%s"%(warning))

# Print undriven warnings by block
print("\n\n")
print("*"*75)
print("\t\t\tUndriven Ports by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    blockUnusedCount = 0
    for warning in blockWarnList:
      if(warning.find("Undriven") != -1):
        print("\t%s"%(warning))

# Print width mismatch warnings by block
print("\n\n")
print("*"*75)
print("\t\t\tPort-width Mismatches by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    blockUnusedCount = 0
    for warning in blockWarnList:
      if(warning.find("Port-width mismatch") != -1):
        print("\t%s"%(warning))

# Simulation mismatch warnings by block
print("\n\n")
print("*"*75)
print("\t\t\tSimulation Mismatches by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    blockUnusedCount = 0
    for warning in blockWarnList:
      if(warning.find("simulation mismatch") != -1):
        print("\t%s"%(warning))

# Prune warnings by block
print("\n\n")
print("*"*75)
print("\t\t\tRegister Prunes by HDL File")
print("*"*75)
for blockName, blockWarnList in blockWarnings.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    blockUnusedCount = 0
    for warning in blockWarnList:
      if(warning.find("Pruning") != -1):
        print("\t%s"%(warning))

# Counters by HDL File
print("\n\n")
print("*"*75)
print("\t\t\tCounters by HDL File")
print("*"*75)
for blockName, blockNoteList in blockNotes.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    for note in blockNoteList:
      if(note.find("Found counter") != -1):
        print("\t%s"%(note.split(sep="inst ")[1]))

# Comparators by HDL File
print("\n\n")
print("*"*75)
print("\t\t\tComparators by HDL File")
print("*"*75)
for blockName, blockNoteList in blockNotes.items():
  if((selectedBlockName is "all") or (blockName == selectedBlockName)):
    print("- %s -"%(blockName))
    for note in blockNoteList:
      if(note.find("comparator,") != -1):
        print("\t%s"%(note))

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
