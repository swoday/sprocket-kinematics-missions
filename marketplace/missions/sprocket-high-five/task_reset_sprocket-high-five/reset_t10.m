% Ready for Task 10: the state after Task 09 (Measure the paw with addFrameVariables).
run("reset_t09.m");

addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");
