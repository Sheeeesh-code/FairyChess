# Fairy Chess: Alpha-Beta Agent

A pure-Python adversarial search agent for a chess variant with custom pieces. Given a position, it returns a good
move for white using minimax with alpha-beta pruning, iterative deepening, a transposition table and capture-first
move ordering.

## The game

An 8x8 board, two players, and the goal is to capture the enemy king (there is no check or checkmate). A position is a
list of `(name, colour, (row, col))` tuples.

| Piece | Movement |
|---|---|
| King | One square in any direction |
| Rook | Any number of squares vertically or horizontally, stopped by the first piece it meets |
| Bishop | Any number of squares diagonally, stopped by the first piece it meets |
| Knight | "L" shape (2x1 or 1x2), jumps over pieces |
| Squire | Jumps 2 squares orthogonally, or 1 square diagonally |
| Combatant | Moves 1 square orthogonally onto an empty square, and captures 1 square diagonally |

A piece can never land on a square occupied by its own colour.

## How the agent works

Everything is in [`agent.py`](agent.py), as two functions that work directly on the list-of-tuples board:

- `get_legal_moves(board, color)` generates the moves of one colour. The list is sorted, so the output (and therefore
  the search) is deterministic.
- `studentAgent(board)` runs the search for white and returns `((from_row, from_col), (to_row, to_col))`.

Search details:

- **Alpha-beta pruning** over a plain minimax tree.
- **Iterative deepening** from depth 3 to depth 6: each depth gives a complete move, and a forced win or loss stops
  the deepening early.
- **Node budget** of 200,000 nodes per depth. If a depth runs out of budget, its unfinished result is discarded and
  the move from the last completed depth is played, so the agent's thinking time stays bounded.
- **Transposition table** keyed on the (sorted) position, the remaining depth and the side to move. Only values that are
  exact for their search window are stored, since a value produced after a cutoff is only a bound.
- **Move ordering**: captures first, the most valuable victim first, which makes the pruning much more effective.
- **Evaluation**: material balance with weights King 10000, Rook 5, Squire 4, Bishop 3, Knight 3, Combatant 2.
- **Terminal scores**: capturing the king scores +/-100000, minus the distance from the root, so the agent prefers the
  fastest win and the slowest loss. Two lone kings score 0.

The agent always plays white. To use it for black, swap the colours of the board before the call. The rules are
colour-symmetric, so the returned move is valid for black on the real board (that is what [`play.py`](play.py) does).

## Usage

```bash
python play.py                          # agent (white) vs a random mover, random start position
python play.py --seed 3 --pieces 5      # another start, 5 extra pieces per side
python play.py --self-play              # agent vs agent
python benchmark.py                     # regenerate results/benchmark.md
python -m pytest tests                  # 23 tests
```

```python
from agent import studentAgent

board = [("King", "white", (7, 0)), ("King", "black", (0, 7)), ("Knight", "white", (3, 4))]
print(studentAgent(board))              # ((from_row, from_col), (to_row, to_col))
```

No dependency is needed to run the agent (`pytest` is only used for the tests).

## Results

Measured on one machine, on random positions (kings plus a number of random pieces):

| pieces on board | mean time per move (s) | max (s) |
|---|---|---|
| 6 | 0.32 | 0.92 |
| 10 | 0.64 | 1.67 |
| 14 | 1.41 | 5.48 |
| 18 | 0.68 | 4.58 |

Against a random mover (20 games, 4 extra pieces per side, colours alternating, 80 plies maximum): **20 wins, 0
losses, 0 draws**. A random opponent is a weak baseline, so this only shows that the agent plays sensibly, not that it
is strong.

Times vary a lot from one position to the next (the node budget caps the worst case), so the means are indicative only.

## Limitations and ideas

- The evaluation only counts material. Mobility, king safety or piece-square tables would help in quiet positions.
- Positions are copied at every node (`apply_move` builds a new list). A make/undo scheme on a mutable board would
  be faster, at the cost of a more complicated code.
- Mate scores stored in the transposition table are measured from the root of the iteration that produced them, so
  a stored win can be reported one or two plies off in a later iteration.
- There is no time-based cutoff, only a node budget.

## Notes

An AI assistant (Claude) was used to review the search code and fix two bugs (the transposition table storing
non-exact values, and an unfinished iteration overwriting the last completed one), and to write the README, the play
script, the benchmark and the tests.
