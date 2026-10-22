import json
import math
import random
import time
from dataclasses import asdict
from typing import Optional

from Fondasi import Problem, State, cells


def simulated_annealing(
    problem: Problem,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.995,
    min_temp: float = 0.01,
    max_iter: int = 10_000,
    stuck_patience: int = 100,
    seed: Optional[int] = None,
) -> dict:

    rng = random.Random(seed)
    start_time = time.perf_counter()

    current = problem.random_state(rng)
    current_value = problem.objective(current)
    initial_state, initial_value = current, current_value

    best, best_value = current, current_value

    temp = initial_temp
    objective_history = [current_value]   # nilai current tiap iterasi
    best_history = [best_value]           # nilai best tiap iterasi
    prob_history = []                     # (iterasi, e^(dE/T)) untuk langkah yang lebih buruk

    stuck_count = 0          # banyak kejadian 'stuck'
    no_improve = 0           # iterasi berturut-turut tanpa perbaikan best
    accepted_worse = 0       # banyak langkah buruk yang diterima
    iteration = 0

    while temp > min_temp and iteration < max_iter:
        iteration += 1

        neighbor = problem.random_neighbor(current, rng)
        if neighbor is not None:
            neighbor_value = problem.objective(neighbor)
            delta_e = neighbor_value - current_value

            if delta_e > 0:
                accept = True
            elif delta_e == 0:
                accept = True  # sideways move: probabilitas e^0 = 1
            else:
                prob = math.exp(delta_e / temp)
                prob_history.append((iteration, prob))
                accept = rng.random() < prob
                if accept:
                    accepted_worse += 1

            if accept:
                current, current_value = neighbor, neighbor_value

        # Perbarui solusi terbaik dan hitung 'stuck'
        if current_value > best_value:
            best, best_value = current, current_value
            no_improve = 0
        else:
            no_improve += 1
            if no_improve == stuck_patience:
                stuck_count += 1
                no_improve = 0

        objective_history.append(current_value)
        best_history.append(best_value)
        temp *= cooling_rate

    duration = time.perf_counter() - start_time

    return {
        "params": {
            "initial_temp": initial_temp,
            "cooling_rate": cooling_rate,
            "min_temp": min_temp,
            "max_iter": max_iter,
            "stuck_patience": stuck_patience,
            "seed": seed,
        },
        "initial_state": initial_state,
        "initial_value": initial_value,
        "final_state": best,
        "final_value": best_value,
        "last_state_value": current_value,
        "total_weight": problem.total_weight(best),
        "is_valid": problem.is_valid(best),
        "iterations": iteration,
        "duration": duration,
        "stuck_count": stuck_count,
        "accepted_worse": accepted_worse,
        "objective_history": objective_history,
        "best_history": best_history,
        "prob_history": prob_history,
    }

# Utilitas output

def state_to_dict(state: State) -> dict:
    """Mengubah state menjadi dict biasa agar bisa disimpan sebagai JSON."""
    return {vid: (asdict(p) if p is not None else None) for vid, p in state.items()}


def deck_to_text(problem: Problem, state: State) -> str:
    """Gambar geladak dalam teks. Tiap kendaraan diberi huruf/angka; '.' = kosong."""
    symbols = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    grid = [["." for _ in range(problem.ship.w)] for _ in range(problem.ship.l)]
    legend = []
    for i, (vid, p) in enumerate((v, p) for v, p in state.items() if p is not None):
        sym = symbols[i % len(symbols)]
        legend.append(f"{sym}={vid}")
        for cx, cy in cells(problem.vehicles[vid], p):
            grid[cy][cx] = sym
    # y = 0 di bawah (posisi dimulai dari pojok kiri bawah)
    rows = ["".join(r) for r in reversed(grid)]
    outside = [vid for vid, p in state.items() if p is None]
    return (
        "\n".join(rows)
        + "\nDi dalam : " + ", ".join(legend)
        + "\nDi luar  : " + (", ".join(outside) if outside else "-")
    )


def save_result(result: dict, path: str) -> None:
    """Menyimpan hasil satu run ke file JSON."""
    out = dict(result)
    out["initial_state"] = state_to_dict(result["initial_state"])
    out["final_state"] = state_to_dict(result["final_state"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

def plot_result(result: dict, path: str, title: str = "Simulated Annealing") -> None:
    """Menyimpan plot objective dan e^(dE/T) terhadap iterasi ke file PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Grafik objective function terhadap iterasi
    ax1.plot(result["objective_history"], label="Current", linewidth=1)
    ax1.plot(result["best_history"], label="Best", linewidth=1.5)
    ax1.set_xlabel("Iterasi")
    ax1.set_ylabel("Objective (total ShippingFee)")
    ax1.set_title(f"{title}: objective function terhadap iterasi")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Grafik probabilitas menerima langkah yang lebih buruk
    if result["prob_history"]:
        it, prob = zip(*result["prob_history"])
        ax2.scatter(it, prob, s=6)
    ax2.set_xlabel("Iterasi")
    ax2.set_ylabel(r"$e^{\Delta E / T}$")
    ax2.set_ylim(-0.05, 1.05)
    ax2.set_title("Probabilitas menerima langkah yang lebih buruk")
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)

