from board import coordinate, SIZE
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import random
import copy

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

def generate_legal_moves(boards, turn, capture):
    legal_moves = []
    for row in range(SIZE - 1):
        for col in range(SIZE - 1):
            move = coordinate((row, col))
            if is_occupied(boards[0], move.co) or is_occupied(boards[1], move.co):
                continue
            legal, _, _ = is_legal(capture, boards, move, turn)
            if legal:
                legal_moves.append(move)
    return legal_moves

def evaluate_board(boards, turn, capture, result):
    def count_patterns(board):
        pairs = 0
        threes = 0
        fours = 0
        size = SIZE - 1

        # Check horizontal patterns
        for i in range(size):
            for j in range(size - 2):
                if is_occupied(board, (i, j)) and is_occupied(board, (i, j + 1)):
                    pairs += 1
                if j < size - 2 and is_occupied(board, (i, j)) and is_occupied(board, (i, j + 1)) and is_occupied(board, (i, j + 2)):
                    threes += 1
                if j < size - 3 and is_occupied(board, (i, j)) and is_occupied(board, (i, j + 1)) and is_occupied(board, (i, j + 2)) and is_occupied(board, (i, j + 3)):
                    fours += 1

        # Check vertical patterns
        for i in range(size - 2):
            for j in range(size):
                if is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j)):
                    pairs += 1
                if i < size - 2 and is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j)) and is_occupied(board, (i + 2, j)):
                    threes += 1
                if i < size - 3 and is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j)) and is_occupied(board, (i + 2, j)) and is_occupied(board, (i + 3, j)):
                    fours += 1

        # Check diagonal patterns (top-left to bottom-right)
        for i in range(size - 2):
            for j in range(size - 2):
                if is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j + 1)):
                    pairs += 1
                if i < size - 2 and j < size - 2 and is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j + 1)) and is_occupied(board, (i + 2, j + 2)):
                    threes += 1
                if i < size - 3 and j < size - 3 and is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j + 1)) and is_occupied(board, (i + 2, j + 2)) and is_occupied(board, (i + 3, j + 3)):
                    fours += 1

        # Check diagonal patterns (bottom-left to top-right)
        for i in range(2, size):
            for j in range(size - 2):
                if is_occupied(board, (i, j)) and is_occupied(board, (i - 1, j + 1)):
                    pairs += 1
                if i > 1 and j < size - 2 and is_occupied(board, (i, j)) and is_occupied(board, (i - 1, j + 1)) and is_occupied(board, (i - 2, j + 2)):
                    threes += 1
                if i > 2 and j < size - 3 and is_occupied(board, (i, j)) and is_occupied(board, (i - 1, j + 1)) and is_occupied(board, (i - 2, j + 2)) and is_occupied(board, (i - 3, j + 3)):
                    fours += 1

        return pairs, threes, fours

    current_board = boards[turn]
    pairs, threes, fours = count_patterns(current_board)
    return pairs + 5 * threes + 10 * fours

def bot_play(boards, turn, captures):
    moves = generate_legal_moves(boards, turn, captures)
    best_move = None
    best_points = float('-inf')

    for move in moves:
        # Create a deep copy of the boards to simulate the move
        new_boards = copy.deepcopy(boards)
        result, capture = handle_move_bot(new_boards, turn, move, captures)
        
        # Evaluate the board after the move
        points = evaluate_board(new_boards, turn, capture, result)
        
        # Select the move with the highest heuristic score
        if points > best_points:
            best_points = points
            best_move = move

    return best_move