# Sprocket guide: teach a robot dog to high-five

This guide holds every task of the mission. You know MATLAB. Simscape
Multibody, robotics and CAD are new to you, so nothing here expects you to
know one of their functions in advance.

## How to work through this mission

1. Ada, your tutor, gives you one small task at a time. A task is one action.
2. Every task has the same four parts:
   * **Background.** The story so far and the idea behind the task.
   * **The function.** What the function is, what goes in and what comes out.
     For a task that you do with the mouse, this part says what to look for.
   * **Why.** The reason for this action.
   * **Your task.** What to do, with the exact command.
3. Do the task. **In MATLAB** means that you type the command in the Command
   Window. **In Simulink** means that you use the mouse in the window that
   shows the Sprocket block diagram.
4. Tell Ada that you are done. She checks your work in MATLAB and gives you
   the next task.
5. Ask Ada for a hint whenever you like. The first hint of every task explains
   the function again and gives the exact command. You can also ask her what
   any word means. No question is too basic.
6. After every solve, look at Sprocket with `viewSolution`. Seeing the pose is
   the point.

## Task 1. Start here: open the guide with edit

**Background:** Welcome. In this mission you teach a robot dog named Sprocket
to give a high-five. You already know MATLAB. The new parts are Simscape
Multibody, which models machines made of parts and joints, and its
KinematicsSolver, which works out how joint angles and positions relate. You
are not expected to know any of their functions.

This is how you will work. Ada, your tutor, gives you one small task at a
time. Every task gives you the same four things: the background, the function
that you need, why you need it, and your task. You do the task in MATLAB or in
Simulink, then you tell Ada, and she checks your work and gives you the next
task.

**The function:** edit opens a file in the MATLAB Editor. The mission setup
stored the location of the guide in the variable guideFile. The guide is a
Markdown file named Sprocket_guide.md, and it holds every task of the mission.

**Why:** the first section of the guide explains how to work through the
mission. You can return to the guide at any time to read ahead or to look
back.

**Your task, in MATLAB:** bring the guide to the front and read its first
section, How to work through this mission.

```matlab
edit(guideFile)
```

**Then tell Ada:** When you want the exact command for a task, which two
places give it to you?

## Task 2. Import Sprocket with smimport

**Background:** Meet Sprocket. He is a robot dog, powered down on a
maintenance stand with his legs hanging straight. His design was made in a
Computer-Aided Design (CAD) program and saved in the Unified Robot Description
Format (URDF). A URDF file is a plain text file that lists every rigid part of
a robot and every joint that connects two parts. Simscape Multibody is the
MATLAB product that models such machines as block diagrams in Simulink.

**The function:** smimport imports a robot description into Simscape
Multibody. You give it the location of a URDF file, and it builds a Simulink
model with one block for each part and one block for each joint. The mission
setup stored the location of the file in the variable urdfFile. After a few
seconds, a Simulink window named Sprocket opens.

**Why:** the solver that you will use works on a Simscape Multibody model, so
Sprocket has to become one first.

**Your task, in MATLAB:** import the URDF file of Sprocket.

```matlab
smimport(urdfFile)
```

## Task 3. See Sprocket in 3D

**Background:** The block diagram describes Sprocket, but it does not look
like a dog. When you update a Simscape Multibody model, Simulink assembles the
parts at their joints and shows the result in a 3D viewer called Mechanics
Explorer.

**What to look for:** Mechanics Explorer opens in its own window. It shows
Sprocket on his stand, with a round pad in front of him. Drag with the mouse
to rotate the view.

**Why:** seeing the robot makes every later task easier to picture, and it
confirms that the import worked.

**Your task, in Simulink:** click an empty area of the Sprocket model window,
then press Ctrl+D (Cmd+D on a Mac). You can also open the Modeling tab and
select Update Model.

**Then tell Ada:** What colour are his paws?

## Task 4. Find the front-left leg joints

**Background:** Engineers describe a machine like Sprocket as rigid parts
connected by joints. A joint is the place where two parts meet and can move,
like a door hinge or your knee. A hinge is called a revolute joint, and one
number describes it: its angle. A leg with three hinges needs three numbers,
which engineers call three Degrees Of Freedom (DOF).

**What to look for:** in the block diagram, every part is a subsystem block,
and every joint is a block that sits between two parts. The blocks of the
front-left leg have names that start with fl_. Four of them are joints:
fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot.

