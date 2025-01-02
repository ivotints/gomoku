from board import coordinate, SIZE, out_of_bounds
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import copy
from macro import PATTERN

def handle_move_bot(boards, turn, move, captures):
    capture, pos = check_capture(boards, move, turn)
    captures[turn] += capture
    place_piece(boards[turn], move.co)
    if capture:
        for p in pos:
            place_piece(boards[not turn], p, False)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture
import time
def generate_legal_moves(boards, turn, capture, t):
    start = time.time()
    legal_moves = set()  # Use set to avoid duplicates
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    
    # Find existing pieces
    for row in range(SIZE - 1):
        for col in range(SIZE - 1):
            # If piece exists (either color)
            if (boards[0][0] >> (row * (SIZE-1) + col) & 1) or \
               (boards[1][0] >> (row * (SIZE-1) + col) & 1):
                # Generate moves in 2-square radius
                for d_row in range(-1, 2):
                    for d_col in range(-1, 2):
                        new_row = row + d_row
                        new_col = col + d_col
                        
                        # Skip if out of bounds
                        if new_row < 0 or new_row >= SIZE - 1 or \
                           new_col < 0 or new_col >= SIZE - 1:
                            continue
                            
                        move = coordinate((new_row, new_col))
                        # Skip if occupied
                        if is_occupied(boards[0], move.co) or \
                           is_occupied(boards[1], move.co):
                            continue
                            
                        # Check if legal
                        legal, _, _ = is_legal(capture, boards, move, turn)
                        if legal:
                            legal_moves.add(move)
    t[0] += time.time() - start
    return list(legal_moves)

def bitwise_heuristic(boards, turn, capture):
    ROW_SIZE = 19
    WINDOW_SIZE = 5
    ROW_MASK = (1 << ROW_SIZE) - 1
    WINDOW_MASK = (1 << WINDOW_SIZE) - 1
    value = 0

    def scan_window(current_bits, opponent_bits):
        local_value = 0
        for window_shift in range(ROW_SIZE - WINDOW_SIZE + 1):
            window_opponent = (opponent_bits >> window_shift) & WINDOW_MASK
            if window_opponent == 0:
                window_turn = (current_bits >> window_shift) & WINDOW_MASK
                if window_turn != 0:
                    for pattern, pat_value in PATTERN:
                        if window_turn == pattern:
                            local_value += pat_value
                            break
        return local_value

    # Horizontal scan
    for row in range(ROW_SIZE):
        row_shift = row * ROW_SIZE
        current_row = (boards[turn][0] >> row_shift) & ROW_MASK
        current_row_opponent = (boards[not turn][0] >> row_shift) & ROW_MASK
        value += scan_window(current_row, current_row_opponent)

    # Vertical scan .It will go from last 361 position to the top 19. goes from down to up
    for col in range(ROW_SIZE): # 0 to 18
        vertical_bits = 0
        vertical_opponent = 0
        for row in range(ROW_SIZE): # 0 to 18
            bit_pos = row * ROW_SIZE + col
            vertical_bits |= ((boards[turn][0] >> bit_pos) & 1) << row
            vertical_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << row
        value += scan_window(vertical_bits, vertical_opponent)

        # Main diagonal scan (↘)
    for start in range(2 * ROW_SIZE - 1): # 0 to 37
        diagonal_bits = 0
        diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = max(0, ROW_SIZE - 1 - start)
        length = min(ROW_SIZE - start_col, ROW_SIZE - start_row)
        
        if length >= WINDOW_SIZE:
            for i in range(length):
                row = start_row + i
                col = start_col + i
                bit_pos = row * ROW_SIZE + col
                diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
            value += scan_window(diagonal_bits, diagonal_opponent)

    # Anti-diagonal scan (↙)
    for start in range(2 * ROW_SIZE - 1):
        anti_diagonal_bits = 0
        anti_diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = min(ROW_SIZE - 1, start)
        length = min(start_col + 1, ROW_SIZE - start_row)
        
        if length >= WINDOW_SIZE:
            for i in range(length):
                row = start_row + i
                col = start_col - i
                bit_pos = row * ROW_SIZE + col
                anti_diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                anti_diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
            value += scan_window(anti_diagonal_bits, anti_diagonal_opponent)

    return 16 * (2 ** capture) + value

def minimax(boards, depth, alpha, beta, maximizing_player, turn, captures, count, t):
    
    if depth == 0:
        count[0] += 1
        return bitwise_heuristic(boards, turn, captures[turn])
    
    moves = generate_legal_moves(boards, turn, captures[turn], t)
    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            # new_captures = copy.deepcopy(captures)
            result, capture = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            
            if result:  # Win found
                return float('inf')
                
            eval = minimax(new_boards, depth - 1, alpha, beta, False, not turn, captures, count, t)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            # new_captures = copy.deepcopy(captures)
            result, capture = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            
            if result:  # Loss found
                return float('-inf')
                
            eval = minimax(new_boards, depth - 1, alpha, beta, True, not turn, captures, count, t)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval

def bot_play(boards, turn, captures):
    t = [0]
    moves = generate_legal_moves(boards, turn, captures[turn], t)
    best_move = moves[0]  # Default to first move
    best_eval = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    count = [0]
    
    # First check for winning moves
    for move in moves:
        new_boards = copy.deepcopy(boards)
        result, capture = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
        
        if result:  # Winning move found
            print("Found winning move")
            return move

    # If no winning move, do minimax search    
    for move in moves:
        new_boards = copy.deepcopy(boards)
        result, _ = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
        
        if not result:  # Only evaluate non-winning moves
            eval = minimax(new_boards, 2, alpha, beta, False, not turn, captures, count, t)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)
    
    print(f"Evaluated {count[0]} positions")
    print(f"Time spent generating moves: {t[0]:.2f}s") 
    return best_move

