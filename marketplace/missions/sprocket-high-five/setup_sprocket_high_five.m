% Setup for sprocket-high-five: Teach a Robot Dog to High-Five
%
% Context: Sprocket is a robot dog that sits powered down on a maintenance
% stand with his legs hanging straight. A trainer's high-five pad is fixed
% to the stand in front of his front-left leg. The CAD assembly ships as a
% URDF file plus one STL file per part.
% Goal: The learner imports the assembly into Simscape Multibody and uses
% KinematicsSolver to move the front-left paw onto the pad.

%% Check the product this mission teaches
assert(exist("smimport", "file") > 0, "Sprocket:setup:noSimscapeMultibody", ...
    "This mission needs Simscape Multibody: the smimport function was not found.");

%% Locate the CAD files
% The Interactive Missions app copies mission.yaml, this script and the
% complete task_reset folder into the learner workspace, and nothing else.
% The URDF and the part geometry therefore travel inside the task_reset
% folder.
resetName = "task_reset_sprocket-high-five";
scriptFolder = string(fileparts(mfilename("fullpath")));
candidates = [fullfile(scriptFolder, resetName), ...
    fullfile(string(pwd), ".interactive-missions", "content", resetName), ...
    string(fileparts(which("Sprocket.urdf")))];
isCad = arrayfun(@(c) isfile(fullfile(c, "Sprocket.urdf")) && ...
    isfolder(fullfile(c, "sprocket_parts")), candidates);
assert(any(isCad), "Sprocket:setup:missingCad", ...
    "Could not find Sprocket.urdf and the sprocket_parts folder. " + ...
    "Prepare the mission workspace again from the Interactive Missions app.");
info = dir(fullfile(candidates(find(isCad, 1)), "Sprocket.urdf"));
cadFolder = string(info(1).folder);                 % absolute path

%% Choose where the learner's copy of the URDF goes
[contentParent, contentLeaf] = fileparts(scriptFolder);
if isfolder(fullfile(pwd, ".interactive-missions"))
    workFolder = string(pwd);                       % learner workspace
elseif contentLeaf == "content" && endsWith(contentParent, ".interactive-missions")
    workFolder = string(fileparts(contentParent));  % learner workspace
else
    workFolder = fullfile(string(tempdir), "sprocket-high-five");   % authoring or validation run
    if ~isfolder(workFolder)
        mkdir(workFolder);
    end
end

%% Write a URDF that points at the part files by full path
% Simscape Multibody stores each mesh file name exactly as the URDF gives it.
% Full paths keep the imported model working whatever the current folder is.
partsFolder = replace(fullfile(cadFolder, "sprocket_parts"), "\", "/");
partsFolder = replace(partsFolder, "&", "&amp;");
urdfText = string(fileread(fullfile(cadFolder, "Sprocket.urdf")));
urdfText = replace(urdfText, "filename=""sprocket_parts/", "filename=""" + partsFolder + "/");
urdfFile = fullfile(workFolder, "Sprocket.urdf");
writelines(urdfText, urdfFile);

%% Mission data
% Where the centre of the front-left paw touches the high-five pad, in
% metres, measured in the world frame.
padPosition = [0.47 0.19 0.44];

%% Give the learner the step-by-step guide
% The guide lists every step of every task: where to work, the command,
% what it does and why. The learner gets a copy in the workspace folder, so
% that notes and edits never touch the copied mission files. An existing
% copy is kept, because it may hold the learner's notes.
guideFile = fullfile(workFolder, "Sprocket_guide.m");
if ~isfile(guideFile)
    copyfile(fullfile(cadFolder, "Sprocket_guide.m"), guideFile);
end
try
    edit(guideFile);    % opens the guide in the MATLAB Editor
catch
    % MATLAB may be running without a desktop. The guide is still on disk.
end

%% Clean up internal variables
clear resetName scriptFolder candidates isCad info cadFolder
clear contentParent contentLeaf workFolder partsFolder urdfText

disp("Sprocket is on the stand. His URDF file is " + urdfFile);
disp("The step-by-step guide is open in the MATLAB Editor: " + guideFile);
