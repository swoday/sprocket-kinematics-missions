% Ready for Task 06: the state after Task 05 (Measure the paw with addFrameVariables).
run("reset_t05.m");

addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");
