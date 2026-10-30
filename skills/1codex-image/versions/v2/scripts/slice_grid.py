"""Cut a transparent icon sheet laid out as a grid into one PNG per icon.

Icons on a generated sheet often cross the even grid lines, so cutting by the
grid clips them. Each opaque piece is assigned to the cell holding its center,
and each icon is cropped to the union of its pieces.

Run: uv run -q --with pillow --with numpy --with scipy python -I slice_grid.py SHEET.png COLS ROWS OUT_PREFIX
"""

import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def main() -> None:
    sheet, cols, rows, prefix = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    image = Image.open(sheet).convert("RGBA")
    width, height = image.size
    labels, _ = ndimage.label(np.array(image)[..., 3] > 10)
    boxes: dict[int, list[int]] = {}
    for index, region in enumerate(ndimage.find_objects(labels), 1):
        cy, cx = ndimage.center_of_mass(labels == index)
        cell = int(cy // (height / rows)) * cols + int(cx // (width / cols))
        x0, y0, x1, y1 = region[1].start, region[0].start, region[1].stop, region[0].stop
        box = boxes.setdefault(cell, [x0, y0, x1, y1])
        boxes[cell] = [min(box[0], x0), min(box[1], y0), max(box[2], x1), max(box[3], y1)]
    for cell, box in sorted(boxes.items()):
        image.crop(tuple(box)).save(f"{prefix}-{cell + 1:02d}.png")
    print(f"{len(boxes)} icons from a {cols}x{rows} grid")


if __name__ == "__main__":
    main()
