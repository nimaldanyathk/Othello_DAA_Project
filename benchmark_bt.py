import time
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move_generator as regular_generator
from algorithms.backtracking import get_backtracking_move_generator as bt_generator

def run_benchmark():
    # Setup initial game state
    board = Board()
    state = GameState(board, Board.BLACK)
    
    depth = 5 # Good depth for testing
    
    print(f"Benchmarking Backtracking vs Regular Minimax (Alpha-Beta) at Depth {depth}...")
    
    # 1. Regular Minimax
    print("\nRunning Regular Minimax...")
    start_time = time.time()
    reg_gen = regular_generator(state, depth=depth)
    reg_result_state = None
    reg_score = None
    
    for item in reg_gen:
        if item['type'] == 'result':
            reg_result_state = item['state']
            reg_score = item.get('score', 0)
            
    reg_duration = time.time() - start_time
    print(f"Regular Minimax Duration: {reg_duration:.4f} seconds")
    
    # 2. Backtracking Minimax
    print("\nRunning Backtracking Minimax...")
    start_time = time.time()
    bt_gen = bt_generator(state, depth=depth)
    bt_result_state = None
    bt_score = None
    
    for item in bt_gen:
        if item['type'] == 'result':
            bt_result_state = item['state']
            bt_score = item['score']
            
    bt_duration = time.time() - start_time
    print(f"Backtracking Minimax Duration: {bt_duration:.4f} seconds")
    
    # 3. Verification
    print("\n--- Results ---")
    
    # Validate Output Match
    if reg_result_state and bt_result_state:
        reg_grid = reg_result_state.board.grid
        bt_grid = bt_result_state.board.grid
        grids_match = (reg_grid == bt_grid)
        
        print(f"Do the resulting boards match? {'YES' if grids_match else 'NO!!!'}")
        if not grids_match:
            print("REGULAR RESULT:")
            for row in reg_grid: print(row)
            print("BACKTRACKING RESULT:")
            for row in bt_grid: print(row)
            
        print(f"Regular Score: {reg_score}")
        print(f"Backtracking Score: {bt_score}")
    else:
        print("Error: One of the algorithms didn't return a state.")

    # Speedup
    if bt_duration > 0:
        speedup = reg_duration / bt_duration
        print(f"\nSpeedup: {speedup:.2f}x faster using in-place Backtracking")

if __name__ == "__main__":
    run_benchmark()
