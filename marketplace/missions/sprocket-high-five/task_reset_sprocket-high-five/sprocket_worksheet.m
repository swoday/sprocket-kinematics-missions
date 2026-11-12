%[text] # Teach Sprocket to high-five
%[text] This live script is where you work through the mission. It has one section for each task, with the background, the function that you need and a place for your code. You know MATLAB. Simscape Multibody, robotics and CAD are new to you, so nothing here expects you to know one of their functions in advance.
%[text] ## How to work through this mission
%[text] 1. Ada, your tutor, gives you one task at a time in the chat: what to do and why. Find the section of that task in this live script.
%[text] 2. Read the section. **Background** tells the story and the idea. **The function** explains the function that you need and shows its general syntax. **Why** gives the reason. For a task that you do with the mouse, the second part is **What to look for**.
%[text] 3. Type your code in the code area at the end of the section, then run the section with `Ctrl+Enter` (`Cmd+Enter` on a Mac). The output appears next to your code.
%[text] 4. Tell Ada that you are done. She checks your work in MATLAB and gives you the next task.
%[text] 5. Ask Ada for a hint whenever you like. The first hint of every task explains the function again and gives the exact commands. You can also ask her what any word means.
%[text] 6. The exact commands of every task are in the **Solutions** section at the very bottom of this live script. Try each task first, and look there when you are stuck.
%[text] 7. Run each section once, in order. If the solver ends up in a state that you did not intend, run the sections again from Task 3, which creates a fresh solver. \
%%
%[text] ## Task 1. Import Sprocket with smimport
%[text] **Background:** Meet Sprocket. He is a robot dog, powered down on a maintenance stand with his legs hanging straight. His design was made in a Computer-Aided Design (CAD) program and saved in the *Unified Robot Description Format (URDF)*. A URDF file is a plain text file that lists every rigid part of a robot and every joint that connects two parts. Simscape Multibody is the MATLAB product that models such machines as block diagrams in Simulink.
%[text] **The function:** `smimport` imports a robot description into Simscape Multibody. You give it the location of a URDF file, and it builds a Simulink model with one block for each part and one block for each joint. The mission setup stored the location of the file in the variable `urdfFile`. After a few seconds, a Simulink window named Sprocket opens.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] smimport(file)
%[text] ```
%[text] **Why:** The solver that you will use works on a Simscape Multibody model, so Sprocket has to become one first.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 1: type your code below this line.

%%
%[text] ## Task 2. Look at Sprocket and find the leg joints
%[text] **Background:** The block diagram describes Sprocket, but it does not look like a dog. When you update a Simscape Multibody model, Simulink assembles the parts at their joints and shows the result in a 3D viewer called Multibody Explorer.
%[text] Engineers describe a machine like Sprocket as rigid parts connected by joints. A *joint* is the place where two parts meet and can move, like a door hinge or your knee. A hinge is called a *revolute joint*, and one number describes it: its angle. A leg with three hinges needs three numbers, which engineers call three *Degrees Of Freedom (DOF)*.
%[text] **What to look for:** Multibody Explorer shows Sprocket on his stand, with a round pad in front of him. In the block diagram, every part is a subsystem block, and every joint is a block that sits between two parts. The blocks of the front-left leg have names that start with `fl_`. Four of them are joints: `fl_hip_abduct`, `fl_hip_pitch`, `fl_knee` and `fl_foot`.
%[text] **Why:** Seeing the robot makes every later task easier to picture. The joints of the front-left leg are the ones that you will drive for the rest of the mission.
%[text] **Your task:** Ada gives you the task in the chat. You do it with the mouse in the Simulink window.
%%
%[text] ## Task 3. Create the solver with KinematicsSolver
%[text] **Background:** *Kinematics* is the geometry of motion. It describes how the joint angles of a machine and the positions of its parts depend on each other, with no forces or motors involved. Simscape Multibody answers kinematics questions with an object called a `KinematicsSolver`. Think of it as a geometry calculator for one model.
%[text] **The function:** `simscape.multibody.KinematicsSolver` creates the solver object. You give it the name of a loaded model. It takes a snapshot of the parts and joints of that model, and it does not run a simulation.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] ks = simscape.multibody.KinematicsSolver(modelName)
%[text] ```
%[text] **Why:** Every other function in this mission takes this object as its first input.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 3: type your code below this line.

