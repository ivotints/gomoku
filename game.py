from wrapper import is_won
BOARD_SIZE = 19

def is_occupied(board, bit_position):
    return (board[0] >> bit_position) & 1

def check_capture(board_turn, board_not_turn, y, x):
    capture = 0
    pos = [0] * 16
    directions = [
        (0,1), (1,1), (1,0), (1,-1),
        (0,-1), (-1,-1), (-1,0), (-1,1)
    ]
    
    for dir_y, dir_x in directions:
        y3 = y + dir_y * 3
        x3 = x + dir_x * 3
        
        if x3 < 0 or x3 >= BOARD_SIZE or y3 < 0 or y3 >= BOARD_SIZE:
            continue
            
        bit1 = (y + dir_y) * BOARD_SIZE + (x + dir_x)
        bit2 = (y + dir_y * 2) * BOARD_SIZE + (x + dir_x * 2)
        bit3 = y3 * BOARD_SIZE + x3
        
        if ((board_turn >> bit3) & 1) and ((board_not_turn >> bit2) & 1) and ((board_not_turn >> bit1) & 1):
            pos[capture * 2] = bit1
            pos[capture * 2 + 1] = bit2
            capture += 1
            
    return capture, pos

def winning_line(board):
    directions = [(0,1), (1,1), (1,0), (1,-1)]  # 4 directions for efficiency

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            bit_pos = i * BOARD_SIZE + j
            if not ((board >> bit_pos) & 1):  # inline is_occupied
                continue
            
            for dy, dx in directions:
                valid = True
                for k in range(1, 5):  # check next 4 positions
                    y, x = i + k*dy, j + k*dx
                    if not (0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE):
                        valid = False
                        break
                    new_bit_pos = y * BOARD_SIZE + x
                    if not ((board >> new_bit_pos) & 1):
                        valid = False
                        break
                if valid:
                    return ((i,j), (i+dy,j+dx), (i+2*dy,j+2*dx), (i+3*dy,j+3*dx), (i+4*dy,j+4*dx))
    return None

# this is readable version. but not the fastest.
def check_double_three(board_turn, board_not_turn, y, x):
    PATTERNS = [(0b01110, 5), (0b010110, 6), (0b011010, 6)]
    MASKS = {5: 0b11111, 6: 0b111111}

    # Inline place_piece
    bit_position = y * BOARD_SIZE + x
    board_turn |= (1 << bit_position)  # Set bit
    count = 0

    def check_pattern(self_bits, opp_bits, space, pattern_len):
        pattern = PATTERNS[0][0] if pattern_len == 5 else PATTERNS[1][0]
        pattern2 = PATTERNS[2][0] if pattern_len == 6 else 0
        mask = MASKS[pattern_len]
        
        for shift in range(space - pattern_len + 1):
            if ((opp_bits >> shift) & mask) == 0:
                chunk = (self_bits >> shift) & mask
                if chunk == pattern or chunk == pattern2:
                    return 1
        return 0

    def compute_spaces(coord, pattern_len):
        max_extra = pattern_len - 2
        left = min(coord, max_extra)
        right = min((BOARD_SIZE - 1) - coord, max_extra)
        return left, left + right + 1


    # Check all directions
    for pattern_len in [5, 6]:
        # Horizontal
        left, bits_space = compute_spaces(x, pattern_len)
        if bits_space >= pattern_len:
            row_self = (board_turn >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
            row_opp = (board_not_turn >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
            extracted_self = (row_self >> (x - left)) & ((1 << bits_space) - 1)
            extracted_opp = (row_opp >> (x - left)) & ((1 << bits_space) - 1)
            count += check_pattern(extracted_self, extracted_opp, bits_space, pattern_len)




        # Vertical
        top, v_bits_space = compute_spaces(y, pattern_len)
        if v_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(v_bits_space):
                bit_pos = (y - top + i) * BOARD_SIZE + x
                extracted_self |= ((board_turn >> bit_pos) & 1) << i
                extracted_opp |= ((board_not_turn >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, v_bits_space, pattern_len)



        # Diagonal (\)
        d_left, d_bits_space = compute_spaces(min(y, x), pattern_len)
        if d_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(d_bits_space):
                bit_pos = (y - d_left + i) * BOARD_SIZE + (x - d_left + i)
                extracted_self |= ((board_turn >> bit_pos) & 1) << i
                extracted_opp |= ((board_not_turn >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, d_bits_space, pattern_len)



        # Diagonal (/)
        d_down = min((BOARD_SIZE - 1) - y, x, pattern_len - 2)
        d_up = min(y, (BOARD_SIZE - 1) - x, pattern_len - 2)
        d2_bits_space = d_down + d_up + 1
        if d2_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(d2_bits_space):
                bit_pos = (y + d_down - i) * BOARD_SIZE + (x - d_down + i)
                extracted_self |= ((board_turn >> bit_pos) & 1) << i
                extracted_opp |= ((board_not_turn >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, d2_bits_space, pattern_len)

    board_turn &= ~(1 << bit_position)  # Unset bit
    return count > 1

def is_legal(captures, boards, move, turn):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards[turn][0], boards[not turn][0], y, x)
    if not capture and ((captures == 4 and winning_line(boards[not turn][0])) or check_double_three(boards[turn][0], boards[not turn][0], y, x)):
        return False, capture, pos
    return True, capture, pos

def handle_move(game, boards, turn, move, captures):
    legal, has_capture, pos = is_legal(captures[turn], boards, move, turn)
    if not legal:
        return None, has_capture
    game.save_move()
    game.last_move = move
    captures[turn] += has_capture
    boards[turn][0] |= (1 << move)
    if has_capture:
        for p in pos:
            boards[not turn][0] &= ~(1 << p)
    if captures[turn] > 4 or is_won(boards[turn][0], boards[not turn][0], captures[not turn]):
        return True, has_capture
    return False, has_capture
