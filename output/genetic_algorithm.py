import json
import random
import time
import copy
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterator, Optional
import matplotlib.pyplot as plt

# =====================================================================
# 1. STRUKTUR DATA & KELAS PROBLEM
# =====================================================================
Horizontal = "Horizontal"
Vertical = "Vertical"

@dataclass(frozen=True)
class Vehicle:
    id: str
    w: int
    l: int
    fee: int
    weight: int
    eta: int

@dataclass(frozen=True)
class Ship:
    w: int
    l: int
    max_capacity: int

@dataclass(frozen=True)
class Placement:
    x: int
    y: int
    orientation: str

State = Dict[str, Optional[Placement]]

def flip(orientation: str) -> str:
    return Horizontal if orientation == Vertical else Vertical

def replaced(state: State, changes: Dict[str, Optional[Placement]]) -> State:
    return {**state, **changes}

def swapped(state: State, a: str, b: str) -> State:
    return replaced(state, {a: state[b], b: state[a]})

def rotated(state: State, vid: str) -> str:
    p = state[vid]
    return replaced(state, {vid: Placement(p.x, p.y, flip(p.orientation))})

def footprint(v: Vehicle, orientation: str) -> tuple[int, int]:
    return (v.w, v.l) if orientation == Vertical else (v.l, v.w)

def cells(v: Vehicle, p: Placement) -> list[tuple[int, int]]:
    sx, sy = footprint(v, p.orientation)
    return [(p.x + i, p.y + j) for i in range(sx) for j in range(sy)]

class Problem:
    def __init__(self, ship: Ship, vehicles: list[Vehicle]):
        self.ship = ship
        self.vehicles = {v.id: v for v in vehicles}
        self.ids = list(self.vehicles)

    @classmethod
    def from_json(cls, path: str) -> "Problem":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        s = d["ship"]
        ship = Ship(s["w"], s["l"], s["max_capacity"])
        return cls(ship, [Vehicle(**v) for v in d["vehicles"]])

    def is_valid(self, state: State) -> bool:
        occupied = set()
        total_weight = 0
        for vid, p in state.items():
            if p is None:
                continue
            v = self.vehicles[vid]
            total_weight += v.weight
            for cx, cy in cells(v, p):
                if not (0 <= cx < self.ship.w and 0 <= cy < self.ship.l):
                    return False              
                if (cx, cy) in occupied:
                    return False              
                occupied.add((cx, cy))
        return total_weight <= self.ship.max_capacity

    def objective(self, state: State) -> int:
        return sum(self.vehicles[vid].fee for vid, p in state.items() if p is not None)

    def random_placement(self, vid: str, rng: random.Random, orientation: Optional[str] = None) -> Optional[Placement]:
        v = self.vehicles[vid]
        o = orientation or rng.choice([Horizontal, Vertical])
        sx, sy = footprint(v, o)
        if sx > self.ship.w or sy > self.ship.l:
            return None
        return Placement(rng.randint(0, self.ship.w - sx), rng.randint(0, self.ship.l - sy), o)

    def random_state(self, rng: random.Random, attempts: int = 20) -> State:
        state: State = {vid: None for vid in self.ids}
        order = self.ids[:]
        rng.shuffle(order)
        for vid in order:
            if rng.random() < 0.5:      
                continue
            for _ in range(attempts):
                cand = self.random_placement(vid, rng)
                if cand is None:
                    continue
                state[vid] = cand
                if self.is_valid(state):
                    break
                state[vid] = None
        return state

    def all_neighbors(self, state: State) -> Iterator[State]:
        W, L = self.ship.w, self.ship.l
        for a, b in combinations(self.ids, 2):
            if state[a] is not None or state[b] is not None:
                yield swapped(state, a, b)
        for vid in self.ids:
            cur = state[vid]
            for o in ([cur.orientation] if cur else [Horizontal, Vertical]):
                sx, sy = footprint(self.vehicles[vid], o)
                for x in range(W - sx + 1):
                    for y in range(L - sy + 1):
                        p = Placement(x, y, o)
                        if p != cur:
                            yield replaced(state, {vid: p})
            if cur:
                yield rotated(state, vid)


