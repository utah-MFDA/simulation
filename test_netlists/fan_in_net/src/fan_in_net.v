module fan_in_net (
    soln1,
    soln2,
    soln3,
    soln4,
    out
);

input soln1 ;
input soln2 ;
input soln3 ;
input soln4 ;

output out ;

wire ch1 ;
wire ch2 ;

wire chm11 ;

serpentine_100px_0 serp1 (.in_fluid(soln1), .out_fluid(ch1)) ;
serpentine_100px_0 serp2 (.in_fluid(soln2), .out_fluid(ch1)) ;

serpentine_100px_0 serp3 (.in_fluid(soln3), .out_fluid(ch2)) ;
serpentine_100px_0 serp4 (.in_fluid(soln4), .out_fluid(ch2)) ;

diffmix_25px_0 m3 (.a_fluid(ch1), .b_fluid(ch2), .out_fluid(chm11)) ;

serpentine_100px_0 serp5 (.in_fluid(chm11), .out_fluid(out)) ;
    
endmodule