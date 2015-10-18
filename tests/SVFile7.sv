// 1995 Verilog, Syntax 7

module SVFile7
(
  input clk, reset,
  output [31:0] addr,
  output [$clog2(PARAM)-1:0] valid,
  output [63:0]               data,
  output              wen, ren,
  input               ready
  );


  parameter PARAM1= 8;
  parameter PARAM2= 7;
  parameter PARAM3= 6;
  parameter PARAM4= 5;
  parameter PARAM5= 4;

endmodule

