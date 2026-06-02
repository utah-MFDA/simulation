module fan_out_output (
    soln1,
    soln2,
    out1
);

input soln1 ;
input soln2 ;
output out1 ;

wire ch1 ;
wire ch2 ;

serpentine_100px_0 serp1 (.in_fluid(soln1), .out_fluid(ch1)) ;
serpentine_200px_0 serp2 (.in_fluid(soln2), .out_fluid(ch2)) ;

serpentine_200px_0 serp3 (.in_fluid(ch1), .out_fluid(out1)) ;
serpentine_200px_0 serp4 (.in_fluid(ch2), .out_fluid(out1)) ;
    
endmodule