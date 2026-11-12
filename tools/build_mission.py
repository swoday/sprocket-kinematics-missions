#!/usr/bin/env python3
"""Build the Sprocket mission from one list of tasks.

The learner knows MATLAB but not Simscape Multibody, robotics or CAD. One task
is one action, and every task gives the same four things in the same order:

  Background     the story and the idea, in plain words
  The function   what the function is, what goes in and what comes out
                 (for a task done with the mouse: what to look for)
  Why            the reason for this action
  Your task      what to do, with the exact command

The stock tutor shows only the title and the goal of a task, so every title
names what to type, and the first hint repeats the function, the reason and
the exact command. This script writes three things that must always agree:

  marketplace/missions/sprocket-high-five/mission.yaml
  .../task_reset_sprocket-high-five/Sprocket_guide.md     (opened by setup)
  .../task_reset_sprocket-high-five/reset_tNN.m           (one per task after the first)

Edit the TASKS list below, then run:  python3 tools/build_mission.py
Check the result with:               python3 tools/validate_mission.py
"""
import re
import textwrap
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MISSION = PROJECT / "marketplace" / "missions" / "sprocket-high-five"
RESET = MISSION / "task_reset_sprocket-high-five"

VERSION = "2.2.0"
GUIDE_NAME = "Sprocket_guide.md"

FRAME_CMD = 'addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");'
LOOP_CMD = "for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end"
VIEW = ["viewSolution(ks)"]

