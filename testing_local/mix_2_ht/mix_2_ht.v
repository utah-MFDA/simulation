module mix_2_ht (
  soln1,
  soln2,
  out
);

input soln1, soln2 ;
output out ;

wire conn1, conn2, conn3, conn4, conn5 ;

serpentine_150px_0_ht serp1 (.in_fluid(soln1), .out_fluid(conn1)) ;
serpentine_150px_0_ht serp2 (.in_fluid(conn1), .out_fluid(conn2)) ;

serpentine_150px_0_ht serp3 (.in_fluid(soln2), .out_fluid(conn3)) ;
serpentine_150px_0_ht serp4 (.in_fluid(conn3), .out_fluid(conn4)) ;

diffmix_25px_0_ht     mix0  (.a_fluid(conn2), .b_fluid(conn4), .out_fluid(conn5)) ;

serpentine_150px_0_ht serp5 (.in_fluid(conn5), .out_fluid(out)) ;

endmodule
