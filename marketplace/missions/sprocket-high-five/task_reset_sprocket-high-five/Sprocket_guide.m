%% Sprocket guide: teach a robot dog to high-five
% This guide lists every step of the mission. Ada, your tutor, checks each
% task and answers your questions. You do the steps.
%
% How to use this guide
% * Work through one step at a time, from top to bottom.
% * A step that says "In MATLAB" has a command. Type it in the Command
%   Window, after the >> prompt, and press Enter. You can also click inside
%   the step in this file and press Ctrl+Enter (Cmd+Enter on a Mac) to run
%   only that step.
% * A step that says "In Simulink" is something that you do with the mouse
%   in the window that shows the Sprocket block diagram.
% * Every step says what it does and why you need it.
% * When you finish a task, tell Ada. Ask her about anything that is not
%   clear. No question is too basic.
%
% Do not press the Run button for the whole file. The next two lines stop
% the file if you do.
disp("Use this guide one step at a time. Read the first lines of the file.")
return

%% TASK 1. Bring Sprocket into Simscape Multibody
% Sprocket is a robot dog, powered down on a maintenance stand with his
% legs hanging straight. Engineers describe a machine like him as rigid
% parts connected by joints. A joint is the place where two parts meet and
% can move, like a door hinge or your knee. One number describes each
% hinge: its angle.
%
% Sprocket was designed in a Computer-Aided Design (CAD) program. The design
% was saved in the Unified Robot Description Format (URDF), a plain text
% file that lists every part and every joint. Your first job is to turn
% that file into a Simscape Multibody model, which is a block diagram with
% one block for each part and one block for each joint.

%% Task 1, step 1. In MATLAB
% What it does: smimport is the import function of Simscape Multibody. It
% reads a robot description file and builds a model from it. The name
% urdfFile is a variable, which is a stored value, and it already holds the
% location of the file.
% Why: MATLAB can only reason about Sprocket once he exists as a model.
% After a few seconds, a Simulink window named Sprocket opens.
smimport(urdfFile)

%% Task 1, step 2. In Simulink
% Click an empty area of the Sprocket window, then press Ctrl+D (Cmd+D on a
% Mac). You can also open the Modeling tab and select Update Model.
% What it does: Simulink assembles all the parts and opens a 3D view called
% Mechanics Explorer.
% Why: you can see what you just imported. Drag with the mouse to look
% around Sprocket.

%% Task 1, step 3. In Simulink
% Go back to the block diagram and find the blocks whose names start with
% fl_. The letters fl stand for front-left.
% What you see: four of those blocks are joints. Their names are
% fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot.
% Why: these are the joints that you will control for the rest of the
% mission.
%
% Then tell Ada: three of those four joints are hinges that move the leg,
% and one is a rigid weld that only holds the paw on. Think about your own
% leg. Which three are the hinges?

%% TASK 2. Create the solver and find the leg joints
% Sprocket is in MATLAB now, but he is only a drawing. To ask questions
% about his geometry you need a KinematicsSolver. Think of it as a geometry
% calculator. It takes a snapshot of the model and works out how the joint
% angles and the positions of the parts relate, without running a
% simulation.
%
% The solver keeps its own list of every joint angle. However, it does not
% use the joint names. It gives each angle a short ID of its own, such as
% j5.Rz.q, which reads as joint 5, rotation about the z axis of that joint,
% position. Before you can move the front-left leg, you have to find out
% which IDs belong to it.

%% Task 2, step 1. In MATLAB
% What it does: KinematicsSolver creates the geometry calculator for the
% model whose name is in quotes. The prefix simscape.multibody is the name
% of the package, a kind of folder, where MATLAB keeps this function. The
% result is stored in the variable ks. The semicolon at the end stops
% MATLAB from printing the result, so nothing visible happens.
% Why: every later command needs ks.
ks = simscape.multibody.KinematicsSolver("Sprocket");

%% Task 2, step 2. In MATLAB
% What it does: jointPositionVariables asks the solver for a table of every
% joint angle that it knows. Each row is one joint angle. The ID column is
% the name that the solver uses for the angle. The BlockPath column tells
% you which joint block in the Simulink model the angle belongs to. The
% Unit column gives the unit.
% Why: you need the IDs of the three front-left joints.
T = jointPositionVariables(ks)

%% Task 2, step 3. In MATLAB
% Find the three rows whose BlockPath ends in fl_hip_abduct, fl_hip_pitch
% and fl_knee. They are normally the first three rows.
% What it does: T.ID takes the ID column of the table, and the numbers in
% parentheses keep rows 1 to 3. If the three joints are on other rows, use
% those row numbers instead, for example legIDs = T.ID([4 5 6]).
% Why: legIDs is now your shortcut for the three leg angles, in the order
% hip abduction, hip pitch, knee.
legIDs = T.ID(1:3)

% Then tell Ada: look at the Unit column of the table. Which unit does the
% solver use for joint angles?

