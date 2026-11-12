% Ready for Task 12: the state after Task 11 (Pick the reachable pose with addInitialGuessVariables).
run("reset_t11.m");

addInitialGuessVariables(ks, legIDs);
[qHighFive, status] = solve(ks, padPosition, [0 40 -80]);