**Why:** these are the joints that you will drive for the rest of the mission,
so you need to know their names.

**Your task, in Simulink:** go back to the Sprocket block diagram and find the
four joint blocks whose names start with fl_.

**Then tell Ada:** Three of those four joints are hinges that move the leg,
and one is a rigid weld that only holds the paw on. Think about your own leg.
Which three do you think are the hinges?

## Task 5. Create the solver with KinematicsSolver

**Background:** Kinematics is the geometry of motion. It describes how the
joint angles of a machine and the positions of its parts depend on each other,
with no forces or motors involved. Simscape Multibody answers kinematics
questions with an object called a KinematicsSolver. Think of it as a geometry
calculator for one model.

**The function:** simscape.multibody.KinematicsSolver creates the solver
object. You give it the name of a loaded model. It takes a snapshot of the
parts and joints of that model, and it does not run a simulation.

**Why:** every other function in this mission takes this object as its first
input.

**Your task, in MATLAB:** create a solver for the model named Sprocket and
store it in a variable named ks.

```matlab
ks = simscape.multibody.KinematicsSolver("Sprocket");
```

## Task 6. List the joint angles with jointPositionVariables

**Background:** The solver calls every quantity that it can work with a
variable. Each joint angle is a joint position variable. The solver does not
use the joint names from the model. It gives each variable an ID of its own,
such as j5.Rz.q, which reads as joint 5, rotation about the z axis of that
joint, position.

**The function:** jointPositionVariables returns a table with one row for each
joint angle. The ID column holds the ID that the solver uses. The BlockPath
column names the joint block in the model that the angle belongs to. The Unit
column gives the unit.

**Why:** you need the IDs of the three front-left leg joints, and this table
is where you look them up.

**Your task, in MATLAB:** list the joint position variables and store the
table in a variable named T.

```matlab
T = jointPositionVariables(ks)
```

**Then tell Ada:** Look at the Unit column of the table. Which unit does the
solver use for joint angles?

## Task 7. Store the leg IDs in legIDs

**Background:** Three rows of the table belong to the front-left leg: the rows
whose BlockPath ends in fl_hip_abduct, fl_hip_pitch and fl_knee. The solver
lists the joints in the order of their block paths, so those three are
normally rows 1 to 3.

**The function:** this task needs no new function. T.ID is the ID column of
the table, and ordinary indexing picks the rows. If the three joints are on
other rows, index those rows instead, for example `legIDs = T.ID([4 5 6])`.

**Why:** the solver functions take lists of IDs as inputs. Storing the three
leg IDs once saves you from typing them in every later task.

**Your task, in MATLAB:** store the IDs of those three rows, in the order hip
abduction, hip pitch, knee, in a variable named legIDs.

```matlab
legIDs = T.ID(1:3)
```

## Task 8. Find the world frame and the paw frame

**Background:** Positions in a multibody model are measured with frames. A
frame is a coordinate system attached to a part: an origin point and three
axes named x, y and z. Think of a frame as a combination of a GPS and a
compass. It tells you where a part is and which way it is facing.

One frame never moves, and it is called the world frame. In this model it sits
on the floor under the middle of the body, with x pointing forward, y pointing
to the left of Sprocket and z pointing up.

**What to look for:** in the block diagram, a frame is a port on a block,
marked with a small letter. The world frame is port W of the block named
World. The joint block fl_foot holds the paw on the leg, and one of its ports
sits at the centre of the paw.

**Why:** the next task tells the solver to measure the paw frame from the
world frame, so you need to know where both frames are.

**Your task, in Simulink:** find the block named World and the joint block
named fl_foot in the Sprocket block diagram, and read the letters on their
ports.

**Then tell Ada:** Which two letters mark the ports of the fl_foot block?

## Task 9. Measure the paw with addFrameVariables

**Background:** The solver knows every joint angle, but it does not yet know
which point on Sprocket you care about. You tell it by defining frame
variables. A frame variable is a measurement of one frame, called the
follower, from another frame, called the base.

**The function:** addFrameVariables creates the measurement. Its inputs are
the solver, a group name of your choice, the kind of measurement, the base
frame and the follower frame. The kind translation gives three variables: the
distances along x, y and z. You write each frame as a path: the model name,
the block name and the port name, with slashes between them.

**Why:** a high-five is about where the paw is, so the solver needs variables
for the position of the paw.