%%
%[text] ## Task 4. Find the leg joints with jointPositionVariables
%[text] **Background:** The solver calls every quantity that it can work with a *variable*. Each joint angle is a *joint position variable*. The solver does not use the joint names from the model. It gives each variable an ID of its own, such as `j5.Rz.q`, which reads as joint 5, rotation about the z axis of that joint, position.
%[text] **The function:** `jointPositionVariables` returns a table with one row for each joint angle. The `ID` column holds the ID that the solver uses. The `BlockPath` column names the joint block in the model that the angle belongs to. The `Unit` column gives the unit. The rows whose `BlockPath` ends in `fl_hip_abduct`, `fl_hip_pitch` and `fl_knee` belong to the front-left leg. They are normally rows 1 to 3.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] T = jointPositionVariables(ks)
%[text] ids = T.ID(rows)
%[text] ```
%[text] **Why:** The solver functions take lists of IDs as inputs. Storing the three leg IDs once saves you from looking them up in every later task.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 4: type your code below this line.

%%
%[text] ## Task 5. Measure the paw with addFrameVariables
%[text] **Background:** The solver knows every joint angle, but it does not yet know which point on Sprocket you care about. Positions in a multibody model are measured with frames. A *frame* is a coordinate system attached to a part: an origin point and three axes named x, y and z. Think of a frame as a combination of a GPS and a compass. It tells you where a part is and which way it is facing.
%[text] One frame never moves, and it is called the *world frame*. In this model it sits on the floor under the middle of the body, with x pointing forward, y pointing to the left of Sprocket and z pointing up. In the block diagram, a frame is a port on a block. The world frame is port `W` of the block named `World`, and port `F` of the joint block `fl_foot` sits at the centre of the paw.
%[text] **The function:** `addFrameVariables` tells the solver to measure one frame, called the *follower*, from another frame, called the *base*. Its inputs are the solver, a group name of your choice, the kind of measurement, the base frame and the follower frame. The kind `"translation"` gives three variables: the distances along x, y and z. You write each frame as a path: the model name, the block name and the port name, with slashes between them. The world frame is `"Sprocket/World/W"`, and the paw frame is `"Sprocket/fl_foot/F"`.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] addFrameVariables(ks, groupName, "translation", baseFrame, followerFrame)
%[text] ```
%[text] **Why:** A high-five is about where the paw is, so the solver needs variables for the position of the paw.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 5: type your code below this line.

%%
%[text] ## Task 6. Check the measurement with frameVariables
%[text] **Background:** The solver now has three new variables, one for each axis of the world frame. Remember the directions: x points forward, y points to the left of Sprocket and z points up.
%[text] **The function:** `frameVariables` returns a table of the frame variables of the solver. The `ID` column holds their IDs, and the `Base` and `Follower` columns show the two frames of each measurement. You should see `Paw.Translation.x`, `Paw.Translation.y` and `Paw.Translation.z`, in metres.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] F = frameVariables(ks)
%[text] ids = F.ID
%[text] ```
%[text] **Why:** The table confirms what you created. Its `ID` column is also the list that stands for the position of the paw in every later task, just as `legIDs` stands for the leg angles.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 6: type your code below this line.

%%
%[text] ## Task 7. Set up the forward problem with addTargetVariables and addOutputVariables
%[text] **Background:** Time to wake Sprocket up. A kinematics problem has knowns and unknowns. *Forward kinematics* is the problem where you know the joint angles and you want the position of a part. It is the easy direction. Bend your own knee by a known amount, and there is exactly one place where your foot can be. The solver calls a known variable a *target*, and it calls a variable that it calculates an *output*.
%[text] **The function:** `addTargetVariables` marks variables as targets, and `addOutputVariables` marks variables as outputs. Each takes the solver and a list of variable IDs. You supply the values of the targets when you solve, and the solver returns the values of the outputs.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] addTargetVariables(ks, ids)
%[text] addOutputVariables(ks, ids)
%[text] ```
%[text] **Why:** The roles tell the solver which problem to solve. In the forward problem, the leg angles are what you know and the position of the paw is what you want.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 7: type your code below this line.

