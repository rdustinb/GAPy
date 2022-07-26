import sys
import glob

# Change this to have the script breakout the violating paths at a lower depth of hierarchy.
# 1 = top/foo
# 2 = top/foo/foo
# 3 = top/foo/foo/foo
#
# If the path is not as deep as this specified function depth value, the path will use the
# lowest hierarchy element name.
majorFunctionDepth = 4

target = "flt"
minmax = "max"
design_name = "my_design"

DEBUG = False

folderToSearch = "pnr/%s/%s_build/designer/%s/"%(target,target,design_name)
listOfFiles = glob.glob(folderToSearch+"*timing_violations_%s*"%(minmax))

if len(listOfFiles) == 0:
  print("\n\nError > there are no timing violations files in '%s'\n"%(folderToSearch))
  sys.exit(-1)

thisData = dict()
thisData["startpoint"] = dict()
thisData["endpoint"] = dict()

###############################################################################
# Amalgamate the Data
###############################################################################
# List of Files
for thisFile in listOfFiles:
  # Individual File
  with open(thisFile, 'r') as fh:
    for thisLine in fh:
      thisLine.strip()
      #print(thisLine)
      # Get Major Function Startpoint
      if thisLine.find("From:") != -1:
        thisStartHierRoot = thisLine.split(":")[1].split("/")[0].strip()
        if len(thisLine.split(":")[1].split("/")) < majorFunctionDepth:
          thisStart = thisLine.split(":")[1].split("/")[len(thisLine.split(":")[1].split("/"))-1].strip()
        else:
          thisStart = thisLine.split(":")[1].split("/")[majorFunctionDepth-1].strip()
        # Remove the bus bit-index, combine these into one entry
        if thisStart.find("[") != -1:
          thisStart = thisStart[0:thisStart.index("[")]
      # Get Major Function Endpoint
      if thisLine.find("To:") != -1:
        thisEndHierRoot = thisLine.split(":")[1].split("/")[0].strip()
        if len(thisLine.split(":")[1].split("/")) < majorFunctionDepth:
          thisEnd = thisLine.split(":")[1].split("/")[len(thisLine.split(":")[1].split("/"))-1].strip()
        else:
          thisEnd = thisLine.split(":")[1].split("/")[majorFunctionDepth-1].strip()
        # Remove the bus bit-index, combine these into one entry
        if thisEnd.find("[") != -1:
          thisEnd = thisEnd[0:thisEnd.index("[")]
      # Find the negative slack values only
      if thisLine.find("Slack (ns):") != -1 and thisLine.find("-") != -1:
        # Updated Max Slack
        thisSlack = float(thisLine.split(":")[1].strip())
        ######### For the Startpoints
        # Create the Major Function if it doesn't yet exist...
        if thisStart not in thisData["startpoint"]:
          thisData["startpoint"][thisStart] = dict()
          thisData["startpoint"][thisStart]["%sSlack"%(minmax)] = 1000000
          thisData["startpoint"][thisStart]["totalSlack"] = 0
          thisData["startpoint"][thisStart]["totalPaths"] = 0
          thisData["startpoint"][thisStart]["hierRoot"] = thisStartHierRoot
        # Update the max slack if this slack is greater...
        if thisData["startpoint"][thisStart]["%sSlack"%(minmax)] > thisSlack:
          thisData["startpoint"][thisStart]["%sSlack"%(minmax)] = thisSlack
        # Accumulate Total Slack
        thisData["startpoint"][thisStart]["totalSlack"] = round(thisData["startpoint"][thisStart]["totalSlack"] + thisSlack, 3)
        # Accumulate Total Paths
        thisData["startpoint"][thisStart]["totalPaths"] += 1
        ######### For the Endpoints
        # Create the Major Function if it doesn't yet exist...
        if thisEnd not in thisData["endpoint"]:
          thisData["endpoint"][thisEnd] = dict()
          thisData["endpoint"][thisEnd]["%sSlack"%(minmax)] = 1000000
          thisData["endpoint"][thisEnd]["totalSlack"] = 0
          thisData["endpoint"][thisEnd]["totalPaths"] = 0
          thisData["endpoint"][thisEnd]["hierRoot"] = thisEndHierRoot
        # Update the max slack if this slack is greater...
        if thisData["endpoint"][thisEnd]["%sSlack"%(minmax)] > thisSlack:
          thisData["endpoint"][thisEnd]["%sSlack"%(minmax)] = thisSlack
        # Accumulate Total Slack
        thisData["endpoint"][thisEnd]["totalSlack"] = round(thisData["endpoint"][thisEnd]["totalSlack"] + thisSlack, 3)
        # Accumulate Total Paths
        thisData["endpoint"][thisEnd]["totalPaths"] += 1

if DEBUG: print(thisData)

###############################################################################
# Display the Data
###############################################################################
import matplotlib.pyplot as plt
import numpy as np

plotRows = 1
plotCols = 2
plt1_position = 1
plt2_position = 2
plt1_key = "startpoint"
plt2_key = "endpoint"

plt.rcParams.update({"toolbar": "None"}) # Disable the menu bar

