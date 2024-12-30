from macro import DIRECTIONS
from board import coordinate, out_of_bounds, coord_to_bit, SIZE

def check_capture(boards, move, turn, captures, clear=True):
    capture = 0
    for pos in DIRECTIONS:
        if out_of_bounds(move + pos * 3):
            continue
        if not is_occupied(boards[turn], move + pos * 3):
            continue
        if is_occupied(boards[not turn], move + pos * 2) and is_occupied(boards[not turn], move + pos):
            capture += 1
            if clear:
                place_piece(boards[not turn], move + pos * 2, False)
                place_piece(boards[not turn], move + pos, False)
    captures[turn] += capture
    return capture

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

def handle_move(boards, turn, move, captures, true_move=True):
    capture = check_capture(boards, move, turn, captures)
    if captures[turn] == 4 and not capture and winning_line(boards[not turn]):
        return None, capture
    place_piece(boards[turn], move.co)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture
