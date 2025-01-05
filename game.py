from macro import DIRECTIONS, THREE, DIRECTION_MIN
from board import coordinate, out_of_bounds, SIZE
BOARD_SIZE = SIZE - 1

def display_board(player1, player2):
    for row in range(SIZE - 1):
        row_display = []
        for col in range(SIZE - 1):
            if is_occupied(player1, (row, col)):
                row_display.append('X')
            elif is_occupied(player2, (row, col)):
                row_display.append('O')
            else:
                row_display.append('.')
        print(' '.join(row_display))
    print("---------------")

# boards, (y, x), 0
def check_capture(boards, move, turn):
    capture = 0
    capture_positions = []
    for pos in DIRECTIONS:
        # check for out of bounds
        if out_of_bounds(move + pos * 3):
            continue
        # check for players piece if present
        if not is_occupied(boards[turn], move + pos * 3):
            continue
        # check for opponent piece to eat
        if is_occupied(boards[not turn], move + pos * 2) and is_occupied(boards[not turn], move + pos):
            capture += 1
            capture_positions.append(move + pos * 2)
            capture_positions.append(move + pos)

    return capture, capture_positions

def place_piece(bitboard, move, set_bit=True):
    row, col = move
    bit_position = row * BOARD_SIZE + col
    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)

def is_occupied(board, pos): # y, x
    y, x = pos
    bit_position = y * BOARD_SIZE + x # y * 19 + x
    return (board[0] >> bit_position) & 1

def winning_line(board):
    size = BOARD_SIZE

    for i in range(size):
        for j in range(size):
            pos = (i, j)
            if not is_occupied(board, pos):
                continue
            for direction in DIRECTION_MIN:
                di, dj = direction.co
                if all(0 <= i + k*di < size and 0 <= j + k*dj < size and is_occupied(board, (i + k*di, j + k*dj)) for k in range(5)):
                    return ((i, j), (i + 1*di, j + 1*dj), (i + 2*di, j + 2*dj), (i + 3*di, j + 3*dj), (i + 4*di, j + 4*dj))
    return None

def is_eatable(boards, pos, direction, turn):
    if not is_occupied(boards[turn], pos + direction):
        return False
    if is_occupied(boards[not turn], pos - direction) and not (is_occupied(boards[not turn], pos + direction * 2) or is_occupied(boards[turn], pos + direction * 2)):
        return True
    if is_occupied(boards[not turn], pos + direction * 2) and not (is_occupied(boards[not turn], pos - direction) or is_occupied(boards[turn], pos - direction)):
        return True
    return False

def is_line_capture(boards, line, turn):
    for pos in line:
        pos = coordinate(pos)
        for direction in DIRECTIONS:
            if out_of_bounds(pos + direction * 2) or out_of_bounds(pos - direction):
                continue
            if is_eatable(boards, pos, direction, turn):
                return True
    return False

def is_won(boards, turn, capture):
    line = winning_line(boards[turn])
    if line is None or (capture == 4 and is_line_capture(boards, line, turn)):
        return False
    return True

# # boards, (y, x), 0
# def check_double_three(board, move, turn): # make it efficient

#     def extract_segment(start, direction): #very unoptimized
#         segment = 0
#         for i in range(pattern_width): # 0, 1, 2, 3, 4
#             current = start + direction * i
#             if out_of_bounds(current):
#                 return -1
#             bit_position = coord_to_bit(current)
#             if (opponent_board[0] >> bit_position) & 1:
#                 return -1
#             segment |= ((current_board[0] >> bit_position) & 1) << i
#         return segment

#     def matches_pattern():
#         count = 0
#         for direction in DIRECTION_MIN: # (0, 1), (1, 0), (1, 1), (1, -1) right, down, right down, right up 
#             for offset in range(-pattern_width + 2, 0): # -3, -2, -1
#                 start = move + direction * offset # (9, 6)
#                 segment = extract_segment(coordinate(start), direction)
#                 if segment == pattern_int:
#                     count += 1
#                     break
#         return count

#     place_piece(board[turn], move.co) # place piece on the board
#     current_board = board[turn] #unnecessary creations
#     opponent_board = board[not turn]

#     count = 0

#     for pattern_int, pattern_width in THREE: # (0b01110, 5)
#         count +=  matches_pattern()
#         if count > 1:
#             place_piece(board[turn], move.co, False)
#             return True
#     place_piece(board[turn], move.co, False)
#     return False