**Your task, in MATLAB:** add frame variables that measure the translation of
the paw frame, Sprocket/fl_foot/F, from the world frame, Sprocket/World/W. Use
the group name Paw.

```matlab
addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");
```

## Task 10. List the measurements with frameVariables

**Background:** The solver now has three new variables, one for each axis of
the world frame. Remember the directions: x points forward, y points to the
left of Sprocket and z points up.

**The function:** frameVariables returns a table of the frame variables of the
solver. The ID column holds their IDs, and the Base and Follower columns show
the two frames of each measurement. You should see Paw.Translation.x,
Paw.Translation.y and Paw.Translation.z, in metres.

**Why:** the table confirms what you created, and it holds the IDs that you
need next.

**Your task, in MATLAB:** list the frame variables and store the table in a
variable named F.

```matlab
F = frameVariables(ks)
```

**Then tell Ada:** If Sprocket lifts his paw straight up, which of those three
numbers changes: x, y or z?

## Task 11. Store the paw IDs in pawIDs

**Background:** You stored the IDs of the leg angles in legIDs. The position
of the paw needs the same treatment.

**The function:** this task needs no new function. F.ID is the ID column of
the table F. It holds Paw.Translation.x, Paw.Translation.y and
Paw.Translation.z.

**Why:** from now on, legIDs stands for the joint angles of the leg and pawIDs
stands for the position of the paw. Every kinematics problem in this mission
connects those two lists.

**Your task, in MATLAB:** store the three paw IDs, in the order x, y, z, in a
variable named pawIDs.

```matlab
pawIDs = F.ID
```

## Task 12. Make the leg angles the targets with addTargetVariables

**Background:** Time to wake Sprocket up. A kinematics problem has knowns and
unknowns. Forward kinematics is the problem where you know the joint angles
and you want the position of a part. It is the easy direction. Bend your own
knee by a known amount, and there is exactly one place where your foot can be.
The solver calls a known variable a target.

**The function:** addTargetVariables marks variables as targets. Its inputs
are the solver and a list of variable IDs. You supply the values of the
targets later, when you solve.

**Why:** in the forward problem, the three leg angles are what you know.

**Your task, in MATLAB:** make the three leg angles in legIDs the targets.

```matlab
addTargetVariables(ks,legIDs);
```

## Task 13. Make the paw position the output with addOutputVariables

**Background:** The solver calls a variable that you want it to calculate an
output. In the forward problem, the output is the position of the paw.

**The function:** addOutputVariables marks variables as outputs. Its inputs
are the solver and a list of variable IDs. The solver returns the values of
the outputs when you solve.

**Why:** the solver only reports the variables that you ask for.

**Your task, in MATLAB:** make the three paw variables in pawIDs the outputs.

```matlab
addOutputVariables(ks,pawIDs);
```

## Task 14. Solve the forward problem with solve

**Background:** When every joint is at 0 degrees, Sprocket hangs straight, so
each angle tells you how far a joint has turned from that pose. In his ready
stance, the front-left leg has fl_hip_abduct at 0, fl_hip_pitch at 40 and
fl_knee at -80 degrees. Before you solve, make a prediction. With the leg
hanging straight, the paw is as low as it can go. Will bending the joints make
the paw end up higher or lower?

**The function:** solve runs the solver. Its inputs are the solver and the
values of the targets, in the same order as the target list. It returns the
values of the outputs, and then a status flag. A status of 1 means that the
solver met every target. A negative status means that it could not.

**Why:** this call answers the forward problem: where is the paw in the ready
stance?

**Your task, in MATLAB:** solve for the ready stance, with the target values
0, 40 and -80, and store the paw position in a variable named pawStance.

```matlab
[pawStance,status] = solve(ks,[0 40 -80])
```

**Then tell Ada:** Hanging straight, the paw was at a height of z = 0.08
metres. Compare that with the third number in pawStance. Was your prediction
right?

## Task 15. See the ready stance with viewSolution

**Background:** Numbers are hard to picture. The solver comes with a viewer
that draws the model in the pose that it just found.

**The function:** viewSolution opens the Kinematics Solver Viewer, a 3D window
that shows the pose from the last call to solve. Its only input is the solver.

**Why:** looking at the pose is the quickest way to catch a mistake. Use
viewSolution after every solve from now on.

**Your task, in MATLAB:** open the viewer and look at the front-left leg.

```matlab
viewSolution(ks)
```

