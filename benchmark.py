"""Thinking time per position and win rate against a random mover.

    python benchmark.py            # writes results/benchmark.md
"""

import random
import statistics
import time
from pathlib import Path

from agent import get_legal_moves, studentAgent
from play import agent_move, play, random_board

OUT = Path(__file__).parent / "results" / "benchmark.md"


def timing(positions=8):
    rows = ["| pieces on board | mean time (s) | max time (s) |", "|---|---|---|"]
    for per_side in (2, 4, 6, 8):
        rng = random.Random(100 + per_side)
        times = []
        for _ in range(positions):
            board = random_board(rng, per_side)
            t = time.perf_counter()
            studentAgent(board)
            times.append(time.perf_counter() - t)
        rows.append(f"| {2 * per_side + 2} | {statistics.mean(times):.2f} | {max(times):.2f} |")
        print(rows[-1], flush=True)
    return rows


def versus_random(games=20, per_side=4, plies=80):
    results = {"agent": 0, "random": 0, "draw": 0}
    for seed in range(games):
        rng = random.Random(seed)
        start = random_board(rng, per_side)
        # Agent plays white on even seeds, black on odd seeds (same start, colours swapped).
        agent_white = seed % 2 == 0
        rand = lambda board, colour: rng.choice(get_legal_moves(board, colour))
        white, black = (agent_move, rand) if agent_white else (rand, agent_move)
        winner = play(start, white, black, plies, verbose=False)
        key = "draw" if winner == "draw" else "agent" if (winner == "white") == agent_white else "random"
        results[key] += 1
        print(f"game {seed}: {key}", flush=True)
    return results


if __name__ == "__main__":
    t_rows = timing()
    r = versus_random()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        "## Thinking time per move (random positions, one machine)\n\n" + "\n".join(t_rows)
        + f"\n\n## Agent vs random mover (20 games, 4 extra pieces per side, 80 plies max)\n\n"
        f"| agent wins | random wins | draws |\n|---|---|---|\n| {r['agent']} | {r['random']} | {r['draw']} |\n"
        "\nGames that reach 80 plies are adjudicated on material. Colours alternate between games.\n")
    print(OUT.read_text())
