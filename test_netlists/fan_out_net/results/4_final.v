module fan_out_net (out1,
    out2,
    soln1);
 output out1;
 output out2;
 input soln1;

 wire ch1;

 serpentine_100px_0 serp1 (.in_fluid(soln1),
    .out_fluid(ch1));
 serpentine_200px_0 serp2 (.in_fluid(ch1),
    .out_fluid(out1));
 serpentine_200px_0 serp3 (.in_fluid(ch1),
    .out_fluid(out2));
endmodule
