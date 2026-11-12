%% Sprocket high-five: reference solution
% The code a learner ends up typing, task by task. Run the mission setup
% script first (setup_sprocket_high_five.m): it creates urdfFile and
% padPosition.
%
% This file was written from the R2026b documentation without access to
% MATLAB. Run verify_sprocket_mission.m once before relying on it.

%% Stage 1. Import the CAD assembly into Simscape Multibody
% smimport reads the URDF (links, joints, part geometry) and builds a model
% named after the file. Press Ctrl+D in the model to see Sprocket in
% Multibody Explorer.
smimport(urdfFile);
mdl = "Sprocket";

%% Stage 2. Create the solver and find the leg joints
% The solver numbers the joints itself (j1, j2, ...), so read the table
% instead of guessing. Rz.q means rotation about the joint's z-axis.
ks = simscape.multibody.KinematicsSolver(mdl);
jointTable = jointPositionVariables(ks)

legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
[~, rows] = ismember(legJoints, string(jointTable.BlockPath));
legIDs = string(jointTable.ID(rows))

%% Stage 3. Tell the solver where the paw is
% A frame variable relates two frame ports: a base and a follower.
base = mdl + "/World/W";
follower = mdl + "/fl_foot/F";
addFrameVariables(ks, "Paw", "translation", base, follower);
frameVariables(ks)
pawIDs = "Paw.Translation." + ["x"; "y"; "z"];

%% Stage 4. Forward kinematics: joint angles in, paw position out
addTargetVariables(ks, legIDs);
addOutputVariables(ks, pawIDs);
[pawStance, status] = solve(ks, [0 40 -80])      % expect [0.2200; 0.1600; 0.1829] m, status 1
viewSolution(ks);

%% Stage 5. Inverse kinematics: paw position in, joint angles out
% A variable holds one role at a time, so clear the forward roles first.
clearTargetVariables(ks);
clearOutputVariables(ks);
addTargetVariables(ks, pawIDs);
addOutputVariables(ks, legIDs);
[qFirst, status] = solve(ks, padPosition)        % one of two valid answers

%% Stage 6. Initial guesses choose the answer
% The solver ignores joint limits. The knee can move from -160 to +5 deg, so
% only the knee-back answer is real.
addInitialGuessVariables(ks, legIDs);
[qKneeForward, status] = solve(ks, padPosition, [0 -120 80])   % knee near +103 deg: outside its limit
[qHighFive, status] = solve(ks, padPosition, [0 40 -80])       % knee near -103 deg: the real pose
viewSolution(ks);

%% Stage 7. Plan the move from stance to high-five
% Each answer seeds the next solve, so the knee never flips along the way.
n = 25;
s = linspace(0, 1, n)';
pawPath = (1 - s) .* pawStance(:)' + s .* padPosition(:)';
qPath = zeros(n, 3);
flags = zeros(n, 1);
guess = [0 40 -80];
for k = 1:n
    [qk, flags(k)] = solve(ks, pawPath(k, :), guess);
    qPath(k, :) = qk(:)';
    guess = qk(:)';
end

figure
plot(s, qPath, "LineWidth", 1.5)
grid on
xlabel("Fraction of the path from stance to pad")
ylabel("Joint angle (deg)")
legend("fl\_hip\_abduct", "fl\_hip\_pitch", "fl\_knee", "Location", "best")
title("Sprocket: joint angles for the high-five")

% The viewer shows one pose: the one from the most recent solve. To see the
% move, replay the path. Each solve starts from the stored answer.
for k = 1:n
    solve(ks, pawPath(k, :), qPath(k, :));
    viewSolution(ks);
    pause(0.1);
end

%% Bonus. Measure from the pad instead of from the world
% Frame variables can relate any two frames. Measured from the pad, "paw on
% the pad" is simply a translation of zero.
%
%   addFrameVariables(ks, "PawToPad", "translation", mdl + "/pad_mount/F", follower);
%   clearTargetVariables(ks);
%   addTargetVariables(ks, "PawToPad.Translation." + ["x"; "y"; "z"]);
%   qSame = solve(ks, [0 0 0], [0 40 -80])       % same joint angles as qHighFive
