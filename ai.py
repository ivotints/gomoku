from board import coordinate
from game import check_capture, is_won, is_legal_lite, has_winning_line
import copy
from macro import PATTERN
import time

def handle_move_bot(boards, turn, move, captures):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards, y, x, turn)
    boards[turn][0] |= (1 << move)
    if capture: # here it will delete opponent's pieces
        captures[turn] += capture
        for p in pos:
            boards[not turn][0] &= ~(1 << p)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True
    return False


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
    top = 0 if top - expand < 0 else top - expand
    bottom = ROW_SIZE - 1 if bottom + expand >= ROW_SIZE else bottom + expand
    left = 0 if left - expand < 0 else left - expand
    right = ROW_SIZE - 1 if right + expand >= ROW_SIZE else right + expand


    # 2) Iterate through the bounding box with a 3x3 sliding window
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):


            window_mask = 0
            for i in range(-1, 2):
                check_row = row + i
                check_col = col - 1
                # Skip if out of bounds or if extracting 3 bits would overflow
                if check_row < 0 or check_row >= ROW_SIZE:
                    continue
                if check_col < 0 or (check_col + 2) >= ROW_SIZE:
                    continue
                shift_pos = (row + i) * ROW_SIZE + col - 1
                window_mask |= (union_board >> shift_pos) & 0b111  # 3 bits
            
            # If the sliding window is not empty, check legality of center position
            if window_mask != 0:
                bit_pos = row * ROW_SIZE + col
                if not ((union_board >> bit_pos) & 1):  # If not occupied
                    if is_legal_lite(capture, boards, row, col, turn):
                        legal_moves.append(bit_pos)

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
                bits_count = 0
                while window_turn:
                    window_turn &= (window_turn - 1)
                    bits_count += 1
                if bits_count > 1:
                    local_value += 1 << (3 * (bits_count - 2))

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

# my goal is to write new lighter heuristic. I whant you not to scan aa the map, but at first create a bounding square like it is done in generate_legal_moves. First you create such a cube, then you go back on 4 lines, to start the 5 bit window and than you do same as in heuristic but this time bounds are smaller, sio it shold take less time.