**Then tell Ada:** Look at the front-left leg in the viewer. Is the knee bent,
or is the leg still straight?

## Task 16. Clear the roles with clearTargetVariables and clearOutputVariables

**Background:** Now flip the question. A trainer has fixed a high-five pad to
the stand. The mission setup stored the point that the paw has to reach in
padPosition: three numbers, x, y and z in metres, measured in the world frame.
This time you know where the paw should be, and you want the joint angles that
put it there. That problem is called inverse kinematics. Every robot has to
solve it before it can touch anything.

**The function:** clearTargetVariables and clearOutputVariables remove the
target and output roles from all variables. Each takes only the solver as
input. The variables themselves stay.

**Why:** a variable can have only one of these two roles at a time, and you
are about to give them the other way round.

**Your task, in MATLAB:** remove the target and output roles from the solver.

```matlab
clearTargetVariables(ks); clearOutputVariables(ks);
```

## Task 17. Swap the roles with addTargetVariables and addOutputVariables

**Background:** In the inverse problem, the position of the paw is what you
know, and the leg angles are what you want.

**The function:** these are the two functions that you used for the forward
problem. Only the lists change: pawIDs now goes to addTargetVariables, and
legIDs goes to addOutputVariables.

**Why:** the roles tell the solver which problem to solve. The same model and
the same variables now describe the inverse problem.

**Your task, in MATLAB:** make the three paw variables the targets and the
three leg angles the outputs.

```matlab
addTargetVariables(ks,pawIDs);
addOutputVariables(ks,legIDs);
```

## Task 18. Solve the inverse problem with solve

**Background:** Inverse kinematics is the hard direction. No formula gives the
solver the angles directly, so it searches. It adjusts the angles a little at
a time until the paw lands on the target.

**The function:** solve works as before. The target values are now a position,
so you give it padPosition. It returns the three leg angles in degrees, in the
order of legIDs, and the status flag. A status of 1 means that the paw reached
the target. A negative status means that the search stopped before it got
there.

**Why:** the result is the set of joint angles that the motors in the leg
would have to reach for the high-five.

**Your task, in MATLAB:** solve for the point in padPosition and store the
joint angles in a variable named qFirst.

```matlab
[qFirst,status] = solve(ks,padPosition)
```

**Then tell Ada:** Which status flag did you get, and what does it tell you?

## Task 19. See where the paw ended with viewSolution

**Background:** A status flag is only a number. Look at the pose before you
trust it.

**The function:** viewSolution shows the pose from the last solve, as before.

**Why:** the viewer shows whether the paw touches the pad. It also shows which
way the knee bends, which matters in the next task.

**Your task, in MATLAB:** open the viewer again and look at the front-left
knee.

```matlab
viewSolution(ks)
```

**Then tell Ada:** In the viewer, is the knee tucked back behind the leg, or
flipped forward above the body?

## Task 20. Check the knee angle in qFirst against its limit

**Background:** The paw can reach the pad in two ways: with the knee tucked
back behind the leg, as in the ready stance, or with the knee flipped forward
above the body. You can feel the same thing with your own arm. Put a fingertip
on the table and move your elbow up and down. The fingertip stays where it is,
yet your joint angles change.

Real joints also have limits. The real knee can move only between -160 and +5
degrees.

**The function:** this task needs no new function. The solver only does
geometry, so it ignores joint limits, and no function checks them for you.
qFirst holds the angles in the order hip abduction, hip pitch, knee.

**Why:** an answer that needs the knee to bend past its limit is useless on
the real robot, and only you can spot it.

**Your task, in MATLAB:** display qFirst and read the knee angle, which is the
third number.

```matlab
qFirst
```

**Then tell Ada:** Is the knee angle in qFirst between -160 and +5 degrees?

## Task 21. Give the search a starting pose with addInitialGuessVariables

**Background:** The solver starts its search from a pose and stops at the
first answer that it finds. Which answer it finds depends on where it starts.
An initial guess is a starting pose that you choose.

**The function:** addInitialGuessVariables marks variables as initial guesses.
Its inputs are the solver and a list of variable IDs. You supply the guess
values when you solve. A variable can be an output and an initial guess at the
same time.

**Why:** a search that starts near the answer that you want ends at that
answer.

**Your task, in MATLAB:** give the three leg angles in legIDs the initial
guess role.

```matlab
addInitialGuessVariables(ks,legIDs);
```

## Task 22. Solve again from the ready stance