%% TASK 3. Tell the solver where the paw is
% The solver knows every joint angle now. However, it does not know which
% point on Sprocket you care about. Positions are measured with frames. A
% frame is a small coordinate system attached to a part: an origin point
% and three axes named x, y and z. Think of a frame as a combination of a
% GPS and a compass. It tells you where a part is and which way it is
% facing.
%
% One frame never moves, and it is called the world frame. It sits on the
% floor under the middle of the body, with x pointing forward, y pointing
% to the left of Sprocket and z pointing up. To track the paw, you ask the
% solver to measure the frame of the paw from the world frame. That
% measurement is called a frame variable.

%% Task 3, step 1. In Simulink
% In the Sprocket block diagram, find the block named World and the joint
% block named fl_foot. Look at the small letters on those blocks.
% What you see: each letter marks a port, and each port is a frame. The
% world frame is port W of the World block. The joint fl_foot holds the paw
% on, and its port F sits at the centre of the paw.
% Why: the next command needs the names of these two frames.

%% Task 3, step 2. In MATLAB
% What it does: addFrameVariables tells the solver to measure one frame
% from another. Its five inputs are the solver, a group name of your
% choice, the kind of measurement, the frame to measure from and the frame
% to measure to. You write a frame as the model name, the block name and
% the port name, with slashes between them. The word translation means the
% distances along x, y and z.
% Why: the solver can now report where the paw is.
addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");

%% Task 3, step 3. In MATLAB
% What it does: frameVariables lists the measurements that the solver
% knows. Three new rows appear: Paw.Translation.x, Paw.Translation.y and
% Paw.Translation.z, in metres.
% Why: you will use these three IDs in the next task.
frameVariables(ks)

% Then tell Ada: if Sprocket lifts his paw straight up, which of those
% three numbers changes: x, y or z?

%% TASK 4. Move into the ready stance with forward kinematics
% Time to wake him up. When every joint is at 0 degrees, Sprocket hangs
% straight, so each angle tells you how far a joint has turned from that
% pose. In his ready stance, the front-left leg has fl_hip_abduct at 0,
% fl_hip_pitch at 40 and fl_knee at -80 degrees.
%
% Working out where the paw ends up for joint angles that you already know
% is called forward kinematics. It is the easy direction. Bend your own
% knee by a known amount, and there is exactly one place where your foot
% can be. The solver needs you to give every variable a role. A target is
% a variable whose value you supply. An output is a variable that the
% solver calculates for you.
%
% Before you start, make a prediction and tell Ada. With the leg hanging
% straight, the paw is as low as it can go. Will bending the joints make
% the paw end up higher or lower?

%% Task 4, step 1. In MATLAB
% What it does: addTargetVariables marks variables as targets, which are
% the values that you will supply. Here the targets are the three leg
% angles.
% Why: in a forward problem you know the angles.
addTargetVariables(ks,legIDs);

%% Task 4, step 2. In MATLAB
% What it does: the first command builds the three paw IDs by joining the
% same text to x, y and z. The second command, addOutputVariables, marks
% them as outputs, which are the values that the solver calculates for
% you.
% Why: in a forward problem you want the paw position.
pawIDs = "Paw.Translation." + ["x";"y";"z"];
addOutputVariables(ks,pawIDs);

%% Task 4, step 3. In MATLAB
% What it does: solve runs the calculation. The numbers in square brackets
% are the target values, in the same order as legIDs: 0 for hip abduction,
% 40 for hip pitch and -80 for the knee. Two results come back. The first,
% pawStance, holds the x, y and z of the paw in metres. The second, status,
% is 1 when the solver met every target.
% Why: this is the answer to the forward problem.
[pawStance,status] = solve(ks,[0 40 -80])

%% Task 4, step 4. In MATLAB
% What it does: viewSolution opens a 3D viewer that shows Sprocket in the
% pose that the solver just found.
% Why: numbers are hard to picture, and the viewer lets you check the pose
% with your own eyes. Use it after every solve from now on.
viewSolution(ks)

% Then tell Ada: hanging straight, the paw was at a height of z = 0.08
% metres. Compare that with the third number in pawStance. Was your
% prediction right?

%% TASK 5. Reach the pad with inverse kinematics
% Now flip the question. A trainer has fixed a high-five pad to the stand.
% The point that the paw has to reach is stored in padPosition: three
% numbers, x, y and z in metres, measured in the world frame. This time you
% know where the paw should be, and you want the joint angles that put it
% there. That is inverse kinematics. Every robot has to answer this
% question before it can touch anything.
%
% It is also the hard direction, because the solver cannot calculate the
% angles directly. Instead, it searches. It adjusts the angles a little at
% a time until the paw lands on the target. A number called the status
% flag tells you how the search went.

%% Task 5, step 1. In MATLAB
% What it does: these two functions remove the roles that you assigned in
% the forward problem. The variables themselves stay.
% Why: a variable can have only one role at a time, and you are about to
% swap the roles.
clearTargetVariables(ks); clearOutputVariables(ks);

