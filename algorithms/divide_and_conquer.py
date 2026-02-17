from algorithms.heuristics import weighted_heuristic

def dnc_minimax_generator(state, depth, player, heuristic_func):

    yield {'type': 'search_node', 'state': state, 'depth': depth, 'score': None}

    if depth == 0 or state.is_terminal():
        score = heuristic_func(state.board, player)
        yield {'type': 'leaf', 'state': state, 'depth': depth, 'score': score}
        return score, state

    successors = state.get_successors()
    
    if not successors:
        val = yield from dnc_minimax_generator(state, depth-1, player, heuristic_func)
        return val

    best_op = None

    if state.player == player: 
        max_eval = float('-inf')
        for successor in successors:
            eval_score, _ = yield from dnc_minimax_generator(successor, depth - 1, player, heuristic_func)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_op = successor
        
        return max_eval, best_op

    else: 
        min_eval = float('inf')
        for successor in successors:
            eval_score, _ = yield from dnc_minimax_generator(successor, depth - 1, player, heuristic_func)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_op = successor
                
        return min_eval, best_op

def get_dnc_move_generator(state, depth=3):

    score, best_state = yield from dnc_minimax_generator(state, depth, state.player, weighted_heuristic)
    
    yield {'type': 'result', 'state': best_state}
