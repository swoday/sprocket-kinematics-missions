#!/usr/bin/env python3
"""Reference kinematics for Sprocket, computed straight from the URDF.

MATLAB is not needed to run this. It reads the same Sprocket.urdf that
smimport reads, does forward kinematics with plain numpy, and solves inverse
kinematics with damped least squares. Its job is to produce the numbers the
mission expects, so the MATLAB side can be checked against an independent
calculation:

  cad/mission_numbers.json     expected answers for every task
  viewer/sprocket_motion.js    joint trajectories the 3D viewer plays back

Run:  python3 cad/kinematics.py
"""
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
URDF = (PROJECT / "marketplace" / "missions" / "sprocket-high-five"
        / "task_reset_sprocket-high-five" / "Sprocket.urdf")


def rot_axis(axis, angle):
    x, y, z = np.asarray(axis, float) / np.linalg.norm(axis)
    c, s, C = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def rot_rpy(r, p, y):
    return rot_axis((0, 0, 1), y) @ rot_axis((0, 1, 0), p) @ rot_axis((1, 0, 0), r)


class Robot:
    def __init__(self, urdf_path=URDF):
        root = ET.parse(urdf_path).getroot()
        self.joints = {}
        children = set()
        for j in root.findall("joint"):
            o = j.find("origin")
            axis = j.find("axis")
            lim = j.find("limit")
            self.joints[j.get("name")] = dict(
                type=j.get("type"), parent=j.find("parent").get("link"),
                child=j.find("child").get("link"),
                xyz=np.array([float(v) for v in o.get("xyz").split()]),
                rpy=[float(v) for v in o.get("rpy").split()],
                axis=[float(v) for v in axis.get("xyz").split()] if axis is not None else None,
                limits_deg=(math.degrees(float(lim.get("lower"))), math.degrees(float(lim.get("upper"))))
                if lim is not None else None)
            children.add(j.find("child").get("link"))
        self.links = [l.get("name") for l in root.findall("link")]
        self.root = next(l for l in self.links if l not in children)
        self.moving = sorted(n for n, j in self.joints.items() if j["type"] != "fixed")

    def fk(self, q_deg=None):
        """World transform (4x4) of every link frame. q_deg maps joint name to degrees."""
        q_deg = q_deg or {}
        T = {self.root: np.eye(4)}
        pending = dict(self.joints)
        while pending:
            for name, j in list(pending.items()):
                if j["parent"] not in T:
                    continue
                M = np.eye(4)
                M[:3, :3] = rot_rpy(*j["rpy"])
                M[:3, 3] = j["xyz"]
                if j["type"] == "revolute":
                    R = np.eye(4)
                    R[:3, :3] = rot_axis(j["axis"], math.radians(q_deg.get(name, 0.0)))
                    M = M @ R
                T[j["child"]] = T[j["parent"]] @ M
                del pending[name]
        return T

    def leg_joints(self, leg):
        return [f"{leg}_hip_abduct", f"{leg}_hip_pitch", f"{leg}_knee"]

    def paw(self, leg, q3, base=None):
        q = dict(base or {})
        q.update(zip(self.leg_joints(leg), q3))
        return self.fk(q)[f"{leg}_paw"][:3, 3]

    def ik(self, leg, target, guess=(0.0, 0.0, 0.0), tol=1e-10, iters=200):
        """Damped least squares on the three leg joints. Angles in degrees.
        Joint limits are ignored on purpose, exactly like KinematicsSolver."""
        q = np.radians(np.array(guess, float))      # solve in radians, report degrees
        target = np.asarray(target, float)
        paw = lambda qr: self.paw(leg, np.degrees(qr))
        lam, h = 1e-7, 1e-6
        for _ in range(iters):
            e = target - paw(q)
            if np.linalg.norm(e) < tol:
                break
            J = np.zeros((3, 3))
            for k in range(3):
                dq = np.zeros(3)
                dq[k] = h
                J[:, k] = (paw(q + dq) - paw(q - dq)) / (2 * h)
            step = np.linalg.solve(J.T @ J + lam * np.eye(3), J.T @ e)
            q = q + np.clip(step, -0.4, 0.4)
        return np.degrees(q), bool(np.linalg.norm(target - paw(q)) < 1e-8)


def wrap(a):
    return (np.asarray(a) + 180.0) % 360.0 - 180.0


def within(robot, leg, q3):
    return [bool(robot.joints[j]["limits_deg"][0] - 1e-9 <= a <= robot.joints[j]["limits_deg"][1] + 1e-9)
            for j, a in zip(robot.leg_joints(leg), q3)]


