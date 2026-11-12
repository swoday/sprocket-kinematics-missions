#!/usr/bin/env python3
"""Sprocket: a parametric CAD assembly of a robot dog on a maintenance stand.

One script is the single source of truth for the whole assembly. It writes:

  mission bundle   Sprocket.urdf + sprocket_parts/*.stl   (metres, what smimport reads)
  cad/step/        one STEP file per unique part            (millimetres, real B-rep CAD)
  cad/             Sprocket_assembly.step                   (coloured assembly, zero pose)
  cad/             Sprocket_STEP.urdf                       (same robot, STEP geometry)
  cad/             sprocket_spec.json                       (frames, joints, limits, masses)
  viewer/          sprocket_data.js                         (indexed meshes for the 3D viewer)

Run with a Python that has CadQuery:  python build_sprocket.py
Frames follow the URDF convention: x forward, y to the robot's left, z up.
Every link frame is parallel to the world frame at the zero pose (all rpy = 0).
"""
import base64
import json
import math
import os
import struct
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
MISSION = PROJECT / "marketplace" / "missions" / "sprocket-high-five"
BUNDLE = MISSION / "task_reset_sprocket-high-five"
PARTS = "sprocket_parts"
STEP_DIR = HERE / "step"
VIEWER = PROJECT / "viewer"

# --------------------------------------------------------------------------
# Design parameters (millimetres)
# --------------------------------------------------------------------------
BODY_Z = 520.0            # height of the body centre above the floor
HIP_X, HIP_Y = 220.0, 75.0  # abduction axes sit on the body sides
PITCH_Y = 85.0            # lateral offset from abduction axis to hip-pitch axis
L1 = 220.0                # upper leg: hip-pitch axis to knee axis
L2 = 220.0                # lower leg: knee axis to paw centre
PAW_R = 28.0
PAD = (470.0, 190.0, 440.0)  # where the paw centre must be to touch the pad
NECK = (238.0, 0.0, 40.0)    # head frame, in the body frame: front top corner of the body
TAIL = (-222.0, 0.0, 80.0)   # tail joint, in the body frame: rear end of the spine rail
NECK_START = np.array([-20.0, 0.0, -22.0])                    # neck axis, in the head frame
NECK_DIR = np.array([0.72, 0.0, 0.69]) / np.hypot(0.72, 0.69)

LEGS = {"fl": (+1, +1), "fr": (+1, -1), "rl": (-1, +1), "rr": (-1, -1)}  # (front, left)

WHITE = (0.93, 0.94, 0.96, 1.0)
GRAPHITE = (0.17, 0.19, 0.22, 1.0)
AMBER = (1.00, 0.56, 0.02, 1.0)
CYAN = (0.10, 0.78, 0.92, 1.0)
RED = (0.90, 0.22, 0.20, 1.0)
STEEL = (0.45, 0.48, 0.53, 1.0)

# Effective densities in kg/m^3 (parts are modelled solid, real ones are hollow)
RHO = dict(stand=2700, pad=1200, body=450, spine=1400, head=500, visor=1200, ears=1100,
           nose=1100, collar=1200, tail=1100, hip=2600, upper=1300, lower=1300, paw=1100)


# --------------------------------------------------------------------------
# Small solid-modelling helpers
# --------------------------------------------------------------------------
def wp():
    return cq.Workplane("XY")


def cyl(r, p, d, h):
    """Cylinder of radius r starting at point p, running length h along d."""
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p), cq.Vector(*d))


def rbox(sx, sy, sz, c, fillet=0.0, sel=None):
    b = wp().box(sx, sy, sz)
    if fillet:
        b = (b.edges(sel) if sel else b.edges()).fillet(fillet)
    return b.translate(c).val()


def ball(r, c):
    return wp().sphere(r).translate(c).val()


def slab(pts_xz, y0, y1, fillet=0.0, soft=0.0):
    """Extrude a profile drawn in the x-z plane so it spans y0..y1.
    fillet rounds the profile corners, soft rounds every edge."""
    s = wp().polyline(pts_xz).close().extrude(y1 - y0)
    if fillet:
        s = s.edges("|Z").fillet(fillet)
    if soft:
        s = s.edges().fillet(soft)
    return s.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, y1, 0)).val()


