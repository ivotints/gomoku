import pygame as py
import pygame.draw as pyd
from macro import BLACK, WHITE
from render import draw_board, update_board, find_mouse_pos
from board import coordinate, SIZE, WIDTH
from game import handle_move, is_occupied

class gomoku:
    def __init__(self):
        self.boards = [[0], [0]]
        self.turn = 0
        self.win = py.display.set_mode((WIDTH, WIDTH))
        self.captures = [0, 0]
        self.running = True

        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()

def main():
    py.init()
    game = gomoku()
    while game.running:
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    game.running = False
            if event.type == py.MOUSEBUTTONDOWN:
                pos = find_mouse_pos(py.mouse.get_pos())
                if pos is None:
                    continue
                move = coordinate((pos[1], pos[0]))
                if not is_occupied(game.boards[0], move.co) and not is_occupied(game.boards[1], move.co):
                    result, update = handle_move(game.boards, game.turn, move, game.captures)
                    if result is None:
                        continue
                    if result:
                        print("GG")
                        exit(0)
                    if update:
                        update_board(game.boards, game.win)
                    else:
                        pyd.circle(game.win, BLACK if not game.turn else WHITE, ((pos[0] + 1) * WIDTH / SIZE , (pos[1] + 1) * WIDTH / SIZE), WIDTH / SIZE / 3)
                    # print(game.captures)
                    # display_board(game.boards[0], game.boards[1])
                    game.turn = not game.turn
                    py.display.update()



if __name__ == '__main__':
    main()

