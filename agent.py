def get_legal_moves(board, color):
    """
    board: list of (name, color, pos)
    color: 'white' or 'black'
    Returns a list of moves: [ (from_pos, to_pos), ... ]
    Deterministic ordering: the returned list is sorted to avoid nondeterminism.
    """
    legal_moves = []
    board_state = {}
    for name, p_color, pos in board:
        board_state[pos] = (name, p_color)
    orthogonal_moves = [(1,0), (0,1), (-1,0), (0,-1)]
    diagonal_moves = [(1,1), (1,-1), (-1,1), (-1,-1)]
    knight_moves = [(2,-1), (2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2)]
    squire_moves = [(2,0), (-2,0), (0,-2), (0,2), (1,1),(-1,-1), (-1,1), (1,-1)]
    for pos, (piece_name, piece_color) in board_state.items():
        if piece_color != color:
            continue
        r, c = pos
        if piece_name == 'King':
            for dr, dc in orthogonal_moves + diagonal_moves:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state or board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
        elif piece_name == 'Combatant':
            for dr, dc in orthogonal_moves:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state:
                        legal_moves.append((pos, target_pos))
            for dr, dc in diagonal_moves:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos in board_state and board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
        elif piece_name == "Knight":
            for dr, dc in knight_moves:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state or board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
        elif piece_name == 'Bishop':
            for dr, dc in diagonal_moves:
                new_r, new_c = r + dr, c + dc
                while 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state:
                        legal_moves.append((pos, target_pos))
                    elif board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
                        break
                    else:
                        break
                    new_r += dr
                    new_c += dc
        elif piece_name == 'Rook':
            for dr, dc in orthogonal_moves:
                new_r, new_c = r + dr, c + dc
                while 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state:
                        legal_moves.append((pos, target_pos))
                    elif board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
                        break
                    else:
                        break
                    new_r += dr
                    new_c += dc
        elif piece_name == 'Squire':
            for dr, dc in squire_moves:
                new_r, new_c = r + dr, c + dc
                if 0 <= new_r <= 7 and 0 <= new_c <= 7:
                    target_pos = (new_r, new_c)
                    if target_pos not in board_state or board_state[target_pos][1] != color:
                        legal_moves.append((pos, target_pos))
    legal_moves.sort(key=lambda mv: (mv[0][0], mv[0][1], mv[1][0], mv[1][1]))
    return legal_moves


def studentAgent(board):
    transposition_table = {}
    nodes_searched = [0]
    MAX_NODES = 200000
    piece_values = {"King": 10000, "Rook": 5, "Bishop": 3, "Knight": 3, "Squire": 4, "Combatant": 2}

    def evaluate(board_state):
        score = 0
        for piece_name, piece_color, _ in board_state:
            value = piece_values.get(piece_name, 0)
            if piece_color == "white":
                score += value
            else:
                score -= value
        return score
    def apply_move(board_state, move):
        from_pos, to_pos = move
        new_board = []
        for piece_name, piece_color, pos in board_state:
            if pos == from_pos:
                new_board.append((piece_name, piece_color, to_pos))
            elif pos == to_pos:
                continue
            else:
                new_board.append((piece_name, piece_color, pos))
        return new_board
    def board_key(board_state):
        return tuple(sorted(board_state, key=lambda x: (x[0], x[1], x[2])))
    def alphabeta(board_state, depth, alpha, beta, maximizing, original_depth=None):
        nodes_searched[0] += 1
        if nodes_searched[0] > MAX_NODES:
            return evaluate(board_state), None
        
        if original_depth is None:
            original_depth = depth
        if depth == 0:
            return evaluate(board_state), None
        key = (board_key(board_state), depth, maximizing)
        if key in transposition_table:
            return transposition_table[key]
        white_king = False
        black_king = False
        for piece_name, piece_color, _ in board_state:
            if piece_name == "King":
                if piece_color == "white":
                    white_king = True
                else:
                    black_king = True
        
        if not black_king:
            return 100000 - (original_depth - depth), None
        if not white_king:
            return -100000 + (original_depth - depth), None
        if len(board_state) == 2 and white_king and black_king:
            return 0, None
        orig_alpha, orig_beta = alpha, beta
        legal_moves = get_legal_moves(board_state, "white" if maximizing else "black")
        if not legal_moves:
            val = evaluate(board_state)
            transposition_table[key] = (val, None)
            return val, None
        board_dict = {pos: (name, color) for name, color, pos in board_state}

        move_scores = []
        for move in legal_moves:
            from_pos, to_pos = move
            score = 0
            if to_pos in board_dict:
                captured_piece, captured_color = board_dict[to_pos]
                if (maximizing and captured_color == "black") or (not maximizing and captured_color == "white"):
                    score = piece_values.get(captured_piece, 0) * 10
            move_scores.append((score, move))
        
        move_scores.sort(reverse=True)
        legal_moves = [move for _, move in move_scores]
        best_move = None
        if maximizing:
            max_eval = -float('inf')
            for move in legal_moves:
                new_board = apply_move(board_state, move)
                eval_val, _ = alphabeta(new_board, depth-1, alpha, beta, False, original_depth)
                if eval_val > max_eval:
                    max_eval = eval_val
                    best_move = move
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            if nodes_searched[0] <= MAX_NODES and orig_alpha < max_eval < orig_beta:
                transposition_table[key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in legal_moves:
                new_board = apply_move(board_state, move)
                eval_val, _ = alphabeta(new_board, depth-1, alpha, beta, True, original_depth)
                if eval_val < min_eval:
                    min_eval = eval_val
                    best_move = move
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            if nodes_searched[0] <= MAX_NODES and orig_alpha < min_eval < orig_beta:
                transposition_table[key] = (min_eval, best_move)
            return min_eval, best_move
    best_move = None
    max_depth = 6

    for depth in range(3, max_depth + 1):
        nodes_searched[0] = 0
        val, current_best = alphabeta(board, depth, -float('inf'), float('inf'), True)
        if nodes_searched[0] > MAX_NODES and best_move is not None:
            break  # budget exhausted mid-iteration: keep the last completed depth
        if current_best:
            best_move = current_best
        if abs(val) > 90000 or nodes_searched[0] > MAX_NODES:
            break
    if best_move is None:
        legal_moves = get_legal_moves(board, "white")
        if legal_moves:
            best_move = legal_moves[0]
        else:
            best_move = ((0,0), (0,0))
    return best_move
