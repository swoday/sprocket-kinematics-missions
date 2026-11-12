"""The task list of the Sprocket mission. tools/build_mission.py turns it into
mission.yaml, Sprocket_guide.md and the reset scripts.

The learner knows MATLAB but not Simscape Multibody, robotics or CAD. A task is
one idea: one to three commands, or one thing to do with the mouse. A task
exists only when it brings a new Simscape Multibody idea or function. Plain
MATLAB bookkeeping and "now look at it" steps ride along with the task they
belong to.

Fields of a task
  where        "MATLAB" (has commands and a "function" text) or "Simulink"
               (done with the mouse, has a "look" text)
  background   the story and the idea; blank lines separate paragraphs
  function     what each new function is, what goes in and what comes out
  look         for a Simulink task: what to look for
  why          the reason for the task
  task         what to do, in words; the commands follow automatically
  question     optional; needs a ("confirm", ...) check
  checks       ("tool name", text) or ("confirm", text)
  h2, h3       second and third hint; the first hint is generated
  reset        MATLAB lines that reproduce the result of the task
"""

FRAME_CMD = 'addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");'
LOOP_CMD = "for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end"

TASKS = [
    dict(
        title="Import Sprocket with smimport", where="MATLAB", lo=["lo01"], involves=["command"],
        background="""Meet Sprocket. He is a robot dog, powered down on a maintenance stand with his legs
        hanging straight. His design was made in a Computer-Aided Design (CAD) program and saved in the Unified
        Robot Description Format (URDF). A URDF file is a plain text file that lists every rigid part of a robot
        and every joint that connects two parts. Simscape Multibody is the MATLAB product that models such
        machines as block diagrams in Simulink.""",
        function="""smimport imports a robot description into Simscape Multibody. You give it the location of a
        URDF file, and it builds a Simulink model with one block for each part and one block for each joint. The
        mission setup stored the location of the file in the variable urdfFile. After a few seconds, a Simulink
        window named Sprocket opens.""",
        why="the solver that you will use works on a Simscape Multibody model, so Sprocket has to become one first.",
        task="import the URDF file of Sprocket.",
        commands=["smimport(urdfFile)"],
        checks=[
            ("evaluate_matlab_code", """a block diagram imported from Sprocket.urdf is loaded: list models with
             find_system("type","block_diagram") and confirm one of them has top-level blocks named World,
             fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot (for example with getSimulinkBlockHandle); accept
             any model name"""),
            ("model_overview", """the imported model's top level shows link subsystems connected by joint blocks;
             if the model tools cannot describe physical-network blocks, rely on the evaluate_matlab_code
             evidence instead of failing the task"""),
        ],
        description="Sprocket.urdf has been imported as a loaded Simscape Multibody model.",
        h2="""If MATLAB says that urdfFile does not exist, tell me and I will run the mission setup again. Pass
        urdfFile as a variable, with no quotes around it.""",
        h3="""When the import works, a Simulink window named Sprocket opens. It shows a diagram of blocks joined
        by lines. Tell me when you can see it.""",
        reset=[
            'if ~exist("urdfFile", "var") || ~isfile(urdfFile)',
            "    setup_sprocket_high_five",
            "end",
            'mdl = "Sprocket";',
            "if ~bdIsLoaded(char(mdl))",
            '    smimport(urdfFile, "ModelName", mdl);',
            "end",
        ],
    ),
    dict(
        title="Look at Sprocket and find the leg joints", where="Simulink", lo=["lo01"],
        involves=["configuration", "output_interpretation"],
        background="""The block diagram describes Sprocket, but it does not look like a dog. When you update a
        Simscape Multibody model, Simulink assembles the parts at their joints and shows the result in a 3D
        viewer called Mechanics Explorer.

        Engineers describe a machine like Sprocket as rigid parts connected by joints. A joint is the place
        where two parts meet and can move, like a door hinge or your knee. A hinge is called a revolute joint,
        and one number describes it: its angle. A leg with three hinges needs three numbers, which engineers
        call three Degrees Of Freedom (DOF).""",
        look="""Mechanics Explorer shows Sprocket on his stand, with a round pad in front of him. In the block
        diagram, every part is a subsystem block, and every joint is a block that sits between two parts. The
        blocks of the front-left leg have names that start with fl_. Four of them are joints: fl_hip_abduct,
        fl_hip_pitch, fl_knee and fl_foot.""",
        why="""seeing the robot makes every later task easier to picture. The joints of the front-left leg are the
        ones that you will drive for the rest of the mission.""",
        task="""click an empty area of the Sprocket model window and press Ctrl+D (Cmd+D on a Mac) to see
        Sprocket in 3D. Then go back to the block diagram and find the four joint blocks whose names start with
        fl_.""",
        question="""Three of those four joints are hinges that move the leg, and one is a rigid weld that only
        holds the paw on. Think about your own leg. Which three do you think are the hinges?""",
        checks=[
            ("confirm", """The learner has named the three joints of the front-left leg: fl_hip_abduct,
             fl_hip_pitch and fl_knee. Accept an answer in their own words that identifies all three."""),
        ],
        description="The learner has seen Sprocket in 3D and identified the three hinges of the front-left leg.",
        h2="""If nothing happens when you press Ctrl+D, click once on an empty white area of the block diagram
        first, so that the window is selected. You can also open the Modeling tab and select Update Model.
        Each joint name says what the joint does: fl_hip_abduct swings the whole leg sideways, fl_hip_pitch
        swings it forward and back, and fl_knee bends the lower leg.""",
        h3="""The joint fl_foot is the weld that holds the paw on. So the three hinges are fl_hip_abduct,
        fl_hip_pitch and fl_knee. Tell me those three names.""",
        reset=[],
    ),
    dict(
        title="Create the solver with KinematicsSolver", where="MATLAB", lo=["lo02"], involves=["command"],
        background="""Kinematics is the geometry of motion. It describes how the joint angles of a machine and
        the positions of its parts depend on each other, with no forces or motors involved. Simscape Multibody
        answers kinematics questions with an object called a KinematicsSolver. Think of it as a geometry
        calculator for one model.""",
        function="""simscape.multibody.KinematicsSolver creates the solver object. You give it the name of a
        loaded model. It takes a snapshot of the parts and joints of that model, and it does not run a
        simulation.""",
        why="every other function in this mission takes this object as its first input.",
        task="create a solver for the model named Sprocket and store it in a variable named ks.",
        commands=['ks = simscape.multibody.KinematicsSolver("Sprocket");'],
        checks=[
            ("evaluate_matlab_code", """the base workspace holds a simscape.multibody.KinematicsSolver object
             whose ModelName is a currently loaded model; find it by class with whos and do not require a
             particular variable name"""),
        ],
        description="A KinematicsSolver object exists for the imported model.",
        h2="""If MATLAB reports an error, check that the Sprocket window is still open and that the name in
        quotes matches its title. If you renamed the model, use your own name in place of Sprocket.""",
        h3="When it works, nothing is printed. Display `ks` if you want to see a summary of the solver.",
        reset=["ks = simscape.multibody.KinematicsSolver(mdl);"],
    ),
    dict(
        title="Find the leg joints with jointPositionVariables", where="MATLAB", lo=["lo02"],
        involves=["command", "output_interpretation"],
        background="""The solver calls every quantity that it can work with a variable. Each joint angle is a
        joint position variable. The solver does not use the joint names from the model. It gives each variable
        an ID of its own, such as j5.Rz.q, which reads as joint 5, rotation about the z axis of that joint,
        position.""",
        function="""jointPositionVariables returns a table with one row for each joint angle. The ID column holds
        the ID that the solver uses. The BlockPath column names the joint block in the model that the angle
        belongs to. The Unit column gives the unit. The rows whose BlockPath ends in fl_hip_abduct, fl_hip_pitch
        and fl_knee belong to the front-left leg. They are normally rows 1 to 3.""",
        why="""the solver functions take lists of IDs as inputs. Storing the three leg IDs once saves you from
        looking them up in every later task.""",
        task="""list the joint position variables in a table named T. Then store the IDs of the three front-left
        leg joints, in the order hip abduction, hip pitch, knee, in a variable named legIDs.""",
        commands=["T = jointPositionVariables(ks)", "legIDs = T.ID(1:3)"],
        question="Look at the Unit column of the table. Which unit does the solver use for joint angles?",
        checks=[
            ("evaluate_matlab_code", """legIDs exists and holds exactly three IDs; look each one up in the table
             returned by jointPositionVariables for the learner's solver and confirm the BlockPath values end
             with fl_hip_abduct, fl_hip_pitch and fl_knee in that order; never assume the IDs are j1, j2, j3"""),
            ("confirm", "The learner states that joint position variables are in degrees by default."),
        ],
        description="legIDs holds the variable IDs of the three front-left leg joints in order.",
        h2="""Check that the BlockPath values of rows 1 to 3 end in fl_hip_abduct, fl_hip_pitch and fl_knee, in
        that order. If the three joints are on other rows, index those rows instead, for example
        `legIDs = T.ID([4 5 6])`.""",
        h3="""The table has 13 rows, one for each joint that can move. legIDs holds three IDs, such as j1.Rz.q,
        j2.Rz.q and j3.Rz.q. The Unit column shows deg, which means degrees.""",
        reset=[
            "T = jointPositionVariables(ks);",
            'legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];',
            "[~, rows] = ismember(legJoints, string(T.BlockPath));",
            "legIDs = string(T.ID(rows));",
            "clear legJoints rows",
        ],
    ),
    dict(
        title="Measure the paw with addFrameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "configuration"],
        background="""The solver knows every joint angle, but it does not yet know which point on Sprocket you
        care about. Positions in a multibody model are measured with frames. A frame is a coordinate system
        attached to a part: an origin point and three axes named x, y and z. Think of a frame as a combination
        of a GPS and a compass. It tells you where a part is and which way it is facing.

        One frame never moves, and it is called the world frame. In this model it sits on the floor under the
        middle of the body, with x pointing forward, y pointing to the left of Sprocket and z pointing up. In
        the block diagram, a frame is a port on a block. The world frame is port W of the block named World,
        and port F of the joint block fl_foot sits at the centre of the paw.""",
        function="""addFrameVariables tells the solver to measure one frame, called the follower, from another
        frame, called the base. Its inputs are the solver, a group name of your choice, the kind of measurement,
        the base frame and the follower frame. The kind translation gives three variables: the distances along
        x, y and z. You write each frame as a path: the model name, the block name and the port name, with
        slashes between them.""",
        why="a high-five is about where the paw is, so the solver needs variables for the position of the paw.",
        task="""add frame variables that measure the translation of the paw frame, Sprocket/fl_foot/F, from the
        world frame, Sprocket/World/W. Use the group name Paw.""",
        commands=[FRAME_CMD],
        checks=[
            ("evaluate_matlab_code", """frameVariables for the learner's solver lists three translation variables
             (x, y, z, in metres) whose Base is the W port of the World block and whose Follower is a frame at
             the paw centre: the F or B port of the fl_foot joint, or an equivalent frame port on the fl_paw
             subsystem; accept any valid group name; do not accept a follower on another leg or on the knee
             joint"""),
        ],
        description="The solver has three translation frame variables that locate the front-left paw from the world frame.",
        h2="""If MATLAB reports an error, the usual cause is a path that does not match a block. Check the
        spelling and the capital letters. If you renamed your model, replace Sprocket at the start of both paths
        with your model name.""",
        h3="When it works, nothing is printed. The next task shows you what was created.",
        reset=['addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");'],
    ),
    dict(
        title="Check the measurement with frameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "output_interpretation"],
        background="""The solver now has three new variables, one for each axis of the world frame. Remember the
        directions: x points forward, y points to the left of Sprocket and z points up.""",
        function="""frameVariables returns a table of the frame variables of the solver. The ID column holds
        their IDs, and the Base and Follower columns show the two frames of each measurement. You should see
        Paw.Translation.x, Paw.Translation.y and Paw.Translation.z, in metres.""",
        why="""the table confirms what you created. Its ID column is also the list that stands for the position
        of the paw in every later task, just as legIDs stands for the leg angles.""",
        task="""list the frame variables in a table named F. Then store the three paw IDs, in the order x, y, z,
        in a variable named pawIDs.""",
        commands=["F = frameVariables(ks)", "pawIDs = F.ID"],
        question="If Sprocket lifts his paw straight up, which of those three numbers changes: x, y or z?",
        checks=[
            ("evaluate_matlab_code", """pawIDs exists and holds exactly the three Paw translation IDs of the
             learner's solver, in the order x, y, z; accept a string array, a cell array or a table column"""),
            ("confirm", """The learner says that z changes when the paw moves straight up. The reason is that the
             z axis of the world frame points up. If the learner picks x or y, explain that kindly and move
             on."""),
        ],
        description="pawIDs holds the IDs of the three paw translation variables, and the learner knows which one measures height.",
        h2="""If the table is empty, the frame variables were not added. Go back one task and run the
        addFrameVariables command again. If F holds more than three rows, keep only the three Paw rows in
        pawIDs.""",
        h3="""You should see three rows, and pawIDs should hold their three IDs. The answer to the question is z,
        because the z axis of the world frame points up.""",
        reset=["F = frameVariables(ks);", 'pawIDs = "Paw.Translation." + ["x"; "y"; "z"];'],
    ),
    dict(
        title="Set up the forward problem with addTargetVariables and addOutputVariables", where="MATLAB",
        lo=["lo04"], involves=["command"],
        background="""Time to wake Sprocket up. A kinematics problem has knowns and unknowns. Forward kinematics
        is the problem where you know the joint angles and you want the position of a part. It is the easy
        direction. Bend your own knee by a known amount, and there is exactly one place where your foot can be.
        The solver calls a known variable a target, and it calls a variable that it calculates an output.""",
        function="""addTargetVariables marks variables as targets, and addOutputVariables marks variables as
        outputs. Each takes the solver and a list of variable IDs. You supply the values of the targets when you
        solve, and the solver returns the values of the outputs.""",
        why="""the roles tell the solver which problem to solve. In the forward problem, the leg angles are what
        you know and the position of the paw is what you want.""",
        task="make the three leg angles in legIDs the targets and the three paw variables in pawIDs the outputs.",
        commands=["addTargetVariables(ks,legIDs);", "addOutputVariables(ks,pawIDs);"],
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three
             front-left leg joint position variables, and outputVariables lists the three Paw translation
             variables"""),
        ],
        description="The leg joint angles are targets and the paw translation variables are outputs.",
        h2="""If MATLAB says that legIDs or pawIDs does not exist, go back and store those IDs again. If it says
        that a variable already has a role, run `clearTargetVariables(ks); clearOutputVariables(ks);` and try
        again.""",
        h3="""When it works, nothing is printed. Display `targetVariables(ks)` and `outputVariables(ks)` to see
        the three targets and the three outputs.""",
        reset=["addTargetVariables(ks, legIDs);", "addOutputVariables(ks, pawIDs);"],
    ),
    dict(
        title="Solve the forward problem with solve and viewSolution", where="MATLAB", lo=["lo04"],
        involves=["command", "output_interpretation"],
        background="""When every joint is at 0 degrees, Sprocket hangs straight, so each angle tells you how far
        a joint has turned from that pose. In his ready stance, the front-left leg has fl_hip_abduct at 0,
        fl_hip_pitch at 40 and fl_knee at -80 degrees. Before you solve, make a prediction. With the leg hanging
        straight, the paw is as low as it can go. Will bending the joints make the paw end up higher or lower?""",
        function="""solve runs the solver. Its inputs are the solver and the values of the targets, in the same
        order as the target list. It returns the values of the outputs, and then a status flag. A status of 1
        means that the solver met every target. A negative status means that it could not. viewSolution opens
        the Kinematics Solver Viewer, a 3D window that shows the pose from the last call to solve.""",
        why="""the call to solve answers the forward problem: where is the paw in the ready stance? The viewer
        lets you check that answer with your own eyes, so use it after every solve from now on.""",
        task="""solve for the ready stance, with the target values 0, 40 and -80, and store the paw position in
        a variable named pawStance. Then open the viewer and look at the front-left leg.""",
        commands=["[pawStance,status] = solve(ks,[0 40 -80])", "viewSolution(ks)"],
        question="""Hanging straight, the paw was at a height of z = 0.08 metres. Compare that with the third
        number in pawStance. Was your prediction right?""",
        checks=[
            ("evaluate_matlab_code", """pawStance is a three-element numeric vector within 1 mm of
             [0.2200 0.1600 0.1829] metres; to judge the formulation rather than the stored numbers you may call
             solve on the learner's solver with the targets 0, 40 and -80 in the order shown by targetVariables
             and expect a status flag of 1"""),
            ("confirm", """The learner compares the third number of pawStance, about 0.18, with the hanging
             height of 0.08 and says that the paw is higher. Accept any answer that recognises the paw rose. Then
             share the rest as a takeaway instead of asking for it: the paw rose by about 0.10 m and stayed
             directly below the hip, so x and y did not change."""),
        ],
        description="pawStance holds the solved paw position for the ready stance, and the learner has seen the pose.",
        h2="""The values that you give to solve must be in the same order as the targets. Display
        `targetVariables(ks)` to see that order. It should list hip abduction, hip pitch and knee, so the values
        are 0, 40 and -80.""",
        h3="""You should get a status of 1 and a paw position close to 0.22, 0.16 and 0.18 metres. The viewer
        shows the front-left knee bent and the paw about 0.10 metres higher than when it hangs.""",
        reset=["[pawStance, status] = solve(ks, [0 40 -80]);"],
    ),
    dict(
        title="Swap the roles with clearTargetVariables and clearOutputVariables", where="MATLAB", lo=["lo05"],
        involves=["command"],
        background="""Now flip the question. A trainer has fixed a high-five pad to the stand. The mission setup
        stored the point that the paw has to reach in padPosition: three numbers, x, y and z in metres, measured
        in the world frame. This time you know where the paw should be, and you want the joint angles that put
        it there. That problem is called inverse kinematics. Every robot has to solve it before it can touch
        anything.""",
        function="""clearTargetVariables and clearOutputVariables remove the target and output roles from all
        variables. Each takes only the solver as input. The variables themselves stay. You then assign the roles
        again with the two functions from the forward problem, with the lists swapped.""",
        why="""a variable can have only one of these two roles at a time. In the inverse problem, the position
        of the paw is what you know and the leg angles are what you want.""",
        task="clear the roles, then make the three paw variables the targets and the three leg angles the outputs.",
        commands=["clearTargetVariables(ks); clearOutputVariables(ks);",
                  "addTargetVariables(ks,pawIDs); addOutputVariables(ks,legIDs);"],
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three Paw
             translation variables and outputVariables lists the three front-left leg joint position variables,
             so the roles from the forward problem have been cleared and swapped"""),
        ],
        description="The paw translation variables are targets and the leg joint angles are outputs.",
        h2="""If MATLAB says that a variable already has a role, the old roles are still in place. Run the first
        line again, then the second.""",
        h3="""When it works, nothing is printed. Display `targetVariables(ks)` to check. It should list the three
        Paw variables.""",
        reset=["clearTargetVariables(ks);", "clearOutputVariables(ks);",
               "addTargetVariables(ks, pawIDs);", "addOutputVariables(ks, legIDs);"],
    ),
    dict(
        title="Solve the inverse problem with solve and check the knee", where="MATLAB", lo=["lo05"],
        involves=["command", "output_interpretation"],
        background="""Inverse kinematics is the hard direction. No formula gives the solver the angles directly,
        so it searches. It adjusts the angles a little at a time until the paw lands on the target.

        Real joints also have limits. The real knee can move only between -160 and +5 degrees. The solver only
        does geometry, so it ignores joint limits, and no function checks them for you.""",
        function="""solve works as before. The target values are now a position, so you give it padPosition. It
        returns the three leg angles in degrees, in the order hip abduction, hip pitch, knee, and then the
        status flag. A status of 1 means that the paw reached the target. A negative status means that the
        search stopped before it got there. viewSolution shows the pose where the search ended.""",
        why="""the result is the set of joint angles that the motors in the leg would have to reach. An answer
        that needs the knee to bend past its limit is useless on the real robot, and only you can spot it.""",
        task="""solve for the point in padPosition and store the joint angles in a variable named qFirst. Then
        open the viewer and look at the front-left knee.""",
        commands=["[qFirst,status] = solve(ks,padPosition)", "viewSolution(ks)"],
        question="The knee angle is the third number in qFirst. Is it between -160 and +5 degrees?",
        checks=[
            ("evaluate_matlab_code", """qFirst is a three-element numeric vector; two answers are both correct
             here, close to [17.82 -14.45 -103.08] or [17.82 -117.53 103.08] degrees (allow 0.1 degree and
             full-turn wraps); if the learner's solve started from the straight-leg pose and returned a negative
             status flag, do not fail the task as long as the roles are right, because the next task fixes
             convergence with initial guesses"""),
            ("confirm", """The learner says whether the knee angle in qFirst is inside the range -160 to +5
             degrees, and their answer matches the current value: a value near -103 is inside, and a value near
             +103 is outside. Accept a correct reading either way."""),
        ],
        description="qFirst holds the joint angles the solver returned for the pad position, and the learner has compared the knee angle with its limit.",
        h2="""The target is now a position, so you pass the variable padPosition directly. If the status is
        negative, the search started from straight legs and lost its way. That is fine here, and the next task
        shows you how to guide it.""",
        h3="""A knee angle near -103 is inside the limit, so that answer is real. A knee angle near +103 is far
        outside the limit, so the real robot cannot reach that pose. Tell me which one you have.""",
        reset=["[qFirst, status] = solve(ks, padPosition);"],
    ),
    dict(
        title="Pick the reachable pose with addInitialGuessVariables", where="MATLAB", lo=["lo05", "lo06"],
        involves=["command", "output_interpretation"],
        background="""The paw can reach the pad in two ways: with the knee tucked back behind the leg, as in the
        ready stance, or with the knee flipped forward above the body. You can feel the same thing with your own
        arm. Put a fingertip on the table and move your elbow up and down. The fingertip stays where it is, yet
        your joint angles change.

        The solver starts its search from a pose and stops at the first answer that it finds. Which answer it
        finds depends on where it starts. An initial guess is a starting pose that you choose.""",
        function="""addInitialGuessVariables marks variables as initial guesses. Its inputs are the solver and a
        list of variable IDs. A variable can be an output and an initial guess at the same time. solve then
        takes the guess values as a third input, in the same order as the initial guess list.""",
        why="""a search that starts near the answer that you want ends at that answer. The ready stance already
        has the knee bent backward, so it leads the search to the answer inside the joint limit.""",
        task="""give the three leg angles in legIDs the initial guess role. Then solve for the point in
        padPosition again, with the guess 0, 40 and -80, and store the answer in a variable named qHighFive.
        Finish by looking at the pose in the viewer.""",
        commands=["addInitialGuessVariables(ks,legIDs);",
                  "[qHighFive,status] = solve(ks,padPosition,[0 40 -80])",
                  "viewSolution(ks)"],
        question="""Why can the same paw position have two different sets of joint angles? Use the fingertip and
        elbow example if it helps.""",
        checks=[
            ("evaluate_matlab_code", """initialGuessVariables for the learner's solver includes at least the
             front-left hip pitch and knee joint position variables"""),
            ("evaluate_matlab_code", """qHighFive is a three-element numeric vector within 0.1 degree of
             [17.82 -14.45 -103.08], in the order of the output table, so the knee angle is negative and inside
             the range -160 to +5 degrees"""),
            ("confirm", """The learner explains in their own words that a two-segment leg can reach the same
             point with the knee bent either way, so the paw position alone does not fix the joint angles. Accept
             the elbow comparison as a full answer."""),
        ],
        description="qHighFive holds the knee-back solution that respects the knee joint limit.",
        h2="""The guess values go in the third input of solve, in the same order as legIDs. The answer should be
        close to 17.8, -14.5 and -103.1 degrees, with a status of 1.""",
        h3="""Two answers exist because a leg with two segments can reach the same point with the knee bent
        either way, just like your elbow. Tell me that in your own words.""",
        reset=["addInitialGuessVariables(ks, legIDs);",
               "[qHighFive, status] = solve(ks, padPosition, [0 40 -80]);"],
    ),
    dict(
        title="Prepare the path points with linspace", where="MATLAB", lo=["lo06"], involves=["command"],
        background="""A real robot cannot jump from one pose to another. It has to pass through every pose in
        between, so your last job is to plan the move. A path is many inverse kinematics problems in a row, one
        for each point between where the paw is and where it has to be. The paw starts at pawStance and has to
        end at padPosition. The points in between lie on the straight line that joins them.""",
        function="""this task uses plain MATLAB. linspace makes a column s of evenly spaced numbers from 0 to 1.
        Blending the two positions with s gives one row of pawPath for each point. qPath is a matrix of zeros
        for the answers, and guess holds the ready stance as the first starting pose.""",
        why="each row of pawPath becomes the target of one inverse kinematics problem, and qPath collects the answers.",
        task="""make 25 points on the straight line from pawStance to padPosition in a matrix named pawPath.
        Also make a matrix of zeros named qPath with one row for each point, and a variable named guess that
        holds the ready stance.""",
        commands=["n = 25; s = linspace(0,1,n)';",
                  "pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';",
                  "qPath = zeros(n,3); guess = [0 40 -80];"],
        checks=[
            ("evaluate_matlab_code", """pawPath is numeric with three columns and at least 15 rows; its first row
             equals pawStance and its last row equals padPosition within 1 mm"""),
            ("evaluate_matlab_code", """qPath is numeric with three columns and as many rows as pawPath, and guess
             is a three-element numeric vector; accept a qPath that the loop of the next task has already
             filled"""),
        ],
        description="pawPath holds the straight-line path of the paw, qPath is ready for the answers, and guess holds a starting pose.",
        h2="""If MATLAB says that pawStance does not exist, solve the forward problem again. If the sizes do not
        match, check that s is a column and not a row.""",
        h3="When it works, nothing is printed. `size(pawPath)` and `size(qPath)` should both be 25 rows and 3 columns.",
        reset=["n = 25; s = linspace(0, 1, n)';",
               "pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';",
               "qPath = zeros(n, 3); guess = [0 40 -80];"],
    ),
    dict(
        title="Solve every point with a for loop", where="MATLAB", lo=["lo06"], involves=["command", "file_edit"],
        background="""If each search starts from the previous answer, neighbouring answers stay close together,
        and the knee never flips. This idea is called a warm start.""",
        function="""the loop calls solve once for each row of pawPath. The targets, outputs and initial guesses
        keep their roles between calls, so only the numbers change.""",
        why="the result is a smooth list of joint angles that takes the paw from the ready stance to the pad.",
        task="""solve the inverse kinematics at every point of pawPath, store each answer as a row of qPath, and
        use it as the guess for the next point. Write the loop on one line.""",
        commands=[LOOP_CMD],
        checks=[
            ("evaluate_matlab_code", """qPath is numeric with three columns and at least 15 rows; its first row is
             within 0.5 degree of [0 40 -80] and its last row within 0.5 degree of [17.82 -14.45 -103.08]; the
             knee column is negative and inside -160 to +5 on every row; no joint jumps by more than about 20
             degrees between consecutive rows"""),
        ],
        description="qPath holds a smooth joint-angle path from the ready stance to the high-five pose.",
        h2="""If MATLAB reports an error inside the loop, check that the roles are still in place: the paw
        translation as targets, and the leg angles as outputs and as initial guesses.""",
        h3="""When it works, nothing is printed. The last row, `qPath(end,:)`, should be close to 17.8, -14.5 and
        -103.1 degrees.""",
        reset=[
            "for k = 1:n",
            "    qk = solve(ks, pawPath(k, :), guess);",
            "    qPath(k, :) = qk(:)';",
            "    guess = qk(:)';",
            "end",
            "clear k qk",
        ],
    ),
    dict(
        title="Plot the path and watch the high-five with viewSolution", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        background="""A figure shows at a glance whether the planned move is smooth. The last solve in the loop
        was the last point of the path, which is the pad, so the viewer now shows the end of the move.""",
        function="""plot draws one line for each column of qPath, and legend labels the lines. viewSolution shows
        the pose from the last solve.""",
        why="""a sudden jump in a line would mean that a joint flipped between two neighbouring points. The
        viewer shows the moment that the whole mission was for.""",
        task="draw the three joint angles along the path in a figure with a legend, then open the viewer one last time.",
        commands=['plot(s,qPath); legend("abduct","pitch","knee")', "viewSolution(ks)"],
        question="Look at the three lines in your figure. Are they smooth, or does any line jump suddenly?",
        checks=[
            ("evaluate_matlab_code", """inspect all open figures, not only gcf, and find one with a legend and at
             least three plotted lines whose values match the three columns of the current qPath"""),
            ("confirm", """The learner says that the three lines are smooth, with no sudden jump. Share the
             takeaway: a jump would mean that the knee flipped between two neighbouring points, and starting each
             search from the previous answer is what prevents it. Then congratulate the learner, because the
             viewer shows Sprocket giving a high-five, and close with a short summary of what they did: import,
             solver, frame variables, forward kinematics, inverse kinematics, initial guess, path."""),
        ],
        description="A figure shows the three joint angles along the path, and the learner has seen Sprocket give a high-five.",
        h2="""The names in legend are in the same order as the columns of qPath: hip abduction, hip pitch,
        knee. If the paw is not on the pad in the viewer, run the loop of the previous task again.""",
        h3="""A figure window opens with three smooth lines, and the knee line stays below zero from start to
        end. The viewer shows Sprocket with his front-left paw pressed against the round pad.""",
        reset=['figure; plot(s, qPath); legend("abduct", "pitch", "knee");'],
    ),
]
