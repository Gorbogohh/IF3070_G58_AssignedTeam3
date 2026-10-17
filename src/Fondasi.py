import json
import random
import string
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterator, Optional

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
