# Sprocket Kinematics Missions

![Sprocket giving a high-five](docs/img/sprocket_high_five.png)

A marketplace for the [Interactive Missions](https://github.com/matlab/agentic-learning-missions) toolbox with one mission:

**Teach a Robot Dog to High-Five with KinematicsSolver**

The learner imports Sprocket, a robot dog built as a real CAD assembly, into Simscape Multibody and poses him with `simscape.multibody.KinematicsSolver`. It has 29 small tasks, one action each, and takes about 75 minutes. It is written for people who know MATLAB and have no Simscape Multibody, robotics or CAD background. Every task gives the same four things: the background, the function that you need, why you need it, and your task with the exact command. The first task shows you how to work through the mission. A guide opens in the MATLAB Editor when the mission starts, and you can ask the tutor for a hint at any time: the first hint of every task is the exact command.

**Status: draft.** The URDF imports, the model opens in MATLAB, and the marketplace registers in the app. The ten-row check script and a full play-through with the tutor are still to be confirmed.

## Run the mission

| Step | Do this |
|---|---|
| 1 | Install the Interactive Missions toolbox, Simscape Multibody, an agent client (Claude Code, Codex, Copilot or Gemini) and the Simulink Agentic Toolkit, which sets up the MATLAB MCP Server |
| 2 | Open **Interactive Missions** from the MATLAB Apps Gallery. In **Marketplace settings**, add this repository's clone URL, then **Refresh** |
| 3 | Pick the Sprocket card. **Start Mission** saves progress, **Practice** does not. Choose your agent client |
| 4 | The app shows a `cd` line for your mission workspace. Run it in a terminal and start the agent in that folder |
| 5 | Start the tutor: `/mission-tutoring` in Claude Code, `$mission-tutoring` in Codex. Other clients follow the prompt the app shows |
| 6 | Work in the MATLAB Command Window. Tell the tutor when you are done with a task, or ask for a hint |

Supported releases: R2024b to R2026b. Products: MATLAB, Simulink, Simscape, Simscape Multibody.

### If adding the marketplace fails

If the app answers `Unrecognized field name "Id"` when you add the link, its list of registered marketplaces has not been created yet. Run this once in the MATLAB Command Window, add the link again, then close and reopen the app:

```matlab
f = fullfile(prefdir,"InteractiveMissions","app","installed_marketplaces.json");
if ~isfile(f)
    if ~isfolder(fileparts(f)), mkdir(fileparts(f)); end
    writelines('{"Marketplaces":[]}', f);
end
```

It only creates the file when it is missing, so existing marketplaces are left alone.

### How the tutor decides what to show

The tutor follows its own skill, which the toolbox copies into your mission workspace. With the standard skill, the tutor presents the goal of each task and gives one hint each time you ask. This mission is built for that. Each task is one action, and its title names the function to use. You get the exact command in two ways that need no change to the tutor:

- **The guide.** When the mission starts, `Sprocket_guide.md` opens in the MATLAB Editor. It is a Markdown file that lists every task: where to work, the exact command, what it does and why. Type or paste each command in the Command Window. The copy in your workspace folder is yours, so you can write notes in it, and you can open it in any Markdown viewer.
- **Hints.** The first hint of every task is the exact command, with what it does and why. Ask the tutor for a hint whenever you want to be shown what to do.

The tutor still checks each task, answers your questions and asks a question after the tasks where there is something to notice.

There is also an optional change to the tutor itself. If you want the tutor to show the command of every task up front, add the guided walkthrough section in `docs/guided-mode-addendum.md` to the tutor skill of your installed toolbox. It only takes effect for missions that declare `teaching_mode: guided_walkthrough`. Run this once in MATLAB, then start the mission again:

```matlab
skill = fullfile(interactiveMissions.internal.toolboxRoot(),"src","skills","mission-tutoring","SKILL.md");
backup = fullfile(prefdir,"mission-tutoring-SKILL-original.md");
if ~isfile(backup), copyfile(skill,backup); end
extra = webread("https://raw.githubusercontent.com/swoday/sprocket-kinematics-missions/main/docs/guided-mode-addendum.md", weboptions(ContentType="text"));
if ~contains(fileread(skill),"Guided Walkthrough Mode"), writelines([string(fileread(skill)); string(extra)], skill); end
```

To undo it, run `copyfile(backup,skill)`. This changes your local copy of the toolbox only, and it has not been tested with every agent client.

## What the mission teaches

| Tasks | Stage | Idea |
|---|---|---|
| 1 | Open the guide and learn how to work | Every task has four parts: background, the function, why, your task |
| 2 to 4 | Import the CAD assembly and look at it | A URDF file and its part files become a Simscape Multibody model |
| 5 to 7 | Create the solver and find the leg joints | The solver names joint variables itself; they are not the joint names |
| 8 to 11 | Tell the solver where the paw is | Frame variables measure one frame from another |
| 12 to 15 | Forward kinematics into the ready stance | Joint angles in, paw position out |
| 16 to 20 | Inverse kinematics to the pad | Paw position in, joint angles out |
| 21 to 23 | Pick the pose the real joints can reach | The solver ignores joint limits; an initial guess picks the answer |
| 24 to 29 | Plan the move from stance to high-five | Solve along a path, each answer seeding the next |

## What is in this repository

| Folder | Contents |
|---|---|
| `marketplace/` | The marketplace manifest and the mission: `mission.yaml`, the setup script, the reset scripts, the URDF and the STL parts |
| `cad/` | The parametric CAD source (`build_sprocket.py`, CadQuery), STEP parts, a coloured STEP assembly, and the reference kinematics (`kinematics.py`, `mission_numbers.json`) |
| `matlab/` | A worked solution and `verify_sprocket_mission.m`, which runs the whole mission and compares it with the reference numbers |
| `viewer/` | An interactive 3D viewer of the assembly and the mission. Open `Sprocket_viewer.html` in a browser (needs internet for three.js) |
| `tools/` | `validate_mission.py`, static checks on the mission files |
| `docs/img/` | Renders |

Spoiler warning for learners: `matlab/` and the hints in `mission.yaml` contain the answers.

## For authors

| To do this | Run |
|---|---|
| Check the mission end to end in MATLAB | `matlab/verify_sprocket_mission.m` (ten rows, all should pass) |
| Change a task, the guide or a reset script | Edit the task list in `tools/build_mission.py`, then run `python3 tools/build_mission.py`. It writes `mission.yaml`, `Sprocket_guide.md` and the reset scripts together |
| Check the mission files without MATLAB | `python3 tools/validate_mission.py` (needs PyYAML) |
| Change the geometry | `pip install cadquery`, then `python cad/build_sprocket.py` |
| Refresh the reference numbers and the viewer | `python3 cad/kinematics.py`, then `python3 viewer/build_viewer.py` |

The CAD files travel inside the mission's `task_reset_sprocket-high-five/` folder because the app copies only the mission file, the setup script, the thumbnail and that folder into a learner workspace.

`source_url` in `marketplace/manifest.yaml` must hold this repository's clone URL. The app refuses to register a marketplace while it is empty.