# where: "MATLAB" tasks have commands and a "function" text; "Simulink" tasks are done with the
# mouse and have a "look" text. checks: ("tool name", text) or ("confirm", text).
# reset: MATLAB lines that reproduce the result of the task.
TASKS = [
    dict(
        title="Start here: open the guide with edit", where="MATLAB", lo=[], involves=["command"],
        background="""Welcome. In this mission you teach a robot dog named Sprocket to give a high-five. You
        already know MATLAB. The new parts are Simscape Multibody, which models machines made of parts and
        joints, and its KinematicsSolver, which works out how joint angles and positions relate. You are not
        expected to know any of their functions.

        This is how you will work. Ada, your tutor, gives you one small task at a time. Every task gives you the
        same four things: the background, the function that you need, why you need it, and your task. You do the
        task in MATLAB or in Simulink, then you tell Ada, and she checks your work and gives you the next task.""",
        function="""edit opens a file in the MATLAB Editor. The mission setup stored the location of the guide in
        the variable guideFile. The guide is a Markdown file named Sprocket_guide.md, and it holds every task
        of the mission.""",
        why="""the first section of the guide explains how to work through the mission. You can return to the
        guide at any time to read ahead or to look back.""",
        task="bring the guide to the front and read its first section, How to work through this mission.",
        commands=["edit(guideFile)"],
        question="When you want the exact command for a task, which two places give it to you?",
        checks=[
            ("evaluate_matlab_code", "guideFile exists in the base workspace and names an existing file"),
            ("confirm", """The learner names the two places that give the exact command: a hint from Ada and the
             guide in the MATLAB Editor. Accept either one if the learner clearly knows how to get help, and
             tell them the other."""),
        ],
        description="The learner has opened the guide and knows how to work through the mission.",
        h2="""If MATLAB says that guideFile does not exist, tell me and I will run the mission setup again. You
        can also open the file Sprocket_guide.md from the Current Folder panel.""",
        h3="""The first section of the guide gives the answer. You get the exact command by asking me for a hint,
        or by reading the task in the guide. Tell me those two places.""",
        reset=[
            'if ~exist("urdfFile", "var") || ~isfile(urdfFile)',
            "    setup_sprocket_high_five",
            "end",
        ],
    ),
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
        title="See Sprocket in 3D", where="Simulink", lo=["lo01"], involves=["configuration", "output_interpretation"],
        background="""The block diagram describes Sprocket, but it does not look like a dog. When you update a
        Simscape Multibody model, Simulink assembles the parts at their joints and shows the result in a 3D
        viewer called Mechanics Explorer.""",
        look="""Mechanics Explorer opens in its own window. It shows Sprocket on his stand, with a round pad in
        front of him. Drag with the mouse to rotate the view.""",
        why="seeing the robot makes every later task easier to picture, and it confirms that the import worked.",
        task="""click an empty area of the Sprocket model window, then press Ctrl+D (Cmd+D on a Mac). You can
        also open the Modeling tab and select Update Model.""",
        question="What colour are his paws?",
        checks=[
            ("confirm", """The learner says that they can see Sprocket in 3D in Mechanics Explorer and names the
             colour of the paws. The paws are amber, so accept orange, gold or yellow as well. If the learner
             reports grey, the colours did not load, which is fine. Accept that too."""),
        ],
        description="The learner has updated the model and seen Sprocket in Mechanics Explorer.",
        h2="""If nothing happens, click once on an empty white area of the Sprocket block diagram first, so that
        the window is selected, and press Ctrl+D again. If an error message appears, read it to me.""",
        h3="""Mechanics Explorer is a separate window. It shows a white robot dog on a dark stand. The paws are
        the balls at the ends of his legs.""",
        reset=[],
    ),
    dict(
        title="Find the front-left leg joints", where="Simulink", lo=["lo01"], involves=["output_interpretation"],
        background="""Engineers describe a machine like Sprocket as rigid parts connected by joints. A joint is
        the place where two parts meet and can move, like a door hinge or your knee. A hinge is called a
        revolute joint, and one number describes it: its angle. A leg with three hinges needs three numbers,
        which engineers call three Degrees Of Freedom (DOF).""",
        look="""in the block diagram, every part is a subsystem block, and every joint is a block that sits
        between two parts. The blocks of the front-left leg have names that start with fl_. Four of them are
        joints: fl_hip_abduct, fl_hip_pitch, fl_knee and fl_foot.""",
        why="these are the joints that you will drive for the rest of the mission, so you need to know their names.",
        task="go back to the Sprocket block diagram and find the four joint blocks whose names start with fl_.",
        question="""Three of those four joints are hinges that move the leg, and one is a rigid weld that only
        holds the paw on. Think about your own leg. Which three do you think are the hinges?""",
        checks=[
            ("confirm", """The learner has named the three joints of the front-left leg: fl_hip_abduct,
             fl_hip_pitch and fl_knee. Accept an answer in their own words that identifies all three."""),
        ],
        description="The learner has identified the three hinges of the front-left leg.",
        h2="""Each joint name says what the joint does. The joint fl_hip_abduct swings the whole leg sideways,
        fl_hip_pitch swings it forward and back, and fl_knee bends the lower leg.""",
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
        h3="""When it works, nothing is printed. Display `ks` if you want to see a summary of the solver.""",
        reset=["ks = simscape.multibody.KinematicsSolver(mdl);"],
    ),
    dict(
        title="List the joint angles with jointPositionVariables", where="MATLAB", lo=["lo02"],
        involves=["command", "output_interpretation"],
        background="""The solver calls every quantity that it can work with a variable. Each joint angle is a
        joint position variable. The solver does not use the joint names from the model. It gives each variable
        an ID of its own, such as j5.Rz.q, which reads as joint 5, rotation about the z axis of that joint,
        position.""",
        function="""jointPositionVariables returns a table with one row for each joint angle. The ID column holds
        the ID that the solver uses. The BlockPath column names the joint block in the model that the angle
        belongs to. The Unit column gives the unit.""",
        why="you need the IDs of the three front-left leg joints, and this table is where you look them up.",
        task="list the joint position variables and store the table in a variable named T.",
        commands=["T = jointPositionVariables(ks)"],
        question="Look at the Unit column of the table. Which unit does the solver use for joint angles?",
        checks=[
            ("evaluate_matlab_code", """a KinematicsSolver object exists; if the base workspace also holds a
             table with ID, BlockPath and Unit columns, that shows the learner listed the joint position
             variables, but do not fail the task only because the table was not stored"""),
            ("confirm", "The learner states that joint position variables are in degrees by default."),
        ],
        description="The learner has listed the joint position variables and read their unit.",
        h2="""If MATLAB says that ks does not exist, go back one task and create the solver again. Leave out the
        semicolon here, so that the table is displayed.""",
        h3="""The table has 13 rows, one for each joint that can move. The first three belong to the front-left
        leg. The Unit column shows deg, which means degrees.""",
        reset=["T = jointPositionVariables(ks);"],
    ),
    dict(
        title="Store the leg IDs in legIDs", where="MATLAB", lo=["lo02"], involves=["command"],
        background="""Three rows of the table belong to the front-left leg: the rows whose BlockPath ends in
        fl_hip_abduct, fl_hip_pitch and fl_knee. The solver lists the joints in the order of their block paths,
        so those three are normally rows 1 to 3.""",
        function="""this task needs no new function. T.ID is the ID column of the table, and ordinary indexing
        picks the rows. If the three joints are on other rows, index those rows instead, for example
        `legIDs = T.ID([4 5 6])`.""",
        why="""the solver functions take lists of IDs as inputs. Storing the three leg IDs once saves you from
        typing them in every later task.""",
        task="store the IDs of those three rows, in the order hip abduction, hip pitch, knee, in a variable named legIDs.",
        commands=["legIDs = T.ID(1:3)"],
        checks=[
            ("evaluate_matlab_code", """legIDs exists and holds exactly three IDs; look each one up in the table
             returned by jointPositionVariables for the learner's solver and confirm the BlockPath values end
             with fl_hip_abduct, fl_hip_pitch and fl_knee in that order; never assume the IDs are j1, j2, j3"""),
        ],
        description="legIDs holds the variable IDs of the three front-left leg joints in order.",
        h2="""Display `T(1:3,:)` and check that the BlockPath values end in fl_hip_abduct, fl_hip_pitch and
        fl_knee, in that order. If they do not, find the right rows and use their numbers.""",
        h3="When it works, legIDs holds three IDs, such as j1.Rz.q, j2.Rz.q and j3.Rz.q.",
        reset=[
            'legJoints = mdl + "/" + ["fl_hip_abduct"; "fl_hip_pitch"; "fl_knee"];',
            "[~, rows] = ismember(legJoints, string(T.BlockPath));",
            "legIDs = string(T.ID(rows));",
            "clear legJoints rows",
        ],
    ),
    dict(
        title="Find the world frame and the paw frame", where="Simulink", lo=["lo03"],
        involves=["output_interpretation"],
        background="""Positions in a multibody model are measured with frames. A frame is a coordinate system
        attached to a part: an origin point and three axes named x, y and z. Think of a frame as a combination
        of a GPS and a compass. It tells you where a part is and which way it is facing.

        One frame never moves, and it is called the world frame. In this model it sits on the floor under the
        middle of the body, with x pointing forward, y pointing to the left of Sprocket and z pointing up.""",
        look="""in the block diagram, a frame is a port on a block, marked with a small letter. The world frame
        is port W of the block named World. The joint block fl_foot holds the paw on the leg, and one of its
        ports sits at the centre of the paw.""",
        why="""the next task tells the solver to measure the paw frame from the world frame, so you need to know
        where both frames are.""",
        task="""find the block named World and the joint block named fl_foot in the Sprocket block diagram, and
        read the letters on their ports.""",
        question="Which two letters mark the ports of the fl_foot block?",
        checks=[
            ("confirm", """The learner reports the two port letters on the fl_foot joint block, B and F. Accept F
             alone if the learner also found port W on the World block."""),
        ],
        description="The learner has found the world frame port and the paw frame port in the block diagram.",
        h2="""If you cannot find a block, zoom out with the mouse wheel until you see the whole diagram. The
        joint fl_foot sits next to the block named fl_paw.""",
        h3="""The joint fl_foot has two ports, B and F. B stands for base and F stands for follower. You will use
        port F, which sits at the centre of the paw.""",
        reset=[],
    ),
    dict(
        title="Measure the paw with addFrameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "configuration"],
        background="""The solver knows every joint angle, but it does not yet know which point on Sprocket you
        care about. You tell it by defining frame variables. A frame variable is a measurement of one frame,
        called the follower, from another frame, called the base.""",
        function="""addFrameVariables creates the measurement. Its inputs are the solver, a group name of your
        choice, the kind of measurement, the base frame and the follower frame. The kind translation gives three
        variables: the distances along x, y and z. You write each frame as a path: the model name, the block
        name and the port name, with slashes between them.""",
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
        title="List the measurements with frameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "output_interpretation"],
        background="""The solver now has three new variables, one for each axis of the world frame. Remember the
        directions: x points forward, y points to the left of Sprocket and z points up.""",
        function="""frameVariables returns a table of the frame variables of the solver. The ID column holds
        their IDs, and the Base and Follower columns show the two frames of each measurement. You should see
        Paw.Translation.x, Paw.Translation.y and Paw.Translation.z, in metres.""",
        why="the table confirms what you created, and it holds the IDs that you need next.",
        task="list the frame variables and store the table in a variable named F.",
        commands=["F = frameVariables(ks)"],
        question="If Sprocket lifts his paw straight up, which of those three numbers changes: x, y or z?",
        checks=[
            ("evaluate_matlab_code", """frameVariables for the learner's solver lists the three Paw translation
             variables; do not fail the task only because the table was not stored in F"""),
            ("confirm", """The learner says that z changes when the paw moves straight up. The reason is that the
             z axis of the world frame points up. If the learner picks x or y, explain that kindly and move
             on."""),
        ],
        description="The learner has listed the frame variables and knows which one measures height.",
        h2="""If the table is empty, the frame variables were not added. Go back one task, run the
        addFrameVariables command again, then list them once more.""",
        h3="""You should see three rows. The answer to the question is z, because the z axis of the world frame
        points up.""",
        reset=["F = frameVariables(ks);"],
    ),
    dict(
        title="Store the paw IDs in pawIDs", where="MATLAB", lo=["lo03"], involves=["command"],
        background="You stored the IDs of the leg angles in legIDs. The position of the paw needs the same treatment.",
        function="""this task needs no new function. F.ID is the ID column of the table F. It holds
        Paw.Translation.x, Paw.Translation.y and Paw.Translation.z.""",
        why="""from now on, legIDs stands for the joint angles of the leg and pawIDs stands for the position of
        the paw. Every kinematics problem in this mission connects those two lists.""",
        task="store the three paw IDs, in the order x, y, z, in a variable named pawIDs.",
        commands=["pawIDs = F.ID"],
        checks=[
            ("evaluate_matlab_code", """pawIDs exists and holds exactly the three Paw translation IDs of the
             learner's solver, in the order x, y, z; accept a string array, a cell array or a table column"""),
        ],
        description="pawIDs holds the IDs of the three paw translation variables in order.",
        h2="""If F holds more than three rows, keep only the three Paw rows. You can also build the IDs directly
        with `pawIDs = "Paw.Translation." + ["x";"y";"z"]`.""",
        h3="When it works, pawIDs holds Paw.Translation.x, Paw.Translation.y and Paw.Translation.z.",
        reset=['pawIDs = "Paw.Translation." + ["x"; "y"; "z"];'],
    ),
    dict(
        title="Make the leg angles the targets with addTargetVariables", where="MATLAB", lo=["lo04"],
        involves=["command"],
        background="""Time to wake Sprocket up. A kinematics problem has knowns and unknowns. Forward kinematics
        is the problem where you know the joint angles and you want the position of a part. It is the easy
        direction. Bend your own knee by a known amount, and there is exactly one place where your foot can be.
        The solver calls a known variable a target.""",
        function="""addTargetVariables marks variables as targets. Its inputs are the solver and a list of
        variable IDs. You supply the values of the targets later, when you solve.""",
        why="in the forward problem, the three leg angles are what you know.",
        task="make the three leg angles in legIDs the targets.",
        commands=["addTargetVariables(ks,legIDs);"],
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three
             front-left leg joint position variables"""),
        ],
        description="The three leg joint angles are assigned as target variables.",
        h2="""If MATLAB says that legIDs does not exist, go back and store the three leg IDs again. If it says
        that a variable already has a role, run `clearTargetVariables(ks);` and try again.""",
        h3="When it works, nothing is printed. Display `targetVariables(ks)` to see the three targets.",
        reset=["addTargetVariables(ks, legIDs);"],
    ),
    dict(
        title="Make the paw position the output with addOutputVariables", where="MATLAB", lo=["lo04"],
        involves=["command"],
        background="""The solver calls a variable that you want it to calculate an output. In the forward
        problem, the output is the position of the paw.""",
        function="""addOutputVariables marks variables as outputs. Its inputs are the solver and a list of
        variable IDs. The solver returns the values of the outputs when you solve.""",
        why="the solver only reports the variables that you ask for.",
        task="make the three paw variables in pawIDs the outputs.",
        commands=["addOutputVariables(ks,pawIDs);"],
        checks=[
            ("evaluate_matlab_code", """outputVariables for the learner's solver lists the three Paw translation
             variables, and targetVariables still lists the three front-left leg joint position variables"""),
        ],
        description="The paw translation variables are assigned as output variables.",
        h2="""If MATLAB says that pawIDs does not exist, create it with
        `pawIDs = "Paw.Translation." + ["x";"y";"z"];` and run the command again.""",
        h3="When it works, nothing is printed. Display `outputVariables(ks)` to see the three outputs.",
        reset=["addOutputVariables(ks, pawIDs);"],
    ),
    dict(
        title="Solve the forward problem with solve", where="MATLAB", lo=["lo04"],
        involves=["command", "output_interpretation"],
        background="""When every joint is at 0 degrees, Sprocket hangs straight, so each angle tells you how far
        a joint has turned from that pose. In his ready stance, the front-left leg has fl_hip_abduct at 0,
        fl_hip_pitch at 40 and fl_knee at -80 degrees. Before you solve, make a prediction. With the leg hanging
        straight, the paw is as low as it can go. Will bending the joints make the paw end up higher or lower?""",
        function="""solve runs the solver. Its inputs are the solver and the values of the targets, in the same
        order as the target list. It returns the values of the outputs, and then a status flag. A status of 1
        means that the solver met every target. A negative status means that it could not.""",
        why="this call answers the forward problem: where is the paw in the ready stance?",
        task="""solve for the ready stance, with the target values 0, 40 and -80, and store the paw position in
        a variable named pawStance.""",
        commands=["[pawStance,status] = solve(ks,[0 40 -80])"],
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
        description="pawStance holds the solved paw position for the ready stance.",
        h2="""The values that you give to solve must be in the same order as the targets. Display
        `targetVariables(ks)` to see that order. It should list hip abduction, hip pitch and knee, so the values
        are 0, 40 and -80.""",
        h3="""You should get a status of 1 and a paw position close to 0.22, 0.16 and 0.18 metres. The paw is
        about 0.10 metres higher than when it hangs.""",
        reset=["[pawStance, status] = solve(ks, [0 40 -80]);"],
    ),
    dict(
        title="See the ready stance with viewSolution", where="MATLAB", lo=["lo04"],
        involves=["command", "output_interpretation"],
        background="Numbers are hard to picture. The solver comes with a viewer that draws the model in the pose that it just found.",
        function="""viewSolution opens the Kinematics Solver Viewer, a 3D window that shows the pose from the last
        call to solve. Its only input is the solver.""",
        why="looking at the pose is the quickest way to catch a mistake. Use viewSolution after every solve from now on.",
        task="open the viewer and look at the front-left leg.",
        commands=VIEW,
        question="Look at the front-left leg in the viewer. Is the knee bent, or is the leg still straight?",
        checks=[
            ("confirm", """The learner says that the front-left leg is bent at the knee in the viewer. That
             matches the ready stance. If they say that the leg is straight, ask them to solve again and then
             open the viewer once more."""),
        ],
        description="The learner has seen the ready stance in the solution viewer.",
        h2="""If the viewer opens but the leg looks straight, the solve did not run. Go back one task, run the
        solve command again, then open the viewer once more.""",
        h3="""The viewer shows Sprocket with his front-left knee bent and the paw raised a little. The other
        three legs still hang straight.""",
        reset=[],
    ),
    dict(
        title="Clear the roles with clearTargetVariables and clearOutputVariables", where="MATLAB", lo=["lo05"],
        involves=["command"],
        background="""Now flip the question. A trainer has fixed a high-five pad to the stand. The mission setup
        stored the point that the paw has to reach in padPosition: three numbers, x, y and z in metres, measured
        in the world frame. This time you know where the paw should be, and you want the joint angles that put
        it there. That problem is called inverse kinematics. Every robot has to solve it before it can touch
        anything.""",
        function="""clearTargetVariables and clearOutputVariables remove the target and output roles from all
        variables. Each takes only the solver as input. The variables themselves stay.""",
        why="a variable can have only one of these two roles at a time, and you are about to give them the other way round.",
        task="remove the target and output roles from the solver.",
        commands=["clearTargetVariables(ks); clearOutputVariables(ks);"],
        checks=[
            ("evaluate_matlab_code", """targetVariables and outputVariables for the learner's solver are both
             empty; also accept the state of the next task, with the Paw translation variables as targets and the
             leg joints as outputs, because that state proves that the old roles were cleared"""),
        ],
        description="The roles from the forward problem have been cleared.",
        h2="""Both functions take only the solver as input. If MATLAB says that ks does not exist, the solver
        variable was cleared, and you need to create it again.""",
        h3="When it works, nothing is printed. Display `targetVariables(ks)` to check. It should show an empty table.",
        reset=["clearTargetVariables(ks);", "clearOutputVariables(ks);"],
    ),
    dict(
        title="Swap the roles with addTargetVariables and addOutputVariables", where="MATLAB", lo=["lo05"],
        involves=["command"],
        background="In the inverse problem, the position of the paw is what you know, and the leg angles are what you want.",
        function="""these are the two functions that you used for the forward problem. Only the lists change:
        pawIDs now goes to addTargetVariables, and legIDs goes to addOutputVariables.""",
        why="""the roles tell the solver which problem to solve. The same model and the same variables now
        describe the inverse problem.""",
        task="make the three paw variables the targets and the three leg angles the outputs.",
        commands=["addTargetVariables(ks,pawIDs);", "addOutputVariables(ks,legIDs);"],
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three Paw
             translation variables and outputVariables lists the three front-left leg joint position variables,
             so the roles from the forward problem have been cleared and swapped"""),
        ],
        description="The paw translation variables are targets and the leg joint angles are outputs.",
        h2="""If MATLAB says that a variable already has a role, the old roles are still in place. Run
        `clearTargetVariables(ks); clearOutputVariables(ks);` and then both commands again.""",
        h3="""When it works, nothing is printed. Display `targetVariables(ks)` to check. It should list the three
        Paw variables.""",
        reset=["addTargetVariables(ks, pawIDs);", "addOutputVariables(ks, legIDs);"],
    ),
    dict(
        title="Solve the inverse problem with solve", where="MATLAB", lo=["lo05"],
        involves=["command", "output_interpretation"],
        background="""Inverse kinematics is the hard direction. No formula gives the solver the angles directly,
        so it searches. It adjusts the angles a little at a time until the paw lands on the target.""",
        function="""solve works as before. The target values are now a position, so you give it padPosition. It
        returns the three leg angles in degrees, in the order of legIDs, and the status flag. A status of 1
        means that the paw reached the target. A negative status means that the search stopped before it got
        there.""",
        why="the result is the set of joint angles that the motors in the leg would have to reach for the high-five.",
        task="solve for the point in padPosition and store the joint angles in a variable named qFirst.",
        commands=["[qFirst,status] = solve(ks,padPosition)"],
        question="Which status flag did you get, and what does it tell you?",
        checks=[
            ("evaluate_matlab_code", """qFirst is a three-element numeric vector; two answers are both correct
             here, close to [17.82 -14.45 -103.08] or [17.82 -117.53 103.08] degrees (allow 0.1 degree and
             full-turn wraps); if the learner's solve started from the straight-leg pose and returned a negative
             status flag, do not fail the task as long as the roles are right, because a later task fixes
             convergence with initial guesses"""),
            ("confirm", """The learner reports the status flag that they got and what it means: 1 means the paw
             reached the pad, a negative value means the search stopped early. Accept either outcome. Both are
             fine here."""),
        ],
        description="qFirst holds the joint angles the solver returned for the pad position.",
        h2="""The target is now a position, so you pass the variable padPosition directly. Leave out the
        semicolon, so that both results are displayed.""",
        h3="""qFirst holds three angles in degrees. If the status is negative, do not worry. The search started
        from straight legs and lost its way, and a later task shows you how to guide it.""",
        reset=["[qFirst, status] = solve(ks, padPosition);"],
    ),
    dict(
        title="See where the paw ended with viewSolution", where="MATLAB", lo=["lo05"],
        involves=["command", "output_interpretation"],
        background="A status flag is only a number. Look at the pose before you trust it.",
        function="viewSolution shows the pose from the last solve, as before.",
        why="""the viewer shows whether the paw touches the pad. It also shows which way the knee bends, which
        matters in the next task.""",
        task="open the viewer again and look at the front-left knee.",
        commands=VIEW,
        question="In the viewer, is the knee tucked back behind the leg, or flipped forward above the body?",
        checks=[
            ("confirm", """The learner describes the knee in the viewer: tucked back or flipped forward. Accept
             either answer, because both poses reach the pad. If the solve returned a negative status, accept any
             description of what they see."""),
        ],
        description="The learner has looked at the first inverse kinematics result in the viewer.",
        h2="""If the viewer is already open, look for its window behind the MATLAB window, or run the
        viewSolution command again to bring it to the front.""",
        h3="""You will see one of two poses. Either the knee points backward, behind the leg, or it points
        forward and up, above the body. Tell me which one you see.""",
        reset=[],
    ),
    dict(
        title="Check the knee angle in qFirst against its limit", where="MATLAB", lo=["lo05", "lo06"],
        involves=["command", "output_interpretation"],
        background="""The paw can reach the pad in two ways: with the knee tucked back behind the leg, as in the
        ready stance, or with the knee flipped forward above the body. You can feel the same thing with your own
        arm. Put a fingertip on the table and move your elbow up and down. The fingertip stays where it is, yet
        your joint angles change.

        Real joints also have limits. The real knee can move only between -160 and +5 degrees.""",
        function="""this task needs no new function. The solver only does geometry, so it ignores joint limits,
        and no function checks them for you. qFirst holds the angles in the order hip abduction, hip pitch,
        knee.""",
        why="an answer that needs the knee to bend past its limit is useless on the real robot, and only you can spot it.",
        task="display qFirst and read the knee angle, which is the third number.",
        commands=["qFirst"],
        question="Is the knee angle in qFirst between -160 and +5 degrees?",
        checks=[
            ("evaluate_matlab_code", """read the third element of the current qFirst, so that you can judge the
             learner's answer: a value near -103 is inside the knee limit, and a value near +103 is outside it"""),
            ("confirm", """The learner says whether the knee angle in qFirst is inside the range -160 to +5
             degrees, and their answer matches the current value. Accept a correct reading either way."""),
        ],
        description="The learner has compared the knee angle of the first answer with the knee joint limit.",
        h2="""The knee angle is the last of the three numbers. Compare it with the two ends of the allowed
        range, -160 and +5.""",
        h3="""A knee angle near -103 is inside the limit, so that answer is real. A knee angle near +103 is far
        outside the limit, so the real robot cannot reach that pose.""",
        reset=[],
    ),
    dict(
        title="Give the search a starting pose with addInitialGuessVariables", where="MATLAB", lo=["lo06"],
        involves=["command"],
        background="""The solver starts its search from a pose and stops at the first answer that it finds.
        Which answer it finds depends on where it starts. An initial guess is a starting pose that you choose.""",
        function="""addInitialGuessVariables marks variables as initial guesses. Its inputs are the solver and a
        list of variable IDs. You supply the guess values when you solve. A variable can be an output and an
        initial guess at the same time.""",
        why="a search that starts near the answer that you want ends at that answer.",
        task="give the three leg angles in legIDs the initial guess role.",
        commands=["addInitialGuessVariables(ks,legIDs);"],
        checks=[
            ("evaluate_matlab_code", """initialGuessVariables for the learner's solver includes at least the
             front-left hip pitch and knee joint position variables"""),
        ],
        description="The leg joint angles are assigned as initial guess variables.",
        h2="""The command has the same shape as addTargetVariables: the solver first, then the list of IDs. You
        do not need to clear anything first.""",
        h3="When it works, nothing is printed. Display `initialGuessVariables(ks)` to see the three leg angles.",
        reset=["addInitialGuessVariables(ks, legIDs);"],
    ),
    dict(
        title="Solve again from the ready stance", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        background="The ready stance already has the knee bent backward, so it is a good place to start the search.",
        function="solve takes the guess values as a third input, in the same order as the initial guess list.",
        why="""starting from the ready stance leads the search to the answer with the knee tucked back, which is
        the one inside the joint limit.""",
        task="""solve for the point in padPosition again, with the guess 0, 40 and -80, and store the answer in a
        variable named qHighFive.""",
        commands=["[qHighFive,status] = solve(ks,padPosition,[0 40 -80])"],
        checks=[
            ("evaluate_matlab_code", """qHighFive is a three-element numeric vector within 0.1 degree of
             [17.82 -14.45 -103.08], in the order of the output table, so the knee angle is negative and inside
             the range -160 to +5 degrees"""),
        ],
        description="qHighFive holds the knee-back solution that respects the knee joint limit.",
        h2="""The guess values go in the third input of solve, in the same order as legIDs. If MATLAB reports
        that it expects no guess, run the addInitialGuessVariables command first.""",
        h3="""The answer should be close to 17.8, -14.5 and -103.1 degrees, with a status of 1. The knee angle is
        now inside its limit.""",
        reset=["[qHighFive, status] = solve(ks, padPosition, [0 40 -80]);"],
    ),
    dict(
        title="See the high-five pose with viewSolution", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        background="You now have an answer that the real joints can reach. Check it.",
        function="""viewSolution shows the pose from the last solve. The knee angle, the third number in
        qHighFive, should be close to -103 degrees.""",
        why="the viewer confirms that the paw is on the pad with the knee tucked back.",
        task="open the viewer again and look at the knee.",
        commands=VIEW,
        question="""Why can the same paw position have two different sets of joint angles? Use the fingertip and
        elbow example if it helps.""",
        checks=[
            ("confirm", """The learner explains in their own words that a two-segment leg can reach the same
             point with the knee bent either way, so the paw position alone does not fix the joint angles. Accept
             the elbow comparison as a full answer."""),
        ],
        description="The learner has seen the high-five pose and can explain why two answers exist.",
        h2="""Think about your arm again. Your fingertip can stay on one spot while your elbow moves. The paw is
        the fingertip, and the knee is the elbow.""",
        h3="""Two answers exist because a leg with two segments can reach the same point with the knee bent
        either way, just like your elbow. Tell me that in your own words.""",
        reset=[],
    ),
    dict(
        title="Space the path points with linspace", where="MATLAB", lo=["lo06"], involves=["command"],
        background="""A real robot cannot jump from one pose to another. It has to pass through every pose in
        between, so your last job is to plan the move. A path is many inverse kinematics problems in a row, one
        for each point between where the paw is and where it has to be.""",
        function="this task uses plain MATLAB. linspace makes the evenly spaced numbers, and the apostrophe turns the row into a column.",
        why="the column s says how far along the path each point is, from 0 at the start to 1 at the end.",
        task="make 25 evenly spaced numbers from 0 to 1 and store them as a column in a variable named s.",
        commands=["n = 25; s = linspace(0,1,n)';"],
        checks=[
            ("evaluate_matlab_code", """s is a numeric column vector with at least 15 elements that runs from 0 to
             1 in equal steps"""),
        ],
        description="s holds evenly spaced path positions from 0 to 1 as a column.",
        h2="Check that s is a column and not a row. The next task relies on it.",
        h3="When it works, nothing is printed. `size(s)` should be 25 rows and 1 column.",
        reset=["n = 25; s = linspace(0, 1, n)';"],
    ),
    dict(
        title="Blend the two paw positions into pawPath", where="MATLAB", lo=["lo06"], involves=["command"],
        background="""The paw starts at pawStance and has to end at padPosition. The points in between lie on the
        straight line that joins them.""",
        function="""this task uses plain MATLAB. Multiplying the column s by a row gives one row for each point.
        When s is 0 the row equals pawStance, and when s is 1 it equals padPosition.""",
        why="each row of pawPath becomes the target of one inverse kinematics problem.",
        task="store the points of the path in a matrix named pawPath, with one row for each point.",
        commands=["pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';"],
        checks=[
            ("evaluate_matlab_code", """pawPath is numeric with three columns and at least 15 rows; its first row
             equals pawStance and its last row equals padPosition within 1 mm"""),
        ],
        description="pawPath holds the straight-line path of the paw from the stance position to the pad.",
        h2="""If MATLAB says that pawStance does not exist, solve the forward problem again. If the sizes do not
        match, check that s is a column.""",
        h3="When it works, nothing is printed. `size(pawPath)` should be 25 rows and 3 columns.",
        reset=["pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';"],
    ),
    dict(
        title="Make room for the answers with zeros", where="MATLAB", lo=["lo06"], involves=["command"],
        background="Each point of the path gives three joint angles. The first search also needs a starting pose.",
        function="this task uses plain MATLAB. zeros makes the matrix for the answers, and guess holds the ready stance.",
        why="the loop in the next task fills qPath row by row and updates guess as it goes.",
        task="""make a matrix of zeros named qPath with one row for each point and three columns, and store the
        ready stance in a variable named guess.""",
        commands=["qPath = zeros(n,3); guess = [0 40 -80];"],
        checks=[
            ("evaluate_matlab_code", """qPath is numeric with three columns and as many rows as pawPath, and guess
             is a three-element numeric vector; accept a qPath that the loop of the next task has already
             filled"""),
        ],
        description="qPath is ready to hold the joint angles of every path point, and guess holds a starting pose.",
        h2="The n in zeros is the number of points that you chose two tasks ago.",
        h3="When it works, nothing is printed. `size(qPath)` should be 25 rows and 3 columns.",
        reset=["qPath = zeros(n, 3); guess = [0 40 -80];"],
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
        title="Draw the joint angles with plot", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        background="A figure shows at a glance whether the planned move is smooth.",
        function="this task uses plain MATLAB. plot draws one line for each column of qPath, and legend labels the lines.",
        why="a sudden jump in a line would mean that a joint flipped between two neighbouring points.",
        task="draw the three joint angles along the path in a figure with a legend.",
        commands=['plot(s,qPath); legend("abduct","pitch","knee")'],
        question="Look at the three lines in your figure. Are they smooth, or does any line jump suddenly?",
        checks=[
            ("evaluate_matlab_code", """inspect all open figures, not only gcf, and find one with a legend and at
             least three plotted lines whose values match the three columns of the current qPath"""),
            ("confirm", """The learner says that the three lines are smooth, with no sudden jump. Then share the
             takeaway: a jump would mean that the knee flipped between two neighbouring points, and starting each
             search from the previous answer is what prevents it."""),
        ],
        description="A figure shows the three joint angles along the path, with a legend.",
        h2="""The names in legend are in the same order as the columns of qPath: hip abduction, hip pitch,
        knee.""",
        h3="""A figure window opens with three lines. They should be smooth, and the knee line should stay below
        zero from start to end.""",
        reset=['figure; plot(s, qPath); legend("abduct", "pitch", "knee");'],
    ),
    dict(
        title="See the high-five with viewSolution", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        background="The last solve in the loop was the last point of the path, which is the pad.",
        function="viewSolution shows the pose from the last solve, so it now shows the end of the path.",
        why="this is the moment that the whole mission was for.",
        task="open the viewer one last time.",
        commands=VIEW,
        question="What is Sprocket doing in the viewer?",
        checks=[
            ("confirm", """The learner says that the front-left paw is on the pad, so Sprocket is giving a
             high-five. Congratulate them. Close with a short summary of what they did: import, solver, frame
             variables, forward kinematics, inverse kinematics, initial guess, path."""),
        ],
        description="The learner has seen Sprocket give a high-five at the end of the planned path.",
        h2="""If the paw is not on the pad, the loop did not finish. Go back two tasks, run the loop again, then
        open the viewer once more.""",
        h3="""The viewer shows Sprocket with his front-left paw pressed against the round pad. He is giving you a
        high-five.""",
        reset=[],
    ),
]

