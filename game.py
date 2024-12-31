from macro import DIRECTIONS, THREE, DIRECTION_MIN
from board import coordinate, out_of_bounds, coord_to_bit, SIZE

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

def check_capture(boards, move, turn):
    capture = 0
    capture_positions = []
    for pos in DIRECTIONS:
        if out_of_bounds(move + pos * 3):
            continue
        if not is_occupied(boards[turn], move + pos * 3):
            continue
        if is_occupied(boards[not turn], move + pos * 2) and is_occupied(boards[not turn], move + pos):
            capture += 1
            capture_positions.append(move + pos * 2)
            capture_positions.append(move + pos)
    return capture, capture_positions

def place_piece(bitboard, move, set_bit=True):
    bit_position = coord_to_bit(move)
    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)

def is_occupied(board, pos):
    bit_position = coord_to_bit(pos)
    return (board[0] >> bit_position) & 1

def winning_line(board):
    directions = [
        [(0, 1), (1, 0), (1, 1), (1, -1)],
        [((SIZE - 1), SIZE - 5), (SIZE - 5, (SIZE - 1)), (SIZE - 5, SIZE - 5), (SIZE - 5, SIZE - 5)]
    ]
    
    for d, bounds in zip(directions[0], directions[1]):
        di, dj = d
        bound_i, bound_j = bounds
        
        for i in range(bound_i):
            j = 0
            while j < bound_j:
                if all(is_occupied(board, (i + k*di, j + k*dj)) 
                      for k in range(5)):
                    return ((i,j), (i + 1*di, j + 1*dj), (i + 2*di, j + 2*dj), (i + 3*di, j + 3*dj), (i + 4*di, j + 4*dj))
                j += 1
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

def check_double_three(board, move, turn):

    def extract_segment(start, direction):
        segment = 0
        for i in range(pattern_width):
            current = start + direction * i
            if out_of_bounds(current):
                return -1
            bit_position = coord_to_bit(current)
            if (opponent_board[0] >> bit_position) & 1:
                return -1
            segment |= ((current_board[0] >> bit_position) & 1) << i
        return segment

    def matches_pattern():
        count = 0
        for direction in DIRECTION_MIN:
            for offset in range(-pattern_width + 2, 0):
                start = move + direction * offset
                segment = extract_segment(coordinate(start), direction)
                if segment == pattern_int:
                    count += 1
                    break
        return count

    place_piece(board[turn], move.co)
    current_board = board[turn]
    opponent_board = board[not turn]

    count = 0

    for pattern_int, pattern_width in THREE:
        count +=  matches_pattern()
        if count >= 2:
            place_piece(board[turn], move.co, False)
            return True
    place_piece(board[turn], move.co, False)
    return False

def is_legal(captures, boards, move, turn):
    capture, pos = check_capture(boards, move, turn)
    if not capture and ((captures == 4 and winning_line(boards[not turn])) or check_double_three(boards, move, turn)):
        return False, capture, pos
    return True, capture, pos

def handle_move(boards, turn, move, captures):
    legal, capture, pos = is_legal(captures[turn], boards, move, turn)
    if not legal:
        return None, capture
    captures[turn] += capture
    place_piece(boards[turn], move.co)
    if capture:
        for p in pos:
            place_piece(boards[not turn], p, False)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        print("capture: ", captures)
        print("won: ", is_won(boards, turn, captures[not turn]))
        display_board(boards[0], boards[1])
        return True, capture
    return False, capture
