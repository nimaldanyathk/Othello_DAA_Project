from model.game_state import GameState
from model.board import Board
from algorithms.greedy import get_greedy_move

def test_greedy_choice():
    print("Testing Greedy Choice...")
    
    # Create a board setup where we have two moves.
    # Move 1 flips 1 piece.
    # Move 2 flips 2 pieces.
    
    # 0 1 2 3 4 5 6 7
    # . . . . . . . . 0
    # . . . . . . . . 1
    # . . . . . . . . 2
    # . . B W W . . . 3 (Black at (3,2), White at (3,3), (3,4))
    # . . . . . . . . 4
    
    # If we place Black at (3, 5), we flip (3,4) and (3,3) -> 2 flips.
    
    # Let's constructing a clearer scenario.
    # Standard board:
    # . . . . . . . .
    # . . . . . . . .
    # . . . . . . . .
    # . . . W B . . .
    # . . . B W . . .
    # . . . . . . . .
    
    # Let's manually build a grid.
    grid = [[0]*8 for _ in range(8)]
    
    # Setup for Black's turn
    # White pieces to flip
    grid[3][3] = Board.WHITE
    grid[3][4] = Board.WHITE
    
    # Black anchor
    grid[3][2] = Board.BLACK
    
    # Valid Move 1: Place at (3, 5) -> Horizontal flip of (3,3), (3,4). Count = 2.
    
    # Let's add another option.
    # White at (4,3)
    # Black at (5,3)
    grid[4][3] = Board.WHITE
    grid[5][3] = Board.BLACK
    
    # Valid Move 2: Place at (2,3) -> Vertical flip of (4,3) would require Black at (5,3) to be anchor.
    # Yes, (2,3) -> flips (3,3) and (4,3)? No, (3,3) is WHITE. 
    # Vertical line: (2,3) -> (3,3)[W] -> (4,3)[W] -> (5,3)[B].
    # So placing at (2,3) flips (3,3) and (4,3). Count = 2.
    
    # Let's make Move 2 better.
    # Add White at (2,4)
    # Add Black at (1,5)... wait this is getting complex to visualize.
    
    # Simpler:
    # Row 0: B W W _ (Play at 0,3 flips 2)
    # Row 1: B W _   (Play at 1,2 flips 1)
    
    grid = [[0]*8 for _ in range(8)]
    grid[0][0] = Board.BLACK
    grid[0][1] = Board.WHITE
    grid[0][2] = Board.WHITE
    # Move at (0,3) flips 2.
    
    grid[1][0] = Board.BLACK
    grid[1][1] = Board.WHITE
    # Move at (1,2) flips 1.
    
    board = Board(grid=grid)
    game_state = GameState(board=board, player=Board.BLACK)
    
    print("Valid moves:", board.get_valid_moves(Board.BLACK))
    # Should be [(0,3), (1,2)]... and maybe others if diagonals work technically?
    # 0,3 captures 0,1 and 0,2 ? 0,1 is W, 0,2 is W. 0,0 is B. Yes.
    
    best_state = get_greedy_move(game_state)
    
    # We expect the move to be (0,3) because it flips 2.
    # (1,2) flips 1.
    
    # Check the resulting board of best_state.
    # In best_state, (0,3) should be BLACK.
    if best_state.board.grid[0][3] == Board.BLACK:
        print("PASS: Greedy chose (0,3) (2 flips)")
    elif best_state.board.grid[1][2] == Board.BLACK:
        print("FAIL: Greedy chose (1,2) (1 flip)")
    else:
        print("FAIL: Greedy chose something else or None")
        
    # Verify exact counts
    # If (0,3) was chosen, (0,1) and (0,2) should be BLACK.
    assert best_state.board.grid[0][1] == Board.BLACK
    assert best_state.board.grid[0][2] == Board.BLACK
    
    # If (1,2) was NOT chosen, (1,1) stays WHITE
    # Wait, the state returned is NEW state. It doesn't modify the previous state.
    # So in 'best_state', if it picked (0,3), then (1,2) was not played.
    # So (1,1) should still be WHITE ?
    # Correct.
    assert best_state.board.grid[1][1] == Board.WHITE

if __name__ == "__main__":
    test_greedy_choice()
