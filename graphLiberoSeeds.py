import sys
import glob

target = "flt"
design_name = "my_design"

DEBUG = False

folderToSearch = "pnr/%s/%s_build/designer/%s/"%(target,target,design_name)
listOfMaxFiles = glob.glob(folderToSearch+"*timing_violations_max*")
listOfMinFiles = glob.glob(folderToSearch+"*timing_violations_min*")

# Check that there is at least 1 Max Violations file...
if len(listOfMaxFiles) == 0:
  print("\n\nError > there are no Max timing violations files in '%s'\n"%(folderToSearch))
  sys.exit(-1)

# Check that there is at least 1 Min Violations file...
if len(listOfMinFiles) == 0:
  print("\n\nError > there are no Min timing violations files in '%s'\n"%(folderToSearch))
  sys.exit(-1)

###############################################################################
# Max Violations
# Get the first violation Slack, total failing paths, per seed file
###############################################################################
thisMaxData = dict() # seed# : (worstSlack, totalNegativeSlack, totalPaths), ...
for thisFile in listOfMaxFiles:
  thisFileSeed = int(thisFile.split("_")[-1].split(".")[0].strip("s"))
  # Individual File
  with open(thisFile, 'r') as fh:
    for thisLine in fh:
      # Fetch the "Slack (ns):" line
      if thisLine.find("Slack (ns):") != -1:
        # Only parse negative slack values...
        if thisLine.find("-") != -1:
          # Format the Slack value, make it abs()
          thisSlack = float(thisLine.split("-")[1].strip())
          # Create the dictionary entry if it doesn't exist
          if thisFileSeed not in thisMaxData.keys():
            thisMaxData[thisFileSeed] = (thisSlack, thisSlack, 1)
          # Add to the current Tuple values
          else:
            tmpWorstSlack = thisMaxData[thisFileSeed][0]
            # Is the Slack greater than what is already stored?
            if thisMaxData[thisFileSeed][0] < thisSlack:
              tmpWorstSlack = thisSlack
            # Increment the Total Negative Slack
            tmpTotalNegativeSlack = thisMaxData[thisFileSeed][1] + thisSlack
            # Increment the Total Paths
            tmpTotalPaths = thisMaxData[thisFileSeed][2] + 1
            # Update Tuple
            thisMaxData[thisFileSeed] = (tmpWorstSlack, tmpTotalNegativeSlack, tmpTotalPaths)
        else:
          continue
      else:
        continue

###############################################################################
# Min Violations
# Get the first violation Slack, total failing paths, per seed file
###############################################################################
thisMinData = dict() # seed# : (worstSlack, totalNegativeSlack, totalPaths), ...
for thisFile in listOfMinFiles:
  thisFileSeed = int(thisFile.split("_")[-1].split(".")[0].strip("s"))
  # Individual File
  with open(thisFile, 'r') as fh:
    for thisLine in fh:
      # Fetch the "Slack (ns):" line
      if thisLine.find("Slack (ns):") != -1:
        # Only parse negative slack values...
        if thisLine.find("-") != -1:
          # Format the Slack value, make it abs()
          thisSlack = float(thisLine.split("-")[1].strip())
          # Create the dictionary entry if it doesn't exist
          if thisFileSeed not in thisMinData.keys():
            thisMinData[thisFileSeed] = (thisSlack, thisSlack, 1)
          # Add to the current Tuple values
          else:
            tmpWorstSlack = thisMinData[thisFileSeed][0]
            # Is the Slack greater than what is already stored?
            if thisMinData[thisFileSeed][0] < thisSlack:
              tmpWorstSlack = thisSlack
            # Increment the Total Negative Slack
            tmpTotalNegativeSlack = thisMinData[thisFileSeed][1] + thisSlack
            # Increment the Total Paths
            tmpTotalPaths = thisMinData[thisFileSeed][2] + 1
            # Update Tuple
            thisMinData[thisFileSeed] = (tmpWorstSlack, tmpTotalNegativeSlack, tmpTotalPaths)
        else:
          continue
      else:
        continue

if DEBUG: print(thisMaxData)
if DEBUG: print(thisMinData)

if DEBUG: print("Total entries in Max: %s"%(len(thisMaxData.keys())))
if DEBUG: print("Total entries in Min: %s"%(len(thisMinData.keys())))

