# Sprocket guide: teach a robot dog to high-five

This guide holds every task of the mission. You know MATLAB. Simscape
Multibody, robotics and CAD are new to you, so nothing here expects you to
know one of their functions in advance.

## How to work through this mission

1. Ada, your tutor, gives you one task at a time. A task is one idea: one to
   three commands, or one thing to do with the mouse.
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

## Task 1. Import Sprocket with smimport

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

## Task 2. Look at Sprocket and find the leg joints

**Background:** The block diagram describes Sprocket, but it does not look
like a dog. When you update a Simscape Multibody model, Simulink assembles the
parts at their joints and shows the result in a 3D viewer called Mechanics
Explorer.

Engineers describe a machine like Sprocket as rigid parts connected by joints.
A joint is the place where two parts meet and can move, like a door hinge or
your knee. A hinge is called a revolute joint, and one number describes it:
its angle. A leg with three hinges needs three numbers, which engineers call
three Degrees Of Freedom (DOF).

**What to look for:** Mechanics Explorer shows Sprocket on his stand, with a
round pad in front of him. In the block diagram, every part is a subsystem
block, and every joint is a block that sits between two parts. The blocks of
the front-left leg have names that start with fl_. Four of them are joints:
fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot.

**Why:** seeing the robot makes every later task easier to picture. The joints
of the front-left leg are the ones that you will drive for the rest of the
mission.

**Your task, in Simulink:** click an empty area of the Sprocket model window
and press Ctrl+D (Cmd+D on a Mac) to see Sprocket in 3D. Then go back to the
block diagram and find the four joint blocks whose names start with fl_.

**Then tell Ada:** Three of those four joints are hinges that move the leg,
and one is a rigid weld that only holds the paw on. Think about your own leg.
Which three do you think are the hinges?

## Task 3. Create the solver with KinematicsSolver

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

## Task 4. Find the leg joints with jointPositionVariables

**Background:** The solver calls every quantity that it can work with a
variable. Each joint angle is a joint position variable. The solver does not
use the joint names from the model. It gives each variable an ID of its own,
such as j5.Rz.q, which reads as joint 5, rotation about the z axis of that
joint, position.

**The function:** jointPositionVariables returns a table with one row for each
joint angle. The ID column holds the ID that the solver uses. The BlockPath
column names the joint block in the model that the angle belongs to. The Unit
column gives the unit. The rows whose BlockPath ends in fl_hip_abduct,
fl_hip_pitch and fl_knee belong to the front-left leg. They are normally rows
1 to 3.

**Why:** the solver functions take lists of IDs as inputs. Storing the three
leg IDs once saves you from looking them up in every later task.

**Your task, in MATLAB:** list the joint position variables in a table named
T. Then store the IDs of the three front-left leg joints, in the order hip
abduction, hip pitch, knee, in a variable named legIDs.

```matlab
T = jointPositionVariables(ks)
legIDs = T.ID(1:3)
```

**Then tell Ada:** Look at the Unit column of the table. Which unit does the
solver use for joint angles?

## Task 5. Measure the paw with addFrameVariables

**Background:** The solver knows every joint angle, but it does not yet know
which point on Sprocket you care about. Positions in a multibody model are
measured with frames. A frame is a coordinate system attached to a part: an
origin point and three axes named x, y and z. Think of a frame as a
combination of a GPS and a compass. It tells you where a part is and which way
it is facing.

One frame never moves, and it is called the world frame. In this model it sits
on the floor under the middle of the body, with x pointing forward, y pointing
to the left of Sprocket and z pointing up. In the block diagram, a frame is a
port on a block. The world frame is port W of the block named World, and port
F of the joint block fl_foot sits at the centre of the paw.

**The function:** addFrameVariables tells the solver to measure one frame,
called the follower, from another frame, called the base. Its inputs are the
solver, a group name of your choice, the kind of measurement, the base frame
and the follower frame. The kind translation gives three variables: the
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

## Task 6. Check the measurement with frameVariables

