import json
import random
import string
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterator, Optional

@dataclass(frozen=True)
class Vehicle:
    id: str       # id kendaraan
    w: int        # width
    l: int        # length
    fee: int      # ShippingFee
    weight: int   # berat
    eta: int      # sisa hari