def main():
    r = Robot()
    spec = json.loads((HERE / "sprocket_spec.json").read_text())
    pad = np.array(spec["pad_position_m"])
    leg = "fl"
    stance = (0.0, 40.0, -80.0)

    paw_hang = r.paw(leg, (0, 0, 0))
    paw_stance = r.paw(leg, stance)
    pad_frame = r.fk()["high_five_pad"][:3, 3]
    assert np.allclose(pad_frame, pad), "pad link frame must sit on the target point"

    q_back, ok_back = r.ik(leg, pad, guess=stance)          # knee stays on the stance side
    q_fwd, ok_fwd = r.ik(leg, pad, guess=(0.0, -120.0, 80.0))  # mirror-image branch
    q_back, q_fwd = wrap(q_back), wrap(q_fwd)
    assert ok_back and ok_fwd
    assert q_back[2] < 0 < q_fwd[2], "expected one knee-back and one knee-forward solution"

    n = 25
    path_pts, path_q, guess = [], [], np.array(stance)
    for s in np.linspace(0, 1, n):
        p = (1 - s) * paw_stance + s * pad
        q, ok = r.ik(leg, p, guess=guess)
        assert ok, f"path point {s:.2f} unreachable"
        guess = q
        path_pts.append(p)
        path_q.append(wrap(q))
    path_q = np.array(path_q)
    assert all(all(within(r, leg, q)) for q in path_q), "path leaves the joint limits"
    assert (path_q[:, 2] < 0).all()

    numbers = {
        "note": "Independent numpy reference computed from Sprocket.urdf. Lengths in m, angles in deg.",
        "leg": leg,
        "joint_names": r.leg_joints(leg),
        "joint_limits_deg": {j: list(r.joints[j]["limits_deg"]) for j in r.leg_joints(leg)},
        "moving_joints_alphabetical": r.moving,
        "pad_position": pad.round(6).tolist(),
        "paw_hanging": paw_hang.round(6).tolist(),
        "fk_task": {"targets_deg": list(stance), "paw_position": paw_stance.round(6).tolist()},
        "ik_pad": {
            "knee_back": {"angles_deg": q_back.round(4).tolist(), "within_limits": within(r, leg, q_back)},
            "knee_forward": {"angles_deg": q_fwd.round(4).tolist(), "within_limits": within(r, leg, q_fwd)},
        },
        "path": {"points": n, "start_point": paw_stance.round(6).tolist(), "end_point": pad.round(6).tolist(),
                 "first_row_deg": path_q[0].round(4).tolist(), "last_row_deg": path_q[-1].round(4).tolist(),
                 "knee_min_deg": float(path_q[:, 2].min().round(4)),
                 "knee_max_deg": float(path_q[:, 2].max().round(4)),
                 "angles_deg": path_q.round(4).tolist()},
    }
    (HERE / "mission_numbers.json").write_text(json.dumps(numbers, indent=2) + "\n", encoding="utf-8")

    # ---- motion clips for the viewer (every clip is a list of {joint: degrees}) ----
    def frame(fl=None, extra=None):
        f = {}
        if fl is not None:
            f.update(zip(r.leg_joints("fl"), [float(a) for a in fl]))
        f.update(extra or {})
        return f

    ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * t)
    clip_mission = []
    for t in np.linspace(0, 1, 30):                      # powered down -> ready stance (joint space)
        clip_mission.append(frame(np.array(stance) * ease(t)))
    for k in np.linspace(0, n - 1, 45):                  # stance -> pad along the solved path
        i = int(math.floor(k)); f = k - i
        j = min(i + 1, n - 1)
        clip_mission.append(frame((1 - f) * path_q[i] + f * path_q[j]))
    for t in np.linspace(0, 1, 40):                      # hold the high-five and wag
        clip_mission.append(frame(path_q[-1], {"tail_wag": 38 * math.sin(6 * math.pi * t)}))

    clip_branches = []
    for t in np.linspace(0, 1, 40):                      # the two answers to the same target
        clip_branches.append(frame((1 - ease(t)) * q_back + ease(t) * q_fwd))

    stance_paw = {l: r.paw(l, stance) for l in ("fl", "fr", "rl", "rr")}
    clip_trot, gq = [], {l: np.array(stance) for l in stance_paw}
    for t in np.linspace(0, 1, 48, endpoint=False):
        f = {"tail_wag": 20 * math.sin(4 * math.pi * t)}
        for l in stance_paw:
            ph = (t + (0.0 if l in ("fl", "rr") else 0.5)) % 1.0
            if ph < 0.5:   # swing: forward along an arc
                u = ph / 0.5
                dx, dz = 0.06 * -math.cos(math.pi * u), 0.05 * math.sin(math.pi * u)
            else:          # stance: slide back in a straight line
                u = (ph - 0.5) / 0.5
                dx, dz = 0.06 * math.cos(math.pi * u), 0.0
            q, ok = r.ik(l, stance_paw[l] + np.array([dx, 0, dz]), guess=gq[l])
            assert ok
            gq[l] = q
            f.update(zip(r.leg_joints(l), [float(a) for a in wrap(q)]))
        clip_trot.append(f)

    motion = {"mission": clip_mission, "branches": clip_branches, "trot": clip_trot,
              "poses": {"stance": list(stance), "knee_back": q_back.tolist(), "knee_forward": q_fwd.tolist()},
              "numbers": numbers}
    (PROJECT / "viewer" / "sprocket_motion.js").write_text(
        "// Generated by cad/kinematics.py. Joint angles in degrees.\n"
        "window.SPROCKET_MOTION = " + json.dumps(motion) + ";\n", encoding="utf-8")

    def row(label, v, unit):
        print(f"{label:34s} [{', '.join(f'{x:9.4f}' for x in v)}] {unit}")

    print("moving joints (alphabetical):", ", ".join(r.moving))
    row("pad position", pad, "m")
    row("paw, powered down (all zero)", paw_hang, "m")
    row("paw, FK task (0, 40, -80) deg", paw_stance, "m")
    row("IK pad, knee-back branch", q_back, "deg   limits ok: " + str(within(r, leg, q_back)))
    row("IK pad, knee-forward branch", q_fwd, "deg   limits ok: " + str(within(r, leg, q_fwd)))
    row("path first row", path_q[0], "deg")
    row("path last row", path_q[-1], "deg")
    print(f"path knee range: {path_q[:,2].min():.2f} .. {path_q[:,2].max():.2f} deg over {n} points")
    for g in [(0, 0, 0), (0, 1, -1), (0, -1, 1), (5, 5, 5)]:
        q, ok = r.ik(leg, pad, guess=g)
        print(f"  reference solver from guess {g}: {wrap(q).round(2)} ok={ok}")


if __name__ == "__main__":
    main()
