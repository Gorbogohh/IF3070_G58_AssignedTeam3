import json
import random
import string
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterator, Optional

Horizontal: str
Vertical: str

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
    x: int              # posisi x kendaraan dalam kapal (Posisi dimulai dari pojok kiri bawah)
    y: int              # posisi y kendaraan dalam kapal
    orientation: str    # orientasi kendaraan (vertikal atau horizontal)


State = Dict[str, Optional[Placement]]

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
