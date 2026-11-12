% Ready for Task 10: the state after Task 09 (Swap the roles with clearTargetVariables and clearOutputVariables).
run("reset_t09.m");

clearTargetVariables(ks);
clearOutputVariables(ks);
addTargetVariables(ks, pawIDs);
addOutputVariables(ks, legIDs);
