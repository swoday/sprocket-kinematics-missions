%% verify_sprocket_mission
% Runs the Sprocket mission end to end in MATLAB and compares every result
% with reference numbers computed outside MATLAB (cad/kinematics.py reads the
% same URDF and solves the kinematics with numpy).
%
% The mission files were written from the R2026b documentation on a machine
% without MATLAB. This script is the first thing to run on a machine that
% has it. Each row of the results table is one assumption being tested.
%
% Needs: Simscape Multibody. Closes a loaded model named Sprocket without
% saving it.

projectFolder = string(fileparts(fileparts(mfilename("fullpath"))));
missionFolder = fullfile(projectFolder, "marketplace", "missions", "sprocket-high-five");
resetFolder = fullfile(missionFolder, "task_reset_sprocket-high-five");
ref = jsondecode(fileread(fullfile(projectFolder, "cad", "mission_numbers.json")));

results = table('Size', [0 3], 'VariableTypes', ["string" "logical" "string"], ...
    'VariableNames', ["Check" "Passed" "Detail"]);
angleGap = @(a, b) max(abs(mod(a(:) - b(:) + 180, 360) - 180));
mdl = "Sprocket";
if bdIsLoaded(char(mdl))
    bdclose(char(mdl));
end

%% 1. Setup script
try
    run(fullfile(missionFolder, "setup_sprocket_high_five.m"));
    ok = isfile(urdfFile) && norm(padPosition(:) - ref.pad_position(:)) < 1e-9;
    results(end + 1, :) = {"setup leaves urdfFile and padPosition", ok, "urdfFile = " + urdfFile};
catch err
    results(end + 1, :) = {"setup leaves urdfFile and padPosition", false, string(err.message)};
end

%% 2. URDF import
try
    smimport(urdfFile, "ModelName", mdl);
    names = mdl + "/" + ["World" "fl_hip_abduct" "fl_hip_pitch" "fl_knee" "fl_foot" "pad_mount"];
    found = arrayfun(@(b) getSimulinkBlockHandle(char(b)) > 0, names);
    results(end + 1, :) = {"smimport builds the model with the expected block names", all(found), ...
        nnz(found) + " of " + numel(found) + " expected blocks found"};
catch err
    results(end + 1, :) = {"smimport builds the model with the expected block names", false, string(err.message)};
end

%% 3. Solver and joint variables
try
    ks = simscape.multibody.KinematicsSolver(mdl);
    jointTable = jointPositionVariables(ks);
    legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];
    [isThere, rows] = ismember(legJoints, string(jointTable.BlockPath));
    legIDs = string(jointTable.ID(rows(isThere)));
    ok = height(jointTable) == numel(ref.moving_joints_alphabetical) && all(isThere) ...
        && all(endsWith(legIDs, ".Rz.q")) && all(string(jointTable.Unit) == "deg");
    results(end + 1, :) = {"13 joint position variables, leg IDs found, unit deg", ok, ...
        "legIDs = " + join(legIDs, ", ")};
catch err
    results(end + 1, :) = {"13 joint position variables, leg IDs found, unit deg", false, string(err.message)};
end

%% 4. Frame variables
try
    addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");
    pawIDs = "Paw.Translation." + ["x"; "y"; "z"];
    frameTable = frameVariables(ks);
    ok = all(ismember(pawIDs, string(frameTable.ID)));
    results(end + 1, :) = {"frame ports World/W and fl_foot/F are accepted", ok, ...
        "IDs = " + join(string(frameTable.ID), ", ")};
catch err
    results(end + 1, :) = {"frame ports World/W and fl_foot/F are accepted", false, string(err.message)};
end

