# Sprocket guide: teach a robot dog to high-five

This guide lists every task of the mission. Each task is one action. Ada, your
tutor, checks each task and answers your questions. You do the actions.

## How to use this guide

* Work through one task at a time, from top to bottom.
* A task that says **in MATLAB** has a command on lines of its own. Type it in
  the Command Window, after the `>>` prompt, and press Enter. You can also
  copy it from here and paste it.
* A task that says **in Simulink** is something that you do with the mouse in
  the window that shows the Sprocket block diagram.
* Every task says what it does and why you need it.
* When you finish a task, tell Ada. Ask her about anything that is not clear.
  No question is too basic.
* If you would like Ada to say the command, ask her for a hint. The first hint
  of every task is the same command, with what it does and why.

## Task 1. Import Sprocket with smimport

Meet Sprocket. He is a robot dog, powered down on a maintenance stand with his
legs hanging straight. His design was made in a Computer-Aided Design (CAD)
program. It was saved in the Unified Robot Description Format (URDF), a plain
text file that lists every part and every joint. MATLAB cannot work with him
until that file becomes a model.

You will work in two places in this mission. The MATLAB Command Window is
where you type commands after the `>>` prompt. Simulink is the window that
shows a model as a diagram of blocks.

**Your one action, in MATLAB:** import the file with the smimport function.
The variable urdfFile already holds the location of the file.

```matlab
smimport(urdfFile)
```

**What it does:** smimport is the import function of Simscape Multibody. It
reads a robot description file and builds a model from it, with one block for
each part and one block for each joint.

**Why:** MATLAB can only reason about Sprocket once he exists as a model.
After a few seconds, a Simulink window named Sprocket opens.

## Task 2. See Sprocket in 3D

The diagram is correct, but it does not look like a dog yet. Simulink can
assemble the parts and show them in a 3D view called Mechanics Explorer.

**Your one action, in Simulink:** click an empty area of the Sprocket window,
then press Ctrl+D (Cmd+D on a Mac). You can also open the Modeling tab and
select Update Model.

**What you see:** Simulink assembles all the parts and opens Mechanics
Explorer. Drag with the mouse to look around Sprocket.

**Why:** seeing the robot makes every later task easier to picture.

**Then tell Ada:** What colour are his paws?

## Task 3. Find the front-left leg joints

Engineers describe a machine like Sprocket as rigid parts connected by joints.
A joint is the place where two parts meet and can move, like a door hinge or
your knee. One number describes each hinge: its angle. In the block diagram,
every part is a block, and every joint is a block that sits between two parts.

**Your one action, in Simulink:** go back to the Sprocket block diagram and
find the blocks whose names start with fl_. The letters fl stand for
front-left.

**What you see:** four of those blocks are joints. Their names are
fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot.

**Why:** these are the joints that you will control for the rest of the
mission.

**Then tell Ada:** Three of those four joints are hinges that move the leg,
and one is a rigid weld that only holds the paw on. Think about your own leg.
Which three do you think are the hinges?

## Task 4. Create the solver with KinematicsSolver

Sprocket is in MATLAB now, but he is only a drawing. To ask questions about
his geometry you need a KinematicsSolver. Think of it as a geometry
calculator. It takes a snapshot of the model and works out how the joint
angles and the positions of the parts relate, without running a simulation.

**Your one action, in MATLAB:** create a solver for the model named Sprocket
and store it in a variable named ks.

```matlab
ks = simscape.multibody.KinematicsSolver("Sprocket");
```

**What it does:** KinematicsSolver creates the geometry calculator for the
model whose name is in quotes. The prefix simscape.multibody is the name of
the package, a kind of folder, where MATLAB keeps this function. The semicolon
at the end stops MATLAB from printing the result, so nothing visible happens.

**Why:** every later command needs ks.

## Task 5. List the joint angles with jointPositionVariables

The solver keeps its own list of every joint angle. However, it does not use
the joint names. It gives each angle a short ID of its own, such as j5.Rz.q,
which reads as joint 5, rotation about the z axis of that joint, position.

**Your one action, in MATLAB:** ask the solver for its table of joint angles
and store the table in a variable named T.

```matlab
T = jointPositionVariables(ks)
```

**What it does:** jointPositionVariables returns a table with one row for each
joint angle. The ID column is the name that the solver uses for the angle. The
BlockPath column tells you which joint block in the Simulink model the angle
belongs to. The Unit column gives the unit. Leave out the semicolon, so that
MATLAB prints the table.

**Why:** you need to know which IDs belong to the front-left leg.

**Then tell Ada:** Look at the Unit column of the table. Which unit does the
solver use for joint angles?

## Task 6. Store the leg IDs in legIDs

