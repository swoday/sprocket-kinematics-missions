function mdl = sprocket_play_path(urdfFile, qPath, moveTime)
%SPROCKET_PLAY_PATH Play a precalculated joint path as a simulation of Sprocket.
%   mdl = sprocket_play_path(urdfFile, qPath) imports Sprocket a second time,
%   as a separate model named SprocketPlayback. It drives the three joints of
%   the front-left leg with the columns of qPath (hip abduction, hip pitch and
%   knee, in degrees), holds every other joint at zero and runs a simulation.
%   Multibody Explorer shows the move, and you can play it again there.
%
%   mdl = sprocket_play_path(urdfFile, qPath, moveTime) sets the duration of
%   the move in seconds. The default is 2.
%
%   To save the move as a video, simulate first with this function, then type:
%
%       smwritevideo(mdl, "sprocket_video")
%
%   Why a second model: the KinematicsSolver object of the mission keeps
%   working on the model named Sprocket, which this function does not change.
%
%   This is a helper function of the mission "Teach a Robot Dog to High-Five
%   with KinematicsSolver". The mission setup copies it into your workspace
%   folder. It is not a MATLAB or Simscape Multibody function.

arguments
    urdfFile (1,1) string
    qPath (:,3) double
    moveTime (1,1) double {mustBePositive} = 2
end

legJoints = ["fl_hip_abduct" "fl_hip_pitch" "fl_knee"];
holdTime = 0.5;                 % seconds of standing still before and after

% A path whose rows are all the same has nothing to play. This happens when
% qPath still holds the zeros of Task 12, before the loop of Task 13 fills it.
if all(abs(qPath - qPath(1, :)) < 1e-9, "all")
    error("sprocket:playPath:noMove", ...
        "Every row of qPath is %s, so there is nothing to play. " + ...
        "Run the loop of Task 13 again, so that qPath holds the solved joint angles.", ...
        mat2str(round(qPath(1, :), 2)));
end
fprintf("Playing %d poses, from %s to %s degrees.\n", size(qPath, 1), ...
    mat2str(round(qPath(1, :), 2)), mat2str(round(qPath(end, :), 2)));

% A fresh copy of the model, so that the model of the mission stays as it is.
if bdIsLoaded("SprocketPlayback")
    close_system("SprocketPlayback", 0);
end
handle = smimport(urdfFile, ModelName="SprocketPlayback");
mdl = string(get_param(handle, "Name"));

% The path against time. The first row is repeated at time zero, so that
% Sprocket stands still in the first pose before the move starts.
n = size(qPath, 1);
t = [0; holdTime + moveTime * linspace(0, 1, n)'];
q = [qPath(1, :); qPath];
stopTime = t(end) + holdTime;

% The data lives in the model workspace under two names: pathTime is the time
% of each pose in seconds, and pathAngles holds one column for each leg joint.
modelWorkspace = get_param(mdl, "ModelWorkspace");
assignin(modelWorkspace, "pathTime", t);
assignin(modelWorkspace, "pathAngles", q);

% Every joint that can take a motion input gets one: the three leg joints
% follow the path, and every other joint is held at zero. The torque of each
% of these joints is computed by Simscape Multibody.
blocks = string(find_system(char(mdl), "SearchDepth", 1, "Type", "block"));
driven = 0;
for b = blocks(:)'
    parameters = get_param(b, "DialogParameters");
    if ~isstruct(parameters)
        continue
    end
    names = string(fieldnames(parameters));
    motion = names(endsWith(names, "MotionActuationMode"));
    torque = names(endsWith(names, "TorqueActuationMode"));
    if isempty(motion) || isempty(torque)
        continue                % a fixed joint, a body or another block
    end
    set_param(b, motion(1), "InputMotion", torque(1), "ComputedTorque");

    % The motion input is the one port that the joint has gained.
    ports = get_param(b, "PortHandles");
    motionPort = [ports.LConn(2:end) ports.RConn(2:end)];
    if ~isscalar(motionPort)
        error("sprocket:playPath:port", ...
            "Expected one motion input port on %s, found %d.", b, numel(motionPort));
    end

    name = string(get_param(b, "Name"));
    position = get_param(b, "Position");
    left = position(1) - 150;
    top = position(4) + 30;
    source = mdl + "/" + name + "_angle";
    converter = mdl + "/" + name + "_to_joint";

    column = find(name == legJoints, 1);
    if isempty(column)
        add_block("simulink/Sources/Constant", source, Value="0", ...
            Position=[left top left + 40 top + 24]);
    else
        add_block("simulink/Sources/From Workspace", source, ...
            VariableName=sprintf("[pathTime pathAngles(:,%d)]", column), ...
            OutputAfterFinalValue="Holding final value", SampleTime="0", ...
            Position=[left top left + 60 top + 24]);
        driven = driven + 1;
    end

    % A joint needs the angle and its first two derivatives. The converter
    % computes them by filtering the angle.
    add_block("nesl_utility/Simulink-PS Converter", converter, Unit="deg", ...
        FilteringAndDerivatives="filter", SimscapeFilterOrder="2", ...
        InputFilterTimeConstant="0.05", ...
        Position=[left + 90 top + 2 left + 110 top + 22]);

    add_line(char(mdl), char(name + "_angle/1"), char(name + "_to_joint/1"));
    converterPorts = get_param(converter, "PortHandles");
    add_line(char(mdl), converterPorts.RConn(1), motionPort);
end
if driven ~= numel(legJoints)
    error("sprocket:playPath:joints", ...
        "Expected to drive %d leg joints, found %d.", numel(legJoints), driven);
end

set_param(mdl, "StopTime", string(stopTime), "MaxStep", "0.02");
try
    set_param(mdl, "EnablePacing", "on", "PacingRate", 1);   % play at real speed
catch
    % Without pacing the simulation is faster than real time. Play it again
    % in Multibody Explorer to see it at real speed.
end

sim(mdl);

fprintf("The move is in Multibody Explorer. Press Play there to see it again.\n");
end
