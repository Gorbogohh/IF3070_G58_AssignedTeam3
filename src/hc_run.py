import csv
import json
import os
import random
from fondasi import Problem
from HC_sideways import hill_climbing

# Mengirim file output ke folder /output
OUT = "../output"                 # folder output di root repo
os.makedirs(OUT, exist_ok=True)   # buat folder jika belum ada

# Mengubah data dari .json menjadi dictionary
def state_to_dict(state):
    return {vid: (None if p is None else {"x": p.x, "y": p.y, "orientation": p.orientation})
            for vid, p in state.items()}

# Membaca file data.json
problem = Problem.from_json("hc.data.json")
rows = []

# Melakukan search terhadap 3 seed yang dipilih dan memberi hasilnya
for seed in (1, 3, 5):
    r = hill_climbing(problem, random.Random(seed), max_sideways=30)
    print("seed", seed, "; Value awal: ", r.initial_value, "; Value akhir:", r.final_value,
          "; jumlah iterasi:", r.iterations, "; durasi search:", round(r.duration, 2), "s",
          "; berhenti di:", r.extra["stop_reason"])

    # simpan hasil dalam file .json
    with open(f"{OUT}/result {seed}.json", "w", encoding="utf-8") as f:
        json.dump({
            "seed": seed,
            "max_sideways": 30,
            "initial_value": r.initial_value,
            "final_value": r.final_value,
            "iterations": r.iterations,
            "duration_sec": r.duration,
            "initial_state": state_to_dict(r.initial_state),
            "final_state": state_to_dict(r.final_state),
            "history": r.history,
            "extra": r.extra,
        }, f)

    # kumpulkan satu baris untuk tabel ringkasan
    rows.append({"seed": seed, "initial_value": r.initial_value,
                 "final_value": r.final_value, "iterations": r.iterations,
                 "duration_sec": round(r.duration, 3),
                 "stop_reason": r.extra["stop_reason"]})

