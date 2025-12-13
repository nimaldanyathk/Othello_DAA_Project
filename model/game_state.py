from model.board import Board

class GameState:
    """
    Represents a node in the game's state-space graph.
    Attributes:
        board (Board): The current board configuration.
        player (int): The player whose turn it is (1=Black, -1=White).
    """

    def __init__(self, board=None, player=Board.BLACK):
        self.board = board if board else Board()
        self.player = player

    def get_successors(self):
        """
        Generates the edges of the state-space graph.
        Returns a list of next GameStates reachable from the current state.
        
        If no moves are available, returns either:
        - A state with the same board but swapped player (pass turn), OR
        - Empty list if game is over (both players stuck).
        """
        moves = self.board.get_valid_moves(self.player)
        
        if not moves:
            # Check if opponent can move (Pass turn case)
            if self.board.get_valid_moves(-self.player):
                return [GameState(self.board, -self.player)]
            else:
                return [] # Terminal state

        successors = []
        successors = []
        for r, c in moves:
            # apply_move now returns (board, flipped_list)
            new_board, _ = self.board.apply_move(r, c, self.player)
            successors.append(GameState(new_board, -self.player))
        
        return successors

    def is_terminal(self):
        """
        Check if this node is a terminal node (leaf) in the game tree.
        """
        return not self.get_successors()

    def get_winner(self):
        """
        Returns the winner: 1 (Black), -1 (White), 0 (Draw), or None (Not over).
        Only valid if is_terminal() is True, or can be called anytime for current leader.
        """
        black, white = self.board.get_counts()
        if black > white:
            return Board.BLACK
        elif white > black:
            return Board.WHITE
        else:
            return 0 # Draw
    
    def __hash__(self):
        # Convert grid to tuple of tuples for hashing
        grid_tuple = tuple(tuple(row) for row in self.board.grid)
        return hash((grid_tuple, self.player))

    def __eq__(self, other):
        return (self.board.grid == other.board.grid) and (self.player == other.player)

    def __repr__(self):
        return f"GameState(Player: {'Black' if self.player == 1 else 'White'})"
