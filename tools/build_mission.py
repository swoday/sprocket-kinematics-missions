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
  .../task_reset_sprocket-high-five/Sprocket_guide.md     (opened by setup)
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

VERSION = "3.0.0"
GUIDE_NAME = "Sprocket_guide.md"

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
# - Every task is one idea, with one to three commands, and every
#   instruction has the same four parts in the same order: Background, The
#   function (or What to look for), Why, and Your task. When you present a
#   task, give all four, in that order. Do not reduce them to the task
#   alone, and never assume that the learner knows which function to use or
#   where to click.
# - In your opening, tell the learner how to work: one task at a time, tell
#   Ada when it is done, ask for a hint to have the function explained again
#   with the exact commands, and the guide holds every task.
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
    return ", then ".join(f"`{c}`" for c in commands)


def second_part(t):
    """The label and the text of the part that explains the function or what to look for."""
    if t["where"] == "MATLAB":
        return "The function", one_line(t["function"])
    return "What to look for", one_line(t["look"])


def task_sentence(t, capital=True):
    start = "Type" if capital else "type"
    if t["where"] == "MATLAB":
        ending = "." if len(t["commands"]) == 1 else " after each line."
        return f"{one_line(t['task'])} {start} {shown(t['commands'])} in the Command Window and press Enter{ending}"
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
