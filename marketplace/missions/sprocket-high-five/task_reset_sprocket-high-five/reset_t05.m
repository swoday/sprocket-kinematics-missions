% Ready for Task 05: the state after Task 04 (Find the leg joints with jointPositionVariables).
run("reset_t04.m");

T = jointPositionVariables(ks);
legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
[~, rows] = ismember(legJoints, string(T.BlockPath));
legIDs = string(T.ID(rows));
clear legJoints rows