%% 5. Forward kinematics
try
    addTargetVariables(ks, legIDs);
    addOutputVariables(ks, pawIDs);
    [pawHang, flagHang] = solve(ks, [0 0 0]);
    [pawStance, flagStance] = solve(ks, ref.fk_task.targets_deg(:)');
    gap = [norm(pawHang(:) - ref.paw_hanging(:)), norm(pawStance(:) - ref.fk_task.paw_position(:))];
    ok = all(gap < 1e-4) && flagHang > 0 && flagStance == 1;
    results(end + 1, :) = {"forward kinematics matches the reference", ok, ...
        "pawStance = [" + join(compose("%.4f", pawStance(:)'), " ") + "] m, gap = " + max(gap) + " m"};
catch err
    results(end + 1, :) = {"forward kinematics matches the reference", false, string(err.message)};
end

%% 6. Inverse kinematics without a guess
try
    clearTargetVariables(ks);
    clearOutputVariables(ks);
    addTargetVariables(ks, pawIDs);
    addOutputVariables(ks, legIDs);
    [qFirst, flagFirst] = solve(ks, padPosition);
    gap = min(angleGap(qFirst, ref.ik_pad.knee_back.angles_deg), ...
        angleGap(qFirst, ref.ik_pad.knee_forward.angles_deg));
    ok = flagFirst > 0 && gap < 0.05;
    results(end + 1, :) = {"inverse kinematics from straight legs lands on one of the two answers", ok, ...
        "qFirst = [" + join(compose("%.2f", qFirst(:)'), " ") + "] deg, status " + flagFirst};
catch err
    results(end + 1, :) = {"inverse kinematics from straight legs lands on one of the two answers", false, string(err.message)};
end

%% 7. Initial guesses select the branch
try
    addInitialGuessVariables(ks, legIDs);
    [qForward, flagForward] = solve(ks, padPosition, [0 -120 80]);
    [qHighFive, flagBack] = solve(ks, padPosition, [0 40 -80]);
    gap = [angleGap(qHighFive, ref.ik_pad.knee_back.angles_deg), ...
        angleGap(qForward, ref.ik_pad.knee_forward.angles_deg)];
    ok = all(gap < 0.05) && flagBack == 1 && flagForward > 0;
    results(end + 1, :) = {"guesses pick the knee-back and knee-forward answers", ok, ...
        "qHighFive = [" + join(compose("%.2f", qHighFive(:)'), " ") + "], qForward = [" + ...
        join(compose("%.2f", qForward(:)'), " ") + "] deg"};
catch err
    results(end + 1, :) = {"guesses pick the knee-back and knee-forward answers", false, string(err.message)};
end

%% 8. Path from stance to pad
try
    n = ref.path.points;
    s = linspace(0, 1, n)';
    pawPath = (1 - s) .* ref.path.start_point(:)' + s .* ref.path.end_point(:)';
    qPath = zeros(n, 3);
    flags = zeros(n, 1);
    guess = [0 40 -80];
    for k = 1:n
        [qk, flags(k)] = solve(ks, pawPath(k, :), guess);
        qPath(k, :) = qk(:)';
        guess = qk(:)';
    end
    gap = max(abs(mod(qPath - ref.path.angles_deg + 180, 360) - 180), [], "all");
    ok = all(flags == 1) && gap < 0.05 && all(qPath(:, 3) < 0);
    results(end + 1, :) = {"25-point path matches the reference and the knee never flips", ok, ...
        "largest difference = " + gap + " deg"};
catch err
    results(end + 1, :) = {"25-point path matches the reference and the knee never flips", false, string(err.message)};
end

%% 9. The pad in the CAD is where padPosition says it is
try
    addFrameVariables(ks, "Pad", "translation", mdl + "/World/W", mdl + "/pad_mount/F");
    clearTargetVariables(ks);
    clearOutputVariables(ks);
    clearInitialGuessVariables(ks);
    addOutputVariables(ks, "Pad.Translation." + ["x"; "y"; "z"]);
    padMeasured = solve(ks);
    ok = norm(padMeasured(:) - padPosition(:)) < 1e-6;
    results(end + 1, :) = {"pad frame in the model equals padPosition", ok, ...
        "measured = [" + join(compose("%.4f", padMeasured(:)'), " ") + "] m"};
catch err
    results(end + 1, :) = {"pad frame in the model equals padPosition", false, string(err.message)};
end

%% 10. Reset scripts rebuild the state for the last task
originalPath = path;
try
    clear ks legIDs pawIDs pawStance qFirst qHighFive qPath
    addpath(missionFolder, resetFolder);
    run(fullfile(resetFolder, "reset_t14.m"));    % the chain runs reset_t02 to reset_t13 first
    path(originalPath);
    ok = isa(ks, "simscape.multibody.KinematicsSolver") && numel(legIDs) == 3 ...
        && angleGap(qHighFive, ref.ik_pad.knee_back.angles_deg) < 0.05 ...
        && norm(pawStance(:) - ref.fk_task.paw_position(:)) < 1e-4 ...
        && isequal(size(qPath), [25 3]) && all(qPath(:, 3) < 0);
    results(end + 1, :) = {"reset_t14 chain rebuilds solver, stance, high-five pose and path", ok, ...
        "qHighFive = [" + join(compose("%.2f", qHighFive(:)'), " ") + "] deg"};
catch err
    path(originalPath);
    results(end + 1, :) = {"reset_t14 chain rebuilds solver, stance, high-five pose and path", false, string(err.message)};
end

%% Report
disp(results)
if all(results.Passed)
    disp("ALL " + height(results) + " CHECKS PASSED. The mission behaves as designed.")
else
    disp(nnz(~results.Passed) + " of " + height(results) + " checks failed. Fix those rows before using the mission.")
end
clear angleGap names found isThere rows frameTable gap ok err k qk guess n s flagHang flagStance flagFirst flagForward flagBack originalPath
