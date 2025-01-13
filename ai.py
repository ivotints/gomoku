from game import check_capture, is_won, has_winning_line, is_legal_lite_py
import copy
from macro import DEPTH
from wrapper import heuristic, generate_legal_moves_cpp, is_legal_lite

# do not return anything
def handle_move_bot_void(boards, turn, move, captures) -> None:
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards, y, x, turn)
    boards[turn][0] |= (1 << move)
    if capture: # here it will delete opponent's pieces
        captures[turn] += capture
        for p in pos:
            boards[not turn][0] &= ~(1 << p)

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

def generate_legal_moves(board_turn, board_not_turn, turn, capture):
    legal_moves = []
    COL_MASK = 0b1000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001 # 000000000000000000
    ROW_MASK = 0b1111111111111111111
    ROW_SIZE = 19
    union_board = board_turn | board_not_turn

    # 1) Define the bounding box
    top = 0
    while top < ROW_SIZE and ((union_board >> (top * ROW_SIZE)) & ROW_MASK) == 0:
        top += 1
    bottom = ROW_SIZE - 1
    while bottom >= 0 and ((union_board >> (bottom * ROW_SIZE)) & ROW_MASK) == 0:
        bottom -= 1
    left = 0
    while left < ROW_SIZE and ((union_board >> left) & COL_MASK) == 0:
        left += 1
    right = ROW_SIZE - 1
    while right >= 0 and ((union_board >> right) & COL_MASK) == 0:
        right -= 1
    # print(f"Bounding box:", top, bottom, left, right)

    # Optionally expand bounding box
    expand = 1
    top = 0 if top - expand < 0 else top - expand
    bottom = ROW_SIZE - 1 if bottom + expand >= ROW_SIZE else bottom + expand
    left = 0 if left - expand < 0 else left - expand
    right = ROW_SIZE - 1 if right + expand >= ROW_SIZE else right + expand

    # print(f"Bounding box:", top, bottom, left, right)

    # 2) Iterate through the bounding box with a 3x3 sliding window
    if right - left == 1:
        mask = 0b11
    else:
        mask = 0b111
    for row in range(top, bottom + 1): # 0, 1, 2
        for col in range(left, right + 1): # 0, 1

            window_mask = 0
            for i in range(-1, 2):
                check_row = row + i
                # Skip if out of bounds or if extracting 3 bits would overflow
                if check_row < top or check_row > bottom:
                    continue
                check_col = col - 1 if col - 1 > left else left


                shift_pos = check_row * ROW_SIZE + check_col
                window_mask |= (union_board >> shift_pos) & mask

            # If the sliding window is not empty, check legality of center position
            if window_mask != 0:
                bit_pos = row * ROW_SIZE + col
                if not ((union_board >> bit_pos) & 1):  # If not occupied
                    if is_legal_lite(capture, board_turn, board_not_turn, row, col):
                        legal_moves.append(bit_pos)

    return legal_moves