def bitwise_heuristic(boards, turn, capture):
    ROW_SIZE = 19
    WINDOW_SIZE = 5
    ROW_MASK = (1 << ROW_SIZE) - 1
    WINDOW_MASK = (1 << WINDOW_SIZE) - 1
    value = 0

    # Find bounding box
    top = 0
    while top < ROW_SIZE and ((boards[turn][0] >> (top * ROW_SIZE)) & ROW_MASK) == 0:
        top += 1
    bottom = ROW_SIZE - 1
    while bottom >= 0 and ((boards[turn][0] >> (bottom * ROW_SIZE)) & ROW_MASK) == 0:
        bottom -= 1
    left = 0
    while left < ROW_SIZE and not any((boards[turn][0] >> (row * ROW_SIZE + left)) & 1 for row in range(top, bottom + 1)):
        left += 1
    right = ROW_SIZE - 1
    while right >= 0 and not any((boards[turn][0] >> (row * ROW_SIZE + right)) & 1 for row in range(top, bottom + 1)):
        right -= 1

    # expand = WINDOW_SIZE - 1
    # top = max(0, top - expand)
    # bottom = min(ROW_SIZE - 1, bottom + expand)
    # left = max(0, left - expand)
    # right = min(ROW_SIZE - 1, right + expand)

    expand = WINDOW_SIZE - 1
    top = 0 if top - expand < 0 else top - expand
    bottom = ROW_SIZE - 1 if bottom + expand >= ROW_SIZE else bottom + expand
    left = 0 if left - expand < 0 else left - expand
    right = ROW_SIZE - 1 if right + expand >= ROW_SIZE else right + expand

    def scan_window(current_bits, opponent_bits, size):
        local_value = 0
        for window_shift in range(size - WINDOW_SIZE + 1):
            window_opponent = (opponent_bits >> window_shift) & WINDOW_MASK
            if window_opponent == 0:
                window_turn = (current_bits >> window_shift) & WINDOW_MASK
                bits_count = 0
                while window_turn:
                    window_turn &= (window_turn - 1)
                    bits_count += 1
                if bits_count > 1:
                    local_value += 1 << (3 * (bits_count - 2))

        return local_value

    # Horizontal scan
    for row in range(top, bottom + 1):
        row_shift = row * ROW_SIZE
        current_row = (boards[turn][0] >> row_shift) & ((1 << (right + 1)) - (1 << left))
        current_row_opponent = (boards[not turn][0] >> row_shift) & ((1 << (right + 1)) - (1 << left))
        value += scan_window(current_row, current_row_opponent, right - left + 1)

    # Vertical scan
    for col in range(left, right + 1):
        vertical_bits = 0
        vertical_opponent = 0
        for row in range(top, bottom + 1):
            bit_pos = row * ROW_SIZE + col
            vertical_bits |= ((boards[turn][0] >> bit_pos) & 1) << (row - top)
            vertical_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << (row - top)
        value += scan_window(vertical_bits, vertical_opponent,  bottom - top + 1)

    # Main diagonal scan (↘)
    for start_row in range(top, bottom + 1):
        for start_col in range(left, right + 1):
            diagonal_bits = 0
            diagonal_opponent = 0
            length = bottom - start_row + 1 if bottom - start_row + 1 < right - start_col + 1 else right - start_col + 1
            
            if length >= WINDOW_SIZE:
                for i in range(length):
                    row = start_row + i
                    col = start_col + i
                    if row > bottom or col > right:
                        break
                    bit_pos = row * ROW_SIZE + col
                    diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                    diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
                value += scan_window(diagonal_bits, diagonal_opponent, length)

    # Anti-diagonal scan (↙)
    for start_row in range(top, bottom + 1):
        for start_col in range(right, left - 1, -1):
            anti_diagonal_bits = 0
            anti_diagonal_opponent = 0
            length = bottom - start_row + 1 if bottom - start_row + 1 < start_col - left + 1 else start_col - left + 1
            
            if length >= WINDOW_SIZE:
                for i in range(length):
                    row = start_row + i
                    col = start_col - i
                    if row > bottom or col < left:
                        break
                    bit_pos = row * ROW_SIZE + col
                    anti_diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                    anti_diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
                value += scan_window(anti_diagonal_bits, anti_diagonal_opponent, length)

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
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            
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
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            
            if result:  # Loss found
                return float('-inf')
                
            eval = minimax(new_boards, depth - 1, alpha, beta, True, not turn, captures, count, t)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval

def is_winning_move(boards, turn, move, captures):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards, y, x, turn)
    if capture + captures[turn] > 4:
        return True
    boards[turn][0] |= (1 << move)
    if has_winning_line(boards[turn][0]):
        return True
    boards[turn][0] &= ~(1 << move)
    return False

def bot_play(boards, turn, captures):
    t = [0]
    moves = generate_legal_moves(boards, turn, captures[turn], t)
    best_move = moves[0]  # Default to first move
    best_eval = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    count = [0]
    
    # First check for winning moves
    # for move in moves:
    for move in moves:
        result = is_winning_move(boards, turn, move, [captures[0], captures[1]])
        
        if result:  # Winning move found
            print("Found winning move")
            return move

    # If no winning move, do minimax search
    for move in moves:
        new_boards = copy.deepcopy(boards)
        result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
        
        if not result:  # Only evaluate non-winning moves
            eval = minimax(new_boards, 5, alpha, beta, False, not turn, captures, count, t)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)
    
    print(f"Evaluated {count[0]} positions")
    print(f"Time spent generating moves: {t[0]:.2f}s") 
    return best_move

