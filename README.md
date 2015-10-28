## Synopsis

GAPy (pronounced "Gee - Aee - Pie") is an assortment of Python scripts that FPGA developers can use to automate code development and work flow. These tools are Python3-based only and will not support the old Python2 constructs.

***getInstance.py*** - A script that will parse a user-specified HDL file's port list and parameter list, converting it to a block of code used for instantiation that is accessible from the user's OS Clipboard.

## Motivation

FPGA development has a lack of automation tools, to say the least. I intend to change that. This repository will contain a list of functions that will make an FPGA developers coding experience faster and more efficient.

## Installation

Clone this project to an accessible location on your local machine or server: 

` git clone https://github.com/rdustinb/fpga_code_ops.git `

The user should run:

`python3 getInstance.py --path`

to properly add the script to the user's .alias file for future use.

If any dependencies are missing each script will tell the designer how to install them.

### Dependecies ###

The tools in this repository depend on the following Python Libraries:

**getopt** - allows user input from the terminal to be pulled into the script in a concise manner.

**sys** - allows Terminal arguments to be enumerated inside the scripts.

**pyperclip** - allows the scripts to access your systems Clipboard for writing. Don't worry, these scripts aren't reading out of the Clipboard for any reasons.

## Code Example

`getInstance path/to/hdl/file.sv <tabSpace> <column align> <comment align>`

Where each option performs the following spacing:

```Verilog
module_name #(
                .BUSWIDTH                  (BUSWIDTH),
<--tabSpace-->  .RSTPOL <--column align--> (RSTPOL),
                ...
                .MAGIC                     (MAGIC)
) module_name_0 (
                .clk                       (clk),                          // in [1]
<--tabSpace-->  .ben    <--column align--> (ben),      <--comment align--> // in [15:0]
                ...
                .active                    (active),                       // inout [1]
                .dout                      (dout)                          // out [3:0]
);
```
I personally use the following command:

`getInstance path/to/hdl/file.sv 2 25 15`

Both the <column align> and <comment align> options begin counting columns at the port-name-dot `.` and the port-connect-opening-parentheses `(`. The three options are additive to an absolute column number. For instance, if the options `2 25 15` are specified, the comments of the ports will begin on column 42 when the instance is pasted into the containing document or code file.

The script location can be installed onto the users $PATH variable with:

`getInstance.py --path`

## Tests

Running any of the scripts with the --test option will cause the script to run using the example code in the tests/ folder.

## Contributors

If you have a feature request, [please add it!](https://github.com/rdustinb/fpga_code_ops/issues)
You can follow me on Twitter: [@RDustinB](https://twitter.com/RDustinB)

## License

I am using the simple [MIT license](http://choosealicense.com) for this repository as I do not intend for this code base to be closed in any way, but I'd like a simple license present.