# =====================================================================
# 2. KELAS GENETIC ALGORITHM
# =====================================================================
class GeneticAlgorithm:
    def __init__(self, pop_size, max_iter, prob, rng):
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.prob = prob
        self.rng = rng
        self.crossover_rate = 0.8
        self.mutation_rate = 0.2

    def run(self):
        start_time = time.time()
        population = [
            self.prob.random_state(self.rng)
            for _ in range(self.pop_size)
        ]

        initial_state = copy.deepcopy(population[0])

        candidate_peak = copy.deepcopy(
            max(population, key=self.prob.objective)
        )
        best_fitness = self.prob.objective(candidate_peak)
        max_fitness_history = []
        avg_fitness_history = []
        

        for _ in range(self.max_iter):
            fitnesses = [self.prob.objective(ind) for ind in population]
            
            cur_max = max(fitnesses)
            cur_avg = sum(fitnesses) / len(fitnesses)
            max_fitness_history.append(cur_max)
            avg_fitness_history.append(cur_avg)

            best_idx = fitnesses.index(cur_max)
            if cur_max > best_fitness:
                best_fitness = cur_max
                candidate_peak = copy.deepcopy(population[best_idx])

            new_population = [copy.deepcopy(population[best_idx])]
            
            while len(new_population) < self.pop_size:
                p1 = population[self.rng.choice(range(len(population)))]
                p2 = population[self.rng.choice(range(len(population)))]

                c1, c2 = copy.deepcopy(p1), copy.deepcopy(p2)
                
                if self.rng.random() < self.crossover_rate:
                    for vid in self.prob.ids:
                        if self.rng.random() < 0.5:
                            c1 = replaced(c1, {vid: p2.get(vid)})
                            c2 = replaced(c2, {vid: p1.get(vid)})

                if self.rng.random() < self.mutation_rate:
                    nbs = list(self.prob.all_neighbors(c1))
                    if nbs: c1 = self.rng.choice(nbs)
                
                if self.rng.random() < self.mutation_rate:
                    nbs = list(self.prob.all_neighbors(c2))
                    if nbs: c2 = self.rng.choice(nbs)

                new_population.append(c1)
                if len(new_population) < self.pop_size:
                    new_population.append(c2)

            population = new_population

        return {
            "initial_state": initial_state,
            "final_state": candidate_peak,
            "candidate_peak": candidate_peak,
            "best_fitness": best_fitness,
            "max_fitness_history": max_fitness_history,
            "avg_fitness_history": avg_fitness_history,
            "execution_time": time.time() - start_time
        }


# =====================================================================
# 3. EKSEKUSI UTAMA
# =====================================================================

if __name__ == "__main__":
    rng = random.Random(42)
    prob = Problem.from_json("data.json")

    pop_size = 5
    max_iter = 50

    print("Menjalankan Genetic Algorithm...")
    print(f"Ukuran populasi: {pop_size}")
    print(f"Jumlah iterasi: {max_iter}")

    ga = GeneticAlgorithm(
        pop_size=pop_size,
        max_iter=max_iter,
        prob=prob,
        rng=rng
    )

    result = ga.run()

    print("\nState Awal:")
    for vid, placement in result["initial_state"].items():
        print(f"Kendaraan {vid}: {placement}")

    print("\nGenetic Algorithm Selesai!")
    print(f"Best Shipping Fee: {result['best_fitness']}")
    print(f"Durasi Eksekusi: {result['execution_time']:.2f} detik")

    print("\nState Akhir Penempatan Kendaraan:")
    for vid, placement in result["final_state"].items():
        if placement is not None:
            print(
                f"Kendaraan {vid}: "
                f"x={placement.x}, y={placement.y}, "
                f"orientasi={placement.orientation}"
            )
        else:
            print(f"Kendaraan {vid}: Tidak dimuat (None)")

    plt.figure(figsize=(9, 5))
    plt.plot(
        range(1, len(result["max_fitness_history"]) + 1),
        result["max_fitness_history"],
        label="Max Fitness",
        color="#386641",
        linewidth=2
    )
    plt.plot(
        range(1, len(result["avg_fitness_history"]) + 1),
        result["avg_fitness_history"],
        label="Average Fitness",
        color="#386641",
        linestyle="--",
        linewidth=2
    )

    plt.xlabel("Iterasi / Generasi")
    plt.ylabel("Objective Function (Shipping Fee)")
    plt.title("Eksperimen Genetic Algorithm")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
