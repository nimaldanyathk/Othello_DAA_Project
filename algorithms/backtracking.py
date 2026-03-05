from algorithms.heuristics import weighted_heuristic
from model.board import Board

def backtracking_minimax_generator(state, depth, alpha, beta, player, heuristic_func):
    """
       minimax generator with Alpha-Beta pruning that uses perfect backtracking (in-place modification).
    it avoids copying the board, massively reducing memory allocations.
    """
    yield {'type': 'search_node', 'state': state, 'depth': depth, 'alpha': alpha, 'beta': beta}

    if depth == 0 or state.is_terminal():
        score = heuristic_func(state.board, player)
        yield {'type': 'leaf', 'state': state, 'depth': depth, 'score': score}
        return score, None

    # we only get moves for the cURRENT turn player
    moves = state.board.get_valid_moves(state.player)
    
    # If no moves (Pass)
    if not moves:
        # Change player but keep board
        original_player = state.player
        state.player = -state.player
        
        val, _ = yield from backtracking_minimax_generator(state, depth-1, alpha, beta, player, heuristic_func)
        
        # Backtrack player
        state.player = original_player
        
        return val, None

    best_move = None

    if state.player == player: 
        # Maximizing Player
        max_eval = float('-inf')
        for r, c in moves:
            # APPLY MOVE IN-PLACE
            flipped = state.board.apply_move_in_place(r, c, state.player)
            original_player = state.player
            state.player = -state.player
            
            # RECURSE
            eval_score, _ = yield from backtracking_minimax_generator(state, depth - 1, alpha, beta, player, heuristic_func)
            
            # BACKTRACK (Undo Move)
            state.player = original_player
            state.board.undo_move(r, c, state.player, flipped)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (r, c)
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                yield {'type': 'prune', 'state': state, 'depth': depth, 'score': eval_score}
                break # Beta Prune

        # best_move is just coordinates. To be compatible with UI which expects a GameState,
        # we will reconstruct the *best state* once at the end in the wrapper.
        return max_eval, best_move

    else: 
        # Minimizing Player
        min_eval = float('inf')
        for r, c in moves:
            # APPLY MOVE IN-PLACE
            flipped = state.board.apply_move_in_place(r, c, state.player)
            original_player = state.player
            state.player = -state.player
            
            # RECURSE
            eval_score, _ = yield from backtracking_minimax_generator(state, depth - 1, alpha, beta, player, heuristic_func)
            
            # BACKTRACK
            state.player = original_player
            state.board.undo_move(r, c, state.player, flipped)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (r, c)
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                yield {'type': 'prune', 'state': state, 'depth': depth, 'score': eval_score}
                break # Alpha Prune
        
        return min_eval, best_move

def get_backtracking_move_generator(state, depth=3):
    """
    Entry point for the Backtracking Minimax generator.
    """
    score, best_move_coords = yield from backtracking_minimax_generator(
        state, depth, float('-inf'), float('inf'), state.player, weighted_heuristic
    )
    
    # Once the search is done, GameState is back to its original configuration.
    # The UI needs the new GameState corresponding to the best move.
    best_state = None
    if best_move_coords:
        r, c = best_move_coords
        new_board, _ = state.board.apply_move(r, c, state.player)
        from model.game_state import GameState
        best_state = GameState(new_board, -state.player)
    else:
        # Pass turn
        from model.game_state import GameState
        best_state = GameState(state.board, -state.player) # Ideally copy board
        
    yield {'type': 'result', 'state': best_state, 'score': score}

def get_best_move(state, depth=3):
    """ Backward compatibility wrapper. """
    gen = get_backtracking_move_generator(state, depth)
    result_state = None
    for item in gen:
        if item['type'] == 'result':
            result_state = item['state']
    return result_state
