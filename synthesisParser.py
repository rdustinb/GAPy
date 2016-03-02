import operator
import sys
import re

singleBit = re.compile('bit \d+ of')
bitList = re.compile('bits \d+ to \d+ of')
portOfMod = re.compile('of \w+ is unused')

"""
  This Python Script will simply count all warnings and errors in the synthesis
  Report file and also count according to filename.
"""

def initialize():
  """
    Initialize the parsing, simply captures the filename now
  """
  print("Please enter synthesis report to parse:")
  filename = input()
  return filename

###############################################################################
# Count the total number of warning
###############################################################################
def warn_count_total(filename):
  """
    Open the file and count all warnings.
  """
  warning_counter = 0
  # For Python 3.x
  with open(filename) as text:
    for line in text:
      if(line.find("@W") != -1):
        warning_counter += 1
  return warning_counter

###############################################################################
# Count the warnings by file
###############################################################################
def warn_count_by_file(filename):
  """
    Open the file and increment warning counter in individual filename bins.
  """
  # Create an empty dictionary
  warning_counter = {}
  line_split = []
  # For Python 3.x
  with open(filename) as text:
    for line in text:
      if((line.find("@W") != -1) and (line.count(":") >= 6)):
        (blah1,warn_num,warn_path,warn_line,*blah2,warn_desc) = line.split(sep=":")
        (*blah1,warn_file) = warn_path.split(sep="/")
        warn_file = warn_file.strip("\"")
        # Increment warning counter for filename
        warning_counter[warn_file] = warning_counter.get(warn_file, 0) + 1
  return warning_counter

###############################################################################
# List of warnings by file
###############################################################################
def warn_list_by_file(filename):
  """
    Open the file and list warnings into individual filename bins.
  """
  # Create an empty dictionary
  warning_list = {}
  line_split = []
  # For Python 3.x
  with open(filename) as text:
    for line in text:
      if((line.find("@W") != -1) and (line.count(":") >= 6)):
        (blah1,warn_num,warn_path,warn_line,*blah2,warn_desc) = line.split(sep=":")
        (*blah1,warn_file) = warn_path.split(sep="/")
        warn_file = warn_file.strip("\"")
        line = line.strip()
        # Append the warning for the filename into the dictionary
        # The dictionary entry is a list of warnings
        if(warn_file in warning_list):
          warning_list[warn_file].append(line)
        else:
          warning_list[warn_file] = []
          warning_list[warn_file].append(line)
  return warning_list

###############################################################################
# Special Warnings
###############################################################################
def overflow_warn_by_file(filename):
  """
    Lists overflow warnings for individual files.
  """
  # Create an empty dictionary
  warning_list = {}
  line_split = []
  # For Python 3.x
  with open(filename) as text:
    for line in text:
      if((line.find("@W") != -1) and (line.count(":") >= 6) and (line.find("overflow") != -1)):
        (blah1,warn_num,warn_path,warn_line,*blah2,warn_desc) = line.split(sep=":")
        warn_line = warn_line.strip()
        (*blah1,warn_file) = warn_path.split(sep="/")
        warn_file = warn_file.strip("\"")
        # Append the warning for the filename into the dictionary
        # The dictionary entry is a list of lines for this warning in this file
        if(warn_file in warning_list):
          if(not(warn_line in warning_list[warn_file])):
            warning_list[warn_file].append(warn_line)
        else:
          warning_list[warn_file] = []
          warning_list[warn_file].append(warn_line)
  return warning_list