**Background:** The ready stance already has the knee bent backward, so it is
a good place to start the search.

**The function:** solve takes the guess values as a third input, in the same
order as the initial guess list.

**Why:** starting from the ready stance leads the search to the answer with
the knee tucked back, which is the one inside the joint limit.

**Your task, in MATLAB:** solve for the point in padPosition again, with the
guess 0, 40 and -80, and store the answer in a variable named qHighFive.

```matlab
[qHighFive,status] = solve(ks,padPosition,[0 40 -80])
```

## Task 23. See the high-five pose with viewSolution

**Background:** You now have an answer that the real joints can reach. Check
it.

**The function:** viewSolution shows the pose from the last solve. The knee
angle, the third number in qHighFive, should be close to -103 degrees.

**Why:** the viewer confirms that the paw is on the pad with the knee tucked
back.

**Your task, in MATLAB:** open the viewer again and look at the knee.

```matlab
viewSolution(ks)
```

**Then tell Ada:** Why can the same paw position have two different sets of
joint angles? Use the fingertip and elbow example if it helps.

## Task 24. Space the path points with linspace

**Background:** A real robot cannot jump from one pose to another. It has to
pass through every pose in between, so your last job is to plan the move. A
path is many inverse kinematics problems in a row, one for each point between
where the paw is and where it has to be.

**The function:** this task uses plain MATLAB. linspace makes the evenly
spaced numbers, and the apostrophe turns the row into a column.

**Why:** the column s says how far along the path each point is, from 0 at the
start to 1 at the end.

**Your task, in MATLAB:** make 25 evenly spaced numbers from 0 to 1 and store
them as a column in a variable named s.

```matlab
n = 25; s = linspace(0,1,n)';
```

## Task 25. Blend the two paw positions into pawPath

**Background:** The paw starts at pawStance and has to end at padPosition. The
points in between lie on the straight line that joins them.

**The function:** this task uses plain MATLAB. Multiplying the column s by a
row gives one row for each point. When s is 0 the row equals pawStance, and
when s is 1 it equals padPosition.

**Why:** each row of pawPath becomes the target of one inverse kinematics
problem.

**Your task, in MATLAB:** store the points of the path in a matrix named
pawPath, with one row for each point.

```matlab
pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';
```

## Task 26. Make room for the answers with zeros

**Background:** Each point of the path gives three joint angles. The first
search also needs a starting pose.

**The function:** this task uses plain MATLAB. zeros makes the matrix for the
answers, and guess holds the ready stance.

**Why:** the loop in the next task fills qPath row by row and updates guess as
it goes.

**Your task, in MATLAB:** make a matrix of zeros named qPath with one row for
each point and three columns, and store the ready stance in a variable named
guess.

```matlab
qPath = zeros(n,3); guess = [0 40 -80];
```

## Task 27. Solve every point with a for loop

**Background:** If each search starts from the previous answer, neighbouring
answers stay close together, and the knee never flips. This idea is called a
warm start.

**The function:** the loop calls solve once for each row of pawPath. The
targets, outputs and initial guesses keep their roles between calls, so only
the numbers change.

**Why:** the result is a smooth list of joint angles that takes the paw from
the ready stance to the pad.

**Your task, in MATLAB:** solve the inverse kinematics at every point of
pawPath, store each answer as a row of qPath, and use it as the guess for the
next point. Write the loop on one line.

```matlab
for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end
```

## Task 28. Draw the joint angles with plot

**Background:** A figure shows at a glance whether the planned move is smooth.

**The function:** this task uses plain MATLAB. plot draws one line for each
column of qPath, and legend labels the lines.

**Why:** a sudden jump in a line would mean that a joint flipped between two
neighbouring points.

**Your task, in MATLAB:** draw the three joint angles along the path in a
figure with a legend.

```matlab
plot(s,qPath); legend("abduct","pitch","knee")
```

**Then tell Ada:** Look at the three lines in your figure. Are they smooth, or
does any line jump suddenly?

## Task 29. See the high-five with viewSolution

**Background:** The last solve in the loop was the last point of the path,
which is the pad.

**The function:** viewSolution shows the pose from the last solve, so it now
shows the end of the path.

**Why:** this is the moment that the whole mission was for.

**Your task, in MATLAB:** open the viewer one last time.

```matlab
viewSolution(ks)
```

**Then tell Ada:** What is Sprocket doing in the viewer?