Three rows of the table belong to the front-left leg: the rows whose BlockPath
ends in fl_hip_abduct, fl_hip_pitch and fl_knee. They are normally the first
three rows. Typing those IDs every time would be slow, so you store them once.

**Your one action, in MATLAB:** store the IDs of those three rows, in that
order, in a variable named legIDs.

```matlab
legIDs = T.ID(1:3)
```

**What it does:** T.ID takes the ID column of the table, and the numbers in
parentheses keep rows 1 to 3. If the three joints are on other rows, use those
row numbers instead, for example `legIDs = T.ID([4 5 6])`.

**Why:** legIDs is now your shortcut for the three leg angles, in the order
hip abduction, hip pitch, knee.

## Task 7. Find the world frame and the paw frame

The solver knows every joint angle now. However, it does not know which point
on Sprocket you care about. Positions are measured with frames. A frame is a
small coordinate system attached to a part: an origin point and three axes
named x, y and z. Think of a frame as a combination of a GPS and a compass. It
tells you where a part is and which way it is facing.

One frame never moves, and it is called the world frame. It sits on the floor
under the middle of the body, with x pointing forward, y pointing to the left
of Sprocket and z pointing up.

**Your one action, in Simulink:** in the Sprocket block diagram, find the
block named World and the joint block named fl_foot. Look at the small letters
on those blocks.

**What you see:** each letter marks a port, and each port is a frame. The
world frame is port W of the World block. The joint fl_foot holds the paw on,
and one of its ports sits at the centre of the paw.

**Why:** the next task measures the paw frame from the world frame, so you
need to know where both are.

**Then tell Ada:** Which two letters mark the ports of the fl_foot block?

## Task 8. Measure the paw with addFrameVariables

To track the paw, you ask the solver to measure the frame of the paw from the
world frame. That measurement is called a frame variable. You write a frame as
the model name, the block name and the port name, with slashes between them.
The world frame is Sprocket/World/W, and the paw frame is Sprocket/fl_foot/F.

**Your one action, in MATLAB:** add frame variables that measure the
translation of the paw frame from the world frame. Use the group name Paw.

```matlab
addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");
```

**What it does:** addFrameVariables tells the solver to measure one frame from
another. Its five inputs are the solver, a group name of your choice, the kind
of measurement, the frame to measure from and the frame to measure to. The
word translation means the distances along x, y and z.

**Why:** the solver can now report where the paw is.

## Task 9. List the measurements with frameVariables

The solver now has three new variables, one for each direction of the world
frame. Remember the directions: x points forward, y points to the left of
Sprocket and z points up.

**Your one action, in MATLAB:** list the frame variables and store the table
in a variable named F.

```matlab
F = frameVariables(ks)
```

**What it does:** frameVariables returns a table of the measurements that the
solver knows. You should see three rows: Paw.Translation.x, Paw.Translation.y
and Paw.Translation.z, in metres.

**Why:** you will use these three IDs in the next task.

**Then tell Ada:** If Sprocket lifts his paw straight up, which of those three
numbers changes: x, y or z?

## Task 10. Store the paw IDs in pawIDs

You stored the leg IDs in legIDs. Now do the same for the three paw IDs.

**Your one action, in MATLAB:** store the three paw IDs, in the order x, y, z,
in a variable named pawIDs.

```matlab
pawIDs = F.ID
```

**What it does:** F.ID takes the ID column of the table F. It holds
Paw.Translation.x, Paw.Translation.y and Paw.Translation.z.

**Why:** pawIDs is now your shortcut for the position of the paw.

## Task 11. Make the leg angles the targets with addTargetVariables

Time to wake him up. When every joint is at 0 degrees, Sprocket hangs
straight, so each angle tells you how far a joint has turned from that pose.
Working out where the paw ends up for joint angles that you already know is
called forward kinematics. It is the easy direction. Bend your own knee by a
known amount, and there is exactly one place where your foot can be.

The solver needs you to give every variable a role. A target is a variable
whose value you supply.

**Your one action, in MATLAB:** make the three leg angles the targets.

```matlab
addTargetVariables(ks,legIDs);
```

**What it does:** addTargetVariables marks variables as targets. Here the
targets are the three leg angles in legIDs.

**Why:** in a forward problem you know the angles.

## Task 12. Make the paw position the output with addOutputVariables

An output is a variable that the solver calculates for you. In a forward
problem, the output is the position of the paw.

**Your one action, in MATLAB:** make the three paw variables the outputs.

```matlab
addOutputVariables(ks,pawIDs);
```

**What it does:** addOutputVariables marks variables as outputs. Here the
outputs are the three paw variables in pawIDs.

**Why:** the solver now knows what you want it to work out.