def check_double_three(board, move, turn): # read and check for efficiency!!!!!!!!!!!!!!!!!!!!!11
    BOARD_SIZE = 19  # Adjust as needed
    y, x = move.co # 9, 9
    margin = 4

    y_min = max(0, y - margin) # 5
    y_max = min(BOARD_SIZE - 1, y + margin) # 13
    x_min = max(0, x - margin) # 5
    x_max = min(BOARD_SIZE - 1, x + margin) # 13

    place_piece(board[turn], move.co)
    current_board = board[turn]
    opponent_board = board[not turn]

    def extract_segment(y_start, x_start, y_dir, x_dir):
        segment = 0
        for i in range(pattern_width): # 0, 1, 2, 3, 4
            r = y_start + y_dir * i
            c = x_start + x_dir * i
            if not (y_min <= r <= y_max and x_min <= c <= x_max): # this checks for out of bounds
                return -1
            # if out_of_bounds((r, c)):
            #     return -1
            bit_pos = r * BOARD_SIZE + c
            if (opponent_board[0] >> bit_pos) & 1:
                return -1
            segment |= ((current_board[0] >> bit_pos) & 1) << i
        return segment

    def matches_pattern():
        count = 0
        for y_dir, x_dir in [(0, 1), (1, 0), (1, 1), (1, -1)]: # right, down, right down, left down
            for offset in range(-pattern_width + 2, 1): # -3, -2, -1, 0
                y_start, x_start = (y + y_dir * offset, x + x_dir * offset)
                if extract_segment(y_start, x_start, y_dir, x_dir) == pattern_int:
                    count += 1
                    if count > 1:
                       return count
        return count

    total = 0
    for pattern_int, pattern_width in THREE:
        total += matches_pattern()
        if total > 1:
            place_piece(board[turn], move.co, False)
            return True

    place_piece(board[turn], move.co, False)
    return False

# now i want to start check_double_three() from beginning. lets for now check only horizontal direction for pattern 0b01110. your goal is to extract from map 5 to 7 bits,  (pattern size is 5) depends on a how close to border we are. if we are on it we dont even check on nothing. We first calculate bits_space which is 5 to 7 bits depends on how close we to the border. than we take mask of that size and check if there is a opponent point in thet area. if result is != 0, we stop. then we take mask of  bits_space bits and apply it to current map. then we take its first  5 bits with mask and we compare it to pattern PATTERN_1. if it is same, we stop and do count as 1. if not, we continue by shifting one bit and