**Background:** The solver now has three new variables, one for each axis of
the world frame. Remember the directions: x points forward, y points to the
left of Sprocket and z points up.

**The function:** frameVariables returns a table of the frame variables of the
solver. The ID column holds their IDs, and the Base and Follower columns show
the two frames of each measurement. You should see Paw.Translation.x,
Paw.Translation.y and Paw.Translation.z, in metres.

**Why:** the table confirms what you created. Its ID column is also the list
that stands for the position of the paw in every later task, just as legIDs
stands for the leg angles.

**Your task, in MATLAB:** list the frame variables in a table named F. Then
store the three paw IDs, in the order x, y, z, in a variable named pawIDs.

```matlab
F = frameVariables(ks)
pawIDs = F.ID
```

**Then tell Ada:** If Sprocket lifts his paw straight up, which of those three
numbers changes: x, y or z?

## Task 7. Set up the forward problem with addTargetVariables and addOutputVariables

**Background:** Time to wake Sprocket up. A kinematics problem has knowns and
unknowns. Forward kinematics is the problem where you know the joint angles
and you want the position of a part. It is the easy direction. Bend your own
knee by a known amount, and there is exactly one place where your foot can be.
The solver calls a known variable a target, and it calls a variable that it
calculates an output.

**The function:** addTargetVariables marks variables as targets, and
addOutputVariables marks variables as outputs. Each takes the solver and a
list of variable IDs. You supply the values of the targets when you solve, and
the solver returns the values of the outputs.

**Why:** the roles tell the solver which problem to solve. In the forward
problem, the leg angles are what you know and the position of the paw is what
you want.

**Your task, in MATLAB:** make the three leg angles in legIDs the targets and
the three paw variables in pawIDs the outputs.

```matlab
addTargetVariables(ks,legIDs);
addOutputVariables(ks,pawIDs);
```

## Task 8. Solve the forward problem with solve and viewSolution

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
viewSolution opens the Kinematics Solver Viewer, a 3D window that shows the
pose from the last call to solve.

**Why:** the call to solve answers the forward problem: where is the paw in
the ready stance? The viewer lets you check that answer with your own eyes, so
use it after every solve from now on.

**Your task, in MATLAB:** solve for the ready stance, with the target values
0, 40 and -80, and store the paw position in a variable named pawStance. Then
open the viewer and look at the front-left leg.

```matlab
[pawStance,status] = solve(ks,[0 40 -80])
viewSolution(ks)
```

**Then tell Ada:** Hanging straight, the paw was at a height of z = 0.08
metres. Compare that with the third number in pawStance. Was your prediction
right?

## Task 9. Swap the roles with clearTargetVariables and clearOutputVariables

**Background:** Now flip the question. A trainer has fixed a high-five pad to
the stand. The mission setup stored the point that the paw has to reach in
padPosition: three numbers, x, y and z in metres, measured in the world frame.
This time you know where the paw should be, and you want the joint angles that
put it there. That problem is called inverse kinematics. Every robot has to
solve it before it can touch anything.

**The function:** clearTargetVariables and clearOutputVariables remove the
target and output roles from all variables. Each takes only the solver as
input. The variables themselves stay. You then assign the roles again with the
two functions from the forward problem, with the lists swapped.

**Why:** a variable can have only one of these two roles at a time. In the
inverse problem, the position of the paw is what you know and the leg angles
are what you want.

**Your task, in MATLAB:** clear the roles, then make the three paw variables
the targets and the three leg angles the outputs.

```matlab
clearTargetVariables(ks); clearOutputVariables(ks);
addTargetVariables(ks,pawIDs); addOutputVariables(ks,legIDs);
```

## Task 10. Solve the inverse problem with solve and check the knee

**Background:** Inverse kinematics is the hard direction. No formula gives the
solver the angles directly, so it searches. It adjusts the angles a little at
a time until the paw lands on the target.

Real joints also have limits. The real knee can move only between -160 and +5
degrees. The solver only does geometry, so it ignores joint limits, and no
function checks them for you.

