% Ready for Task 07: the state after Task 06 (Check the measurement with frameVariables).
run("reset_t06.m");

F = frameVariables(ks);
pawIDs = "Paw.Translation." + ["x"; "y"; "z"];
