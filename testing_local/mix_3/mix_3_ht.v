module mix_2_ht (
  soln1,
  soln2,
  out
);

input soln1, soln2 ;
output out;

wire conn1, conn2, conn3 ;

serpentine_200px_0_ht serp1 (.in_fluid(soln1), .out_fluid(conn1));
serpentine_200px_0_ht serp2 (.in_fluid(soln2), .out_fluid(conn2));

diffmix_25px_0_ht (.a_fluid(conn1), .b_fluid(conn2), .out_fluid(conn3)) ;

serpentine_200px_0_ht serp3 (.in_fluid(conn3), .out_fluid(out)) ;

endmodule
