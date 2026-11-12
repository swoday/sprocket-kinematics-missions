% Ready for Task 07: the state after Task 06 (Store the leg IDs in legIDs).
run("reset_t06.m");

legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
[~, rows] = ismember(legJoints, string(T.BlockPath));
legIDs = string(T.ID(rows));
clear legJoints rows
