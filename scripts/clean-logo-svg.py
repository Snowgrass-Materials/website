#!/usr/bin/env python3
"""Strip Inkscape cruft from a single-colour logo SVG, in place.

Keeps only the viewBox, the path outlines and the brand fill; drops editor
metadata, namespaces and pixel width/height so the SVG scales to its box.
Coordinates are rounded to 1 decimal, which is well under a pixel at the
sizes we display and cuts the file by about a third.

Run after re-exporting or re-cropping a logo in Inkscape, e.g.

    python3 scripts/clean-logo-svg.py static/images/snowgrass-materials.svg
"""

import re
import sys

FILL = "#4a4b19"
LABEL = "Snowgrass Materials"


def clean(text):
    view_box = re.search(r'viewBox="([^"]+)"', text)
    if not view_box:
        raise SystemExit("no viewBox found — is this an SVG?")
    paths = []
    for path in re.findall(r"<path\b.*?/>", text, re.S):
        d = re.search(r'\sd="([^"]*)"', path)
        if not d:
            continue
        d = re.sub(
            r"-?\d*\.\d+(?![\de])",
            lambda m: ("%.1f" % float(m.group())).rstrip("0").rstrip("."),
            d.group(1),
        )
        d = re.sub(r"\s+", " ", d).strip()
        fill_rule = ' fill-rule="evenodd"' if "evenodd" in path else ""
        paths.append(f'<path{fill_rule} d="{d}"/>')
    if not paths:
        raise SystemExit("no <path> elements found — flatten text to outlines first?")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box.group(1)}"'
        f' role="img" aria-label="{LABEL}">'
        f'<g fill="{FILL}">{"".join(paths)}</g></svg>\n'
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    target = sys.argv[1]
    before = open(target).read()
    after = clean(before)
    open(target, "w").write(after)
    print(f"{target}: {len(before)} -> {len(after)} bytes")
