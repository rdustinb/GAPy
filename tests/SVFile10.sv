// 1995 Verilog, Syntax 10

module SVFile10 #(
  parameter PARAM1= 8,
  parameter PARAM2= 7,
  parameter PARAM3= 6,
  parameter PARAM4= 5,
  parameter PARAM5= 4
)(
  input clk, reset,
  output [31:0] addr[1:0],
  output [$clog2(PARAM2)-1:0] valid,
  output [63:0]               data1, data2,
  output              wen, ren,
  input               ready);


endmodule

