module grad_gen_3 (
	input soln1,
	input soln2,
	output out
);

wire connect1;
wire connect2;
wire connect3;
wire connect4;
wire connect5;
wire connect6;
// wire connect7;
// wire connect8;
// wire connect9;
// wire connect10;
// wire connect11;
// wire connect12;
// wire connect13;

// Layer 1
serpentine_200px_0 serp1 (.in_fluid(soln1), .out_fluid(connect1));
diffmix_25px_0 mix1 (.a_fluid(soln1), .b_fluid(soln2), .out_fluid(connect2));
serpentine_200px_0 serp2 (.in_fluid(connect2), .out_fluid(connect3));
serpentine_200px_0 serp3 (.in_fluid(soln2), .out_fluid(connect4));
// Layer 2
serpentine_200px_0 serp4 (.in_fluid(connect1), .out_fluid(out));
diffmix_25px_0 mix2 (.a_fluid(connect1), .b_fluid(connect3), .out_fluid(connect5));
serpentine_200px_0 serp5 (.in_fluid(connect5), .out_fluid(out));
diffmix_25px_0 mix3 (.a_fluid(connect3), .b_fluid(connect4), .out_fluid(connect6));
serpentine_200px_0 serp6 (.in_fluid(connect6), .out_fluid(out));
serpentine_200px_0 serp7 (.in_fluid(connect4), .out_fluid(out));
// Layer 3
// serpentine_200px_0 serp8 (.in_fluid(connect5), .out_fluid(out));
// diffmix_25px_0 mix4 (.a_fluid(connect5), .b_fluid(connect7), .out_fluid(connect11));
// serpentine_200px_0 serp9 (.in_fluid(connect11), .out_fluid(out));
// diffmix_25px_0 mix5 (.a_fluid(connect7), .b_fluid(connect9), .out_fluid(connect12));
// serpentine_200px_0 serp10 (.in_fluid(connect12), .out_fluid(out));
// diffmix_25px_0 mix6 (.a_fluid(connect9), .b_fluid(connect10), .out_fluid(connect13));
// serpentine_200px_0 serp11 (.in_fluid(connect13), .out_fluid(out));
// serpentine_200px_0 serp12 (.in_fluid(connect10), .out_fluid(out));
//
endmodule
