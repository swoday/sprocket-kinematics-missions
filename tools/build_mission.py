#!/usr/bin/env python3
"""Build the Sprocket mission from one list of tasks.

The learner knows MATLAB but not Simscape Multibody, robotics or CAD. One task
is one idea (one to three commands, or one thing to do with the mouse), and
every task gives the same four things in the same order:

  Background     the story and the idea, in plain words
  The function   what the function is, what goes in and what comes out
                 (for a task done with the mouse: what to look for)
  Why            the reason for this action
  Your task      what to do, with the exact command

The stock tutor shows only the title and the goal of a task, so every title
names what to type, and the first hint repeats the function, the reason and
the exact command. This script writes three things that must always agree:

  marketplace/missions/sprocket-high-five/mission.yaml
  .../task_reset_sprocket-high-five/sprocket_worksheet.m  (a plain text live script: the
                                                           instructions and an empty code area
                                                           per task; setup copies it to the
                                                           learner as sprocket_high_five.m)
  .../task_reset_sprocket-high-five/reset_tNN.m           (one per task after the first)

Edit the task list in tools/mission_tasks.py, then run:  python3 tools/build_mission.py
Check the result with:                                  python3 tools/validate_mission.py
"""
import re
import textwrap
from pathlib import Path

from mission_tasks import TASKS

PROJECT = Path(__file__).resolve().parent.parent
MISSION = PROJECT / "marketplace" / "missions" / "sprocket-high-five"
RESET = MISSION / "task_reset_sprocket-high-five"

VERSION = "3.2.1"
WORKSHEET_NAME = "sprocket_worksheet.m"     # the plain text live script that ships in the reset folder
LEARNER_SCRIPT = "sprocket_high_five.m"     # the name of the learner's copy in the workspace folder

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
  How you will work: you work in a live script named sprocket_high_five.m,
  which opens when the mission starts. Ada gives you one task at a time,
  %(count)d in all, and tells you what to do and why. The section of that task
  in the live script gives the background, explains the function that you
  need, and has a place for your code. You type your code there, run the
  section, and tell Ada. She checks your work and gives you the next task.
  Ask Ada for a hint whenever you want the function explained again with the
  exact commands. The exact commands of every task are also in the Solutions
  section at the bottom of the live script. Before you begin, think
  about your own leg. When you bend your knee, does your foot move up or
  down?
supported_matlab_releases: [R2026a, R2026b]
required_capabilities: [MATLAB, Simulink, Simscape, Simscape Multibody, MATLAB MCP, Simulink Agentic Toolkit]
write_mode: read_inspect
capability_mode: guided_tutor
teaching_mode: guided_walkthrough