**The function:** solve works as before. The target values are now a position,
so you give it padPosition. It returns the three leg angles in degrees, in the
order hip abduction, hip pitch, knee, and then the status flag. A status of 1
means that the paw reached the target. A negative status means that the search
stopped before it got there. viewSolution shows the pose where the search
ended.

**Why:** the result is the set of joint angles that the motors in the leg
would have to reach. An answer that needs the knee to bend past its limit is
useless on the real robot, and only you can spot it.

**Your task, in MATLAB:** solve for the point in padPosition and store the
joint angles in a variable named qFirst. Then open the viewer and look at the
front-left knee.

```matlab
[qFirst,status] = solve(ks,padPosition)
viewSolution(ks)
```

**Then tell Ada:** The knee angle is the third number in qFirst. Is it between
-160 and +5 degrees?

## Task 11. Pick the reachable pose with addInitialGuessVariables

**Background:** The paw can reach the pad in two ways: with the knee tucked
back behind the leg, as in the ready stance, or with the knee flipped forward
above the body. You can feel the same thing with your own arm. Put a fingertip
on the table and move your elbow up and down. The fingertip stays where it is,
yet your joint angles change.

The solver starts its search from a pose and stops at the first answer that it
finds. Which answer it finds depends on where it starts. An initial guess is a
starting pose that you choose.

**The function:** addInitialGuessVariables marks variables as initial guesses.
Its inputs are the solver and a list of variable IDs. A variable can be an
output and an initial guess at the same time. solve then takes the guess
values as a third input, in the same order as the initial guess list.

**Why:** a search that starts near the answer that you want ends at that
answer. The ready stance already has the knee bent backward, so it leads the
search to the answer inside the joint limit.

**Your task, in MATLAB:** give the three leg angles in legIDs the initial
guess role. Then solve for the point in padPosition again, with the guess 0,
40 and -80, and store the answer in a variable named qHighFive. Finish by
looking at the pose in the viewer.

```matlab
addInitialGuessVariables(ks,legIDs);
[qHighFive,status] = solve(ks,padPosition,[0 40 -80])
viewSolution(ks)
```

**Then tell Ada:** Why can the same paw position have two different sets of
joint angles? Use the fingertip and elbow example if it helps.

## Task 12. Prepare the path points with linspace

**Background:** A real robot cannot jump from one pose to another. It has to
pass through every pose in between, so your last job is to plan the move. A
path is many inverse kinematics problems in a row, one for each point between
where the paw is and where it has to be. The paw starts at pawStance and has
to end at padPosition. The points in between lie on the straight line that
joins them.

**The function:** this task uses plain MATLAB. linspace makes a column s of
evenly spaced numbers from 0 to 1. Blending the two positions with s gives one
row of pawPath for each point. qPath is a matrix of zeros for the answers, and
guess holds the ready stance as the first starting pose.

**Why:** each row of pawPath becomes the target of one inverse kinematics
problem, and qPath collects the answers.

**Your task, in MATLAB:** make 25 points on the straight line from pawStance
to padPosition in a matrix named pawPath. Also make a matrix of zeros named
qPath with one row for each point, and a variable named guess that holds the
ready stance.

```matlab
n = 25; s = linspace(0,1,n)';
pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';
qPath = zeros(n,3); guess = [0 40 -80];
```

## Task 13. Solve every point with a for loop

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

## Task 14. Plot the path and watch the high-five with viewSolution

**Background:** A figure shows at a glance whether the planned move is smooth.
The last solve in the loop was the last point of the path, which is the pad,
so the viewer now shows the end of the move.

**The function:** plot draws one line for each column of qPath, and legend
labels the lines. viewSolution shows the pose from the last solve.

**Why:** a sudden jump in a line would mean that a joint flipped between two
neighbouring points. The viewer shows the moment that the whole mission was
for.

**Your task, in MATLAB:** draw the three joint angles along the path in a
figure with a legend, then open the viewer one last time.

```matlab
plot(s,qPath); legend("abduct","pitch","knee")
viewSolution(ks)
```

**Then tell Ada:** Look at the three lines in your figure. Are they smooth, or
does any line jump suddenly?