def bitwise_heuristic(board_turn, board_not_turn, capture, capture_opponent):
    ROW_SIZE = 19
    WINDOW_SIZE = 5
    ROW_MASK = 0b1111111111111111111
    COL_MASK = 0b1000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001000000000000000000100000000000000000010000000000000000001
    WINDOW_MASK = 0b11111
    value = 0

    # Find bounding box
    if capture > 4:
        return float('inf') 
    if capture_opponent > 4:
        return float('-inf') 
    
    union_board = board_turn | board_not_turn
    top = 0
    while top < ROW_SIZE and ((union_board >> (top * ROW_SIZE)) & ROW_MASK) == 0:
        top += 1
    bottom = ROW_SIZE - 1
    while bottom >= 0 and ((union_board >> (bottom * ROW_SIZE)) & ROW_MASK) == 0:
        bottom -= 1
    left = 0
    while left < ROW_SIZE and ((union_board >> left) & COL_MASK) == 0:
        left += 1
    right = ROW_SIZE - 1
    while right >= 0 and ((union_board >> right) & COL_MASK) == 0:
        right -= 1

    expand = WINDOW_SIZE - 1
    top_exp = 0 if top - expand < 0 else top - expand
    bottom_exp = ROW_SIZE - 1 if bottom + expand >= ROW_SIZE else bottom + expand
    left_exp = 0 if left - expand < 0 else left - expand
    right_exp = ROW_SIZE - 1 if right + expand >= ROW_SIZE else right + expand
    n = bottom - top + 1
    m = right - left + 1

    # Horizontal scan
    for row in range(top, bottom + 1):
        row_shift = row * ROW_SIZE
        current_row = (board_turn >> row_shift) & ((1 << (right_exp + 1)) - (1 << left_exp))
        current_row_opponent = (board_not_turn >> row_shift) & ((1 << (right_exp + 1)) - (1 << left_exp))
        
        for window_shift in range(right_exp - left_exp - WINDOW_SIZE + 2):
            window_turn = (current_row >> window_shift) & WINDOW_MASK
            window_opponent = (current_row_opponent >> window_shift) & WINDOW_MASK
            
            if window_opponent == 0:
                bits_count = 0
                temp_window = window_turn
                while temp_window:
                    temp_window &= (temp_window - 1)
                    bits_count += 1
                if bits_count > 1:
                    if bits_count == 5:
                        return float('inf')
                    value += 1 << (3 * (bits_count - 2))
                    
            if window_turn == 0:
                bits_count = 0
                temp_window = window_opponent
                while temp_window:
                    temp_window &= (temp_window - 1)
                    bits_count += 1
                if bits_count > 1:
                    if bits_count == 5:
                        return float('-inf')
                    value -= 1 << (3 * (bits_count - 2))

    # Vertical scan
    for col in range(left, right + 1):
        vertical_bits = 0
        vertical_opponent = 0
        for row in range(top_exp, bottom_exp + 1):
            bit_pos = row * ROW_SIZE + col
            vertical_bits |= ((board_turn >> bit_pos) & 1) << (row - top_exp)
            vertical_opponent |= ((board_not_turn >> bit_pos) & 1) << (row - top_exp)
        
        # Inline scan_window logic
        for window_shift in range(bottom_exp - top_exp - WINDOW_SIZE + 2):
            window_turn = (vertical_bits >> window_shift) & WINDOW_MASK
            window_opponent = (vertical_opponent >> window_shift) & WINDOW_MASK
            
            if window_opponent == 0:
                bits_count = 0
                temp_window = window_turn
                while temp_window:
                    temp_window &= (temp_window - 1)
                    bits_count += 1
                if bits_count > 1:
                    if bits_count == 5:
                        return float('inf')
                    value += 1 << (3 * (bits_count - 2))
            
            if window_turn == 0:
                bits_count = 0
                temp_window = window_opponent
                while temp_window:
                    temp_window &= (temp_window - 1)
                    bits_count += 1
                if bits_count > 1:
                    if bits_count == 5:
                        return float('-inf')
                    value -= 1 << (3 * (bits_count - 2))

    # Main diagonal scan (↘)
    n = bottom - top + 1
    m = right - left + 1
    
    for k in range(n + m - 1):
        start_row = top_exp + n - k - 1 if top_exp + n - k - 1 > top_exp else top_exp
        start_col = left_exp - n + k + 1 if left_exp - n + k + 1 > left_exp else left_exp
        length = bottom_exp - start_row + 1 if bottom_exp - start_row + 1 < right_exp - start_col + 1 else right_exp - start_col + 1
    
        if length >= WINDOW_SIZE:
            diagonal_bits = 0
            diagonal_opponent = 0
            for i in range(length):
                row = start_row + i
                col = start_col + i
                bit_pos = row * ROW_SIZE + col
                diagonal_bits |= ((board_turn >> bit_pos) & 1) << i
                diagonal_opponent |= ((board_not_turn >> bit_pos) & 1) << i
            
            for window_shift in range(length - WINDOW_SIZE + 1):
                window_turn = (diagonal_bits >> window_shift) & WINDOW_MASK
                window_opponent = (diagonal_opponent >> window_shift) & WINDOW_MASK
                
                if window_opponent == 0:
                    bits_count = 0
                    temp_window = window_turn
                    while temp_window:
                        temp_window &= (temp_window - 1)
                        bits_count += 1
                    if bits_count > 1:
                        if bits_count == 5:
                            return float('inf')
                        value += 1 << (3 * (bits_count - 2))
                
                if window_turn == 0:
                    bits_count = 0
                    temp_window = window_opponent
                    while temp_window:
                        temp_window &= (temp_window - 1)
                        bits_count += 1
                    if bits_count > 1:
                        if bits_count == 5:
                            return float('-inf')
                        value -= 1 << (3 * (bits_count - 2))

     # Anti-diagonal scan (↙)
    for k in range(n + m - 1):
        start_row = top_exp + n - k - 1 if top_exp + n - k - 1 > top_exp else top_exp
        start_col = right_exp + n - k - 1 if right_exp + n - k - 1 < right_exp else right_exp
        length = bottom_exp - start_row + 1 if bottom_exp - start_row + 1 < start_col - left_exp + 1 else start_col - left_exp + 1
    
        if length >= WINDOW_SIZE:
            anti_bits = 0
            anti_opponent = 0
            for i in range(length):
                row = start_row + i
                col = start_col - i
                bit_pos = row * ROW_SIZE + col
                anti_bits |= ((board_turn >> bit_pos) & 1) << i
                anti_opponent |= ((board_not_turn >> bit_pos) & 1) << i
    
            for window_shift in range(length - WINDOW_SIZE + 1):
                window_turn = (anti_bits >> window_shift) & WINDOW_MASK
                window_opponent = (anti_opponent >> window_shift) & WINDOW_MASK
                
                if window_opponent == 0:
                    bits_count = 0
                    temp_window = window_turn
                    while temp_window:
                        temp_window &= (temp_window - 1)
                        bits_count += 1
                    if bits_count > 1:
                        if bits_count == 5:
                            return float('inf')
                        value += 1 << (3 * (bits_count - 2))
                
                if window_turn == 0:
                    bits_count = 0
                    temp_window = window_opponent
                    while temp_window:
                        temp_window &= (temp_window - 1)
                        bits_count += 1
                    if bits_count > 1:
                        if bits_count == 5:
                            return float('-inf')
                        value -= 1 << (3 * (bits_count - 2))

    return (16 * (2 ** capture) + value) - (16 * (2 ** capture_opponent))