plt.figure(figsize=(12, 6)) # WxH in inches

plt.subplots_adjust(left=0.15, right=0.85, top=0.97, bottom=0.05, wspace=0.02, hspace=0)#, wspace=plt_width_padding)

################
# Plot 1
plt1_Ylabels = ["[%s]\n%s"%(thisData[plt1_key][thisName]["hierRoot"],thisName) for thisName in thisData[plt1_key]] # Keys in the dictionary
plt1_Yvalues = np.arange(len(plt1_Ylabels)) # Base ticks

if DEBUG: print(plt1_Ylabels)
if DEBUG: print(plt1_Yvalues)

plt1_Y1values = [Yval+0.18 for Yval in plt1_Yvalues] # Offset of Data 1
plt1_Y2values = [Yval-0.18 for Yval in plt1_Yvalues] # Offset of Data 2
plt1_Y3values = [Yval      for Yval in plt1_Yvalues] # Offset of Data 3
plt1_X1values = [thisData[plt1_key][thisName]["totalSlack"] for thisName in thisData[plt1_key]]
plt1_X2values = [thisData[plt1_key][thisName]["%sSlack"%(minmax)] for thisName in thisData[plt1_key]]
plt1_X3values = [thisData[plt1_key][thisName]["totalPaths"] for thisName in thisData[plt1_key]]

if DEBUG: print(plt1_Y1values)
if DEBUG: print(plt1_Y2values)
if DEBUG: print(plt1_Y3values)
if DEBUG: print(plt1_X1values)
if DEBUG: print(plt1_X2values)
if DEBUG: print(plt1_X3values)

# Define the subplot, comment this out if this doesn't work...
plt.subplot(plotRows, plotCols, plt1_position)

plt1_barh_displayTotalSlack = plt.barh(plt1_Y1values, plt1_X1values, 0.36, align="center", color='purple'   , label="Total Slack")
plt1_barh_displayWNS        = plt.barh(plt1_Y2values, plt1_X2values, 0.36, align="center", color='yellow'   , label="WNS")
plt1_barh_displayTotalPaths = plt.barh(plt1_Y3values, plt1_X3values, 0.36, align="center", color='darkgreen', label="Total Paths")
plt1_legend_object          = plt.legend(handles=[plt1_barh_displayTotalSlack,plt1_barh_displayWNS,plt1_barh_displayTotalPaths], loc="best")

plt.xscale('symlog')
plt.yticks(plt1_Yvalues, plt1_Ylabels)
plt.xlabel('ns / count')
plt.grid(axis='x', linestyle=':')
plt.title(plt1_key+" - "+target)

################
# Plot 2
plt2_Ylabels = ["[%s]\n%s"%(thisData[plt2_key][thisName]["hierRoot"],thisName) for thisName in thisData[plt2_key]] # Keys in the dictionary
plt2_Yvalues = np.arange(len(plt2_Ylabels)) # Base ticks

if DEBUG: print(plt2_Ylabels)
if DEBUG: print(plt2_Yvalues)

plt2_Y1values = [Yval+0.18 for Yval in plt2_Yvalues] # Offset of Data 1
plt2_Y2values = [Yval-0.18 for Yval in plt2_Yvalues] # Offset of Data 2
plt2_Y3values = [Yval      for Yval in plt2_Yvalues] # Offset of Data 3
plt2_X1values = [thisData[plt2_key][thisName]["totalSlack"] for thisName in thisData[plt2_key]]
plt2_X2values = [thisData[plt2_key][thisName]["%sSlack"%(minmax)] for thisName in thisData[plt2_key]]
plt2_X3values = [thisData[plt2_key][thisName]["totalPaths"] for thisName in thisData[plt2_key]]

if DEBUG: print(plt2_Y1values)
if DEBUG: print(plt2_Y2values)
if DEBUG: print(plt2_Y3values)
if DEBUG: print(plt2_X1values)
if DEBUG: print(plt2_X2values)
if DEBUG: print(plt2_X3values)

# Define the subplot, comment this out if this doesn't work...
plt.subplot(plotRows, plotCols, plt2_position)

plt2_barh_displayTotalSlack = plt.barh(plt2_Y1values, plt2_X1values, 0.36, align="center", color='purple'   , label="Total Slack")
plt2_barh_displayWNS        = plt.barh(plt2_Y2values, plt2_X2values, 0.36, align="center", color='yellow'   , label="WNS")
plt2_barh_displayTotalPaths = plt.barh(plt2_Y3values, plt2_X3values, 0.36, align="center", color='darkgreen', label="Total Paths")
plt2_legend_object          = plt.legend(handles=[plt2_barh_displayTotalSlack,plt2_barh_displayWNS,plt2_barh_displayTotalPaths], loc="best")

plt.xscale('symlog')
plt.tick_params(axis="y", right=True, left=False, labelright=True, labelleft=False)
plt.yticks(plt2_Yvalues, plt2_Ylabels)
plt.xlabel('ns / count')
plt.grid(axis='x', linestyle=':')
plt.title(plt2_key+" - "+target)

################
# Show the final results...
plt.show()
