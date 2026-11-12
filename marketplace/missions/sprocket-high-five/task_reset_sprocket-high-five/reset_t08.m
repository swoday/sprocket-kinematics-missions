% Ready for Task 08: the state after Task 07 (Store the leg IDs in legIDs).
run("reset_t07.m");

legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
[~, rows] = ismember(legJoints, string(T.BlockPath));
legIDs = string(T.ID(rows));
clear legJoints rows
