"""Play the alpha-beta agent against a random mover (or against itself).

    python play.py                      # agent (white) vs random, random start, seed 0
    python play.py --seed 3 --pieces 5  # 5 extra pieces per side
    python play.py --self-play          # agent vs agent

`studentAgent` always plays white. To let it play black, the colours are swapped
before the call: the rules are colour-symmetric (no pawn direction), so the
returned move is valid for black on the real board.
"""

import argparse
import random

from agent import get_legal_moves, studentAgent

PIECES = ["Rook", "Bishop", "Knight", "Squire", "Combatant"]
SYMBOLS = {"King": "K", "Rook": "R", "Bishop": "B", "Knight": "N", "Squire": "S", "Combatant": "C"}
VALUES = {"King": 0, "Rook": 5, "Bishop": 3, "Knight": 3, "Squire": 4, "Combatant": 2}


def random_board(rng, pieces_per_side):
    """Both kings plus `pieces_per_side` random pieces for each colour."""
    cells = [(r, c) for r in range(8) for c in range(8)]
    rng.shuffle(cells)
    board = [("King", "white", cells.pop()), ("King", "black", cells.pop())]
    for _ in range(pieces_per_side):
        for colour in ("white", "black"):
            board.append((rng.choice(PIECES), colour, cells.pop()))
    return board


def swap_colours(board):
    return [(n, "black" if c == "white" else "white", p) for n, c, p in board]


def apply_move(board, move):
    from_pos, to_pos = move
    return [(n, c, to_pos if p == from_pos else p)
            for n, c, p in board if p == from_pos or p != to_pos]


def material(board):
    return sum(VALUES[n] * (1 if c == "white" else -1) for n, c, _ in board)


def render(board):
    grid = [[" ."] * 8 for _ in range(8)]
    for name, colour, (r, c) in board:
        symbol = SYMBOLS[name]
        grid[r][c] = " " + (symbol if colour == "white" else symbol.lower())
    lines = ["   " + " ".join(f" {c}" for c in range(8))]
    lines += [f"{r}  " + " ".join(row) for r, row in enumerate(grid)]
    return "\n".join(lines) + "\n(UPPER = white, lower = black)"


def agent_move(board, colour):
    if colour == "white":
        return studentAgent(board)
    return studentAgent(swap_colours(board))


def play(board, white, black, max_plies=100, verbose=True):
    """`white` / `black` are callables (board, colour) -> move. Returns the winner."""
    colour = "white"
    for ply in range(max_plies):
        moves = get_legal_moves(board, colour)
        if not moves:
            return "draw"
        move = (white if colour == "white" else black)(board, colour)
        move = tuple(map(tuple, move))
        assert move in moves, f"illegal move {move} for {colour}"
        board = apply_move(board, move)
        if verbose:
            print(f"\nply {ply + 1}: {colour} {move[0]} -> {move[1]}\n{render(board)}")
        kings = {c for n, c, _ in board if n == "King"}
        if "black" not in kings:
            return "white"
        if "white" not in kings:
            return "black"
        colour = "black" if colour == "white" else "white"
    score = material(board)
    return "white" if score > 0 else "black" if score < 0 else "draw"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--pieces", type=int, default=4, help="extra pieces per side (default 4)")
    parser.add_argument("--plies", type=int, default=100, help="maximum number of half-moves")
    parser.add_argument("--self-play", action="store_true", help="agent plays both sides")
    parser.add_argument("--quiet", action="store_true", help="only print the result")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    start = random_board(rng, args.pieces)
    print(render(start))

    def random_player(board, colour):
        return rng.choice(get_legal_moves(board, colour))

    black_player = agent_move if args.self_play else random_player
    winner = play(start, agent_move, black_player, args.plies, verbose=not args.quiet)
    print(f"\nresult: {winner}")
