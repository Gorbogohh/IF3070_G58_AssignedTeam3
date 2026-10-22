from dataclasses import dataclass, field
from typing import Any, Dict, List

from foundation import State


@dataclass
class SearchResult:
    initial_state: State
    final_state: State
    initial_value: int
    final_value: int
    history: List[float]          # nilai objective per iterasi (untuk plot)
    duration: float               # detik
    iterations: int
    extra: Dict[str, Any] = field(default_factory=dict)  # data khusus algoritma




    