app:
  summary: Import a robot dog from CAD and solve forward and inverse kinematics to make it give a high-five.
  audience: MATLAB users with no Simscape Multibody, robotics or CAD background.
  difficulty: beginner
  estimated_minutes: 60
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
    paw centre must reach. It also copies the live script sprocket_high_five.m
    into the learner workspace, opens it in the Live Editor, and leaves its
    full path in the variable scriptFile. The live script holds the
    instructions and an empty code area for every task. No model is created
    and no solver exists yet.
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
        description: The live script was copied into the workspace
        code: "isfile(scriptFile)"
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
    - task: t04
      assertions:
        - type: workspace_var
          name: ks
          class: simscape.multibody.KinematicsSolver
    - task: t05
      assertions:
        - type: matlab_expression
          description: Three leg joint IDs are stored
          code: "numel(legIDs) == 3"
    - task: t06
      assertions:
        - type: matlab_expression
          description: Three Paw frame variables exist
          code: "height(frameVariables(ks)) == 3"
    - task: t07
      assertions:
        - type: matlab_expression
          description: Three paw IDs are stored
          code: "numel(pawIDs) == 3"
    - task: t09
      assertions:
        - type: matlab_expression
          description: Forward kinematics is posed with three targets and three outputs
          code: "height(targetVariables(ks)) == 3 && height(outputVariables(ks)) == 3"
        - type: matlab_expression
          description: The stance paw position matches the reference
          code: "norm(reshape(pawStance, 1, []) - [0.22 0.16 0.1829]) < 1e-3"
    - task: t11
      assertions:
        - type: matlab_expression
          description: Inverse kinematics has been solved once
          code: "numel(qFirst) == 3 && all(isfinite(qFirst))"
    - task: t12
      assertions:
        - type: matlab_expression
          description: Initial guess variables are assigned
          code: "height(initialGuessVariables(ks)) >= 2"
        - type: matlab_expression
          description: The high-five pose is on the knee-back branch
          code: "abs(qHighFive(3) + 103.08) < 0.1"
    - task: t14
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
# - You give the task. The instruction of every task is the task
#   description: what to do, then why, in words. It contains no commands on
#   purpose, so there is nothing in it to hold back. Present it in full and
#   keep every name and value that it contains, in code formatting. Then ask
#   its question, if it has one.
# - The live script teaches. The setup script opens a live script named
#   sprocket_high_five.m in the learner's Live Editor. It has one section for
#   each task, under the headings Task 1 to Task %(count)d. Each section has
#   Background, The function with its general syntax, Why, and an empty code
#   area where the learner types. Point the learner to the heading of the
#   current task, and never assume that they know which function to use or
#   where to click.
# - In your opening, tell the learner how to work: you give one task at a
#   time, they read the section of that task in the live script, type their
#   code there, run the section, and tell you.
# - The first hint of every task repeats the function, the reason, the task
#   and the exact commands. Give it as soon as the learner asks, hesitates or
#   reports an error. If the learner says that they are new, treat that as a
#   standing request for the first hint of every task.
# - The exact commands of every task are also in the Solutions section at
#   the very bottom of the live script. Encourage the learner to try first.
#   Offer the first hint before you send them to the Solutions.
# - The live script is the learner's own file, in the workspace folder. It
#   is saved as plain text, so you can read the learner's code in it when
#   they ask for help. Do not edit it.
# - The learner may do several tasks in the live script before talking to you.
#   When you check a task, also look whether the next tasks are already
#   done, and move the learner forward without asking them to redo anything.
# - Keep each check quick. The tasks are small on purpose, and a learner who
#   waits a long time after every command loses the thread.
# - In MATLAB means the code area of the task in the live script. In
#   Simulink means the window that shows the Sprocket block diagram.
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

WORKSHEET_HEADER = '''%[text] # Teach Sprocket to high-five
%[text] This live script is where you work through the mission. It has one section for each task, with the background, the function that you need and a place for your code. You know MATLAB. Simscape Multibody, robotics and CAD are new to you, so nothing here expects you to know one of their functions in advance.
%[text] ## How to work through this mission
%[text] 1. Ada, your tutor, gives you one task at a time in the chat: what to do and why. Find the section of that task in this live script.
%[text] 2. Read the section. **Background** tells the story and the idea. **The function** explains the function that you need and shows its general syntax. **Why** gives the reason. For a task that you do with the mouse, the second part is **What to look for**.
%[text] 3. Type your code in the code area at the end of the section, then run the section with `Ctrl+Enter` (`Cmd+Enter` on a Mac). The output appears next to your code.
%[text] 4. Tell Ada that you are done. She checks your work in MATLAB and gives you the next task.
%[text] 5. Ask Ada for a hint whenever you like. The first hint of every task explains the function again and gives the exact commands. You can also ask her what any word means.
%[text] 6. The exact commands of every task are in the **Solutions** section at the very bottom of this live script. Try each task first, and look there when you are stuck.
%[text] 7. Run each section once, in order. If the solver ends up in a state that you did not intend, run the sections again from Task 3, which creates a fresh solver. \\
'''

SOLUTIONS_INTRO = ("Try each task first. If you are stuck, ask Ada for a hint, or look here. The commands below are "
                   "examples in text, so running this section does nothing. Type them in the section of their task.")

