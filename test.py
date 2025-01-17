def read_board_from_file():
    with open('./test', 'r') as file:
        lines = file.readlines()
    board = [line.strip().split() for line in lines]
    return board

def generate_bitboards():
    board = read_board_from_file()
    bitboard_X = 0
    bitboard_O = 0

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 'X':
                bitboard_X |= (1 << (i * len(board) + j))
            elif board[i][j] == 'O':
                bitboard_O |= (1 << (i * len(board) + j))

    return [[bitboard_X], [bitboard_O]]

