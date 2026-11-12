% Ready for Task 09: the state after Task 08 (Measure the paw with addFrameVariables).
run("reset_t08.m");

addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");