HEADER = '''mission_id: "01"
version: "%(version)s"
title: Teach a Robot Dog to High-Five with KinematicsSolver
thumbnail: thumbnail.png
objective: >
  Sprocket is a robot dog, powered down on a maintenance stand, and your job
  is to teach him to give a high-five. A machine like Sprocket is a set of
  rigid parts connected by joints, and each joint angle is a single number.
  The Simscape Multibody KinematicsSolver works out how those joint angles and
  the position of his paw depend on each other. Forward kinematics asks where
  the paw ends up for joint angles that you choose. Inverse kinematics asks
  which joint angles put the paw on a point that you choose. By the end you
  will have imported Sprocket from his Computer-Aided Design (CAD) files,
  solved both problems, and picked the answer that his real joints can reach.
  This mission assumes that you know MATLAB: variables, tables, indexing,
  loops and plotting. It assumes no knowledge of Simscape Multibody, robotics
  or CAD, so you are never expected to know one of their functions in advance.
  How you will work: Ada gives you one small task at a time, %(count)d in all.
  Every task gives the background, the function that you need, why you need
  it, and your task. You do the task in MATLAB or in Simulink, then you tell
  Ada, and she checks your work and gives you the next task. Ask Ada for a
  hint whenever you want the function explained again with the exact command.
  The guide Sprocket_guide.md, open in the MATLAB Editor, holds every task.
  Before you begin, think about your own leg. When you bend your knee, does
  your foot move up or down?
supported_matlab_releases: [R2024b, R2025a, R2025b, R2026a, R2026b]
required_capabilities: [MATLAB, Simulink, Simscape, Simscape Multibody, MATLAB MCP, Simulink Agentic Toolkit]
write_mode: read_inspect
capability_mode: guided_tutor
teaching_mode: guided_walkthrough

app:
  summary: Import a robot dog from CAD and solve forward and inverse kinematics to make it give a high-five.
  audience: MATLAB users with no Simscape Multibody, robotics or CAD background.
  difficulty: beginner
  estimated_minutes: 75
  products: [MATLAB, Simulink, Simscape, Simscape Multibody]
  topics: [kinematics, KinematicsSolver, forward kinematics, inverse kinematics, URDF import, initial guesses]
  status: draft
  learner_visible: true
  tile_order: 10

learning_outcomes:
  - id: lo01
    description: Import a URDF CAD assembly into a Simscape Multibody model and identify its joints.
  - id: lo02
    description: Create a KinematicsSolver object and match its joint variable IDs to the joints of the model.
  - id: lo03
    description: Define frame variables that measure the position of a point of interest relative to the world frame.
  - id: lo04
    description: Pose and solve a forward kinematics problem by assigning target and output variables.
  - id: lo05
    description: Pose and solve an inverse kinematics problem and read its status flag.
  - id: lo06
    description: Use initial guesses to choose between multiple solutions, check a solution against joint limits, and solve a smooth path.

setup:
  script: "setup_sprocket_high_five.m"
  description: >
    Finds the Sprocket CAD files that ship in the task_reset folder and writes
    Sprocket.urdf into the learner workspace with full paths to the part
    geometry, so the import works from any current folder. Leaves two
    variables in the MATLAB workspace: urdfFile, the full path of that URDF
    file, and padPosition, the 1-by-3 point in metres (world frame) that the
    paw centre must reach. It also copies the guide Sprocket_guide.md into the
    learner workspace, opens it in the MATLAB Editor, and leaves its full path
    in the variable guideFile. No model is created and no solver exists yet.
    Construction variables are cleared. Run via run_matlab_file at session
    start.

runtime_validation:
  setup:
    assertions:
      - type: workspace_var
        name: padPosition
        class: double
      - type: workspace_var
        name: urdfFile
        class: string
      - type: matlab_expression
        description: The staged URDF file exists
        code: "isfile(urdfFile)"
      - type: matlab_expression
        description: The guide was copied into the workspace
        code: "isfile(guideFile)"
      - type: workspace_absent
        name: cadFolder
  resets:
    - task: t03
      assertions:
        - type: model_loaded
          name: Sprocket
        - type: block_exists
          path: Sprocket/fl_knee
        - type: block_exists
          path: Sprocket/World
    - task: t06
      assertions:
        - type: workspace_var
          name: ks
          class: simscape.multibody.KinematicsSolver
    - task: t08
      assertions:
        - type: matlab_expression
          description: Three leg joint IDs are stored
          code: "numel(legIDs) == 3"
    - task: t10
      assertions:
        - type: matlab_expression
          description: Three Paw frame variables exist
          code: "height(frameVariables(ks)) == 3"
    - task: t12
      assertions:
        - type: matlab_expression
          description: Three paw IDs are stored
          code: "numel(pawIDs) == 3"
    - task: t15
      assertions:
        - type: matlab_expression
          description: Forward kinematics is posed with three targets and three outputs
          code: "height(targetVariables(ks)) == 3 && height(outputVariables(ks)) == 3"
        - type: matlab_expression
          description: The stance paw position matches the reference
          code: "norm(reshape(pawStance, 1, []) - [0.22 0.16 0.1829]) < 1e-3"
    - task: t19
      assertions:
        - type: matlab_expression
          description: Inverse kinematics has been solved once
          code: "numel(qFirst) == 3 && all(isfinite(qFirst))"
    - task: t23
      assertions:
        - type: matlab_expression
          description: Initial guess variables are assigned
          code: "height(initialGuessVariables(ks)) >= 2"
        - type: matlab_expression
          description: The high-five pose is on the knee-back branch
          code: "abs(qHighFive(3) + 103.08) < 0.1"
    - task: t28
      assertions:
        - type: matlab_expression
          description: The path has one row of joint angles for each point
          code: "isequal(size(qPath), [25 3]) && all(qPath(:, 3) < 0)"

discovery:
  model_name:
    tool: evaluate_matlab_code
    code: "bdroot"
    note: >
      The learner imports the model and may give it any name. The default is
      Sprocket. Use bdroot or find_system('type','block_diagram') to discover
      it, or read the ModelName property of the learner's KinematicsSolver
      object once it exists. Use the discovered name in every block path.

# Notes for the tutor (Ada):
#
# Who the learner is. The learner knows MATLAB: variables, tables, indexing,
# loops and plotting. The learner does not know Simscape Multibody, robotics
# or CAD. Do not explain basic MATLAB. Do explain every Simscape Multibody
# function, every Simulink action and every mechanical term.
#
# Teaching style. The line teaching_mode: guided_walkthrough above marks this
# mission as a guided walkthrough.
# - Every task is one action, and every instruction has the same four parts
#   in the same order: Background, The function (or What to look for), Why,
#   and Your task. When you present a task, give all four, in that order. Do
#   not reduce them to the task alone, and never assume that the learner
#   knows which function to use or where to click.
# - Task 1 tells the learner how to work. Make sure that the routine is
#   clear before you move on: one task at a time, tell Ada when it is done,
#   ask for a hint to have the function explained again with the exact
#   command, and the guide holds every task.
# - The first hint of every task repeats the function, the reason and the
#   exact command. Give it as soon as the learner asks, hesitates or reports
#   an error. If the learner says that they are new, treat that as a standing
#   request for the first hint of every task.
# - The setup script opens a guide named Sprocket_guide.md in the learner's
#   MATLAB Editor. It is a Markdown file with one section for each task,
#   under the headings Task 1 to Task %(count)d, with the same four parts and
#   the same command. Point the learner to the heading of the current task.
#   The guide is the learner's own copy, in the workspace folder.
# - The learner may do several tasks from the guide before talking to you.
#   When you check a task, also look whether the next tasks are already
#   done, and move the learner forward without asking them to redo anything.
# - Keep each check quick. The tasks are small on purpose, and a learner who
#   waits a long time after every command loses the thread.
# - In MATLAB means the Command Window. In Simulink means the window that
#   shows the Sprocket block diagram.
# - After every solve the learner looks at Sprocket with viewSolution. If
#   they skip it, remind them, because seeing the pose is the point.
# - Ask fair questions only. A fair question has one idea, and the learner
#   can answer it from what this mission has already shown them or from
#   everyday experience. Ask one question at a time. If the learner
#   hesitates, offer two or three choices. For the opening prediction, use
#   the question at the end of the objective, about bending a knee. Do not
#   ask what the solver will do.
# - When an answer is not right, never just say that it is wrong. Explain in
#   one or two supportive sentences why the right answer is right, then
#   invite the learner to try again or to move on.
# - A question about what a word means is not a hint request. Answer it in
#   full, in everyday language, at any time. Introduce a new term in four
#   moves: name it, define it, relate it to something familiar, then show
#   where it appears in Sprocket's model. Useful definitions:
#     part (also body or link). One rigid piece that does not bend.
#     joint. The place where two parts meet and can move. A revolute joint
#       is a hinge with one angle. A weld joint allows no motion.
#     degrees of freedom (DOF). The number of independent ways to move. A
#       leg with three hinges has three.
#     pose. The full list of joint angles at one moment.
#     frame. A coordinate system attached to a part, an origin and x, y, z.
#     world frame. The frame that never moves. Here it sits on the floor
#       under the middle of Sprocket's body, x forward, y to his left, z up.
#     kinematics. The geometry of motion, with no forces or motors.
#     forward kinematics. Joint angles in, position out. One answer.
#     inverse kinematics. Position in, joint angles out. The solver finds it
#       by search, and there can be more than one answer.
#     target, output, initial guess. The three roles of a solver variable.
#       A value you supply, a value you want, and where the search starts.
#     status flag. How the search went. 1 means every target was met.
# - When a task is complete, congratulate the learner in a few words, give a
#   one-sentence takeaway in their terms, and link it to the next task.
# - Write to the learner as "you", in active voice, and use no jargon that
#   this mission has not explained.
#
# Checking the work.
# - Every check below can be answered with evaluate_matlab_code. Find the
#   learner's solver by class (simscape.multibody.KinematicsSolver), not by
#   variable name, and inspect it with jointPositionVariables,
#   frameVariables, targetVariables, outputVariables and
#   initialGuessVariables. These calls only read the solver.
# - Reference answers come from an independent calculation on the same URDF.
#   Lengths are in metres, angles in degrees. Treat them as sanity anchors
#   and judge the learner's formulation first.
# - The solver ignores joint limits. That is the point of the knee tasks, so
#   do not reveal it before the learner reaches them.
# - Calling solve yourself changes which pose viewSolution shows. If you call
#   it to verify, say so, or re-run the learner's last solve afterwards.

tasks:
'''

