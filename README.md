## Synopsis

An assortment of Python scripts that FPGA developers can use to automate code development and work flow.

***getInstance.py*** - A script that will parse a user-specified HDL file's port list and parameter list, converting it to a block of code used for instantiation that is accessible from the user's OS Clipboard.

## Motivation

FPGA development has a lack of automation tools, to say the least. I intend to change that. This repository will contain a list of functions that will make an FPGA developers coding experience faster and more efficient.

## Installation

Clone this project to an accessible location on your local machine or server: 

` git clone https://github.com/rdustinb/fpga_code_ops.git `

Running any of the scripts for the first time from their install directory will cause that folder to be added to your $PATH one time only. From there the tools will be accessible from anywhere.

If any dependencies are missing each script will tell the designer how to install them.

### Dependecies ###

The tools in this repository depend on the following Python Libraries:

**getopt** - allows user input from the terminal to be pulled into the script in a concise manner.

**sys** - allows Terminal arguments to be enumerated inside the scripts.

**pyperclip** - allows the scripts to access your systems Clipboard for writing. Don't worry, these scripts aren't reading out of the Clipboard for any reasons.

## Code Example

`getInstance.py --test`

This will test the script with example code. Really only used to verify the script works.

`getInstance.py path/to/hdl/file.[sv,v,vhd]`

This is how the scripts is used. The port list is now simply available to paste wherever the designer wishes (email, code file, document, etc).

## Tests

Running any of the scripts with the --test option will cause the script to run using the example code in the tests/ folder.

## Contributors

If you have a feature request, [please add it!](https://github.com/rdustinb/fpga_code_ops/issues)
You can follow me on Twitter: [@RDustinB](https://twitter.com/RDustinB)

## License

I am using the simple [MIT license](http://choosealicense.com) for this repository as I do not intend for this code base to be closed in any way, but I'd like a simple license present.
