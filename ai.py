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
    def count_pairs(board):
        count = 0
        size = SIZE - 1

        # Check horizontal pairs
        for i in range(size):
            for j in range(size - 1):
                if is_occupied(board, (i, j)) and is_occupied(board, (i, j + 1)):
                    count += 1

        # Check vertical pairs
        for i in range(size - 1):
            for j in range(size):
                if is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j)):
                    count += 1

        # Check diagonal pairs (top-left to bottom-right)
        for i in range(size - 1):
            for j in range(size - 1):
                if is_occupied(board, (i, j)) and is_occupied(board, (i + 1, j + 1)):
                    count += 1

        # Check diagonal pairs (bottom-left to top-right)
        for i in range(1, size):
            for j in range(size - 1):
                if is_occupied(board, (i, j)) and is_occupied(board, (i - 1, j + 1)):
                    count += 1

        return count

    current_board = boards[turn]
    return count_pairs(current_board)

def bot_play(boards, turn, captures):
    moves = generate_legal_moves(boards, turn, captures)
    curr_choices = None
    best_points = float('-inf')
    for move in moves:
        result, capture = handle_move_bot(copy.deepcopy(boards), turn, move, captures)
        points = evaluate_board(boards, turn, capture, result)
        if points > best_points:
            best_points = points
            curr_choices = move
    return moves[random.randint(0, len(moves) - 1)]
    return curr_choices


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