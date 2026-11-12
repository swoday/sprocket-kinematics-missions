% Ready for Task 09: the state after Task 08 (Solve the forward problem with solve and viewSolution).
run("reset_t08.m");

[pawStance, status] = solve(ks, [0 40 -80]);