def circle_wire(centre, normal, r):
    """Circle whose seam always starts on the +y side, so a loft through
    several of them does not twist."""
    plane = cq.Plane(origin=tuple(centre), xDir=(0, 1, 0), normal=tuple(normal))
    return cq.Workplane(plane).circle(r).val()


def fuse(*shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s.fuse(o)
    return s.clean()


# --------------------------------------------------------------------------
# Parts, each modelled in its own link frame
# --------------------------------------------------------------------------
def part_stand():
    plate = rbox(980, 520, 20, (110, 0, 10), fillet=40, sel="|Z")
    collar = cyl(62, (0, 0, 20), (0, 0, 1), 14)
    column = cyl(28, (0, 0, 20), (0, 0, 1), 425)
    saddle = rbox(210, 110, 25, (0, 0, 457.5), fillet=8)
    post_x = PAD[0] + PAW_R + 14 + 12
    flange = cyl(34, (post_x, PAD[1], 20), (0, 0, 1), 10)
    post = cyl(12, (post_x, PAD[1], 20), (0, 0, 1), PAD[2] - 20 + 34)
    return fuse(plate, collar, column, saddle, flange, post)


def part_pad():
    disc = cyl(62, (PAW_R, 0, 0), (1, 0, 0), 14)
    ring = cyl(47, (PAW_R, 0, 0), (1, 0, 0), 3).cut(cyl(37, (PAW_R, 0, 0), (1, 0, 0), 3))
    return disc.cut(ring).clean()


def part_body():
    # Deep chest, tucked waist: a loft through three rounded sections. The top
    # stays flat for the spine rail and the belly stays flat over the stand.
    def section(w, h, r, x, zc):   # on the YZ workplane local x is world y, local y is world z
        return cq.Sketch().rect(w, h).vertices().fillet(r).moved(cq.Location(cq.Vector(0, zc, x)))
    torso = cq.Workplane("YZ").placeSketch(
        section(132, 74, 22, -250, 13), section(150, 100, 24, -105, 0), section(150, 100, 24, 250, 0)).loft()
    shell = torso.faces(">X").edges().fillet(16).faces("<X").edges().fillet(16).val()
    bosses = [cyl(46, (x0, s * HIP_Y, 0), (1, 0, 0), 70) for x0 in (185, -255) for s in (1, -1)]
    return fuse(shell, *bosses)


def part_spine():  # sensor rail, carry handle and tail mount along the back, in the body frame
    rail = rbox(380, 50, 14, (-50, 0, 55), fillet=5)
    posts = [cyl(7, (x, 0, 60), (0, 0, 1), 34) for x in (-95, 75)]
    grip = cyl(8, (-103, 0, 94), (1, 0, 0), 186)
    mount = cyl(24, (TAIL[0], 0, 60), (0, 0, 1), 12)   # socket the tail root sits in
    return fuse(rail, grip, mount, *posts)


def part_head():  # head frame: origin at the neck joint, x forward
    neck = cyl(36, tuple(NECK_START), tuple(NECK_DIR), 100)
    skull = rbox(116, 122, 98, (104, 0, 84), fillet=24)
    snout = rbox(74, 80, 52, (178, 0, 62), fillet=18)
    return fuse(neck, skull, snout)


def part_visor():
    return rbox(8, 88, 26, (163, 0, 103), fillet=3.5)


def part_nose():
    return ball(12, (216, 0, 74))


def part_ears():
    def ear(side):  # a rounded triangular flap, tip swept back, leaning outward
        flap = slab([(-24, 0), (24, 0), (-8, 66)], -6, 6, fillet=6)
        flap = flap.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -16 * side)
        return flap.translate(cq.Vector(82, 40 * side, 124))
    return fuse(ear(1), ear(-1))