%% Task 5, step 2. In MATLAB
% What it does: these are the same two functions as before, with the lists
% swapped.
% Why: the paw position is now what you know, and the leg angles are what
% you want.
addTargetVariables(ks,pawIDs);
addOutputVariables(ks,legIDs);

%% Task 5, step 3. In MATLAB
% What it does: solve searches for joint angles that put the paw on the
% point stored in padPosition. The result qFirst holds three angles in
% degrees, in the order of legIDs: hip abduction, hip pitch and knee.
% Why: these are the angles that the motors in the leg would have to reach.
[qFirst,status] = solve(ks,padPosition)

%% Task 5, step 4. In MATLAB
% What it does: the viewer shows the pose where the search ended.
% Why: you can see whether the paw touches the pad.
viewSolution(ks)

% Then tell Ada: which status flag did you get? A status of 1 means that
% the paw reached the pad. A negative status means that the search stopped
% before it got there. Both are fine here.

%% TASK 6. Pick the pose the real joints can reach
% Look at the knee in the solution viewer. The paw can reach the pad in two
% ways: with the knee tucked back behind the leg, as in the ready stance,
% or with the knee flipped forward above the body. You can feel the same
% thing with your own arm. Put a fingertip on the table and move your elbow
% up and down. The fingertip stays where it is, yet your joint angles
% change.
%
% The solver only does geometry, so it ignores joint limits. However, the
% real knee can move only between -160 and +5 degrees, so only one of the
% two answers is real. The solver starts its search from a pose and stops
% at the first answer that it finds. An initial guess is a starting pose
% that you choose, so that the search ends at the answer that you want.

%% Task 6, step 1. In MATLAB
% What it does: typing the name of a variable prints its value. The third
% number is the knee angle. If it is greater than +5, the knee has flipped
% forward, past its limit.
% Why: the solver does not check joint limits, so you have to.
qFirst

%% Task 6, step 2. In MATLAB
% What it does: addInitialGuessVariables gives the leg angles a third role,
% initial guess, which is the pose where the search starts.
% Why: a search that starts near the answer that you want ends at that
% answer.
addInitialGuessVariables(ks,legIDs);

%% Task 6, step 3. In MATLAB
% What it does: solve now has a third input, the guess. The values 0, 40
% and -80 are the ready stance, where the knee already bends the right way.
% Why: starting from the ready stance leads the search to the answer with
% the knee tucked back.
[qHighFive,status] = solve(ks,padPosition,[0 40 -80])

%% Task 6, step 4. In MATLAB
% What to check: look at the knee in the viewer. The knee angle, the third
% number in qHighFive, should be close to -103 degrees, which is inside
% the limit.
viewSolution(ks)

% Then tell Ada: why can the same paw position have two different sets of
% joint angles? Use the fingertip and elbow example if it helps.

%% TASK 7. Plan the move from stance to high-five
% A real robot cannot jump from one pose to another. It has to pass through
% every pose in between, so your last job is to plan the move. A path is
% simply many inverse kinematics problems in a row, one for each point
% between where the paw is and where it needs to be. If each search starts
% from the previous answer, neighbouring answers stay close together, and
% the knee never flips.

%% Task 7, step 1. In MATLAB
% What it does: n is the number of points. The function linspace makes n
% evenly spaced numbers from 0 to 1, and the apostrophe turns that row into
% a column.
% Why: s says how far along the path each point is, from 0 at the start to
% 1 at the end.
n = 25; s = linspace(0,1,n)';

%% Task 7, step 2. In MATLAB
% What it does: this blends the two positions. When s is 0 you get
% pawStance, and when s is 1 you get padPosition. In between, you get
% points on the straight line that joins them. Each row of pawPath is one
% point.
% Why: these are the 25 places where the paw has to be.
pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';

%% Task 7, step 3. In MATLAB
% What it does: zeros makes a grid of zeros with n rows and 3 columns,
% ready for the answers. The variable guess holds the ready stance as the
% first starting pose.
% Why: the loop in the next step fills qPath row by row.
qPath = zeros(n,3); guess = [0 40 -80];

%% Task 7, step 4. In MATLAB
% What it does: a for loop repeats its commands, here once for each point.
% Each pass solves one point, stores the three angles as row k of qPath,
% and keeps them as the guess for the next point.
% Why: starting each search from the previous answer keeps the motion
% smooth.
for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end

%% Task 7, step 5. In MATLAB
% What it does: plot draws one line for each column of qPath, and legend
% labels the three lines.
% Why: the figure shows how each joint angle changes along the move.
plot(s,qPath); legend("abduct","pitch","knee")

%% Task 7, step 6. In MATLAB
% What you see: Sprocket in the last pose of the path, giving you a
% high-five.
viewSolution(ks)

% Then tell Ada: look at the three lines in your figure. Are they smooth,
% or does any line jump suddenly?
