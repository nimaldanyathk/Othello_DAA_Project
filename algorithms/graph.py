from collections import deque
from algorithms.heuristics import weighted_heuristic

def bfs_explore(start_state, max_nodes=1000):
    """
    Breadth-First Search traversal generator.
    Explores the game graph layer by layer.
    Useful for analyzing immediate move possibilities.
    """
    queue = deque([start_state])
    visited = set()
    visited.add(start_state)
    count = 0
    
    while queue and count < max_nodes:
        state = queue.popleft()
        yield state
        count += 1
        
        if not state.is_terminal():
            for successor in state.get_successors():
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)

def dfs_explore(start_state, max_depth=3):
    """
    Depth-First Search traversal generator.
    Explores deep into one variation before backtracking.
    """
    stack = [(start_state, 0)]
    visited = set()
    visited.add(start_state)
    
    while stack:
        state, depth = stack.pop()
        yield state
        
        if depth < max_depth and not state.is_terminal():
            for successor in state.get_successors():
                if successor not in visited:
                    visited.add(successor)
                    stack.append((successor, depth + 1))

def depth_limited_dfs_generator(state, depth, player, heuristic_func):
    """
    Generator version of Minimax.
    Yields:
        dict: {'type': 'search_node', 'state': state, 'depth': depth, 'score': val}
    Returns:
        (best_score, best_op) via StopIteration value (or final yield logic)
    """
    # Yield current state visiting
    yield {'type': 'search_node', 'state': state, 'depth': depth, 'score': None}

    if depth == 0 or state.is_terminal():
        score = heuristic_func(state.board, player)
        yield {'type': 'leaf', 'state': state, 'depth': depth, 'score': score}
        return score, state

    successors = state.get_successors()
    if not successors:
        # Pass turn
        # We need to yield from recursive call
        result = yield from depth_limited_dfs_generator(state, depth-1, player, heuristic_func)
        return result

    best_score = float('-inf') if state.player == player else float('inf')
    best_op = None

    for successor in successors:
        score, _ = yield from depth_limited_dfs_generator(successor, depth - 1, player, heuristic_func)
        
        if state.player == player: # Maximize
            if score > best_score:
                best_score = score
                best_op = successor
        else: # Minimize (Opponent's turn)
            if score < best_score:
                best_score = score
                best_op = successor
                
    return best_score, best_op

def get_best_move_generator(state, depth=3):
    """
    Generator wrapper.
    Yields visualization data.
    Finally yields {'type': 'result', 'state': best_state}
    """
    # Use yield from to capture the return value (best_score, best_op)
    # while propagating all visualization dicts up.
    _, best_op = yield from depth_limited_dfs_generator(state, depth, state.player, weighted_heuristic)
            
    yield {'type': 'result', 'state': best_op}

def get_best_move(state, depth=3):
    """
    Backward compatibility wrapper.
    Consumes the generator and returns the final result.
    """
    gen = get_best_move_generator(state, depth)
    result_state = None
    for item in gen:
        if item['type'] == 'result':
            result_state = item['state']
    return result_state