WORKSHEET_APPENDIX = '''%[appendix]{"version":"1.0"}
%---
%[metadata:view]
%   data: {"layout":"inline"}
%---
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


def sentence(text):
    """Start a sentence that follows a label with a capital letter."""
    return text[:1].upper() + text[1:]


def shown(commands):
    return ", then ".join(f"`{c}`" for c in commands)


def second_part(t):
    """The label and the text of the part that explains the function or what to look for."""
    if t["where"] == "MATLAB":
        return "The function", one_line(t["function"])
    return "What to look for", one_line(t["look"])


def instruction_paragraphs(n, t):
    """What the tutor says: the task description and the reason, in words, with no commands.
    The stock tutor cuts commands out of an instruction, so there are none here to cut."""
    label, _ = second_part(t)
    pointer = (f"Before you start, read Background and {label} in the section Task {n} of your live script, "
               f"{LEARNER_SCRIPT}.")
    if t["where"] == "MATLAB":
        pointer += " Type your code in the code area of that section, then run the section with `Ctrl+Enter`."
    paras = [f"Your task, in {t['where']}: {one_line(t['task'])}", f"Why: {sentence(one_line(t['why']))}", pointer]
    if t.get("question"):
        paras.append(f"Then answer this: {one_line(t['question'])}")
    return paras


def first_hint(t):
    """The first hint carries everything, with the exact commands. The tutor passes hints on as written."""
    label, text = second_part(t)
    hint = f"{label}: {text} Why: {sentence(one_line(t['why']))} Your task, in {t['where']}: {one_line(t['task'])}"
    if t["where"] == "MATLAB":
        hint += (f" Type {shown(t['commands'])} in the code area of this task in your live script, "
                 f"then run the section with `Ctrl+Enter`.")
    return hint


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


def ls(text):
    """One paragraph of live script text. The text markup is based on Markdown, where an
    underscore is formatting, so every name with an underscore goes into a code span."""
    pieces = re.split(r"(`[^`]*`)", one_line(text))
    return "".join(p if p.startswith("`") else re.sub(r"\b\w*_\w*", lambda found: f"`{found.group(0)}`", p)
                   for p in pieces)


def code_example(lines):
    return ["%[text] ```matlabCodeExample", *[f"%[text] {line}" for line in lines], "%[text] ```"]


def worksheet_section(n, t):
    """One task as a section of a plain text live script: Background, The function with its general
    syntax, Why, then an empty code area. The tutor gives the task itself, and the exact commands are
    in the Solutions section. Each paragraph is a single %[text] line, and no blank line may sit
    between two markup lines."""
    label, text = second_part(t)
    first, *rest = paragraphs(t["background"])
    out = ["%%", f"%[text] ## Task {n}. {ls(t['title'])}", f"%[text] **Background:** {ls(first)}"]
    out += [f"%[text] {ls(p)}" for p in rest]
    out.append(f"%[text] **{label}:** {ls(text)}")
    if t["where"] == "MATLAB":
        out.append("%[text] **Syntax:**")
        out += code_example(t["syntax"])
    out.append(f"%[text] **Why:** {sentence(ls(t['why']))}")
    if t["where"] == "MATLAB":
        out.append("%[text] **Your task:** Ada gives you the task in the chat. Type your code below, "
                   "then run this section with `Ctrl+Enter`.")
        out += [f"% Task {n}: type your code below this line.", ""]
    else:
        out.append("%[text] **Your task:** Ada gives you the task in the chat. You do it with the mouse "
                   "in the Simulink window.")
    return "\n".join(out)


def solutions_section(tasks):
    """The exact commands of every task, as text, at the very bottom of the live script."""
    out = ["%%", "%[text] ## Solutions", f"%[text] {SOLUTIONS_INTRO}"]
    for n, t in enumerate(tasks, 1):
        out.append(f"%[text] **Task {n}. {ls(t['title'])}**")
        if t["where"] == "MATLAB":
            out += code_example(t["commands"])
        else:
            out.append("%[text] This task has no code. You do it with the mouse in the Simulink window.")
    return "\n".join(out)


def worksheet(tasks):
    sections = [worksheet_section(i, t) for i, t in enumerate(tasks, 1)] + [solutions_section(tasks)]
    body = "\n".join(sections).rstrip("\n")
    return WORKSHEET_HEADER + body + "\n\n" + WORKSHEET_APPENDIX     # exactly one blank line before the appendix


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

    for old in ("Sprocket_guide.m", "Sprocket_guide.md"):     # earlier forms of the guide
        (RESET / old).unlink(missing_ok=True)
    (RESET / WORKSHEET_NAME).write_text(worksheet(TASKS), encoding="utf-8")

    for old in RESET.glob("reset_t*.m"):
        old.unlink()
    for n in range(2, count + 1):
        (RESET / f"reset_t{n:02d}.m").write_text(reset_script(n, TASKS), encoding="utf-8")

    in_simulink = sum(t["where"] == "Simulink" for t in TASKS)
    print(f"mission.yaml: version {VERSION}, {count} tasks ({count - in_simulink} in MATLAB, {in_simulink} in Simulink)")
    print(f"{WORKSHEET_NAME}: live script with {count} sections and Solutions, copied to the learner as {LEARNER_SCRIPT}")
    print(f"reset scripts: reset_t02.m to reset_t{count:02d}.m")


if __name__ == "__main__":
    main()
