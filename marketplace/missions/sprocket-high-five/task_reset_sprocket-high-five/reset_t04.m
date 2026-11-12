% Ready for Task 04: Paw frame variables measure the front-left paw from the world frame.
run("reset_t03.m");

addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");
pawIDs = "Paw.Translation." + ["x"; "y"; "z"];
