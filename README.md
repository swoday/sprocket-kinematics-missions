# Sprocket Kinematics Missions

![Sprocket giving a high-five](docs/img/sprocket_high_five.png)

A marketplace for the [Interactive Missions](https://github.com/matlab/agentic-learning-missions) toolbox with one mission:

**Teach a Robot Dog to High-Five with KinematicsSolver**

The learner imports Sprocket, a robot dog built as a real CAD assembly, into Simscape Multibody and poses him with `simscape.multibody.KinematicsSolver`. Seven tasks, about 45 minutes, for MATLAB users who are new to Simscape Multibody.

**Status: draft.** The URDF imports and the model opens in MATLAB. The ten-row check script and a full play-through with the tutor are still to be confirmed.

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

## What the mission teaches

| # | Task | Idea |
|---|---|---|
| 1 | Import the CAD assembly | A URDF file and its part files become a Simscape Multibody model |
| 2 | Create the solver and find the leg joints | The solver names joint variables itself; they are not the joint names |
| 3 | Tell the solver where the paw is | Frame variables measure one frame from another |
| 4 | Forward kinematics into the ready stance | Joint angles in, paw position out |
| 5 | Inverse kinematics to the pad | Paw position in, joint angles out |
| 6 | Pick the pose the real joints can reach | The solver ignores joint limits; an initial guess picks the answer |
| 7 | Plan the move from stance to high-five | Solve along a path, each answer seeding the next |

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
| Check the mission files without MATLAB | `python3 tools/validate_mission.py` (needs PyYAML) |
| Change the geometry | `pip install cadquery`, then `python cad/build_sprocket.py` |
| Refresh the reference numbers and the viewer | `python3 cad/kinematics.py`, then `python3 viewer/build_viewer.py` |

The CAD files travel inside the mission's `task_reset_sprocket-high-five/` folder because the app copies only the mission file, the setup script, the thumbnail and that folder into a learner workspace.

`source_url` in `marketplace/manifest.yaml` must hold this repository's clone URL. The app refuses to register a marketplace while it is empty.