###############################################################################
# Normalize the Dictionaries
###############################################################################
# If Seeds in Max but not Min
for thisSeed in thisMaxData.keys():
  if thisSeed not in thisMinData.keys():
    thisMinData[thisSeed] = (0.0, 0.0, 0)

# If Seeds in Min but not Max
for thisSeed in thisMinData.keys():
  if thisSeed not in thisMaxData.keys():
    thisMaxData[thisSeed] = (0.0, 0.0, 0)

if DEBUG: print(thisMaxData)
if DEBUG: print(thisMinData)

if DEBUG: print("Total entries in Max: %s"%(len(thisMaxData.keys())))
if DEBUG: print("Total entries in Min: %s"%(len(thisMinData.keys())))

###############################################################################
# Display the Data
###############################################################################
import matplotlib.pyplot as plt
import numpy as np

# Display Max/Min data, per seed, as a set of bar graphs

plt.rcParams.update({"toolbar": "None"}) # Disable the menu bar

################
# Define the Y-labels and ticks
plt_Ylabels = list(thisMaxData.keys())
plt_Ylabels.sort() # Put them in order because the Seed runs make sense in order...
plt_Yvalues = plt_Ylabels # Base ticks

if DEBUG: print(plt_Ylabels)
if DEBUG: print(plt_Yvalues)

################
# Define the Y-offsets for the 6 bars per seed
plt_Y1values = [Yval+0.40 for Yval in plt_Yvalues]
plt_Y2values = [Yval+0.24 for Yval in plt_Yvalues]
plt_Y3values = [Yval+0.08 for Yval in plt_Yvalues]
plt_Y4values = [Yval-0.08 for Yval in plt_Yvalues]
plt_Y5values = [Yval-0.24 for Yval in plt_Yvalues]
plt_Y6values = [Yval-0.40 for Yval in plt_Yvalues]

if DEBUG: print(plt_Y1values)
if DEBUG: print(plt_Y2values)
if DEBUG: print(plt_Y3values)
if DEBUG: print(plt_Y4values)
if DEBUG: print(plt_Y5values)
if DEBUG: print(plt_Y6values)

################
# Bars in order:
# maxWorstSlack, maxTotalNegativeSlack, maxTotalPaths, minWorstSlack, minTotalNegativeSlack, minTotalPaths
plt_X1values = [thisMaxData[thisKey][0] for thisKey in plt_Ylabels]
plt_X2values = [thisMaxData[thisKey][1] for thisKey in plt_Ylabels]
plt_X3values = [thisMaxData[thisKey][2] for thisKey in plt_Ylabels]
plt_X4values = [thisMinData[thisKey][0] for thisKey in plt_Ylabels]
plt_X5values = [thisMinData[thisKey][1] for thisKey in plt_Ylabels]
plt_X6values = [thisMinData[thisKey][2] for thisKey in plt_Ylabels]

if DEBUG: print(plt_X1values)
if DEBUG: print(plt_X2values)
if DEBUG: print(plt_X3values)
if DEBUG: print(plt_X4values)
if DEBUG: print(plt_X5values)
if DEBUG: print(plt_X6values)

################
# Create the array of bar plots
plt_barh1 = plt.barh(plt_Y1values, plt_X1values, 0.16, align="center", color="firebrick", label="Max WNS")
plt_barh2 = plt.barh(plt_Y2values, plt_X2values, 0.16, align="center", color="red"      , label="Max TNS")
plt_barh3 = plt.barh(plt_Y3values, plt_X3values, 0.16, align="center", color="darkred"  , label="Max Total Paths")
plt_barh4 = plt.barh(plt_Y4values, plt_X4values, 0.16, align="center", color="slateblue", label="Min WNS")
plt_barh5 = plt.barh(plt_Y5values, plt_X5values, 0.16, align="center", color="blue"     , label="Min TNS")
plt_barh6 = plt.barh(plt_Y6values, plt_X6values, 0.16, align="center", color="darkblue" , label="Min Total Paths")

################
# Create the legend object
plt_legend_object = plt.legend(handles=[plt_barh1,plt_barh2,plt_barh3,plt_barh4,plt_barh5,plt_barh6], loc="best")

################
# Configure the Graph
plt.xscale('symlog')
plt.yticks(plt_Yvalues, plt_Ylabels)
plt.xlabel('ns / count')
plt.grid(axis='x', linestyle=':')
plt.title("Seed Space Results")

################
# Show the final results...
plt.show()