## Task 13. Solve the forward problem with solve

In his ready stance, the front-left leg has fl_hip_abduct at 0, fl_hip_pitch
at 40 and fl_knee at -80 degrees. Before you solve, make a prediction. With
the leg hanging straight, the paw is as low as it can go. Will bending the
joints make the paw end up higher or lower? Make your guess before you solve.

**Your one action, in MATLAB:** solve for the ready stance and store the paw
position in a variable named pawStance.

```matlab
[pawStance,status] = solve(ks,[0 40 -80])
```

**What it does:** solve runs the calculation. The numbers in square brackets
are the target values, in the same order as legIDs: 0 for hip abduction, 40
for hip pitch and -80 for the knee. Two results come back. The first,
pawStance, holds the x, y and z of the paw in metres. The second, status, is 1
when the solver met every target.

**Why:** this is the answer to the forward problem.

**Then tell Ada:** Hanging straight, the paw was at a height of z = 0.08
metres. Compare that with the third number in pawStance. Was your prediction
right?

## Task 14. See the ready stance with viewSolution

Numbers are hard to picture. The solver has a viewer that shows Sprocket in
the pose that it just found.

**Your one action, in MATLAB:** open the solution viewer.

```matlab
viewSolution(ks)
```

**What it does:** viewSolution opens a 3D viewer that shows the pose from the
last solve. Use it after every solve from now on.

**Why:** you can check the pose with your own eyes.

**Then tell Ada:** Look at the front-left leg in the viewer. Is the knee bent,
or is the leg still straight?

## Task 15. Clear the roles with clearTargetVariables and clearOutputVariables

Now flip the question. A trainer has fixed a high-five pad to the stand. The
point that the paw has to reach is stored in padPosition: three numbers, x, y
and z in metres, measured in the world frame. This time you know where the paw
should be, and you want the joint angles that put it there. That is inverse
kinematics. Every robot has to answer this question before it can touch
anything.

A variable can have only one role at a time, so first you remove the roles
from the forward problem.

**Your one action, in MATLAB:** remove the target and output roles from the
solver.

```matlab
clearTargetVariables(ks); clearOutputVariables(ks);
```

**What it does:** these two functions remove the roles that you assigned. The
variables themselves stay.

**Why:** you are about to swap the roles.

## Task 16. Swap the roles with addTargetVariables and addOutputVariables

In the inverse problem, the paw position is what you know, and the leg angles
are what you want.

**Your one action, in MATLAB:** make the three paw variables the targets and
the three leg angles the outputs.

```matlab
addTargetVariables(ks,pawIDs);
addOutputVariables(ks,legIDs);
```

**What it does:** these are the same two functions as before, with the lists
swapped.

**Why:** the solver now knows that you will give it a position and that it
must work out the angles.

## Task 17. Solve the inverse problem with solve

Inverse kinematics is the hard direction, because the solver cannot calculate
the angles directly. Instead, it searches. It adjusts the angles a little at a
time until the paw lands on the target. A number called the status flag tells
you how the search went.

**Your one action, in MATLAB:** solve for the point in padPosition and store
the joint angles in a variable named qFirst.

```matlab
[qFirst,status] = solve(ks,padPosition)
```

**What it does:** solve searches for joint angles that put the paw on the
point stored in padPosition. The result qFirst holds three angles in degrees,
in the order of legIDs: hip abduction, hip pitch and knee.

**Why:** these are the angles that the motors in the leg would have to reach.

**Then tell Ada:** Which status flag did you get? A status of 1 means that the
paw reached the pad. A negative status means that the search stopped before it
got there.

## Task 18. See where the paw ended with viewSolution

Look at the result before you trust it.

**Your one action, in MATLAB:** open the solution viewer again.

```matlab
viewSolution(ks)
```

**What it does:** the viewer shows the pose where the search ended.

**Why:** you can see whether the paw touches the pad, and which way the knee
bends.

**Then tell Ada:** In the viewer, is the knee tucked back behind the leg, or
flipped forward above the body?

## Task 19. Check the knee angle in qFirst against its limit

The paw can reach the pad in two ways: with the knee tucked back behind the
leg, as in the ready stance, or with the knee flipped forward above the body.
You can feel the same thing with your own arm. Put a fingertip on the table
and move your elbow up and down. The fingertip stays where it is, yet your
joint angles change.

The solver only does geometry, so it ignores joint limits. However, the real
knee can move only between -160 and +5 degrees.

**Your one action, in MATLAB:** print qFirst and read the knee angle, which is
the third number.

```matlab
qFirst
```

**What it does:** typing the name of a variable prints its value.

**Why:** the solver does not check joint limits, so you have to.