def part_collar():
    centre = NECK_START + 62 * NECK_DIR
    band = cq.Solid.makeTorus(40, 7, cq.Vector(*centre), cq.Vector(*NECK_DIR))
    down = np.array([NECK_DIR[2], 0.0, -NECK_DIR[0]])   # in the collar plane, forward and down
    tag_centre = centre + 49 * down
    tag = cyl(12, tuple(tag_centre - np.array([2.5, 0, 0])), (1, 0, 0), 5)
    return fuse(band, tag)


# Tail styles. Each one is a centreline (heading in degrees above straight
# back, from root to tip), a radius profile along it, and the point where the
# coloured tip starts. SPROCKET_TAIL=<style> picks one without editing the file.
TAIL_STYLES = {
    # sleek and tapered, carried up and back like a pointer's tail
    "sabre": dict(length=220.0, heading=(28, 68), radius=[(0, 15), (1, 5)], split=0.76,
                  root=16, colours=(WHITE, AMBER)),
    # bushy plume, fullest in the middle
    "brush": dict(length=230.0, heading=(38, 82),
                  radius=[(0, 12), (0.2, 22), (0.45, 27), (0.7, 22), (0.9, 11), (1, 4)],
                  split=0.74, root=14, colours=(WHITE, AMBER)),
    # thin whip antenna with a light at the end
    "whip": dict(length=250.0, heading=(40, 76), radius=[(0, 6.5), (1, 3.2)], split=0.985,
                 root=13, tip_ball=10, colours=(GRAPHITE, CYAN)),
}
TAIL_STYLE = os.environ.get("SPROCKET_TAIL", "brush")


def tail_curve(style, n=41):
    """Centreline in the x-z plane of the tail frame: arc length, points,
    unit tangents and radius at each point."""
    length = style["length"]
    s = np.linspace(0.0, length, n)
    h0, h1 = (math.radians(a) for a in style["heading"])
    heading = h0 + (h1 - h0) * s / length          # 0 = straight back, 90 deg = straight up
    pts = np.zeros((n, 3))
    for i in range(1, n):
        mid = 0.5 * (heading[i] + heading[i - 1])
        pts[i] = pts[i - 1] + (s[i] - s[i - 1]) * np.array([-math.cos(mid), 0.0, math.sin(mid)])
    tangents = np.stack([-np.cos(heading), np.zeros(n), np.sin(heading)], axis=1)
    us, rs = zip(*style["radius"])
    return s, pts, tangents, np.interp(s / length, us, rs)


def tail_parts():
    """The tail and its coloured tip, both in the tail frame. They share one
    cross-section, so they meet flush."""
    style = TAIL_STYLES[TAIL_STYLE]
    s, pts, tan, r = tail_curve(style)
    n = len(s)
    k = int(round(style["split"] * (n - 1)))
    wire = lambda i: circle_wire(pts[i], tan[i], r[i])
    lower = sorted(set(list(range(0, k, 4)) + [k]))
    upper = sorted(set(list(range(k, n - 1, 4)) + [n - 1]))
    tail = fuse(ball(style["root"], (0, 0, 0)), cq.Solid.makeLoft([wire(i) for i in lower]))
    tip = fuse(cq.Solid.makeLoft([wire(i) for i in upper]),
               ball(style.get("tip_ball", r[-1]), tuple(pts[-1])))
    return tail, tip


def part_hip():  # left-hand version; the right-hand one is its mirror image
    neck = cyl(38, (0, 0, 0), (0, 1, 0), 18)
    motor = cyl(48, (0, 18, 0), (0, 1, 0), PITCH_Y - 18)
    return fuse(neck, motor)


def part_upper_leg():  # left-hand version
    hub = cyl(44, (0, 0, 0), (0, 1, 0), 38)
    bar = slab([(-36, 0), (36, 0), (26, -L1), (-26, -L1)], 12, 38, soft=6)
    knee = cyl(32, (0, 12, -L1), (0, 1, 0), 26)
    pin = cyl(11, (0, -14, -L1), (0, 1, 0), 56)
    return fuse(hub, bar, knee, pin)