def inout_warn_by_file(filename):
  """
    Lists input ports driven by a value warnings for individual files.
  """
  # Create an empty dictionary
  warning_list = {}
  # For Python 3.x
  with open(filename) as text:
    for line in text:
      # Input Ports
      if("Input" in line):
        if((line.find("@W") != -1) and (line.count(":") >= 6) and (line.find("is the target of an assignment") != -1)):
          # Create the new embedded dictionary for input ports
          if("inputs" not in warning_list):
            warning_list["inputs"] = {}
          # Parse the warning
          (blah1,warn_num,warn_path,*blah2,warn_port) = line.split(sep=":")
          # Grab only the filename, not the whole path
          (*blah1,warn_file) = warn_path.split(sep="/")
          warn_file = warn_file.strip("\"")
          # Make the key all lowercase as this is how the user input is parsed
          warn_file = warn_file.lower()
          # Grab the port name in the file that has issues
          (warn_port,*blah) = warn_port.split(sep=")")
          (*blah,warn_port) = warn_port.split(sep="(port ")
          warn_port = warn_port+" - assignment"
          # Append the warning for the filename into the dictionary
          # The dictionary entry is a list of lines for this warning in this file
          if(warn_file in warning_list["inputs"]):
            # Only append the port to the list if it isn't already in the list
            # Synplify Pro likes to repeat warnings
            if(not(warn_port in warning_list["inputs"][warn_file])):
              warning_list["inputs"][warn_file].append(warn_port)
          else:
            warning_list["inputs"][warn_file] = []
            warning_list["inputs"][warn_file].append(warn_port)
        elif((line.find("@W") != -1) and (line.find("is unused") != -1)):
          # Create the new embedded dictionary for input ports
          if("inputs" not in warning_list):
            warning_list["inputs"] = {}
          # Parse the warning
          (blah1,warn_port) = line.split(sep="|")
          (*blah0,warn_path,blah4,blah3,blah2,blah1) = blah1.split(sep=":")
          # Grab only the filename, not the whole path
          (*blah1,warn_file) = warn_path.split(sep="/")
          warn_file = warn_file.strip("\"")
          # Make the key all lowercase as this is how the user input is parsed
          warn_file = warn_file.lower()
          # Grab the port name in the file that has issues
          warn_port = warn_port.replace("Input","")
          warn_port = warn_port.replace("port","")
          # Need an RE to handle the bits if this is in the statement
          warn_port = re.sub(singleBit, "", warn_port)
          warn_port = re.sub(bitList, "", warn_port)
          warn_port = re.sub(portOfMod, "", warn_port)
          warn_port = warn_port.replace("is unused","")
          warn_port = warn_port.strip()
          # Since this is a new type of input issue, give it a slight description
          warn_port = warn_port+" - unused"
          # Append the warning for the filename into the dictionary
          # The dictionary entry is a list of lines for this warning in this file
          if(warn_file in warning_list["inputs"]):
            # Only append the port to the list if it isn't already in the list
            # Synplify Pro likes to repeat warnings
            if(not(warn_port in warning_list["inputs"][warn_file])):
              warning_list["inputs"][warn_file].append(warn_port)
          else:
            warning_list["inputs"][warn_file] = []
            warning_list["inputs"][warn_file].append(warn_port)
      # Inout Ports
      if("Inout" in line):
        if((line.find("@W") != -1) and (line.find("is unused") != -1)):
          # Create the new embedded dictionary for input ports
          if("inouts" not in warning_list):
            warning_list["inouts"] = {}
          # Parse the warning
          blah1,warn_port = line.split(sep="|")
          (*blah0,warn_path,blah4,blah3,blah2,blah1) = blah1.split(sep=":")
          # Grab only the filename, not the whole path
          (*blah1,warn_file) = warn_path.split(sep="/")
          warn_file = warn_file.strip("\"")
          # Make the key all lowercase as this is how the user input is parsed
          warn_file = warn_file.lower()
          # Grab the port name in the file that has issues
          warn_port = warn_port.replace("Inout","")
          warn_port = warn_port.replace("port","")
          # Need an RE to handle the bits if this is in the statement
          warn_port = re.sub(singleBit, "", warn_port)
          warn_port = re.sub(bitList, "", warn_port)
          warn_port = re.sub(portOfMod, "", warn_port)
          warn_port = warn_port.replace("is unused","")
          warn_port = warn_port.strip()
          # Since this is a new type of inout issue, give it a slight description
          warn_port = warn_port+" - unused"
          # Append the warning for the filename into the dictionary
          # The dictionary entry is a list of lines for this warning in this file
          if(warn_file in warning_list["inouts"]):
            # Only append the port to the list if it isn't already in the list
            # Synplify Pro likes to repeat warnings
            if(not(warn_port in warning_list["inouts"][warn_file])):
              warning_list["inouts"][warn_file].append(warn_port)
          else:
            warning_list["inouts"][warn_file] = []
            warning_list["inouts"][warn_file].append(warn_port)

  return warning_list

