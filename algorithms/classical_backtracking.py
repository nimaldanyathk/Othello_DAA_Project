from model.board import Board


def classical_backtracking_generator(state, alpha, beta, player):
    """
    Pure / Classical Backtracking Minimax with Alpha-Beta Pruning.

    Key differences from heuristic backtracking:
    - NO depth limit: searches all the way to a terminal game state.
    - NO heuristic: score is the raw piece-count difference at game over.
      (positive = Black winning, negative = White winning)
    - Uses in-place board mutation + undo to avoid copying (memory efficient).

    WARNING: Exponential complexity. Best on 4x4 or 6x6 boards.
    """
    yield {'type': 'search_node', 'state': state, 'depth': 0, 'alpha': alpha, 'beta': beta}

    moves = state.board.get_valid_moves(state.player)

    # --- Terminal Check ---
    if not moves:
        # Try passing to the opponent
        opponent = -state.player
        opponent_moves = state.board.get_valid_moves(opponent)

        if not opponent_moves:
            # Neither player can move → true game over
            black, white = state.board.get_counts()
            score = black - white  # pure piece count, no heuristic
            yield {'type': 'leaf', 'state': state, 'depth': 0, 'score': score}
            return score, None

        # Current player must pass; switch and continue
        original_player = state.player
        state.player = opponent

        val, _ = yield from classical_backtracking_generator(state, alpha, beta, player)

        state.player = original_player  # backtrack player
        return val, None

    best_move = None

    if state.player == player:
        # --- Maximising Player ---
        max_eval = float('-inf')
        for r, c in moves:
            # Apply move in-place
            flipped = state.board.apply_move_in_place(r, c, state.player)
            original_player = state.player
            state.player = -state.player

            # Recurse (no depth decrement — goes until terminal)
            eval_score, _ = yield from classical_backtracking_generator(state, alpha, beta, player)

            # BACKTRACK
            state.player = original_player
            state.board.undo_move(r, c, state.player, flipped)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (r, c)

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                yield {'type': 'prune', 'state': state, 'depth': 0, 'score': eval_score}
                break  # Beta cut-off

        return max_eval, best_move

    else:
        # --- Minimising Player ---
        min_eval = float('inf')
        for r, c in moves:
            # Apply move in-place
            flipped = state.board.apply_move_in_place(r, c, state.player)
            original_player = state.player
            state.player = -state.player

            # Recurse
            eval_score, _ = yield from classical_backtracking_generator(state, alpha, beta, player)

            # BACKTRACK
            state.player = original_player
            state.board.undo_move(r, c, state.player, flipped)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (r, c)

            beta = min(beta, eval_score)
            if beta <= alpha:
                yield {'type': 'prune', 'state': state, 'depth': 0, 'score': eval_score}
                break  # Alpha cut-off

        return min_eval, best_move


def get_classical_bt_generator(state):
    """
    Entry point for the Classical Backtracking generator.
    Compatible with the UI's generator protocol (yields vis events, ends with 'result').
    """
    score, best_move_coords = yield from classical_backtracking_generator(
        state, float('-inf'), float('inf'), state.player
    )

    best_state = None
    if best_move_coords:
        r, c = best_move_coords
        new_board, _ = state.board.apply_move(r, c, state.player)
        from model.game_state import GameState
        best_state = GameState(new_board, -state.player)
    else:
        # Pass turn
        from model.game_state import GameState
        best_state = GameState(state.board, -state.player)

    yield {'type': 'result', 'state': best_state, 'score': score}
