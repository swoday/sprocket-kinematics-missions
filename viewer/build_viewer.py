#!/usr/bin/env python3
"""Inline the generated data into one self-contained page.

index.html loads sprocket_data.js and sprocket_motion.js as separate files,
which needs a local web server. This writes Sprocket_viewer.html with both
inlined, so the page opens from a double-click or an in-app preview. three.js
still comes from the jsDelivr CDN, so it needs an internet connection.

Run:  python3 viewer/build_viewer.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
html = (HERE / "index.html").read_text(encoding="utf-8")
for name in ("sprocket_data.js", "sprocket_motion.js"):
    tag = f'<script src="{name}"></script>'
    assert tag in html, f"missing {tag}"
    html = html.replace(tag, "<script>\n" + (HERE / name).read_text(encoding="utf-8") + "</script>")
out = HERE / "Sprocket_viewer.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out.name}: {out.stat().st_size / 1024:.0f} kB")
