#!/usr/bin/env python3
"""Build the Sprocket mission from one list of tasks.

One task is one action. The stock tutor shows only the title and the goal of a
task, so every title names the function to use and every task asks for a
single thing. This script writes three files that must always agree:

  marketplace/missions/sprocket-high-five/mission.yaml
  .../task_reset_sprocket-high-five/Sprocket_guide.m      (opened by setup)
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

VERSION = "2.0.0"

FRAME_CMD = 'addFrameVariables(ks,"Paw","translation","Sprocket/World/W","Sprocket/fl_foot/F");'
LOOP_CMD = "for k = 1:n, qk = solve(ks,pawPath(k,:),guess); qPath(k,:) = qk(:)'; guess = qk(:)'; end"

# where: "MATLAB" tasks have commands; "Simulink" tasks have an action done with the mouse.
# checks: ("tool name", text) or ("confirm", text). reset: MATLAB lines that reproduce the task.
TASKS = [
    dict(
        title="Import Sprocket with smimport", where="MATLAB", lo=["lo01"], involves=["command"],
        story="""Meet Sprocket. He is a robot dog, powered down on a maintenance stand with his legs hanging
        straight. His design was made in a Computer-Aided Design (CAD) program. It was saved in the Unified Robot
        Description Format (URDF), a plain text file that lists every part and every joint. MATLAB cannot work
        with him until that file becomes a model.

        You will work in two places in this mission. The MATLAB Command Window is where you type commands after
        the >> prompt. Simulink is the window that shows a model as a diagram of blocks.""",
        action="import the file with the smimport function. The variable urdfFile already holds the location of the file.",
        commands=["smimport(urdfFile)"],
        what="""smimport is the import function of Simscape Multibody. It reads a robot description file and
        builds a model from it, with one block for each part and one block for each joint.""",
        why="""MATLAB can only reason about Sprocket once he exists as a model. After a few seconds, a Simulink
        window named Sprocket opens.""",
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
        h2="""If MATLAB says that urdfFile is not recognized, tell me and I will run the mission setup again.
        Type urdfFile with no quotes, because it is the name of a variable and not a piece of text.""",
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
        story="""The diagram is correct, but it does not look like a dog yet. Simulink can assemble the parts and
        show them in a 3D view called Mechanics Explorer.""",
        action="""click an empty area of the Sprocket window, then press Ctrl+D (Cmd+D on a Mac). You can also
        open the Modeling tab and select Update Model.""",
        see="""Simulink assembles all the parts and opens Mechanics Explorer. Drag with the mouse to look around
        Sprocket.""",
        why="seeing the robot makes every later task easier to picture.",
        question="What colour are his paws?",
        checks=[
            ("confirm", """The learner says that they can see Sprocket in 3D in Mechanics Explorer and names the
             colour of the paws. The paws are amber, so accept orange, gold or yellow as well. If the learner
             reports grey, the colours did not load, which is fine. Accept that too."""),
        ],
        description="The learner has updated the model and seen Sprocket in Mechanics Explorer.",
        h2="""If nothing happens, click once on an empty white area of the Sprocket block diagram first, so that
        the window is selected, and press Ctrl+D again. If an error message appears, read it to me.""",
        h3="""Mechanics Explorer is a separate window. It shows a white robot dog on a dark stand, with a round
        pad in front of him. The paws are the balls at the ends of his legs.""",
        reset=[],
    ),
    dict(
        title="Find the front-left leg joints", where="Simulink", lo=["lo01"], involves=["output_interpretation"],
        story="""Engineers describe a machine like Sprocket as rigid parts connected by joints. A joint is the
        place where two parts meet and can move, like a door hinge or your knee. One number describes each hinge:
        its angle. In the block diagram, every part is a block, and every joint is a block that sits between two
        parts.""",
        action="""go back to the Sprocket block diagram and find the blocks whose names start with fl_. The
        letters fl stand for front-left.""",
        see="""four of those blocks are joints. Their names are fl_hip_abduct, fl_hip_pitch, fl_knee and
        fl_foot.""",
        why="these are the joints that you will control for the rest of the mission.",
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
        story="""Sprocket is in MATLAB now, but he is only a drawing. To ask questions about his geometry you
        need a KinematicsSolver. Think of it as a geometry calculator. It takes a snapshot of the model and works
        out how the joint angles and the positions of the parts relate, without running a simulation.""",
        action="create a solver for the model named Sprocket and store it in a variable named ks.",
        commands=['ks = simscape.multibody.KinematicsSolver("Sprocket");'],
        what="""KinematicsSolver creates the geometry calculator for the model whose name is in quotes. The
        prefix simscape.multibody is the name of the package, a kind of folder, where MATLAB keeps this function.
        The semicolon at the end stops MATLAB from printing the result, so nothing visible happens.""",
        why="every later command needs ks.",
        checks=[
            ("evaluate_matlab_code", """the base workspace holds a simscape.multibody.KinematicsSolver object
             whose ModelName is a currently loaded model; find it by class with whos and do not require a
             particular variable name"""),
        ],
        description="A KinematicsSolver object exists for the imported model.",
        h2="""If MATLAB reports an error, check that the Sprocket window is still open and that the name in
        quotes matches its title. If you renamed the model, use your own name in place of Sprocket.""",
        h3="""When it works, MATLAB shows a new prompt and nothing else. Type `ks` with no semicolon if you want
        to see a summary of the solver.""",
        reset=["ks = simscape.multibody.KinematicsSolver(mdl);"],
    ),
    dict(
        title="List the joint angles with jointPositionVariables", where="MATLAB", lo=["lo02"],
        involves=["command", "output_interpretation"],
        story="""The solver keeps its own list of every joint angle. However, it does not use the joint names.
        It gives each angle a short ID of its own, such as j5.Rz.q, which reads as joint 5, rotation about the z
        axis of that joint, position.""",
        action="ask the solver for its table of joint angles and store the table in a variable named T.",
        commands=["T = jointPositionVariables(ks)"],
        what="""jointPositionVariables returns a table with one row for each joint angle. The ID column is the
        name that the solver uses for the angle. The BlockPath column tells you which joint block in the Simulink
        model the angle belongs to. The Unit column gives the unit. Leave out the semicolon, so that MATLAB
        prints the table.""",
        why="you need to know which IDs belong to the front-left leg.",
        question="Look at the Unit column of the table. Which unit does the solver use for joint angles?",
        checks=[
            ("evaluate_matlab_code", """a KinematicsSolver object exists; if the base workspace also holds a
             table with ID, BlockPath and Unit columns, that shows the learner listed the joint position
             variables, but do not fail the task only because the table was not stored"""),
            ("confirm", "The learner states that joint position variables are in degrees by default."),
        ],
        description="The learner has listed the joint position variables and read their unit.",
        h2="""If MATLAB says that ks does not exist, go back one task and create the solver again. If the table
        does not print, check that you left out the semicolon at the end.""",
        h3="""The table has 13 rows, one for each joint that can move. The first three belong to the front-left
        leg. The Unit column shows deg, which means degrees.""",
        reset=["T = jointPositionVariables(ks);"],
    ),
    dict(
        title="Store the leg IDs in legIDs", where="MATLAB", lo=["lo02"], involves=["command"],
        story="""Three rows of the table belong to the front-left leg: the rows whose BlockPath ends in
        fl_hip_abduct, fl_hip_pitch and fl_knee. They are normally the first three rows. Typing those IDs every
        time would be slow, so you store them once.""",
        action="store the IDs of those three rows, in that order, in a variable named legIDs.",
        commands=["legIDs = T.ID(1:3)"],
        what="""T.ID takes the ID column of the table, and the numbers in parentheses keep rows 1 to 3. If the
        three joints are on other rows, use those row numbers instead, for example `legIDs = T.ID([4 5 6])`.""",
        why="legIDs is now your shortcut for the three leg angles, in the order hip abduction, hip pitch, knee.",
        checks=[
            ("evaluate_matlab_code", """legIDs exists and holds exactly three IDs; look each one up in the table
             returned by jointPositionVariables for the learner's solver and confirm the BlockPath values end
             with fl_hip_abduct, fl_hip_pitch and fl_knee in that order; never assume the IDs are j1, j2, j3"""),
        ],
        description="legIDs holds the variable IDs of the three front-left leg joints in order.",
        h2="""Type `T(1:3,:)` to print only the first three rows. Check that their BlockPath values end in
        fl_hip_abduct, fl_hip_pitch and fl_knee, in that order. If they do not, find the right rows and use
        their numbers.""",
        h3="""When it works, legIDs holds three IDs, such as j1.Rz.q, j2.Rz.q and j3.Rz.q. Type `legIDs` to see
        them.""",
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
        story="""The solver knows every joint angle now. However, it does not know which point on Sprocket you
        care about. Positions are measured with frames. A frame is a small coordinate system attached to a part:
        an origin point and three axes named x, y and z. Think of a frame as a combination of a GPS and a
        compass. It tells you where a part is and which way it is facing.

        One frame never moves, and it is called the world frame. It sits on the floor under the middle of the
        body, with x pointing forward, y pointing to the left of Sprocket and z pointing up.""",
        action="""in the Sprocket block diagram, find the block named World and the joint block named fl_foot.
        Look at the small letters on those blocks.""",
        see="""each letter marks a port, and each port is a frame. The world frame is port W of the World block.
        The joint fl_foot holds the paw on, and one of its ports sits at the centre of the paw.""",
        why="the next task measures the paw frame from the world frame, so you need to know where both are.",
        question="Which two letters mark the ports of the fl_foot block?",
        checks=[
            ("confirm", """The learner reports the two port letters on the fl_foot joint block, B and F. Accept F
             alone if the learner also found port W on the World block."""),
        ],
        description="The learner has found the world frame port and the paw frame port in the block diagram.",
        h2="""If you cannot find a block, zoom out with the mouse wheel until you see the whole diagram. The
        World block is on one side of the diagram, and fl_foot sits next to the block named fl_paw.""",
        h3="""The joint fl_foot has two ports, B and F. B stands for base and F stands for follower. You will use
        port F, which sits at the centre of the paw.""",
        reset=[],
    ),
    dict(
        title="Measure the paw with addFrameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "configuration"],
        story="""To track the paw, you ask the solver to measure the frame of the paw from the world frame. That
        measurement is called a frame variable. You write a frame as the model name, the block name and the port
        name, with slashes between them. The world frame is Sprocket/World/W, and the paw frame is
        Sprocket/fl_foot/F.""",
        action="add frame variables that measure the translation of the paw frame from the world frame. Use the group name Paw.",
        commands=[FRAME_CMD],
        what="""addFrameVariables tells the solver to measure one frame from another. Its five inputs are the
        solver, a group name of your choice, the kind of measurement, the frame to measure from and the frame to
        measure to. The word translation means the distances along x, y and z.""",
        why="the solver can now report where the paw is.",
        checks=[
            ("evaluate_matlab_code", """frameVariables for the learner's solver lists three translation variables
             (x, y, z, in metres) whose Base is the W port of the World block and whose Follower is a frame at
             the paw centre: the F or B port of the fl_foot joint, or an equivalent frame port on the fl_paw
             subsystem; accept any valid group name; do not accept a follower on another leg or on the knee
             joint"""),
        ],
        description="The solver has three translation frame variables that locate the front-left paw from the world frame.",
        h2="""If MATLAB reports an error, the usual cause is a missing quote or a path that does not match. Every
        input except ks is text in double quotes. If you renamed your model, replace Sprocket at the start of
        both paths with your model name.""",
        h3="When it works, MATLAB prints nothing. The next task shows you what was created.",
        reset=['addFrameVariables(ks, "Paw", "translation", mdl + "/World/W", mdl + "/fl_foot/F");'],
    ),
    dict(
        title="List the measurements with frameVariables", where="MATLAB", lo=["lo03"],
        involves=["command", "output_interpretation"],
        story="""The solver now has three new variables, one for each direction of the world frame. Remember the
        directions: x points forward, y points to the left of Sprocket and z points up.""",
        action="list the frame variables and store the table in a variable named F.",
        commands=["F = frameVariables(ks)"],
        what="""frameVariables returns a table of the measurements that the solver knows. You should see three
        rows: Paw.Translation.x, Paw.Translation.y and Paw.Translation.z, in metres.""",
        why="you will use these three IDs in the next task.",
        question="If Sprocket lifts his paw straight up, which of those three numbers changes: x, y or z?",
        checks=[
            ("evaluate_matlab_code", """frameVariables for the learner's solver lists the three Paw translation
             variables; do not fail the task only because the table was not stored in F"""),
            ("confirm", """The learner says that z changes when the paw moves straight up. The reason is that the
             z axis of the world frame points up. If the learner picks x or y, explain that kindly and move
             on."""),
        ],
        description="The learner has listed the frame variables and knows which one measures height.",
        h2="""If the table is empty, the frame variables were not added. Go back one task and run the
        addFrameVariables command again, then list them once more.""",
        h3="""You should see three rows. The answer to the question is z, because the z axis of the world frame
        points up.""",
        reset=["F = frameVariables(ks);"],
    ),
    dict(
        title="Store the paw IDs in pawIDs", where="MATLAB", lo=["lo03"], involves=["command"],
        story="You stored the leg IDs in legIDs. Now do the same for the three paw IDs.",
        action="store the three paw IDs, in the order x, y, z, in a variable named pawIDs.",
        commands=["pawIDs = F.ID"],
        what="""F.ID takes the ID column of the table F. It holds Paw.Translation.x, Paw.Translation.y and
        Paw.Translation.z.""",
        why="pawIDs is now your shortcut for the position of the paw.",
        checks=[
            ("evaluate_matlab_code", """pawIDs exists and holds exactly the three Paw translation IDs of the
             learner's solver, in the order x, y, z; accept a string array, a cell array or a table column"""),
        ],
        description="pawIDs holds the IDs of the three paw translation variables in order.",
        h2="""If F holds more than three rows, keep only the three Paw rows. You can also build the IDs directly:
        type `pawIDs = "Paw.Translation." + ["x";"y";"z"]`.""",
        h3="""When it works, pawIDs holds Paw.Translation.x, Paw.Translation.y and Paw.Translation.z. Type
        `pawIDs` to see them.""",
        reset=['pawIDs = "Paw.Translation." + ["x"; "y"; "z"];'],
    ),
    dict(
        title="Make the leg angles the targets with addTargetVariables", where="MATLAB", lo=["lo04"],
        involves=["command"],
        story="""Time to wake him up. When every joint is at 0 degrees, Sprocket hangs straight, so each angle
        tells you how far a joint has turned from that pose. Working out where the paw ends up for joint angles
        that you already know is called forward kinematics. It is the easy direction. Bend your own knee by a
        known amount, and there is exactly one place where your foot can be.

        The solver needs you to give every variable a role. A target is a variable whose value you supply.""",
        action="make the three leg angles the targets.",
        commands=["addTargetVariables(ks,legIDs);"],
        what="addTargetVariables marks variables as targets. Here the targets are the three leg angles in legIDs.",
        why="in a forward problem you know the angles.",
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three
             front-left leg joint position variables"""),
        ],
        description="The three leg joint angles are assigned as target variables.",
        h2="""If MATLAB says that legIDs does not exist, go back and store the three leg IDs again. If it says
        that a variable already has a role, type `clearTargetVariables(ks);` and try again.""",
        h3="When it works, MATLAB prints nothing. Type `targetVariables(ks)` to see the three targets.",
        reset=["addTargetVariables(ks, legIDs);"],
    ),
    dict(
        title="Make the paw position the output with addOutputVariables", where="MATLAB", lo=["lo04"],
        involves=["command"],
        story="""An output is a variable that the solver calculates for you. In a forward problem, the output is
        the position of the paw.""",
        action="make the three paw variables the outputs.",
        commands=["addOutputVariables(ks,pawIDs);"],
        what="addOutputVariables marks variables as outputs. Here the outputs are the three paw variables in pawIDs.",
        why="the solver now knows what you want it to work out.",
        checks=[
            ("evaluate_matlab_code", """outputVariables for the learner's solver lists the three Paw translation
             variables, and targetVariables still lists the three front-left leg joint position variables"""),
        ],
        description="The paw translation variables are assigned as output variables.",
        h2="""If MATLAB says that pawIDs does not exist, type `pawIDs = "Paw.Translation." + ["x";"y";"z"];`
        first, then run the command again.""",
        h3="When it works, MATLAB prints nothing. Type `outputVariables(ks)` to see the three outputs.",
        reset=["addOutputVariables(ks, pawIDs);"],
    ),
    dict(
        title="Solve the forward problem with solve", where="MATLAB", lo=["lo04"],
        involves=["command", "output_interpretation"],
        story="""In his ready stance, the front-left leg has fl_hip_abduct at 0, fl_hip_pitch at 40 and fl_knee
        at -80 degrees. Before you solve, make a prediction. With the leg hanging straight, the paw is as low as
        it can go. Will bending the joints make the paw end up higher or lower? Make your guess before you solve.""",
        action="solve for the ready stance and store the paw position in a variable named pawStance.",
        commands=["[pawStance,status] = solve(ks,[0 40 -80])"],
        what="""solve runs the calculation. The numbers in square brackets are the target values, in the same
        order as legIDs: 0 for hip abduction, 40 for hip pitch and -80 for the knee. Two results come back. The
        first, pawStance, holds the x, y and z of the paw in metres. The second, status, is 1 when the solver met
        every target.""",
        why="this is the answer to the forward problem.",
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
        h2="""The numbers that you give to solve must be in the same order as the targets. Type
        `targetVariables(ks)` to see that order. It should list hip abduction, hip pitch and knee, so the values
        are 0, 40 and -80.""",
        h3="""You should get a status of 1 and a paw position close to 0.22, 0.16 and 0.18 metres. The paw is
        about 0.10 metres higher than when it hangs.""",
        reset=["[pawStance, status] = solve(ks, [0 40 -80]);"],
    ),
    dict(
        title="See the ready stance with viewSolution", where="MATLAB", lo=["lo04"],
        involves=["command", "output_interpretation"],
        story="Numbers are hard to picture. The solver has a viewer that shows Sprocket in the pose that it just found.",
        action="open the solution viewer.",
        commands=["viewSolution(ks)"],
        what="viewSolution opens a 3D viewer that shows the pose from the last solve. Use it after every solve from now on.",
        why="you can check the pose with your own eyes.",
        question="Look at the front-left leg in the viewer. Is the knee bent, or is the leg still straight?",
        checks=[
            ("confirm", """The learner says that the front-left leg is bent at the knee in the viewer. That
             matches the ready stance. If they say that the leg is straight, ask them to solve again and then
             open the viewer once more."""),
        ],
        description="The learner has seen the ready stance in the solution viewer.",
        h2="""If the viewer opens but the leg looks straight, the solve did not run. Go back one task, run the
        solve command again, then type the viewSolution command once more.""",
        h3="""The viewer shows Sprocket with his front-left knee bent and the paw raised a little. The other
        three legs still hang straight.""",
        reset=[],
    ),
    dict(
        title="Clear the roles with clearTargetVariables and clearOutputVariables", where="MATLAB", lo=["lo05"],
        involves=["command"],
        story="""Now flip the question. A trainer has fixed a high-five pad to the stand. The point that the paw
        has to reach is stored in padPosition: three numbers, x, y and z in metres, measured in the world frame.
        This time you know where the paw should be, and you want the joint angles that put it there. That is
        inverse kinematics. Every robot has to answer this question before it can touch anything.

        A variable can have only one role at a time, so first you remove the roles from the forward problem.""",
        action="remove the target and output roles from the solver.",
        commands=["clearTargetVariables(ks); clearOutputVariables(ks);"],
        what="these two functions remove the roles that you assigned. The variables themselves stay.",
        why="you are about to swap the roles.",
        checks=[
            ("evaluate_matlab_code", """targetVariables and outputVariables for the learner's solver are both
             empty; also accept the state of the next task, with the Paw translation variables as targets and the
             leg joints as outputs, because that state proves that the old roles were cleared"""),
        ],
        description="The roles from the forward problem have been cleared.",
        h2="""Both functions take only the solver as input. If MATLAB says that ks does not exist, the solver
        variable was cleared, and you need to create it again.""",
        h3="""When it works, MATLAB prints nothing. Type `targetVariables(ks)` to check. It should show an empty
        table.""",
        reset=["clearTargetVariables(ks);", "clearOutputVariables(ks);"],
    ),
    dict(
        title="Swap the roles with addTargetVariables and addOutputVariables", where="MATLAB", lo=["lo05"],
        involves=["command"],
        story="In the inverse problem, the paw position is what you know, and the leg angles are what you want.",
        action="make the three paw variables the targets and the three leg angles the outputs.",
        commands=["addTargetVariables(ks,pawIDs);", "addOutputVariables(ks,legIDs);"],
        what="these are the same two functions as before, with the lists swapped.",
        why="the solver now knows that you will give it a position and that it must work out the angles.",
        checks=[
            ("evaluate_matlab_code", """targetVariables for the learner's solver lists exactly the three Paw
             translation variables and outputVariables lists the three front-left leg joint position variables,
             so the roles from the forward problem have been cleared and swapped"""),
        ],
        description="The paw translation variables are targets and the leg joint angles are outputs.",
        h2="""If MATLAB says that a variable already has a role, the old roles are still in place. Type
        `clearTargetVariables(ks); clearOutputVariables(ks);` and then run both commands again.""",
        h3="""When it works, MATLAB prints nothing. Type `targetVariables(ks)` to check. It should list the three
        Paw variables.""",
        reset=["addTargetVariables(ks, pawIDs);", "addOutputVariables(ks, legIDs);"],
    ),
    dict(
        title="Solve the inverse problem with solve", where="MATLAB", lo=["lo05"],
        involves=["command", "output_interpretation"],
        story="""Inverse kinematics is the hard direction, because the solver cannot calculate the angles
        directly. Instead, it searches. It adjusts the angles a little at a time until the paw lands on the
        target. A number called the status flag tells you how the search went.""",
        action="solve for the point in padPosition and store the joint angles in a variable named qFirst.",
        commands=["[qFirst,status] = solve(ks,padPosition)"],
        what="""solve searches for joint angles that put the paw on the point stored in padPosition. The result
        qFirst holds three angles in degrees, in the order of legIDs: hip abduction, hip pitch and knee.""",
        why="these are the angles that the motors in the leg would have to reach.",
        question="""Which status flag did you get? A status of 1 means that the paw reached the pad. A negative
        status means that the search stopped before it got there.""",
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
        h2="""The target is now a position, so you give solve the variable padPosition and no square brackets.
        Leave out the semicolon, so that MATLAB prints both results.""",
        h3="""qFirst holds three angles in degrees. If the status is negative, do not worry. The search started
        from straight legs and lost its way, and a later task shows you how to guide it.""",
        reset=["[qFirst, status] = solve(ks, padPosition);"],
    ),
    dict(
        title="See where the paw ended with viewSolution", where="MATLAB", lo=["lo05"],
        involves=["command", "output_interpretation"],
        story="Look at the result before you trust it.",
        action="open the solution viewer again.",
        commands=["viewSolution(ks)"],
        what="the viewer shows the pose where the search ended.",
        why="you can see whether the paw touches the pad, and which way the knee bends.",
        question="In the viewer, is the knee tucked back behind the leg, or flipped forward above the body?",
        checks=[
            ("confirm", """The learner describes the knee in the viewer: tucked back or flipped forward. Accept
             either answer, because both poses reach the pad. If the solve returned a negative status, accept any
             description of what they see."""),
        ],
        description="The learner has looked at the first inverse kinematics result in the viewer.",
        h2="""If the viewer is already open, look for its window behind the MATLAB window, or type the
        viewSolution command again to bring it to the front.""",
        h3="""You will see one of two poses. Either the knee points backward, behind the leg, or it points
        forward and up, above the body. Tell me which one you see.""",
        reset=[],
    ),
    dict(
        title="Check the knee angle in qFirst against its limit", where="MATLAB", lo=["lo05", "lo06"],
        involves=["command", "output_interpretation"],
        story="""The paw can reach the pad in two ways: with the knee tucked back behind the leg, as in the ready
        stance, or with the knee flipped forward above the body. You can feel the same thing with your own arm.
        Put a fingertip on the table and move your elbow up and down. The fingertip stays where it is, yet your
        joint angles change.

        The solver only does geometry, so it ignores joint limits. However, the real knee can move only between
        -160 and +5 degrees.""",
        action="print qFirst and read the knee angle, which is the third number.",
        commands=["qFirst"],
        what="typing the name of a variable prints its value.",
        why="the solver does not check joint limits, so you have to.",
        question="Is the knee angle in qFirst between -160 and +5 degrees?",
        checks=[
            ("evaluate_matlab_code", """read the third element of the current qFirst, so that you can judge the
             learner's answer: a value near -103 is inside the knee limit, and a value near +103 is outside it"""),
            ("confirm", """The learner says whether the knee angle in qFirst is inside the range -160 to +5
             degrees, and their answer matches the current value. Accept a correct reading either way."""),
        ],
        description="The learner has compared the knee angle of the first answer with the knee joint limit.",
        h2="""qFirst holds three numbers in the order hip abduction, hip pitch, knee. The knee angle is the last
        one. Compare it with the two ends of the allowed range, -160 and +5.""",
        h3="""A knee angle near -103 is inside the limit, so that answer is real. A knee angle near +103 is far
        outside the limit, so the real robot cannot reach that pose.""",
        reset=[],
    ),
    dict(
        title="Give the search a starting pose with addInitialGuessVariables", where="MATLAB", lo=["lo06"],
        involves=["command"],
        story="""The solver starts its search from a pose and stops at the first answer that it finds. An initial
        guess is a starting pose that you choose, so that the search ends at the answer that you want.""",
        action="give the three leg angles the initial guess role.",
        commands=["addInitialGuessVariables(ks,legIDs);"],
        what="""addInitialGuessVariables gives variables a third role, initial guess, which is the pose where the
        search starts.""",
        why="a search that starts near the answer that you want ends at that answer.",
        checks=[
            ("evaluate_matlab_code", """initialGuessVariables for the learner's solver includes at least the
             front-left hip pitch and knee joint position variables"""),
        ],
        description="The leg joint angles are assigned as initial guess variables.",
        h2="""The command has the same shape as addTargetVariables: the solver first, then the list of IDs. A
        variable can be an output and an initial guess at the same time, so you do not need to clear anything.""",
        h3="When it works, MATLAB prints nothing. Type `initialGuessVariables(ks)` to see the three leg angles.",
        reset=["addInitialGuessVariables(ks, legIDs);"],
    ),
    dict(
        title="Solve again from the ready stance", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        story="The ready stance already has the knee bent the right way, so it makes a good starting pose.",
        action="""solve for the point in padPosition again, starting from the ready stance, and store the answer
        in a variable named qHighFive.""",
        commands=["[qHighFive,status] = solve(ks,padPosition,[0 40 -80])"],
        what="solve now has a third input, the guess. The values 0, 40 and -80 are the ready stance.",
        why="starting from the ready stance leads the search to the answer with the knee tucked back.",
        checks=[
            ("evaluate_matlab_code", """qHighFive is a three-element numeric vector within 0.1 degree of
             [17.82 -14.45 -103.08], in the order of the output table, so the knee angle is negative and inside
             the range -160 to +5 degrees"""),
        ],
        description="qHighFive holds the knee-back solution that respects the knee joint limit.",
        h2="""The guess values go in the third input of solve, in square brackets, in the same order as legIDs.
        If MATLAB reports that it expects no guess, run the addInitialGuessVariables command first.""",
        h3="""The answer should be close to 17.8, -14.5 and -103.1 degrees, with a status of 1. The knee angle is
        now inside its limit.""",
        reset=["[qHighFive, status] = solve(ks, padPosition, [0 40 -80]);"],
    ),
    dict(
        title="See the high-five pose with viewSolution", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        story="Check the pose that the real joints can reach.",
        action="open the solution viewer again.",
        commands=["viewSolution(ks)"],
        what="the viewer shows the new pose, with the paw on the pad and the knee tucked back.",
        why="you can confirm that this answer looks like a move that a real dog could make.",
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
        story="""A real robot cannot jump from one pose to another. It has to pass through every pose in between,
        so your last job is to plan the move. A path is simply many inverse kinematics problems in a row, one for
        each point between where the paw is and where it needs to be.""",
        action="make 25 evenly spaced numbers from 0 to 1 and store them as a column in a variable named s.",
        commands=["n = 25; s = linspace(0,1,n)';"],
        what="""n is the number of points. The function linspace makes n evenly spaced numbers from 0 to 1, and
        the apostrophe turns that row into a column.""",
        why="s says how far along the path each point is, from 0 at the start to 1 at the end.",
        checks=[
            ("evaluate_matlab_code", """s is a numeric column vector with at least 15 elements that runs from 0 to
             1 in equal steps"""),
        ],
        description="s holds evenly spaced path positions from 0 to 1 as a column.",
        h2="""Do not forget the apostrophe after the closing parenthesis. Without it, s is a row, and the next
        task needs a column.""",
        h3="When it works, MATLAB prints nothing. Type `size(s)` to check. It should show 25 rows and 1 column.",
        reset=["n = 25; s = linspace(0, 1, n)';"],
    ),
    dict(
        title="Blend the two paw positions into pawPath", where="MATLAB", lo=["lo06"], involves=["command"],
        story="""The paw starts at pawStance and has to end at padPosition. The points in between lie on the
        straight line that joins them.""",
        action="store the points of the path in a matrix named pawPath, with one row for each point.",
        commands=["pawPath = (1-s).*pawStance(:)' + s.*padPosition(:)';"],
        what="""this blends the two positions. When s is 0 you get pawStance, and when s is 1 you get
        padPosition. In between, you get points on the line that joins them.""",
        why="these are the places where the paw has to be, one after the other.",
        checks=[
            ("evaluate_matlab_code", """pawPath is numeric with three columns and at least 15 rows; its first row
             equals pawStance and its last row equals padPosition within 1 mm"""),
        ],
        description="pawPath holds the straight-line path of the paw from the stance position to the pad.",
        h2="""Type the command exactly, with the dots before the stars. The dot makes MATLAB multiply each row
        by its own number. If MATLAB says that pawStance does not exist, solve the forward problem again.""",
        h3="""When it works, MATLAB prints nothing. Type `size(pawPath)` to check. It should show 25 rows and 3
        columns.""",
        reset=["pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';"],
    ),
    dict(
        title="Make room for the answers with zeros", where="MATLAB", lo=["lo06"], involves=["command"],
        story="""Each point of the path will give three joint angles. You need a place to keep them, and a
        starting pose for the first search.""",
        action="""make a matrix of zeros named qPath with one row for each point and three columns, and store
        the ready stance in a variable named guess.""",
        commands=["qPath = zeros(n,3); guess = [0 40 -80];"],
        what="""zeros makes a grid of zeros with n rows and 3 columns. The variable guess holds the ready stance
        as the first starting pose.""",
        why="the loop in the next task fills qPath row by row.",
        checks=[
            ("evaluate_matlab_code", """qPath is numeric with three columns and as many rows as pawPath, and guess
             is a three-element numeric vector; accept a qPath that the loop of the next task has already
             filled"""),
        ],
        description="qPath is ready to hold the joint angles of every path point, and guess holds a starting pose.",
        h2="""Both commands fit on one line, separated by a semicolon. The n in zeros is the number of points
        that you chose two tasks ago.""",
        h3="When it works, MATLAB prints nothing. Type `size(qPath)` to check. It should show 25 rows and 3 columns.",
        reset=["qPath = zeros(n, 3); guess = [0 40 -80];"],
    ),
    dict(
        title="Solve every point with a for loop", where="MATLAB", lo=["lo06"], involves=["command", "file_edit"],
        story="""If each search starts from the previous answer, neighbouring answers stay close together, and
        the knee never flips.""",
        action="""solve the inverse kinematics at every point of pawPath, and use each answer as the guess for
        the next point.""",
        commands=[LOOP_CMD],
        what="""a for loop repeats its commands, here once for each point. Each pass solves one point, stores the
        three angles as row k of qPath, and keeps them as the guess for the next point. Type the whole loop on
        one line.""",
        why="starting each search from the previous answer keeps the motion smooth.",
        checks=[
            ("evaluate_matlab_code", """qPath is numeric with three columns and at least 15 rows; its first row is
             within 0.5 degree of [0 40 -80] and its last row within 0.5 degree of [17.82 -14.45 -103.08]; the
             knee column is negative and inside -160 to +5 on every row; no joint jumps by more than about 20
             degrees between consecutive rows"""),
        ],
        description="qPath holds a smooth joint-angle path from the ready stance to the high-five pose.",
        h2="""Type the loop on one line, ending with the word end. If MATLAB reports an error inside the loop,
        check that the roles are still in place: the paw translation as targets, and the leg angles as outputs
        and as initial guesses.""",
        h3="""When it works, MATLAB prints nothing. Type `qPath(end,:)` to see the last row. It should be close
        to 17.8, -14.5 and -103.1 degrees.""",
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
        story="A figure shows at a glance whether the move is smooth.",
        action="draw the three joint angles along the path in a figure with a legend.",
        commands=['plot(s,qPath); legend("abduct","pitch","knee")'],
        what="plot draws one line for each column of qPath, and legend labels the three lines.",
        why="the figure shows how each joint angle changes along the move.",
        question="Look at the three lines in your figure. Are they smooth, or does any line jump suddenly?",
        checks=[
            ("evaluate_matlab_code", """inspect all open figures, not only gcf, and find one with a legend and at
             least three plotted lines whose values match the three columns of the current qPath"""),
            ("confirm", """The learner says that the three lines are smooth, with no sudden jump. Then share the
             takeaway: a jump would mean that the knee flipped between two neighbouring points, and starting each
             search from the previous answer is what prevents it."""),
        ],
        description="A figure shows the three joint angles along the path, with a legend.",
        h2="""The first input of plot is s, the position along the path, and the second is qPath. The names in
        legend are in the same order as the columns of qPath: hip abduction, hip pitch, knee.""",
        h3="""A figure window opens with three lines. They should be smooth, and the knee line should stay below
        zero from start to end.""",
        reset=['figure; plot(s, qPath); legend("abduct", "pitch", "knee");'],
    ),
    dict(
        title="See the high-five with viewSolution", where="MATLAB", lo=["lo06"],
        involves=["command", "output_interpretation"],
        story="The last solve in the loop was the last point of the path, which is the pad.",
        action="open the solution viewer one last time.",
        commands=["viewSolution(ks)"],
        what="the viewer shows the last pose of the path.",
        why="this is the moment that the whole mission was for.",
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
  is to teach him to give a high-five. You do not need any robotics
  background. A machine like Sprocket is a set of rigid parts connected by
  joints, and each joint angle is a single number. The Simscape Multibody
  KinematicsSolver works out how those joint angles and the position of his
  paw depend on each other. Forward kinematics asks where the paw ends up for
  joint angles that you choose. Inverse kinematics asks which joint angles put
  the paw on a point that you choose. By the end you will have imported
  Sprocket from his Computer-Aided Design (CAD) files, solved both problems,
  and picked the answer that his real joints can reach. This mission assumes
  only that you can type commands at the MATLAB prompt. You are never expected
  to know a command in advance. The mission has %(count)d small tasks, and each
  task is one action. When the mission starts, a guide named Sprocket_guide
  opens in the MATLAB Editor. It lists every task: whether to work in MATLAB
  or in Simulink, the exact command, what the command does and why you need
  it. You can also ask Ada for a hint at any time, and the first hint of every
  task is the exact command. Before you begin, think about your own leg. When
  you bend your knee, does your foot move up or down?
supported_matlab_releases: [R2024b, R2025a, R2025b, R2026a, R2026b]
required_capabilities: [MATLAB, Simulink, Simscape, Simscape Multibody, MATLAB MCP, Simulink Agentic Toolkit]
write_mode: read_inspect
capability_mode: guided_tutor
teaching_mode: guided_walkthrough

app:
  summary: Import a robot dog from CAD and solve forward and inverse kinematics to make it give a high-five.
  audience: Anyone who can type MATLAB commands. No robotics, CAD or Simscape Multibody background is needed.
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
    paw centre must reach. It also copies the guide Sprocket_guide.m into the
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
    - task: t02
      assertions:
        - type: model_loaded
          name: Sprocket
        - type: block_exists
          path: Sprocket/fl_knee
        - type: block_exists
          path: Sprocket/World
    - task: t05
      assertions:
        - type: workspace_var
          name: ks
          class: simscape.multibody.KinematicsSolver
    - task: t07
      assertions:
        - type: matlab_expression
          description: Three leg joint IDs are stored
          code: "numel(legIDs) == 3"
    - task: t09
      assertions:
        - type: matlab_expression
          description: Three Paw frame variables exist
          code: "height(frameVariables(ks)) == 3"
    - task: t11
      assertions:
        - type: matlab_expression
          description: Three paw IDs are stored
          code: "numel(pawIDs) == 3"
    - task: t14
      assertions:
        - type: matlab_expression
          description: Forward kinematics is posed with three targets and three outputs
          code: "height(targetVariables(ks)) == 3 && height(outputVariables(ks)) == 3"
        - type: matlab_expression
          description: The stance paw position matches the reference
          code: "norm(reshape(pawStance, 1, []) - [0.22 0.16 0.1829]) < 1e-3"
    - task: t18
      assertions:
        - type: matlab_expression
          description: Inverse kinematics has been solved once
          code: "numel(qFirst) == 3 && all(isfinite(qFirst))"
    - task: t22
      assertions:
        - type: matlab_expression
          description: Initial guess variables are assigned
          code: "height(initialGuessVariables(ks)) >= 2"
        - type: matlab_expression
          description: The high-five pose is on the knee-back branch
          code: "abs(qHighFive(3) + 103.08) < 0.1"
    - task: t27
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
# Teaching style. The author wrote this mission for learners who start from
# zero. The line teaching_mode: guided_walkthrough above marks that choice.
# - Every task is one action. The title names the function to use. Say the
#   action plainly when you present a task, and never assume that the learner
#   knows which function to use or where to click.
# - The first hint of every task is the exact command or action, with what it
#   does and why. Give it as soon as the learner asks, hesitates or reports
#   an error. If the learner says that they are new, treat that as a standing
#   request for the first hint of every task.
# - The setup script opens a guide named Sprocket_guide.m in the learner's
#   MATLAB Editor. It has one section for each task, under the headings
#   TASK 1 to TASK %(count)d, with the same command. Point the learner to the
#   heading of the current task. The guide is the learner's own copy.
# - The learner may run several tasks from the guide before talking to you.
#   When you check a task, also look whether the next tasks are already
#   done, and move the learner forward without asking them to redo anything.
# - Keep each check quick. The tasks are small on purpose, and a learner who
#   waits a long time after every command loses the thread.
# - In MATLAB means the Command Window, after the >> prompt. In Simulink
#   means the window that shows the Sprocket block diagram. If the learner
#   cannot find one of them, help with that first.
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

GUIDE_HEADER = '''%%%% Sprocket guide: teach a robot dog to high-five
%% This guide lists every task of the mission. Each task is one action. Ada,
%% your tutor, checks each task and answers your questions. You do the
%% actions.
%%
%% How to use this guide
%% * Work through one task at a time, from top to bottom.
%% * A task that says "In MATLAB" has a command. Type it in the Command
%%   Window, after the >> prompt, and press Enter. You can also click inside
%%   the task in this file and press Ctrl+Enter (Cmd+Enter on a Mac) to run
%%   only that task.
%% * A task that says "In Simulink" is something that you do with the mouse
%%   in the window that shows the Sprocket block diagram.
%% * Every task says what it does and why you need it.
%% * When you finish a task, tell Ada. Ask her about anything that is not
%%   clear. No question is too basic.
%%
%% Do not press the Run button for the whole file. The next two lines stop
%% the file if you do.
disp("Use this guide one task at a time. Read the first lines of the file.")
return
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


def type_sentence(commands):
    shown = " and then ".join(f"`{c}`" for c in commands)
    return f"Type {shown} in the Command Window and press Enter."


def instruction_paragraphs(n, t):
    paras = paragraphs(t["story"])
    if t["where"] == "MATLAB":
        paras.append(f"Your one action, in MATLAB: {one_line(t['action'])} {type_sentence(t['commands'])}")
        paras.append(f"What it does: {one_line(t['what'])}")
    else:
        paras.append(f"Your one action, in Simulink: {one_line(t['action'])}")
        paras.append(f"What you see: {one_line(t['see'])}")
    paras.append(f"Why: {one_line(t['why'])}")
    paras.append(f"The guide that is open in the MATLAB Editor shows this task under the heading TASK {n}.")
    if t.get("question"):
        paras.append(f"Then answer this: {one_line(t['question'])}")
    return paras


def first_hint(t):
    if t["where"] == "MATLAB":
        shown = " and then ".join(f"`{c}`" for c in t["commands"])
        return (f"In MATLAB, type {shown} in the Command Window and press Enter. "
                f"What it does: {one_line(t['what'])} Why: {one_line(t['why'])}")
    return (f"In Simulink, {one_line(t['action'])} What you see: {one_line(t['see'])} "
            f"Why: {one_line(t['why'])}")


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


def comment(text, width=76):
    return "\n".join("% " + line.replace("\x00", " ")
                     for line in textwrap.wrap(protect(text), width=width - 2,
                                               break_long_words=False, break_on_hyphens=False))


def guide_section(n, t):
    out = [f"%% TASK {n}. {t['title']}"]
    for i, p in enumerate(paragraphs(t["story"])):
        if i:
            out.append("%")
        out.append(comment(p))
    out.append("%")
    if t["where"] == "MATLAB":
        out.append(comment(f"Your one action, in MATLAB: {t['action']}"))
        out.append(comment(f"What it does: {t['what']}"))
        out.append(comment(f"Why: {t['why']}"))
        out.extend(t["commands"])
    else:
        out.append(comment(f"Your one action, in Simulink: {t['action']}"))
        out.append(comment(f"What you see: {t['see']}"))
        out.append(comment(f"Why: {t['why']}"))
    if t.get("question"):
        if t["where"] == "MATLAB":
            out.append("")
        else:
            out.append("%")
        out.append(comment(f"Then tell Ada: {t['question']}"))
    return "\n".join(out)


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

    guide = GUIDE_HEADER % () + "\n" + "\n\n".join(guide_section(i, t) for i, t in enumerate(TASKS, 1)) + "\n"
    (RESET / "Sprocket_guide.m").write_text(guide, encoding="utf-8")

    for old in RESET.glob("reset_t*.m"):
        old.unlink()
    for n in range(2, count + 1):
        (RESET / f"reset_t{n:02d}.m").write_text(reset_script(n, TASKS), encoding="utf-8")

    in_simulink = sum(t["where"] == "Simulink" for t in TASKS)
    print(f"mission.yaml: version {VERSION}, {count} tasks ({count - in_simulink} in MATLAB, {in_simulink} in Simulink)")
    print(f"Sprocket_guide.m: {count} sections")
    print(f"reset scripts: reset_t02.m to reset_t{count:02d}.m")


if __name__ == "__main__":
    main()