%%
%[text] ## Task 8. Solve the forward problem with solve and viewSolution
%[text] **Background:** When every joint is at 0 degrees, Sprocket hangs straight, so each angle tells you how far a joint has turned from that pose. In his ready stance, the front-left leg has `fl_hip_abduct` at 0, `fl_hip_pitch` at 40 and `fl_knee` at -80 degrees.
%[text] **The function:** `solve` runs the solver. Its inputs are the solver and the values of the targets, in the same order as the target list. It returns the values of the outputs, and then a *status flag*. A status of 1 means that the solver met every target. A negative status means that it could not. `viewSolution` opens the Kinematics Solver Viewer, a 3D window that shows the pose from the last call to `solve`.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] [outputValues, status] = solve(ks, targetValues)
%[text] viewSolution(ks)
%[text] ```
%[text] **Why:** The call to `solve` answers the forward problem: where is the paw in the ready stance? The viewer lets you check that answer with your own eyes, so use it after every solve from now on.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 8: type your code below this line.

%%
%[text] ## Task 9. Swap the roles with clearTargetVariables and clearOutputVariables
%[text] **Background:** Now flip the question. A trainer has fixed a high-five pad to the stand. The mission setup stored the point that the paw has to reach in `padPosition`: three numbers, x, y and z in metres, measured in the world frame. This time you know where the paw should be, and you want the joint angles that put it there. That problem is called *inverse kinematics*. Every robot has to solve it before it can touch anything.
%[text] **The function:** `clearTargetVariables` and `clearOutputVariables` remove the target and output roles from all variables. Each takes only the solver as input. The variables themselves stay. You then assign the roles again with `addTargetVariables` and `addOutputVariables`, with the lists swapped.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] clearTargetVariables(ks)
%[text] clearOutputVariables(ks)
%[text] ```
%[text] **Why:** A variable can have only one of these two roles at a time. In the inverse problem, the position of the paw is what you know and the leg angles are what you want.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 9: type your code below this line.

%%
%[text] ## Task 10. Solve the inverse problem with solve and check the knee
%[text] **Background:** Inverse kinematics is the hard direction. No formula gives the solver the angles directly, so it searches. It adjusts the angles a little at a time until the paw lands on the target.
%[text] Real joints also have limits. The real knee can move only between -160 and +5 degrees. The solver only does geometry, so it ignores joint limits, and no function checks them for you.
%[text] **The function:** `solve` works as before. The target values are now a position, so you give it `padPosition`. It returns the three leg angles in degrees, in the order hip abduction, hip pitch, knee, and then the status flag. A status of 1 means that the paw reached the target. A negative status means that the search stopped before it got there. `viewSolution` shows the pose where the search ended.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] [outputValues, status] = solve(ks, targetValues)
%[text] viewSolution(ks)
%[text] ```
%[text] **Why:** The result is the set of joint angles that the motors in the leg would have to reach. An answer that needs the knee to bend past its limit is useless on the real robot, and only you can spot it.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 10: type your code below this line.

%%
%[text] ## Task 11. Pick the reachable pose with addInitialGuessVariables
%[text] **Background:** The paw can reach the pad in two ways: with the knee tucked back behind the leg, as in the ready stance, or with the knee flipped forward above the body. You can feel the same thing with your own arm. Put a fingertip on the table and move your elbow up and down. The fingertip stays where it is, yet your joint angles change.
%[text] The solver starts its search from a pose and stops at the first answer that it finds. Which answer it finds depends on where it starts. An *initial guess* is a starting pose that you choose.
%[text] **The function:** `addInitialGuessVariables` marks variables as initial guesses. Its inputs are the solver and a list of variable IDs. A variable can be an output and an initial guess at the same time. `solve` then takes the guess values as a third input, in the same order as the initial guess list.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] addInitialGuessVariables(ks, ids)
%[text] [outputValues, status] = solve(ks, targetValues, guessValues)
%[text] ```
%[text] **Why:** A search that starts near the answer that you want ends at that answer. The ready stance already has the knee bent backward, so it leads the search to the answer inside the joint limit.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 11: type your code below this line.