def minimax(boards, depth, alpha, beta, maximizing_player, turn, captures, count):
    if depth == 1:
        count[0] += 1
        value = heuristic(boards[turn][0], boards[not turn][0],captures[turn],captures[not turn])
        # value = bitwise_heuristic(boards[turn][0], boards[not turn][0], captures[turn], captures[not turn])
        return value
    moves = generate_legal_moves(boards[turn][0], boards[not turn][0], turn, captures[turn])

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return float('inf')
            eval = minimax(new_boards, depth - 1, alpha, beta, False, not turn, captures, count)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return float('-inf')
            eval = minimax(new_boards, depth - 1, alpha, beta, True, not turn, captures, count)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
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
    moves = generate_legal_moves(boards[turn][0], boards[not turn][0], turn, captures[turn])

    for move in moves:
        if is_winning_move(boards, turn, move, captures):
            return move

    best_move = moves[0]  # Default to first move
    best_eval = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    count = [0]

    for move in moves:
        new_boards = copy.deepcopy(boards)
        handle_move_bot_void(new_boards, turn, move, [captures[0], captures[1]])

        eval = minimax(new_boards, DEPTH, alpha, beta, False, not turn, captures, count)
        if eval > best_eval:
            best_eval = eval
            best_move = move
        alpha = max(alpha, eval)

    print(f"Evaluated {count[0]} positions")
    return best_move