def part_lower_leg():  # symmetric, shared by all four legs
    hub = cyl(30, (0, -11, 0), (0, 1, 0), 22)
    bar = slab([(-23, 0), (23, 0), (12, -(L2 - 18)), (-12, -(L2 - 18))], -11, 11, soft=5)
    return fuse(hub, bar)


def part_paw():
    return fuse(ball(PAW_R, (0, 0, 0)), cyl(13, (0, 0, 0), (0, 0, 1), 26))


def mirror_y(shape):
    return shape.mirror("XZ", (0, 0, 0))


# --------------------------------------------------------------------------
# Robot description: links (mesh, colour, density) and joints
# --------------------------------------------------------------------------
def build_description():
    hip_l, upper_l = part_hip(), part_upper_leg()
    tail, tail_tip = tail_parts()
    tail_colour, tip_colour = TAIL_STYLES[TAIL_STYLE]["colours"]
    meshes = {
        "stand": part_stand(), "high_five_pad": part_pad(), "body": part_body(),
        "spine": part_spine(), "head": part_head(), "visor": part_visor(), "ears": part_ears(),
        "nose": part_nose(), "collar": part_collar(), "tail": tail, "tail_tip": tail_tip,
        "hip_left": hip_l, "hip_right": mirror_y(hip_l),
        "upper_leg_left": upper_l, "upper_leg_right": mirror_y(upper_l),
        "lower_leg": part_lower_leg(), "paw": part_paw(),
    }
    links = [  # name, mesh, colour, density key
        ("stand", "stand", STEEL, "stand"),
        ("high_five_pad", "high_five_pad", RED, "pad"),
        ("body", "body", WHITE, "body"),
        ("spine", "spine", GRAPHITE, "spine"),
        ("head", "head", WHITE, "head"),
        ("visor", "visor", CYAN, "visor"),
        ("ears", "ears", AMBER, "ears"),
        ("nose", "nose", GRAPHITE, "nose"),
        ("collar", "collar", AMBER, "collar"),
        ("tail", "tail", tail_colour, "tail"),
        ("tail_tip", "tail_tip", tip_colour, "tail"),
    ]
    joints = [  # name, type, parent, child, xyz (mm), axis, (lower, upper) in degrees
        ("body_mount", "fixed", "stand", "body", (0, 0, BODY_Z), None, None),
        ("pad_mount", "fixed", "stand", "high_five_pad", PAD, None, None),
        ("spine_mount", "fixed", "body", "spine", (0, 0, 0), None, None),
        ("neck", "fixed", "body", "head", NECK, None, None),
        ("visor_mount", "fixed", "head", "visor", (0, 0, 0), None, None),
        ("ears_mount", "fixed", "head", "ears", (0, 0, 0), None, None),
        ("nose_mount", "fixed", "head", "nose", (0, 0, 0), None, None),
        ("collar_mount", "fixed", "head", "collar", (0, 0, 0), None, None),
        ("tail_wag", "revolute", "body", "tail", TAIL, (0, 0, 1), (-50, 50)),
        ("tail_tip_mount", "fixed", "tail", "tail_tip", (0, 0, 0), None, None),
    ]
    for leg, (sx, sy) in LEGS.items():
        side = "left" if sy > 0 else "right"
        links += [
            (f"{leg}_hip", f"hip_{side}", GRAPHITE, "hip"),
            (f"{leg}_upper_leg", f"upper_leg_{side}", WHITE, "upper"),
            (f"{leg}_lower_leg", "lower_leg", GRAPHITE, "lower"),
            (f"{leg}_paw", "paw", AMBER, "paw"),
        ]
        joints += [
            (f"{leg}_hip_abduct", "revolute", "body", f"{leg}_hip",
             (sx * HIP_X, sy * HIP_Y, 0), (1, 0, 0), (-40, 40)),
            (f"{leg}_hip_pitch", "revolute", f"{leg}_hip", f"{leg}_upper_leg",
             (0, sy * PITCH_Y, 0), (0, 1, 0), (-150, 150)),
            (f"{leg}_knee", "revolute", f"{leg}_upper_leg", f"{leg}_lower_leg",
             (0, 0, -L1), (0, 1, 0), (-160, 5)),
            (f"{leg}_foot", "fixed", f"{leg}_lower_leg", f"{leg}_paw",
             (0, 0, -L2), None, None),
        ]
    return meshes, links, joints