%%
%[text] ## Task 12. Prepare the path points with linspace
%[text] **Background:** A real robot cannot jump from one pose to another. It has to pass through every pose in between, so your last job is to plan the move. A path is many inverse kinematics problems in a row, one for each point between where the paw is and where it has to be. The paw starts at `pawStance` and has to end at `padPosition`. The points in between lie on the straight line that joins them.
%[text] **The function:** this task uses plain MATLAB. `linspace` makes a column `s` of evenly spaced numbers from 0 to 1. Blending the two positions with `s` gives one row of `pawPath` for each point. `qPath` is a matrix of zeros for the answers, and `guess` holds the ready stance as the first starting pose.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] s = linspace(0, 1, n)'
%[text] points = (1-s).*startRow + s.*endRow
%[text] answers = zeros(n, 3)
%[text] ```
%[text] **Why:** Each row of `pawPath` becomes the target of one inverse kinematics problem, and `qPath` collects the answers.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 12: type your code below this line.

%%
%[text] ## Task 13. Solve every point with a for loop and plot the path
%[text] **Background:** If each search starts from the previous answer, neighbouring answers stay close together, and the knee never flips. This idea is called a *warm start*. A figure shows at a glance whether the result is smooth.
%[text] **The function:** the loop calls `solve` once for each row of `pawPath`. The targets, outputs and initial guesses keep their roles between calls, so only the numbers change. `plot` then draws one line for each column of `qPath`, and `legend` labels the lines.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] for k = 1:n
%[text]     answer = solve(ks, targetRow, guess);
%[text]     % store the answer, and use it as the next guess
%[text] end
%[text] plot(s, qPath)
%[text] legend(name1, name2, name3)
%[text] ```
%[text] **Why:** The result is a smooth list of joint angles that takes the paw from the ready stance to the pad. A sudden jump in a line of the figure would mean that a joint flipped between two neighbouring points.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 13: type your code below this line.

%%
%[text] ## Task 14. Play the high-five as a simulation and save it with smwritevideo
%[text] **Background:** The viewer of the solver shows one pose at a time, so it cannot play the move. To see Sprocket move, you play the path in a *simulation*. A simulation steps through time, and Multibody Explorer animates every step.
%[text] In a simulation, a joint follows a *motion input*: a signal that tells the joint which angle to take at each moment. The mission comes with a helper function, `sprocket_play_path`, that prepares this for you. It imports Sprocket a second time as a model named `SprocketPlayback`. It feeds the three columns of `qPath` to the three leg joints, holds every other joint still and runs the simulation. Your solver and the model `Sprocket` stay as they are.
%[text] **The function:** `sprocket_play_path` is a helper function of this mission, not a MATLAB function. You give it the URDF file and the path, and it returns the name of the model that it simulated. To read how it works, type `edit sprocket_play_path`. `smwritevideo` is a Simscape Multibody function. It saves the animation of the most recent simulation of a model as a video file in the current folder. Multibody Explorer must be open when you call it.
%[text] **Syntax:**
%[text] ```matlabCodeExample
%[text] modelName = sprocket_play_path(urdfFile, qPath)
%[text] smwritevideo(modelName, videoName)
%[text] ```
%[text] **Why:** This is how robot motion is planned in practice: a solver works out the joint angles once, and a simulation plays them. The video is the high-five that the whole mission was for, and you can share it.
%[text] **Your task:** Ada gives you the task in the chat. Type your code below, then run this section with `Ctrl+Enter`.
% Task 14: type your code below this line.

