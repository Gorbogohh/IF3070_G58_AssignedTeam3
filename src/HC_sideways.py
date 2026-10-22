import random
import time
from typing import Optional

from foundation import Problem, State
from search import SearchResult


def hill_climbing(problem: Problem, rng: random.Random, max_sideways: int = 0,
                  max_iterations: int = 10_000,
                  initial: Optional[State] = None) -> SearchResult:
    state = initial if initial is not None else problem.random_state(rng)
    initial_state = state
    value = problem.objective(state)
    history = [value]
    sideways_streak = 0          # sideways move beruntun sejak perbaikan terakhir
    sideways_total = 0
    stop_reason = "max_iterations"
    iteration = 0

    t0 = time.perf_counter()
    while iteration < max_iterations:
        scored = [(problem.objective(nb), nb) for nb in problem.all_neighbors(state)]
        if not scored:
            stop_reason = "no_neighbor"
            break
        best_value = max(v for v, _ in scored)
        best_neighbors = [nb for v, nb in scored if v == best_value]

        if best_value > value:                                   # naik
            sideways_streak = 0
        elif best_value == value and sideways_streak < max_sideways:   # sideways
            sideways_streak += 1
            sideways_total += 1
        else:                                                    # berhenti
            stop_reason = ("max_sideways" if best_value == value and max_sideways > 0
                           else "local_optimum")
            break


        state = rng.choice(best_neighbors)    # tie-break acak
        value = best_value
        iteration += 1
        history.append(value)
    duration = time.perf_counter() - t0


    return SearchResult(initial_state, state, history[0], value, history, duration,
                        iteration, {"stop_reason": stop_reason,
                                    "max_sideways": max_sideways,
                                    "sideways_total": sideways_total})

