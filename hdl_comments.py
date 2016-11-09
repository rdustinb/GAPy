import sys, getopt, os
from termcolor import colored, cprint

def main(argv):
  """
    Main Script Execution Point
  """
  directory = ''
  singlefile = ''
  ignorestart = 'NaN'
  try:
    opts,args = getopt.getopt(argv, "hf:d:i:")
  except getopt.GetoptError:
    print('python hdl_comments.py -f <filename>')
    print('or')
    print('python hdl_comments.py -d <directory name>')
    sys.exit(2)
# Parse through the options
  for opt,arg in opts:
    if opt == '-h':
      print('python hdl_comments.py -f <filename>')
      print('or')
      print('python hdl_comments.py -d <directory name>')
      sys.exit()
    elif opt in ('-f'):
      singlefile = arg
    elif opt in ('-d'):
      directory = arg
    elif opt in ('-i'):
      ignorestart = arg
# If Directory has been specified, only parse the directory
  if(directory != ''):
    for path, subdirs, files in os.walk(directory):
      if ".svn" in path:
        next
      else:
        for filename in files:
          f = os.path.join(path, filename)
          parse_single_file(f,ignorestart)
# If Only the file has been specified, parse the file
  elif(singlefile != ''):
    parse_single_file(singlefile,ignorestart)

def parse_single_file(file_name_path,ignore_start):
  if(file_name_path[-3:] == "vhd"):
    (total,single) = count_vhdl_file_comments(file_name_path,ignore_start)
    percentage = (single/total)*100
    if(percentage < 15):
      percentage = colored("%.1f"%(percentage), 'red')
    elif(percentage < 20):
      percentage = colored("%.1f"%(percentage), 'yellow')
    else:
      percentage = colored("%.1f"%(percentage), 'green')
    print("%s"%(file_name_path))
    print("\tTotal Lines Parsed:\t\t%s"%(total))
    print("\tSingle Line Comments:\t\t%s"%(single))
    print("\tComment-Total Percentage:\t%s"%(percentage))
  elif(file_name_path[-1:] == 'v' or file_name_path[-2:] == 'sv' or file_name_path[-2:] == 'vh'):
    (total,block,single) = count_verilog_file_comments(file_name_path,ignore_start)
    percentage = ((single+block)/total)*100
    if(percentage < 15):
      percentage = colored("%.1f"%(percentage), 'red')
    elif(percentage < 20):
      percentage = colored("%.1f"%(percentage), 'yellow')
    else:
      percentage = colored("%.1f"%(percentage), 'green')
    print("%s"%(file_name_path))
    print("\tTotal Lines Parsed:\t\t%s"%(total))
    print("\tBlock Comment Lines:\t\t%s"%(block))
    print("\tSingle Comment Lines:\t\t%s"%(single))
    print("\tComment-Total Percentage:\t%s"%(percentage))

def count_verilog_file_comments(file_name_path,ignore_start):
  """
    This functions scans a single SystemVerilog/Verilog file, or other file that
    is compatible with that language.
  """
  total_file_lines = 1
  block_comment_line_count = 0
  single_comment_line_count = 0
  ignoring = 1
  if(ignore_start == "NaN"):
    ignoring = 0
  with open(file_name_path, 'r') as fp:
    counting_block_comment = 0
    for line in fp:
      if(ignoring == 1):
        if(ignore_start in line):
          ignoring = 0
      else:
        total_file_lines += 1
        if(counting_block_comment == 1):
          block_comment_line_count += 1
          if "*/" in line and "/*" in line:
# Weird case where a block comment may end, and another begin on the same line.
            counting_block_comment = 1
          if "*/" in line:
            counting_block_comment = 0
        elif "/*" in line and "*/" in line:
# Weird case where a block comment may be started and ended in the same line
          counting_block_comment = 0
          block_comment_line_count += 1
        elif "/*" in line:
          counting_block_comment = 1
          block_comment_line_count += 1
        elif "//" in line:
          single_comment_line_count += 1
  # Return the Tuple: (total, block, single) for external processing/display
  return (total_file_lines,block_comment_line_count,single_comment_line_count)

def count_vhdl_file_comments(file_name_path,ignore_start):
  """
    This function scans a single VHDL file for instances of a VHDL comment. Since
    VHDL doesn't have block comments available, only the single line comment can
    be scanned for.
  """
  total_file_lines = 1
  single_comment_line_count = 0
  ignoring = 1
  if(ignore_start == "NaN"):
    ignoring = 0
  with open(file_name_path, 'r') as fp:
    for line in fp:
      if(ignoring == 1):
        if(ignore_start in line):
          ignoring = 0
      else:
        total_file_lines += 1
        if "--" in line:
          single_comment_line_count += 1
  # Return the Tuple: (total, single) for external processing/display
  return (total_file_lines,single_comment_line_count)

if __name__ == "__main__":
  main(sys.argv[1:])
