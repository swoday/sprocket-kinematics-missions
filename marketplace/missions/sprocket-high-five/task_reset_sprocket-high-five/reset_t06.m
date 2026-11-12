% Ready for Task 06: inverse kinematics posed and solved once without a guess.
run("reset_t05.m");

clearTargetVariables(ks);
clearOutputVariables(ks);
addTargetVariables(ks, pawIDs);
addOutputVariables(ks, legIDs);
qFirst = solve(ks, padPosition);
