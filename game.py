from macro import DIRECTIONS
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

def is_capture(board_turn, board_not_turn, y, x):
    BOARD_SIZE = 19
    directions = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]

    for dy, dx in directions:
        y3, x3 = y + dy*3, x + dx*3       # own piece
        if (x3 < 0 or x3 >= BOARD_SIZE or y3 < 0 or y3 >= BOARD_SIZE):
            continue

        # Calculate bit positions
        bit1 = (y + dy) * BOARD_SIZE + (x + dx)
        bit2 = (y + dy*2) * BOARD_SIZE + (x + dx*2)
        bit3 = y3 * BOARD_SIZE + x3

        # Check if pattern matches: empty->opponent->opponent->player
        if ((board_turn >> bit3) & 1) and \
           ((board_not_turn >> bit2) & 1) and \
           ((board_not_turn >> bit1) & 1):
            return True

    return False

def check_capture(boards, y, x, turn):
    BOARD_SIZE = 19
    capture = 0
    positions = []
    
    # Each direction - right, down-right, down, down-left, left, up-left, up, up-right
    directions = [
        (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)
    ]

    for dy, dx in directions:
        # Calculate positions for 3 pieces in line
        y1, x1 = y + dy, x + dx           # first adjacent
        y2, x2 = y + dy*2, x + dx*2       # second adjacent  
        y3, x3 = y + dy*3, x + dx*3       # own piece

        # Check bounds for all positions
        if (x3 < 0 or x3 >= BOARD_SIZE or y3 < 0 or y3 >= BOARD_SIZE):
            continue

        # Calculate bit positions
        bit1 = y1 * BOARD_SIZE + x1
        bit2 = y2 * BOARD_SIZE + x2  
        bit3 = y3 * BOARD_SIZE + x3

        # Check if pattern matches: empty->opponent->opponent->player
        if ((boards[turn][0] >> bit3) & 1) and \
           ((boards[not turn][0] >> bit2) & 1) and \
           ((boards[not turn][0] >> bit1) & 1):
            capture += 1
            positions.extend([bit1, bit2])

    return capture, positions


def place_piece_old(bitboard, move, set_bit=True):
    row, col = move
    bit_position = row * BOARD_SIZE + col
    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)

def place_piece(bitboard, move, set_bit=True):
    if isinstance(move, tuple):
        # Handle (row, col) coordinates
        row, col = move
        bit_position = row * BOARD_SIZE + col
    else:
        # Handle bit position directly
        bit_position = move

    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)


def is_occupied(board, pos): # y, x
    y, x = pos
    bit_position = y * BOARD_SIZE + x # y * 19 + x
    return (board[0] >> bit_position) & 1

def winning_line(board):
    BOARD_SIZE = 19
    directions = [(0,1), (1,1), (1,0), (1,-1)]  # 4 directions for efficiency

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            bit_pos = i * BOARD_SIZE + j
            if not ((board[0] >> bit_pos) & 1):  # inline is_occupied
                continue
            
            for dy, dx in directions:
                valid = True
                for k in range(1, 5):  # check next 4 positions
                    y, x = i + k*dy, j + k*dx
                    if not (0 <= y < BOARD_SIZE and 0 <= x < BOARD_SIZE):
                        valid = False
                        break
                    new_bit_pos = y * BOARD_SIZE + x
                    if not ((board[0] >> new_bit_pos) & 1):
                        valid = False
                        break
                if valid:
                    return ((i,j), (i+dy,j+dx), (i+2*dy,j+2*dx), (i+3*dy,j+3*dx), (i+4*dy,j+4*dx))
    return None

def has_winning_line(board):
    BOARD_SIZE = 19
    directions = [(0,1), (1,1), (1,0), (1,-1)]
    
    # Pre-calculate bounds to avoid repeated checks
    for i in range(BOARD_SIZE - 4):  # No need to check last 4 rows
        for j in range(BOARD_SIZE):
            bit_pos = i * BOARD_SIZE + j
            
            # Skip if current position is empty
            if not (board & (1 << bit_pos)):
                continue
                
            for dy, dx in directions:
                # Early bounds check
                end_y, end_x = i + 4*dy, j + 4*dx
                if (end_y >= BOARD_SIZE or end_y < 0 or 
                    end_x >= BOARD_SIZE or end_x < 0):
                    continue
                
                # Check all 5 positions in one go
                valid = True
                for k in range(1, 5):
                    next_pos = (i + k*dy) * BOARD_SIZE + (j + k*dx)
                    if not (board & (1 << next_pos)):
                        valid = False
                        break
                        
                if valid:
                    return True
                    
    return False

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
    if line is None or (capture == 4 and is_line_capture(boards, line, turn)): # if opponent has 4 captures and he can eat one more during the event where we have 5 in a row 
        return False
    return True

# this is readable version. but not the fastest. 
def check_double_three(board_turn, board_not_turn, y, x):
    BOARD_SIZE = 19
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

def is_legal_lite_py(captures, board_turn, board_not_turn, y, x):
    if not is_capture(board_turn, board_not_turn, y, x) and (captures == 4 and has_winning_line(board_not_turn)) or check_double_three(board_turn, board_not_turn, y, x):
        return False
    return True


# 0, boards, (y, x), 0
def is_legal(captures, boards, move, turn):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards, y, x, turn) 
    if not capture and ((captures == 4 and winning_line(boards[not turn])) or check_double_three(boards[turn][0], boards[not turn][0], y, x)):
        return False, capture, pos
    return True, capture, pos

# our 2 boards
# which turn
# move that was made
# current captures for both players
def handle_move(boards, turn, move, captures):
    # turbn is 0 for black
    # 0, boards, (y, x), 0
    legal, has_capture, pos = is_legal(captures[turn], boards, move, turn)
    if not legal:
        return None, has_capture
    captures[turn] += has_capture
    boards[turn][0] |= (1 << move)
    if has_capture:
        for p in pos:
            boards[not turn][0] &= ~(1 << p)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, has_capture
    return False, has_capture