**Then tell Ada:** Is the knee angle in qFirst between -160 and +5 degrees?

## Task 20. Give the search a starting pose with addInitialGuessVariables

The solver starts its search from a pose and stops at the first answer that it
finds. An initial guess is a starting pose that you choose, so that the search
ends at the answer that you want.

**Your one action, in MATLAB:** give the three leg angles the initial guess
role.

```matlab
addInitialGuessVariables(ks,legIDs);
```

**What it does:** addInitialGuessVariables gives variables a third role,
initial guess, which is the pose where the search starts.

**Why:** a search that starts near the answer that you want ends at that
answer.

## Task 21. Solve again from the ready stance

The ready stance already has the knee bent the right way, so it makes a good
starting pose.

**Your one action, in MATLAB:** solve for the point in padPosition again,
starting from the ready stance, and store the answer in a variable named
qHighFive.

```matlab
[qHighFive,status] = solve(ks,padPosition,[0 40 -80])
```

**What it does:** solve now has a third input, the guess. The values 0, 40 and
-80 are the ready stance.

**Why:** starting from the ready stance leads the search to the answer with
the knee tucked back.

## Task 22. See the high-five pose with viewSolution

Check the pose that the real joints can reach.

**Your one action, in MATLAB:** open the solution viewer again.

```matlab
viewSolution(ks)
```

**What it does:** the viewer shows the new pose, with the paw on the pad and
the knee tucked back.

**Why:** you can confirm that this answer looks like a move that a real dog
could make.

**Then tell Ada:** Why can the same paw position have two different sets of
joint angles? Use the fingertip and elbow example if it helps.

## Task 23. Space the path points with linspace

A real robot cannot jump from one pose to another. It has to pass through
every pose in between, so your last job is to plan the move. A path is simply
many inverse kinematics problems in a row, one for each point between where
the paw is and where it needs to be.

**Your one action, in MATLAB:** make 25 evenly spaced numbers from 0 to 1 and
store them as a column in a variable named s.

```matlab
n = 25; s = linspace(0,1,n)';
```

**What it does:** n is the number of points. The function linspace makes n
evenly spaced numbers from 0 to 1, and the apostrophe turns that row into a
column.

**Why:** s says how far along the path each point is, from 0 at the start to 1
at the end.

## Task 24. Blend the two paw positions into pawPath

The paw starts at pawStance and has to end at padPosition. The points in
between lie on the straight line that joins them.

**Your one action, in MATLAB:** store the points of the path in a matrix named
pawPath, with one row for each point.

```matlab
pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';
```

**What it does:** this blends the two positions. When s is 0 you get
pawStance, and when s is 1 you get padPosition. In between, you get points on
the line that joins them.

**Why:** these are the places where the paw has to be, one after the other.

## Task 25. Make room for the answers with zeros

Each point of the path will give three joint angles. You need a place to keep
them, and a starting pose for the first search.

**Your one action, in MATLAB:** make a matrix of zeros named qPath with one
row for each point and three columns, and store the ready stance in a variable
named guess.

```matlab
qPath = zeros(n,3); guess = [0 40 -80];
```

**What it does:** zeros makes a grid of zeros with n rows and 3 columns. The
variable guess holds the ready stance as the first starting pose.

**Why:** the loop in the next task fills qPath row by row.

## Task 26. Solve every point with a for loop

If each search starts from the previous answer, neighbouring answers stay
close together, and the knee never flips.

**Your one action, in MATLAB:** solve the inverse kinematics at every point of
pawPath, and use each answer as the guess for the next point.

```matlab
for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end
```

**What it does:** a for loop repeats its commands, here once for each point.
Each pass solves one point, stores the three angles as row k of qPath, and
keeps them as the guess for the next point. Type the whole loop on one line.

**Why:** starting each search from the previous answer keeps the motion
smooth.

## Task 27. Draw the joint angles with plot

A figure shows at a glance whether the move is smooth.

**Your one action, in MATLAB:** draw the three joint angles along the path in
a figure with a legend.

```matlab
plot(s,qPath); legend("abduct","pitch","knee")
```

**What it does:** plot draws one line for each column of qPath, and legend
labels the three lines.

**Why:** the figure shows how each joint angle changes along the move.

**Then tell Ada:** Look at the three lines in your figure. Are they smooth, or
does any line jump suddenly?

## Task 28. See the high-five with viewSolution

The last solve in the loop was the last point of the path, which is the pad.

**Your one action, in MATLAB:** open the solution viewer one last time.

```matlab
viewSolution(ks)
```

**What it does:** the viewer shows the last pose of the path.

**Why:** this is the moment that the whole mission was for.

**Then tell Ada:** What is Sprocket doing in the viewer?
