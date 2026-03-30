"""
Visualize the 6 slot positions of Centrifuge-2.

Top-down view (x = forward/back, y = left/right).
Each slot arrow shows the gripper orientation based on the r value.
"""

import math
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — saves file without opening a window
import matplotlib.pyplot as plt
import numpy as np

# Centrifuge-2 slot positions: [x, y, z, r]
slots = {
    1: [214, -77, 82, 20],
    2: [228, -54, 82, 80],
    3: [254, -54, 82, 140],
    4: [268, -77, 82, 20],
    5: [254, -100, 82, 80],
    6: [228, -100, 82, 140],
}

CENTER_X = 241
CENTER_Y = -77
RADIUS = 27
ARROW_LEN = 10  # length of gripper orientation arrow

fig, ax = plt.subplots(figsize=(8, 8))

# Draw centrifuge circle
circle = plt.Circle((CENTER_X, CENTER_Y), RADIUS, color="lightgray", fill=True, zorder=1)
ax.add_patch(circle)
circle_edge = plt.Circle((CENTER_X, CENTER_Y), RADIUS, color="gray", fill=False, linewidth=2, zorder=2)
ax.add_patch(circle_edge)
ax.plot(CENTER_X, CENTER_Y, "k+", markersize=12, markeredgewidth=2, zorder=3)
ax.annotate("center\n[241, -77]", xy=(CENTER_X, CENTER_Y),
            xytext=(CENTER_X + 3, CENTER_Y + 5), fontsize=8, color="gray")

colors = plt.cm.tab10.colors

for slot_num, (x, y, z, r) in slots.items():
    color = colors[slot_num - 1]

    # Slot marker
    ax.plot(x, y, "o", markersize=18, color=color, zorder=4)
    ax.text(x, y, str(slot_num), ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=5)

    # Gripper orientation arrow (r is degrees, 0° = pointing in +x direction)
    r_rad = math.radians(r)
    dx = ARROW_LEN * math.cos(r_rad)
    dy = ARROW_LEN * math.sin(r_rad)
    ax.annotate("", xy=(x + dx, y + dy), xytext=(x - dx, y - dy),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.8), zorder=5)

    # Coordinate label
    label = f"  Slot {slot_num}\n  [{x}, {y}, {z}]\n  r={r}°"
    offset_x = 14 if x >= CENTER_X else -14
    offset_y = 6 if y >= CENTER_Y else -6
    ax.annotate(label, xy=(x, y), xytext=(x + offset_x, y + offset_y),
                fontsize=8, color=color, va="center",
                arrowprops=dict(arrowstyle="-", color=color, lw=0.8))

# Axis labels and formatting
ax.set_xlabel("x (mm)", fontsize=12)
ax.set_ylabel("y (mm)", fontsize=12)
ax.set_title("Centrifuge-2 — Top-down view of 6 slots\n"
             "Arrows show gripper orientation (r angle)", fontsize=13)
ax.set_aspect("equal")
ax.grid(True, linestyle="--", alpha=0.4)

margin = 55
ax.set_xlim(CENTER_X - RADIUS - margin, CENTER_X + RADIUS + margin)
ax.set_ylim(CENTER_Y - RADIUS - margin, CENTER_Y + RADIUS + margin)

plt.tight_layout()
plt.savefig("centrifuge2_slots.png", dpi=150)
print("Saved: centrifuge2_slots.png")
plt.show()
