% Ready for Task 15: the state after Task 14 (Solve the forward problem with solve).
run("reset_t14.m");

[pawStance, status] = solve(ks, [0 40 -80]);
