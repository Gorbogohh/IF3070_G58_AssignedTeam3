import json
import random
import string
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterator, Optional

Horizontal = "Horizontal"
Vertical = "Vertical"

@dataclass(frozen=True)
class Vehicle:
    id: str            # id kendaraan
    w: int             # width kendaraan
    l: int             # length kendaraan
    fee: int           # Tarif pengiriman kendaraan
    weight: int        # berat kendaraan 
    eta: int           # perkiraan waktu datangnya kendaraan


@dataclass(frozen=True)
class Ship:
    w: int              # width kapal            
    l: int              # length kapal
    max_capacity: int   # Kapasitas berat maksimum kapal


@dataclass(frozen=True)
class Placement:
    x: int              # posisi x kendaraan dalam kapal 
    y: int              # posisi y kendaraan dalam kapal
    orientation: str    # orientasi kendaraan (vertikal atau horizontal)


State = Dict[str, Optional[Placement]]         # dictionary

# Fungsi

# Fungsi untuk mengubah orientasi kendaraan (Dari vertikal ke horizontal, dan sebaliknya)
def flip(orientation: str) -> str:
    return Horizontal if orientation == Vertical else Vertical

# Membuat salinan state untuk perubahan placement satu kendaraan
def replaced(state: State, changes: Dict[str, Optional[Placement]]) -> State:
    return {**state, **changes}

# Membuat salinan satet untuk penukaran posisi 2 kendaraan
def swapped(state: State, a: str, b: str) -> State:
    return replaced(state, {a: state[b], b: state[a]})

# Membuat salinan state untuk perubahan orientasi kendaraan
def rotated(state: State, vid: str) -> State:
    p = state[vid]
    return replaced(state, {vid: Placement(p.x, p.y, flip(p.orientation))})

# Melihat ukuran kendaraan dalam x dan y sesuai orientation (Contoh: vehicle w=3, l=4 menghasilkan (3, 4) jika Vertical dan (4, 3) jika Horizontal)
def footprint(v: Vehicle, orientation: str) -> tuple[int, int]:
    return (v.w, v.l) if orientation == Vertical else (v.l, v.w)

# Mendaftar semua grid yang ditempati kendaraan
def cells(v: Vehicle, p: Placement) -> list[tuple[int, int]]:
    sx, sy = footprint(v, p.orientation)
    return [(p.x + i, p.y + j) for i in range(sx) for j in range(sy)]

# Constraint dan objective

# Menyimpan data kapal dan kendaraan berdasarkan id
class Problem:
    def __init__(self, ship: Ship, vehicles: list[Vehicle]):
        self.ship = ship
        self.vehicles = {v.id: v for v in vehicles}
        self.ids = list(self.vehicles)

# Membaca file .json 
    @classmethod
    def from_json(cls, path: str) -> "Problem":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        s = d["ship"]
        ship = Ship(s["w"], s["l"], s["max_capacity"])
        return cls(ship, [Vehicle(**v) for v in d["vehicles"]])

# Melakukan cek tentang apakah penataan kendaraan di dalam kapal diperbolehkan atau tidak
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

# Menghitung nilai penataan (Total fee)
    def objective(self, state: State) -> int:
        return sum(self.vehicles[vid].fee for vid, p in state.items() if p is not None)

# Menghitung total weight total muatan
    def total_weight(self, state: State) -> int:
        return sum(self.vehicles[vid].weight for vid, p in state.items() if p is not None)

# Membuat random initial state (belum memeriksa kendaraan yang tumpang tindih atau total berat))
    def random_placement(self, vid: str, rng: random.Random,
                         orientation: Optional[str] = None) -> Optional[Placement]:
        v = self.vehicles[vid]
        o = orientation or rng.choice([Horizontal, Vertical])
        sx, sy = footprint(v, o)
        if sx > self.ship.w or sy > self.ship.l:
            return None
        return Placement(rng.randint(0, self.ship.w - sx), rng.randint(0, self.ship.l - sy), o)

# Membuat initial state yang valid
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

# Mengembalikan satu neighbor valid yang dipilih secara acak
    def random_neighbor(self, state: State, rng: random.Random, tries: int = 50) -> Optional[State]:
        moves = [self._random_swap, self._random_move, self._random_rotate]
        for _ in range(tries):
            nb = rng.choice(moves)(state, rng)
            if nb is not None and self.is_valid(nb):
                return nb
        return None

# Langkah neighbor untuk menukar posisi dua kendaraan
    def _random_swap(self, state: State, rng: random.Random) -> Optional[State]:
        a, b = rng.sample(self.ids, 2)
        return None if state[a] is None and state[b] is None else swapped(state, a, b)

# Langkah neighbor untuk memindahkan posisi satu kendaraan ke posisi lain
    def _random_move(self, state: State, rng: random.Random) -> Optional[State]:
        vid = rng.choice(self.ids)
        cur = state[vid]
        new = self.random_placement(vid, rng, cur.orientation if cur else None)
        return None if new is None or new == cur else replaced(state, {vid: new})

# Langkah neighbor untuk mengubah orientasi kendaraan
    def _random_rotate(self, state: State, rng: random.Random) -> Optional[State]:
        vid = rng.choice(self.ids)
        # kendaraan di luar: rotasi tidak berarti
        return None if state[vid] is None else rotated(state, vid)

#####

# Menghasilkan semua kandidat dari langkah neighbor (belum cek validasi)
    def _candidates(self, state: State) -> Iterator[State]:
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

# Mengembalikan semua neighbor yang valid dari _candidates
    def all_neighbors(self, state: State) -> Iterator[State]:
        return (nb for nb in self._candidates(state) if self.is_valid(nb))