def regs_opt_by_file(filename):
  """
    This function will list a total number of registers optimized
    out of the module due to being unconnected or unused. Simply
    adds all optimized register info or warnings per file or
    module.
    Listing optimizations by file or all optimizations by file
    will be supported.
  """
  pass

def busses_opt_by_file(filename):
  """
    This function will provide a more in-depth view into the typical
    register optimization that occurs. It will list the names of all
    busses or signals that have registers optimized per file or
    module and will list how many registers for each bus or signal
    have been optimized away.
    Listing optimizations by file or all optimizations by file
    will be supported.
  """
  pass

###############################################################################
###############################################################################
if __name__ == '__main__':
  if(int(sys.version[0]) == 3):
    # Initialize
    filename = initialize()
    # Get Overflow Warnings by file
    warn_ovflw_by_file = overflow_warn_by_file(filename)
    # Get warnings by file
    warn_by_filecnt = warn_count_by_file(filename)
    # Convert the dictionary to list of tuples ordered by value
    sorted_warn_by_file = sorted(warn_by_filecnt.items(), key=operator.itemgetter(1))
    # Get the list of warnings for each filename, does not need to be sorted
    warn_by_filelist = warn_list_by_file(filename)
    # Get list of port errors by filename
    warn_inout_by_file = inout_warn_by_file(filename)
    # Get the total count of warnings
    warn_total = warn_count_total(filename)

    # Request user input on what to display
    request = "start"
    while(request != "quit"):
      print("What data do you want to display?")
      print("\tCount of total warnings                [warn_total]")
      print("\tCount of warnings by file              [warn_count]")
      print("\tList of warnings by file               [warn_list]")
      print("\tList of counter overflows by file      [warn_ovflw]")
      print("\tList of warnings pertaining to IO      [warn_inout]")
      print("\tQuit script....                        [quit]")

      # For Python 3.x
      request = input().lower()

      # Branch based on request
      if(request == "warn_total"):
        print("Total warnings in the synthesis report: \n\t%s\n"%(warn_total))
      elif(request == "warn_count"):
        print("Please enter a filename to display number of warnings, or")
        print("enter 'all' to view all warning counts. The available ")
        print("filenames are:")

        # Get the maximum filename field
        max_len_filename = int()
        for key in warn_by_filelist.keys():
          if(len(key) > max_len_filename):
            max_len_filename = len(key)

        # Add some extra space between columns
        max_len_filename += 2

        # Create columns of filenames
        mult_names = str()
        column = int(0)
        for name in warn_by_filelist.keys():
          # If all filenames are small, can fit more than two columns
          # per line
          if(column == int(80/max_len_filename)):
            # Print the made line
            print(mult_names)
            # Clear the line variable
            mult_names = ""
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column = 1
          else:
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column += 1
        print("%s\n"%(mult_names))

        # For Python 3.x
        request = input().lower()

        if(request == "all"):
          # Iterate over the entire list
          for (warn_file, warn_val) in sorted_warn_by_file:
            print("Total warnings for file %s:\n\t%s\n"%(warn_file,warn_val))
        else:
          print("Total warnings for file %s:\n\t%s\n"%(request,warn_by_filecnt.get(request, 0)))
      elif(request == "warn_list"):
        print("Please enter a filename to display the list of warnings for")
        print("that file, or enter 'all' to view the list of all warnings")
        print("for all files. The available filenames with warnings are:")

        # Get the maximum filename field
        max_len_filename = int()
        for key in warn_by_filelist.keys():
          if(len(key) > max_len_filename):
            max_len_filename = len(key)

        # Add some extra space between columns
        max_len_filename += 2

        # Create columns of filenames
        mult_names = str()
        column = int(0)
        for name in warn_by_filelist.keys():
          # If all filenames are small, can fit more than two columns
          # per line
          if(column == int(80/max_len_filename)):
            # Print the made line
            print(mult_names)
            # Clear the line variable
            mult_names = ""
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column = 1
          else:
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column += 1
        print("%s\n"%(mult_names))

        # For Python 3.x
        request = input().lower()

        if(request == "all"):
          # Iterate over the entire list
          for (warn_file, warn_list) in warn_by_filelist.items():
            print("List of warnings for file %s:"%(warn_file))
            for warn_val in warn_by_filelist[warn_file]:
              print("\t%s"%(warn_val))
          print("\n")
        else:
          print("List of warnings for file %s:"%(request))
          for warn_val in warn_by_filelist[request]:
            print("\t%s"%(warn_val))
          print("\n")
      elif(request == "warn_ovflw"):
        print("Please enter a filename to display the list of lines where")
        print("counter overflow warnings occur for that file, or enter 'all'")
        print("to view the list of all lines in all files that have an")
        print("overflow warning. The available filenames with warnings are:")

        # Get the maximum filename field
        max_len_filename = int()
        for key in warn_ovflw_by_file.keys():
          if(len(key) > max_len_filename):
            max_len_filename = len(key)

        # Add some extra space between columns
        max_len_filename += 2

        # Create columns of filenames
        mult_names = str()
        column = int(0)
        for name in warn_ovflw_by_file.keys():
          # If all filenames are small, can fit more than two columns
          # per line
          if(column == int(80/max_len_filename)):
            # Print the made line
            print(mult_names)
            # Clear the line variable
            mult_names = ""
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column = 1
          else:
            # Append spaces for common filename field size
            mult_names += " "*(max_len_filename - len(name))
            # Append the latest name
            mult_names += name
            # Reset column counter
            column += 1
        print("%s\n"%(mult_names))

        # For Python 3.x
        request = input().lower()

        if(request == "all"):
          # Iterate over the entire list
          for (warn_file, warn_list) in warn_ovflw_by_file.items():
            print("List of lines where counter overflow warnings occur for file %s:"%(warn_file))
            for warn_val in warn_ovflw_by_file[warn_file]:
              print("\t%s"%(warn_val))
          print("\n")
        else:
          print("List of lines where counter overflow warnings occur for file %s:"%(request))
          for warn_val in warn_ovflw_by_file[request]:
            print("\t%s"%(warn_val))
          print("\n")
      elif(request == "warn_inout"):
        print("Please specify which port type you wish to review")
        print("whether that be inputs, outputs or inouts:")
        # For Python 3.x
        port_type = input().lower()

        # Check that the port direction has issues
        if(port_type in warn_inout_by_file):
          print("Please enter a filename to display the list of ports")
          print("which are misassigned in that file, or enter 'all' to")
          print("view the list of all ports in all files that have a")
          print("misassigned port warning. The available filenames are:")

          # Get the maximum filename field
          max_len_filename = int()
          for key in warn_inout_by_file[port_type].keys():
            if(len(key) > max_len_filename):
              max_len_filename = len(key)

          # Add some extra space between columns
          max_len_filename += 2

          # Create columns of filenames
          mult_names = str()
          column = int(0)
          for name in warn_inout_by_file[port_type].keys():
            # If all filenames are small, can fit more than two columns
            # per line
            if(column == int(80/max_len_filename)):
              # Print the made line
              print(mult_names)
              # Clear the line variable
              mult_names = ""
              # Append spaces for common filename field size
              mult_names += " "*(max_len_filename - len(name))
              # Append the latest name
              mult_names += name
              # Reset column counter
              column = 1
            else:
              # Append spaces for common filename field size
              mult_names += " "*(max_len_filename - len(name))
              # Append the latest name
              mult_names += name
              # Reset column counter
              column += 1
          print("%s\n"%(mult_names))

          # For Python 3.x
          request = input().lower()

          if(request == "all"):
            # Inputs
            # Iterate over the entire list
            print("\n")
            for (warn_file, warn_list) in warn_inout_by_file[port_type].items():
              print("List of ports that have specific warnings, for file %s [%s]:"%(warn_file,port_type))
              for warn_val in warn_inout_by_file[port_type][warn_file]:
                print("\t%s"%(warn_val))
            print("\n")
          else:
            print("\n")
            print("List of ports that have specific warnings, for file %s [%s]:"%(request,port_type))
            for warn_val in warn_inout_by_file[port_type][request]:
              print("\t%s"%(warn_val))
            print("\n")
        else:
          print("\n")
          print("There are no reported warnings for that port direction.")
          print("\n")
      elif(request == "quit"):
        print("Exiting...")
      else:
        print("Unknown entry received, please try again.")
  else:
    print("This tool only supports version 3.x.")
    print("Exiting...")
