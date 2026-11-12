% Ready for Task 07: leg joints assigned as initial guesses, high-five pose solved.
run("reset_t06.m");

addInitialGuessVariables(ks, legIDs);
qHighFive = solve(ks, padPosition, [0 40 -80]);
