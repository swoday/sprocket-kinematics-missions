#!/usr/bin/env python3
"""Static checks for the Sprocket mission package. No MATLAB needed.

Part 1 ports the mission rules from the public framework validator
(matlab/agentic-learning-missions, tests/validate_framework.py: check_missions,
check_app_metadata, check_tasks, check_learner_guidance, check_matlab_scripts).
Part 2 adds checks that matter for this mission: the URDF only uses what
smimport supports, every mesh exists, the numbers quoted in the YAML match the
reference kinematics, and the files parse the way the toolbox's own MATLAB
code reads them.

Run:  python3 tools/validate_mission.py        (needs PyYAML)
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
MARKET = PROJECT / "marketplace"
MISSION_DIR = MARKET / "missions" / "sprocket-high-five"
MISSION = MISSION_DIR / "mission.yaml"
RESET = MISSION_DIR / "task_reset_sprocket-high-five"

ALLOWED_MCP_TOOLS = {
    "check_matlab_code", "detect_matlab_toolboxes", "evaluate_matlab_code", "model_check",
    "model_edit", "model_overview", "model_query_params", "model_read", "model_read_diagnostics",
    "model_resolve_params", "model_test", "run_matlab_file", "run_matlab_test_file",
}
ALLOWED_COMPLETION_KINDS = {"learner_confirmation"}
FORBIDDEN_MATLAB = [
    (re.compile(r"^\s*cd\s*(?:\(|\s|$)", re.I | re.M), "cd"),
    (re.compile(r"^\s*rmdir\s*(?:\(|\s|$)", re.I | re.M), "rmdir"),
    (re.compile(r"^\s*delete\s*(?:\(|\s|$)", re.I | re.M), "delete"),
    (re.compile(r"\bprogress[\\/]", re.I), "progress-file write"),
    (re.compile(r"\bfopen\s*\([^)]*progress", re.I), "progress-file write"),
]
FORBIDDEN_INITIAL_GUIDANCE = re.compile(
    r"\b(?:add_block|add_line|new_system|open_system|set_param|plot|sim)\s*\(", re.I)
ASSERTION_TYPES = {"workspace_var", "workspace_absent", "model_loaded", "block_exists",
                   "block_param", "line_source", "figure_count", "matlab_expression"}
# What smimport reads, per "Import URDF Models" (R2026b). Anything else is ignored or unsupported.
URDF_SUPPORTED = {
    "robot": {"name"}, "link": {"name"}, "inertial": set(), "origin": {"xyz", "rpy"},
    "mass": {"value"}, "inertia": {"ixx", "iyy", "izz", "ixy", "ixz", "iyz"},
    "visual": set(), "geometry": set(), "mesh": {"filename", "scale"},
    "box": {"size"}, "cylinder": {"radius", "length"}, "sphere": {"radius"},
    "material": {"name"}, "color": {"rgba"},
    "joint": {"name", "type"}, "parent": {"link"}, "child": {"link"}, "axis": {"xyz"},
    "limit": {"lower", "upper", "effort", "velocity"},   # effort and velocity are ignored by smimport
}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def strip_matlab_comments(text):
    """Framework behaviour: cut every line at the first percent sign."""
    return "\n".join(line.split("%", 1)[0] for line in text.splitlines())


def strip_comments_string_aware(text):
    """Cut at a percent sign only when it is outside a double-quoted string."""
    out = []
    for line in text.splitlines():
        in_str, cut = False, len(line)
        for i, ch in enumerate(line):
            if ch == '"':
                in_str = not in_str
            elif ch == "%" and not in_str:
                cut = i
                break
        out.append(line[:cut])
    return "\n".join(out)


def main():
    text = MISSION.read_text(encoding="utf-8")
    m = yaml.safe_load(text)

    # ---------------- Part 1: framework rules ----------------
    check("mission folder is a lowercase slug",
          re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", MISSION_DIR.name))
    required = ["mission_id", "version", "title", "objective", "supported_matlab_releases",
                "required_capabilities", "write_mode", "capability_mode", "app", "tasks"]
    check("required top-level fields", all(f in m for f in required),
          "missing: " + ", ".join(f for f in required if f not in m))
    check("mission_id is a quoted two-digit string",
          isinstance(m["mission_id"], str) and re.fullmatch(r"\d{2}", m["mission_id"]))
    check("write_mode and capability_mode use supported values",
          m["write_mode"] in {"read_inspect", "allow_agent_edits"}
          and m["capability_mode"] in {"guided_tutor", "agent_build", "review_only"})
    check("release and capability lists are non-empty text lists",
          all(isinstance(m[f], list) and m[f] and all(isinstance(i, str) and i for i in m[f])
              for f in ("supported_matlab_releases", "required_capabilities")))
    thumb = m.get("thumbnail", "")
    check("declared thumbnail exists and is PNG or SVG",
          (not thumb) or (Path(thumb).suffix.lower() in {".png", ".svg"} and (MISSION_DIR / thumb).is_file()),
          str(thumb))

    app = m["app"]
    check("app text fields", all(isinstance(app.get(f), str) and app[f].strip()
                                 for f in ("summary", "audience", "difficulty", "status")))
    check("app difficulty and status values",
          app.get("difficulty") in {"beginner", "intermediate", "advanced", "unspecified"}
          and app.get("status") in {"published", "draft", "demo", "deprecated"})
    check("app estimated_minutes, learner_visible, tile_order",
          isinstance(app.get("estimated_minutes"), int) and app["estimated_minutes"] > 0
          and isinstance(app.get("learner_visible"), bool) and "tile_order" in app)
    check("app products and topics lists",
          all(isinstance(app.get(f), list) and app[f] and all(isinstance(i, str) and i for i in app[f])
              for f in ("products", "topics")))

    tasks = m["tasks"]
    ids = [t.get("id") for t in tasks]
    check("task ids are sequential", ids == [f"t{i:02d}" for i in range(1, len(tasks) + 1)], str(ids))
    check("10 to 16 tasks, one idea each", 10 <= len(tasks) <= 16, f"{len(tasks)} tasks")
    bad_fields, bad_tools, bad_hints, bad_guidance = [], [], [], []
    for t in tasks:
        tid = t["id"]
        if not all(t.get(f) for f in ("title", "instruction", "completion", "hints")):
            bad_fields.append(tid)
        strategy = t["completion"].get("strategy")
        if not (isinstance(strategy, list) and strategy and isinstance(t["completion"].get("description"), str)):
            bad_fields.append(tid)
        for item in strategy or []:
            if not (isinstance(item.get("check"), str) and item["check"].strip()):
                bad_tools.append(f"{tid}: empty check")
            if item.get("tool") is not None:
                if item["tool"] not in ALLOWED_MCP_TOOLS:
                    bad_tools.append(f"{tid}: {item['tool']}")
            elif item.get("kind") not in ALLOWED_COMPLETION_KINDS:
                bad_tools.append(f"{tid}: kind {item.get('kind')}")
        hints = t["hints"]
        if not (isinstance(hints, list) and 1 <= len(hints) <= 3
                and all(isinstance(h, str) and h.strip() for h in hints)):
            bad_hints.append(tid)
        if FORBIDDEN_INITIAL_GUIDANCE.search(t["title"]):
            bad_guidance.append(tid)
    check("every task has title, instruction, completion, hints", not bad_fields, str(bad_fields))
    check("completion items use allowed MCP tools or learner_confirmation", not bad_tools, str(bad_tools))
    check("hints are ordered lists of 1 to 3 strings", not bad_hints, str(bad_hints))
    check("titles contain no runnable commands", not bad_guidance, str(bad_guidance))

    # One action per task. The stock tutor shows only the title and the goal of a
    # task and gives hints one at a time on request. So every task asks for a
    # single thing, the title of a MATLAB task names what to type, and the first
    # hint is the exact command. This departs on purpose from the framework rule
    # that instructions carry no commands: the author wants a learner who starts
    # from zero to be helped at every step.
    def action_of(t):
        found = re.findall(r"Your task, in (MATLAB|Simulink): ", t["instruction"])
        return found[0] if len(found) == 1 else None

    def commands_of(t):
        typed = re.search(r"Type (.*?) in the code area of this task in your live script", t["hints"][0], re.S)
        return re.findall(r"`([^`]+)`", typed.group(1)) if typed else []

    def second_label(t):
        return "The function: " if action_of(t) == "MATLAB" else "What to look for: "

    # The tutor gives the task: the instruction is the task description and the
    # reason, in words. It holds no commands, because the stock tutor cuts them
    # out. Background and the function live in the live script, and the exact
    # commands are in the first hint and in the Solutions section.
    bad_action = []
    for n, t in enumerate(tasks, 1):
        where, body = action_of(t), t["instruction"]
        if where is None or not body.startswith(f"Your task, in {where}: ") or "Why: " not in body \
                or f"section Task {n} of your live script" not in body \
                or (where == "MATLAB" and not commands_of(t)) \
                or any(f"`{c}`" in body for c in commands_of(t)):
            bad_action.append(t["id"])
    check("every instruction is the task description and the reason, with no commands", not bad_action, str(bad_action))
    check("the opening tells the learner how to work and who the mission is for",
          "How you will work: " in m["objective"] and "know MATLAB" in m["objective"])
    busywork = [t["id"] for t in tasks if commands_of(t) and all(
        re.fullmatch(r"\w+|edit\(\w+\)", c.strip()) for c in commands_of(t))]
    check("no task is only displaying a variable or opening a file", not busywork, str(busywork))
    many = [f"{t['id']}: {len(commands_of(t))}" for t in tasks if len(commands_of(t)) > 3]
    check("no task asks for more than three command lines", not many, str(many))
    untitled = [t["id"] for t in tasks if action_of(t) == "MATLAB"
                and not any(word.lower() in t["title"].lower()
                            for c in commands_of(t) for word in re.findall(r"[A-Za-z]\w{3,}", c))]
    check("the title of every MATLAB task names what to type", not untitled, str(untitled))
    weak_hints = []
    for t in tasks:
        h = t["hints"]
        if len(h) != 3:
            weak_hints.append(f"{t['id']}: needs 3 hints")
        elif not (h[0].startswith(second_label(t)) and "Why: " in h[0]
                  and f"Your task, in {action_of(t)}: " in h[0]
                  and all(f"`{c}`" in h[0] for c in commands_of(t))):
            weak_hints.append(t["id"])
    check("the first hint of every task gives the function, the reason and the exact command",
          not weak_hints, str(weak_hints))
    # The live script that setup copies to the learner and opens. It is a plain
    # text live script (R2025a and later) with the instructions and an empty
    # code area for every task. It does not depend on the tutor. The format
    # rules come from "Live Code File Formats" in the R2026b documentation.
    sheet_path = RESET / "sprocket_worksheet.m"
    sheet = sheet_path.read_text(encoding="utf-8") if sheet_path.is_file() else ""
    squeeze = lambda s: re.sub(r"\s+", "", s)
    sheet_lines = sheet.split("\n")
    appendix_at = next((i for i, line in enumerate(sheet_lines) if line.startswith("%[appendix]")), len(sheet_lines))
    body_lines, appendix_lines = sheet_lines[:appendix_at], sheet_lines[appendix_at:]
    is_markup = lambda line: line == "%%" or line.startswith("%[text")
    blank_between = [i + 1 for i in range(1, len(body_lines) - 1)
                     if body_lines[i] == "" and is_markup(body_lines[i - 1]) and is_markup(body_lines[i + 1])]
    check("live script: no blank line sits between two markup lines", not blank_between, str(blank_between))
    check("live script: one blank line, then the appendix with the view metadata, ends the file",
          len(body_lines) >= 2 and body_lines[-1] == "" and body_lines[-2] != ""
          and appendix_lines[:5] == ['%[appendix]{"version":"1.0"}', "%---", "%[metadata:view]",
                                     '%   data: {"layout":"inline"}', "%---"])
    check("the mission needs a release with plain text live scripts (R2025a or later)",
          all(str(r) >= "R2025a" for r in m["supported_matlab_releases"]), str(m["supported_matlab_releases"]))
    text_lines = [line[len("%[text] "):] for line in body_lines if line.startswith("%[text] ")]
    in_fence, prose = False, []
    for line in text_lines:
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            prose.append(line)
    bare = sorted({w for line in prose for w in re.findall(r"\b\w*_\w*", re.sub(r"`[^`]*`", "", line))})
    check("live script: every name with an underscore is in a code span", not bare, str(bare))
    check("live script: code examples are opened and closed", not in_fence
          and sum(line == "```matlabCodeExample" for line in text_lines) == sum(line == "```" for line in text_lines))
    lists = [i for i, line in enumerate(prose) if re.match(r"(\d+\.|-) ", line)]
    check("live script: only the last item of the list ends with a backslash",
          bool(lists) and prose[lists[-1]].endswith(" \\") and not any(prose[i].endswith("\\") for i in lists[:-1]))
    sheet_heads = re.findall(r"(?m)^%\[text\] ## Task (\d+)\. (.+)$", sheet)
    check("live script: one section per task, with the same titles",
          sheet_heads == [(str(i), t["title"]) for i, t in enumerate(tasks, 1)], f"{len(sheet_heads)} sections")
    section_starts = [i for i, line in enumerate(body_lines) if line.startswith("%[text] ## Task ")]
    check("live script: every task heading follows a section break",
          bool(section_starts) and all(body_lines[i - 1] == "%%" for i in section_starts))
    solutions_at = next((i for i, line in enumerate(body_lines) if line == "%[text] ## Solutions"), len(body_lines))
    sections = ["\n".join(body_lines[a:b]) for a, b in zip(section_starts, section_starts[1:] + [solutions_at - 1])]
    examples = lambda block: [[line[len("%[text] "):].strip() for line in found.splitlines()] for found in
                              re.findall(r"(?s)%\[text\] ```matlabCodeExample\n(.*?)\n%\[text\] ```", block)]
    out_of_sync = []
    for n, (t, section) in enumerate(zip(tasks, sections), 1):
        in_matlab = action_of(t) == "MATLAB"
        labels = ["**Background:**", "**" + second_label(t).strip() + "**"] + (["**Syntax:**"] if in_matlab else []) \
            + ["**Why:**", "**Your task:**"]
        places = [section.find(label) for label in labels]
        has_area = f"% Task {n}: type your code below this line." in section
        if -1 in places or places != sorted(places) or has_area != in_matlab \
                or len(examples(section)) != (1 if in_matlab else 0):
            out_of_sync.append(t["id"])
    check("live script: every section has background, the function with its syntax, why and a code area",
          len(sections) == len(tasks) and not out_of_sync, str(out_of_sync))
    solutions = "\n".join(body_lines[solutions_at:])
    unsolved = []
    for n, t in enumerate(tasks, 1):
        part = solutions.split(f"%[text] **Task {n}. {t['title']}**")
        after = part[1].split("%[text] **Task ")[0] if len(part) == 2 else ""
        given = examples(after)[0] if examples(after) else []
        if len(part) != 2 or [squeeze(c) for c in given] != [squeeze(c) for c in commands_of(t)]:
            unsolved.append(t["id"])
    check("live script: the Solutions section at the very bottom has the exact commands of every task",
          solutions_at < len(body_lines) and body_lines[solutions_at - 1] == "%%" and not unsolved, str(unsolved))
    check("live script: it opens with how to work through the mission",
          "%[text] ## How to work through this mission" in sheet.split("%[text] ## Task 1.")[0])
    stale = [name for name in ("Sprocket_guide.m", "Sprocket_guide.md") if (RESET / name).exists()]
    check("the earlier guide files are gone", not stale, str(stale))
    guide_comments = "\n".join(prose)
    guide_style = sorted(set(re.findall(
        r"—|–|\s-\s|\b\w+n't\b|\b(?:it|that|you|we|they|he|she|let|here|there|what)'(?:s|ll|re|ve|d)\b",
        guide_comments, re.I)))
    check("live script: the text has no dashes and no contractions (house style)", not guide_style, str(guide_style))
    setup_text = (MISSION_DIR / m["setup"]["script"]).read_text(encoding="utf-8")
    check("setup copies the live script to the learner, opens it and leaves scriptFile",
          '"sprocket_worksheet.m"' in setup_text and '"sprocket_high_five.m"' in setup_text
          and "edit(scriptFile)" in setup_text and "guideFile" not in setup_text
          and not re.search(r"(?m)^clear .*\bscriptFile\b", setup_text))
    check("the opening says that the learner works in a live script",
          "live script named sprocket_high_five.m" in " ".join(m["objective"].split()))
    in_simulink = [t["id"] for t in tasks if action_of(t) == "Simulink"]
    check("the mission has tasks in both MATLAB and Simulink", len(in_simulink) >= 1, str(in_simulink))
    mismatch = [t["id"] for t in tasks
                if bool(re.search(r"Then answer this:[^?]*\?", t["instruction"], re.S))
                != any(i.get("kind") == "learner_confirmation" for i in t["completion"]["strategy"])
                or t["instruction"].count("Then answer this:") > 1]
    check("every question is checked by the tutor, with at most one per task", not mismatch, str(mismatch))
    solve_at = [i for i, t in enumerate(tasks) if any("solve(ks" in c for c in commands_of(t))]
    view_at = [i for i, t in enumerate(tasks) if "viewSolution(ks)" in commands_of(t)]
    unseen = [tasks[i]["id"] for i in solve_at if not any(i <= v <= i + 1 for v in view_at)]
    check("every solve is followed by viewSolution, in the same task or the next",
          len(view_at) >= 4 and not unseen, str(unseen))
    learner_text = [m["objective"]] + [t["instruction"] for t in tasks] + [h for t in tasks for h in t["hints"]]
    style = sorted({w for txt in learner_text
                    for w in re.findall(r"—|–|\s-\s|\b\w+n't\b|\b(?:it|that|you|we|they|he|she|let|here|there|what)'(?:s|ll|re|ve|d)\b",
                                        txt, re.I)})
    check("learner text has no dashes and no contractions (house style)", not style, str(style))
    long_sentences = [s.strip()[:60] for txt in learner_text
                      for s in re.split(r"(?<=[.?!])\s+", re.sub(r"`[^`]*`", "CODE", txt))
                      if len(s.split()) > 35]
    check("no learner sentence is longer than 35 words", not long_sentences, str(long_sentences))

    setup = m.get("setup")
    setup_script = MISSION_DIR / setup["script"] if setup else None
    check("setup script exists", setup is None or setup_script.is_file(), str(setup and setup["script"]))
    missing_resets = [t["id"] for t in tasks[1:] if not (RESET / f"reset_{t['id']}.m").is_file()]
    check("a reset script exists for every task after the first", not missing_resets, str(missing_resets))
    scripts = ([setup_script] if setup_script else []) + sorted(RESET.glob("reset_t*.m"))
    forbidden = [f"{s.name}: {label}" for s in scripts for pat, label in FORBIDDEN_MATLAB
                 if pat.search(strip_matlab_comments(s.read_text(encoding="utf-8")))]
    check("setup and reset scripts avoid cd, rmdir, delete and progress writes", not forbidden, str(forbidden))

    # ---------------- Part 2: this mission ----------------
    lo = [o["id"] for o in m.get("learning_outcomes", [])]
    refs = [r for t in tasks for r in t.get("outcome_refs", [])]
    check("every outcome_ref names a learning outcome", all(r in lo for r in refs))
    check("every learning outcome is practised by a task", all(o in refs for o in lo),
          "unused: " + ", ".join(o for o in lo if o not in refs))

    # The toolbox reads some fields with line regexes, not a YAML parser.
    check("objective uses the '>' folded form the catalog reader expects",
          re.search(r"(?m)^objective:\s*>\s*$", text))
    check("task ids match the catalog regex",
          len(re.findall(r'(?m)^\s+- id:\s*"?t\d{2}"?', text)) == len(tasks))
    check("setup.script is readable by the workspace copier",
          re.search(r'(?m)^\s+script:\s*["\']?([^"\'\r\n]+)["\']?\s*$', text))
    check("thumbnail is readable by the workspace copier",
          (not thumb) or re.search(r'(?m)^thumbnail:\s*["\']?([^"\'\r\n]+)["\']?\s*$', text))
    check("inline lists in the app block have no nested commas or quotes",
          all("," not in i and '"' not in i for f in ("products", "topics") for i in app[f]))

    rv = m.get("runtime_validation", {})
    assertions = list(rv.get("setup", {}).get("assertions", []))
    reset_tasks = [r["task"] for r in rv.get("resets", [])]
    for r in rv.get("resets", []):
        assertions += r["assertions"]
    check("runtime_validation uses supported assertion types",
          all(a.get("type") in ASSERTION_TYPES for a in assertions),
          str({a.get("type") for a in assertions} - ASSERTION_TYPES))
    check("runtime_validation resets name real tasks", all(t in ids[1:] for t in reset_tasks), str(reset_tasks))

    manifest = yaml.safe_load((MARKET / "manifest.yaml").read_text(encoding="utf-8"))
    entry = [e for e in manifest.get("missions", []) if e.get("id") == MISSION_DIR.name]
    check("manifest lists the mission at the right path",
          len(entry) == 1 and (MARKET / entry[0]["path"]).is_file())
    # registerMarketplace.m reads these five fields with this pattern and rejects
    # the marketplace when one is missing or empty (an empty source_url included).
    manifest_text = (MARKET / "manifest.yaml").read_text(encoding="utf-8")
    unreadable = [f for f in ("id", "title", "source_url", "content_version", "minimum_toolbox_version")
                  if not re.search(r"(?m)^" + f + r":\s*[\"']?([^\"'\r\n]+)[\"']?\s*$", manifest_text)]
    check("manifest fields the app requires are present and not empty", not unreadable, str(unreadable))
    src = str(manifest.get("source_url") or "")
    check("manifest source_url is an HTTPS or SSH Git clone URL",
          bool(re.match(r"^https://[^/@:]+(?::[0-9]+)?/\S+$", src)
               or re.match(r"^ssh://[^@/\s]+@[^/:\s]+(?::[0-9]+)?/\S+$", src)
               or re.match(r"^[^@/\s]+@[^:/\s]+:\S+$", src)), src or "(empty)")

    # URDF
    urdf = RESET / "Sprocket.urdf"
    root = ET.parse(urdf).getroot()
    unsupported = sorted({f"<{el.tag} {a}>" if a else f"<{el.tag}>"
                          for el in root.iter()
                          for a in ([None] if el.tag not in URDF_SUPPORTED
                                    else [k for k in el.attrib if k not in URDF_SUPPORTED[el.tag]])})
    check("URDF uses only elements and attributes smimport supports", not unsupported, str(unsupported))
    links = [l.get("name") for l in root.findall("link")]
    joints = root.findall("joint")
    children = [j.find("child").get("link") for j in joints]
    parents = [j.find("parent").get("link") for j in joints]
    check("URDF is a tree: every link but one has exactly one parent joint",
          len(set(children)) == len(children) == len(links) - 1 and all(p in links for p in parents)
          and all(c in links for c in children))
    names = links + [j.get("name") for j in joints]
    check("link and joint names are unique (they become block names)", len(set(names)) == len(names))
    meshes = [el.get("filename") for el in root.iter("mesh")]
    missing = [f for f in meshes if not (RESET / f).is_file()]
    check("every mesh file referenced by the URDF exists", not missing, f"{len(meshes)} references, missing {missing}")
    check("mesh files are STL, DAE or STEP",
          all(Path(f).suffix.lower() in {".stl", ".dae", ".step", ".stp"} for f in meshes))
    revolute = sorted(j.get("name") for j in joints if j.get("type") == "revolute")
    check("revolute joints have an axis and lower/upper limits",
          all(j.find("axis") is not None and j.find("limit") is not None
              and {"lower", "upper"} <= set(j.find("limit").attrib)
              for j in joints if j.get("type") == "revolute"), f"{len(revolute)} revolute joints")
    used = set(re.findall(r"\b(?:fl|fr|rl|rr)_[a-z_]+|\bpad_mount\b|\btail_wag\b", text))
    used |= set(re.findall(r"\b(?:fl|fr|rl|rr)_[a-z_]+|\bpad_mount\b", "\n".join(
        p.read_text(encoding="utf-8") for p in list(RESET.glob("*.m")) + list((PROJECT / "matlab").glob("*.m")))))
    unknown = sorted(n for n in used if n not in names)
    check("every joint or link named in the YAML and MATLAB files exists in the URDF", not unknown, str(unknown))

    # Numbers quoted to the tutor must equal the reference kinematics.
    ref = json.loads((PROJECT / "cad" / "mission_numbers.json").read_text())
    f2 = lambda v: " ".join(f"{x:.2f}" for x in v)
    back, fwd = f2(ref["ik_pad"]["knee_back"]["angles_deg"]), f2(ref["ik_pad"]["knee_forward"]["angles_deg"])
    stance = " ".join(f"{x:.4f}" for x in ref["fk_task"]["paw_position"])
    check("YAML quotes the reference knee-back answer", f"[{back}]" in text, back)
    check("YAML quotes the reference knee-forward answer", f"[{fwd}]" in text, fwd)
    check("YAML quotes the reference stance paw position", f"[{stance}]" in text, stance)
    check("knee-back answer is inside the joint limits, knee-forward is not",
          all(ref["ik_pad"]["knee_back"]["within_limits"]) and not all(ref["ik_pad"]["knee_forward"]["within_limits"]))
    setup_text = setup_script.read_text(encoding="utf-8")
    pad = re.search(r"padPosition\s*=\s*\[([^\]]+)\]", setup_text)
    check("setup's padPosition equals the pad frame in the CAD",
          pad and [float(v) for v in pad.group(1).split()] == ref["pad_position"], pad.group(1) if pad else "")
    lim = ref["joint_limits_deg"]["fl_knee"]
    check("the knee limits stated to the learner match the URDF",
          round(lim[0]) == -160 and round(lim[1]) == 5 and "-160 and +5" in text, str([round(x, 2) for x in lim]))

    # Cheap MATLAB sanity: balanced brackets and quotes outside comments.
    unbalanced = []
    for p in scripts + sorted((PROJECT / "matlab").glob("*.m")):
        code = strip_comments_string_aware(p.read_text(encoding="utf-8"))
        nostr = re.sub(r'"(?:[^"\n]|"")*"', '""', code)
        if any(nostr.count(a) != nostr.count(b) for a, b in ("()", "[]", "{}")) or code.count('"') % 2:
            unbalanced.append(p.name)
    check("MATLAB files have balanced brackets and string quotes", not unbalanced, str(unbalanced))

    width = max(len(n) for n, _, _ in results)
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail if (detail and not ok) or (ok and detail and len(detail) < 60) else ''}".rstrip())
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)} of {len(results)} checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
