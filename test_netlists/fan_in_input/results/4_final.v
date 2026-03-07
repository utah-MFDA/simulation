module fan_in_input (out,
    soln1,
    soln2);
 output out;
 input soln1;
 input soln2;

 wire ch1;
 wire ch2;
 wire ch3;
 wire ch4;
 wire chm01;
 wire chm02;
 wire chm11;

 diffmix_25px_0 m1 (.a_fluid(ch1),
    .b_fluid(ch2),
    .out_fluid(chm01));
 diffmix_25px_0 m2 (.a_fluid(ch3),
    .b_fluid(ch4),
    .out_fluid(chm02));
 diffmix_25px_0 m3 (.a_fluid(chm01),
    .b_fluid(chm02),
    .out_fluid(chm11));
 serpentine_100px_0 serp1 (.in_fluid(soln1),
    .out_fluid(ch1));
 serpentine_100px_0 serp2 (.in_fluid(soln1),
    .out_fluid(ch2));
 serpentine_100px_0 serp3 (.in_fluid(soln2),
    .out_fluid(ch3));
 serpentine_100px_0 serp4 (.in_fluid(soln2),
    .out_fluid(ch4));
 serpentine_100px_0 serp5 (.in_fluid(chm11),
    .out_fluid(out));
endmodule