def check_double_three(board, move, turn):
    y, x = move.co # 3, 3
    BOARD_SIZE = 19
    PATTERN_1 = 0b01110
    PATTERN_2 = 0b010110
    PATTERN_3 = 0b011010
    PATTERN_1_LEN = 5
    PATTERN_2_3_LEN = 6
    MASK_5 = 0b11111
    MASK_6 = 0b111111
    MAX_EXTRA = 3
    MAX_EXTRA_PATTERN_2_3 = 4


    place_piece(board[turn], move.co) ## later change it on piece of code.

    count = 0
    
    # Calculate horizontal space
    left_space = min(x, MAX_EXTRA) # 3
    right_space = min((BOARD_SIZE - 1) - x, MAX_EXTRA) # 3
    bits_space = left_space + right_space + 1
    if bits_space >= PATTERN_1_LEN:
        # Build mask
        mask = 0
        if bits_space == 7:
            mask = 0b1111111
        elif bits_space == 6:
            mask = 0b111111
        elif bits_space == 5:
            mask = 0b11111
        start_col = x - left_space # 0
        # Get full row data for both players
        current_row = (board[turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
        opponent_row = (board[not turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)

        # Extract bits_space bits
        extracted_self = (current_row >> start_col) & mask
        extracted_opp  = (opponent_row >> start_col) & mask

        for shift in range(bits_space - PATTERN_1_LEN + 1):
            if ((extracted_opp >> shift) & MASK_5) == 0:
                if ((extracted_self >> shift) & MASK_5) == PATTERN_1:
                    count += 1
                    break
        

    # 2. Vertical
    top_space = min(y, MAX_EXTRA)
    bottom_space = min((BOARD_SIZE - 1) - y, MAX_EXTRA)
    v_bits_space = top_space + bottom_space + 1
    if v_bits_space >= PATTERN_1_LEN:
        extracted_self_v = 0
        extracted_opp_v = 0
        start_row = y - top_space
        for i in range(v_bits_space):
            bit_pos = (start_row + i) * BOARD_SIZE + x
            extracted_self_v |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_v  |= ((board[not turn][0] >> bit_pos) & 1) << i

        for shift in range(v_bits_space - PATTERN_1_LEN + 1):
            if ((extracted_opp_v >> shift) & MASK_5) == 0:
                if ((extracted_self_v >> shift) & MASK_5) == PATTERN_1:
                    count += 1
                    break
        
    # 3. Diagonal (\) top-left to bottom-right
    up_left_space = min(y, x, MAX_EXTRA)
    down_right_space = min((BOARD_SIZE - 1) - y, (BOARD_SIZE - 1) - x, MAX_EXTRA)
    d_bits_space = up_left_space + down_right_space + 1
    if d_bits_space >= PATTERN_1_LEN:
        extracted_self_d = 0
        extracted_opp_d  = 0
        start_y = y - up_left_space
        start_x = x - up_left_space
        for i in range(d_bits_space):
            bit_pos = (start_y + i) * BOARD_SIZE + (start_x + i)
            extracted_self_d |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_d  |= ((board[not turn][0] >> bit_pos) & 1) << i

        for shift in range(d_bits_space - PATTERN_1_LEN + 1):
            if ((extracted_opp_d >> shift) & MASK_5) == 0:
                if ((extracted_self_d >> shift) & MASK_5) == PATTERN_1:
                    count += 1
                    break

    # 4. Diagonal (/) bottom-left to top-right
    down_left_space = min((BOARD_SIZE - 1) - y, x, MAX_EXTRA)
    up_right_space = min(y, (BOARD_SIZE - 1) - x, MAX_EXTRA)
    d2_bits_space = down_left_space + up_right_space + 1
    if d2_bits_space >= PATTERN_1_LEN:
        extracted_self_d2 = 0
        extracted_opp_d2  = 0
        start_y2 = y + down_left_space
        start_x2 = x - down_left_space
        for i in range(d2_bits_space):
            # increment y up or down while incrementing x in the opposite direction
            bit_pos = (start_y2 - i) * BOARD_SIZE + (start_x2 + i)
            extracted_self_d2 |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_d2  |= ((board[not turn][0] >> bit_pos) & 1) << i

        for shift in range(d2_bits_space - PATTERN_1_LEN + 1):
            if ((extracted_opp_d2 >> shift) & MASK_5) == 0:
                if ((extracted_self_d2 >> shift) & MASK_5) == PATTERN_1:
                    count += 1
                    break
        

    place_piece(board[turn], move.co, False)
    return count > 1



def check_double_three(board, move, turn):
    y, x = move.co
    BOARD_SIZE = 19

    PATTERN_1 = 0b01110       # length 5
    PATTERN_2 = 0b010110      # length 6
    PATTERN_3 = 0b011010      # length 6

    PATTERN_1_LEN = 5
    PATTERN_2_3_LEN = 6

    MASK_5 = 0b11111
    MASK_6 = 0b111111

    # Separate max extra expansions for each pattern length
    MAX_EXTRA_PATTERN_1 = 3
    MAX_EXTRA_PATTERN_2_3 = 4

    # Helper to compute left/right spaces for any pattern length
    def compute_spaces(coord, length):
        # coord: (y or x)
        # length: either 5 or 6
        max_extra = MAX_EXTRA_PATTERN_1 if length == 5 else MAX_EXTRA_PATTERN_2_3
        left_or_top = min(coord, max_extra)
        right_or_bottom = min((BOARD_SIZE - 1) - coord, max_extra)
        return left_or_top, right_or_bottom

    place_piece(board[turn], move.co)  # place piece temporarily
    count = 0

    def check_5_bits(self_bits, opp_bits, space):
        for shift in range(space - PATTERN_1_LEN + 1):
            if ((opp_bits >> shift) & MASK_5) == 0:
                if ((self_bits >> shift) & MASK_5) == PATTERN_1:
                    return 1
        return 0

    def check_6_bits(self_bits, opp_bits, space):
        hits = 0
        for shift in range(space - PATTERN_2_3_LEN + 1):
            if ((opp_bits >> shift) & MASK_6) == 0:
                chunk = ((self_bits >> shift) & MASK_6)
                if chunk == PATTERN_2 or chunk == PATTERN_3:
                    hits += 1
                    break
        return hits

    # ------------------------------------
    # Check horizontal
    left_space, right_space = compute_spaces(x, PATTERN_1_LEN)
    bits_space = left_space + right_space + 1
    if bits_space >= PATTERN_1_LEN:
        start_col = x - left_space
        current_row = (board[turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
        opponent_row = (board[not turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
        mask = (1 << bits_space) - 1

        extracted_self = (current_row >> start_col) & mask
        extracted_opp  = (opponent_row >> start_col) & mask
        count += check_5_bits(extracted_self, extracted_opp, bits_space)

        # For 6-bit patterns, use max extra for 6
        left_space_6, right_space_6 = compute_spaces(x, PATTERN_2_3_LEN)
        bits_space_6 = left_space_6 + right_space_6 + 1
        if bits_space_6 >= PATTERN_2_3_LEN:
            start_col_6 = x - left_space_6
            row_self_6 = (current_row >> start_col_6) & ((1 << bits_space_6) - 1)
            row_opp_6  = (opponent_row >> start_col_6) & ((1 << bits_space_6) - 1)
            count += check_6_bits(row_self_6, row_opp_6, bits_space_6)

    # ------------------------------------
    # Check vertical
    top_space, bottom_space = compute_spaces(y, PATTERN_1_LEN)
    v_bits_space = top_space + bottom_space + 1
    if v_bits_space >= PATTERN_1_LEN:
        extracted_self_v = 0
        extracted_opp_v  = 0
        start_row = y - top_space
        for i in range(v_bits_space):
            bit_pos = (start_row + i) * BOARD_SIZE + x
            extracted_self_v |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_v  |= ((board[not turn][0] >> bit_pos) & 1) << i
        count += check_5_bits(extracted_self_v, extracted_opp_v, v_bits_space)

        # For 6-bit patterns
        top_space_6, bottom_space_6 = compute_spaces(y, PATTERN_2_3_LEN)
        v_bits_space_6 = top_space_6 + bottom_space_6 + 1
        if v_bits_space_6 >= PATTERN_2_3_LEN:
            self_v6 = 0
            opp_v6  = 0
            start_row_6 = y - top_space_6
            for i in range(v_bits_space_6):
                bit_pos_6 = (start_row_6 + i) * BOARD_SIZE + x
                self_v6 |= ((board[turn][0] >> bit_pos_6) & 1) << i
                opp_v6  |= ((board[not turn][0] >> bit_pos_6) & 1) << i
            count += check_6_bits(self_v6, opp_v6, v_bits_space_6)

    # ------------------------------------
    # Diagonal (\)
    up_left_space, down_right_space = compute_spaces(min(y, x), PATTERN_1_LEN)
    d_bits_space = up_left_space + down_right_space + 1
    if d_bits_space >= PATTERN_1_LEN:
        extracted_self_d = 0
        extracted_opp_d  = 0
        start_y = y - up_left_space
        start_x = x - up_left_space
        for i in range(d_bits_space):
            bit_pos = (start_y + i) * BOARD_SIZE + (start_x + i)
            extracted_self_d |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_d  |= ((board[not turn][0] >> bit_pos) & 1) << i
        count += check_5_bits(extracted_self_d, extracted_opp_d, d_bits_space)

        # For 6-bit patterns
        up_left_space_6, down_right_space_6 = compute_spaces(min(y, x), PATTERN_2_3_LEN)
        d_bits_space_6 = up_left_space_6 + down_right_space_6 + 1
        if d_bits_space_6 >= PATTERN_2_3_LEN:
            self_d6 = 0
            opp_d6  = 0
            start_y_6 = y - up_left_space_6
            start_x_6 = x - up_left_space_6
            for i in range(d_bits_space_6):
                bit_pos_6 = (start_y_6 + i) * BOARD_SIZE + (start_x_6 + i)
                self_d6 |= ((board[turn][0] >> bit_pos_6) & 1) << i
                opp_d6  |= ((board[not turn][0] >> bit_pos_6) & 1) << i
            count += check_6_bits(self_d6, opp_d6, d_bits_space_6)

    # ------------------------------------
    # Diagonal (/)
    # For the slash diagonal, we figure out how many steps we can go downward-left, upward-right
    # We'll do a helper function for that as well if needed
    def slash_spaces(y, x, p_len):
        max_ex = get_max_extra(p_len)
        down_left = min((BOARD_SIZE - 1) - y, x, max_ex)
        up_right  = min(y, (BOARD_SIZE - 1) - x, max_ex)
        return down_left, up_right

    # We'll define once again get_max_extra or inline it:
    def get_max_extra(l):
        return MAX_EXTRA_PATTERN_1 if l == 5 else MAX_EXTRA_PATTERN_2_3

    # For pattern 5
    down_left_space_5, up_right_space_5 = slash_spaces(y, x, PATTERN_1_LEN)
    d2_bits_space = down_left_space_5 + up_right_space_5 + 1
    if d2_bits_space >= PATTERN_1_LEN:
        extracted_self_d2 = 0
        extracted_opp_d2  = 0
        start_y2 = y + down_left_space_5
        start_x2 = x - down_left_space_5
        for i in range(d2_bits_space):
            bit_pos = (start_y2 - i) * BOARD_SIZE + (start_x2 + i)
            extracted_self_d2 |= ((board[turn][0] >> bit_pos) & 1) << i
            extracted_opp_d2  |= ((board[not turn][0] >> bit_pos) & 1) << i
        count += check_5_bits(extracted_self_d2, extracted_opp_d2, d2_bits_space)

    # For pattern 6
    down_left_space_6, up_right_space_6 = slash_spaces(y, x, PATTERN_2_3_LEN)
    d2_bits_space_6 = down_left_space_6 + up_right_space_6 + 1
    if d2_bits_space_6 >= PATTERN_2_3_LEN:
        self_d2_6 = 0
        opp_d2_6  = 0
        start_y2_6 = y + down_left_space_6
        start_x2_6 = x - down_left_space_6
        for i in range(d2_bits_space_6):
            bit_pos_6 = (start_y2_6 - i) * BOARD_SIZE + (start_x2_6 + i)
            self_d2_6 |= ((board[turn][0] >> bit_pos_6) & 1) << i
            opp_d2_6  |= ((board[not turn][0] >> bit_pos_6) & 1) << i
        count += check_6_bits(self_d2_6, opp_d2_6, d2_bits_space_6)

    place_piece(board[turn], move.co, False)  # remove piece
    return count > 1

def check_double_three(board, move, turn):
    y, x = move.co
    BOARD_SIZE = 19
    PATTERNS = [(0b01110, 5), (0b010110, 6), (0b011010, 6)]
    MASKS = {5: 0b11111, 6: 0b111111}

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

    place_piece(board[turn], move.co)
    count = 0

    # Check all directions
    for pattern_len in [5, 6]:
        # Horizontal
        left, bits_space = compute_spaces(x, pattern_len)
        if bits_space >= pattern_len:
            row_self = (board[turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
            row_opp = (board[not turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
            extracted_self = (row_self >> (x - left)) & ((1 << bits_space) - 1)
            extracted_opp = (row_opp >> (x - left)) & ((1 << bits_space) - 1)
            count += check_pattern(extracted_self, extracted_opp, bits_space, pattern_len)

        # Vertical
        top, v_bits_space = compute_spaces(y, pattern_len)
        if v_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(v_bits_space):
                bit_pos = (y - top + i) * BOARD_SIZE + x
                extracted_self |= ((board[turn][0] >> bit_pos) & 1) << i
                extracted_opp |= ((board[not turn][0] >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, v_bits_space, pattern_len)

        # Diagonal (\)
        d_left, d_bits_space = compute_spaces(min(y, x), pattern_len)
        if d_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(d_bits_space):
                bit_pos = (y - d_left + i) * BOARD_SIZE + (x - d_left + i)
                extracted_self |= ((board[turn][0] >> bit_pos) & 1) << i
                extracted_opp |= ((board[not turn][0] >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, d_bits_space, pattern_len)

        # Diagonal (/)
        d_down = min((BOARD_SIZE - 1) - y, x, pattern_len - 2)
        d_up = min(y, (BOARD_SIZE - 1) - x, pattern_len - 2)
        d2_bits_space = d_down + d_up + 1
        if d2_bits_space >= pattern_len:
            extracted_self = extracted_opp = 0
            for i in range(d2_bits_space):
                bit_pos = (y + d_down - i) * BOARD_SIZE + (x - d_down + i)
                extracted_self |= ((board[turn][0] >> bit_pos) & 1) << i
                extracted_opp |= ((board[not turn][0] >> bit_pos) & 1) << i
            count += check_pattern(extracted_self, extracted_opp, d2_bits_space, pattern_len)

        if count > 1:
            break

    place_piece(board[turn], move.co, False)
    return count > 1

# 0, boards, (y, x), 0
def is_legal(captures, boards, move, turn):
    capture, pos = check_capture(boards, move, turn) # will return 0, [] if no capture otherwise 1, [pos1, pos2] where pos1 and pos2 are the positions to remove (y, x)
    if not capture and ((captures == 4 and winning_line(boards[not turn])) or check_double_three(boards, move, turn)):
        return False, capture, pos
    return True, capture, pos

# our 2 boards
# which turn
# move that was made
# current captures for both players
def handle_move(boards, turn, move, captures):
    # turbn is 0 for black
    # 0, boards, (y, x), 0
    legal, capture, pos = is_legal(captures[turn], boards, move, turn)
    if not legal:
        return None, capture
    captures[turn] += capture
    place_piece(boards[turn], move.co)
    if capture:
        for p in pos:
            place_piece(boards[not turn], p, False)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture
