% Ready for Task 03: solver created, front-left leg joint IDs stored in legIDs.
run("reset_t02.m");

ks = simscape.multibody.KinematicsSolver(mdl);
jointTable = jointPositionVariables(ks);
legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
[~, rows] = ismember(legJoints, string(jointTable.BlockPath));
legIDs = string(jointTable.ID(rows));
clear jointTable legJoints rows