%%
%[text] ## Solutions
%[text] Try each task first. If you are stuck, ask Ada for a hint, or look here. The commands below are examples in text, so running this section does nothing. Type them in the section of their task.
%[text] **Task 1. Import Sprocket with smimport**
%[text] ```matlabCodeExample
%[text] smimport(urdfFile)
%[text] ```
%[text] **Task 2. Look at Sprocket and find the leg joints**
%[text] This task has no code. You do it with the mouse in the Simulink window.
%[text] **Task 3. Create the solver with KinematicsSolver**
%[text] ```matlabCodeExample
%[text] ks = simscape.multibody.KinematicsSolver("Sprocket");
%[text] ```
%[text] **Task 4. Find the leg joints with jointPositionVariables**
%[text] ```matlabCodeExample
%[text] T = jointPositionVariables(ks)
%[text] legIDs = T.ID(1:3)
%[text] ```
%[text] **Task 5. Measure the paw with addFrameVariables**
%[text] ```matlabCodeExample
%[text] addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");
%[text] ```
%[text] **Task 6. Check the measurement with frameVariables**
%[text] ```matlabCodeExample
%[text] F = frameVariables(ks)
%[text] pawIDs = F.ID
%[text] ```
%[text] **Task 7. Set up the forward problem with addTargetVariables and addOutputVariables**
%[text] ```matlabCodeExample
%[text] addTargetVariables(ks,legIDs);
%[text] addOutputVariables(ks,pawIDs);
%[text] ```
%[text] **Task 8. Solve the forward problem with solve and viewSolution**
%[text] ```matlabCodeExample
%[text] [pawStance,status] = solve(ks,[0 40 -80])
%[text] viewSolution(ks)
%[text] ```
%[text] **Task 9. Swap the roles with clearTargetVariables and clearOutputVariables**
%[text] ```matlabCodeExample
%[text] clearTargetVariables(ks); clearOutputVariables(ks);
%[text] addTargetVariables(ks,pawIDs); addOutputVariables(ks,legIDs);
%[text] ```
%[text] **Task 10. Solve the inverse problem with solve and check the knee**
%[text] ```matlabCodeExample
%[text] [qFirst,status] = solve(ks,padPosition)
%[text] viewSolution(ks)
%[text] ```
%[text] **Task 11. Pick the reachable pose with addInitialGuessVariables**
%[text] ```matlabCodeExample
%[text] addInitialGuessVariables(ks,legIDs);
%[text] [qHighFive,status] = solve(ks,padPosition,[0 40 -80])
%[text] viewSolution(ks)
%[text] ```
%[text] **Task 12. Prepare the path points with linspace**
%[text] ```matlabCodeExample
%[text] n = 25; s = linspace(0,1,n)';
%[text] pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';
%[text] qPath = zeros(n,3); guess = [0 40 -80];
%[text] ```
%[text] **Task 13. Solve every point with a for loop and plot the path**
%[text] ```matlabCodeExample
%[text] for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end
%[text] plot(s,qPath); legend("abduct","pitch","knee")
%[text] ```
%[text] **Task 14. Play the high-five as a simulation and save it with smwritevideo**
%[text] ```matlabCodeExample
%[text] playback = sprocket_play_path(urdfFile,qPath)
%[text] smwritevideo(playback,"sprocket_video")
%[text] ```

%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"inline"}
%---