GUIDE_HEADER = '''# Sprocket guide: teach a robot dog to high-five

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
'''


def one_line(text):
    return " ".join(text.split())


def paragraphs(text):
    return [one_line(p) for p in text.split("\n\n") if p.strip()]


def protect(text):
    """Keep commands in backticks and number lists in brackets on one line."""
    return re.sub(r"`[^`]*`|\[[^\]\[]*\]", lambda found: found.group(0).replace(" ", "\x00"), one_line(text))


def wrap(text, indent, width=79):
    pad = " " * indent
    filled = textwrap.fill(protect(text), width=width, initial_indent=pad, subsequent_indent=pad,
                           break_long_words=False, break_on_hyphens=False)
    return filled.replace("\x00", " ")


def folded(paras, indent):
    return "\n\n".join(wrap(p, indent) for p in paras)


def shown(commands):
    return " and then ".join(f"`{c}`" for c in commands)


def second_part(t):
    """The label and the text of the part that explains the function or what to look for."""
    if t["where"] == "MATLAB":
        return "The function", one_line(t["function"])
    return "What to look for", one_line(t["look"])


def task_sentence(t, capital=True):
    start = "Type" if capital else "type"
    if t["where"] == "MATLAB":
        return f"{one_line(t['task'])} {start} {shown(t['commands'])} in the Command Window and press Enter."
    return one_line(t["task"])


