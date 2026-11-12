% Ready for Task 14: the state after Task 13 (Solve the forward problem with solve).
run("reset_t13.m");

[pawStance, status] = solve(ks, [0 40 -80]);
