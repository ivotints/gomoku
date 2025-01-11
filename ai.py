from game import check_capture, is_won, is_legal_lite, has_winning_line
import copy
from macro import DEPTH
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

def bitwise_heuristic(boards, turn, capture, capture_opponent):
    ROW_SIZE = 19
    WINDOW_SIZE = 5
    ROW_MASK = 0b1111111111111111111
    WINDOW_MASK = (1 << WINDOW_SIZE) - 1
    value = 0

    # Find bounding box
    if capture > 4:
        return float('inf') 
    if capture_opponent > 4:
        return float('-inf') 
    top = 0
    while top < ROW_SIZE and ((boards[turn][0] >> (top * ROW_SIZE)) & ROW_MASK) == 0:
        top += 1
    bottom = ROW_SIZE - 1
    while bottom >= 0 and ((boards[turn][0] >> (bottom * ROW_SIZE)) & ROW_MASK) == 0:
        bottom -= 1
    left = 0
    while left < ROW_SIZE:
        has_piece = False
        for row in range(top, bottom + 1):
            bit_pos = row * ROW_SIZE + left
            has_piece |= (boards[turn][0] >> bit_pos) & 1
        if has_piece:
            break
        left += 1
    right = ROW_SIZE - 1
    while right >= 0:
        has_piece = False
        for row in range(top, bottom + 1):
            bit_pos = row * ROW_SIZE + right
            has_piece |= (boards[turn][0] >> bit_pos) & 1
        if has_piece:
            break
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
        current_row = (boards[turn][0] >> row_shift) & ((1 << (right_exp + 1)) - (1 << left_exp))
        current_row_opponent = (boards[not turn][0] >> row_shift) & ((1 << (right_exp + 1)) - (1 << left_exp))
        
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
            vertical_bits |= ((boards[turn][0] >> bit_pos) & 1) << (row - top_exp)
            vertical_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << (row - top_exp)
        
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
                diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
            
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
                anti_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                anti_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
    
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

def minimax(boards, depth, alpha, beta, maximizing_player, turn, captures, count, t, transposition_table=None):
    if transposition_table is None:
        transposition_table = {}

    board_hash = hash((boards[0][0], boards[1][0]))
    if board_hash in transposition_table and transposition_table[board_hash][1] >= depth:
        return transposition_table[board_hash][0]

    if depth == 1:
        count[0] += 1
        value = bitwise_heuristic(boards, turn, captures[turn], captures[not turn])
        transposition_table[board_hash] = (value, depth)
        return value

    moves = generate_legal_moves(boards, turn, captures[turn], t)
    
    if depth > 2:
        # Move ordering
        move_values = []
        for move in moves:
            # Quick static evaluation
            new_boards = copy.deepcopy(boards)
            handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            value = bitwise_heuristic(new_boards, turn, captures[turn], captures[not turn])
            move_values.append((move, value))
        
        # Sort moves based on evaluation
        move_values.sort(key=lambda x: x[1], reverse=maximizing_player)
        moves = [move for move, _ in move_values]

    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return float('inf')
            eval = minimax(new_boards, depth - 1, alpha, beta, False, not turn, captures, count, t, transposition_table)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (max_eval, depth)
        return max_eval
    else:
        min_eval = float('inf')
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return float('-inf')
            eval = minimax(new_boards, depth - 1, alpha, beta, True, not turn, captures, count, t, transposition_table)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (min_eval, depth)
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
        is_win = is_winning_move(boards, turn, move, [captures[0], captures[1]])

        if is_win:  # Winning move found
            print("Found winning move")
            return move

    # If no winning move, do minimax search
    for move in moves:
        new_boards = copy.deepcopy(boards)

        is_win = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])

        if not is_win:  # Only evaluate non-winning moves
            eval = minimax(new_boards, DEPTH, alpha, beta, False, not turn, captures, count, t)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            alpha = max(alpha, eval)

    print(f"Evaluated {count[0]} positions")
    print(f"Time spent generating moves: {t[0]:.2f}s")
    return best_move

