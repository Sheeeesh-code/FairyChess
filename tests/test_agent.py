"""Tests for the move generator and the search."""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import get_legal_moves, studentAgent
from play import apply_move, random_board


def lone(name, pos, colour="white"):
    """A single piece plus the two kings parked in opposite corners."""
    return [(name, colour, pos), ("King", "white", (7, 7)), ("King", "black", (0, 0))]


def moves_of(board, pos, colour="white"):
    return {m[1] for m in get_legal_moves(board, colour) if m[0] == pos}


# ---------------------------------------------------------------- move generation

@pytest.mark.parametrize("name, pos, count", [
    ("Rook", (3, 3), 14),
    ("Bishop", (3, 3), 13),
    ("Knight", (3, 3), 8),
    ("Squire", (3, 3), 8),
    ("Combatant", (3, 3), 4),
    ("Knight", (0, 7), 2),
])
def test_move_counts_on_open_board(name, pos, count):
    board = [("King", "white", (7, 0)), ("King", "black", (7, 7)), (name, "white", pos)]
    assert len(moves_of(board, pos)) == count


def test_squire_moves_are_manhattan_distance_two():
    board = [("King", "white", (7, 0)), ("King", "black", (7, 7)), ("Squire", "white", (3, 3))]
    assert moves_of(board, (3, 3)) == {(5, 3), (1, 3), (3, 5), (3, 1), (4, 4), (2, 2), (4, 2), (2, 4)}


def test_king_in_corner_has_three_moves():
    board = [("King", "white", (0, 0)), ("King", "black", (7, 7))]
    assert moves_of(board, (0, 0)) == {(0, 1), (1, 0), (1, 1)}


def test_sliders_stop_at_pieces():
    board = [("King", "white", (7, 7)), ("King", "black", (6, 0)),
             ("Rook", "white", (0, 0)), ("Combatant", "white", (0, 3)), ("Combatant", "black", (3, 0))]
    targets = moves_of(board, (0, 0))
    assert targets == {(0, 1), (0, 2), (1, 0), (2, 0), (3, 0)}  # own piece blocks, enemy can be taken


def test_combatant_captures_only_diagonally_and_walks_only_orthogonally():
    board = [("King", "white", (7, 7)), ("King", "black", (7, 0)),
             ("Combatant", "white", (3, 3)),
             ("Rook", "black", (2, 3)),      # straight ahead: blocked, not capturable
             ("Rook", "black", (4, 4))]      # diagonal: capturable
    assert moves_of(board, (3, 3)) == {(3, 2), (3, 4), (4, 3), (4, 4)}


def test_moves_are_sorted_and_deterministic():
    board = random_board(random.Random(5), 6)
    moves = get_legal_moves(board, "white")
    assert moves == sorted(moves)
    assert moves == get_legal_moves(list(reversed(board)), "white")


def test_cannot_capture_own_piece():
    board = lone("Rook", (7, 0)) + [("Combatant", "white", (7, 3))]
    assert (7, 3) not in moves_of(board, (7, 0))


# ---------------------------------------------------------------- search

def test_takes_the_king_when_possible():
    board = [("King", "white", (7, 7)), ("King", "black", (0, 7)), ("Rook", "white", (0, 0))]
    assert studentAgent(board) == ((0, 0), (0, 7))


def test_wins_a_free_piece():
    board = [("King", "white", (7, 7)), ("King", "black", (3, 3)),
             ("Rook", "white", (0, 0)), ("Rook", "black", (0, 5))]
    assert studentAgent(board) == ((0, 0), (0, 5))


def test_does_not_leave_a_piece_en_prise():
    # The black combatant attacks the rook diagonally; the agent must move it out of danger.
    board = [("King", "white", (7, 7)), ("King", "black", (0, 0)),
             ("Rook", "white", (4, 4)), ("Combatant", "black", (3, 3))]
    after = apply_move(board, studentAgent(board))
    white_squares = {pos for _, colour, pos in after if colour == "white"}
    replies = {to for _, to in get_legal_moves(after, "black")}
    assert not (replies & white_squares)


def test_survives_positions_that_reduce_to_two_kings():
    # Every capture sequence ends with only kings left; the search must not crash.
    board = [("King", "white", (0, 0)), ("King", "black", (7, 7)),
             ("Combatant", "white", (3, 3)), ("Combatant", "black", (4, 4))]
    move = studentAgent(board)
    assert move in get_legal_moves(board, "white")


@pytest.mark.parametrize("seed", range(6))
def test_returns_a_legal_move_on_random_positions(seed):
    board = random_board(random.Random(seed), 4)
    assert studentAgent(board) in get_legal_moves(board, "white")


def test_is_deterministic():
    board = random_board(random.Random(11), 4)
    assert studentAgent(board) == studentAgent(list(board))
