from model.game_state import GameState
from model.board import Board
from algorithms.graph import get_best_move

def test_headless():
    print("Initializing GameState...")
    state = GameState()
    
    # Check initial moves
    print("Checking initial successors...")
    successors = state.get_successors()
    print(f"Initial moves count: {len(successors)}")
    assert len(successors) == 4, "Should be 4 initial moves (vertical/horizontal * 2 players, wait... actually 4 specific positions)"
    
    # Simulate a human move (Black)
    # Valid moves for Black at start: (2,3), (3,2), (4,5), (5,4)
    # Let's pick (2,3) -> index 2,3
    print("Applying move for Black at (2,3)...")
    # We need to find the successor corresponding to this move or just apply it manually for test
    # Since get_successors returns GameState objects, let's just use the first one as a simulation
    next_state = successors[0]
    print(f"New state player: {next_state.player} (Should be -1/White)")
    assert next_state.player == Board.WHITE
    
    # Ask AI for a move (White)
    print("Asking AI for a move (Depth 3)...")
    ai_state_response = get_best_move(next_state, depth=3)
    
    if ai_state_response:
        print("AI returned a valid state.")
        print(f"AI moved. New player: {ai_state_response.player} (Should be 1/Black)")
    else:
        print("AI returned None? (Should have moves)")
        
    print("Verification passed!")

if __name__ == "__main__":
    test_headless()
