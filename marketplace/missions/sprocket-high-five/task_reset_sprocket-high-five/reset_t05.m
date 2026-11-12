% Ready for Task 05: forward kinematics posed and solved for the ready stance.
run("reset_t04.m");

addTargetVariables(ks, legIDs);
addOutputVariables(ks, pawIDs);
pawStance = solve(ks, [0 40 -80]);
