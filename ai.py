from board import coordinate, SIZE, out_of_bounds
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import copy
from macro import PATTERN
import time

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



def generate_legal_moves(boards, turn, capture, t):
    start_time = time.time()
    legal_moves = set()
    
    ROW_SIZE = 19
    union_board = boards[0][0] | boards[1][0]
    ROW_MASK = (1 << ROW_SIZE) - 1 # 0b1111111111111111111    
    # 1) Find top bound
    top = 0
    while top < ROW_SIZE: # 0 to 18
        row_bits = (union_board >> (top * ROW_SIZE)) & ROW_MASK
        if row_bits != 0:
            break
        top += 1

    # 2) Find bottom bound
    bottom = ROW_SIZE - 1
    while bottom >= 0:
        row_bits = (union_board >> (bottom * ROW_SIZE)) & ROW_MASK
        if row_bits != 0:
            break
        bottom -= 1

    # 3) Find left bound
    left = 0
    while left < ROW_SIZE:
        col_mask = 0
        # Build mask for column 'left'
        for row in range(top, bottom + 1):
            col_mask |= ((union_board >> (row * ROW_SIZE + left)) & 1)
        if col_mask != 0:
            break
        left += 1

    # 4) Find right bound
    right = ROW_SIZE - 1
    while right >= 0:
        col_mask = 0
        for row in range(top, bottom + 1):
            col_mask |= ((union_board >> (row * ROW_SIZE + right)) & 1)
        if col_mask != 0:
            break
        right -= 1
    #print (top, bottom, left, right)

    # Optionally expand bounding box by 1 or 2 squares:
    expand = 1
    top = max(0, top - expand)
    bottom = min(ROW_SIZE - 1, bottom + expand)
    left = max(0, left - expand)
    right = min(ROW_SIZE - 1, right + expand)
    #print (top, bottom, left, right)

    # need another logic here

# i need another logic for generating children. i want create a sliding wimdow 3 by 3inside of bounding boz. it will move throu each dot in the bounding box, cheking if int, which we created from sliding window 3 by 3 is not 0 than generate this move. it should increase speed of function becouse will use only bitwise operations an will not use set.

    moves = []
    # 5) 3×3 sliding window
    for row in range(top, bottom - 1): # 8, 11
        for col in range(left, right - 1): # 8, 11
            # Extract 3×3 block bits
            block = 0
            for i in range(3):
                shift_pos = (row + i) * ROW_SIZE + col
                row_bits |= (union_board >> shift_pos) & 0b111  # 3 bits
            # If block == 0 => no pieces in this 3×3 window
            if block == 0:
                continue
            # Check each cell in that 3×3
            for i in range(3):
                for j in range(3):
                    r = row + i
                    c = col + j
                    bit_pos = r * ROW_SIZE + c
                    # If position is unoccupied
                    if not ((union_board >> bit_pos) & 1):
                        m = coordinate((r, c))
                        legal, _, _ = is_legal(capture, boards, m, turn)
                        if legal:
                            moves.append(m)

    # # 5) Generate all moves within bounding box
    # for row in range(top, bottom + 1):
    #     for col in range(left, right + 1):
    #         bit_pos = row * ROW_SIZE + col
    #         # If this board position is not occupied:
    #         if not ((union_board >> bit_pos) & 1):
    #             move = coordinate((row, col))
    #             # Check if legal
    #             legal, _, _ = is_legal(capture, boards, move, turn)
    #             if legal:
    #                 legal_moves.add(move)

    # Record time
    t[0] += time.time() - start_time
    return list(moves)


# new faster version
def generate_legal_moves(boards, turn, capture, t):
    start_time = time.time()
    legal_moves = []

    ROW_SIZE = 19
    union_board = boards[0][0] | boards[1][0]

    # 1) Define the bounding box
    ROW_MASK = (1 << ROW_SIZE) - 1
    top = 0
    while top < ROW_SIZE and ((union_board >> (top * ROW_SIZE)) & ROW_MASK) == 0:
        top += 1
    bottom = ROW_SIZE - 1
    while bottom >= 0 and ((union_board >> (bottom * ROW_SIZE)) & ROW_MASK) == 0:
        bottom -= 1
    left = 0
    while left < ROW_SIZE and not any((union_board >> (row * ROW_SIZE + left)) & 1 for row in range(top, bottom + 1)):
        left += 1
    right = ROW_SIZE - 1
    while right >= 0 and not any((union_board >> (row * ROW_SIZE + right)) & 1 for row in range(top, bottom + 1)):
        right -= 1

    # Optionally expand bounding box
    expand = 1
    top = max(0, top - expand)
    bottom = min(ROW_SIZE - 1, bottom + expand)
    left = max(0, left - expand)
    right = min(ROW_SIZE - 1, right + expand)


    # 2) Iterate through the bounding box with a 3x3 sliding window
    for row in range(top, bottom + 1): # 8, 11
        for col in range(left, right + 1):


            window_mask = 0
            for i in range(-1, 2): # -1, 0, 1
                check_row = row + i
                check_col = col - 1
                # Skip if out of bounds or if extracting 3 bits would overflow
                if check_row < 0 or check_row >= ROW_SIZE:
                    continue
                if check_col < 0 or (check_col + 2) >= ROW_SIZE:
                    continue
                shift_pos = (row + i) * ROW_SIZE + col - 1
                window_mask |= (union_board >> shift_pos) & 0b111  # 3 bits

            # # Check 3x3 window centered at (row, col)
            # window_mask = 0
            # for d_row in range(-1, 2):
            #     for d_col in range(-1, 2):
            #         n_row = row + d_row
            #         n_col = col + d_col
            #         if 0 <= n_row < ROW_SIZE and 0 <= n_col < ROW_SIZE:
            #             bit_pos = n_row * ROW_SIZE + n_col
            #             window_mask |= ((union_board >> bit_pos) & 1)
            
            # If the sliding window is not empty, check legality of center position
            if window_mask != 0:
                bit_pos = row * ROW_SIZE + col
                if not ((union_board >> bit_pos) & 1):  # If not occupied
                    move = coordinate((row, col))
                    legal, _, _ = is_legal(capture, boards, move, turn) # it is too slow!! fix it
                    if legal:
                        legal_moves.append(move)

    # Record time
    t[0] += time.time() - start_time
    return legal_moves


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

    # Vertical scan
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
            eval = minimax(new_boards, 3, alpha, beta, False, not turn, captures, count, t)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)
    
    print(f"Evaluated {count[0]} positions")
    print(f"Time spent generating moves: {t[0]:.2f}s") 
    return best_move