# --------------------------------------------------------------------------
# Exporters
# --------------------------------------------------------------------------
def tessellate(shape, tol=0.12, ang=0.22):
    verts, tris = shape.tessellate(tol, ang)
    v = np.array([(p.x, p.y, p.z) for p in verts], dtype=np.float64)
    t = np.array(tris, dtype=np.uint32)
    return v, t


def write_stl_m(path, v_mm, tris):
    """Binary STL in metres, so no scale attribute is needed anywhere."""
    v = (v_mm / 1000.0).astype(np.float32)
    with open(path, "wb") as f:
        f.write(b"Sprocket part, units: metres".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = np.cross(v[b] - v[a], v[c] - v[a])
            ln = float(np.linalg.norm(n))
            n = n / ln if ln > 0 else n
            f.write(struct.pack("<12fH", *n, *v[a], *v[b], *v[c], 0))


def mass_props(shape, rho):
    vol_m3 = shape.Volume() * 1e-9
    mass = vol_m3 * rho
    com = cq.Shape.centerOfMass(shape)
    inertia_mm5 = np.array(cq.Shape.matrixOfInertia(shape))  # about the COM, unit density
    inertia = inertia_mm5 * 1e-15 * rho                      # kg m^2
    return mass, (com.x / 1000, com.y / 1000, com.z / 1000), inertia


def fmt(x, nd=6):
    s = f"{x:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_urdf(path, links, joints, props, mesh_ref):
    out = ['<?xml version="1.0"?>',
           "<!-- Sprocket: robot dog on a maintenance stand. Generated by cad/build_sprocket.py.",
           "     Units: metres, kilograms, radians. x forward, y left, z up.",
           "     All link frames are parallel to the world frame at the zero pose. -->",
           '<robot name="Sprocket">']
    for name, mesh, rgba, _ in links:
        m, com, I = props[name]
        out += [
            f'  <link name="{name}">',
            "    <inertial>",
            f'      <origin xyz="{fmt(com[0])} {fmt(com[1])} {fmt(com[2])}" rpy="0 0 0"/>',
            f'      <mass value="{fmt(m, 4)}"/>',
            f'      <inertia ixx="{I[0,0]:.6e}" ixy="{I[0,1]:.6e}" ixz="{I[0,2]:.6e}" '
            f'iyy="{I[1,1]:.6e}" iyz="{I[1,2]:.6e}" izz="{I[2,2]:.6e}"/>',
            "    </inertial>",
            "    <visual>",
            '      <origin xyz="0 0 0" rpy="0 0 0"/>',
            f"      <geometry>{mesh_ref(mesh)}</geometry>",
            f'      <material name="{name}_color"><color rgba="{" ".join(fmt(c, 3) for c in rgba)}"/></material>',
            "    </visual>",
            "  </link>",
        ]
    for name, jtype, parent, child, xyz, axis, lim in joints:
        out += [f'  <joint name="{name}" type="{jtype}">',
                f'    <origin xyz="{" ".join(fmt(c / 1000) for c in xyz)}" rpy="0 0 0"/>',
                f'    <parent link="{parent}"/>',
                f'    <child link="{child}"/>']
        if jtype == "revolute":
            lo, hi = (math.radians(a) for a in lim)
            out += [f'    <axis xyz="{axis[0]} {axis[1]} {axis[2]}"/>',
                    f'    <limit lower="{fmt(lo, 5)}" upper="{fmt(hi, 5)}" effort="30" velocity="10"/>']
        out.append("  </joint>")
    out.append("</robot>")
    Path(path).write_text("\n".join(out) + "\n", encoding="utf-8")


def world_frames(joints, q=None):
    """Zero-pose (or posed) world position of every link frame, in mm. Rotation
    is only needed for the assembly export at zero pose, where it is identity."""
    pos = {"stand": np.zeros(3)}
    for name, _, parent, child, xyz, _, _ in joints:
        pos[child] = pos[parent] + np.array(xyz, dtype=float)
    return pos


def b64(arr):
    return base64.b64encode(np.ascontiguousarray(arr).tobytes()).decode("ascii")


def main():
    meshes, links, joints = build_description()
    parts_dir = BUNDLE / PARTS
    for d in (parts_dir, STEP_DIR, VIEWER):
        d.mkdir(parents=True, exist_ok=True)

    viewer_meshes, report = {}, []
    # Per-part mesh quality: (linear tolerance in mm, angular tolerance in rad).
    quality = {"tail": (0.3, 0.36), "tail_tip": (0.3, 0.36), "collar": (0.35, 0.42), "nose": (0.3, 0.4),   # small organic parts
               "body": (0.1, 0.15)}                                                # large lofted surface
    for mesh, shape in meshes.items():
        v, t = tessellate(shape, *quality.get(mesh, (0.12, 0.22)))
        write_stl_m(parts_dir / f"{mesh}.stl", v, t)
        shape.exportStep(str(STEP_DIR / f"{mesh}.step"))
        viewer_meshes[mesh] = {"p": b64((v / 1000.0).astype(np.float32)), "i": b64(t.astype(np.uint32))}
        report.append((mesh, len(t), (parts_dir / f"{mesh}.stl").stat().st_size))

    props = {name: mass_props(meshes[mesh], RHO[key]) for name, mesh, _, key in links}

    write_urdf(BUNDLE / "Sprocket.urdf", links, joints, props,
               lambda m: f'<mesh filename="{PARTS}/{m}.stl"/>')
    write_urdf(HERE / "Sprocket_STEP.urdf", links, joints, props,
               lambda m: f'<mesh filename="step/{m}.step" scale="0.001 0.001 0.001"/>')

    # Coloured assembly at the zero pose: opens in Onshape, SolidWorks, Fusion, FreeCAD.
    pos = world_frames(joints)
    assy = cq.Assembly(name="Sprocket")
    for name, mesh, rgba, _ in links:
        assy.add(meshes[mesh], name=name, loc=cq.Location(cq.Vector(*pos[name])),
                 color=cq.Color(*rgba))
    assy.save(str(HERE / "Sprocket_assembly.step"))

    spec = {
        "units": {"length": "m", "angle": "deg", "mass": "kg"},
        "pad_position_m": [c / 1000 for c in PAD],
        "paw_radius_m": PAW_R / 1000,
        "leg_lengths_m": {"upper": L1 / 1000, "lower": L2 / 1000},
        "links": [{"name": n, "mesh": m, "rgba": list(c), "mass_kg": round(props[n][0], 4)}
                  for n, m, c, _ in links],
        "joints": [{"name": n, "type": t, "parent": p, "child": c,
                    "xyz_m": [v / 1000 for v in xyz], "axis": list(a) if a else None,
                    "limits_deg": list(l) if l else None}
                   for n, t, p, c, xyz, a, l in joints],
    }
    (HERE / "sprocket_spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    (VIEWER / "sprocket_data.js").write_text(
        "// Generated by cad/build_sprocket.py. Indexed meshes in metres (base64 Float32 / Uint32).\n"
        "window.SPROCKET = " + json.dumps({"spec": spec, "meshes": viewer_meshes}) + ";\n",
        encoding="utf-8")

    total = sum(r[2] for r in report)
    for mesh, ntri, size in report:
        print(f"{mesh:18s} {ntri:7d} triangles {size/1024:8.1f} kB")
    print(f"{'TOTAL':18s} {sum(r[1] for r in report):7d} triangles {total/1024:8.1f} kB")
    print(f"robot mass (without stand and pad): "
          f"{sum(props[n][0] for n, *_ in links if n not in ('stand', 'high_five_pad')):.2f} kg")


if __name__ == "__main__":
    main()