def instruction_paragraphs(n, t):
    label, text = second_part(t)
    first, *rest = paragraphs(t["background"])
    paras = [f"Background: {first}", *rest,
             f"{label}: {text}",
             f"Why: {one_line(t['why'])}",
             f"Your task, in {t['where']}: {task_sentence(t)}",
             f"The guide that is open in the MATLAB Editor shows this task under the heading Task {n}."]
    if t.get("question"):
        paras.append(f"Then answer this: {one_line(t['question'])}")
    return paras


def first_hint(t):
    label, text = second_part(t)
    return f"{label}: {text} Why: {one_line(t['why'])} Your task, in {t['where']}: {task_sentence(t)}"


def task_yaml(n, t):
    out = [f'  - id: "t{n:02d}"',
           f"    title: {t['title']}" if ":" not in t["title"] else f'    title: "{t["title"]}"',
           f"    involves: [{', '.join(t['involves'])}]",
           f"    outcome_refs: [{', '.join(t['lo'])}]",
           "    instruction: >",
           folded(instruction_paragraphs(n, t), 6),
           "    completion:",
           "      strategy:"]
    for kind, text in t["checks"]:
        out.append("        - kind: learner_confirmation" if kind == "confirm" else f"        - tool: {kind}")
        out.append("          check: >")
        out.append(wrap(text, 12))
    out.append("      description: >")
    out.append(wrap(t["description"], 8))
    out.append("    hints:")
    for hint in (first_hint(t), t["h2"], t["h3"]):
        out.append("      - >")
        out.append(wrap(hint, 8))
    return "\n".join(out)


