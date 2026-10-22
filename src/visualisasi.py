import json
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from fondasi import Problem, footprint

OUT = "../output"
SEEDS = (1, 3, 5)

problem = Problem.from_json("data.json")
ship = problem.ship
cmap = plt.get_cmap("tab20")


def load(seed):
    with open(f"{OUT}/result {seed}.json", encoding="utf-8") as f:
        return json.load(f)


def draw_state(ax, state, title, value):
    ax.set_xlim(0, ship.w)
    ax.set_ylim(ship.l, 0)                   
    ax.set_aspect("equal")
    ax.set_xticks(range(ship.w + 1))
    ax.set_yticks(range(ship.l + 1))
    ax.tick_params(labelsize=6)
    ax.grid(True, linewidth=0.3)
    ax.add_patch(Rectangle((0, 0), ship.w, ship.l, fill=False, linewidth=2))

    outside = []
    for vid, p in state.items():
        if p is None:
            outside.append(vid)
            continue
        sx, sy = footprint(problem.vehicles[vid], p["orientation"])
        color = cmap(problem.ids.index(vid) % 20)
        ax.add_patch(Rectangle((p["x"], p["y"]), sx, sy,
                               facecolor=color, edgecolor="black"))
        ax.text(p["x"] + sx / 2, p["y"] + sy / 2, vid,
                ha="center", va="center", fontsize=7)

    ax.set_title(f"{title}\nValue = {value}", fontsize=10)
    ax.set_xlabel("Di luar: " + textwrap.fill(", ".join(outside) or "-", 38), fontsize=7)


# Menunjukkan state awal dan akhir pada tiap eksperimen
for seed in SEEDS:
    d = load(seed)
    fig, axes = plt.subplots(1, 2, figsize=(9, 10))
    draw_state(axes[0], d["initial_state"], "State awal", d["initial_value"])
    draw_state(axes[1], d["final_state"], "State akhir", d["final_value"])
    fig.suptitle(f"Hill-climbing with Sideways Move (seed {seed})")
    fig.tight_layout()
    fig.savefig(f"{OUT}/HC_state_seed{seed}.png", dpi=150)
    plt.close(fig)

# Nilai objektif dalam tiap iterasi
fig, ax = plt.subplots(figsize=(8, 5))
for seed in SEEDS:
    d = load(seed)
    ax.plot(range(len(d["history"])), d["history"],
            drawstyle="steps-post", label=f"seed {seed}")
ax.set_xlabel("Iterasi")
ax.set_ylabel("Nilai Objektif (Shipping Fee)")
ax.set_title(f"Hill-climbing with Sideways Move (max sideways = {d['max_sideways']})")
ax.grid(True, linewidth=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(f"{OUT}/HC_objective.png", dpi=150)
plt.close(fig)