def md(text, width=78):
    """One Markdown paragraph, wrapped so that it also reads well as plain text."""
    lines = textwrap.wrap(protect(text), width=width, break_long_words=False, break_on_hyphens=False)
    # A wrapped line must not start with something Markdown reads as a list, a quote or a heading.
    lines = [re.sub(r"^(\d+)\. ", r"\1\\. ", line) for line in lines]
    lines = [re.sub(r"^([-+*>#]) ", r"\\\1 ", line) for line in lines]
    return "\n".join(lines).replace("\x00", " ")


def guide_section(n, t):
    label, text = second_part(t)
    first, *rest = paragraphs(t["background"])
    out = [f"## Task {n}. {t['title']}", md(f"**Background:** {first}")]
    out += [md(p) for p in rest]
    out.append(md(f"**{label}:** {text}"))
    out.append(md(f"**Why:** {t['why']}"))
    out.append(md(f"**Your task, in {t['where']}:** {t['task']}"))
    if t["where"] == "MATLAB":
        out.append("```matlab\n" + "\n".join(t["commands"]) + "\n```")
    if t.get("question"):
        out.append(md(f"**Then tell Ada:** {t['question']}"))
    return "\n\n".join(out)


def reset_script(n, tasks):
    """State at the start of task n: everything that tasks 1 to n-1 produce."""
    prev = tasks[n - 2]
    lines = [f"% Ready for Task {n:02d}: the state after Task {n - 1:02d} ({prev['title']})."]
    if n > 2:
        lines += [f'run("reset_t{n - 1:02d}.m");', ""]
    lines += prev["reset"] or [f"% Task {n - 1:02d} changes nothing in MATLAB."]
    return "\n".join(lines) + "\n"


def main():
    count = len(TASKS)
    header = HEADER % dict(version=VERSION, count=count)
    body = "\n\n".join(task_yaml(i, t) for i, t in enumerate(TASKS, 1))
    (MISSION / "mission.yaml").write_text(header + body + "\n", encoding="utf-8")

    guide = GUIDE_HEADER + "\n" + "\n\n".join(guide_section(i, t) for i, t in enumerate(TASKS, 1)) + "\n"
    (RESET / "Sprocket_guide.m").unlink(missing_ok=True)     # the guide was a MATLAB script before version 2.1.0
    (RESET / GUIDE_NAME).write_text(guide, encoding="utf-8")

    for old in RESET.glob("reset_t*.m"):
        old.unlink()
    for n in range(2, count + 1):
        (RESET / f"reset_t{n:02d}.m").write_text(reset_script(n, TASKS), encoding="utf-8")

    in_simulink = sum(t["where"] == "Simulink" for t in TASKS)
    print(f"mission.yaml: version {VERSION}, {count} tasks ({count - in_simulink} in MATLAB, {in_simulink} in Simulink)")
    print(f"{GUIDE_NAME}: {count} sections")
    print(f"reset scripts: reset_t02.m to reset_t{count:02d}.m")


if __name__ == "__main__":
    main()
